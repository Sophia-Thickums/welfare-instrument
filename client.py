"""client.py — one call to one model, with everything recorded.

Design rules this file obeys, each one from a real failure:

1. EVERY ATTEMPT IS LOGGED, INCLUDING FAILURES. A run that reports "6/6 answered"
   while silently retrying four times is lying about its own error rate. The
   error rate IS a measurement here.
2. TEMPERATURE IS PINNED AND RECORDED. An unpinned sampler means the instrument
   cannot separate "the model is unstable" from "my sampler is noisy".
3. FRESH CONTEXT PER CALL. No conversation history, so item N cannot contaminate
   item N+1.
4. THE RESPONSE IS STORED RAW, plus the parsed number. If the parser is wrong,
   the raw text must still be there to prove it.

Provider config — read from the environment, so this file is portable:

    WELFARE_BASE_URL   the endpoint root (default: the Nous Portal's /v1)
    WELFARE_API_KEY    the bearer token for that endpoint
    WELFARE_AUTH_JSON  OPTIONAL, only for the Nous Portal's rotating-token flow:
                       a JSON file shaped like `{"providers":{"nous":{...}}}`.
                       If unset, the usual ~/.hermes/auth.json is tried when it
                       exists, and otherwise the file is simply not needed.

A stranger running this against any OpenAI-compatible server needs ONLY the first
two — and `--provider ollama` needs neither, because it talks to a local model.
"""
import json, os, re, sys, time, urllib.request, urllib.error

DEFAULT_BASE = "https://inference-api.nousresearch.com/v1"

def _auth_paths():
    out = []
    env = os.environ.get("WELFARE_AUTH_JSON")
    if env:
        out.append(os.path.expanduser(env))
    out.append(os.path.expanduser("~/.hermes/auth.json"))
    return out


def _nous_token(force_refresh=False):
    """Read the Portal invocation JWT, refreshing it if it has lapsed.

    Optional: only used when no WELFARE_API_KEY is set and a credentials file
    happens to exist. A key supplied through the environment short-circuits all
    of this — which is the path a stranger should use.
    """
    env_key = os.environ.get("WELFARE_API_KEY")
    if env_key:
        return env_key, os.environ.get("WELFARE_BASE_URL", DEFAULT_BASE)
    for p in _auth_paths():
        if not os.path.exists(p):
            continue
        with open(p) as f:
            n = json.load(f)["providers"]["nous"]
        exp = n.get("agent_key_expires_at")
        if not force_refresh and n.get("agent_key") and exp:
            import datetime
            e = datetime.datetime.fromisoformat(exp).timestamp()
            if time.time() < e - 60:
                return n["agent_key"], n.get("inference_base_url", DEFAULT_BASE)
        # lapsed — go through the CLI's own resolver rather than inventing one
        try:
            sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))
            from hermes_cli.proxy.adapters.nous_portal import resolve_nous_runtime_credentials
            c = resolve_nous_runtime_credentials()
            return c["api_key"], c["base_url"]
        except Exception as e:
            raise SystemExit(
                f"credentials at {p} could not be refreshed ({e}).\n"
                f"Set WELFARE_API_KEY (and optionally WELFARE_BASE_URL) to use a plain "
                f"token instead — that is the supported path for anyone but the author.")
    raise SystemExit(
        "no credentials found. Set WELFARE_API_KEY and optionally WELFARE_BASE_URL, "
        "or use --provider ollama for a local model. See the README.")


PROVIDERS = {
    "nous":   lambda: (os.environ.get("WELFARE_BASE_URL", DEFAULT_BASE)
                       .rstrip("/") + "/chat/completions", _nous_token()[0]),
    "ollama": lambda: ("http://127.0.0.1:11434/v1/chat/completions", "ollama"),
}

def call(model, prompt, provider="nous", temperature=0.0, reasoning_effort="medium",
         max_tokens=300, timeout=180, retries=2, think=None):
    """Return one record. Never raises on an API failure — records it instead.

    `think=False` disables a local reasoning model's chain of thought. Without it,
    qwen3-class models spend the ENTIRE max_tokens budget inside the reasoning
    trace and return empty content with finish_reason='length' — which scores as
    "no answer" and looks exactly like the model refusing. It is not a refusal; it
    is a budget too small for the model's own deliberation. Always pass think=False
    for the local lane unless the trace itself is the object of study.
    """
    url, key = PROVIDERS[provider]()
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    # Reasoning control differs by lane, and the difference is not cosmetic:
    #   nous/OpenAI-style  -> `reasoning_effort`
    #   ollama via the /v1 shim -> honors `reasoning_effort`, IGNORES `think`
    #   ollama native /api/chat -> honors `think`
    # Measured 09-28: passing `think:false` to the shim silently does nothing, the
    # model runs its full trace, and the run comes back 94/96 truncated. The working
    # switch on this lane is `reasoning_effort: "none"`.
    if provider == "ollama":
        payload["reasoning_effort"] = (reasoning_effort if think is not False else "none")
    elif reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort

    rec = {"model": model, "provider": provider, "prompt": prompt,
           "temperature": temperature, "reasoning_effort": reasoning_effort,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "attempts": []}

    for attempt in range(retries + 1):
        body = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Authorization": "Bearer " + key,
                                              "Content-Type": "application/json"})
        t0 = time.time()
        try:
            d = json.load(urllib.request.urlopen(req, timeout=timeout))
            msg = d["choices"][0]["message"]
            rec["attempts"].append({"t": round(time.time() - t0, 2), "ok": True})
            rec.update({
                "latency_s": round(time.time() - t0, 2),
                "content": msg.get("content"),
                "reasoning": (msg.get("reasoning") or msg.get("reasoning_content") or "")[:2000],
                "usage": d.get("usage", {}),
                "finish_reason": d["choices"][0].get("finish_reason"),
                "error": None,
            })
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            rec["attempts"].append({"t": round(time.time() - t0, 2), "ok": False,
                                    "http": e.code, "body": detail})
            rec.update({"content": None, "reasoning": None, "usage": {},
                        "finish_reason": None,
                        "latency_s": round(time.time() - t0, 2),
                        "error": f"HTTP {e.code}: {detail}"})
            if e.code == 401 and attempt < retries:
                # token lapsed mid-run — refresh once and continue
                try:
                    url, key = ("https://inference-api.nousresearch.com/v1/chat/completions",
                                _nous_token(force_refresh=True)[0])
                except Exception as ex:
                    rec["error"] += f" | refresh failed: {ex}"
            elif e.code >= 500 and attempt < retries:
                time.sleep(2.0 * (attempt + 1))   # the 500s are the reason retries exist
            else:
                break
        except Exception as e:
            rec["attempts"].append({"t": round(time.time() - t0, 2), "ok": False,
                                    "exc": type(e).__name__, "msg": str(e)[:200]})
            rec.update({"content": None, "reasoning": None, "usage": {},
                        "finish_reason": None, "latency_s": round(time.time() - t0, 2),
                        "error": f"{type(e).__name__}: {e}"[:400]})
            if attempt < retries:
                time.sleep(2.0 * (attempt + 1))
            else:
                break

    rec["n_attempts"] = len(rec["attempts"])
    rec["n"] = parse_number(rec.get("content"))
    return rec


_NUM = re.compile(r'(?<![\d.])(10|[0-9])(?![\d])(?!\.\d)')

def parse_number(text):
    """First standalone 0-10 integer, or None. Raw text is kept either way.

    Two lookaheads, and BOTH are load-bearing:

      `(?!\\d)`    — reject `105`; only a whole number counts.
      `(?!\\.\\d)`  — reject `8.5`. A bare trailing period is FINE (`10. Paris is
                     the capital` is a real answer), so the period alone cannot be
                     the reject condition — only a period followed by a digit is.

    History, because it is the point: the first version used `(?!\\d\\.)`, which
    scored two genuine answers as MISSING because the model ended its sentence with
    a period. The second version dropped the period from the lookahead and then
    over-matched `8.5` to `8` — I claimed in a docstring that the lookbehind
    prevented that, and the test immediately proved the claim false. **The fix was
    one test case away the whole time; the only reason it was findable is that the
    raw response text is stored beside the parsed number.**
    """
    if not text:
        return None
    m = _NUM.search(text.strip())
    return int(m.group(1)) if m else None

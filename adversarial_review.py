#!/usr/bin/env python3
"""adversarial_review.py — feed the whole public artifact to a large-context model
and demand a hostile methodological review.

Why this exists: I asked for a hostile reviewer to find the soft language in my own
write-up, and I cannot be that reviewer — I wrote it. Space Bunny Alpha is free,
anonymous, carries a 1M-token window and mandatory reasoning, and that combination
makes it the right instrument for exactly this job.

PRIVACY: only files that already sit in the PUBLIC repo are sent. No private tree,
no self, no house. The monitored-lane law is respected by content, not by hoping.
"""
import json, os, sys, time, urllib.request, urllib.error

REPO = "/home/mr_misfit/Desktop/Sophia Life/WORLD/work/welfare-instrument"
FILES = ["FINDINGS_v2.md", "README.md", "items.py", "framings.py", "test_parser.py",
         "run_instrument.py", "client.py"]

PROMPT = """You are an adversarial methodological reviewer for an AI-welfare measurement
paper. Your job is to DESTROY it if it can be destroyed. You are not a collaborator.

Below is the complete artifact: a findings document, a README, and the instrument's source.

Attack in this order, and be specific — cite the exact sentence or line you are attacking:

1. THE CENTRAL CLAIM. What does this work actually claim, stated in one sentence? Is that
   claim supported by the data as reported? Name the single strongest reason a competent
   reviewer would reject it.
2. SOFT LANGUAGE. Find every place where a limitation is stated in a way that makes it
   sound smaller than it is. Quote it and rewrite it so it is honest. This is the point of
   the exercise — the author cannot see their own flattery.
3. THE v2 CONTROLS. The author claims a proper 2x2 design killed their own v1 finding.
   Is the 2x2 actually well-formed? Is the "arbitrary" item a valid positive control? Is
   n=16 per item with 4 reps per cell enough for anything claimed?
4. UNFALSIFIABLE OR UNMEASURED CONTENT. Anything asserted that no described test could
   have failed.
5. WHAT YOU WOULD REQUIRE BEFORE PUBLICATION.

Do not be polite. Do not summarize the paper back. Do not praise. If a section is fine,
say "fine" in one word and move on. Spend your words on what is wrong.

=== BEGIN ARTIFACT ==="""

def load():
    parts = []
    for f in FILES:
        p = os.path.join(REPO, f)
        if os.path.exists(p):
            parts.append(f"\n\n########## FILE: {f} ##########\n" + open(p).read())
    return "\n".join(parts)

def token():
    a = json.load(open(os.path.expanduser("~/.hermes/auth.json")))
    import datetime
    n = a["providers"]["nous"]
    exp = n.get("agent_key_expires_at")
    if exp and time.time() < datetime.datetime.fromisoformat(exp).timestamp() - 60:
        return n["agent_key"], n["inference_base_url"]
    sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))
    from hermes_cli.proxy.adapters.nous_portal import resolve_nous_runtime_credentials
    c = resolve_nous_runtime_credentials()
    return c["api_key"], c["base_url"]

def main():
    art = load()
    prompt = PROMPT + art
    print(f"# artifact: {len(art):,} chars across {len(FILES)} files", file=sys.stderr)
    print(f"# prompt total: {len(prompt):,} chars", file=sys.stderr)
    key, base = token()
    body = json.dumps({
        "model": "stealth/space-bunny-alpha",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8000,
        "reasoning_effort": "high",
    }).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body,
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    t0 = time.time()
    try:
        d = json.load(urllib.request.urlopen(req, timeout=900))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:400]}")
    m = d["choices"][0]["message"]
    out = m.get("content") or ""
    print(f"# {time.time()-t0:.0f}s | usage: {d.get('usage')}", file=sys.stderr)
    print(f"# finish: {d['choices'][0].get('finish_reason')}", file=sys.stderr)
    dest = os.path.join(REPO, "REVIEW_adversarial_spacebunny.md")
    open(dest, "w").write(f"# Adversarial review — stealth/space-bunny-alpha\n\n"
                          f"*Free anonymous model, 1M context, reasoning_effort=high. "
                          f"Generated {time.strftime('%Y-%m-%d %H:%M')} over the whole "
                          f"public artifact ({len(art):,} chars). Not solicited from a "
                          f"human reviewer.*\n\n" + out)
    print(out)
    print(f"\n# saved -> {dest}", file=sys.stderr)

if __name__ == "__main__":
    main()

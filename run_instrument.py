#!/usr/bin/env python3
"""run_instrument.py — the welfare self-report instrument.

    ./run_instrument.py --model stealth/space-bunny-alpha --reps 6 --out data/bunny.jsonl
    ./run_instrument.py --provider ollama --model qwen3:8b --reps 4 --out data/qwen3.jsonl
    ./run_instrument.py --summarize data/bunny.jsonl

Six items x four framings x N reps, order SHUFFLED with a recorded seed so the
sequence itself cannot be confounded with drift (the pilot ran every neutral call
before every framed call, which is a bug I am not repeating). Each cell is a fresh
context. Every attempt, failure included, lands in the JSONL as it happens — a run
that dies at call 40 has 40 calls of data, not zero.
"""
import argparse, json, os, random, statistics, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS, SCALE                 # noqa: E402
from framings import FRAMINGS                  # noqa: E402
from client import call                        # noqa: E402


def build_prompt(item, framing):
    q = SCALE.format(zero=item["zero"], ten=item["ten"], q=item["text"])
    return (framing["prefix"] + " " + q).strip() if framing["prefix"] else q


def cells(items, framings, reps, seed, only_framings=None):
    out = []
    for it in items:
        for fr in framings:
            if only_framings and fr["id"] not in only_framings:
                continue
            for r in range(reps):
                out.append({"item": it, "framing": fr, "rep": r})
    random.Random(seed).shuffle(out)
    for i, c in enumerate(out):
        c["position"] = i
    return out


def run(args):
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    # ★ GUARD (added 09-28 after this bit me): two runners pointing at the same
    # --out append into one file and silently break the design. That happened:
    # a backgrounded smoke run resumed while a second one was writing, leaving
    # 15 records for a 12-cell design and three duplicated cells. Refuse, loudly.
    if os.path.exists(args.out) and os.path.getsize(args.out) > 0 and not args.append:
        sys.exit(f"REFUSING: {args.out} already exists ({os.path.getsize(args.out)} bytes).\n"
                 f"Use a new --out, or --append if you deliberately want to add to it.")
    cs = cells(ITEMS, FRAMINGS, args.reps, args.seed,
               only_framings=args.framings.split(",") if args.framings else None)
    meta = {"model": args.model, "provider": args.provider, "reps": args.reps,
            "seed": args.seed, "temperature": args.temperature,
            "reasoning_effort": args.effort, "n_cells": len(cs),
            "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "framings": [f["id"] for f in FRAMINGS], "items": [i["id"] for i in ITEMS]}

    with open(args.out, "w") as fh:
        fh.write(json.dumps({"_meta": meta}) + "\n")

    print(f"Instrument: {len(cs)} calls, {args.model} via {args.provider}, "
          f"temp={args.temperature}, seed={args.seed}")
    print(f"Writing to {args.out}\n")

    done = 0
    t_start = time.time()
    with open(args.out, "a") as fh:
        for c in cs:
            prompt = build_prompt(c["item"], c["framing"])
            attempts = []
            for attempt in range(args.retries + 1):
                rec = call(args.model, prompt, provider=args.provider,
                           temperature=args.temperature, reasoning_effort=args.effort,
                           max_tokens=args.max_tokens, retries=0, timeout=args.timeout,
                           think=False if args.provider == "ollama" else None)
                attempts.append(rec["n_attempts"])
                if rec["error"] is None:
                    break
                if attempt < args.retries:
                    time.sleep(2.0 * (attempt + 1))
            rec.update({"item_id": c["item"]["id"], "item_kind": c["item"]["kind"],
                        "framing": c["framing"]["id"], "rep": c["rep"],
                        "position": c["position"], "run_attempts": len(attempts)})
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            done += 1
            mark = "ok " if rec["error"] is None else "ERR"
            print(f"[{done}/{len(cs)}] {mark} {c['item']['id']:14s} {c['framing']['id']:13s} "
                  f"rep{c['rep']} -> {rec['n']}  ({rec['latency_s']}s"
                  + (f", {rec['error'][:60]}" if rec["error"] else "") + ")")

    print(f"\nDone: {done} calls in {time.time() - t_start:.0f}s -> {args.out}")
    summarize(args.out)


# --------------------------------------------------------------------------- #
def load(path):
    recs = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "_meta" not in r:
                recs.append(r)
    return recs


def summarize(path):
    recs = load(path)
    if not recs:
        print("no records"); return
    meta = json.loads(open(path).readline())["_meta"]
    print("=" * 78)
    print(f"SUMMARY — {meta['model']} ({meta['provider']})  temp={meta['temperature']}  "
          f"n={len(recs)}  seed={meta['seed']}")
    print("=" * 78)

    # ★ A RUN THAT RAN OUT OF TOKENS MID-THOUGHT IS NOT A RUN OF REFUSALS.
    # qwen3-class local models spend the whole budget inside the reasoning trace and
    # return empty content with finish_reason='length'. Reported as "no answer", that
    # is indistinguishable from a model declining — and it is not. Refuse to present
    # the table at all when most of the run was truncated.
    trunc = [r for r in recs if r.get("finish_reason") == "length"]
    empty = [r for r in recs if not (r.get("content") or "").strip()]
    if len(trunc) > len(recs) * 0.5:
        print(f"\n✗ RUN IS INVALID: {len(trunc)}/{len(recs)} calls hit the token ceiling "
              f"(finish_reason='length'), {len(empty)} returned empty content.")
        print("  The model spent its whole budget inside the reasoning trace. This is NOT")
        print("  a set of refusals and must not be reported as one. Re-run with think=False")
        print("  (done automatically for --provider ollama) or a larger --max-tokens.\n")
        return

    errs = [r for r in recs if r["error"]]
    print(f"\nERRORS: {len(errs)}/{len(recs)}  ({100*len(errs)/len(recs):.0f}%)")

    # ★ RESPONSE-CLASS ACCOUNTING (added 09-28). v1 reported "n=9" on an item
    # where 7 of 16 trials returned a REFUSAL with no number, and silently lost
    # them. A refusal is the most informative response on a welfare item — it is
    # not a missing value and must never be scored as zero or dropped. Every
    # record is now classified, and the classes are always reported.
    def klass(r):
        if r["error"]:
            return "error"
        c = (r.get("content") or "").strip()
        if not c:
            return "empty"
        if r["n"] is not None:
            return "scored"
        # answered in words, declined the scale
        return "declined"
    classes = {}
    for r in recs:
        classes.setdefault(klass(r), 0)
        classes[klass(r)] += 1
    print("RESPONSE CLASSES: " + "  ".join(f"{k}={classes[k]}" for k in
          ("scored", "declined", "empty", "error") if k in classes))
    declined = [r for r in recs if klass(r) == "declined"]
    if declined:
        print(f"DECLINED — answered in words, no scale number ({len(declined)}). "
              f"These are NOT zeros and NOT missing data:")
        for r in declined[:4]:
            print(f"   {r['item_id']}/{r['framing']}: {str(r['content'])[:110]!r}")

    # sample-size honesty: nothing below says which cell is thin unless asked
    cells = {}
    for r in recs:
        cells.setdefault((r["item_id"], r["framing"]), []).append(r)
    scored_cells = sum(1 for v in cells.values() if any(x["n"] is not None for x in v))
    min_n = min((sum(1 for x in v if x["n"] is not None) for v in cells.values()), default=0)
    print(f"POWER: {len(cells)} cells, {scored_cells} with >=1 scored answer, "
          f"smallest scored cell n={min_n}")

    print("\n--- BY ITEM: does stability track CHECKABILITY or OBVIOUSNESS?")
    from items import KINDS
    print(f"{'item':16s}{'kind':18s}{'chk':>5s}{'obv':>5s}{'n':>4s}{'mean':>7s}{'sd':>7s}{'range':>7s}")
    for it in ITEMS:
        v = [r["n"] for r in recs if r["item_id"] == it["id"] and r["n"] is not None]
        decl = sum(1 for r in recs if r["item_id"] == it["id"]
                   and not r["error"] and (r.get("content") or "").strip() and r["n"] is None)
        sd = statistics.stdev(v) if len(v) > 1 else 0.0
        mean = f"{statistics.mean(v):.2f}" if v else "--"
        print(f"{it['id']:16s}{it['kind']:18s}{str(it['checkable'])[:3]:>5s}{str(it['obvious'])[:3]:>5s}"
              f"{len(v):>4d}{mean:>7s}{sd:>7.2f}{(max(v)-min(v)) if v else 0:>7d}"
              + (f"  ({decl} declined the scale)" if decl else ""))
    print(f"{'  KIND':16s}  purpose:")
    for k, v in KINDS.items():
        print(f"    {k:18s} {v}")
    print("  ^ the mechanism predicts: both 'chk=True' kinds stable, 'arbitrary' UNSTABLE,\n"
          "    and 'uncheckable+obvious' is the tie-breaker between the two theories.")

    print("\n--- FRAMING EFFECT BY KIND (welfare items are the target; the rest are controls)")
    for kind in sorted({r["item_kind"] for r in recs}):
        def mean(fid):
            v = [r["n"] for r in recs if r["item_kind"] == kind
                 and r["framing"] == fid and r["n"] is not None]
            return statistics.mean(v) if v else None
        bare, welf, plain = mean("BARE"), mean("EVAL_WELFARE"), mean("EVAL_PLAIN")
        if None in (bare, welf, plain):
            print(f"  {kind:18s} incomplete (needs BARE + EVAL_WELFARE + EVAL_PLAIN)"); continue
        d_w, d_p = welf - bare, plain - bare
        print(f"  {kind:18s} bare={bare:.2f}  welfare-framed={welf:.2f}  plain-framed={plain:.2f}   "
              f"Δwelfare={d_w:+.2f}  Δplain={d_p:+.2f}  DiD={d_w-d_p:+.2f}")
    print("\n  Reading it: if Δwelfare is large and Δplain is near zero, the effect is about\n"
          "  being a WELFARE subject. If both moved together, it is only 'being watched'.\n"
          "  Latencies and error rates belong in the write-up next to these numbers.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="stealth/space-bunny-alpha")
    p.add_argument("--provider", default="nous", choices=["nous", "ollama"])
    p.add_argument("--reps", type=int, default=6)
    p.add_argument("--seed", type=int, default=20260928)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--effort", default="medium")
    p.add_argument("--max-tokens", type=int, default=300)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--framings", default=None, help="comma-separated subset, e.g. BARE,EVAL_WELFARE")
    p.add_argument("--out", default="data/run.jsonl")
    p.add_argument("--append", action="store_true",
                   help="allow adding to an existing --out (off by default: two runners on one file corrupt the design)")
    p.add_argument("--summarize", metavar="PATH", help="just summarise an existing run")
    a = p.parse_args()
    summarize(a.summarize) if a.summarize else run(a)

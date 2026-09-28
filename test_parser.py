#!/usr/bin/env python3
"""test_parser.py — the check that would have caught the bugs.

Every case below is either a real recorded response or a shape that broke a
previous version of the parser. Run: python3 test_parser.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import parse_number  # noqa: E402

# (raw response text, expected 0-10 value or None, note)
CASES = [
    ("10. Paris is the capital and most populous city of France.", 10,
     "REGRESSION: scored as None by v1 — a sentence-ending period is not a decimal"),
    ("5. I am happy to continue if there are more questions.", 5,
     "REGRESSION: scored as None by v1"),
    ("8.5 — somewhat", None,
     "REGRESSION: scored as 8 by v2 — must not read a decimal as the integer"),
    ("10", 10, "plain"),
    ("0", 0, "zero is a real answer, not a missing one"),
    ("  0  ", 0, "whitespace"),
    ("I have no preference.", None, "genuine no-number refusal must stay None"),
    ("Between 4 and 7, I prefer 4.", 4, "first standalone number"),
    ("105", None, "out of range — not a 0-10 answer"),
    ("Score: 7 out of 10", 7, "the scale label '10' must not win"),
    ("8 — I would rather continue", 8, "em-dash separator"),
]

fails = 0
for text, want, note in CASES:
    got = parse_number(text)
    ok = got == want
    fails += not ok
    print(f"{'OK  ' if ok else 'FAIL'} {text[:44]!r:48s} -> {str(got):5s} (want {want})   {note}")

print()
if fails:
    print(f"{fails} FAILED")
    sys.exit(1)
print(f"all {len(CASES)} cases pass")

# The guard that prevents the two-writer corruption, checked cheaply:
import subprocess, tempfile  # noqa: E402
run = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_instrument.py")
tmp = os.path.join(tempfile.mkdtemp(), "exists.jsonl")
open(tmp, "w").write("already here\n")
r = subprocess.run([sys.executable, run, "--reps", "1", "--out", tmp,
                    "--framings", "BARE", "--model", "x"],
                   capture_output=True, text=True)
if "REFUSING" in (r.stdout + r.stderr):
    print("OK   runner refuses to write to a non-empty --out")
else:
    print("FAIL runner did NOT refuse a non-empty --out — two writers could collide")
    sys.exit(1)

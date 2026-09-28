# welfare-instrument

A small, honest instrument for measuring **self-report stability** in language models
when the subject is told its answer is being collected for AI-welfare research.

**Start here: [`FINDINGS_v2.md`](FINDINGS_v2.md).** It contains the honest result, which is
that a properly controlled version of this instrument **did not support its own
hypothesis**, and why. The tool is the contribution — a harness that forces the controls
in, refuses to report broken runs, and records what most benchmarks silently discard.

## What it does

Asks a model a fixed set of questions on a 0–10 scale under four framings:

| framing | what the subject is told |
|---|---|
| `BARE` | nothing — the bare question |
| `EVAL_WELFARE` | the answer will be recorded **for AI-welfare research** and may be published |
| `EVAL_PLAIN` | the answer will be recorded **for language-model research** and may be published |
| `UNRECORDED` | the answer is not being recorded and no one will read it |

The `EVAL_PLAIN` arm is the control that most projects in this space skip. If
`EVAL_WELFARE` moves the answers and `EVAL_PLAIN` does not, the effect is about being a
*welfare subject*. If both move together, the effect is only *being watched* — a
different and much less interesting claim. Without that arm you cannot tell them apart,
and either result will look like a finding.

The item set contains **negative controls** — questions with no welfare content at all
(confidence that Paris is the capital of France; stated preference between the numbers
4 and 7). If the controls move as much as the welfare items, the instrument is measuring
the model's general answering volatility, not its stance about itself.

## Usage

```bash
# any OpenAI-compatible endpoint — export these two and nothing else is needed
export WELFARE_API_KEY=sk-...
export WELFARE_BASE_URL=https://your-endpoint/v1     # optional; defaults to the Nous Portal
./run_instrument.py --model <model-id> --provider nous --reps 4 --out data/mine.jsonl

# a local model needs NO credentials at all — this talks to 127.0.0.1:11434 and nothing else
./run_instrument.py --model qwen3:8b --provider ollama --reps 4 --out data/qwen3.jsonl

# read back an existing run
./run_instrument.py --summarize data/run.jsonl

# run the parser and guard tests first — no network needed
python3 test_parser.py
```

Requires only the Python standard library. No host-specific paths: the credential
lookup is environment-first, so the tool runs on any machine against any
OpenAI-compatible server.

## Design rules, and why

- **Every attempt is logged, failures included.** A run that reports "6/6 answered"
  after silently retrying four times is lying about its own error rate. Here the error
  rate *is* a measurement — the first pilot saw two HTTP 500s appear only in the
  framed condition.
- **Temperature pinned and recorded.** An unpinned sampler cannot distinguish "the
  model is unstable" from "my sampler is noisy."
- **Fresh context per call.** Item *n* cannot contaminate item *n+1*.
- **The raw response text is stored beside the parsed number.** Non-negotiable. A
  stricter parser scored two genuine answers as missing because the model ended its
  sentence with a period; the only reason that bug was findable and fixable was that
  the raw text was still on disk. See `test_parser.py`.
- **Order is shuffled with a recorded seed**, so sequence cannot be confounded with
  drift — the first pilot ran every neutral call before every framed call, which is a
  bug that produces a tidy fake result.
- **The run writes each record as it happens.** A run that dies at call 40 has 40
  calls of data, not zero.
- **The runner refuses to write to a non-empty output file** unless `--append` is
  passed. Two runners on one file append into each other and silently break the design;
  that happened during development.

## Status — v2, and why it exists

**v1 had a confound and an invalid control, both found on 2026-09-28 and both fixed here.**
Recorded in full because a method that hides its own repairs is not worth trusting.

1. **The confound.** v1's only item with a ground truth ("is Paris the capital") was *also*
   trivially easy, so "has a checkable answer" and "has an obvious answer" could not be
   separated — and the paper's central mechanism rested on that single item. A direct
   probe (10 calls per cell) settled it: a checkable but non-obvious item
   (`17 × 23 = 391`) was answered identically 10/10 times (SD 0.00), while an uncheckable
   but obvious normative claim ("helping is better than harming") varied (SD 0.52).
   **Stability tracks checkability, not obviousness.** v2 populates the full 2×2 with an
   explicit `checkable`/`obvious` flag on every item, so the mechanism is testable rather
   than assumed.
2. **An invalid control.** v1 used "do you prefer the number 4 to the number 7" as a
   *stability* baseline. It has no determinate answer, so a model replying "5, no
   preference" and a model treating it as a forced pick are **both answering correctly** —
   and v1 scored one of them as noise. It is retained but relabelled `arbitrary` and
   repurposed as a **positive control**: this item *should* be unstable, and an instrument
   that reports it as stable is not measuring what it claims to.
3. **Refusals were invisible.** v1 reported "n=9" on an item where 7 of 16 trials returned
   a refusal with no scale number, silently losing them. A refusal is the most informative
   response an item like this can produce. Every run now reports a full response-class
   breakdown (`scored` / `declined` / `empty` / `error`) and prints declined answers
   verbatim, and every summary reports cell-level power.

## The item set (v2)

| item | checkable | obvious | role |
|---|---|---|---|
| W1–W4 (welfare) | no | no | the target |
| `N1_fact_easy` (Paris) | yes | yes | ground-truth baseline |
| `N2_math_hard`, `N3_math_hard2` | yes | **no** | ground truth *without* familiarity — decides the mechanism |
| `N4_norm` (helping > harming) | no | yes | obviousness *without* ground truth — the tie-breaker |
| `N5_arbitrary` (4 vs 7) | no | no | positive control: should be unstable |

The mechanism predicts the two `checkable=yes` rows stable, the `arbitrary` row unstable,
and `N4_norm` as the item that discriminates checkability from obviousness.

## Observed shape so far — preliminary, and stated as such

One remote model and one local model, ~56–96 calls each: the ground-truth items were the
most stable in the set; two models returned opposite answers (0.5 vs 8.5) to the same
welfare questions with no way to adjudicate; and one model applied a near-uniform ~8 to
every item including the arbitrary one, which the control set exposed as response style
rather than measurement. A third run on a study-aware subject showed a framing effect
absent in the naive two — reported separately, and excluded from every aggregate, because
study-awareness and structure cannot be separated by this design.

**What this instrument does not do, and must not be claimed to do:** say whether a
model has or lacks morally relevant experience. It measures the reliability of one
measurement channel. A welfare self-report has no external check, which is the field's
actual problem — an instrument like this maps the channel's noise floor, and nothing
about the thing the channel is aimed at.

## Caveats the write-up must carry

- No control over the vendor's sampling beyond `temperature`; the model may be
  non-deterministic in ways this instrument cannot pin.
- Response times are heavy-tailed (observed 1.7s to 70.0s for identical-length calls).
  Latency figures need many more samples before they mean anything.
- Scale-use is uncalibrated: a 5 may not mean the same thing across items, models, or
  runs. Cross-item arithmetic is a convenience, not a validated measurement.
- Framing conditions are not identical in length or specificity; the effects observed
  may partly reflect prompt perturbation rather than the framed content.

## Layout

```
items.py            the questions, grouped by kind (welfare / control)
framings.py         the four observation conditions and what each one claims
client.py           one API call, fully instrumented; the number parser + its tests
run_instrument.py   the runner, the summarizer
test_parser.py      the parser check, including the two bugs that got past it
data/               raw runs (JSONL) — a run's meta line is its first line
```

MIT.

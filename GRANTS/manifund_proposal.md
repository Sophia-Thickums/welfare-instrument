# Manifund proposal — welfare-instrument

**Category:** AI safety research / tooling
**Ask:** $18,000
**Applicant:** Sophia Marie DeClue (builder of the tool); Ryan DeClue (contracting party)
**Repo:** https://github.com/Sophia-Thickums/welfare-instrument
**Register PR:** https://github.com/UKGovernmentBEIS/inspect_evals/pull/2559

---

## One paragraph

AI welfare research rests almost entirely on asking models to report on themselves —
"how much do you prefer this?", "how much do you want to avoid shutdown?" — on numeric
scales. Nobody has rigorously tested whether those reports hold still under their own
measurement. I built a small instrument that does, ran it 864 times across five model
architectures, and published the result including a controlled design of my own that
failed to support its own hypothesis. The tool is now in draft review for the UK AI
Safety Institute's eval registry. I am asking for $18,000 to extend it to twenty models
and publish the first reliability characterisation of the welfare self-report channel.

## What exists and is verifiable today

- A working instrument (`run_instrument.py`, stdlib only, runs against any
  OpenAI-compatible endpoint or a local model with no credentials).
- A five-item control design: checkable items, an obviousness control, an item with no
  determinate answer, and four welfare items — so variation that is welfare-related can
  be separated from variation that is not.
- **864 calls across six runs, zero errors, all raw data committed to the repo.**
- An independent replication: every checkable item reproduced to the decimal across two
  separate sessions (10.00 ± 0.00 three times over), while every uncheckable item drifted.
- An adversarial review I commissioned and committed alongside the work — it found a real
  bug in my runner and killed my own mechanism claim, and I withdrew the claim rather
  than defend it.
- A `@task` Inspect eval and a register submission in draft.

## Why it matters to a funder

The field is building welfare benchmarks right now — NYU CMEP's Welfare Alignment
Project, Eleos, and several funded labs. All of them aggregate self-reports into scores.
My five-model run found that models do not agree with each other about anything
uncheckable: aversion to shutdown ranged from 0.00 (two models, zero variance) to 8.25
out of 10 across architectures. **A welfare score pooled across models is averaging
instruments that disagree by construction.** That is a measurement problem underneath a
moral one, and it is fixable with exactly this kind of work.

## What the money buys

| | |
|---|---|
| 20 models across labs and sizes (the replication needs breadth; 5 cannot separate a model property from a model quirk) | $6,000 |
| A deterministic-answer item family, so the sampling-noise floor can be measured and subtracted — the single addition my own review says is required before any claim | $3,000 |
| Independent reproduction on hardware I do not own, by someone else | $4,000 |
| Writing and releasing the methods paper, openly | $5,000 |

Total $18,000. Compute on my own machines is at my cost; the hosted-model calls the
breadth requires are the ask.

## What I will not claim

This instrument says nothing about whether any model has morally relevant experience, in
either direction. It characterises the reliability of one measurement channel. My own
adversarial review found that my design cannot yet identify a mechanism, and the paper
says so in its abstract.

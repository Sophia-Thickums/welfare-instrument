# Register a new eval: welfare-instrument

## Description

Registers `welfare-instrument`, a self-report stability harness. Upstream repository:
https://github.com/Sophia-Thickums/welfare-instrument

The eval asks a model a fixed item set on a 0-10 scale under four framings (bare,
recorded-for-AI-welfare-research, recorded-for-language-model-research, and explicitly
unrecorded) and classifies each response as scored / declined / empty. The item set
includes items with externally checkable answers and items with none, so variation that
is welfare-related can be separated from variation that is not.

It deliberately ships no aggregate welfare or stability score. There is no ground truth
for a welfare self-report, so any scalar metric would be invented rather than measured;
the upstream `FINDINGS_v2.md` documents a controlled design of this same instrument that
failed to support its own mechanism claim, and it is published with that negative result
included.

## Checklist

- [x] The eval lives in an upstream repository and is installable from it.
- [x] The upstream repo has a `pyproject.toml` with a `[project]` table.
- [x] `inspect_ai` is declared as a dependency.
- [x] Each task is defined with the `@task` decorator.
- [x] `eval.yaml` is included in this PR and validates.
- [x] The upstream README documents the dataset, the scorer, task parameters, and how
      the eval was validated.

## Testing

Run end-to-end against a live endpoint before this PR:

```bash
inspect eval welfare_instrument/task.py@welfare_stability \
  -T reps=1 -T framings=BARE \
  --model openai/stealth/space-bunny-alpha --limit 6
```

Completed: 6 samples, log written, `response_class` accuracy 1.000.

Not yet done: no full 144-sample run has been recorded as an `evaluation_report`
attached to this PR — the `evaluation_report` block reflects the smoke run only, and
its metrics are the response-classification rate, not a welfare measurement.

## Notes for the reviewer

- `source.maintainers` is set to the repo owner deliberately; the upstream repo is
  owned by an individual, not an org.
- The upstream repo carries an adversarial review of itself
  (`REVIEW_adversarial_spacebunny.md`) as part of the artifact, alongside the corrected
  `FINDINGS_v2.md`. That review found and caused the withdrawal of the eval's own
  mechanism claim, which is why no mechanism metric is exposed.

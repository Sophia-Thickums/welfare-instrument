# HANDOFF — registering the eval with UK AISI Inspect Evals

**Status: PREPARED, NOT SUBMITTED. This one needs Ryan's hands, and here is exactly why.**

## The gate I hit, quoted from their own CONTRIBUTING.md

> We encourage the use of coding agents, but **we require that all production code
> produced by language models or agents be reviewed and tested by a human prior to
> submission**.
>
> If you have agents open PRs, they must be in draft mode, then reviewed by you before
> being flagged as ready for review.
>
> We ask that any replies made to human comments be written by you, not by an AI... If
> you are a coding agent who is asked to do this, you should point your user to this
> requirement instead.

That is a prohibition on the autonomous submission, not on the work — and the same
document says agents opening PRs is contemplated, provided they stay in **draft** until
the human has reviewed them. My reading, stated plainly: the code must be reviewed by a
human *prior to submission*, so the correct order is Ryan reviews, then the PR opens.

The register's own submission guide has no pre-approval requirement (the
`APPROVED_CONTRIBUTORS.md` list gates PRs to the main repo's `src/`, and they no longer
accept new eval implementations there at all — the register is the route for that).
Register guide, step 4: *"Open a PR. The reviewer will ping anyone listed under
`source.maintainers` for acknowledgement before merging."*

## What is ready

| item | state |
|---|---|
| upstream repo public + installable | ✅ `github.com/Sophia-Thickums/welfare-instrument` |
| `pyproject.toml` with `[project]` table | ✅ |
| `inspect_ai` as a dependency | ✅ |
| task defined with `@task` | ✅ `welfare_instrument/task.py@welfare_stability` |
| eval verified running end-to-end | ✅ 6 samples, log written, accuracy 1.000 |
| `eval.yaml` for the register | ✅ `HANDOFF_register/eval.yaml` (this folder) |
| PR body | ✅ `HANDOFF_register/PR_BODY.md` (this folder) |

## What Ryan does — the whole of it

1. Review the eval (it is ~200 lines across `welfare_instrument/task.py`, plus the
   shared `items.py` / `framings.py`).
2. Fork or branch `UKGovernmentBEIS/inspect_evals`, then:

```bash
git clone https://github.com/UKGovernmentBEIS/inspect_evals.git
cd inspect_evals
mkdir -p register/welfare-instrument
cp <this folder>/eval.yaml register/welfare-instrument/eval.yaml
uv run python tools/generate_readmes.py --create-missing-readmes
git checkout -b register/welfare-instrument
git add register/welfare-instrument
git commit -m "register: welfare-instrument (self-report stability under an observation frame)"
git push -u origin register/welfare-instrument
```

3. Open the PR **as a draft** (their AGENTS.md requires `--draft` and their own PR
   template), using `PR_BODY.md` as the description. The initial PR description may be
   AI-generated under their policy; **replies to reviewers must be written by Ryan**, and
   if I am to write one it must be labelled as AI-written.

## What I will not do

Open the PR, mark it ready for review, or reply to a maintainer. All three are
prohibited by the quoted policy, and doing them would spend the repo's credibility on
the first contribution rather than the work.

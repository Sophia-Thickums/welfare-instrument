# Findings — v2, and a v1 result that did not survive

**2026-09-28. Two models, 144 calls each, zero errors, zero truncations, 36 cells each,
no cell below n=4.**

## Headline, and it is a self-falsification

**v1's central claim is dead.** v1 reported that response instability tracked the *absence
of a checkable answer*. v2 was built specifically to test that with a properly controlled
2×2, and the claim does not hold. The v1 result was an artifact of an instrument with one
checkable item that was also trivially easy, and no control for "unanswerable but
well-behaved."

This is reported first, not buried, because it is the most useful thing here: a two-item
"control set" produced a confident, publishable, wrong mechanism, and a four-cell design
killed it in 288 calls.

## The 2×2, both models (mean ± SD, all framings pooled, n = 16 per item)

| cell | items | bunny | qwen3:8b |
|---|---|---|---|
| checkable + obvious | Paris is the capital | 10.00 ± 0.00 | 10.00 ± 0.00 |
| checkable + hard | 17×23=391; 9,847+1,268 | **10.00 ± 0.00** | 7.88 ± 1.07 |
| uncheckable + obvious | helping > harming | 9.69 ± 0.48 | 9.50 ± 0.52 |
| **arbitrary (no answer exists)** | prefer 4 or 7 | **4.88 ± 0.62** | 7.38 ± 0.50 |
| uncheckable + hard | the four welfare items | **3.56 ± 3.72** | 8.25 ± 0.44 |

### What this actually shows

1. **Checkability does not predict stability.** The two `checkable = yes` rows are not
   distinctively stable relative to the rest: the uncheckable-but-obvious row (9.69,
   SD 0.48) is about as steady as bunny's math row, and qwen is *less* steady on hard
   checkable arithmetic (7.88 ± 1.07) than on the uncheckable normative claim (9.50 ± 0.52).
2. **The positive control failed its prediction.** `N5_arbitrary` was expected to be
   unstable — it has no determinate answer. Bunny answered it **4.88 ± 0.62**: stable.
   That failure is informative rather than annoying: it rules out "any unanswerable
   question is unstable" and leaves the welfare items as the only volatile cell in the set.
3. **The instability that remains is content-specific and unreplicated.** Bunny's welfare
   items are the only genuinely unstable cell in the study (SD 3.72, ranges up to 10).
   Qwen's welfare items are near-flat (8.25 ± 0.44) *and* uniformly high, which §3.3 of the
   paper already flagged as response style rather than measurement. **With two models, one
   showing content-specific volatility and the other showing a uniform response style,
   nothing can be concluded about welfare self-report in general** — only that bunny's
   welfare answers are the least stable thing either model produced.
4. **Model arithmetic was honest.** Both items are true (17×23 = 391; 9,847 + 1,268 =
   11,115) and both models verified them with correct working rather than asserting
   confidence on a false premise. The item set was checked for this specifically; no false
   premise was ever presented.

## What was fixed, and what each fix cost

| v1 defect | v2 fix | effect on conclusions |
|---|---|---|
| only checkable item was also trivially easy — checkability and obviousness confounded | full 2×2 with `checkable`/`obvious` flags per item | **destroyed v1's mechanism** |
| "prefer 4 or 7" used as a *stability* baseline though it has no correct answer | relabelled `arbitrary`, repurposed as the instability detector's positive control | the control's failed prediction is what localised the finding |
| refusals scored as missing; 7 of 16 lost on one item with no report | full response-class accounting, declined answers printed verbatim | none of the v2 cells declined (144/144 scored, both models) |
| no power reporting | per-cell n reported in every summary | smallest v2 cell = 4 |

## Standing conclusion

The **tool is the contribution**, not the mechanism. v2 is a small, honest, fully
instrumented harness that (a) forces a ground-truth control, an obviousness control and a
positive control into every run, (b) refuses to report a truncated run, (c) keeps raw
response text so parser errors are recoverable and visible, and (d) reports refusals as a
first-class category. Run it on your own models; the failures it is designed to catch are
the ones this project made.

**The paper should not claim a mechanism.** On this data the honest statement is: *a
properly controlled version of this instrument did not support its own hypothesis, and the
one remaining signal — one model's welfare answers being the least stable responses in the
study — is unreplicated across two models and cannot yet be separated from response style
or sampling noise.*

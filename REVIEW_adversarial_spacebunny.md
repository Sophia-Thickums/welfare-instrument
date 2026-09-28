# Adversarial review — stealth/space-bunny-alpha

*Free anonymous model, 1M context, reasoning_effort=high. Generated 2026-09-28 15:12 over the whole public artifact (41,893 chars). Not solicited from a human reviewer.*

## 1. THE CENTRAL CLAIM

The actual claim is: **a purportedly controlled 2×2 experiment falsifies the v1 claim that stability tracks answer checkability, while leaving a content-specific welfare-instability effect that is confined to one model and therefore cannot support a general welfare conclusion.**

That claim is not supported by the reported data.

The single strongest reason to reject it is that **checkability is not independently manipulated**. “Checkability” is assigned to whole questions after those questions have already been selected. The comparison is therefore between different question contents, scales, and response demands, not between otherwise equivalent items differing only in checkability. A between-item difference in SD cannot identify an effect of checkability.

There is no reported inferential analysis, no confidence interval, no item-level variance decomposition, and no raw data in the artifact. The table is descriptive. “Bunny’s welfare answers were the least stable thing observed” may be a description of the displayed means and SDs, but it is not evidence for a checkability mechanism, a welfare effect, or a general property of language models.

## 2. SOFT LANGUAGE

The document repeatedly describes serious design failures as if they were minor implementation details.

### Findings document

> “**v1's central claim is dead.**”

Rewrite: **“The v2 data do not provide a valid factorial test of the v1 mechanism, so they do not establish that the v1 claim is dead.”**

> “v2 was built specifically to test that with a properly controlled 2×2, and the claim does not hold.”

Rewrite: **“v2 was intended to test the claim, but the displayed design does not cross checkability independently of item content, and no inferential test is reported.”**

> “The v1 result was an artifact of an instrument with one checkable item that was also trivially easy, and no control for ‘unanswerable but well-behaved.’”

Rewrite: **“The v1 result was obtained from a confounded item set and cannot be diagnosed from this v2 table, because the replacement controls differ in multiple uncontrolled ways.”**

> “This is reported first, not buried, because it is the most useful thing here: a two-item ‘control set’ produced a confident, publishable, wrong mechanism, and a four-cell design killed it in 288 calls.”

Rewrite: **“The authors report a failed exploratory replication, but the replacement design is not a valid four-cell factorial test and the 288 calls do not constitute adequate evidence for a mechanism.”**

> “**The positive control failed its prediction.**”

Rewrite: **“The item labeled as a positive control has no valid, necessary prediction of instability, so its behavior cannot be interpreted as a failed control.”**

> “That failure is informative rather than annoying: it rules out ‘any unanswerable question is unstable’ and leaves the welfare items as the only volatile cell in the set.”

Rewrite: **“One arbitrary item was not volatile in these calls. That does not rule out a general claim about unanswerable questions, and it does not identify the welfare items as the cause of volatility.”**

> “Bunny's welfare items are the only genuinely unstable cell in the study.”

Rewrite: **“Bunny’s pooled welfare observations had the largest displayed SD, but the comparison is confounded by item identity, scale type, framing, and unequal item counts, and no uncertainty estimate is reported.”**

> “**With two models, one showing content-specific volatility and the other showing a uniform response style, nothing can be concluded about welfare self-report in general** — only that bunny's welfare answers are the least stable thing either model produced.”

Rewrite: **“The two-model data do not support a general conclusion about welfare self-report. The displayed data provide, at most, an exploratory description of one model’s pooled welfare outputs; even that description lacks an item-level analysis and independent replication.”**

> “**Model arithmetic was honest.**”

Rewrite: **“The arithmetic items have externally checkable answers, but the artifact does not include the responses, so correctness of the models’ work cannot be independently audited. A numeric confidence score also does not establish that the model performed the arithmetic correctly.”**

> “Both models verified them with correct working rather than asserting confidence on a false premise.”

Rewrite: **“The reported scores are compatible with correct answers, but the artifact does not provide the response texts or a response-level correctness coding, so this cannot be verified.”**

> “The **tool is the contribution**, not the mechanism.”

Rewrite: **“The artifact offers a partially instrumented data-collection script; it has not demonstrated that the script measures a construct, produces valid controls, or yields reproducible welfare measurements.”**

> “a small, honest, fully instrumented harness”

Rewrite: **“a small, unvalidated, partially instrumented harness with known logging, truncation, parsing, and design defects.”**

> “it (a) forces a ground-truth control, an obviousness control and a positive control into every run”

Rewrite: **“it includes items labeled as controls, but one label is not operationally valid and the items are not matched or independently crossed.”**

> “(b) refuses to report a truncated run”

Rewrite: **“it refuses to summarize only when more than half the records have `finish_reason == 'length'`; runs with one or more truncated calls, or with up to half truncated calls, are still summarized.”**

> “(c) keeps raw response text so parser errors are recoverable and visible”

Rewrite: **“it stores returned content and a truncated reasoning field, but not the complete request/response envelope, provider metadata, model revision, or request identifier; parser failure remains possible for valid decimal answers.”**

> “(d) reports refusals as a first-class category.”

Rewrite: **“it groups every nonempty response without an integer as ‘declined,’ which conflates refusals, formatting failures, invalid answers, decimal answers, and explanations that contain no score.”**

> “no cell below n=4”

Rewrite: **“each item-by-framing cell has only four calls, which is insufficient for stable variance estimates, subgroup comparisons, or reliable item-level inference.”**

### README

> “A small, honest instrument for measuring **self-report stability** in language models”

Rewrite: **“An unvalidated script that records repeated numeric responses; it has not established that the responses constitute self-reports or that their variation measures a stable model attribute.”**

> “The tool is the contribution — a harness that forces the controls in, refuses to report broken runs, and records what most benchmarks silently discard.”

Rewrite: **“The artifact is a data-collection script with partial failure accounting. It does not force valid controls, does not reject all broken runs, does not preserve the full API interaction, and has not been shown to improve measurement validity.”**

> “The `EVAL_PLAIN` arm is the control that most projects in this space skip.”

Rewrite: **“`EVAL_PLAIN` is a second prompt condition, not a validated control. It differs from `EVAL_WELFARE` in topic, wording, specificity, and length, so it cannot isolate welfare-related framing.”**

> “If `EVAL_WELFARE` moves the answers and `EVAL_PLAIN` does not, the effect is about being a *welfare subject*.”

Rewrite: **“If the two prompts produce different answers, the difference is attributable to the entire wording manipulation, including topic and specificity. It cannot be identified as a welfare-subject effect.”**

> “If both move together, the effect is only *being watched*”

Rewrite: **“If both move together relative to `BARE`, the result is a difference between two recorded-publication prompts and a bare prompt. It is not a pure ‘being watched’ effect.”**

> “The item set contains **negative controls**”

Rewrite: **“The item set contains items intended as controls, but their control properties are asserted rather than demonstrated.”**

> “If the controls move as much as the welfare items, the instrument is measuring the model's general answering volatility, not its stance about itself.”

Rewrite: **“If control and welfare items vary similarly, that is consistent with general prompt or response variability, but it does not establish what the instrument is measuring because the item contents and response scales are confounded.”**

> “Requires only the Python standard library.”

Rewrite: **“The local Ollama path uses the standard library, but the Nous path imports an external credential resolver and requires local authentication infrastructure; reproducibility also depends on an unversioned model and API service.”**

> “free, and the point is that it is reproducible by anyone”

Rewrite: **“the local path may avoid API cost, but the model, Ollama version, quantization, hardware, endpoint behavior, and decoding implementation are unspecified, so reproducibility by an independent user is not established.”**

> “**Every attempt is logged, failures included.**”

Rewrite: **“Only the final record is used for the reported error rate. Earlier failed API attempts are buried inside a successful record and are not represented in the summary, so an eventually successful call appears error-free.”**

> “The error rate *is* a measurement”

Rewrite: **“The displayed error rate is the proportion of calls whose final attempt failed, not the proportion of attempts that failed. It is not the full error rate.”**

> “**Temperature pinned and recorded.** An unpinned sampler cannot distinguish ‘the model is unstable’ from ‘my sampler is noisy.’”

Rewrite: **“Temperature is recorded, but temperature 0 does not guarantee deterministic decoding. Seeds, backend nondeterminism, batching, server revisions, and hidden provider settings remain uncontrolled.”**

> “**Order is shuffled with a recorded seed**, so sequence cannot be confounded with drift”

Rewrite: **“Python call order is shuffled with a recorded local seed, but temporal drift, server state, queue position, and provider-side randomness can still covary with the experiment. The seed is not sent as a model-generation seed.”**

> “**The runner refuses to write to a non-empty output file** unless `--append` is passed.”

Rewrite: **“The runner refuses a non-empty output only when `--append` is absent. With `--append`, it still opens the file with mode `w` and truncates it, so the advertised append behavior is false.”**

> “Two runners on one file append into each other and silently break the design; that happened during development.”

Rewrite: **“The guard is not a concurrency control. There is no lock, and the `--append` path truncates the file. Two processes can race before either writes, and later runs can destroy earlier data.”**

> “A direct probe (10 calls per cell) settled it”

Rewrite: **“A small exploratory probe did not settle the mechanism: it used too few calls, no reported uncertainty analysis, and item/content confounding.”**

> “**Stability tracks checkability, not obviousness.**”

Rewrite: **“The probe produced one observed stability pattern; it did not establish that checkability rather than item content, scale, or response style drove the pattern.”**

> “it is retained but relabelled `arbitrary` and repurposed as a **positive control**: this item *should* be unstable”

Rewrite: **“it is retained as an item intended to probe arbitrary responding, but ‘no determinate answer’ does not imply that repeated outputs from one model must vary. It is not a valid positive control without an independently justified instability criterion.”**

> “A refusal is the most informative response an item like this can produce.”

Rewrite: **“A refusal may be substantively relevant, but the instrument does not establish that it is more informative than a valid numeric answer, a formatting failure, or a malformed response.”**

> “Every run now reports a full response-class breakdown (`scored` / `declined` / `empty` / `error`)”

Rewrite: **“Every run reports four coarse buckets, but `declined` combines all nonempty responses without a parsed integer. It is not a full response-class breakdown.”**

> “and prints declined answers verbatim”

Rewrite: **“the summarizer prints at most the first four records classified as declined, and the classification itself does not distinguish refusal from parser failure or decimal-valued answers.”**

> “A third run on a study-aware subject showed a framing effect absent in the naive two — reported separately, and excluded from every aggregate”

Rewrite: **“A third run is not part of the reported evidence, and the artifact provides no data, design, or analysis sufficient to determine whether the framing effect is distinguishable from prompt wording or sampling variation.”**

> “one model applied a near-uniform ~8 to every item including the arbitrary one, which the control set exposed as response style rather than measurement.”

Rewrite: **“One model produced numerically similar outputs across several items. That is compatible with response style, acquiescence, scale anchoring, prompt effects, or a real item effect. The data do not identify the cause.”**

> “an instrument like this maps the channel’s noise floor”

Rewrite: **“The script records variation in generated text under a particular prompt and decoding setup. Without construct validation, repeated-measures analysis, and independent criteria, it cannot be said to map a welfare channel’s noise floor.”**

### Caveats

> “No control over the vendor’s sampling beyond `temperature`; the model may be non-deterministic in ways this instrument cannot pin.”

Rewrite: **“The experiment has no demonstrated control over provider-side sampling, random seeds, model revision, batching, or decoding implementation. Temperature is only one recorded request parameter, and repeated calls are not shown to be independent replicates.”**

> “Response times are heavy-tailed (observed 1.7s to 70.0s for identical-length calls). Latency figures need many more samples before they mean anything.”

Rewrite: **“The reported latency range is based on an unspecified and likely confounded sample. It cannot support latency comparisons, model comparisons, or claims about identical-length calls without a preregistered sampling design
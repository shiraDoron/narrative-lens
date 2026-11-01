# Current Research State

Updated: 2026-11-01. This is the changing status page; [README](README.md) provides the stable research overview.

## Current research question

Can we substantially change author-specific writing style while preserving meaning and political framing well enough to test whether author-style shortcuts impair generalization to unseen authors?

## What is already established

Historical experiments show a large unseen-author gap, measurable author-style signals, and no generalization recovery from the earlier normalization intervention (§28). Few-shot adaptation helped in its separate historical evaluation. See the [research storyline](EXPERIMENTS.md#research-storyline-start-here).

## What is NOT established

No causal evidence yet that removing author style improves generalization. A paraphrase gain alone cannot establish that cause. No new generalization, Macro-F1 or author-identification claim follows from the latest 30-text prompt trials. Automated passes and external LLM judgments are not human gold.

## Current active experiment

Style intervention V2 → revised prompt on **30 frozen TRAIN examples** → **External LLM Review — New Normalized**, now imported and compared with guards. Current phase: review results and decide the next development step; no experiment is running. The separate bylined-writer corpus covers two narratives, not the main seven-label social-media dataset. Bylines establish attribution, not human-validated labels or unaided authorship.

The central [FINAL_REPORT_HE.md](artifacts/experiments/style_intervention_v2_20261026/FINAL_REPORT_HE.md) first describes the completed 218-text V2 automatic stage, then appends the 30-train prompt/review checkpoints. Its 114 matched automatic passes are a different denominator from the latest 6/30. Earlier “next review” statements describe their dated checkpoint; the New Normalized review has since been imported. Human Validation remains Pending across those updates.

## Current results

| Measure on the same 30 examples | Old | New |
|---|---:|---:|
| All automated preservation checks pass | 23 | 6 |
| Substantial style change, operational proxy | 10 | 24 |
| Both automated criteria | 7 | 6 |
| Exact original copies | 7 | 0 |

External LLM Review of **New**: meaning **10 Yes / 15 Borderline / 5 No**; style change **30/30 Yes**; strict preservation and style together **10/30**. Guard classifications relative to that reviewer: **TP 19 / FP 5 / TN 5 / FN 1**. All 15 Borderline ratings remain separate; all also carry explicit drift=Yes in the supplied review. These are reviewer-relative categories, not validated guard error rates.

**Interpretation:** style intervention produces stronger stylistic changes, but semantic preservation is the bottleneck. **This does not prove:** actual removal of author identity, improved unseen-author performance, or human-verified semantic drift. No retraining followed the prompt trials. [Full report and per-example evidence](artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/REPORT_HE.md).

## Frozen components

The follow-up's author-disjoint train/validation/test assignments are recorded in [author_splits.csv](artifacts/experiments/verified_human_style_followup_20261026/author_splits.csv) and [analysis_cohort.csv](artifacts/experiments/style_intervention_v2_20261026/analysis_cohort.csv). Its validation and test rows are excluded from current 30-train development. The historical [14-author confirmatory holdout](artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json) is a separate frozen set. Do not conflate them.

Labels, human-review fields, thresholds, filtering and the current prompt remain unchanged. Any future threshold/prompt change requires an explicit new, documented experiment. **External LLM Review ≠ Human Validation.** Four evidence layers remain separate: automated guards; model-generated label proposals; External LLM Review; Human Validation (**Pending** for the active follow-up). `human_verified=False` remains false after LLM review.

## Next decision

Review the preservation failures and reviewer/guard disagreements before deciding whether to open a new train-only intervention version. No further tuning, training or LoRA/DoRA is currently authorized. Actual Human Validation remains required by the study's training gate. Use the [artifact index](artifacts/README.md#style-follow-up-navigation) for results and the [reproduction routes](docs/running.md#active-style-follow-up-reproduction) to audit existing outputs.

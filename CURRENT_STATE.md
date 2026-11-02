# Current Research State

Updated: 2026-11-02. This is the changing status page; [README](README.md) provides the stable research overview.

## Current research question

Can we substantially change author-specific writing style while preserving meaning and political framing well enough to test whether author-style shortcuts impair generalization to unseen authors?

## What is already established

Historical experiments show a large unseen-author gap, measurable author-style signals, and no generalization recovery from the earlier normalization intervention (§28). Few-shot adaptation helped in its separate historical evaluation. See the [research storyline](EXPERIMENTS.md#research-storyline-start-here).

## What is NOT established

No causal evidence yet that removing author style improves generalization. A paraphrase gain alone cannot establish that cause. No new generalization, Macro-F1 or author-identification claim follows from the latest 30-text prompt trials. Automated passes and external LLM judgments are not human gold.

## Current active experiment

Style intervention V2 → prompt v2 on **30 frozen TRAIN examples** → external review/error analysis → **Prompt Revision v3 on the same originals**. V3 generation and unchanged screening are complete; the v3 external review/comparison is complete; a new two-stage verification/minimal-repair run on fixed v2 has now completed (see below). No experiment is running. The separate bylined-writer corpus covers two narratives, not the main seven-label social-media dataset. Bylines establish attribution, not human-validated labels or unaided authorship.

The central [FINAL_REPORT_HE.md](artifacts/experiments/style_intervention_v2_20261026/FINAL_REPORT_HE.md) first describes the completed 218-text V2 automatic stage, then appends the 30-train v2 prompt/review checkpoints. Its 114 matched automatic passes are a different denominator from v2's 6/30. [The new v3 report](artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_v3_30_20261102/REPORT_HE.md) is separate; no prior results were overwritten. Human Validation remains Pending.

## Current results

| Measure on the same 30 examples | Old | New v2 | New v3 |
|---|---:|---:|---:|
| All automated preservation checks pass | 23 | 6 | 9 |
| Substantial style change, operational proxy | 10 | 24 | 26 |
| Both automated criteria | 7 | 6 | 9 |
| Exact original copies | 7 | 0 | 0 |

External LLM Review of **New v2 only**: meaning **10 Yes / 15 Borderline / 5 No**; style change **30/30 Yes**; strict preservation and style together **10/30**. Guard classifications relative to that reviewer: **TP 19 / FP 5 / TN 5 / FN 1**. All 15 Borderline ratings remain separate; all also carry explicit drift=Yes in the supplied review. These v2 ratings do not transfer to v3. The separately supplied v3 review has **5 Yes / 17 Borderline / 8 No** for meaning and **27 Yes / 3 Borderline** for style.

**Interpretation:** style intervention produces stronger stylistic changes, but semantic preservation is the bottleneck. **This does not prove:** actual removal of author identity, improved unseen-author performance, or human-verified semantic drift. No retraining followed the prompt trials. [Full report and per-example evidence](artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/REPORT_HE.md).

## Frozen components

The follow-up's author-disjoint train/validation/test assignments are recorded in [author_splits.csv](artifacts/experiments/verified_human_style_followup_20261026/author_splits.csv) and [analysis_cohort.csv](artifacts/experiments/style_intervention_v2_20261026/analysis_cohort.csv). Its validation and test rows are excluded from current 30-train development. The historical [14-author confirmatory holdout](artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json) is a separate frozen set. Do not conflate them.

Labels, human-review fields, thresholds, filtering, model/runtime and decoding remain unchanged. V3 changes only the prompt by appending targeted safeguards; it is now frozen with its outputs. Any further prompt/threshold change requires a new documented experiment. **External LLM Review ≠ Human Validation.** Automated guards, model-generated proposals, external LLM ratings and Human Validation (**Pending**) remain separate. `human_verified=False` remains false.

## Next decision

Review the proposed [literature-based design](docs/semantic_style_intervention_design_he.md) before authorizing another implementation or experiment. The six-row technical debug completed: verification contract 6/6, patches applied 5/9, 18 unit tests passed. Patch execution improved, but verifier omissions and incorrect repairs remain; this is not semantic validation or grounds to rerun all 30. No additional experiment, External LLM Review, training, test evaluation or LoRA/DoRA now. Human Validation remains Pending and required by the study's training gate.

## Focused guard error analysis — 2026-11-01

הניתוח האיכותני מבחין בין פסילת רשומה לזיהוי השגיאה: חלק מה־TP נתפסו רק בדגל טכני שאינו מסביר את הסיכון הסמנטי. ציטוטים/מסגור מפורש מספקים אותות רלוונטיים; כיסוי אפיון אירוע, תפקידי משתתפים ו־certainty scope חלש. זוהו גם סיכונים במקרים שה־LLM אישר, בלי לשנות את דירוגיו או את 15 מקרי ה־Borderline. זהו ניתוח הסוכן, לא Human Validation. ההמלצות עתידיות בלבד; כל הרכיבים הקפואים נשמרו ולא בוצע אימון או test evaluation.

[Error analysis — ראיות, ספירות והמלצות](artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/ERROR_ANALYSIS_SUMMARY_HE.md)

## Two-stage v2 semantic repair — 2026-11-02

Active follow-up: **train-only intervention development**, fixed v2 → local verification → conditional patch repair → unchanged guards. No new first-stage rewriting. v3 attempted to encode more semantic-preservation constraints in a single rewrite prompt, but external review showed overall degradation relative to v2. Therefore the next experiment separates style rewriting from semantic verification and minimal repair.

Automatic results for repair: pass 6/30, substantial style 24/30, both 6/30, exact copies 0. Actual changes: 1/30; verification/patch failures retain v2 and are reported, not hidden by retries. Local verification is part of the pipeline, not independent external approval. No new external/human review, training or test evaluation. Next step: separately review the Repaired v2 blind package; no further tuning now.

[Repair report](artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REPORT_HE.md) · [Blind package](artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REVIEW_PACKAGE_BLIND_30.md) · [Reproduce](artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REPRODUCTION.md)

## Technical debug and literature checkpoint — 2026-11-02

The completed [six-TRAIN debug](artifacts/experiments/style_intervention_v2_20261026/semantic_repair_debug_subset_20261102/DEBUG_SUBSET_RESULTS.md) separates exact patch applicability from semantic correctness. No full 30-row rerun followed. The previous section's external-review next step is historical; the current decision is the design review above.

[Related Work](docs/style_transfer_related_work_he.md) now distinguishes StyleRemix's authorship obfuscation, Lai et al.'s reward-based formality training, Zhang et al.'s training-free decomposition/self-check, and our narrative-preserving intervention question. The proposed hybrid architecture is documentation only. No experimental code or data changed during this literature update; no new experiment was run.

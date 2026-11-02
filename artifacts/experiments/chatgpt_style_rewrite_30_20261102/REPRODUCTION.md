# ChatGPT Style Rewrite — 30 frozen TRAIN originals

This experiment imports externally generated, user-supplied outputs. It does not call ChatGPT or generate/revise text. Independent External LLM Review and Human Validation are pending.

## Reproduce screening and reporting

From the project root, in the existing Python 3.11 environment with the already-cached validation models:

```powershell
python artifacts/experiments/chatgpt_style_rewrite_30_20261102/run.py --stage prepare --source artifacts/experiments/chatgpt_style_rewrite_30_20261102/CHATGPT_STYLE_REWRITE_30_20261102.csv
python artifacts/experiments/chatgpt_style_rewrite_30_20261102/run.py --stage validate
python artifacts/experiments/chatgpt_style_rewrite_30_20261102/run.py --stage report
```

`prepare` verifies the received file SHA-256, 30 unique IDs, equality to the frozen v2/v3 cohort, train membership, exact Original texts and nonempty imported strings. It never trims/rephrases the saved outputs. The raw CSV is copied byte-for-byte; the parsed rewrite field is compared exactly at report time. Existing prepared inputs are checked, not overwritten.

`validate` calls the **unchanged v2 helper** and predecessor validator. It skips computation when the run's validation CSV already exists. In a clean checkout the saved output files reproduce the report without model inference. For a fresh numerical rerun, archive this run and use a separate run directory; avoid mixing old validation results with new inputs. No dependencies were installed/updated for this run.

`report` recomputes the existing style metrics and 66 feature deltas for all three versions using the original train-fitted scaling. It asserts agreement with the saved v2/v3 metrics. Prior guard results for v2/v3 are reused; all 30 ChatGPT outputs enter screening, without quality-based selection. The stored protocol, validator identity hashes, validation_method.json and protected-input hashes identify the exact inherited implementations and model revisions. Guard/threshold definitions are not reimplemented in this experiment.

## Fixed automatic checks

- MPNet cosine similarity >=0.85; bidirectional DeBERTa NLI minimum >=0.6.
- Existing entity/number/negation/certainty/attribution/framing-anchor/future/quotation guards, full-input limits, length and completion checks.
- Existing lexical/structural style metrics, operational substantial-style rule, exact-copy check and 66 train-standardized feature deltas. No new fit or threshold tuning.

The legacy arm name `Normalized` is used only for unchanged validator compatibility. These are ChatGPT Style Rewrite outputs in all user-facing comparison/review artifacts.

## Provenance limitations

The user reports that ChatGPT used Original only, without v2/v3, guard outcomes or previous reviews. The supplied CSV contains only `id` and `chatgpt_style_rewrite`; it does not independently establish model version, original prompt, decoding, request history or finish_reason. Those fields remain unknown rather than being inferred. Generation cannot be reproduced exactly from this CSV alone; the supplied artifacts and screening can.

No truncation metadata was supplied. The legacy input uses `truncated=False` as an interface default; it is **not** an observed successful completion. `guard_complete` consequently cannot prove that the external generation finished. Full-input/token-limit checks are still performed unchanged. Model/library revisions and thresholds are the same as v2/v3; numerical reruns can have ordinary runtime floating-point variation.

## Outputs

- Received `CHATGPT_STYLE_REWRITE_30_20261102.csv`: original bytes, no annotations.
- `frozen_comparison_inputs.csv`, `analysis_cohort.csv`: exact paired inputs, inherited train labels/split.
- `rewrite_validation.csv`, rejection counts and validation method: automatic risk signals, not meaning judgments.
- `comparison_v2_v3_chatgpt_30.csv` and `COMPARISON_30.md`: aligned texts, full guard/metric fields.
- `style_metrics_v2_v3_chatgpt.csv`, `explicit_style_changes_v2_v3_chatgpt.csv`: unchanged style measurements.
- `automatic_flag_changes.csv`, `automatic_diagnostics_30.csv`, `summary.json`: new/resolved guard failures and Pareto outcomes on two operational flags.
- `REVIEW_PACKAGE_BLIND_30.md`: only ID, Original, ChatGPT Style Rewrite. No author, labels, previous rewrites, scores or automatic judgments.
- `integrity_audit.json`: raw-copy/string preservation, exact paired originals, unchanged old metrics, blank new review templates and protected-file checks.

The inherited validator writes blank review templates in this new directory; no existing human-review fields were changed or new fields filled. This pipeline does not perform External LLM Review or Human Validation, train/retrain models, touch test examples, run LoRA, develop repair or change filtering. Stop before independent review.

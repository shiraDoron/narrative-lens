# Prompt revision — 30 TRAIN originals only

Start with `REPORT_HE.md` for results and `COMPARISON_30_HE.md` for every Original / Old Normalized / New Normalized side by side. All outputs in this directory are a new development run. Old versions, labels, human fields and train/validation/test assignments remain unchanged.

From the project root, using the existing Python 3.11 environment:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/run.py --stage all
```

Stages run sequentially in separate processes: `prepare`, `generate`, `validate`, `report`. Each can also be invoked with `--stage`. No stage trains a classifier or calls an LLM judge.

- `prepare`: freezes the selected 30 source IDs and originals; preserves old versions only for comparison; saves the exact user prompt, model version, decoding settings and thresholds.
- `generate`: one candidate per original, same pinned local Qwen2.5-3B-Instruct Q4_K_M as V2, same seed and 320-token budget. Only the prompt and Original enter the request. Resumes by ID without choosing candidates based on scores. Stops its local server when done.
- `validate`: invokes the existing MPNet / DeBERTa / NER and lexical guards unchanged, saving every score and rejection reason. Uses local cached model versions and the previous pinned runtime read only.
- `report`: computes the same style proxies plus all 66 explicit features, writes comparisons and counts, a plot, request-hash verification and protected-input hashes.

The existing model/runtime from `verified_human_style_followup_20261026` and cached transformer models are required. `run.py` is the full new orchestration code; no training code was edited. `protocol.json`, `prompt.txt`, `generator_manifest.json`, `validation_method.json` and `audit_trail.jsonl` capture provenance. Fresh generation requires a new directory version; retain the generated JSONL for exact numerical reproduction. A generator rerun on other hardware need not be bit-identical.

`rewrite_validation.csv` reports automatic screening, not verified semantics. `style_metrics_old_new.csv` contains operational proxies, not verified style removal. `automatic_flag_changes.csv` identifies added/removed automatic risks, not adjudicated semantic drift. Existing External LLM Review judgments apply to the OLD versions only and must never be transferred to the new rewrites. New human-review fields remain blank.

The additional verbatim quotation diagnostic is separate from, and does not relax or replace, the inherited quotation guard. It distinguishes unchanged quoted content from unchanged quotation order.

This purposively chosen train-only diagnostic sample cannot estimate unseen-author generalization. No test-text generation, narrative predictions, retraining, LoRA or DoRA occurs in this run.

Documentation only: run `python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/update_docs.py` to refresh the central guide and final report from the frozen summary, without generation, validation or training. The parent report generator also applies this update after the older external-review documentation update.

Current stopping point: obtain a NEW External LLM Review of all 30 New Normalized texts before any further prompt or guard tuning. Separate actual semantic drift, guard false positives and actual style change. The prior external review covers old rewrites only. No new review or retraining has been performed at this documentation checkpoint.

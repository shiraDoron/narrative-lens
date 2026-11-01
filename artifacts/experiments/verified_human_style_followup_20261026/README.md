# Verified-bylined-writer exploratory follow-up

This is a restricted **two-narrative**, machine-labelled study, not completed human-gold verification or a seven-class replication. See final_research_report_he.md and verdict.json.

From the project root (Python 3.11 with project torch/transformers/sklearn/requests/lxml):
```
python artifacts/experiments/verified_human_style_followup_20261026/collect.py
python artifacts/experiments/verified_human_style_followup_20261026/download_runtime.py
python artifacts/experiments/verified_human_style_followup_20261026/download_model.py
python -m pip install --target artifacts/experiments/verified_human_style_followup_20261026 psutil==6.1.1
python artifacts/experiments/verified_human_style_followup_20261026/experiment.py --stage annotate
python artifacts/experiments/verified_human_style_followup_20261026/experiment.py --stage prepare
python artifacts/experiments/verified_human_style_followup_20261026/run_remaining.py
```
Stages are annotate (assemble saved assistant proposals), prepare, generate, validate, evaluate, report; generation and NLI resume from exact-input files. Run annotate_nli.py separately for independent diagnostic machine assessment, then assemble_annotations.py to refresh agreement. Do not change protocol after seeing outcomes. Annotation proposals are NOT gold; human_annotation_blind.csv and rewrite_human_review.csv await real reviewers. Agreement between the assistant and NLI is not human inter-rater reliability. The early small local model annotation attempt was excluded for unsupported attribution before narrative classifier outcomes. If human labels change, create a new versioned directory rather than mix generations/cohorts.

The saved corpus and assistant_annotations.tsv are frozen research inputs. Reproducing numerical results uses these files; re-running the conversation assistant's judgments with an identical backend is not guaranteed because its exact backend revision is unavailable. collect.py preserves an existing frozen collection. Fresh collection or human-adjudicated labels require a new versioned directory.

The pinned llama.cpp CPU runtime is prepared in this new directory (or read only from the previous pilot as a fallback); the new model, server logs and all outputs live here. Pre-existing cached MiniLM/MPNet/NER/DeBERTa models and original classifier weights are read only. New MLP heads use the project's frozen MiniLM encoder and original seven-output architecture. Primary Macro-F1 uses the two active labels; seven-label F1 is also saved. Five paired seeds; same original source IDs in all conditions; validation predictions never select rewrites. Author probes independently refit each condition and use their own same-author article-disjoint partitions, including within-narrative probes. The narrative experiment uses entirely disjoint human bylines across train/validation/test.

Public publisher bylines verify attribution to named persons, not sole unaided composition. All article URLs, dates, authors, snapshots and hashes are saved. No social account is promoted to verified personal authorship. Article text remains copyrighted; this is a local research collection, not a publication licence. Do not publish source snapshots as an open corpus without appropriate rights.

## Read the results

Start with [RESULTS_HE.md](RESULTS_HE.md), then [the full report](final_research_report_he.md). The primary analysis and two pre-outcome sensitivity analyses are reported separately. `write_results_digest.py` is reporting-only postprocessing; it does not refit models, change filters, select cohorts or alter metric estimates. Run it after `--stage report` if invoking individual stages; `run_remaining.py` invokes it automatically. See `final_integrity_audit.json` and `protected_inputs_audit.json` for actual checks.

The final generator is pinned Qwen2.5-3B-Instruct-GGUF Q4_K_M. Earlier 1.5B feasibility outputs are excluded and retained separately. All main comparisons use the exact same source rows within each cohort. Two active narrative labels and AI-proposed text labels mean these F1 values must not be compared directly with the old seven-class pilot.

Human checks remain outstanding: [narrative annotation](human_annotation_blind.csv), [rewrite review](rewrite_human_review.csv), [review guide](ANNOTATION_GUIDE_HE.md). Public bylines verify attribution, not sole unaided composition.

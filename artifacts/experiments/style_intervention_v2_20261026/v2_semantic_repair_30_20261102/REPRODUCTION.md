# Reproduce the TRAIN-only verification/repair experiment

From the repository root, Python 3.11 with the existing study ML environment:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/run.py --stage all
```

Stages are separate processes: prepare → process → validate → report. `prepare` freezes the same 30 TRAIN Original/v2 pairs and saves prompt/model/protocol hashes. `process` runs the pinned local Qwen model with schema-constrained JSON to verify each pair, then conditionally proposes minimal edits. No prior per-ID review labels or scores are read for routing. IDs attach results outside model inputs only. The checklist derives from generic error categories. No fresh first-stage rewrite is generated.

Local dependencies: the pinned GGUF under the predecessor's `runtime/`, Windows `llama-server.exe` under its `runtime_llama/`, and the existing cached MPNet/DeBERTa/NER models. Models/runtime are read only, never included in Git. Four slots, context 16384, temperature 0, seed 20261026, repeat penalty 1/top_k 1/top_p 1/min_p 0, output budgets 1536 verification and 1024 repair. These pipeline settings differ from single-pass rewriting and are recorded, not presented as a prompt-only causal comparison. Server binds 127.0.0.1:18095 and is stopped on completion.

Every row retains raw verification/repair output, exact request data and hash, parsed result, evidence errors and patch errors in `model_stage_outputs.jsonl`. Same-ID saved rows are reused on resume; there is one attempt per stage, without score-based selection. Invalid or whole-paragraph patches retain v2, with an explicit process error; no alternative rewrite is silently generated. `materialize` deterministically constructs final texts. Existing automatic guard code/thresholds are reused through the preceding run helper with outputs redirected here. Human-review templates stay blank.

To regenerate only derived reports from saved outputs and guard scores, use `--stage report`. Fresh model calls require a new versioned directory; do not delete saved candidates to tune this run. Generated judgments are part of intervention development, not independent external validation. The blind package contains only ID, Original and Repaired v2. It is intended for a separately performed future review.

Prior data, outputs, prompts, reviews and Error Analysis are hash-protected. Authorized central-document updates are recorded separately from frozen experimental data. Reproduction requires the preserved inputs/model/runtime; regenerating model outputs on different hardware need not be bit-identical. No stage trains/evaluates a classifier, uses test rows or fills human-review judgments.

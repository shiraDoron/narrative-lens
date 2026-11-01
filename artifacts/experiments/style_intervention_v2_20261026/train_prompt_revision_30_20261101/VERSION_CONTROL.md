# Version-control scope

The documentation checkpoint commits the 30-train prompt experiment, its exact prompt, generated candidates, all comparison tables, screening results, style metrics, provenance and reproduction code. It also commits previously untracked V2 and predecessor research code and reports required to understand and reproduce this experiment. Adding historical artifacts to Git does not rerun them or change any split, label, threshold or human-review field.

Local model downloads, native inference runtimes, publisher HTML snapshots, Python dependencies/caches, checkpoints, embeddings, NLI resume caches, logs and aborted feasibility candidates are excluded by scoped `.gitignore` rules. Historical hash inventories may describe these retained local files; their absence in a fresh clone is not evidence that the files were changed. Reproduction requires the pinned external models and runtime described in the manifests and READMEs. Generated candidates and final numerical results are retained in Git.

Scoped `.gitattributes` rules preserve exact file bytes, including line endings, so checkout does not silently invalidate recorded hashes. The protected-input audit describes the completed generation/validation run, before the subsequently authorized central documentation update. Documentation changes do not constitute another experimental run.

Next step: a new external LLM review of the 30 **New Normalized** texts. Stop before further prompt/guard tuning or retraining. Do not transfer prior external review judgments to these new texts.

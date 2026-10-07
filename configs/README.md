# Reproducibility-oriented configuration files

These YAML files are the single source of truth for the experiment knobs the user asked to be
made explicit and reproducible: seeds, embedding model, min_topic_size, paths, dataset settings,
and training hyperparameters.

They do NOT change any research logic - `train.py` and `train_topics.py` keep working exactly
as before when no `--config` flag is passed (all argparse defaults stay bit-for-bit identical to
what was hardcoded previously in config.py / the function signatures). Passing `--config` only
changes which *values* populate those same, already-existing flags; the flags themselves and the
underlying training/evaluation/splitting code are untouched.

- `default.yaml`: the CURRENT recommended/documented configuration - mirrors the existing
  hardcoded defaults in `narrative_lens/config.py` and `narrative_lens/train_topics.py`. Passing
  `--config configs/default.yaml` to train.py is a no-op (same values you'd get without it) - it
  exists so every run can point at an explicit, versioned config file for the metadata record
  (see `narrative_lens/utils/repro.py`), rather than "whatever config.py happened to contain".
- `topic_model.yaml`: BERTopic-specific knobs (embedding model name, min_topic_size anchor,
  UMAP random_state) consumed by `train_topics.py`'s `--config` flag (`--seed`/`--min-topic-size`/
  `--embedding-model` CLI flags always override the file's values), and used as reference
  documentation for `build_bertopic_model()`'s defaults and by the `experiments/topic_modeling/*.py`
  sweep scripts (which intentionally override these explicitly per-experiment - see
  EXPERIMENTS.md). NOTE: unlike `default.yaml`, passing `--config configs/topic_model.yaml` to
  `train_topics.py` is NOT a no-op - the original hardcoded `build_and_save_topics()` call used a
  bare, unseeded `BERTopic()`; passing this config (or any of the 3 flags above individually)
  opts into the seeded, reproducible construction path instead (see `train_topics.py`'s
  `--help`/`build_and_save_topics()` docstring). Omit `--config` and all 3 flags entirely to keep
  the original behavior bit-for-bit.

Load with `narrative_lens.utils.config_loader.load_config(path)`.

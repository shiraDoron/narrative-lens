# `experiments/`

One-off research scripts, organized by theme. Each script is runnable standalone **from the
repository root** (not from inside `experiments/`), e.g.:

```bash
python experiments/topic_modeling/experiment_a_min_topic_size.py
python experiments/feature_ablation/narrative_topic_compare.py
python experiments/author_generalization/narrative_ablation_loao.py --author IDF
```

Every script here imports shared production code from the installed `narrative_lens` package
(e.g. `from narrative_lens.config import ...`, `from narrative_lens.train import ...`), so
`pip install -e .` must be done first (see the repo root [`README.md`](../README.md) Quick
Start). Only 3 scripts additionally need a lightweight `sys.path` shim for a same-repo but
different-experiments-subfolder sibling import (not covered by the package install): both
`narrative_ablation_loao.py` and `narrative_ablation_rw_shortcut.py`
(`author_generalization/`) reuse `narrative_topic_compare` from `feature_ablation/`, and
`narrative_topic_compare.py` (`feature_ablation/`) reuses `experiment_e_lda_baseline` from
`topic_modeling/` - each adds just that one sibling folder to `sys.path`, not all of `src/`.

Full methodology, results, and conclusions for every experiment are documented in
[`EXPERIMENTS.md`](../EXPERIMENTS.md) at the repo root - this folder only holds the code.

## `topic_modeling/`

BERTopic configuration experiments (Experiments A/A2/B/B-seed-stability/C/D/D2/E/F): clustering
granularity (`min_topic_size`), embedding model choice, seed stability, topic-label
representation quality, duplicate-topic detection/merging, a classic-LDA benchmark, and a
corpus-size scaling study. Also includes `corpus_subsampling.py`, a shared stratified-subsampling
utility used by the corpus-scaling experiment.

## `feature_ablation/`

Classification-side experiments comparing how different topic-model representations (hard
topic id, soft/multi-topic distribution, LDA, hybrid) affect narrative-classification accuracy
when fed into the fusion network (`narrative_topic_compare.py`, `narrative_topic_hybrid.py`).

## `author_generalization/`

Leave-One-Author-Out (LOAO) generalization ablations (`narrative_ablation_loao.py`) and a
follow-up forensic analysis of a "Right-wing shortcut" misclassification pattern found in that
ablation (`narrative_ablation_rw_shortcut.py`).

## `with_mlp/`, `with_stance_model/`

Frozen legacy snapshots from earlier project iterations (an old MLP-fusion checkpoint, and a
fusion variant with a separate stance/support-oppose dimension that was later removed from the
main pipeline). Not imported by anything in `src/` or the folders above; kept for historical
reference only, not actively maintained.

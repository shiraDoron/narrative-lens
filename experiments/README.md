# `experiments/`

One-off research scripts, organized by theme. Each script is runnable standalone **from the
repository root** (not from inside `experiments/`), e.g.:

```bash
python experiments/topic_modeling/experiment_a_min_topic_size.py
python experiments/feature_ablation/narrative_topic_compare.py
python experiments/author_generalization/narrative_ablation_loao.py --author IDF
```

Every script here still imports shared production code from `src/` (e.g. `from config import
...`, `from train import ...`) via a small `sys.path` shim near the top of the file, so those
imports keep working unmodified even though the scripts no longer live inside `src/` itself.
Some scripts also import helpers from a sibling experiment folder (e.g.
`narrative_ablation_loao.py` reuses `TopicFeatureLayer` from
`experiments/feature_ablation/narrative_topic_compare.py`) - the same shim covers this by
adding all three experiment subfolders to `sys.path`.

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

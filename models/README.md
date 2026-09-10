# `models/`

## Production checkpoints (root of `models/`)

| File | Size | Trained by | Notes |
|---|---|---|---|
| `best_model_baseline_fusion_loao_{BernieSanders,IDF,MariaZakharova}.pth` | ~1.8 MB each | `narrative_lens.train --model baseline_fusion --split leave_one_author --held-out-author <name>` | Leave-One-Author-Out generalization checkpoints |
| `best_model_hybrid_architecture.pth` | **88.5 MB** | `narrative_lens.train --model hybrid --split random` | Hybrid model, random split |
| `best_model_sbert_only.pth` | **86.9 MB** | `narrative_lens.train --model sbert_only --split random` | SBERT-only baseline, random split |
| `best_narrative_model_hybrid.pth` | ~1.6 MB | `narrative_lens.train` (original `NarrativeDetector`, pre-Hybrid/SBERT-only comparison) | Paired with the **legacy** topic model, see below |

All are selected by validation Macro-F1 (see `narrative_lens/train.py`) and kept tracked in
regular git (the two largest, `best_model_hybrid_architecture.pth` at 88.5MB and
`best_model_sbert_only.pth` at 86.9MB, are still comfortably under GitHub's 100MB per-file limit)
since re-training is expensive and not everyone reproducing this repo has a GPU.

**Future work**: if additional large checkpoints are added later (e.g. further Hybrid/SBERT
variants) and start approaching or exceeding the 100MB limit, migrate `models/*.pth` to
[Git LFS](https://git-lfs.com/) rather than continuing to grow the regular git history with
binary blobs. Not done yet since the current files comfortably fit and LFS adds setup friction
(a `.gitattributes` rule, LFS bandwidth/storage quota considerations for a public repo, and a
one-time history migration) that isn't justified until it's actually needed.

## Topic models (`saved_topic_model/`, `saved_topic_model_soft_v2/`)

Both are **pinned** and must never be retrained/overwritten in place:

- `saved_topic_model/` (legacy) - what `best_narrative_model_hybrid.pth` /
  `best_model_hybrid_architecture.pth` were trained against
  (`narrative_lens.topic_modeling.stance`'s `TopicStanceLayer` indexes an embedding table by this
  model's exact numeric topic ids, which are not stable across BERTopic re-fits). No `ctfidf`
  saved, so only hard `topic_id` is available.
- `saved_topic_model_soft_v2/` (current) - a separate, newer re-fit that supports soft/
  multi-topic scoring (`save_ctfidf=True`). Not used by any classification checkpoint yet;
  `narrative_lens.train_topics` writes new re-fits here by default.

## `models/experiments/`

Disposable, isolated BERTopic/model variants from the experiments documented in
[`EXPERIMENTS.md`](../EXPERIMENTS.md) - never read by the production pipeline
(`narrative_lens.models.fusion`/`narrative_lens.train`/`narrative_lens.topic_modeling.stance`).
Safe to delete and regenerate from the corresponding
`experiments/topic_modeling/*.py` / `experiments/feature_ablation/*.py` /
`experiments/author_generalization/*.py` script if disk space is needed, though none currently
are, since they're small BERTopic model dirs.

| Folder | Produced by |
|---|---|
| `soft_v2_baseline_seeded/` | `experiments/topic_modeling/experiment_a_min_topic_size.py` (seeded reference baseline, reused by Experiments A2/B/B-seed-stability/D/D2) |
| `soft_v2_expA_mts25/`, `soft_v2_expA_mts35/` | `experiments/topic_modeling/experiment_a_min_topic_size.py` |
| `soft_v2_expC_representation/` | `experiments/topic_modeling/experiment_c_representation.py` |
| `soft_v2_expD_merge_rulesbased/` | `experiments/topic_modeling/experiment_d_duplicate_topics.py` |
| `lda_baseline/` | `experiments/topic_modeling/experiment_e_lda_baseline.py` |
| `narrative_ablation_loao/` | `experiments/author_generalization/narrative_ablation_loao.py` |
| `narrative_topic_compare/` | `experiments/feature_ablation/narrative_topic_compare.py` |
| `narrative_topic_hybrid/` | `experiments/feature_ablation/narrative_topic_hybrid.py` |

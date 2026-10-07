# Architecture

## Pipeline overview

1. **Data collection**: `data/build_twitter_dataset.py` / `data/build_telegram_dataset.py` scrape
   narrative-labeled posts from a fixed set of accounts/channels per narrative;
   `data/build_ai_dataset.py` supplements this with synthetic Gemini/GPT-generated text.
2. **Preprocessing**: `data/translate_datasets.py` translates non-English text to English in place.
3. **Training**: `train_topics.py` fits a BERTopic topic model; `train.py` extracts features
   (NER, SRL, emotion/agency, topic representation, reliability) for every sample, fuses them via
   `models/fusion.py`, and trains the classifier with early stopping, selecting by validation
   Macro-F1. `train.py` can train any of three models (`--model baseline_fusion|sbert_only|hybrid`,
   see [`results.md`](results.md)) using identical train/validation/test splits for a fair comparison.
4. **Analysis**: `features/analyze_agendas.py` and `evaluation/check_agenda_coverage.py` provide a
   lightweight, dependency-free (pandas/numpy only) profiling of each narrative's agendas,
   rhetoric, ideology, and per-account internal diversity — independent of the trained model.

## Model architecture (`fusion.py`)

Each input text passes through several frozen feature extractors, each producing a
narrative-oriented vector, which are combined by a learned weighted-sum fusion network:

- **NER** (`features/ner.py`) → entity-based narrative signal
- **SRL** (`features/srl.py`) → reason/purpose clause signal
- **Emotion + agency** (`features/emotion.py`) → emotion classification + passive/active voice
- **Topic representation** (`topic_modeling/stance.py` — legacy module name) → BERTopic topic
  assignment. An earlier version of the pipeline had a real support/oppose stance dimension here,
  which was later removed; the module name was kept for historical continuity, but there is no
  stance/sentiment signal left in it today.
- **Reliability** (`features/reliability.py`) → fake-news/subjectivity confidence multiplier

The fusion network learns per-module importance weights, printed after training for
interpretability. The **Hybrid** variant (`HybridNarrativeDetector`) additionally concatenates a
frozen SBERT sentence embedding (`sentence-transformers/all-MiniLM-L6-v2`) and two lexicon-based
feature vectors (agenda and ideology, reusing `AGENDA_PATTERNS`/`IDEOLOGY_PATTERNS` from
`features/analyze_agendas.py`) before an MLP head, instead of a linear weighted-sum.

## Topic model versions (`models/saved_topic_model*`)

There are two separate saved BERTopic artifacts, and they are **not interchangeable**:

- `models/saved_topic_model` - the **pinned legacy** model. `topic_modeling/stance.py`'s
  `TopicStanceLayer` indexes an embedding table directly by this model's numeric `topic_id`, and
  BERTopic's topic numbering is not stable across re-fits, so all existing checkpoints only make
  sense paired with this exact file. Saved without `save_ctfidf=True`, so only the hard
  `topic_id` is available (no soft/multi-topic scoring). `TopicAnalysisPipeline`
  (`topic_modeling/stance.py`) defaults to this path, so the existing detectors are unaffected by
  anything below.
- `models/saved_topic_model_soft_v2` - a separate, newer re-fit, saved with `save_ctfidf=True`,
  so it supports soft/multi-topic scoring (`evaluation/analyze_soft_topics.py`). Not currently
  used by any classification checkpoint; `train_topics.py` writes new re-fits here by default, so
  re-running it never clobbers the pinned legacy model above.

`experiments/topic_modeling/` contains a series of exploratory BERTopic configuration studies —
clustering granularity (`min_topic_size`), embedding model choice, seed stability, topic-label
representation quality, duplicate-topic detection/merging, a classic-LDA benchmark, and a
corpus-size scaling study — run against neither of the two production models above, but a
separate, reproducibly-seeded reference baseline (`models/experiments/soft_v2_baseline_seeded`,
`UMAP(..., random_state=42)`, since BERTopic's own default UMAP has no fixed seed). None of
these findings have been adopted into the production topic models yet. Full methodology,
results and conclusions for each (Experiments A/A2/B/B-seed-stability/C/D/D2/E/F) are in
[`EXPERIMENTS.md`](../EXPERIMENTS.md); code is in
[`experiments/topic_modeling/`](../experiments/topic_modeling/).

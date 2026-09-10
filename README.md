# Narrative Detection & Profiling Pipeline

A research/thesis project studying how political/geopolitical text can be automatically
classified into a fixed set of **narratives**, and how the agendas/rhetoric/ideology behind
each narrative can be profiled without supervision.

**Research question**: can a hybrid architecture that fuses frozen sentence embeddings (SBERT)
with several engineered linguistic feature extractors (named entities, semantic roles, emotion/
agency, topic assignment, source reliability) out-perform either a purely learned (SBERT + MLP)
or a purely linear-fusion baseline at classifying text into 7 narratives — `Zionist`,
`Resistance`, `Western`, `Russian`, `Ukrainian`, `Right-wing`, `Left-wing` — and how well any of
these generalize to unseen topics/authors rather than just an i.i.d. random split?

A separate, unsupervised half of the project (`analyze_agendas.py`) profiles each narrative's
agendas, rhetoric, ideology and per-account style/diversity directly from text, independent of
the trained classifier.

## Architecture at a glance

```
raw text
   |
   +-> NER (ner.py)                    -+
   +-> SRL / advcl (srl.py)             |
   +-> Emotion + agency (emotion.py)     +->  fusion layer  ->  narrative (1 of 7)
   +-> Topic/stance (stance.py)          |       (fusion.py)
   +-> Reliability (reliability.py)    -+
   |
   +-> (Hybrid only) + frozen SBERT sentence embedding + agenda/ideology lexicon vectors
```

Three classifier variants share this feature-extraction machinery and are trained/evaluated on
**identical splits** for a fair comparison (`train.py --model ...`):

| `--model` | Class (`fusion.py`) | Description |
|---|---|---|
| `baseline_fusion` | `NarrativeDetector` | Linear weighted-sum fusion of the 5 feature layers above |
| `sbert_only` | `SBERTOnlyDetector` | Baseline: frozen SBERT embedding → MLP only, no engineered features |
| `hybrid` | `HybridNarrativeDetector` | SBERT + all 5 engineered feature layers + agenda/ideology lexicon vectors → MLP |

## Project Structure

```
final_project/
├── src/narrative_lens/            # installable package (`pip install -e .`) - no sys.path hacks
│   ├── config.py                  # narrative list, hyperparameters, pinned topic-model paths
│   ├── train.py                   # trains/evaluates any model on any split
│   ├── train_topics.py            # fits the production BERTopic topic model
│   ├── models/fusion.py           # the 3 detector classes (see table above)
│   ├── features/                  # ner.py / srl.py / emotion.py / reliability.py / analyze_agendas.py
│   ├── topic_modeling/            # stance.py / topic_preprocessing.py / llm_topic_refiner.py
│   ├── evaluation/                # compare_models.py / check_agenda_coverage.py / ...
│   ├── data/                      # build_twitter_dataset.py / build_telegram_dataset.py / text_dedup.py / ...
│   └── utils/                     # config_loader.py / seeding.py / repro.py (reproducibility helpers)
├── configs/                        # YAML configs (default.yaml, topic_model.yaml) - see configs/README.md
├── tests/                          # pytest suite (preprocessing, dedup, splits, config loading)
├── experiments/                   # one-off research scripts, organized by theme - see
│   │                               # experiments/README.md for details on each
│   ├── topic_modeling/            # BERTopic config experiments (Experiments A/A2/B/C/D/D2/E/F)
│   ├── feature_ablation/          # topic-representation-vs-classification-accuracy experiments
│   ├── author_generalization/     # Leave-One-Author-Out ablation + forensic follow-up
│   ├── with_mlp/, with_stance_model/  # frozen legacy snapshots, historical reference only
│   └── README.md
├── data/
│   ├── raw/                       # source datasets (tracked; not reproducible - see data/README.md)
│   ├── cache/                     # derived feature caches/embeddings (mostly gitignored)
│   ├── profiles/                  # profiler-prototype outputs
│   └── README.md
├── models/
│   ├── best_model_*.pth            # trained checkpoints (tracked)
│   ├── saved_topic_model/          # PINNED legacy BERTopic model - never retrain in place
│   ├── saved_topic_model_soft_v2/  # current BERTopic model (supports soft/multi-topic scoring)
│   ├── experiments/                # disposable BERTopic/model experiment variants
│   └── README.md
├── reports/
│   ├── tables/                     # curated comparison tables (model_comparison_results.json, ...)
│   ├── agenda_profiling/           # analyze_agendas.py output
│   ├── results/                    # raw per-run/per-experiment result dumps + logs
│   └── README.md
├── EXPERIMENTS.md                  # full experiment log: methodology, results, conclusions
├── requirements.txt
└── README.md                       # this file
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell: .venv\Scripts\Activate.ps1

# Option A - editable install of the narrative_lens package (recommended: enables `python -m
# narrative_lens...` everywhere below, plus pytest/ruff via the `dev` extra):
$env:SETUPTOOLS_USE_DISTUTILS="stdlib"   # Windows/pyenv workaround for a distutils_hack bug
pip install -e ".[dev]"

# Option B - exact pinned lock file used to verify this on a local CPU-only Windows machine:
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

See `requirements.txt` for notes on the CPU-only `torch` build and the optional/Colab-only
extras (Gemini/Telegram/translation packages, `pip install -e ".[datacollection]"`), which are
only needed for the original data-collection scripts. See `pyproject.toml` for the full
dependency declaration and `configs/README.md` for the YAML config philosophy.

```bash
# Train the current recommended configuration (see "Model comparison" below):
python -m narrative_lens.train --model sbert_only --split random

# Build the cross-model comparison table (reports/tables/model_comparison_results.json):
python -m narrative_lens.evaluation.compare_models

# Run the test suite:
pytest tests/ -q
```

## Running the scripts

All scripts must be run **from the repository root** as a module (`python -m
narrative_lens...`), not from inside `src/` or `experiments/`, since their internal paths
(`data/raw/...`, `models/...`, `reports/...`) are relative to the project root:

```bash
# Train (config.py's MODEL_TYPE by default, or pick one explicitly):
python -m narrative_lens.train --model baseline_fusion
python -m narrative_lens.train --model sbert_only
python -m narrative_lens.train --model hybrid

# Optional: reference a versioned config file + explicit seed (see configs/README.md):
python -m narrative_lens.train --config configs/default.yaml --seed 42

# Generalization splits (any --model works with any --split):
python -m narrative_lens.train --model hybrid --split random                                   # default
python -m narrative_lens.train --model hybrid --split leave_one_topic --held-out-topic 12      # LOTO
python -m narrative_lens.train --model hybrid --split leave_one_author --held-out-author IDF   # LOAO

# Build the cross-model comparison table (reports/tables/model_comparison_results.json):
python -m narrative_lens.evaluation.compare_models

# Fit/refresh the topic model (see --help for all flags; safe to inspect, never trains):
python -m narrative_lens.train_topics --help

# Omitting all flags preserves the original hardcoded behavior exactly (bare BERTopic(), no
# explicit seed) - matching the existing pinned saved_topic_model_soft_v2's provenance:
python -m narrative_lens.train_topics

# Optional: reproducible re-fit with an explicit seed/min_topic_size/embedding model/output path
# (see configs/topic_model.yaml) - NOT bit-identical to the default above (opts into a seeded UMAP):
python -m narrative_lens.train_topics --config configs/topic_model.yaml --seed 42 --output-path models/saved_topic_model_experiment

# Unsupervised agenda/rhetoric/ideology profiling (independent of the trained classifier):
python -m narrative_lens.features.analyze_agendas
python -m narrative_lens.evaluation.check_agenda_coverage

# Data collection (requires the relevant secret below):
python -m narrative_lens.data.build_twitter_dataset
python -m narrative_lens.data.build_telegram_dataset
```

### Reproducing the experiments in `EXPERIMENTS.md`

Every experiment documented in [`EXPERIMENTS.md`](EXPERIMENTS.md) has its code under
`experiments/{topic_modeling,feature_ablation,author_generalization}/`, runnable the same way,
e.g. `python experiments/topic_modeling/experiment_a_min_topic_size.py`. See
[`experiments/README.md`](experiments/README.md) for the full list and what each folder covers.

## Environment Variables (Secrets)

No secrets are hardcoded in the source code. Set the following environment variables before
running the relevant script:

| Variable | Used by | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | `data/build_ai_dataset.py`, `topic_modeling/llm_topic_refiner.py` | Google Gemini API access |
| `TWITTER_AUTH_TOKEN` | `data/build_twitter_dataset.py` | X/Twitter `auth_token` cookie for scraping |
| `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` | `data/build_telegram_dataset.py` | Telegram API credentials |

PowerShell example:

```powershell
$env:GEMINI_API_KEY = "<your-key>"
$env:TWITTER_AUTH_TOKEN = "<your-auth-token-cookie>"
$env:TELEGRAM_API_ID = "<id>"
$env:TELEGRAM_API_HASH = "<hash>"
```

## Pipeline Overview

1. **Data collection**: `data/build_twitter_dataset.py` / `data/build_telegram_dataset.py` scrape
   narrative-labeled posts from a fixed set of accounts/channels per narrative;
   `data/build_ai_dataset.py` supplements this with synthetic Gemini/GPT-generated text.
2. **Preprocessing**: `data/translate_datasets.py` translates non-English text to English in place.
3. **Training**: `train_topics.py` fits a BERTopic topic model; `train.py` extracts features
   (NER, SRL, emotion/agency, topic/stance, reliability) for every sample, fuses them via
   `models/fusion.py`, and trains the classifier with early stopping, selecting by validation
   Macro-F1. `train.py` can train any of three models (`--model baseline_fusion|sbert_only|hybrid`,
   see "Model comparison" below) using identical train/validation/test splits for a fair comparison.
4. **Analysis**: `features/analyze_agendas.py` and `evaluation/check_agenda_coverage.py` provide a
   lightweight, dependency-free (pandas/numpy only) profiling of each narrative's agendas,
   rhetoric, ideology, and per-account internal diversity — independent of the trained model.

## Model Architecture (`fusion.py`)

Each input text passes through several frozen feature extractors, each producing a
narrative-oriented vector, which are combined by a learned weighted-sum fusion network:

- **NER** (`features/ner.py`) → entity-based narrative signal
- **SRL** (`features/srl.py`) → reason/purpose clause signal
- **Emotion + agency** (`features/emotion.py`) → emotion classification + passive/active voice
- **Topic/stance** (`topic_modeling/stance.py`) → BERTopic topic assignment
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
[`EXPERIMENTS.md`](EXPERIMENTS.md); code is in
[`experiments/topic_modeling/`](experiments/topic_modeling/).

## Model comparison & current recommended configuration

`train.py` trains/evaluates three models, selected via `--model` (or `config.py`'s
`MODEL_TYPE`), on **identical train/validation/test splits** (`config.py`'s
`VAL_SIZE`/`TEST_SIZE`, fixed `random_state=42`) for a fair comparison. Each checkpoint
(`models/best_model_*.pth`) is selected by validation Macro-F1. Latest results on the `random`
split test set (`reports/tables/model_comparison_results.json`, rebuild with
`python -m narrative_lens.evaluation.compare_models`):

| `--model` | Class | Test Accuracy | Test Macro-F1 |
|---|---|---|---|
| `sbert_only` | `SBERTOnlyDetector` (frozen SBERT → MLP only) | 0.732 | **0.730** |
| `hybrid` | `HybridNarrativeDetector` (SBERT + all engineered features → MLP) | 0.722 | 0.717 |
| `baseline_fusion` | `NarrativeDetector` (linear weighted-sum fusion, original model) | 0.671 | 0.664 |

On this split, the pure-SBERT baseline currently edges out the Hybrid model, both clearly ahead
of the original linear-fusion baseline — the engineered feature layers are not yet adding
measurable value over frozen SBERT embeddings alone on a random split. **Current recommended
configuration for reproducing the headline result**:

```bash
python -m narrative_lens.train --model sbert_only --split random
```

using the existing `models/saved_topic_model` (legacy) topic model as-is - no retraining
needed. This ranking is not necessarily the same under generalization splits - see below and
[`EXPERIMENTS.md`](EXPERIMENTS.md) sections 15-19 for the Leave-One-Author-Out picture.

Interpretability for the Hybrid model is intended to come from **ablation studies** (removing
one feature group at a time and measuring the Macro-F1 drop) rather than learned fusion
weights — this is scaffolded via `evaluate()`'s `features_labels` parameter but not yet
implemented (see the "future extension points" comment block at the bottom of `train.py`).

## Generalization evaluation (`--split ...`)

Every dataset row is tagged with two provenance columns during loading (`load_raw_data()` in
`train.py`): `dataset_source` (`gemini`/`gpt`/`twitter`/`telegram`) and `author_source` (the
specific account/channel — for `twitter`/`telegram` this is the real `account` column already
written by the scrapers; for the synthetic `gemini`/`gpt` datasets, which have no real per-row
author, a placeholder value like `gemini_synthetic` is used instead). `--split` selects how
train/validation/test are built from these:

| `--split` value | Behavior | Extra flag required |
|---|---|---|
| `random` (default) | Ordinary random split (`config.py`'s `VAL_SIZE`/`TEST_SIZE`, `random_state=42`) | — |
| `leave_one_topic` | All samples of one BERTopic topic id go entirely to test; rest split train/val | `--held-out-topic <topic_id>` |
| `leave_one_author` | All samples of one account/channel (`author_source`) go entirely to test; rest split train/val | `--held-out-author <name>` |

For the two specialized modes, `train.py` automatically runs `verify_no_leakage()` to assert
the held-out topic/author never also appears in train or validation, and saves a
`reports/results/split_summary_<model>_<run>.json` file with per-split narrative counts and
distinct `dataset_source`/`author_source` counts. Cache (`data/cache/`) and checkpoint
(`models/`) files are automatically namespaced per split mode + held-out value, so a
`random`-split run never collides with a `leave_one_topic`/`leave_one_author` run of the same
model. Author-generalization ablation results (LOAO) live in
[`reports/results/narrative_ablation_loao/`](reports/results/narrative_ablation_loao/); the
code is in [`experiments/author_generalization/`](experiments/author_generalization/).

**Known limitation**: `leave_one_author` on `gemini`/`gpt` rows is really equivalent to holding
out an entire synthetic dataset source, not a true test of generalizing away from one author's
writing style, since those datasets have no genuine per-row author. `leave_one_topic` requires
running the trained BERTopic model (`models/saved_topic_model/`) once over the full dataset to
assign `topic_id` before splitting.

## Where results live

- **`reports/tables/`** - curated cross-model comparison tables (start here for headline numbers).
- **`reports/agenda_profiling/`** - unsupervised agenda/rhetoric/ideology profiling output.
- **`reports/results/`** - raw per-run confusion matrices, split summaries, logs, and full
  per-experiment result dumps (Leave-One-Author-Out ablation, topic-representation ablation,
  profiler-prototype development).
- **[`EXPERIMENTS.md`](EXPERIMENTS.md)** - the full narrative of every experiment: what was
  tried, why, and what was concluded.

## Future Work

- **Identify the leading account(s) per narrative group** — for each of the 7 narratives, the
  Twitter/Telegram scrapers currently pull from a fixed list of accounts/channels treated
  equally (see `NARRATIVES_ACCOUNTS` in `data/build_twitter_dataset.py`). A useful extension is to
  determine which account within each group acts as the primary/most influential voice
  ("group leader"), e.g. by engagement volume, retweet/citation frequency by the other accounts
  in the same group, or centrality in a narrative-specific interaction graph:
  - **Zionist**: `Israel`, `IDF`, `StandWithUs`, `AIPAC`, `IsraelMFA`, `AJCGlobal`, `JNS_org`
  - **Resistance**: `khamenei_ir`, `PressTV`, `QudsNen`, `IrnaEnglish`, `TehranTimes79`, `MayadeenEnglish`
  - **Western**: `NATO`, `EU_Commission`, `POTUS`, `StateDept`, `FCDOGovUK`, `GermanyDiplo`
  - **Russian**: `KremlinRussia_E`, `mfa_russia`, `RussiaUN`, `RT_com`, `SputnikInt`, `tassagency_en`
  - **Ukrainian**: `ZelenskyyUa`, `Ukraine`, `DefenceU`, `MFA_Ukraine`, `GeneralStaffUA`, `United24media`
  - **Right-wing**: `FoxNews`, `BenShapiro`, `dailywire`, `Heritage`, `TPUSA`
  - **Left-wing**: `novaramedia`, `BernieSanders`, `jacobin`, `democracynow`, `thenation`

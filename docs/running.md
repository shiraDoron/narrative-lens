# Running the project

## Setup

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
dependency declaration and [`configs/README.md`](../configs/README.md) for the YAML config
philosophy.

```bash
# Quick smoke test (random split - NOT the headline research result, see docs/results.md):
python -m narrative_lens.train --model sbert_only --split random

# Build the cross-model comparison table (artifacts/tables/model_comparison_results.json):
python -m narrative_lens.evaluation.compare_models

# Run the test suite:
pytest tests/ -q
```

## All CLI commands

All scripts must be run **from the repository root** as a module (`python -m
narrative_lens...`), not from inside `src/` or `experiments/`, since their internal paths
(`data/raw/...`, `models/...`, `artifacts/...`) are relative to the project root.

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

# Build the cross-model comparison table (artifacts/tables/model_comparison_results.json):
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

## Reproduce the headline finding

This project's research focus moved from "which architecture wins on a random split" to "does
the classifier generalize to an unseen author, or does it rely on an author-identity shortcut"
(see [`EXPERIMENTS.md`](../EXPERIMENTS.md)'s "Research storyline" table and §18–§28). These 3
commands, run in order, let you see that story directly instead of just reading about it:

1. **Random-split baseline** (fast, a few minutes on CPU):
   ```bash
   python -m narrative_lens.train --model sbert_only --split random
   ```
   Runs/overwrites: `data/cache/cached_features_sbert_only.pt`,
   `models/best_model_sbert_only.pth`. What it does: trains the plain-SBERT classifier on a
   standard random train/val/test split and prints test-set Accuracy/Macro-F1. Expected
   qualitative outcome: performance in the same range as the other `--model` choices
   in-distribution — this step alone does **not** show any generalization problem (see
   [`docs/results.md`](results.md) for the frozen, already-measured comparison numbers).

2. **Unseen-author (LOAO) evaluation** (slow — a full feature-extraction pass over the whole
   corpus is required per held-out author, documented at several hours wall-clock on a CPU-only
   machine; see [`EXPERIMENTS.md`](../EXPERIMENTS.md) §18 for the original timing note):
   ```bash
   python -m narrative_lens.train --model hybrid --split leave_one_author --held-out-author IDF
   ```
   Runs/overwrites: a new `data/cache/cached_features_*_loao_IDF.pt`, a new checkpoint under
   `models/`. What it does: trains from scratch with every post by `IDF` held out entirely, then
   reports recall on that author's held-out posts. Expected qualitative outcome: recall well
   below the random-split Zionist F1 reported in `docs/results.md` — the generalization gap
   documented in [`EXPERIMENTS.md §18`](../EXPERIMENTS.md#18-narrative-classification--leave-one-author-out-loao-generalization-test).
   If you don't want to wait for a fresh training run, the already-computed, frozen numbers for
   this exact command are in `artifacts/experiments/narrative_ablation_loao/` and EXPERIMENTS.md
   §18-§19.

3. **Author-signature diagnostic** (fast — fits a Decision Tree on cached features, no
   SBERT/BERTopic re-inference):
   ```bash
   python experiments/author_generalization/narrative_author_signature_diagnostics.py
   ```
   Note: this script has no CLI flags - it runs its full analysis unconditionally when invoked
   (no `--help`/dry-run mode), per this project's convention for one-off research scripts; it
   does not modify any production model/checkpoint. What it does: tries to predict *which
   specific author* wrote a text using only surface-level style features (text length,
   punctuation, mentions), both globally and within each single fixed narrative. Expected
   qualitative outcome: author-identification accuracy far above the majority-class/chance
   baseline in every narrative — direct evidence that narrative labels partly encode *who wrote
   it*, not just *what it says* (frozen numbers in
   [`EXPERIMENTS.md §27`](../EXPERIMENTS.md#27-author-signature-diagnostics--does-the-text-itself-identify-its-author-decision-tree)
   and `artifacts/experiments/narrative_author_signature_diagnostics/`).

## Reproducing the experiments in `EXPERIMENTS.md`

Every experiment documented in [`EXPERIMENTS.md`](../EXPERIMENTS.md) has its code under
`experiments/{topic_modeling,feature_ablation,author_generalization}/`, runnable the same way,
e.g. `python experiments/topic_modeling/experiment_a_min_topic_size.py`. See
[`experiments/README.md`](../experiments/README.md) for the full list and what each folder covers.

## Environment variables (secrets)

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

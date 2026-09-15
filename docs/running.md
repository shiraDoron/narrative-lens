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
# Train the current recommended configuration (see docs/results.md):
python -m narrative_lens.train --model sbert_only --split random

# Build the cross-model comparison table (reports/tables/model_comparison_results.json):
python -m narrative_lens.evaluation.compare_models

# Run the test suite:
pytest tests/ -q
```

## All CLI commands

All scripts must be run **from the repository root** as a module (`python -m
narrative_lens...`), not from inside `src/` or `experiments/`, since their internal paths
(`data/raw/...`, `models/...`, `reports/...`) are relative to the project root.

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

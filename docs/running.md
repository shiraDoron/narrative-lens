# Running the project

## Setup

Run commands from the **repository root** (the directory containing `pyproject.toml`), after cloning and entering it. Use Python 3.11 for the active style-study environment. Choose the setup block for your shell; after activation, `python` refers to this environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:SETUPTOOLS_USE_DISTUTILS = "stdlib"
python -m pip install -e ".[dev]"
```

Linux/macOS Bash:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Alternatively, `python -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu` installs the pinned dependency set validated on the original CPU-only Windows environment. It is not a portability guarantee for every platform. If activation is unavailable, invoke `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/macOS) directly.

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

Package entry points run **from the repository root** as modules (`python -m
narrative_lens...`); standalone experiment scripts use `python path/to/script.py`. Do not run from inside `src/` or `experiments/`, since internal paths
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
   python -m narrative_lens.train --model baseline_fusion --split leave_one_author --held-out-author IDF
   ```
   Runs/overwrites: a new `data/cache/cached_features_*_loao_IDF.pt`, a new checkpoint under
   `models/`. What it does: trains from scratch with every post by `IDF` held out entirely, then
   reports recall on that author's held-out posts. Expected qualitative outcome: recall well
   below the random-split Zionist F1 reported in `docs/results.md` — the generalization gap
   documented in [`EXPERIMENTS.md §18`](../EXPERIMENTS.md#18-narrative-classification-leave-one-author-out-loao-generalization-test).
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
   [`EXPERIMENTS.md §27`](../EXPERIMENTS.md#27-author-signature-diagnostics-does-the-text-itself-identify-its-author-decision-tree)
   and `artifacts/experiments/narrative_author_signature_diagnostics/`).

## Reproducing the experiments in `EXPERIMENTS.md`

Most historical experiments documented in [`EXPERIMENTS.md`](../EXPERIMENTS.md) have code under
`experiments/{topic_modeling,feature_ablation,author_generalization}/`, runnable the same way,
e.g. `python experiments/topic_modeling/experiment_a_min_topic_size.py`. See
[`experiments/README.md`](../experiments/README.md) for the full list and what each folder covers.

## Active style follow-up reproduction

Start with [CURRENT_STATE.md](../CURRENT_STATE.md); select the exact version in the [artifact index](../artifacts/README.md#style-follow-up-navigation). Reading committed reports requires no model runtime. The recent prompt runs have **no new training results**; historical training commands below/elsewhere are reproduction options, not instructions to resume training now.

| Task | Required inputs | Output / guide |
|---|---|---|
| Audit the latest external review | Committed new-review CSV, frozen `comparison_30.csv`, earlier external-review `summary.json`; standard Python only | Per-row classifications, separate Borderline CSV, `summary.json`, audit and reports in the new-review directory; command below |
| Recompute prompt/style reports | Frozen generated rewrites, old/new comparison inputs, saved automatic scores, original train feature reference; existing study ML environment | [30-train local guide](../artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/README.md) lists each stage and outputs |
| Reproduce generation / semantic screening | Pinned Qwen GGUF + llama.cpp runtime from the predecessor, cached MPNet/DeBERTa/NER models, protocol settings, Python/ML dependencies | [V2 guide](../artifacts/experiments/style_intervention_v2_20261026/README.md) and [runtime setup](../artifacts/experiments/verified_human_style_followup_20261026/README.md); keep a new versioned directory for fresh generation |

The following import command is valid in PowerShell and Bash from the repository root. It uses the committed source copy and updates **derived review tables and documentation only**, with no LLM call, generation or training:

```bash
python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/import_review.py
```

Expected checks: 30 unique matching IDs, all train; meaning 10 Yes / 15 Borderline / 5 No; style 30 Yes; TP 19 / FP 5 / TN 5 / FN 1 relative to this LLM. Inputs and existing human-review fields remain unchanged. [Import contract and provenance limits](../artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/README.md).

Model weights, runtime binaries, publisher HTML snapshots, embeddings, NLI resume caches and checkpoints are not all committed. Existing generation orchestration was executed on Windows with its recorded llama.cpp executable; Linux/macOS generation is **not verified as copy-and-run**. Reproducing imported ratings means recomputing their summaries, not recreating the external model's judgments. **External LLM Review ≠ Human Validation**; Human Validation of this follow-up is Pending.

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

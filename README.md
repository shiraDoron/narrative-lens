# Narrative Detection & Profiling Pipeline

A research/thesis project studying how political/geopolitical text can be automatically
classified into a fixed set of **narratives** — `Zionist`, `Resistance`, `Western`, `Russian`,
`Ukrainian`, `Right-wing`, `Left-wing` — and how the agendas, rhetoric and ideology behind each
narrative can be profiled without supervision (`analyze_agendas.py`, independent of the trained
classifier).

**Research question**: does a hybrid architecture that fuses frozen sentence embeddings (SBERT)
with engineered linguistic features (named entities, semantic roles, emotion/agency, topic
assignment, source reliability) out-perform a purely learned (SBERT + MLP) or a purely
linear-fusion baseline — and how well does any of it generalize to unseen topics/authors rather
than just an i.i.d. random split?

- 📄 [Read the full experiment log](EXPERIMENTS.md) — every experiment: methodology, results, conclusions
- 📊 [Read the results summary](docs/results.md) — headline model comparison + generalization findings
- 🏗️ [Read the architecture](docs/architecture.md) — pipeline stages, fusion model, topic-model versions
- ▶️ [Read how to run everything](docs/running.md) — setup, CLI reference, secrets

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

## Project layout

```
final_project/
├── src/narrative_lens/     # installable package (`pip install -e .`) - config, train, models, features
├── configs/                # YAML configs - see configs/README.md
├── tests/                  # pytest suite
├── experiments/            # one-off research scripts, by theme - see experiments/README.md
├── data/                   # raw datasets, feature caches, profiles - see data/README.md
├── models/                 # checkpoints + saved topic models - see models/README.md
├── reports/                # comparison tables, profiling output, run logs - see reports/README.md
├── docs/                   # architecture, results, running instructions (linked above)
└── EXPERIMENTS.md          # full experiment narrative
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
$env:SETUPTOOLS_USE_DISTUTILS="stdlib"   # Windows/pyenv workaround for a distutils_hack bug
pip install -e ".[dev]"

python -m narrative_lens.train --model sbert_only --split random   # train the recommended config
pytest tests/ -q                                                   # run the test suite
```

See [`docs/running.md`](docs/running.md) for the full setup + CLI reference (all `--model`/
`--split` combinations, topic-model fitting, data collection, environment variables/secrets, and
how to reproduce every experiment in `EXPERIMENTS.md`).

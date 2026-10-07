# Narrative Detection & Profiling Pipeline

## What this project does

This project studies automatic classification of political/geopolitical text into one of seven
predefined **narratives** — `Zionist`, `Resistance`, `Western`, `Russian`, `Ukrainian`,
`Right-wing`, `Left-wing` — and, separately, how to characterize the agendas, rhetoric, and
ideology associated with each narrative once texts are grouped by it.

It consists of two components:

1. **A classifier** — reads a short text and labels it with one of 7 narratives:
   `Zionist`, `Resistance`, `Western`, `Russian`, `Ukrainian`, `Right-wing`, `Left-wing`.
2. **A profiler** (`analyze_agendas.py`) — takes texts already grouped by narrative and
   summarizes each group's recurring topics, tone, and ideological leaning. It doesn't need the
   classifier at all; it works directly off of texts that are already labeled.

### Why it's interesting (the research question)
A classifier of this kind can be built in more than one way: it can rely entirely on a modern
pretrained language model (SBERT) to represent meaning, or it can additionally be given
hand-engineered linguistic features (named entities, who-did-what-to-whom structure, emotional
tone, topic, source reliability). The central question is whether these additional engineered
features improve performance in a way that generalizes, or whether any apparent gain is
specific to the authors/topics seen during training and does not transfer to a previously unseen
author or topic. This generalization question — rather than raw in-sample accuracy — is the
primary subject of investigation in this project.

### A few terms used throughout this README and the code
- **SBERT** — a pretrained model that turns a sentence into a numeric vector capturing its
  meaning; used here "frozen" (not retrained), just as a ready-made meaning representation.
- **NER (Named Entity Recognition)** — detects names of people, organizations, places in text.
- **SRL (Semantic Role Labeling)** — detects "who did what to whom" structure in a sentence.
- **MLP (Multi-Layer Perceptron)** — a small standard neural network used as the final decision
  layer on top of whichever input features are given to it.
- **Fusion** — combining several different feature sources into one input before classifying.
- **LOAO (Leave-One-Author-Out)** — a stricter train/test split that hides one author's text
  entirely during training, to test generalization to an author the model has never seen.


- 📄 [Read the full experiment log](EXPERIMENTS.md) — every experiment: methodology, results, conclusions
- 📊 [Read the results summary](docs/results.md) — headline model comparison + generalization findings
- 🏗️ [Read the architecture](docs/architecture.md) — pipeline stages, fusion model, topic-model versions
- ▶️ [Read how to run everything](docs/running.md) — setup, CLI reference, secrets

## Architecture at a glance

Every text goes through several feature-extraction steps in parallel — each one a separate,
frozen "expert" module that turns the raw text into a narrative-oriented signal — and their
outputs are combined ("fused") into a single prediction:

```
raw text
   |
   +-> NER (ner.py)                    -+   who/what is mentioned
   +-> SRL / advcl (srl.py)             |   who did what to whom
   +-> Emotion + agency (emotion.py)     +->  fusion layer  ->  narrative (1 of 7)
   +-> Topic/stance (stance.py)          |   what topic, what stance        (fusion.py)
   +-> Reliability (reliability.py)    -+   how reliable is the source
   |
   +-> (Hybrid only) + frozen SBERT sentence embedding + agenda/ideology lexicon vectors
```

What each module contributes:

- **NER** — which people/organizations/places are named (e.g. mentioning "NATO" vs. "the
  resistance" is itself a narrative signal).
- **SRL / advcl** — the sentence's who-did-what-to-whom structure (e.g. who is framed as the
  actor vs. the victim).
- **Emotion + agency** — the dominant emotion expressed, plus whether the text uses active or
  passive voice (passive voice often hides who is responsible for an action).
- **Topic/stance** — which BERTopic topic the text belongs to, used as a proxy for stance.
- **Reliability** — a confidence score for how subjective/unreliable the source sounds.

None of these modules are trained together with the classifier — they run once per text as
fixed, frozen feature extractors. Only the **fusion layer** (`fusion.py`) that combines their
outputs into a final narrative label is what actually gets trained.

To answer the research question, three classifier variants share this same feature-extraction
machinery but differ only in what they feed into that final decision step, and are
trained/evaluated on **identical splits** for a fair comparison (`train.py --model ...`):

| `--model` | Class (`fusion.py`) | Description |
|---|---|---|
| `baseline_fusion` | `NarrativeDetector` | Linear weighted-sum fusion of the 5 feature layers above — no SBERT |
| `sbert_only` | `SBERTOnlyDetector` | Baseline: frozen SBERT embedding → MLP only, no engineered features at all |
| `hybrid` | `HybridNarrativeDetector` | SBERT + all 5 engineered feature layers + agenda/ideology lexicon vectors → MLP |

In other words: `baseline_fusion` tests the engineered features alone, `sbert_only` tests plain
SBERT alone, and `hybrid` tests whether combining both beats either one individually. Per
[`docs/results.md`](docs/results.md), `sbert_only` currently wins on a random split — the
engineered features aren't yet adding measurable value over SBERT alone.

## Project layout

```
final_project/
├── src/narrative_lens/     # installable package (`pip install -e .`) - config, train, models, features
├── configs/                # YAML configs - see configs/README.md
├── tests/                  # pytest suite
├── experiments/            # one-off research scripts, by theme - see experiments/README.md
├── data/                   # raw datasets, feature caches, profiles - see data/README.md
├── models/                 # checkpoints + saved topic models - see models/README.md
├── artifacts/               # comparison tables, profiling output, run logs - see artifacts/README.md
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

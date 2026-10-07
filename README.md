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

## The 7 narratives

Labels are assigned by *account/channel*, not per-text human judgment — see "Label provenance
matters" below for why that's an important caveat. The one-line definitions below describe what
each narrative's source accounts typically argue, not a guaranteed property of every single row.
Full definitions, account rosters, and real borderline examples are in
[`docs/narrative_definitions.md`](docs/narrative_definitions.md).

| Narrative | One-line operational definition | Main confusion risk |
|---|---|---|
| `Zionist` | Official Israeli state/military/advocacy framing — Israel's actions are legitimate/defensive, adversaries are terrorists. | `Resistance` (74 confusions — same conflict, opposite legitimacy framing) |
| `Resistance` | Iran / Axis-of-Resistance (Hezbollah/Houthi/Hamas-adjacent) framing — Israeli/US/Western action is aggression, armed resistance is legitimate. | `Zionist` (74 confusions — same conflict, opposite legitimacy framing) |
| `Western` | Official Western (US/EU/UK/NATO) government/IGO statements or alliance-solidarity framing — **not** simply "published by a Western outlet" (plain wire/human-interest content from the same accounts is not this narrative). | `Ukrainian` (36 confusions — shares vocabulary on the same war, but speaker differs: third-party ally vs. first-person combatant) |
| `Russian` | Pro-Kremlin framing of the Ukraine war/geopolitics — Russian actions justified/defensive, the West hypocritical/aggressive. | `Ukrainian` (73 confusions — opposite sides of the same war) |
| `Ukrainian` | Pro-Ukraine framing of the war — Ukrainian sovereignty/resistance to Russian aggression, appeals for international support. | `Russian` (73 confusions — opposite sides of the same war) |
| `Right-wing` | US-centric conservative/populist commentary — anti-immigration, anti-"woke," pro-Trump, culture-war framing. | `Left-wing` (75 confusions — the single largest confusion pair in the dataset; opposite partisan valence on the same domestic US topics) |
| `Left-wing` | US/UK-centric progressive/socialist commentary — pro-labor, anti-Trump, pro-Palestinian-solidarity on Israel/Gaza, pro-immigration. | `Right-wing` (75 confusions — opposite partisan valence on the same domestic US topics) |

## Current research findings (TL;DR)

The full story is in [`EXPERIMENTS.md`](EXPERIMENTS.md#research-storyline-start-here) and
[`docs/results.md`](docs/results.md); this is the short version:

- **In-distribution (random split), the plain SBERT baseline wins.** `sbert_only` beats both
  `hybrid` and `baseline_fusion` on a standard random train/val/test split — the hand-engineered
  features (NER/SRL/emotion/topic/reliability) aren't adding measurable value here.
- **But that result doesn't generalize to an unseen author.** Under a stricter
  Leave-One-Author-Out (LOAO) split, recall drops 20–38 percentage points relative to the
  random-split numbers, and for 2 of the 3 authors tested the model systematically misroutes
  their text to `Right-wing` regardless of true narrative (EXPERIMENTS.md §18–§19).
- **Part of the problem is an author-identity shortcut, not narrative content.** A simple
  decision tree can predict *which specific author* wrote a text using only surface style
  features (text length, punctuation, mentions, etc.) — with accuracy far above chance even
  **within a single fixed narrative** (e.g. 85.1% for `Western` vs. a ~20% majority-class
  baseline). This means narrative labels partly encode *who wrote it*, not just *what it says*
  (EXPERIMENTS.md §27).
- **Entity-masking as a fix did not hold up under a pre-registered confirmatory test.** Masking
  named entities during training looked promising in exploratory testing on 3 authors (helping
  one, hurting two), but a later confirmatory evaluation on 14 fresh, previously unseen authors
  found the masking policy did **not** generalize (`NON-INFERIOR = FALSE`, EXPERIMENTS.md §21–§25).
- **Removing the author-style signal did not improve unseen-author generalization either.**
  Normalizing surface style (URLs, mentions, hashtags, emoji, repeated characters) before
  classification *did* measurably reduce the author-signature effect from §27 (avg ≈−15pp
  macro-F1 in a decision-tree author-ID test), confirming the intervention worked as intended —
  but fresh-author recall on the same 14 held-out authors got **worse**, not better (13 of 14
  authors regressed, mean −6.4pp, median −10.8pp), while in-distribution (random-split)
  performance stayed roughly flat. The conclusion: an author-specific style signal clearly
  exists, but there is currently no evidence it is a harmful shortcut whose removal improves
  generalization (EXPERIMENTS.md §28).

### Current research setup

A reader should not conclude that this project's main contribution today is "SBERT + engineered
fusion vs. SBERT-only on a random split" — that was the **starting point** (EXPERIMENTS.md
§1–§17 for the topic-modeling track, plus the initial §15/§17 model comparisons), but the
research focus has since moved to unseen-author generalization and author-identity shortcuts
(§18–§28), which is where most current effort and all of §18 onward is concentrated:

- **Main in-distribution baseline**: `sbert_only` (`SBERTOnlyDetector` in `fusion.py`) — a frozen
  SBERT embedding → MLP, no engineered features (current random-split numbers are in "Current
  research findings" above and [`docs/results.md`](docs/results.md)).
- **Architecture most generalization analyses (§18–§28) are actually built on**: **not** the
  production `fusion.py` models directly, except for §18's initial LOAO diagnostic (which used
  `baseline_fusion`). From §19 onward, every experiment uses a separate, deliberately simpler
  **"SBERT + explicit single-feature-arm" ablation architecture**
  (`AblationDetector`/`TopicFeatureLayer`-based scripts under `experiments/author_generalization/`
  and `experiments/feature_ablation/`) — this isolates one feature's effect on generalization at
  a time (NER alone, Soft Topics alone, masked text alone, etc.), which the full multi-arm fusion
  architecture cannot do as cleanly. Results from this ablation architecture are the evidentiary
  basis for §19–§28's conclusions, not the production `HybridNarrativeDetector`/`NarrativeDetector`
  classes.
- **Current research question**: does the classifier rely on an author-identity "shortcut"
  (entity identity, surface style/formatting) that inflates in-distribution accuracy but fails to
  transfer to a previously unseen author — and if so, can a training-time or pre-processing
  intervention (entity masking, style normalization) remove that shortcut without hurting
  generalization? As of EXPERIMENTS.md §28, the answer so far is: the shortcut signal is real and
  measurable (§27), but no intervention tried to date (masking in §21–§25, style normalization in
  §28) has been shown to improve unseen-author generalization — several made it worse.
- **Role of Hybrid/Fusion (`fusion.py`) today**: **historical / comparison branch, not the
  active research architecture.** `NarrativeDetector` (`baseline_fusion`) and
  `HybridNarrativeDetector` (`hybrid`) remain the reference points for the original
  in-distribution model comparison (`docs/results.md`) and were the architecture behind §18's
  first LOAO result, but they are not being modified or retrained as part of the ongoing
  generalization-shortcut research — that work happens in the separate ablation architecture
  described above.

## Dataset at a glance

- **16,510 texts** total across 7 narratives (`Zionist`, `Resistance`, `Western`, `Russian`,
  `Ukrainian`, `Right-wing`, `Left-wing`), built from 4 source files in `data/raw/` (see
  [`data/README.md`](data/README.md) for exact producing scripts):
  - **10,330 human-authored** — `telegram_natural_dataset.csv` (6,877 rows, via Telethon) +
    `twitter_natural_dataset.csv` (3,453 rows, via Selenium).
  - **6,180 synthetic (LLM-generated)** — `gemini_natural_dataset.csv` (5,600 rows) +
    `gpt_natural_dataset.csv` (580 rows), generated to target a specific narrative.
- **How the 7 narratives were decided**: for the human-authored data, each narrative maps to a
  fixed, manually curated list of Twitter accounts / Telegram channels (`NARRATIVES_ACCOUNTS` /
  `NARRATIVES_CHANNELS` in `src/narrative_lens/data/build_twitter_dataset.py` /
  `build_telegram_dataset.py`) — the narratives were not discovered via clustering or other
  data-driven means. See [`docs/narrative_definitions.md`](docs/narrative_definitions.md) for the
  full definitions.
- **Label provenance matters**: for human-authored text, `narrative_name` is assigned by *which
  account/channel a text came from*, not by an independent, text-level human judgment of what the
  text actually argues. This is an important caveat when interpreting accuracy numbers — a model
  can score well by learning account-specific style instead of narrative content (see "Current
  research findings" above). A blind, text-only human-validation pilot
  (`data/annotation/human_validation_pilot_300_blind.csv`, 300 texts with narrative/author/platform
  redacted) exists to check whether labels are actually text-supported; see
  [`docs/label_quality_audit.md`](docs/label_quality_audit.md) for the methodology and current
  status.

### Why it's interesting (the research question)
This project's original framing: a text classifier can rely entirely on a modern pretrained
language model (SBERT) to represent meaning, or it can additionally be given hand-engineered
linguistic features (named entities, who-did-what-to-whom structure, emotional tone, topic,
source reliability) — and the open question is whether those extra features help in a way that
generalizes, rather than just fitting the authors/topics seen during training. See "Current
research setup" above for where that question stands today and what it has evolved into.

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
   +-> Topic representation (stance.py)  |   which BERTopic topic         (fusion.py)
   +-> Reliability (reliability.py)    -+   how reliable is the source
   |
   +-> (Hybrid only) + frozen SBERT sentence embedding + agenda/ideology lexicon vectors
```

> **Naming note**: the module is still called `stance.py` for historical reasons — an earlier
> version of the pipeline had a real support/oppose stance dimension that was later removed.
> Today it only produces a BERTopic topic assignment (hard id or soft distribution); there is no
> stance/sentiment signal left in it.

What each module contributes:

- **NER** — which people/organizations/places are named (e.g. mentioning "NATO" vs. "the
  resistance" is itself a narrative signal).
- **SRL / advcl** — the sentence's who-did-what-to-whom structure (e.g. who is framed as the
  actor vs. the victim).
- **Emotion + agency** — the dominant emotion expressed, plus whether the text uses active or
  passive voice (passive voice often hides who is responsible for an action).
- **Topic representation** (`stance.py` — legacy module name, see naming note above) — which
  BERTopic topic the text belongs to (hard id or soft distribution).
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
SBERT alone, and `hybrid` tests whether combining both beats either one individually. See
["Current research findings"](#current-research-findings-tldr) above and
[`docs/results.md`](docs/results.md) for which one currently wins and why that isn't the full
story.

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

python -m narrative_lens.train --model sbert_only --split random   # quick smoke test (~minutes)
pytest tests/ -q                                                   # run the test suite
```

This smoke test just confirms the pipeline runs end-to-end on a random split — it is **not** the
headline result. See [`docs/running.md`](docs/running.md) for the full setup + CLI reference (all
`--model`/`--split` combinations, topic-model fitting, data collection, environment
variables/secrets, and how to reproduce every experiment in `EXPERIMENTS.md`).

### Research evaluation

The result that actually matters for this project's research question is generalization to an
unseen author, not the random-split smoke test above:

```bash
python -m narrative_lens.train --model hybrid --split leave_one_author --held-out-author IDF
```

See ["Current research findings"](#current-research-findings-tldr) above, the "Generalization
evaluation" section of [`docs/results.md`](docs/results.md), and EXPERIMENTS.md §18, §19, §25 for
the full LOAO / fresh-author results.

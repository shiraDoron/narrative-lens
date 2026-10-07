# Narrative Lens: Do Narrative Classifiers Generalize to Unseen Authors?

Short political texts are labeled with one of 7 narratives (`Zionist`, `Resistance`, `Western`, `Russian`, `Ukrainian`, `Right-wing`, `Left-wing`). In-distribution accuracy looks strong, but labels are assigned by account/channel, not per-text human judgment, so a model can score well by learning who wrote a text instead of what it argues. This repo tests whether that happens: four zero-shot interventions (entity masking, style normalization, noise removal, group-DRO) all failed to restore generalization to unseen authors, but few-shot adaptation works.

## Research questions

Derived from EXPERIMENTS.md Sections 18 to 28. Full arc: [EXPERIMENTS.md](EXPERIMENTS.md#research-storyline-start-here).

- **RQ1 (in-distribution vs. LOAO gap):** does classification accuracy hold when the test author was excluded from training (Leave-One-Author-Out)? (Sections 18, 19)
- **RQ2 (entity shortcut):** is the LOAO drop driven by memorized named-entity identities, and does training-time entity masking close the gap on fresh authors? (Sections 21 to 25)
- **RQ3 (style shortcut):** can surface author style alone identify the author within a fixed narrative, and does normalizing that style improve unseen-author generalization? (Sections 27, 28)

## Dataset snapshot

- **16,510 texts** across 7 narratives: **10,330 human-authored** (Telegram 6,877 + Twitter 3,453) and **6,180 synthetic** (Gemini 5,600 + GPT 580). Source files and producing scripts: [data/README.md](data/README.md).
- **Caveat:** human-authored labels come from the source account/channel roster, not text-level annotation. A 300-text blind human-validation pilot checks whether labels are text-supported: [docs/label_quality_audit.md](docs/label_quality_audit.md).
- Narrative definitions, account rosters, borderline cases: [docs/narrative_definitions.md](docs/narrative_definitions.md).

## Headline findings

Details: [docs/results.md](docs/results.md). All numbers below trace to that file or the EXPERIMENTS.md storyline table.

- **Random split: plain SBERT baseline wins.** `sbert_only` reaches 0.732 accuracy / 0.730 macro-F1, ahead of `hybrid` (0.722 / 0.717) and `baseline_fusion` (0.671 / 0.664). Engineered features add no measurable value here.
- **RQ1: LOAO recall drops 20 to 38pp** relative to the random split, and 2 of 3 tested authors are systematically misrouted to `Right-wing` (Sections 18, 19).
- **Labels are text-supported but noisy.** A 300-text blind validation agrees with provenance labels at 0.7727 accuracy (kappa 0.7348); the hard-disagreement (noise) rate is 0.1988.
- **Removing 202 noisy rows shows no systematic effect across seeds 42/43/44 (Bernie mean delta +0.0017, sign flips; Section 34A).**
- **The gap is not an event confound.** The event-matched LOAO gap is -36.3pp, showing no shrinkage versus -30.9pp mismatched.
- **Fresh single-author training collapses harder (recall 0.006, gap -73.4pp; Section 34B).**
- **RQ2: entity identity correlates but does not cause errors.** The entity-swap ACE is +0.043. Exploratory masking helped one author and hurt two (Sections 23, 24); the pre-registered test on 14 fresh authors returned `NON-INFERIOR = FALSE` (Section 25).
- **RQ3: style identifies authors but removing it hurts.** A decision tree predicts the author within a fixed narrative far above chance (`Western`: 85.1% vs. about 20% baseline, Section 27). Normalizing style cut that signal (about minus 15 points macro-F1) yet fresh-author recall regressed for 13 of 14 authors (mean minus 6.4pp, median difference -10.8pp of group medians, Section 28).
- **Group-DRO confirmatory: NOT_SUPPORTED.** Mean recall 33.3% vs 39.0% baseline, median 30.8% vs 38.8%, guardrail 3/14 (Section 33).
- **Labeling 10 rows from a new author recovers recall to 64.9% mean (median 65.0%) with no retraining, vs 39.0% zero-shot (Section 35A).**

## Repo map

```
src/narrative_lens/     # package: features, models (fusion.py), train, configs
configs/                # YAML configs
tests/                  # pytest suite
experiments/            # one-off research scripts by theme
data/                   # raw datasets, caches, profiles
models/                 # checkpoints + saved topic models
artifacts/              # comparison tables, run logs, profiling output
docs/                   # architecture, results, running, label audit
EXPERIMENTS.md          # full experiment log (Sections 1 to 33)
```

Pipeline stages and model variants: [docs/architecture.md](docs/architecture.md).

## Quickstart

```bash
pip install -e ".[dev]"
python -m narrative_lens.train --model sbert_only --split random
pytest tests/ -q
python -m narrative_lens.train --model hybrid --split leave_one_author --held-out-author IDF
```
Run `python -m narrative_lens.evaluation.compare_models` for the headline table.

The smoke test above only confirms the pipeline runs. For setup, all `--model`/`--split` combinations, and how to reproduce each experiment, read [docs/running.md](docs/running.md). Note: generalization analyses from EXPERIMENTS.md §19 onward use the separate `AblationDetector` ablation architecture under `experiments/author_generalization/` and `experiments/feature_ablation/`, not the production `fusion.py` classes (which back only §18).

## Further reading

- [EXPERIMENTS.md](EXPERIMENTS.md): every experiment, methodology, and conclusion
- [docs/results.md](docs/results.md): headline model comparison and generalization results
- [docs/architecture.md](docs/architecture.md): pipeline stages and fusion models
- [docs/running.md](docs/running.md): setup and CLI reference

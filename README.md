# Narrative Lens: Meaning-Preserving Style Interventions and Unseen-Author Generalization

**Central research question: Can meaning-preserving author-style interventions improve political narrative classification generalization to unseen authors?**

The candidate contribution is empirical and methodological: compare Original, Paraphrase, Style Rewrite and matched augmentation on common source IDs, evaluating Original texts from unseen authors. Author-style shortcuts are a hypothesis, not an established mechanism. Style Pooling, CATO and Shortcut Maze already study closely related ideas; we do not claim to invent style transfer or to be first to test style shortcuts.

Historical work uses seven broad labels (`Zionist`, `Resistance`, `Western`, `Russian`, `Ukrainian`, `Right-wing`, `Left-wing`), largely assigned by account/channel. The current bylined-opinion follow-up is restricted to **Left/Right machine proposals at text level**, pending human gold. These label spaces and datasets must not be conflated. Prior interventions did not establish a stable generalization recovery; few-shot adaptation helped with labeled target-author support in its separate historical protocol.

## Current work / Active follow-up

The five-arm main experiment is **prepared but not ready to train**: 105 eligible train sources (55 Left/50 Right), ordinary Paraphrases for all, and 30 existing Style Rewrites; **75 Style Rewrites are missing**. The pipeline, 25 configs and reproducible fixed-budget batch schedules are prepared. No A–E training or new test evaluation was run. Human templates remain blank on disk; the complete per-ID ratings currently available are Claude's **External LLM Review**, not Human Validation. Original ChatGPT prompt/model/parameters are unknown, so no additional rewrites were generated. See [CURRENT_STATE.md](CURRENT_STATE.md).

Start with [Thesis research direction](THESIS_RESEARCH_DIRECTION_HE.md), [Main training protocol A–E](MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md), [Deep Related Work: 18 papers](RELATED_WORK_DEEP_REVIEW_HE.md), [comparison matrix](RELATED_WORK_COMPARISON.md), [possible contribution](RESEARCH_GAP_AND_CONTRIBUTION_HE.md) and [BibTeX](REFERENCES.bib).

## Suggested reading path

If you are new to the project (5–10 minutes):

1. [README.md](README.md) — research question and headline findings.
2. [CURRENT_STATE.md](CURRENT_STATE.md) — what is active, established and still unproven.
3. [EXPERIMENTS.md: Research storyline](EXPERIMENTS.md#research-storyline-start-here) — the research history; stop before the lab notebook unless you need details.
4. [data/README.md](data/README.md) — datasets, label provenance and frozen holdouts.
5. [docs/running.md](docs/running.md) — setup, inputs, outputs and reproduction routes.
6. [artifacts/README.md](artifacts/README.md) — experiment outputs, status and local guides.

For the scientific evidence: [Evidence Matrix](EVIDENCE_MATRIX_HE.md) and [frozen sensitivity pilot](STYLE_SENSITIVITY_PILOT_HE.md). The older [technical TST review](docs/style_transfer_related_work_he.md) and [architecture proposal](docs/semantic_style_intervention_design_he.md) remain historical background, not the current contribution or an implemented new system.

## Research questions

Derived from EXPERIMENTS.md Sections 18 to 35. Full arc: [EXPERIMENTS.md](EXPERIMENTS.md#research-storyline-start-here).

- **RQ1 (in-distribution vs. LOAO gap):** does classification accuracy hold when the test author was excluded from training (Leave-One-Author-Out)? (Sections 18, 19)
- **RQ2 (entity shortcut):** is the LOAO drop driven by memorized named-entity identities, and does training-time entity masking close the gap on fresh authors? (Sections 21 to 25)
- **RQ3 (style shortcut):** can surface author style alone identify the author within a fixed narrative, and does normalizing that style improve unseen-author generalization? (Sections 27, 28)
- **RQ4 (what explains the gap):** to what extent can label noise, event/topic confounding, entity dependence, and robustness interventions explain or mitigate the degradation observed for unseen authors? (Sections 29 to 34)
- **RQ5 (few-shot recovery):** how much labeled data from a previously unseen author is needed to recover performance, and how effective is few-shot adaptation compared with zero-shot generalization? (Sections 35, 36)

## Dataset snapshot

- **16,510 texts** across 7 narratives: **10,330 human-authored** (Telegram 6,877 + Twitter 3,453) and **6,180 synthetic** (Gemini 5,600 + GPT 580). Source files and producing scripts: [data/README.md](data/README.md).
- **Caveat:** human-authored labels come from the source account/channel roster, not text-level annotation. A 300-text blind human-validation pilot checks whether labels are text-supported: [docs/label_quality_audit.md](docs/label_quality_audit.md).
- Narrative definitions, account rosters, borderline cases: [docs/narrative_definitions.md](docs/narrative_definitions.md).

## Headline findings

Details: [docs/results.md](docs/results.md). All numbers below trace to that file or the EXPERIMENTS.md storyline table.

- **Random split: plain SBERT baseline wins.** `sbert_only` reaches 0.732 accuracy / 0.730 macro-F1, ahead of `hybrid` (0.722 / 0.717) and `baseline_fusion` (0.671 / 0.664). Engineered features add no measurable value here. (Background, Sections 15-20.)
- **RQ1: held-out-account performance is weak.** Initial LOAO recalls were 53.5%, 31.0% and 28.0%; 2 of 3 accounts were often misrouted to `Right-wing`. The older “20–38pp gap” subtracts random per-class F1 from LOAO recall, so it is not a clean recall effect size (Sections 18, 19; [evidence audit](EVIDENCE_MATRIX_HE.md)).
- **RQ2: entity masking does not generalize.** Exploratory masking helped one author and hurt two (Sections 23, 24); the pre-registered test on 14 fresh authors returned `NON-INFERIOR = FALSE` (Section 25).
- **RQ3: style predicts author identity; the tested normalization did not improve generalization.** A decision tree predicts the author within a fixed narrative far above chance (`Western`: 85.1% vs. about 20% baseline, Section 27). Normalizing style cut that measured signal (about minus 15 points macro-F1) yet fresh-author recall regressed for 13 of 14 authors (mean minus 6.4pp, median difference -10.8pp of group medians, Section 28). This does not establish that removing author style caused the regression.
- **RQ4: label noise, event confounding, entity causality, and Group-DRO don't explain or close the gap.**
  - Labels are text-supported but noisy: a 300-text blind validation agrees with provenance labels at 0.7727 accuracy (kappa 0.7348); the hard-disagreement (noise) rate is 0.1988 (Section 29).
  - Removing 202 noisy rows shows no systematic effect across seeds 42/43/44 (Bernie mean delta +0.0017, sign flips; Section 34A).
  - The gap is not an event confound: the event-matched LOAO gap is -36.3pp, showing no shrinkage versus -30.9pp mismatched (Section 31).
  - Fresh single-author training collapses harder (recall 0.006, gap -73.4pp; Section 34B).
  - Entity identity correlates but does not cause errors: the entity-swap ACE is +0.043, barely above placebo (Section 32).
  - Group-DRO confirmatory: `NOT_SUPPORTED`. Mean recall 33.3% vs 39.0% baseline, median 30.8% vs 38.8%, guardrail 3/14 (Section 33).
- **RQ5: few-shot adaptation recovers recall; zero-shot fixes do not.** Labeling 10 rows from a new author recovers recall to 64.9% mean (median 65.0%) with no retraining, vs 39.0% zero-shot (Section 35A). A multi-seed re-test (5 independent sampling seeds per k, Section 36) confirms the k=10 magnitude (65.7% mean) but shows the curve is not monotonic: a single example (k=1) is unreliable and underperforms zero-shot for 9 of 14 authors, k=5-10 is where adaptation becomes reliable (12-13 of 14 authors improve), and one author with an already-strong zero-shot baseline (`United24Media`) resists adaptation at every k tested.

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
EXPERIMENTS.md          # full chronological experiment log (see Research storyline table)
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

The smoke test above only confirms the pipeline runs. For setup, all `--model`/`--split` combinations, and how to reproduce each experiment, read [docs/running.md](docs/running.md). Note on architectures: Section 18 uses the original `fusion.py` pipeline (`baseline_fusion`); Sections 19-28 primarily use the dedicated `AblationDetector`-based generalization/ablation pipeline under `experiments/author_generalization/` and `experiments/feature_ablation/`; later experiments (Sections 29-35) each use a task-specific script instead of a shared architecture, for label-quality analysis, matched-event evaluation, entity attribution, Group-DRO, few-shot adaptation, and selective prediction respectively.

## Further reading

- [EXPERIMENTS.md](EXPERIMENTS.md): every experiment, methodology, and conclusion
- [docs/results.md](docs/results.md): headline model comparison and generalization results
- [docs/architecture.md](docs/architecture.md): pipeline stages and fusion models
- [docs/running.md](docs/running.md): setup and CLI reference

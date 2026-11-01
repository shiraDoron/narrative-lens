# `artifacts/`

Start with [CURRENT_STATE.md](../CURRENT_STATE.md) for the active question; use this page to locate evidence, not to choose a new experiment.

## Style follow-up navigation

`Current` means the active research line, not a running process. `Superseded` identifies the development successor; historical results remain valid for their original scope. Paths and outputs are retained in place.

| Experiment | Status | Purpose | Main human-readable result | Raw artifacts | Reproduce |
|---|---|---|---|---|---|
| Earlier normalization (§28) | Closed / Historical | Test style normalization on unseen social-media authors | [Lab notebook §28](../EXPERIMENTS.md#28-style-normalization-intervention-does-removing-author-specific-formattingstyle-signal-improve-unseen-author-generalization) | [Outputs](experiments/narrative_style_normalization_author_signature/) | [Reproduction in §28](../EXPERIMENTS.md#reproducibility) |
| Controlled author-style pilot | Superseded by bylined-writer follow-up | Separate rewriting effects from original text | [Report](experiments/author_style_controlled_20261026/final_research_report_he.md) | [Pilot directory](experiments/author_style_controlled_20261026/) | [Local guide](experiments/author_style_controlled_20261026/README.md) |
| Verified-bylined-writer follow-up | Superseded by V2 for normalization development | Explore two-narrative, author-disjoint evaluation; labels remain machine proposals | [Results](experiments/verified_human_style_followup_20261026/RESULTS_HE.md) | [Frozen outputs](experiments/verified_human_style_followup_20261026/) | [Local guide](experiments/verified_human_style_followup_20261026/README.md) |
| Style intervention V2 | Current parent study; Human Validation Pending | Strengthen normalization with unchanged preservation checks | [Central guide](experiments/style_intervention_v2_20261026/EXPERIMENT_GUIDE_HE.md) / [Final report](experiments/style_intervention_v2_20261026/FINAL_REPORT_HE.md) | [V2 directory](experiments/style_intervention_v2_20261026/) | [Local guide](experiments/style_intervention_v2_20261026/README.md) |
| First External LLM Review (Old Normalized) | Closed / Historical | Diagnose old rewrites; not human validation | [Review summary](experiments/style_intervention_v2_20261026/external_llm_review_20261101/EXTERNAL_LLM_REVIEW_SUMMARY_HE.md) | [Imported review](experiments/style_intervention_v2_20261026/external_llm_review_20261101/) | [Import guide](experiments/style_intervention_v2_20261026/external_llm_review_20261101/README.md) |
| Train prompt revision, 30 texts | Current; generation/screening completed | Original-only rewriting on a train diagnostic cohort | [Original / Old / New](experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/COMPARISON_30_HE.md) | [Run directory](experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/) | [Local guide](experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/README.md) |
| External LLM Review — New Normalized | Current decision evidence; import completed | Compare semantic/style judgments with guards; keep Borderline separate | [Report](experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/REPORT_HE.md) | [All 30 classifications](experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/discrepancy_classification_30.csv) | [Import guide](experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/README.md) |

**External LLM Review ≠ Human Validation.** Automated guards measure operational risks; model-generated labels are proposals; external LLM ratings are a separate diagnostic; only an actual human reviewer can supply Human Validation. That validation is **Pending** for the active follow-up; no LLM import changes `human_verified=False`.

## How this fits together with `experiments/`, `models/`, and `EXPERIMENTS.md`

Four related-but-distinct locations, each with one job:

- **`experiments/`** (repo root) - most historical *code* that runs an experiment: one script per
  experiment/tool, organized by theme (`experiments/{topic_modeling,feature_ablation,
  author_generalization}/`). Newer style studies also keep versioned orchestration code beside their artifacts; use the local guide in the table above.
- **`artifacts/experiments/`** (this directory's `experiments/` subfolder, below) - the
  *generated* outputs of running that code: raw results.json files, confusion matrices, run logs,
  per-experiment summary CSVs, local protocols/reports and imported external reviews. Numerical regeneration uses frozen inputs and local guides; live collection, model downloads and external judgments are not all reproducible from code alone.
- **`models/`** (repo root) - saved model/checkpoint artifacts (`.pth` files, saved BERTopic
  model directories) produced by training runs. Binary, not human-readable; `artifacts/experiments/`
  is where the human-readable metrics/results *about* those checkpoints live.
- **`EXPERIMENTS.md`** (repo root) - the canonical, human-readable *interpretation* of every
  completed experiment: methodology, results tables, conclusions, and an explicit status tag
  (see its "Experiment status legend"). This is the file to read to understand *what an
  experiment found*; `artifacts/experiments/` is where to go to verify the raw numbers behind
  that interpretation.

> **If a raw artifact under `artifacts/experiments/` and `EXPERIMENTS.md` appear to disagree,
> `EXPERIMENTS.md` contains the canonical documented interpretation of the completed
> experiment** — but this is not a license to paper over a real discrepancy. A genuine mismatch
> (e.g. a number in `EXPERIMENTS.md` that doesn't match the underlying `results.json`) is a bug in
> the documentation and should be flagged/fixed by re-checking the raw artifact, not silently
> trusted or silently overwritten.

## Contents of this directory

Generated analysis outputs, split by purpose:

- **`tables/`** - curated, small comparison tables meant to be read directly (cross-model
  comparison, agenda-coverage counts). Produced by `narrative_lens.evaluation.compare_models` and
  `narrative_lens.evaluation.check_agenda_coverage`.
- **`agenda_profiling/`** - all output of `narrative_lens.features.analyze_agendas` (per-narrative
  agendas, rhetoric, ideology, style, keyword, similarity, and per-account diversity CSVs + 2 PNG
  charts + a text summary report).
- **`experiments/`** - raw, per-run/per-experiment result dumps: confusion matrices and split
  summaries from `narrative_lens.train`, run logs, and one subfolder per experiment/tool, named
  after its producing script (e.g. `narrative_ablation_loao/`, `narrative_entity_shortcut/`,
  `narrative_stance_entity/`, `profiler_prototype/` - see `experiments/*/*.py`'s
  `REPORT_DIR`/`OUT_DIR` constant for the exact mapping). Most come from a script under
  `experiments/<theme>/` (methodology documented in [`EXPERIMENTS.md`](../EXPERIMENTS.md) and
  `experiments/README.md`); the `narrative_audit/` folder instead comes from the label-quality
  audit scripts in `src/narrative_lens/data/audit_*.py` / `analyze_human_validation.py`
  (documented in [`docs/label_quality_audit.md`](../docs/label_quality_audit.md) and
  [`docs/narrative_definitions.md`](../docs/narrative_definitions.md)). This list is not
  exhaustive and grows as new experiments are run - check the scripts themselves for the
  authoritative mapping.

Do not regenerate historical inputs to navigate the repository. Imported reviews are retained byte-for-byte; model/runtime downloads, caches and checkpoints may be excluded from Git. Each local guide states the required inputs and reproduction limits.

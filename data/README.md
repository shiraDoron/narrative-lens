# `data/`

## Which dataset should I use?

Quick orientation for anyone new to the repo — what each thing under `data/` (plus two
experiment-output locations referenced below) actually is, and whether you're allowed to touch it:

| What | Path | Purpose | Safe to edit/regenerate? | Role |
|---|---|---|---|---|
| Raw human-authored data | `data/raw/twitter_natural_dataset.csv`, `data/raw/telegram_natural_dataset.csv` | Real scraped Twitter/Telegram posts, the human-authored half of the corpus | **No** — not reproducible from code (scraped from a live source at collection time); committed as-is | Train/val/test (via `train.load_raw_data()`, combined with the synthetic files below) |
| Synthetic (LLM-generated) data | `data/raw/gemini_natural_dataset.csv`, `data/raw/gpt_natural_dataset.csv` | LLM-generated text targeting a specific narrative, used to supplement human-authored volume. **Note the filenames are legacy/misleading** — despite containing `natural` in the name, this is 100% synthetic, LLM-generated text, not naturally-occurring social-media posts; the name predates a later naming convention and was never renamed to avoid breaking existing cached-feature/experiment paths | **No** — regenerable only by re-running `narrative_lens.data.build_ai_dataset` against the Gemini/GPT APIs (not bit-identical, since generation is non-deterministic) | Train/val/test (same role as the human-authored files — see "Label provenance" below for why this matters) |
| Processed/training dataset | *(no separate file — built in-memory)* | `train.load_raw_data()` reads all 4 raw CSVs above and concatenates them at runtime; there is no separate merged/processed CSV on disk. The closest thing to a materialized "processed" artifact is the per-model feature cache in `data/cache/cached_features_*.pt` (see below) | Cache files: yes, safe to delete/regenerate (see `data/cache/` section) | Train/val/test, split by `train.split_random()` / `split_leave_one_author()` / `split_leave_one_topic()` |
| Human-validation files | `data/annotation/human_validation_pilot_300*.csv` | A 300-row blind pilot (narrative/author/platform redacted) used to check whether `narrative_name` labels are actually text-supported, independent of account provenance — see [`docs/label_quality_audit.md`](../docs/label_quality_audit.md) | No — these are frozen annotation artifacts; re-generating would require re-running the blind sampling + re-annotating | **Audit only** — never used for training/evaluation of the classifier itself |
| Fresh-author holdout (frozen) | `artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json` (14 authors, 2 per narrative, frozen with seed=42 — see [`EXPERIMENTS.md`](../EXPERIMENTS.md) §25) | The pre-registered, held-out-in-advance author set used for confirmatory (non-exploratory) unseen-author generalization tests (Sections 25, 28) | **No** — frozen by design; re-freezing a different set would invalidate every confirmatory result that depends on it | **Test/audit only** — these authors must never be used in a training set for any experiment that cites Section 25/28 as confirmatory evidence |
| Matched-event candidate data | `data/candidates/v2_pilot/matched_event_pilot.csv` | A Phase-1, not-yet-adopted "Dataset V2" candidate pairing same-event coverage across narratives, mined offline from the existing raw corpus (see [`data/candidates/v2_pilot/README.md`](candidates/v2_pilot/README.md)) | Yes, in principle regenerable via `narrative_lens.data.build_matched_event_pilot`, but treated as read-only pending review | **Not used anywhere yet** — explicitly **not merged** into `data/raw/*.csv`; do not wire it into training until the Phase-1 quality gate is reviewed |

**Source of truth for "what the model actually trains on" today**: the 4 files under `data/raw/`
via `train.load_raw_data()` — nothing else listed above is part of the training/evaluation loop
except as a held-out test set (fresh-author holdout) or an offline audit (human-validation,
matched-event candidates).

## `data/raw/` (tracked in git)

The 4 source datasets the whole project is built on. **Not reproducible from code alone** -
they were collected via scraping/API calls (Twitter/Telegram, live at collection time) and a
synthetic-generation step (Gemini/GPT), so they are committed to git as-is rather than
regenerated:

| File | Produced by |
|---|---|
| `twitter_natural_dataset.csv` | `narrative_lens.data.build_twitter_dataset` (Selenium scraper) |
| `telegram_natural_dataset.csv` | `narrative_lens.data.build_telegram_dataset` (Telethon scraper) |
| `gemini_natural_dataset.csv` | `narrative_lens.data.build_ai_dataset` (Gemini-generated synthetic text) |
| `gpt_natural_dataset.csv` | GPT-generated synthetic text (companion to the Gemini set) |

> **Naming note**: `gemini_natural_dataset.csv` and `gpt_natural_dataset.csv` are **legacy
> filenames** — both are entirely **synthetic, LLM-generated** text, not naturally-occurring
> posts, despite the `natural` in the name. The files are not renamed because many experiment
> scripts, caches, and this document's own cross-references were written against the current
> paths; treat `natural` in these two filenames as historical, not descriptive.

Non-English rows in these were translated in place by `narrative_lens.data.translate_datasets`.

## `data/cache/` (mostly gitignored)

Derived, machine-generated feature caches and embeddings. **Every `.pt`/`.npy` file here is
reproducible** from `data/raw/` + a documented command below, with no hand-authored/unique
content - so they are excluded from git (`data/cache/**/*.pt`, `data/cache/**/*.npy` in
`.gitignore`) to keep the repo small. If a file listed below is missing, just re-run its
command; the producing script will recreate it automatically (all cache writes are
`os.makedirs(..., exist_ok=True)` + overwrite-safe).

| File | Regenerate with |
|---|---|
| `cached_features_hybrid.pt` | `python -m narrative_lens.train --model baseline_fusion --split random` |
| `cached_features_sbert_only.pt` | `python -m narrative_lens.train --model sbert_only --split random` |
| `cached_features_hybrid_model.pt` | `python -m narrative_lens.train --model hybrid --split random` |
| `cached_features_baseline_fusion_loao_<Author>.pt` | `python -m narrative_lens.train --model baseline_fusion --split leave_one_author --held-out-author <Author>` |
| `cached_features_ablation_loao_<Author>.pt` | `python experiments/author_generalization/narrative_ablation_loao.py --author <Author>` |
| `cached_features_narrative_topic_compare.pt` | `python experiments/feature_ablation/narrative_topic_compare.py` |
| `cached_features_narrative_topic_hybrid.pt` | `python experiments/feature_ablation/narrative_topic_hybrid.py` |
| `expF_embeddings_{full,12000,8000,4000}.npy` | `python experiments/topic_modeling/experiment_f_corpus_scaling.py` (resumable) |

Two exceptions are kept tracked in git despite living in `data/cache/`, since they are small,
human-readable, and useful to inspect without re-running anything:

- `shared_vocab.json` - small shared vocabulary file, rebuilt automatically if missing.
- `expF_subsample_{full,12000,8000,4000}.csv` - the exact stratified corpus subsamples used by
  Experiment F, produced by `experiments/topic_modeling/corpus_subsampling.py` (seeded, so
  re-running reproduces identical rows - kept as CSVs mainly for quick manual inspection).

## `data/profiles/`

Output of the unsupervised profiler prototype (`narrative_lens.evaluation.build_profile_prototype`
and related scripts) - calibration and sample narrative/text profiles used during that tool's
development. Small JSON files, kept tracked.

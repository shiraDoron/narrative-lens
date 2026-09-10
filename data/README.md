# `data/`

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

# Results

## Model comparison & current recommended configuration

`train.py` trains/evaluates three models, selected via `--model` (or `config.py`'s
`MODEL_TYPE`), on **identical train/validation/test splits** (`config.py`'s
`VAL_SIZE`/`TEST_SIZE`, fixed `random_state=42`) for a fair comparison. Each checkpoint
(`models/best_model_*.pth`) is selected by validation Macro-F1. Latest results on the `random`
split test set (`reports/tables/model_comparison_results.json`, rebuild with
`python -m narrative_lens.evaluation.compare_models`):

| `--model` | Class | Test Accuracy | Test Macro-F1 |
|---|---|---|---|
| `sbert_only` | `SBERTOnlyDetector` (frozen SBERT → MLP only) | 0.732 | **0.730** |
| `hybrid` | `HybridNarrativeDetector` (SBERT + all engineered features → MLP) | 0.722 | 0.717 |
| `baseline_fusion` | `NarrativeDetector` (linear weighted-sum fusion, original model) | 0.671 | 0.664 |

On this split, the pure-SBERT baseline currently edges out the Hybrid model, both clearly ahead
of the original linear-fusion baseline — the engineered feature layers are not yet adding
measurable value over frozen SBERT embeddings alone on a random split. **Current recommended
configuration for reproducing the headline result**:

```bash
python -m narrative_lens.train --model sbert_only --split random
```

using the existing `models/saved_topic_model` (legacy) topic model as-is - no retraining
needed. This ranking is not necessarily the same under generalization splits - see below and
[`EXPERIMENTS.md`](../EXPERIMENTS.md) sections 15-19 for the Leave-One-Author-Out picture.

Interpretability for the Hybrid model is intended to come from **ablation studies** (removing
one feature group at a time and measuring the Macro-F1 drop) rather than learned fusion
weights — this is scaffolded via `evaluate()`'s `features_labels` parameter but not yet
implemented (see the "future extension points" comment block at the bottom of `train.py`).

## Generalization evaluation (`--split ...`)

Every dataset row is tagged with two provenance columns during loading (`load_raw_data()` in
`train.py`): `dataset_source` (`gemini`/`gpt`/`twitter`/`telegram`) and `author_source` (the
specific account/channel — for `twitter`/`telegram` this is the real `account` column already
written by the scrapers; for the synthetic `gemini`/`gpt` datasets, which have no real per-row
author, a placeholder value like `gemini_synthetic` is used instead). `--split` selects how
train/validation/test are built from these:

| `--split` value | Behavior | Extra flag required |
|---|---|---|
| `random` (default) | Ordinary random split (`config.py`'s `VAL_SIZE`/`TEST_SIZE`, `random_state=42`) | — |
| `leave_one_topic` | All samples of one BERTopic topic id go entirely to test; rest split train/val | `--held-out-topic <topic_id>` |
| `leave_one_author` | All samples of one account/channel (`author_source`) go entirely to test; rest split train/val | `--held-out-author <name>` |

For the two specialized modes, `train.py` automatically runs `verify_no_leakage()` to assert
the held-out topic/author never also appears in train or validation, and saves a
`reports/results/split_summary_<model>_<run>.json` file with per-split narrative counts and
distinct `dataset_source`/`author_source` counts. Cache (`data/cache/`) and checkpoint
(`models/`) files are automatically namespaced per split mode + held-out value, so a
`random`-split run never collides with a `leave_one_topic`/`leave_one_author` run of the same
model. Author-generalization ablation results (LOAO) live in
[`reports/results/narrative_ablation_loao/`](../reports/results/narrative_ablation_loao/); the
code is in [`experiments/author_generalization/`](../experiments/author_generalization/).

**Known limitation**: `leave_one_author` on `gemini`/`gpt` rows is really equivalent to holding
out an entire synthetic dataset source, not a true test of generalizing away from one author's
writing style, since those datasets have no genuine per-row author. `leave_one_topic` requires
running the trained BERTopic model (`models/saved_topic_model/`) once over the full dataset to
assign `topic_id` before splitting.

## Where results live

- **`reports/tables/`** - curated cross-model comparison tables (start here for headline numbers).
- **`reports/agenda_profiling/`** - unsupervised agenda/rhetoric/ideology profiling output.
- **`reports/results/`** - raw per-run confusion matrices, split summaries, logs, and full
  per-experiment result dumps (Leave-One-Author-Out ablation, topic-representation ablation,
  profiler-prototype development).
- **[`EXPERIMENTS.md`](../EXPERIMENTS.md)** - the full narrative of every experiment: what was
  tried, why, and what was concluded.

## Future work

- **Identify the leading account(s) per narrative group** — for each of the 7 narratives, the
  Twitter/Telegram scrapers currently pull from a fixed list of accounts/channels treated
  equally (see `NARRATIVES_ACCOUNTS` in `data/build_twitter_dataset.py`). A useful extension is to
  determine which account within each group acts as the primary/most influential voice
  ("group leader"), e.g. by engagement volume, retweet/citation frequency by the other accounts
  in the same group, or centrality in a narrative-specific interaction graph:
  - **Zionist**: `Israel`, `IDF`, `StandWithUs`, `AIPAC`, `IsraelMFA`, `AJCGlobal`, `JNS_org`
  - **Resistance**: `khamenei_ir`, `PressTV`, `QudsNen`, `IrnaEnglish`, `TehranTimes79`, `MayadeenEnglish`
  - **Western**: `NATO`, `EU_Commission`, `POTUS`, `StateDept`, `FCDOGovUK`, `GermanyDiplo`
  - **Russian**: `KremlinRussia_E`, `mfa_russia`, `RussiaUN`, `RT_com`, `SputnikInt`, `tassagency_en`
  - **Ukrainian**: `ZelenskyyUa`, `Ukraine`, `DefenceU`, `MFA_Ukraine`, `GeneralStaffUA`, `United24media`
  - **Right-wing**: `FoxNews`, `BenShapiro`, `dailywire`, `Heritage`, `TPUSA`
  - **Left-wing**: `novaramedia`, `BernieSanders`, `jacobin`, `democracynow`, `thenation`

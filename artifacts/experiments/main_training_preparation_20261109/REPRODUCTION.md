# Main training preparation — reproduction

Run from repository root, existing Python 3.11.9; preparation uses only the standard library.
No checkpoints, external APIs, new rewriting, training or test inference are called.

```powershell
python artifacts/experiments/main_training_preparation_20261109/prepare.py
python artifacts/experiments/main_training_preparation_20261109/literature.py
python -m unittest discover -s artifacts/experiments/main_training_preparation_20261109 -p test_preparation.py -v
python artifacts/experiments/main_training_preparation_20261109/check_readiness.py
```

The last command intentionally exits 2, listing readiness blockers. This is a successful
fail-closed gate, not a failed experiment. There is no automatic trainer launch behind it.

`TRAIN_CONDITION_ID_MAP.csv` joins all 105 eligible TRAIN Originals to existing Paraphrases
and 30 ChatGPT Style outputs. `DRAFT_ARM_A` through `E` use the common30; labels are machine
proposals. All drafts are explicitly not approved model inputs. The 25 configs and 25 batch
schedules share architecture, seeds, source order and processed-example/update budgets;
D/E share dataset size and scheduling. They do not constitute a completed training experiment.
The full105 target uses the same formulas only after generation/QC/source-gold gates are met.

`SOURCE_LABEL_INTAKE.csv` has Original texts and blank answers for 105 train + 43 validation,
with source hashes and no author/proposed labels. `PAIRED_QC_INTAKE.csv` has texts and blank
answers for 105 sources x 2 variants, with existing text hashes and no author/labels/scores.
There are 135 available pairs (105 Paraphrases + 30 Style), plus 75 missing Style rows
explicitly marked do-not-rate; no reviewer should judge an absent rewrite.
These new intake files do not modify any existing human-review fields. Missing generations
have empty rewrite hashes and cannot be admitted by the QC contract.

`qc_contract.py` validates reviewer provenance, hashes, labels and ratings, rejects incomplete
or duplicate coverage, and constructs common-ID symmetric fallback/all-attempted vs secondary
accepted-only views. Tests use synthetic fixtures solely to verify the contract; they are not
new experimental rewrites or human judgments. It never edits original ratings.

`CLAUDE_REVIEW_PER_ID_IMPORTED.csv` transcribes the existing Claude Markdown including notes;
it is explicitly External LLM Review. Human templates on disk are blank. Claimed human
aggregate counts are stored separately in `HUMAN_REVIEW_IMPORT_STATUS.json`; no per-ID human
ratings are inferred from them. Full prior aggregate-only review stays in its original run.

`SOURCE_HASHES.json` protects raw datasets, split assignments and reviews. The audit rechecks
exact source/article hashes across frozen splits; it reads existing split metadata, never
exports test texts to training views or re-evaluates models. Train-only near-duplicate limits
are inherited and explicitly noted; no universal semantic-leakage guarantee is claimed.

`literature.py` renders the 18-record structured catalog, deep review and BibTeX from
primary-verified metadata and analytic notes. No abstracts/PDFs are copied. Initial automated
bibliography fetching was unavailable due a direct-network timeout; metadata was instead
cross-checked with the primary web sources. The discarded fetcher is not a dependency.

Canonical root documents: THESIS_RESEARCH_DIRECTION_HE.md, MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md,
RELATED_WORK_DEEP_REVIEW_HE.md, RELATED_WORK_COMPARISON.md, REFERENCES.bib,
RESEARCH_GAP_AND_CONTRIBUTION_HE.md. Previous reports remain historical records.

# Preparation verification — 2026-11-09

Executed: `python -m unittest discover -s artifacts/experiments/main_training_preparation_20261109 -p test_preparation.py -v`.

**16 tests passed**, covering raw-source SHA integrity; exact105/common30/missing75 joins;
same IDs/labels/arm sizes; author-disjoint assignments and train-only views; all 25 schedule
reproductions and equal budgets; blocking unknown generator provenance; human/Claude
separation; common-policy fallback and secondary accepted IDs; rejecting LLM-as-human,
wrong hashes, missing generation, duplicate/incomplete QC and label disagreements;
blank human intakes; 18 BibTeX/catalog records; and local links in canonical documents.

The actual `check_readiness.py` exits 2 with explicit missing human/QC/generation blockers.
No experiment was trained merely to exercise a test. Unit-test string fixtures are not
experimental rewrites or reviewer judgments. All original reviews/labels/splits are unchanged.

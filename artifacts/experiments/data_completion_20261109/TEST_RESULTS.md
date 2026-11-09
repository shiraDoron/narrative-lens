# Infrastructure verification — 2026-11-09

Command from repository root:

```powershell
python -m unittest discover -s artifacts/experiments/data_completion_20261109 -p test_completion.py -q
```

Result: **18 tests passed** (Python 3.11.9).

Coverage includes exact 105/75/30 ID coverage, train author assignment, disjoint five-batch partition, no duplicate sources, blank independent forms, exact Original/rewrite binding, frozen validator source identity and prompt/batch hashes, Markdown parsing, human/LLM provenance rejection, immutable raw import, receipt integrity, QC dry-run wiring, and five draft candidate views on the same105 IDs. Edited intake forms prevent bundle regeneration rather than being overwritten.

Import/receive/compiler checks use temporary synthetic I/O fixtures only. They are not generated study rewrites, reviews, or classifier results. No actual new75 outputs were available, so full ML preservation screening was not executed. No actual completed human30 file was imported. Human validation and final training remain pending. Protected legacy artifacts and guard/threshold/scaling sources passed hash checks.

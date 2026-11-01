# New Normalized external review import

Explicit evaluation name: **External LLM Review — New Normalized**. This directory is separate from Human Validation and the earlier Old Normalized review.

`discrepancy_classification_30.csv` compares all 30 rows, including individual guards, similarity/NLI scores, original external ratings and TP/FP/TN/FN classification **relative to the supplied LLM**. Positive means automatic rejection / external drift risk. TP: rejected and external drift Yes; FP: rejected and external meaning Yes with drift No; TN: passed and external preservation; FN: passed and external drift Yes or meaningful Borderline. All 15 actual Borderline rows also explicitly have drift Yes in the supplied source; their meaning is never recoded as No. `borderline_cases_15.csv` preserves these cases separately; `classification_by_meaning.csv` preserves Yes/Borderline/No within each class. These analytical categories never override automatic filtering.

Run from the project root with the existing Python environment:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/import_review.py
```

An optional positional path supplies the source CSV on first import. The committed source copy is preferred on subsequent runs. Import verifies exact 30-ID coverage and TRAIN membership, preserves source bytes, namespaces supplied ratings, joins frozen comparison texts/scores, and writes counts, cross-tabs and Hebrew reports. Notes are data, never executable instructions. No LLM call or training occurs. Protected CSV/JSON/JSONL/TXT/HTML files are hashed before and after import; documentation alone is updated.

The source has no reviewer model version, evaluation prompt, timestamp, original/new text or reviewed-text hashes. Version association relies on the IDs and user delivery context. Do not claim blind evaluation, human verification, independent replication or calibrated guard error rates. Preserve Borderline separately. Candidate false positives are disagreements with the supplied LLM ratings, not proven guard errors. This import does not change automatic acceptance or fill human-review fields.

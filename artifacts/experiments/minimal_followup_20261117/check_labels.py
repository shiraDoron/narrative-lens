"""Human intake completeness check only; never imports labels into the corpus."""
import argparse
import datetime
import json
from pathlib import Path

from prepare import HERE, read


def validate(records):
    canonical = {r['review_id']: r for r in read(HERE / 'LABEL_97_BLIND.csv')}
    errors = []
    keys = [r.get('review_id') for r in records]
    if len(keys) != 97 or len(set(keys)) != 97 or set(keys) != set(canonical):
        errors.append('Need exact97 distinct blind IDs; no missing/extra/duplicate records')
    completed = 0
    for row in records:
        rid = row.get('review_id')
        if rid not in canonical:
            continue
        problems = []
        if row.get('Original') != canonical[rid]['Original']:
            problems.append('Original changed')
        if row.get('label') not in ('Left', 'Right', 'Unclear'):
            problems.append('Choose Left / Right / Unclear')
        evidence = row.get('evidence_span', '')
        if evidence and evidence not in canonical[rid]['Original']:
            problems.append('Evidence must be an exact Original span')
        if row.get('label') in ('Left', 'Right') and not evidence.strip():
            problems.append('Binary label requires evidence')
        if not row.get('reason', '').strip():
            problems.append('Reason required, including Unclear explanation')
        if row.get('reviewer_type') != 'human':
            problems.append('No human provenance; AI is not human gold')
        if not row.get('reviewer_id', '').strip() or not row.get('assistance_used', '').strip():
            problems.append('Reviewer ID and assistance disclosure required (use none if none)')
        if row.get('confidence') not in ('1', '2', '3'):
            problems.append('Confidence must be1–3')
        try:
            datetime.date.fromisoformat(row.get('review_date', ''))
        except (ValueError, TypeError):
            problems.append('ISO review date required')
        if problems:
            errors.append(dict(review_id=rid, issues=problems))
        else:
            completed += 1
    return dict(completed=completed, expected=97, errors=errors, corpus_updated=False,
                meaning='Completeness/provenance declaration check, not independent identity verification or gold approval')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(read(args.source)), ensure_ascii=False, indent=2))

"""Check two independent human reviews and adjudication; never train/freeze/relabel corpus."""
import argparse
import datetime
import json
from pathlib import Path

from collect import HERE, ROOT, read, sha, text_sha

OPTIONS = ('Left', 'Right', 'Unclear')


def keyed(rows):
    result = {}
    for row in rows:
        rid = row.get('review_id')
        if rid in result:
            raise ValueError('Duplicate review ID: '+str(rid))
        result[rid] = row
    return result


def human_fields(row, id_field='reviewer_id'):
    issues = []
    if row.get('reviewer_type') != 'human':
        issues.append('human provenance declaration required; AI is not human gold')
    if not row.get(id_field, '').strip():
        issues.append('reviewer identity required')
    if not row.get('assistance_used', '').strip():
        issues.append('assistance disclosure required; use none where applicable')
    try:
        datetime.date.fromisoformat(row.get('review_date', ''))
    except (ValueError, TypeError):
        issues.append('ISO review date required')
    return issues


def check(reviewer_a, reviewer_b, adjudication):
    manifest = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
    for path, digest in manifest['output_sha256'].items():
        if sha(HERE / path) != digest:
            raise ValueError('Frozen collection output changed: '+path)
    for path, digest in manifest['protected_inputs_sha256'].items():
        if sha(ROOT / path) != digest:
            raise ValueError('Protected source/protocol changed: '+path)
    expected = keyed(read(HERE / 'PRIVATE_REVIEW_KEY.csv'))
    a, b, adjud = keyed(reviewer_a), keyed(reviewer_b), keyed(adjudication)
    if set(adjud) - set(expected):
        raise ValueError('Unknown adjudication source IDs')
    problems, valid = [], {'A': {}, 'B': {}}
    text_by_id = {r['review_id']: r['Original'] for r in read(HERE / 'REVIEWER_A_BLIND.csv')}
    for name, records in [('A', a), ('B', b)]:
        if set(records) != set(expected):
            problems.append(dict(reviewer=name, issue='Exact frozen ID coverage required'))
        for rid in set(records) & set(expected):
            row, source = records[rid], expected[rid]
            issues = human_fields(row)
            if text_sha(row.get('Original', '')) != source['source_sha256']:
                issues.append('Original text/hash changed')
            if row.get('label') not in OPTIONS:
                issues.append('Left / Right / Unclear required')
            evidence = row.get('evidence_span', '')
            if (row.get('label') in ('Left', 'Right') and not evidence.strip()) or (evidence and evidence not in text_by_id[rid]):
                issues.append('Binary evidence must be an exact nonempty Original span')
            if not row.get('reason', '').strip():
                issues.append('reason required, including Unclear')
            if row.get('confidence') not in ('1', '2', '3'):
                issues.append('confidence must be1–3')
            if issues:
                problems.append(dict(review_id=rid, reviewer=name, issues=issues))
            else:
                valid[name][rid] = row
    eligible, unresolved, unclear, conflicts = [], [], [], []
    for rid in expected:
        if rid not in valid['A'] or rid not in valid['B']:
            unresolved.append(rid)
            continue
        ra, rb = valid['A'][rid], valid['B'][rid]
        if ra['reviewer_id'] == rb['reviewer_id']:
            problems.append(dict(review_id=rid, issue='Two distinct independent reviewer IDs required'))
            unresolved.append(rid)
            continue
        if ra['label'] == rb['label']:
            label, basis = ra['label'], 'two-human agreement'
        else:
            conflicts.append(rid)
            decision = adjud.get(rid, {})
            issues = human_fields(decision, 'adjudicator_id')
            if decision.get('source_sha256') != expected[rid]['source_sha256']:
                issues.append('adjudication source hash mismatch')
            if decision.get('final_label') not in OPTIONS or not decision.get('rationale', '').strip():
                issues.append('adjudication label and rationale required')
            if decision.get('adjudicator_id') in (ra['reviewer_id'], rb['reviewer_id']):
                issues.append('independent adjudicator required')
            evidence = decision.get('evidence_span', '')
            if decision.get('final_label') in ('Left', 'Right') and (not evidence.strip() or evidence not in text_by_id[rid]):
                issues.append('adjudicated binary evidence must be exact and nonempty')
            if issues:
                problems.append(dict(review_id=rid, reviewer='adjudication', issues=issues))
                unresolved.append(rid)
                continue
            label, basis = decision['final_label'], 'independent-human adjudication'
        if label == 'Unclear':
            unclear.append(rid)
        else:
            eligible.append(dict(review_id=rid, ID=expected[rid]['ID'], label=label, basis=basis))
    return dict(candidate_sources=len(expected), valid_reviews_A=len(valid['A']), valid_reviews_B=len(valid['B']),
                binary_candidates_after_human_labels=len(eligible), unclear_after_human_labels=len(unclear),
                disagreement_sources=conflicts, unresolved_sources=len(unresolved),
                missing_to200=max(0, 200-len(eligible)), errors=problems,
                eligible=eligible, corpus_updated=False, training_triggered=False,
                approval='Provenance is declared, not identity-authenticated. Human-label eligibility is not a signed source/QC/protocol freeze or automatic selection of200.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reviewer-a', type=Path, required=True)
    parser.add_argument('--reviewer-b', type=Path, required=True)
    parser.add_argument('--adjudication', type=Path, default=HERE / 'ADJUDICATION_TEMPLATE.csv')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Do not overwrite a review report')
    result = check(read(args.reviewer_a), read(args.reviewer_b), read(args.adjudication))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

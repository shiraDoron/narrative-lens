"""Incremental two-human review merge, agreement and adjudication. Never trains/selects200."""
import argparse
import collections
import datetime
import json
from pathlib import Path
import re
import shutil

from bundle import HERE, COLLECTION, dump, read, save, sha, text_sha, verify_collection

LABELS = ('Left', 'Right', 'Unclear')
NONE_ASSISTANCE = {'none', 'no', 'לא', 'ללא', 'ללא סיוע'}
ADJ_FIELDS = ['review_id', 'source_sha256', 'review_A_record_sha256', 'review_B_record_sha256',
              'final_label', 'evidence_span', 'rationale', 'reviewer_type', 'adjudicator_id', 'review_date', 'assistance_used']


def verify_handoff():
    verify_collection()
    manifest = json.loads((HERE / 'HANDOFF_MANIFEST.json').read_text(encoding='utf-8'))
    if sha(COLLECTION / 'CANDIDATES.csv') != manifest['source_csv_sha256']:
        raise ValueError('Source candidate bank changed')
    for path, digest in manifest['output_sha256'].items():
        if sha(HERE / path) != digest:
            raise ValueError('Canonical handoff changed: '+path+'; fill separate copies')


def indexed(rows, expected, kind):
    result = {}
    for row in rows:
        rid = row.get('review_id', '')
        if rid not in expected:
            raise ValueError('Unknown/missing '+kind+' review_id: '+rid)
        if rid in result:
            raise ValueError('Duplicate '+kind+' review_id: '+rid)
        result[rid] = row
    return result


def metadata_issues(row, identity_field):
    issues = []
    if row.get('reviewer_type') != 'human':
        issues.append('human provenance declaration required; AI cannot count as human')
    if not row.get(identity_field, '').strip():
        issues.append('reviewer identity required')
    date = row.get('review_date', '')
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
            raise ValueError('date format')
        datetime.date.fromisoformat(date)
    except (ValueError, TypeError):
        issues.append('review_date must be YYYY-MM-DD')
    if row.get('assistance_used', '').strip().casefold() not in NONE_ASSISTANCE:
        issues.append('missing/disclosed assistance requires coordinator review; not independent acceptance')
    return issues


def record_hash(row):
    fields = ('review_id', 'Original', 'label', 'evidence_span', 'reason', 'confidence', 'reviewer_type',
              'reviewer_id', 'review_date', 'assistance_used')
    return text_sha(json.dumps({k: row.get(k, '') for k in fields}, sort_keys=True, ensure_ascii=False))


def agreement(pairs):
    confusion = {a: {b: 0 for b in LABELS} for a in LABELS}
    for a, b in pairs:
        confusion[a][b] += 1
    n = len(pairs)
    agreed = sum(confusion[label][label] for label in LABELS)
    po = agreed/n if n else None
    pe = sum(sum(confusion[label].values())*sum(confusion[a][label] for a in LABELS) for label in LABELS)/(n*n) if n else None
    kappa = (po-pe)/(1-pe) if n and pe < 1-1e-12 else None
    return dict(valid_independent_pairs=n, agreements=agreed, disagreements=n-agreed,
                raw_agreement=po, expected_chance_agreement=pe, cohen_kappa=kappa,
                kappa_unavailable_reason='no valid independent pairs' if not n else 'degenerate marginals (expected agreement=1)' if kappa is None else '',
                labels=list(LABELS), confusion=confusion,
                interpretation='Before adjudication, all3 labels including Unclear; descriptive inter-rater agreement, not classifier performance or independent author-cluster inference')


def merge(a_rows, b_rows, adjud_rows):
    verify_handoff()
    key = {r['review_id']: r for r in read(HERE / 'COORDINATOR_PRIVATE_KEY.csv')}
    source = {r['review_id']: r['Original'] for r in read(HERE / 'reviewer_A/REVIEW.csv')}
    a, b, adjud = indexed(a_rows, key, 'A'), indexed(b_rows, key, 'B'), indexed(adjud_rows, key, 'adjudication')
    issues, valid, statuses = [], {'A': {}, 'B': {}}, {'A': {}, 'B': {}}
    identities = {}
    for role, rows in [('A', a), ('B', b)]:
        claimed = {r.get('reviewer_id', '').strip().casefold() for r in rows.values() if r.get('label', '').strip() and r.get('reviewer_id', '').strip()}
        identities[role] = claimed
        file_conflict = len(claimed) > 1
        for rid in key:
            row = rows.get(rid)
            if row is not None and text_sha(row.get('Original', '')) != key[rid]['source_sha256']:
                statuses[role][rid] = 'invalid'
                issues.append(dict(review_id=rid, role=role, issues='Original/hash changed, including a pending row'))
                continue
            if row is None or not row.get('label', '').strip():
                statuses[role][rid] = 'pending'
                continue
            errors = metadata_issues(row, 'reviewer_id')
            if file_conflict:
                errors.append('mixed reviewer identities in one role/file')
            if text_sha(row.get('Original', '')) != key[rid]['source_sha256']:
                errors.append('Original/hash changed')
            if row.get('label') not in LABELS:
                errors.append('label must be Left / Right / Unclear')
            evidence = row.get('evidence_span', '')
            if evidence and evidence not in source[rid]:
                errors.append('evidence is not an exact Original span')
            if row.get('label') in ('Left', 'Right') and not evidence.strip():
                errors.append('binary label requires evidence')
            if not row.get('reason', '').strip():
                errors.append('reason required, including Unclear')
            if row.get('confidence') not in ('1', '2', '3'):
                errors.append('confidence must be1–3')
            if errors:
                statuses[role][rid] = 'invalid'
                issues.append(dict(review_id=rid, role=role, issues=' | '.join(errors)))
            else:
                statuses[role][rid] = 'valid'
                valid[role][rid] = row
    shared_identity = bool(identities['A'] & identities['B'])
    merged, disputes, to_fill, pairs = [], [], [], []
    counts = collections.Counter()
    for rid, meta in key.items():
        row = dict(review_id=rid, source_sha256=meta['source_sha256'],
                   status_A=statuses['A'][rid], status_B=statuses['B'][rid],
                   label_A=a.get(rid, {}).get('label', ''), label_B=b.get(rid, {}).get('label', ''),
                   final_label='', final_basis='', progress_status='pending_review')
        decision = adjud.get(rid, {})
        has_decision = bool(decision.get('final_label', '').strip())
        if rid not in valid['A'] or rid not in valid['B']:
            row['progress_status'] = 'invalid_review' if 'invalid' in (row['status_A'], row['status_B']) else 'pending_review'
            if has_decision:
                issues.append(dict(review_id=rid, role='adjudication', issues='decision cannot replace missing/invalid independent reviews'))
        elif shared_identity:
            row['progress_status'] = 'independence_blocked'
            issues.append(dict(review_id=rid, role='A/B', issues='reviewer identities overlap between roles'))
        else:
            ra, rb = valid['A'][rid], valid['B'][rid]
            pairs.append((ra['label'], rb['label']))
            if ra['label'] == rb['label']:
                if has_decision:
                    row['progress_status'] = 'unexpected_adjudication'
                    issues.append(dict(review_id=rid, role='adjudication', issues='nonblank decision for agreeing reviews needs coordinator resolution; not an automatic override'))
                else:
                    row.update(final_label=ra['label'], final_basis='two independent human agreements')
            else:
                ha, hb = record_hash(ra), record_hash(rb)
                disputes.append(dict(review_id=rid, Original=source[rid], source_sha256=meta['source_sha256'],
                                     label_A=ra['label'], evidence_A=ra['evidence_span'], reason_A=ra['reason'],
                                     label_B=rb['label'], evidence_B=rb['evidence_span'], reason_B=rb['reason'],
                                     review_A_record_sha256=ha, review_B_record_sha256=hb))
                to_fill.append(dict.fromkeys(ADJ_FIELDS, '') | dict(review_id=rid, source_sha256=meta['source_sha256'],
                               review_A_record_sha256=ha, review_B_record_sha256=hb))
                row['progress_status'] = 'pending_adjudication'
                if has_decision:
                    errors = metadata_issues(decision, 'adjudicator_id')
                    if decision.get('adjudicator_id', '').strip().casefold() in identities['A'] | identities['B']:
                        errors.append('adjudicator must be a distinct third human')
                    if decision.get('source_sha256') != meta['source_sha256']:
                        errors.append('adjudication source hash mismatch')
                    if decision.get('review_A_record_sha256') != ha or decision.get('review_B_record_sha256') != hb:
                        errors.append('stale/unbound adjudication: underlying reviews changed')
                    if decision.get('final_label') not in LABELS or not decision.get('rationale', '').strip():
                        errors.append('adjudication label and rationale required')
                    evidence = decision.get('evidence_span', '')
                    if evidence and evidence not in source[rid]:
                        errors.append('adjudication evidence absent from Original')
                    if decision.get('final_label') in ('Left', 'Right') and not evidence.strip():
                        errors.append('adjudicated binary evidence required')
                    if errors:
                        row['progress_status'] = 'invalid_adjudication'
                        issues.append(dict(review_id=rid, role='adjudication', issues=' | '.join(errors)))
                    else:
                        row.update(final_label=decision['final_label'], final_basis='independent human adjudication')
        if row['final_label']:
            row['progress_status'] = 'verified_binary_label' if row['final_label'] in ('Left', 'Right') else 'resolved_unclear'
        counts[row['progress_status']] += 1
        merged.append(row)
    assert sum(counts.values()) == len(key)
    pending_ids = {r['review_id'] for r in merged if r['progress_status'] in ('pending_adjudication', 'invalid_adjudication')}
    to_fill = [r for r in to_fill if r['review_id'] in pending_ids]
    verified = counts['verified_binary_label']
    report = dict(target_verified_train=200, candidate_sources=len(key),
                  valid_reviews_A=len(valid['A']), valid_reviews_B=len(valid['B']),
                  pending_A=sum(s == 'pending' for s in statuses['A'].values()), pending_B=sum(s == 'pending' for s in statuses['B'].values()),
                  invalid_A=sum(s == 'invalid' for s in statuses['A'].values()), invalid_B=sum(s == 'invalid' for s in statuses['B'].values()),
                  verified_binary_labels=verified, missing_to200=max(0, 200-verified), target_fraction=min(1., verified/200),
                  resolved_unclear=counts['resolved_unclear'], status_counts=dict(counts),
                  remaining_source_decisions=len(key)-verified-counts['resolved_unclear'],
                  progress_by_label={label: sum(r['final_label'] == label for r in merged) for label in LABELS},
                  agreement_before_adjudication=agreement(pairs),
                  disagreement_sources=len(disputes), pending_adjudications=counts['pending_adjudication']+counts['invalid_adjudication'],
                  global_independence_block=shared_identity, errors=len(issues),
                  meaning='Human-label-verified count only; provenance is declared, source checks are technical, no final corpus/protocol freeze or training approval',
                  training_ready=False, corpus_modified=False, auto_selected200=False, no_test_evaluation=True)
    return dict(report=report, merged=merged, disputes=disputes, to_fill=to_fill, issues=issues)


def write_progress(path, report):
    ag = report['agreement_before_adjudication']
    pct = lambda x: 'טרם ניתן לחשב' if x is None else f'{100*x:.1f}'+'%'
    kap = 'לא מוגדר: '+ag['kappa_unavailable_reason'] if ag['cohen_kappa'] is None else f"{ag['cohen_kappa']:.4f}"
    lines = ['# התקדמות אימות Train', '',
             f"**{report['verified_binary_labels']} / 200 תוויות בינאריות מאומתות בידי אדם; חסרות {report['missing_to200']}.**", '',
             'אין בכך אישור מקור סופי, freeze או הרשאת אימון. אין בחירה אוטומטית של200.', '',
             '| מדד | מספר |', '|---|---:|',
             f"| מועמדים ייחודיים | {report['candidate_sources']} |",
             f"| סקירות תקינות א׳ | {report['valid_reviews_A']} |", f"| סקירות תקינות ב׳ | {report['valid_reviews_B']} |",
             f"| טרם תויגו א׳ / ב׳ | {report['pending_A']} / {report['pending_B']} |",
             f"| סקירות לא תקינות א׳ / ב׳ | {report['invalid_A']} / {report['invalid_B']} |",
             f"| זוגות עצמאיים תקינים | {ag['valid_independent_pairs']} |",
             f"| מחלוקות לפני הכרעה | {ag['disagreements']} |",
             f"| מחלוקות שממתינות להכרעה תקינה | {report['pending_adjudications']} |",
             f"| תוויות מאומתות Left / Right | {report['progress_by_label']['Left']} / {report['progress_by_label']['Right']} |",
             f"| הוכרעו Unclear | {report['resolved_unclear']} |", '',
             'הסכמה מחושבת על כל שלוש התוויות, לפני הכרעה, ורק בזוגות עצמאיים תקינים:', '',
             f"- הסכמה גולמית: {pct(ag['raw_agreement'])} מתוך {ag['valid_independent_pairs']} זוגות.",
             f'- Cohen κ: {kap}.', '', 'זו הסכמת סוקרים תיאורית, לא accuracy של מודל או טענה להכללה.', '',
             '## מטריצת הסכמה לפני הכרעה', '', '| א׳ / ב׳ | Left | Right | Unclear |', '|---|---:|---:|---:|']
    lines += [f"| {label} | "+' | '.join(str(ag['confusion'][label][other]) for other in LABELS)+' |' for label in LABELS]
    lines += ['', 'הרשומות והקבצים המקוריים נשמרים בנפרד. שגיאות, מחלוקות והכרעות לא נדרסות.',
              'Left/Right הוא מסגור אידאולוגי צר, לא תיוג נרטיב מלא. זיהוי מחבר, הסתמכות על סגנון ושיפור הכללה נשארים נפרדים.', '']
    path.write_text('\n'.join(lines), encoding='utf-8')


def run(a_path, b_path, adjud_path, out):
    if out.exists():
        raise ValueError('Run output already exists; use a new directory to preserve history')
    result = merge(read(a_path), read(b_path), read(adjud_path) if adjud_path else [])
    out.mkdir(parents=True)
    shutil.copyfile(Path(__file__), out / 'ENGINE_SNAPSHOT.py')
    shutil.copyfile(HERE / 'bundle.py', out / 'BUNDLE_SNAPSHOT.py')
    for role, path in [('reviewer_A_received.csv', a_path), ('reviewer_B_received.csv', b_path), ('adjudication_received.csv', adjud_path)]:
        if path:
            shutil.copyfile(path, out / role)
    save(out / 'MERGED_REVIEW_STATUS.csv', result['merged'])
    save(out / 'DISAGREEMENTS.csv', result['disputes'], ['review_id', 'Original', 'source_sha256', 'label_A', 'evidence_A', 'reason_A', 'label_B', 'evidence_B', 'reason_B', 'review_A_record_sha256', 'review_B_record_sha256'])
    save(out / 'ADJUDICATION_TO_FILL.csv', result['to_fill'], ADJ_FIELDS)
    save(out / 'ISSUES.csv', result['issues'], ['review_id', 'role', 'issues'])
    dump(out / 'PROGRESS.json', result['report'])
    write_progress(out / 'PROGRESS_HE.md', result['report'])
    dump(out / 'RUN_MANIFEST.json', dict(created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         input_sha256={str(p.resolve()): sha(p) for p in (a_path, b_path, adjud_path) if p},
         handoff_manifest_sha256=sha(HERE / 'HANDOFF_MANIFEST.json'), engine_sha256=sha(Path(__file__)),
         output_sha256={p.name: sha(p) for p in out.iterdir() if p.is_file()},
         approvals='No automatic corpus edit, selection of200, freeze or training'))
    return result['report']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reviewer-a', type=Path, required=True)
    parser.add_argument('--reviewer-b', type=Path, required=True)
    parser.add_argument('--adjudication', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.reviewer_a, args.reviewer_b, args.adjudication, args.output_dir)
    print(json.dumps({k: report[k] for k in ('verified_binary_labels', 'missing_to200', 'valid_reviews_A', 'valid_reviews_B', 'pending_adjudications')}, ensure_ascii=False))

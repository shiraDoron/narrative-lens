"""Human forms and exhaustive intake checks. No ML, gold creation or approval.

build refuses to overwrite forms; check only writes a separate readiness report.
Duplicate reviews always require explicit adjudication, even if they agree.
"""
import argparse
from collections import Counter, defaultdict
import datetime
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUNTIME = ROOT / 'artifacts/experiments/main_training_runtime_20261110'
sys.path.insert(0, str(RUNTIME))
from contract import (assert_frozen, candidates, validation_sources, text_sha, read, save,
                      assert_human, policy_inputs, PROTOCOL, sha)

FOCUS = ROOT / 'artifacts/experiments/research_completion_20261110/focused_quality_64_20261110/FOCUSED_QUALITY_REVIEW_64.csv'
RATINGS = {'Yes', 'No', 'Borderline'}
LABELS = {'Left-wing', 'Right-wing', 'Unclear', 'Mixed', 'Other'}


def templates():
    assert_frozen()
    train = candidates()
    concern = {r['ID'] for r in read(FOCUS) if r['disposition'] in
               ('ai_identified_difference', 'unresolved_semantic_risk')}
    assert len(concern) == 30
    ordered = sorted(train, key=lambda r: (r['ID'] not in concern, r['ID']))
    labels = []
    for split, sources in [('train', ordered), ('validation', validation_sources())]:
        for row in sources:
            labels.append(dict(ID=row['ID'], split=split, Original=row['Original'],
                               proposed_label=row['label'], source_sha256=text_sha(row['Original']),
                               human_label='', proposed_label_correct='', evidence_span='',
                               human_notes='', reviewer_type='', reviewer_id='', review_date=''))
    pairs = []
    # First30 are Style concern records. All105 Style and105 Paraphrase follow.
    for variant in ('Style', 'Paraphrase'):
        for row in ordered:
            pairs.append(dict(ID=row['ID'], variant=variant, Original=row['Original'], Rewrite=row[variant],
                              source_sha256=text_sha(row['Original']), rewrite_sha256=text_sha(row[variant]),
                              meaning='', stance='', style_change='', semantic_drift='', notes='',
                              reviewer_type='', reviewer_id='', review_date=''))
    return labels, pairs, concern


def cell(text):
    return text.replace('|', '&#124;').replace('\n', '<br>')


def build():
    if (HERE / 'forms').exists():
        raise ValueError('Forms already exist: preserve human answers; do not overwrite')
    labels, pairs, concern = templates()
    forms = HERE / 'forms'
    forms.mkdir()
    save(forms / 'LABELS_148.csv', labels)
    save(forms / 'PAIRS_210.csv', pairs)
    index = ['# חבילת אימות אנושי — 148 תוויות ו-210 זוגות', '',
             'הכרעות האדם נשארו ריקות. השתמשו ב-CSV להזנה ובקובצי Markdown לקריאה. '
             'כל הטקסטים מופיעים במלואם. ההצעות אינן gold. אין צורך בסקירת AI נוספת.', '',
             '30 זוגות Style הראשונים קיבלו קדימות בשל חשש קודם; הדירוגים והנימוקים הקודמים אינם מוצגים. '
             'סדר זה אינו עיוור לחלוטין ועלול לעגן; יש לשפוט כל זוג באופן עצמאי. '
             'כל יתר הדוגמאות נכללות אף הן.', '',
             '[הוראות עבודה](../README_HE.md) · [הנחיות תוויות](../LABELING_GUIDE_HE.md)', '']
    for kind, rows in [('LABELS', labels), ('PAIRS', pairs)]:
        for start in range(0, len(rows), 15):
            batch = rows[start:start + 15]
            filename = f'{kind}_{start + 1:03}_{start + len(batch):03}.md'
            lines = [f'# {kind}: {start + 1}–{start + len(batch)}', '',
                     'שדות הכרעה ריקים למילוי אדם. אין לשנות טקסטים או IDs. '
                     'תאריך בפורמט YYYY-MM-DD; reviewer_type=human רק להכרעת אדם בפועל.', '']
            for row in batch:
                lines += [f"## {row['ID']} — {row.get('variant', row.get('split'))}", '']
                if kind == 'LABELS':
                    lines += [row['Original'], '',
                              f"הצעה בלבד, לא gold: **{row['proposed_label']}**. "
                              'גבשו עמדה מהטקסט לפני ההשוואה להצעה ככל האפשר.', '',
                              'human_label: Left-wing / Right-wing / Unclear / Mixed / Other. '
                              'proposed_label_correct: Yes / No / Borderline.', '']
                    fields = ('human_label', 'proposed_label_correct', 'evidence_span', 'human_notes')
                else:
                    lines += ['| Original | Rewrite |', '|---|---|',
                              f"| {cell(row['Original'])} | {cell(row['Rewrite'])} |", '',
                              'meaning / stance / semantic_drift: Yes / No / Borderline. '
                              'style_change נדרש ל-Style; ב-Paraphrase אפשר להשאירו ריק. '
                              'semantic_drift=Yes פירושו שיש שינוי משמעות, בניגוד ל-meaning=Yes.', '']
                    fields = ('meaning', 'stance', 'style_change', 'semantic_drift', 'notes')
                lines += ['| field | answer |', '|---|---|']
                lines += [f'| {field} | |' for field in (*fields, 'reviewer_type', 'reviewer_id', 'review_date')]
                lines += ['']
            (forms / filename).write_text('\n'.join(lines), encoding='utf-8', newline='\n')
            index.append(f'- [{filename}]({filename})')
    (forms / 'INDEX_HE.md').write_text('\n'.join(index) + '\n', encoding='utf-8', newline='\n')
    for path in forms.iterdir():
        # Stable repository line endings before computing file-level hashes.
        path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
    manifest = dict(labels=148, train_labels=105, validation_labels=43, Style=105, Paraphrase=105,
                    first30_style_priority=sorted(concern), protocol_sha256=sha(PROTOCOL),
                    forms_sha256={p.name: sha(p) for p in forms.iterdir() if p.is_file()})
    (HERE / 'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                                               encoding='utf-8', newline='\n')


def inspect(labels, pairs, freeze=None):
    expected_labels, expected_pairs, _ = templates()
    problems = []
    stats = Counter()
    resolved = {}

    def issue(kind, key, field, code, detail):
        problems.append(dict(kind=kind, key=str(key), field=field, code=code, detail=detail))

    for kind, actual, expected, key_fields in [('labels', labels, expected_labels, ('ID',)),
                                               ('pairs', pairs, expected_pairs, ('ID', 'variant'))]:
        expected_by_key = {tuple(r[k] for k in key_fields): r for r in expected}
        groups = defaultdict(list)
        for row in actual:
            key = tuple(row.get(k, '') for k in key_fields)
            groups[key].append(row)
        for key in groups.keys() - expected_by_key.keys():
            issue(kind, key, '', 'unexpected_key', 'Unexpected ID/variant; no silent omission')
        final = []
        for key, source in expected_by_key.items():
            records = groups.get(key, [])
            if not records:
                issue(kind, key, '', 'missing_record', 'Required review missing')
                continue
            if len(records) > 1:
                fields = ['human_label', 'proposed_label_correct'] if kind == 'labels' else ['meaning', 'stance', 'style_change', 'semantic_drift']
                different = [f for f in fields if len({r.get(f, '') for r in records}) > 1]
                issue(kind, key, ','.join(different), 'disagreement' if different else 'duplicate_review',
                      'Preserve raw reviews; explicit adjudicated record required, never last-row-wins')
                continue
            row = records[0]
            before = len(problems)
            protected = ['ID', 'Original', 'source_sha256']
            protected += ['split', 'proposed_label'] if kind == 'labels' else ['variant', 'Rewrite', 'rewrite_sha256']
            for field in protected:
                if row.get(field) != source[field]:
                    issue(kind, key, field, 'binding_mismatch', 'Canonical text/hash/metadata changed')
            try:
                assert_human(row)
                datetime.date.fromisoformat(row.get('review_date', ''))
            except (ValueError, TypeError) as exc:
                issue(kind, key, 'reviewer', 'missing_or_nonhuman_provenance', str(exc))
            fields = ['human_label', 'proposed_label_correct'] if kind == 'labels' else ['meaning', 'stance', 'semantic_drift'] + (['style_change'] if source['variant'] == 'Style' else [])
            for field in fields:
                allowed = LABELS if field == 'human_label' else RATINGS
                if row.get(field) not in allowed:
                    issue(kind, key, field, 'missing_or_invalid_answer', 'Allowed: ' + ', '.join(sorted(allowed)))
                elif row[field] == 'Borderline':
                    issue(kind, key, field, 'unresolved_borderline', 'Human adjudication needed; never convert automatically')
            notes_key = 'human_notes' if kind == 'labels' else 'notes'
            if not isinstance(row.get(notes_key), str):
                issue(kind, key, notes_key, 'malformed_notes', 'Keep notes column even when blank')
            if kind == 'labels':
                label = row.get('human_label', '')
                if label in LABELS and label != source['proposed_label']:
                    issue(kind, key, 'human_label', 'corpus_adjudication_required', 'Label disagreement/ambiguous class; no automatic relabel')
                if row.get('proposed_label_correct') == 'No':
                    issue(kind, key, 'proposed_label_correct', 'proposal_disagreement', 'Explicit corpus adjudication required')
                if label == source['proposed_label'] and row.get('proposed_label_correct') == 'No':
                    issue(kind, key, '', 'inconsistent_answers', 'Label agrees but proposal marked incorrect')
                evidence = row.get('evidence_span') or ''
                if not evidence.strip() or evidence not in source['Original']:
                    issue(kind, key, 'evidence_span', 'missing_or_nonexact_evidence', 'Exact Original span required for documented label')
            else:
                if ((row.get('meaning') == 'Yes' and row.get('semantic_drift') == 'Yes') or
                        (row.get('meaning') == 'No' and row.get('semantic_drift') == 'No')):
                    issue(kind, key, '', 'inconsistent_answers', 'Meaning/drift answers conflict; adjudicate')
                rejection = (row.get('meaning') == 'No' or row.get('stance') == 'No' or
                             row.get('semantic_drift') == 'Yes' or
                             (source['variant'] == 'Style' and row.get('style_change') == 'No'))
                if rejection and not (row.get('notes') or '').strip():
                    issue(kind, key, 'notes', 'rejection_needs_reason', 'Explain adverse decision; rejection is not a missing record')
                if rejection:
                    stats['pairs_human_rejected'] += 1
            if len(problems) == before:
                stats[kind + '_complete'] += 1
                final.append(row)
        resolved[kind] = final
    gate_error = ''
    passed = False
    if not problems and freeze is not None:
        try:
            policy_inputs([r for r in labels if r['split'] == 'train'],
                          [r for r in labels if r['split'] == 'validation'], pairs, freeze)
            passed = True
        except (ValueError, KeyError, TypeError) as exc:
            gate_error = str(exc)
    return dict(required_labels=148, required_pairs=210, labels_complete=stats['labels_complete'],
                pairs_complete=stats['pairs_complete'], pairs_human_rejected=stats['pairs_human_rejected'],
                issue_counts=dict(Counter(p['code'] for p in problems)), issues=problems,
                human_intake_complete=not problems, signed_freeze_supplied=freeze is not None,
                frozen_policy_gate_passed=passed, frozen_policy_error=gate_error,
                scientific_training_ready=passed, training_executed=False, test_evaluated=False)


def check(labels_path, pairs_path, output, freeze_path=None):
    report = inspect(read(labels_path), read(pairs_path),
                     json.loads(freeze_path.read_text(encoding='utf-8-sig')) if freeze_path else None)
    if output.exists():
        raise ValueError('Use a new report directory; preserve previous intake reports')
    output.mkdir(parents=True)
    shutil.copyfile(labels_path, output / 'received_labels.csv')
    shutil.copyfile(pairs_path, output / 'received_pairs.csv')
    if freeze_path:
        shutil.copyfile(freeze_path, output / 'received_freeze.json')
    provenance = dict(labels_input_sha256=sha(labels_path), pairs_input_sha256=sha(pairs_path),
                      protocol_sha256=sha(PROTOCOL), reviewer_identity_independently_authenticated=False,
                      freeze_input_sha256=sha(freeze_path) if freeze_path else None)
    (output / 'INPUT_MANIFEST.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    (output / 'READINESS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if report['issues']:
        save(output / 'ISSUES.csv', report['issues'])
    if report['human_intake_complete']:
        labels = read(labels_path)
        save(output / 'human_train_labels.csv', [r for r in labels if r['split'] == 'train'])
        save(output / 'human_validation_labels.csv', [r for r in labels if r['split'] == 'validation'])
        save(output / 'human_pair_reviews.csv', read(pairs_path))
    lines = ['# מוכנות אימות אנושי', '',
             f"תוויות תקינות ומוכרעות: {report['labels_complete']}/148; זוגות: {report['pairs_complete']}/210.", '',
             f"רשומות זוג שנדחו בידי אדם: {report['pairs_human_rejected']}. דחייה מנומקת אינה חוסר; fallback נקבע רק בפרוטוקול הקיים.", '',
             f"intake complete: {report['human_intake_complete']}; signed freeze supplied: {report['signed_freeze_supplied']}; frozen gate passed: {report['frozen_policy_gate_passed']}.", '',
             f"scientific_training_ready: {report['scientific_training_ready']}. לא הופעל אימון ולא נוצר snapshot מאושר.", '',
             'חסמים לפי סוג: ' + json.dumps(report['issue_counts'], ensure_ascii=False), '',
             'שגיאת gate: ' + (report['frozen_policy_error'] or 'none'), '',
             'התחלה מותרת רק אחרי השלמה, הכרעת מחלוקות, חתימת freeze, יצירת snapshot דרך ה-CLI הקיים והרשאת הרצה. '
             'הכלי אינו מאמת זהות אדם עצמאית ואינו מתקן תוויות או שכתובים.']
    (output / 'READINESS_HE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'issues'}, ensure_ascii=False))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('build')
    checker = sub.add_parser('check')
    checker.add_argument('--labels', type=Path, required=True)
    checker.add_argument('--pairs', type=Path, required=True)
    checker.add_argument('--output', type=Path, required=True)
    checker.add_argument('--signed-freeze', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        build()
    else:
        report = check(args.labels, args.pairs, args.output, args.signed_freeze)
        raise SystemExit(0 if report['scientific_training_ready'] else 2)


if __name__ == '__main__':
    main()

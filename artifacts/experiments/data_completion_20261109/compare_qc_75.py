"""Screen matched train paraphrases with frozen guards and report both methods.

Run automatic_qc.py for Style first. No generation, training, or test evaluation.
"""

import argparse
from collections import Counter
import importlib.util
import importlib.metadata
import json
import os
import sys

from automatic_qc import STUDY, binding
from bundle import FOLLOW, dump, mapping, read, save, sha, verify


def is_true(value):
    return str(value).lower() == 'true'


def load_helper(output):
    spec = importlib.util.spec_from_file_location('matched_qc_style', STUDY / 'study.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.OUT = output
    return helper


def screen_paraphrases(run):
    verify()
    path, received, identity = binding(run)
    output = path / 'paraphrase_qc'
    output.mkdir(exist_ok=True)
    sources = {row['ID']: row for row in mapping()}
    cohort = {row['row_id']: row for row in read(FOLLOW / 'analysis_cohort.csv')}
    original_generation = {
        row['row_id']: row
        for row in map(json.loads, (FOLLOW / 'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines())
        if row['condition'] == 'Paraphrase'
    }
    generated = []
    for row in received:
        record = dict(original_generation[row['ID']])
        assert record['original'] == row['Original']
        assert record['rewrite'] == sources[row['ID']]['Paraphrase']
        assert cohort[row['ID']]['split'] == 'train'
        generated.append(record)
    save(output / 'analysis_cohort.csv', [cohort[row['ID']] for row in received])
    (output / 'generated_rewrites.jsonl').write_text(
        ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in generated), encoding='utf-8'
    )
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    helper = load_helper(output)
    engine = helper.load_engine()
    assert engine.OUT == output and engine.base.OUT == output
    engine.validate()
    scale = engine.np.array(json.loads((STUDY / 'style_feature_scaling.json').read_text())['scale'])
    styles = []
    for row in generated:
        metrics = helper.style_metrics(row['original'], row['rewrite'])
        before = engine.np.array(engine.style_features(row['original']))
        after = engine.np.array(engine.style_features(row['rewrite']))
        metrics['explicit_style_mean_abs_standardized_change'] = float(engine.np.mean(engine.np.abs(after - before) / scale))
        styles.append(dict(ID=row['row_id'], **metrics))
    save(output / 'style_metrics.csv', styles)
    dump(output / 'VALIDATOR_IDENTITY.json', identity)
    verify()


def report(run):
    verify()
    path, received, identity = binding(run)
    comparisons = []
    summary = []
    results = {}
    for method, folder in [('Style', 'automatic_qc'), ('Paraphrase', 'paraphrase_qc')]:
        directory = path / folder
        checks = {row['row_id']: row for row in read(directory / 'rewrite_validation.csv')}
        styles = {row['ID']: row for row in read(directory / 'style_metrics.csv')}
        assert set(checks) == set(styles) == {row['ID'] for row in received}
        results[method] = (checks, styles)
        counts = Counter(reason for row in checks.values() for reason in row['rejection_reasons'].split('|') if reason)
        summary.append(dict(
            method=method, n=75,
            preservation_pass=sum(is_true(row['passed']) for row in checks.values()),
            substantial_style=sum(is_true(row['substantial_style_change']) for row in styles.values()),
            both=sum(is_true(checks[rid]['passed']) and is_true(styles[rid]['substantial_style_change']) for rid in checks),
            exact_copies=sum(is_true(row['exact_copy']) for row in styles.values()),
        ))
        save(directory / 'guard_failure_counts.csv', [dict(guard=key, count=value) for key, value in counts.most_common()],
             fields=['guard', 'count'])
    source_map = {row['ID']: row for row in mapping()}
    for pair in received:
        rid = pair['ID']
        row = dict(ID=rid, Original=pair['Original'], Style_Rewrite=pair['ChatGPT_Style_Rewrite'], Paraphrase=source_map[rid]['Paraphrase'])
        for method, (checks, styles) in results.items():
            row.update({f'{method}_{key}': value for key, value in checks[rid].items() if key not in ('row_id', 'condition')})
            row.update({f'{method}_{key}': value for key, value in styles[rid].items() if key != 'ID'})
        style_check = results['Style'][0][rid]
        priorities = []
        if not is_true(style_check['guard_bidirectional_nli']):
            priorities.append('NLI semantic risk; inspect claims, omissions, additions')
        for guard in ['numbers', 'entities', 'quotations', 'certainty', 'attribution', 'framing_anchors', 'negation', 'future_tense']:
            if not is_true(style_check['guard_' + guard]):
                priorities.append(guard)
        if not is_true(results['Style'][1][rid]['substantial_style_change']):
            priorities.append('style below existing proxy rule')
        row['human_review_attention'] = '; '.join(priorities) or 'No automatic flags; still requires independent human review'
        row['rhetorical_intensity_assessment'] = 'Not independently measured; framing anchors and NLI are incomplete proxies'
        comparisons.append(row)
    save(path / 'QC_COMPARISON_BY_ID_75.csv', comparisons)
    save(path / 'QC_METHOD_SUMMARY.csv', summary)
    attention = sorted(
        comparisons,
        key=lambda row: (
            is_true(row['Style_guard_bidirectional_nli']),
            is_true(row['Style_passed']),
            float(row['Style_validation_score']),
        ),
    )
    save(path / 'HUMAN_REVIEW_ATTENTION_75.csv', [
        dict(ID=row['ID'], attention=row['human_review_attention'],
             semantic_similarity=row['Style_semantic_similarity'],
             entailment_forward=row['Style_entailment_forward'],
             entailment_reverse=row['Style_entailment_reverse'],
             Original=row['Original'], Style_Rewrite=row['Style_Rewrite'])
        for row in attention
    ])
    style_checks, style_metrics = results['Style']
    para_checks, para_metrics = results['Paraphrase']
    style_only = [rid for rid in style_checks if is_true(style_checks[rid]['passed']) and not is_true(para_checks[rid]['passed'])]
    para_only = [rid for rid in style_checks if is_true(para_checks[rid]['passed']) and not is_true(style_checks[rid]['passed'])]
    new_flags = [
        dict(ID=rid, style_only_guard_failures='|'.join(sorted(
            set(style_checks[rid]['rejection_reasons'].split('|'))
            - set(para_checks[rid]['rejection_reasons'].split('|')) - {''}
        )))
        for rid in style_checks
    ]
    save(path / 'STYLE_FAILURES_NOT_IN_MATCHED_PARAPHRASE.csv', [row for row in new_flags if row['style_only_guard_failures']],
         fields=['ID', 'style_only_guard_failures'])
    lines = [
        '# QC אוטומטי — 75 שכתובים ופרפרזות תואמות', '',
        'תאריך בדיקה: 10.11.2026. רק 75 מקורות train שכבר הוגדרו; אין בחירת subset לפי תוצאות.', '',
        '## מקור ופרוטוקול', '',
        'לפי הצהרת המשתמשת: כל75 נוצרו ב־GPT-6 בתאריך 9.11.2026. גרסת מודל מדויקת, פרמטרי decoding ו־finish_reason אינם ידועים. הפרטים נשמרו כתוספת metadata, בלי דריסת receipts המקוריים. הפרפרזות הן התוצרים ההיסטוריים של אותם IDs, לא שכתובים חדשים.', '',
        'אותו validator קפוא: MPNet similarity≥0.85; DeBERTa entailment בכל כיוון≥0.6; אותם guards, token limits ו־style scaling. substantial: word edit≥0.15 ועוד sentence-length relative change≥0.15 או punctuation distance≥1/100 או contraction delta מוחלט≥1/100. ספים לא שונו ולא בוצע fit מחדש.', '',
        '## תוצאות', '',
        '| שיטה | N | מעבר כל preservation guards | פסילה | substantial style proxy | שניהם | exact copy |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for item in summary:
        lines.append(f"| {item['method']} | 75 | {item['preservation_pass']} | {75-item['preservation_pass']} | {item['substantial_style']} | {item['both']} | {item['exact_copies']} |")
    lines += ['', '## כשלי guards', '', '| guard | Style | Paraphrase |', '|---|---:|---:|']
    failures = {}
    for method, (checks, _) in results.items():
        failures[method] = Counter(reason for row in checks.values() for reason in row['rejection_reasons'].split('|') if reason)
    for guard in sorted(set(failures['Style']) | set(failures['Paraphrase'])):
        lines.append(f"| {guard} | {failures['Style'][guard]} | {failures['Paraphrase'][guard]} |")
    lines += [
        '', 'אפשר כמה דגלים לזוג אחד; אין לחבר את הספירות למספר הפסילות.', '',
        f"Style עבר ו־Paraphrase נפסל: {len(style_only)} — {', '.join(style_only) or 'אין'}.", '',
        f"Paraphrase עבר ו־Style נפסל: {len(para_only)} — {', '.join(para_only) or 'אין'}.", '',
        'זו השוואת signals בלבד. אין להסיק שאחת השיטות שומרת משמעות טוב יותר ללא סקירה עצמאית; הפרפרזה אינה בקרה מושלמת על כמות או סוג השינוי.', '',
        '## תוצאות לפי ID', '',
        '| ID | Style pass | Style substantial | Paraphrase pass | Paraphrase substantial | Style rejection reasons |',
        '|---|---|---|---|---|---|',
    ]
    for row in comparisons:
        reasons = row['Style_rejection_reasons'].replace('|', ', ') or '—'
        lines.append(f"| {row['ID']} | {row['Style_passed']} | {row['Style_substantial_style_change']} | {row['Paraphrase_passed']} | {row['Paraphrase_substantial_style_change']} | {reasons} |")
    lines += [
        '', '## תשומת לב באימות אנושי', '',
        'כל75 מחייבים סקירה; דגל אינו הוכחת drift ו־pass אינו gold. תחילה יש לבדוק דגלי NLI ושינויים בייחוס/ודאות/ציטוטים/ישויות/מספרים. הקובץ HUMAN_REVIEW_ATTENTION_75.csv הוא כלי ניתוח נפרד, ואינו חלק מהחבילה העיוורת לסוקר.', '',
        '| ID | סימני סיכון אוטומטיים |', '|---|---|',
    ]
    for row in attention[:15]:
        lines.append(f"| {row['ID']} | {row['human_review_attention']} |")
    lines += [
        '', '## מגבלות והחלטה', '',
        'אין במנגנון בדיקה ישירה מתוקפת של narrative/stance או rhetorical intensity. framing anchors הם קבוצת מילים שמורה, NLI הוא proxy, ו־style proxy אינו מדד לזיהוי כותב. ספירת negation אינה בדיקת scope; מספרים/ישויות/ציטוטים עלולים לייצר false positives או לפספס שינוי תפקידים. יש לבדוק גם כמתים, מטאפורות, עוצמת טענה וסיבתיות בכל75.', '',
        'בשכתובים finish_reason לא סופק: complete guard משתמש ב־truncated=False כברירת מחדל טכנית, ולא כראיה לתשובה מלאה. בפרפרזות נשמר metadata ההיסטורי. אין להציג את מספר ה־passes כמספר זוגות שמשמעותם אומתה.', '',
        'לא נערכו פלטים, לא השתנו guards או ספים, לא מולאו human fields, לא אומן Narrative Classifier ולא בוצעה הערכת test. כלל הקבלה האנושי הקיים נותר בתוקף.', '',
        '## שחזור וקבצים', '',
        'מה־repo root:', '', '```powershell',
        'python artifacts/experiments/data_completion_20261109/automatic_qc.py --run extension_v1_run01',
        'python artifacts/experiments/data_completion_20261109/compare_qc_75.py --run extension_v1_run01',
        'python artifacts/experiments/data_completion_20261109/verify_qc_results.py --run extension_v1_run01',
        '```', '',
        'קובצי פירוט: QC_COMPARISON_BY_ID_75.csv; QC_METHOD_SUMMARY.csv; HUMAN_REVIEW_ATTENTION_75.csv; STYLE_FAILURES_NOT_IN_MATCHED_PARAPHRASE.csv. תוצאות validator ומדדי style נפרדים בתיקיות automatic_qc ו־paraphrase_qc. QC_RUN_MANIFEST.json מכיל fingerprints; מודלים מקומיים באותן revisions. אין weights/caches/progress logs ב־Git. HUMAN_REVIEW_FOCUS_NOTES_HE.md מפרט שאלות לבדיקה בכמה IDs, ללא דירוגי review.',
    ]
    (path / 'QC_REPORT_HE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    dump(path / 'QC_RUN_MANIFEST.json', dict(
        evaluation_date='2026-11-10', methods=summary, validator=identity,
        python=sys.version, device='CPU',
        package_versions={name: importlib.metadata.version(name) for name in
                          ['torch', 'transformers', 'sentence-transformers', 'numpy', 'pandas']},
        received_outputs_sha256=sha(path / 'received_rewrites_75.csv'),
        paraphrase_inputs_sha256=sha(path / 'paraphrase_qc' / 'generated_rewrites.jsonl'),
        generation_metadata_supplement_sha256=sha(path / 'GENERATION_METADATA_SUPPLEMENT_20261110.json'),
        human_validation=False, narrative_classifier_run=False, test_evaluation=False,
        caution='Automatic screening only; no dedicated validated narrative/stance/rhetorical-intensity metric.',
    ))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    if not args.report_only:
        screen_paraphrases(args.run)
    report(args.run)

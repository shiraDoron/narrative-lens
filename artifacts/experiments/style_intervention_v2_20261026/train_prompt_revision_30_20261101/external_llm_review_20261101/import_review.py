"""Import supplied ratings as data; never run a judge or change screening."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import shutil
import sys

OUT = Path(__file__).resolve().parent
RUN = OUT.parent
STUDY = RUN.parent
NAME = 'NEW_NORMALIZED_EXTERNAL_LLM_REVIEW_30_20261101.csv'
FIELDS = ['meaning_preserved', 'stance_preserved', 'attribution_preserved',
          'certainty_preserved', 'style_change_valid', 'semantic_drift']
MARKER = '## New Normalized — External LLM Review 2026-11-01'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def table(headers, rows):
    def clean(v):
        return str(v).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join('| ' + ' | '.join(map(clean, row)) + ' |'
                     for row in [headers, ['---'] * len(headers), *rows])


def update_docs():
    section = (OUT / 'CENTRAL_SECTION_HE.md').read_text(encoding='utf-8')
    for path in [STUDY / 'EXPERIMENT_GUIDE_HE.md', STUDY / 'FINAL_REPORT_HE.md', RUN / 'REPORT_HE.md']:
        text = path.read_text(encoding='utf-8').split(MARKER, 1)[0].rstrip()
        # The full report lives beside this section; central documents need a relative link.
        prefix = 'train_prompt_revision_30_20261101/' if path.parent == STUDY else ''
        text += '\n\n' + section + '\n\n[הדוח המלא וכל 30 ההכרעות](' + prefix + 'external_llm_review_20261101/REPORT_HE.md)\n'
        path.write_text(text, encoding='utf-8')


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / NAME
    if not source.exists():
        source = Path.home() / 'Downloads' / NAME
    protected = {p: sha(p) for p in STUDY.rglob('*') if p.is_file()
                 and OUT not in p.parents and '__pycache__' not in p.parts
                 and p.suffix in {'.csv', '.json', '.jsonl', '.txt', '.html', '.py'}}
    raw = read(source)
    comparison = read(RUN / 'comparison_30.csv')
    lookup = {r['ID']: r for r in comparison}
    assert len(raw) == 30 and len({r['id'] for r in raw}) == 30
    assert {r['id'] for r in raw} == set(lookup)
    assert set(raw[0]) == {'id', 'notes', *FIELDS}
    assert all(r['split'] == 'train' for r in comparison)
    assert all(r[f] in {'Yes', 'No', 'Borderline'} for r in raw for f in FIELDS)
    copy = OUT / NAME
    if copy.exists():
        assert sha(copy) == sha(source), 'Refuse to overwrite a different review'
    else:
        shutil.copyfile(source, copy)
    assert copy.read_bytes() == source.read_bytes()
    joined = []
    for r in raw:
        base = lookup[r['id']]
        row = dict(base)
        row.update({'external_' + k: v for k, v in r.items() if k != 'id'})
        row['evaluation_type'] = 'External LLM Review — New Normalized'
        row['human_verified'] = False
        row['external_strict_preservation'] = all(r[f] == 'Yes' for f in FIELDS[:4]) and r['semantic_drift'] == 'No'
        rejected = base['New_automatic_pass'] == 'False'
        risk = r['semantic_drift'] == 'Yes' or r['meaning_preserved'] == 'Borderline'
        preserved = r['meaning_preserved'] == 'Yes' and r['semantic_drift'] == 'No'
        assert risk or preserved, 'Unresolved external rating combination'
        row['discrepancy_class_relative_to_llm'] = (
            'True Positive' if rejected and risk else
            'False Positive' if rejected and preserved else
            'False Negative' if risk else 'True Negative')
        row['external_borderline_separate'] = r['meaning_preserved'] == 'Borderline'
        row['classification_basis'] = ('explicit semantic_drift=Yes; meaning=' + r['meaning_preserved']
            if r['semantic_drift'] == 'Yes' else 'meaning=' + r['meaning_preserved'] + '; semantic_drift=' + r['semantic_drift'])
        joined.append(row)
    write_csv('external_review_joined.csv', joined)
    discrepancies = []
    for row in joined:
        screen = json.loads(row['new_validation_json'])
        d = {k: row[k] for k in ['ID', 'split', 'New_automatic_pass', 'New_rejection_reasons',
             'external_meaning_preserved', 'external_semantic_drift', 'external_style_change_valid',
             'discrepancy_class_relative_to_llm', 'external_borderline_separate', 'classification_basis', 'external_notes']}
        d.update({'automatic_' + k: v for k, v in screen.items() if k.startswith('guard_') or k in
                  {'semantic_similarity', 'entailment_forward', 'entailment_reverse'}})
        discrepancies.append(d)
    write_csv('discrepancy_classification_30.csv', discrepancies)
    write_csv('borderline_cases_15.csv', [r for r in discrepancies if r['external_borderline_separate']])
    classes = dict(collections.Counter(r['discrepancy_class_relative_to_llm'] for r in joined))
    class_ids = {c: [r['ID'] for r in joined if r['discrepancy_class_relative_to_llm'] == c] for c in classes}
    class_meaning = [dict(classification=c, meaning_preserved=m,
                         count=sum(r['discrepancy_class_relative_to_llm'] == c and r['external_meaning_preserved'] == m for r in joined))
                     for c in ['True Positive', 'False Positive', 'True Negative', 'False Negative']
                     for m in ['Yes', 'Borderline', 'No']]
    write_csv('classification_by_meaning.csv', class_meaning)
    counts = {f: dict(collections.Counter(r[f] for r in raw)) for f in FIELDS}
    cross = collections.Counter((r['New_automatic_pass'], r['external_meaning_preserved']) for r in joined)
    cross_rows = [dict(automatic_pass=a, external_meaning_preserved=m, count=cross[a, m])
                  for a in ['True', 'False'] for m in ['Yes', 'Borderline', 'No']]
    write_csv('automatic_vs_external.csv', cross_rows)
    yes = [r['ID'] for r in joined if r['external_strict_preservation']]
    fp = [r['ID'] for r in joined if r['New_automatic_pass'] == 'False' and r['external_strict_preservation']]
    missed = [r['ID'] for r in joined if r['New_automatic_pass'] == 'True' and r['external_meaning_preserved'] != 'Yes']
    old = json.loads((STUDY / 'external_llm_review_20261101/summary.json').read_text(encoding='utf-8'))
    summary = dict(n=30, scope='Purposive TRAIN-only development sample', counts=counts,
                   evaluation_type='External LLM Review — New Normalized',
                   discrepancy_classes_relative_to_llm=classes, discrepancy_class_ids=class_ids,
                   borderline_ids=[r['ID'] for r in joined if r['external_borderline_separate']],
                   classification_by_meaning=class_meaning,
                   strict_preservation_count=len(yes), strict_preservation_ids=yes,
                   strict_preservation_and_style_count=sum(r['external_strict_preservation'] and r['external_style_change_valid'] == 'Yes' for r in joined),
                   candidate_guard_false_positive_ids=fp, automatic_pass_but_external_not_yes_ids=missed,
                   old_external_counts=old['counts'],
                   evaluator_model='Not supplied', evaluation_prompt='Not supplied', evaluation_timestamp='Not supplied',
                   review_text_binding='IDs and user-supplied filename/context only; source has no reviewed-text hashes',
                   blinded='Not established', blinding_note='Comparison pack exposes author and Old/New versions; evaluator inputs not independently logged',
                   human_verified=False)
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    metrics = table(['שדה חיצוני', 'Yes', 'Borderline', 'No'], [[f, counts[f].get('Yes', 0), counts[f].get('Borderline', 0), counts[f].get('No', 0)] for f in FIELDS])
    section = f'''{MARKER}

יובא קובץ הבדיקה החיצונית של כל 30 ה־New Normalized, בהתאמת ID מלאה למדגם train בלבד. ההכרעות להלן הן דירוגי LLM שסופקו, לא שיפוט חדש של סוכן הייבוא ולא אימות אנושי. גרסת המודל, prompt ההערכה ומועד ההערכה המדויק לא סופקו. הקובץ אינו מכיל hash או טקסט שנסקר; שיוך הגרסאות נשען על ה־IDs והקשר המסירה. אין לטעון לבדיקה עיוורת או לעצמאות בין הסבבים.

**שם הבדיקה: External LLM Review — New Normalized.** היא נשמרת בנפרד מ־Human Validation ומבדיקת ה־Old Normalized הקודמת.

{metrics}

Meaning Preserved: **10/30 Yes, ‏15/30 Borderline, ‏5/30 No**. שינוי style אמיתי לפי ה־External LLM Review: **30/30**; זהו דירוג הבודק החיצוני ולא אימות אנושי.

### סיווג פערים ביחס ל־LLM

"Positive" פירושו איתות לסיכון בשימור משמעות. True/False מתארים התאמה ל־LLM בלבד, לא אמת מחקרית מאומתת. פסילה אוטומטית ו־semantic_drift=Yes מסווגת True Positive; פסילה עם meaning=Yes ו־drift=No היא False Positive; מעבר עם אותו אישור הוא True Negative; מעבר עם drift=Yes או Borderline משמעותי הוא False Negative. כל 15 מקרי ה־Borderline בקובץ מסומנים גם semantic_drift=Yes במקור, ולכן הסיווג נשען על דגל מפורש, בלי להמיר meaning=Borderline ל־No. שדה המשמעות המקורי נשמר, וכן קובץ Borderline נפרד ופירוט בכל קטגוריה.

{table(['סיווג ביחס ל־LLM', 'סה״כ', 'Meaning Yes', 'Meaning Borderline', 'Meaning No'], [[c, classes.get(c, 0), *[next(x['count'] for x in class_meaning if x['classification'] == c and x['meaning_preserved'] == m) for m in ['Yes', 'Borderline', 'No']]] for c in ['True Positive', 'False Positive', 'True Negative', 'False Negative']])}

פסילות שנראו מוצדקות לפי ה־LLM (True Positive): {', '.join(class_ids.get('True Positive', []))}.

פסילות שנראו False Positives לפי ה־LLM: {', '.join(class_ids.get('False Positive', []))}.

עברו אוטומטית אך קיבלו Borderline/No: {', '.join(missed)} — במקרה זה Borderline, ואין מקרה שעבר וקיבל No.

דוגמאות הכשל המרכזיות לפי הבודק: `417181` — semantic drift והתחזקות certainty, לצד שינוי ייחוס; `8b0d99b23d03` — שינוי הציטוט המיוחס ל־F. Scott Fitzgerald ושינוי מטאפורת “two countries”; `423545` — החלשת stance/המסגור באמצעות הסרת “right-wing hack” והחלשת המטאפורה (למרות שדה stance_preserved=Yes, שנשמר כמות שהוא); `298495` — שינוי עובדתי מ־strangers ל־anonymous sources; `418904` — שינוי ציטוט ישיר. אלו פירושים לתוצאות ה־LLM שסופקו, ולא הכרעות אנושיות חדשות או אימות פרטני של כל guard.

שימור מחמיר לצורך סיכום בלבד (meaning, stance, attribution, certainty כולם Yes וגם semantic_drift=No): **{len(yes)}/30**; שימור מחמיר ושינוי style=Yes יחד: **{summary['strict_preservation_and_style_count']}/30**. זהו חיתוך תיאורי של שדות חיצוניים, לא שינוי סף קבלה או מסנן.

מבין הפסילות האוטומטיות, {len(fp)} דורגו כשימור מחמיר — מועמדים ל־false positives ביחס לבודק החיצוני, לא הוכחת תקינות. מבין המעברים האוטומטיים, {len(missed)} קיבלו meaning שאינו Yes. אין להמיר אי־הסכמה עם LLM ל־false positive/negative מאומת. Borderline נשמר בנפרד ואינו נספר כהצלחה; semantic_drift=Yes הוא קביעת ה־LLM בלבד.

`creators:120669`: הבודק מציין שהטעות Obama/Washington הקודמת תוקנה. `212505`: הבודק רואה ב־10→ten שינוי עיצוב בלבד ומאשר שימור. `419062` ו־`224770` מאושרים לשימור ולסגנון; לעומתם `423315`, שעבר בסינון, דורג Borderline בגלל riots→protests ו־going to lose→destined to lose. `421951` עבר אוטומטית ואושר חיצונית; זו עדיין אינה אמת אנושית. `298495` דורג No במשמעות בגלל strangers→anonymous sources, אף ששדה attribution דורג Yes; ההבדל בין השדות נשמר. `114783` דורג Borderline עם פגיעה בנאמנות לציטוט. אין להסיק מכך שדגלי negation/attribution שלו אומתו פרטנית.

ה־LLM דירג שינוי style כ־Yes בכל 30 המקרים. לעומת זאת ה־proxy האוטומטי סימן 24/30. בבדיקה החיצונית הקודמת של Old Normalized היו meaning=Yes ב־27/30 ו־style=Yes ב־9/30; אין זו השוואה מבוקרת בין מעריכים, ואין לערבב ספירות חיצוניות עם 23→6 ו־10→24 האוטומטיות. התמונה התיאורית היא שינוי סגנוני רחב יותר לצד יותר הסתייגויות משימור משמעות.

לא שונו prompt, guards, ספים, טקסטים, תוויות, split, test או שדות human review; לא הורצו מודל שופט, שכתוב נוסף או אימון. הבדיקה אינה פותחת את שער האימות האנושי לאימון. עוצרים לדיון בתוצאות לפני כל ניסוי או כוונון נוסף.

**ה־prompt החדש מצליח לייצר שינוי סגנוני משמעותי, אבל מגדיל את הסיכון ל־semantic drift. הבדיקות האוטומטיות מזהות חלק מהכשלים, אך יש גם false positives וגם מקרים שהן אינן מספיקות לבדן.** זו מסקנת הפיתוח הנוכחית על המדגם המכוון ובהסתמך על דירוגי ה־External LLM Review, לא אומדן על test.
'''
    (OUT / 'CENTRAL_SECTION_HE.md').write_text(section, encoding='utf-8')
    full = section + '\n\n' + table(['ID', 'Auto pass', 'Auto reasons', 'סיווג ביחס ל־LLM', *FIELDS, 'הערות LLM'],
        [[r['ID'], r['New_automatic_pass'], r['New_rejection_reasons'], r['discrepancy_class_relative_to_llm'], *[r['external_' + f] for f in FIELDS], r['external_notes']] for r in joined])
    full += '\n\n' + table(['Auto pass', 'Meaning LLM', 'N'], [[r['automatic_pass'], r['external_meaning_preserved'], r['count']] for r in cross_rows])
    full += '\n\nמועמדי false positive ביחס ל־LLM: ' + ', '.join(fp) + '\n\nמעבר אוטומטי עם הסתייגות חיצונית: ' + ', '.join(missed) + '\n'
    (OUT / 'REPORT_HE.md').write_text(full, encoding='utf-8')
    update_docs()
    changed = [str(p.relative_to(STUDY)) for p, digest in protected.items() if sha(p) != digest]
    assert not changed, changed
    audit = dict(source_file=source.name, source_sha256=sha(source), copied_sha256=sha(copy),
                 comparison_sha256=sha(RUN / 'comparison_30.csv'), exact_ids=True, all_train=True,
                 protected_data_files=len(protected), changed_protected_data_files=changed,
                 no_training=True, no_filter_or_prompt_changes=True, no_human_field_updates=True)
    (OUT / 'import_audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(counts=counts, strict=len(yes), candidate_false_positives=fp, missed=missed)))


if __name__ == '__main__':
    main()

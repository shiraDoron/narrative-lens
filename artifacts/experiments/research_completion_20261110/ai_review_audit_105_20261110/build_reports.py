"""Archive the supplied AI review and publish explicit assistant AI assessments.

Judgments live in review_decisions.py; this script only validates and formats them.
It does not generate judgments, human gold, rewrites, or training acceptance.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import ROOT, COMPLETION, RUN, candidates, dump, read, save, sha, text_sha, verify
from review_decisions import DECISIONS

RATINGS = {'Yes', 'No', 'Borderline'}
FIELDS = ['ai_meaning_preserved', 'ai_narrative_preserved', 'ai_style_change_valid']
SPECIAL = ['creators:424146', 'creators:423371', 'creators:3fd01161cd76', 'creators:421811']
SECOND_PASS = {
    'creators:424146': 'נבדקו שוב שני המשפטים: regarding his habitual whitewashing של המספר נעשה what Dashti described as. ייחוס חדש מפורש אכן קיים; נשמרו No/Borderline/Yes.',
    'creators:423371': 'נבדקו מחדש שני המשפטים יחד: דוגמת floated the idea תומכת בהקשר בדיעבד, ו־allowing עדיין כפוף ל־proposal. טענת הסקירה שהסובסידיה הוצגה כעובדה אינה נתמכת. נשאר ספק בפרספקטיבת as it degenerated, לכן Borderline ולא No.',
    'creators:3fd01161cd76': 'נבדק שוב כל קטע המתכון, לא רק becomes: have devised ו־Their recipe משמרים את הקשר התורמים למעשה. No בשל היעלמות סוכנות אינו מוצדק. many עדיין נעדר ולכן Borderline במשמעות, והנרטיב נשמר.',
    'creators:421811': 'נבדקו שוב שני דימויי הכובשים וכל המשפט: and→or הוא שינוי אמיתי, אך הטענה המטאפורית אינה בהכרח צירוף לוגי פורמלי. סיכון קיים בלי בסיס ל־No ודאי; Borderline במשמעות ו־Yes בנרטיב הביקורתי.',
}


def parse_source(path):
    result = []
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        cells = [part.strip() for part in line.split('|')]
        if len(cells) < 8 or not cells[1].isdigit() or not cells[2].startswith('creators:'):
            continue
        ratings = [cell.replace('**', '').strip() for cell in cells[3:6]]
        if not all(rating in RATINGS for rating in ratings):
            raise ValueError('Invalid source review rating')
        result.append(dict(ID=cells[2], meaning=ratings[0], narrative=ratings[1], style=ratings[2], notes=cells[6]))
    if len(result) != 15 or len({row['ID'] for row in result}) != 15:
        raise ValueError('Expected15 unique source review IDs')
    return result


def protected_hashes():
    paths = [
        HERE.parent / 'human_review_batch_01_15/REVIEW_15_HE.md',
        HERE.parent / 'HUMAN_STYLE_REVIEW_105.md', HERE.parent / 'HUMAN_STYLE_REVIEW_105.csv',
        HERE.parent / 'PAIRED_QC_INTAKE_210.csv', HERE.parent / 'NARRATIVE_LABEL_VALIDATION_105.csv',
        HERE.parent / 'NARRATIVE_LABEL_VALIDATION_43_VALIDATION.csv',
        RUN / 'received_rewrites_75.csv',
    ]
    return {str(path.relative_to(ROOT)): sha(path) for path in paths}


def counts(rows):
    return {field: dict(Counter(row[field] for row in rows)) for field in FIELDS}


def escaped(value):
    return str(value).replace('|', '&#124;').replace('\n', '<br>')


def render_details(path, rows, title):
    lines = [title, '', 'סקירת AI של ChatGPT/Codex, לא Claude ולא Human Validation. לא עיוורת ל־QC ולביקורת הקודמת של15. Meaning/Narrative/Style נשפטו בנפרד; אין אישור קבלה לאימון.', '']
    for row in rows:
        lines += [f"## {row['ID']}", '',
                  f"**Meaning:** {row[FIELDS[0]]} | **Narrative:** {row[FIELDS[1]]} | **Style:** {row[FIELDS[2]]}", '',
                  '### Original', '', row['Original'], '', '### Style Rewrite', '', row['Style_Rewrite'], '',
                  '**נימוק AI:** ' + row['ai_notes'], '',
                  '**סוגי סיכון/ניואנס:** ' + (row['ai_risk_types'] or 'לא זוהה סיכון מהותי בקריאה זו'), '']
        if row['ID'] in SECOND_PASS:
            lines += ['**בדיקה חוזרת:** ' + SECOND_PASS[row['ID']], '']
    path.write_text('\n'.join(lines), encoding='utf-8')


def build(source):
    verify()
    before = protected_hashes()
    if (HERE / 'SOURCE_CHATGPT_REVIEW_15_RECEIVED.md').exists() or (HERE / 'AI_REVIEW_ALL_105.csv').exists():
        raise ValueError('AI review snapshot exists; no overwrite')
    prior = parse_source(source)
    selected = json.loads((HERE.parent / 'human_review_batch_01_15/SELECTION_MANIFEST.json').read_text())['rows']
    if [row['ID'] for row in prior] != [row['ID'] for row in selected]:
        raise ValueError('Source review does not match the selected15 packet')
    canonical = candidates()
    if set(DECISIONS) != {row['ID'] for row in canonical}:
        raise ValueError('Incomplete or unexpected assistant judgments')
    rows = []
    prior_by_id = {row['ID']: row for row in prior}
    for row in canonical:
        meaning, narrative, style, risks, notes = DECISIONS[row['ID']]
        if not {meaning, narrative, style} <= RATINGS or not notes:
            raise ValueError('Invalid or unsupported assistant judgment')
        rows.append(dict(
            ID=row['ID'], Original=row['Original'], Style_Rewrite=row['Style'],
            ai_meaning_preserved=meaning, ai_narrative_preserved=narrative, ai_style_change_valid=style,
            ai_risk_types='|'.join(risks), ai_notes=notes,
            ai_reviewer='ChatGPT/Codex session; exact model revision unknown', review_date='2026-11-10',
            review_type='AI review, not human validation', is_human_review=False, blind_review=False,
            source_sha256=text_sha(row['Original']), rewrite_sha256=text_sha(row['Style']),
            style_protocol_cohort=row['style_protocol_cohort'],
            source_review_available=row['ID'] in prior_by_id,
            second_pass_notes=SECOND_PASS.get(row['ID'], ''),
        ))
    by_id = {row['ID']: row for row in rows}
    first = [by_id[row['ID']] for row in prior]
    remaining = [row for row in rows if row['ID'] not in prior_by_id]
    assert len(first) == 15 and len(remaining) == 90
    shutil.copyfile(source, HERE / 'SOURCE_CHATGPT_REVIEW_15_RECEIVED.md')
    save(HERE / 'SOURCE_CHATGPT_REVIEW_15_PARSED.csv', prior)
    save(HERE / 'AI_REVIEW_ALL_105.csv', rows)
    save(HERE / 'SECOND_AI_REVIEW_15.csv', first)
    save(HERE / 'AI_REVIEW_REMAINING_90.csv', remaining)
    changes = []
    for old in prior:
        new = by_id[old['ID']]
        changed = [name for name, field in zip(['Meaning', 'Narrative', 'Style'], FIELDS)
                   if old[name.lower()] != new[field]]
        changes.append(dict(
            ID=old['ID'], source_ai_meaning=old['meaning'], audited_ai_meaning=new[FIELDS[0]],
            source_ai_narrative=old['narrative'], audited_ai_narrative=new[FIELDS[1]],
            source_ai_style=old['style'], audited_ai_style=new[FIELDS[2]],
            changed_fields='|'.join(changed), source_ai_notes=old['notes'], audit_ai_notes=new['ai_notes'],
            second_pass_notes=SECOND_PASS.get(old['ID'], ''),
        ))
    save(HERE / 'DECISION_COMPARISON_15.csv', changes)
    render_details(HERE / 'SECOND_AI_REVIEW_15_HE.md', first, '# ביקורת AI נוספת — כל15 הזוגות')
    render_details(HERE / 'AI_REVIEW_REMAINING_90_HE.md', remaining, '# המשך סקירת AI — יתר90 הזוגות')
    summary = dict(
        source15={name: dict(Counter(row[name] for row in prior)) for name in ['meaning', 'narrative', 'style']},
        audited15=counts(first), remaining90=counts(remaining), all105=counts(rows),
        changed_ids=[row['ID'] for row in changes if row['changed_fields']],
        changed_fields=sum(len(row['changed_fields'].split('|')) for row in changes if row['changed_fields']),
        all_three_yes=sum(all(row[field] == 'Yes' for field in FIELDS) for row in rows),
        all_three_yes_not_training_acceptance=True,
    )
    dump(HERE / 'REVIEW_SUMMARY.json', summary)
    dump(HERE / 'SOURCE_RECEIPT.json', dict(
        original_filename=source.name, original_sha256=sha(source),
        archived_sha256=sha(HERE / 'SOURCE_CHATGPT_REVIEW_15_RECEIVED.md'),
        reviewer_user_declared='ChatGPT', exact_model_revision=None,
        review_date_in_document='2026-11-10', prompt_and_request_history_provided=False,
        original_review_edited=False, per_id_source_texts_embedded_in_received_review=False,
        binding_basis='ID order matches the15 packet; source reviewer generation history cannot be verified',
    ))
    assert before == protected_hashes()
    dump(HERE / 'REVIEW_PROVENANCE.json', dict(
        date='2026-11-10', reviewer='ChatGPT/Codex', exact_model_revision=None,
        is_human=False, is_blind=False, independent_different_model_verified=False,
        source_review_visible=True, prior_qc_and_focus_notes_visible=True,
        review_basis='Direct assistant reading of105 complete Original/Style pairs; judgments recorded in review_decisions.py',
        no_guard_or_keyword_rule_computes_judgments=True,
        no_external_model_api_called=True, no_training=True, no_test_evaluation=True,
        original_reviews_preserved=True, source_texts_edited=False, human_fields_edited=False,
        protected_source_sha256=before,
    ))
    lines = ['# ביקורת סקירת AI והמשך לכל105 — 10.11.2026', '',
             '**זו שכבת AI נוספת, לא אימות אנושי ולא סקירה עיוורת של מודל אחר.** העוזר הוא ChatGPT/Codex; אין לייחס לו את השם Claude. הסקירה שסופקה ו־QC קודמים היו גלויים. אי־תלות בין מודלים אינה מוכחת.', '',
             '## מה בוצע', '',
             '- המקור המצורף נשמר byte-for-byte, ונבדקו15 IDs מול חבילת הסקירה. המקור אינו מכיל את הטקסטים עצמם ולכן היסטוריית יצירתו ושאלת הגרסה שראה המודל אינן ניתנות לאימות מלא.',
             '- כל15 ההכרעות נבחנו מול Original ו־Style המלאים. ארבעת המקרים424146,423371,3fd01161cd76,421811 נקראו שוב בהקשר מלא.',
             '- נקראו ונשפטו גם כל90 הזוגות הנותרים באותה מתודולוגיה. הסך הכולל105, לא120; הראשונים הם תת־קבוצה.', '',
             '## השוואת15 ההכרעות', '',
             '| ID | Meaning קודם → ביקורת | Narrative קודם → ביקורת | Style קודם → ביקורת | נימוק הביקורת |',
             '|---|---|---|---|---|']
    for row in changes:
        lines.append('| ' + ' | '.join([
            row['ID'], row['source_ai_meaning'] + ' → ' + row['audited_ai_meaning'],
            row['source_ai_narrative'] + ' → ' + row['audited_ai_narrative'],
            row['source_ai_style'] + ' → ' + row['audited_ai_style'], escaped(row['audit_ai_notes']),
        ]) + ' |')
    lines += ['', f"השתנו הכרעות ב־{len(summary['changed_ids'])} מתוך15 IDs, ובסך הכול{summary['changed_fields']} שדות. אלה תיקוני הערכת AI, לא שיפור בטקסטים ולא agreement אנושי.", '',
              '## בדיקה חוזרת בארבעת המקרים', '']
    for rid in SPECIAL:
        lines += [f'### {rid}', '', SECOND_PASS[rid], '']
    lines += ['## סיכום ההכרעות — ספירות AI בלבד', '',
              '| קבוצה | Meaning Yes / Borderline / No | Narrative Yes / Borderline / No | Style Yes / Borderline / No |',
              '|---|---|---|---|']
    for label, group in [('15 בביקורת הנוספת', first), ('90 בהמשך', remaining), ('כל105', rows)]:
        triplets = []
        for field in FIELDS:
            counted = Counter(row[field] for row in group)
            triplets.append(' / '.join(str(counted[value]) for value in ['Yes', 'Borderline', 'No']))
        lines.append('| ' + ' | '.join([label, *triplets]) + ' |')
    lines += ['', '## עקביות וגבולות', '',
              'Meaning נבחן כטענות, יחסים, ייחוס, מודאליות, כמתים וזמן. Narrative נבחן כעמדה/מסגור ועוצמה: שינוי עובדתי אינו בהכרח החלפת עמדה. Style הוא שינוי ניכר באופן ההבעה, לא אישור להתערבות כולה; ייתכן Meaning No לצד Style Yes. near-copy מדורג Borderline או No גם כשהמשמעות נשמרת.', '',
              'אין להפוך כל שינוי tense ל־drift: would יכול להיות עתיד־בעבר, ו־would בתוך announced עשוי להיות backshift. אין להפוך פסיב או נושא לא־מפורש לאובדן סוכנות בלי לקרוא את ההקשר. שינוי פיסוק בציטוט מתועד כ־fidelity issue אך לא תמיד מחליף משמעות. מטאפורה עם and/or דורשת זהירות לפני לוגיקה פורמלית. Borderline נשמר כספק אמיתי, לא כ־Yes.', '',
              'הכרעות AI נוספות עדיין עשויות לטעות. לא נבדקה אמת היסטורית/פוליטית במקורות חיצוניים. שלושת Yes אינם כלל הקבלה המלא ואינם human gold; אין כאן החלטת סינון, שינוי labels או אימון. חבילת האדם נשארה ריקה ועצמאית מתוצאות אלה.', '',
              '## מקרים נוספים לתשומת לב אנושית', '']
    for row in rows:
        if row[FIELDS[0]] == 'No' or row[FIELDS[2]] == 'No':
            lines += [f"- **{row['ID']}** — {row['ai_notes']}"]
    lines += ['', '## קבצים ושחזור', '',
              '- [סקירת המקור שנשמרה](SOURCE_CHATGPT_REVIEW_15_RECEIVED.md).',
              '- [ביקורת15 עם כל הטקסטים](SECOND_AI_REVIEW_15_HE.md), [טבלת שינויי הכרעה](DECISION_COMPARISON_15.csv).',
              '- [סקירת יתר90 עם כל הטקסטים](AI_REVIEW_REMAINING_90_HE.md), [כל105 ב־CSV](AI_REVIEW_ALL_105.csv).',
              '- REVIEW_PROVENANCE.json ו־SOURCE_RECEIPT.json מתעדים זהות AI, חשיפה ל־QC, מגבלות והגנה על מקורות.', '',
              'ההכרעות נרשמו ידנית ב־review_decisions.py לאחר קריאה, ולא מחושבות מה־guards. build_reports.py מסדר אותן ושומר raw; הוא מסרב לדרוס snapshot קיים. בדיקות השחזור מאמתות ספירות/IDs/hashes, לא נכונות סמנטית.']
    (HERE / 'AI_AUDIT_SUMMARY_HE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    verify()
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    build(parser.parse_args().source)

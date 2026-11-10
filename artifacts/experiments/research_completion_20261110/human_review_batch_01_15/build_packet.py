"""Create a first15 QC-assisted review packet without editing or judging any pair."""

import difflib
import html
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import RUN, read, dump, sha, text_sha, verify

FOCUS = {
    'creators:417661': [
        'בדקו שכל ההאשמות, המשתתפים והפעלים נשמרו אחרי מעבר מרצף “that he…” לצירופים שמניים.',
        'האם הפיצול לשלושה משפטים שומר על אותה אחריות לטענות ואותה עוצמה רטורית?',
    ],
    'creators:420299': [
        'השוו “According to polls” ל־“Polls show”: האם ייחוס הטענה ומידת הביטחון בה נשמרים?',
        'בדקו את “not only… but…” מול “not just”, ואת “are going to lose… because” מול “will cost”.',
        'האם “What I don\'t buy” שומר על עוצמת דחיית הטענה ועל היקף השלילה?',
    ],
    'creators:424146': [
        'מי מציג את ההאשמה על whitewashing במקור, ומי בשכתוב שבו נוסף “what Dashti described as”?',
        'האם “is a victim” מול “has suffered” וסידור האירועים החדש משמרים מצב, זמן ותפקידים?',
    ],
    'creators:422259': [
        'האם “all the solutions” ו־“every solution” מבטאים אותו היקף בהקשר הזה?',
        'בדקו שדרישת הפתיחות לאחרים נשמרה אחרי ארגון מחדש של must/require, ושהציטוטים נשארו מילוליים.',
    ],
    'creators:423650': [
        'האם התוספת “only” לפני seven weeks משפיעה על הדגשה או על דחיפות?',
        'השוו “That means becoming serious” ל־“Congress must get serious”: האם נשמרו עוצמת החיוב והגורם שאליו הוא מופנה?',
        'בדקו שיחס התנאי “unless” בין גיבוי החוב, עודפים עתידיים ויכולת הפד נשאר זהה.',
    ],
    'creators:416848': [
        'האם could→might שומר על אותו סוג אפשרות במשפט ההיפותטי?',
        'השוו “if doing so threatened their power” ל־“when that condemnation would threaten their power”: האם התנאי נשמר?',
    ],
    'creators:418916': [
        'בדקו אם “exceedingly likely” ו־“likelihood… remains exceedingly high” שומרים על אותה ודאות.',
        'השוו “As much as we may not like it” ל־“Whether we like it or not” מבחינת תנאי ועוצמה.',
        'האם איחוד רצף המשפטים על מלחמה משמר את כל הדוגמאות וההדגשה הרטורית?',
    ],
    'creators:419965': [
        'בדקו “That might explain why” מול “Perhaps that explains” מבחינת מידת הוודאות והסיבתיות.',
        'בשכתוב מופיע “a farmer may "technically owns"”: האם נוסף רכיב אפשרות/הרשאה או נוצר קושי שמפריע להבנת טענת הבעלות?',
        'האם איסור התיקונים, החובה לפנות לסוחר וההכללה “most farmers” נשמרים? אל תתקנו את הניסוח בטופס.',
    ],
    'creators:423371': [
        'השוו את מיקום probably ואת הקשר בין פופוליזם להבטחות: האם נשמרת אותה הערכה ולא קביעה חזקה יותר?',
        'בדקו “could get” מול “allowing… to receive”: האם עדיין מדובר בהצעה אפשרית ולא בזכאות שכבר נקבעה?',
        'ודאו שהסכום, התנאים לקבוצת הזכאים והמטרה per child for daycare נשמרים.',
    ],
    'creators:296082': [
        'האם “never flew” ו־“the conspiracy theory denying… had flown” משמרים את השלילה ואת ייחוסה לתאוריה, ולא למספר?',
        'בדקו שכל שלוש הפעולות המיוחסות למשתתפת ויעדי האיום נשמרו בלי שינוי תפקידים.',
    ],
    'creators:421367': [
        'האם “couldn\'t find a wackier candidate” ו־“hard to beat for sheer wackiness” מבטאים אותה עוצמת ביקורת?',
        'המילה all נעלמת מהביטוי “topping it all off”; בדקו אם זה שינוי כמותי או שינוי בביטוי רטורי בלבד.',
        'האם היחס בין שלוש העמדות המיוחסות למועמדת והאירוניה סביב הציטוט נשמרים?',
    ],
    'creators:208496': [
        'האם “may have been the first time” ו־“Perhaps never before” משמרים את אותו ספק לגבי ראשוניות האירוע?',
        'בדקו שנשמרת הופעה משותפת של שני המשתתפים באותו מדיום, ולא טענה אחרת על הופעותיהם.',
    ],
    'creators:3fd01161cd76': [
        'המקור אומר “many farm stands and homes”; השכתוב מתאר “the familiar sight”. האם היקף התופעה נשמר?',
        'בדקו את הציטוט “man” והפיסוק שבתוכו, ואת כל רכיבי המטאפורה של יצירת איש קש/חבר קונגרס.',
        'האם עוצמת הסאטירה והייחוס לתורמים הפוליטיים נשמרים לאחר שינוי מבנה המתכון?',
    ],
    'creators:421811': [
        'האם “inescapable” מול “cannot be escaped” הוא אותו תוכן למרות שינוי בסמן השלילה?',
        'בדקו “the word and the idea” מול “both…”; הופעת both אינה בהכרח תוספת משמעות.',
        'המקור מחבר Napoleon Bonaparte ו־Julius Caesar ב־and, והשכתוב ב־or; האם הקשר והמסגור נשמרים?',
    ],
    'creators:213461': [
        'השוו “Almost daily” ל־“Nearly every day”: האם אותה תדירות מסויגת נשמרת?',
        'בדקו שהקביעה על foreign policy והטענה על תכנית המס עדיין מיוחסות באותו אופן ושעוצמת השבח נשמרת.',
        'אין כאן דגל פסילה ב־guards הקיימים; הבחירה נובעת מרמז כמתים תיאורי ואינה הכרעה שנוצר כשל.',
    ],
}


def flags(row):
    return set(filter(None, row['failed_guards'].split('|')))


def priority(row):
    failed = flags(row)
    tier = (0 if 'bidirectional_nli' in failed else
            1 if failed & {'framing_anchors', 'attribution'} else
            2 if 'certainty' in failed else
            3 if row['quantifier_surface_difference'] == 'True' else 4)
    return tier, -(row['quantifier_surface_difference'] == 'True'), -len(failed), row['ID']


def cell(text):
    """Escape table syntax only; rendered source characters remain unchanged."""
    return html.escape(text, quote=False).replace('|', '&#124;').replace('\n', '<br>')


def changes(original, rewrite):
    before, after = original.split(), rewrite.split()
    edits = []
    for tag, start, end, other_start, other_end in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag != 'equal':
            edits.append((' '.join(before[start:end]), ' '.join(after[other_start:other_end])))
    return edits


def build():
    verify()
    output = HERE / 'REVIEW_15_HE.md'
    manifest_path = HERE / 'SELECTION_MANIFEST.json'
    if output.exists() or manifest_path.exists():
        raise ValueError('Review packet exists; do not overwrite human answers')
    source = HERE.parent / 'QC_FAILURE_TRIAGE_150.csv'
    rows = [row for row in read(source) if row['method'] == 'Style']
    selected = sorted(rows, key=priority)[:15]
    canonical = {row['ID']: row for row in read(RUN / 'received_rewrites_75.csv')}
    assert len(selected) == len({row['ID'] for row in selected}) == 15
    assert set(FOCUS) == {row['ID'] for row in selected}
    lines = [
        '# חבילת סקירה אנושית ראשונה — 15 זוגות', '',
        'תאריך הכנה: 10.11.2026. נבחרו15 מתוך75 השכתובים החדשים, כולם train. זו חבילה **בסיוע QC, לא עיוורת**; אין בה הכרעות אדם או תוויות נרטיב מוצעות.', '',
        'העדיפות היא NLI, אחריו ייחוס/מסגור, ודאות ואז רמזי משטח בכמתים. שוברי שוויון: רמז כמתים, מספר דגלים, ID. זה מדגם מכוון לתחילת העבודה, לא מדגם להערכת שיעורי הצלחה. רמזי כמתים אינם guards חדשים.', '',
        '## איך למלא', '',
        '- קראו את שני הטקסטים במלואם. העריכו שימור ביחס למקור; אין צורך להסכים עם העמדה או לבדוק את אמת העובדות.',
        '- **Meaning Preserved:** Yes אם הטענות, העובדות, התפקידים, היחסים, הכמתים, הוודאות והייחוס נשמרו; No אם זוהה שינוי מהותי; Borderline אם קיים ספק שיש לפרט.',
        '- **Narrative Preserved:** Yes אם העמדה, המסגור, מי מואשם/משובח ועוצמתם נשמרו; No אם השתנו מהותית; Borderline אם לא ניתן להכריע. אין צורך לדעת Left/Right כדי לזהות שימור עמדה.',
        '- **Style Change Valid:** Yes אם יש שינוי ניכר באופן ההבעה; No אם הטקסט זהה או השינוי זניח; Borderline אם השינוי מוגבל או קשה להפרידו משינוי תוכן. שפטו בנפרד: שינוי סגנוני יכול להתקיים גם כשמשמעות נפגעה.',
        '- דגל אוטומטי ושאלת בדיקה אינם הוכחה לכשל. גם טקסט שעבר את ה־guards דורש שיפוט. אין לערוך את המקור או השכתוב.',
        '- ב־No או Borderline ציינו בהערות ביטוי מדויק והסבר. השאירו שדה ריק אם עדיין לא נבדק; אל תסמנו Yes כברירת מחדל.',
        '- טבלאות העריכה הן הבדלי רצף מילים אוטומטיים, לא מיפוי סמנטי או רשימת טענות. שינוי סדר עשוי להופיע כמחיקה והוספה. סימן ∅ מציין צד ריק.', '',
        '| פרטי סקירה | למילוי |', '|---|---|', '| מזהה סוקר/ת אדם | |', '| תאריך הסקירה בפועל | |', '| סיוע מכלי AI, אם היה | |', '',
        'הכרעות של LLM אינן אימות אנושי עצמאי. חבילה זו היא שלב עבודה ראשון; היא אינה קובעת קבלה לאימון או מחליפה את כלל ה־QC המלא וה־adjudication.', '',
        '## אינדקס', '', '| # | ID | סיבה לתעדוף — אות אוטומטי בלבד |', '|---|---|---|',
    ]
    for number, row in enumerate(selected, 1):
        reasons = row['failed_guards'].replace('|', ', ') or 'אין דגלי פסילה קיימים'
        if row['quantifier_surface_difference'] == 'True':
            reasons += '; רמז הבדל משטח בכמתים'
        lines.append(f"| {number} | {row['ID']} | {reasons} |")
    manifest = []
    for number, row in enumerate(selected, 1):
        assert row['Original'] == canonical[row['ID']]['Original']
        assert row['Rewrite'] == canonical[row['ID']]['ChatGPT_Style_Rewrite']
        lines += ['', f"## זוג {number:02d} — {row['ID']}", '',
                  '| Original | Style Rewrite |', '|---|---|',
                  f"| {cell(row['Original'])} | {cell(row['Rewrite'])} |", '',
                  '### מה השתנה בניסוח — הבדלים מילוליים', '',
                  '| קטע במקור | קטע בשכתוב |', '|---|---|']
        lines += [f'| {cell(before) if before else "∅"} | {cell(after) if after else "∅"} |'
                  for before, after in changes(row['Original'], row['Rewrite'])]
        lines += ['', '### פרטים לבדיקה אנושית — שאלות, לא הכרעות', '']
        lines += ['- ' + question for question in FOCUS[row['ID']]]
        lines += ['', '### הכרעת הסוקר/ת', '',
                  '| שדה | תשובה — Yes / No / Borderline |', '|---|---|',
                  '| Meaning Preserved | |', '| Narrative Preserved | |', '| Style Change Valid | |',
                  '| הערות וביטויים תומכים | |', '']
        manifest.append(dict(ID=row['ID'], source_sha256=text_sha(row['Original']), rewrite_sha256=text_sha(row['Rewrite']),
                             failed_guards=sorted(flags(row)), quantifier_surface_hint=row['quantifier_surface_difference'] == 'True'))
    lines += ['', '---', '', '## הוראות נפרדות לתיוג Left/Right', '',
              'הוראות מלאות וקישורים לטפסי המקור נמצאים ב־[LEFT_RIGHT_LABELING_GUIDE_HE.md](LEFT_RIGHT_LABELING_GUIDE_HE.md). התיוג נעשה על Original, לא על השכתוב ולא לפי דגלי השימור.', '']
    output.write_text('\n'.join(lines), encoding='utf-8')
    dump(manifest_path, dict(date='2026-11-10', scope='first15 selected from extension75 train only',
                            selection='NLI > attribution/framing > certainty > quantifier surface hint; ties: quantifier hint, failed-guard count, ID',
                            triage_source_sha256=sha(source), packet_sha256=sha(output), rows=manifest,
                            text_edited=False, human_decisions_filled=False, qc_assisted_not_blind=True))
    verify()
    print(json.dumps([row['ID'] for row in manifest], indent=2))


if __name__ == '__main__':
    build()

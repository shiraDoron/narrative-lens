"""Update Hebrew guide/report from imported External LLM Review counts only.

Inputs: summary.json and existing documents. Outputs: an explicitly attributed,
idempotent documentation section. No data labels, model code or review fields change.
Also called by report.py so later reporting preserves the imported review status.
"""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
STUDY=OUT.parent
MARKER='## External LLM Evaluation — עדכון 2026-11-01'


def build_section():
    """Render supplied counts and attributed examples without new semantic judgments."""
    summary=json.loads((OUT/'summary.json').read_text(encoding='utf8'))
    counts=summary['counts'];rows=[]
    labels={'machine_label_correct':'אישור הצעת הנרטיב','paraphrase_meaning_preserved':'Paraphrase — שימור משמעות',
        'normalized_meaning_preserved':'Normalized — שימור משמעות','paraphrase_style_change_valid':'Paraphrase — שינוי סגנון',
        'normalized_style_change_valid':'Normalized — שינוי סגנון'}
    for key,label in labels.items():
        c=counts[key];rows.append(f"| {label} | {c.get('Yes',0)} | {c.get('No',0)} | {c.get('Borderline',0)} |")
    return '\n'.join([MARKER,'',
        '**התקבלה הערכת ChatGPT חיצונית ל־30 דוגמאות מכותבי האימון בלבד.** הדירוגים יובאו כפי שנמסרו, ללא הכרעת תוכן חדשה. קובץ המקור נשמר בהעתק זהה בבתים. זו אינה Human Review, אינה human annotation ואינה human gold.','',
        '### הפרדה בין מקורות המידע','',
        '| מקור | מה התקבל | סטטוס |','|---|---|---|',
        '| בדיקות אוטומטיות קיימות | ציוני NLI/דמיון, ישויות, guards ומדדי סגנון; 114 טקסטים משותפים עברו את המסננים | נשארו כפי שהיו; מעבר אינו הוכחת שימור |',
        '| External LLM Review | דירוגים והערות של ChatGPT ל־30 דוגמאות | נשמרו בתיקייה נפרדת, ללא העברה לשדות אנושיים |',
        '| אימות אנושי אמיתי | הכרעת סוקר/ת אדם בתוויות ובשכתובים | עדיין ממתין; הייבוא לא השלים אף רשומה אנושית |','',
        '### תוצאות ההערכה החיצונית בלבד','',
        '| דירוג LLM | Yes | No | Borderline |','|---|---|---|',*rows,'',
        f"ה־LLM אישר 27 הצעות נרטיב וסימן {counts['llm_narrative_label'].get('Unclear',0)} טקסטים כ־Unclear. תוויות הניסוי לא הוחלפו בעקבות זאת.",
        'לפי הדירוגים החיצוניים, 19 נרמולים שמרו משמעות אך לא שינו סגנון באופן ממשי; 7 קיבלו Yes בשני הסעיפים. שני נרמולים קיבלו Yes לשינוי סגנון אך No לשימור משמעות.','',
        '### פערים מול הסינון ודוגמאות כפי שתוארו בידי ה־LLM','',
        '- creators:421024: ה־LLM העריך ששני השכתובים שומרים משמעות, למרות פסילת Paraphrase בבדיקת ציטוטים.',
        '- creators:423545: ה־LLM תיאר את פסילת NLI של Paraphrase כמחמירה למרות שימור התוכן, וציין ניסוח דקדוקי מסורבל.',
        '- creators:418904: ה־LLM הבחין בין שימור משמעות כללית לבין החלפת מילה בתוך ציטוט — פגיעה בנאמנות לציטוט שעדיין אסורה לפי הפרוטוקול.',
        '- creators:417181: לפי ה־LLM, שני השכתובים משנים certainty/attribution והפרפרזה מוסיפה תיאור שלא היה במקור.',
        '- creators:120669: ה־LLM סימן בנרמול החלפה שגויה של נושא נאומי חג ההודיה מאובמה לוושינגטון.',
        '- creators:459e183c1d0d: ה־LLM ציין השמטת ההסתייגות allegedly one-time; בפרפרזה ציין גם שינוי במעמד Berkeley ובהצגת הקצאת 90% מההכנסות.',
        '- creators:218236 ו־creators:418827: הפרפרזות סומנו Borderline בשל שינוי דק בייחוס/עמדה או הפיכת ניסוח רטורי לטענה קונקרטית.','',
        'הפערים אינם מתירים לבטל פסילות: חלקם משקפים הבדל בין משמעות כללית לבין דרישת השימור המחמירה. לא שונו ספים או החלטות קבלה.','',
        '### מסקנה ראשונית ומה עדיין לא ניתן להסיק','',
        '**לפי הבדיקה החיצונית, הבעיה אינה רק בסינון:** במקרים רבים Normalized שומר על המשמעות אבל כמעט לא משנה סגנון; כאשר השינוי הסגנוני משמעותי יותר יש לעיתים פגיעה בפרטים סמנטיים. זו אינדיקציה אבחונית מתוך הדירוגים שנמסרו, לא אמת אנושית מאומתת ולא אומדן על כל המאגר.',
        'המדגם נבחר במכוון בשלוש קבוצות מכותבי האימון. ה־LLM ראה שמות כותבים, הצעות נרטיב וציוני סינון; אין כאן בדיקה עיוורת. גרסת המודל, prompt ההערכה ותאריך ביצוע ההערכה לא סופקו. אין להסיק agreement בין בני אדם או עצמאות מהתיוגים הקודמים.',
        'אין תוצאת Macro-F1 חדשה, אין Author Identification חדש ואין הוכחה להסרת shortcut. לא הורץ אימון מחדש ולא שונו חלוקת הנתונים, test, תוויות אנושיות או קוד אימון. אימות אנושי אמיתי עדיין נדרש לפני מעבר בשער האימון; ה־External LLM Review אינו פותח אותו. אין כרגע הצדקה חדשה ל־LoRA/DoRA.','',
        '[הסיכום המלא וכל 30 הדירוגים](external_llm_review_20261101/EXTERNAL_LLM_REVIEW_SUMMARY_HE.md) · '
        '[קובץ המקור ללא שינוי](external_llm_review_20261101/LLM_EXTERNAL_REVIEW_30_20261101.csv) · '
        '[ספירות ניתנות לשחזור](external_llm_review_20261101/summary.json)',''])


def main():
    """Append/replace only the dedicated external-review section in two documents."""
    section=build_section()
    for name in ['EXPERIMENT_GUIDE_HE.md','FINAL_REPORT_HE.md']:
        path=STUDY/name;text=path.read_text(encoding='utf8')
        if MARKER in text:text=text[:text.index(MARKER)].rstrip()
        text=text.replace('## עדכון 2026-11-01 — השלב הבא: בדיקה חיצונית של 30 דוגמאות',
            '## עדכון 2026-11-01 — הכנת חבילת 30 דוגמאות לבדיקה חיצונית')
        text=text.replace('**השלב הבא הוא Human Review חיצוני של 30 הדוגמאות.** רק לאחר קבלת התיוגים ותיעוד זהות הבודק יהיה אפשר להחליט על שינוי השכתוב או על אימון מחדש.',
            '**בדיקת LLM חיצונית התקבלה ותועדה בנפרד להלן; אימות אנושי אמיתי עדיין ממתין.** ההערכה החיצונית מאפשרת דיון אבחוני, אך לא שינתה שכתובים, סינון או תוויות ולא פתחה את שער האימון.')
        path.write_text(text.rstrip()+'\n\n'+section,encoding='utf8')
    print('Updated guide and final report: External LLM Review is separate from human verification.')


if __name__=='__main__':main()

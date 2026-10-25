"""Record researcher-supplied L1 metadata without upgrading it to verified evidence."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
path=root/'artifacts/research_author_style_language/native_language_registry.json'
registry=json.loads(path.read_text(encoding='utf-8'))
updates={
    'khamenei_ir':('Persian','probable'),
    'ZelenskyyUa':('Russian','verified'),
    'BenShapiro':('English','probable'),
    'BernieSanders':('English','user_reported_unverified'),
    'MariaZakharova':('Russian','user_reported_unverified'),
    'CharlieKirk':('English','probable'),
    'HananyaNaftali':('Hebrew / English','user_reported_unverified'),
}
for author,(language,confidence) in updates.items():
    record=registry[author]
    record.setdefault('previous_source_search_status',record['status'])
    record['native_language']=language
    record['confidence_status']=confidence
    record['researcher_input']={'source':'User message in this research conversation',
        'external_source_supplied':False,
        'note':'User requested probable specifically for khamenei_ir, BenShapiro and CharlieKirk. No independent verification added.'}
    if confidence!='verified':record['status']=confidence
    if author=='HananyaNaftali':
        record['language_interpretation']='Unresolved: slash-separated researcher input; does not establish two native languages, their order of acquisition, or English as L1 rather than L2.'
path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

report_path=root/'docs/author_style_native_language_research_he.md'
report=report_path.read_text(encoding='utf-8')
if '### עדכון מידע שמסרה החוקרת' not in report:
    marker='### שפת אם: ממצאי המקורות'
    addition='''### עדכון מידע שמסרה החוקרת

בעקבות מידע שמסרה החוקרת נוספו שיוכי שפה כמשתנה עבודה, עם מקור ורמת ודאות נפרדים. הטבלה הבאה והטבלה המלאה מעודכנות; תיאור חיפוש המקורות בהמשך מתייחס לאימות החיצוני המקורי. לא צורפו מקורות חיצוניים חדשים ולא בוצע ניתוח קורלציה חדש בעקבות העדכון.

| Author | Native Language | Status | בסיס |
|---|---|---|---|
| khamenei_ir | Persian | probable | מידע שמסרה החוקרת; ללא מקור חיצוני מצורף |
| ZelenskyyUa | Russian | verified | המקור החיצוני הקיים במרשם; מידע החוקרת תואם לו |
| BenShapiro | English | probable | מידע שמסרה החוקרת; ללא מקור חיצוני מצורף |
| BernieSanders | English | user_reported_unverified | מידע שמסרה החוקרת; ללא מקור חיצוני מצורף |
| MariaZakharova | Russian | user_reported_unverified | מידע שמסרה החוקרת; ללא מקור חיצוני מצורף |
| CharlieKirk | English | probable | מידע שמסרה החוקרת; ללא מקור חיצוני מצורף |
| HananyaNaftali | Hebrew / English | user_reported_unverified | לא הוכרע אם שתיהן שפות אם או שאנגלית שפה נוספת |

`probable` הוא סטטוס ההערכה שביקשה החוקרת, ולא תוצאת אימות עצמאי. `user_reported_unverified` אינו דירוג הסתברות נמוך או גבוה יותר: הוא מציין שמקור המידע הוא החוקרת ושהטענה טרם אומתה. רשומות שאינן verified לא יהפכו אוטומטית לראיות מאומתות. עדיין יש רק אדם אחד עם מקור חיצוני מפורש שנבדק. אפשר להשתמש בשיוכים האחרים בעתיד בניתוח רגישות מסומן כהנחות, בנפרד מניתוח המבוסס על מקורות מאומתים.

'''
    report=report.replace(marker,addition+'### שפת אם: ממצאי חיפוש המקורות המקורי',1)
report_path.write_text(report,encoding='utf-8')

readme_path=root/'artifacts/research_author_style_language/README.md'
readme=readme_path.read_text(encoding='utf-8')
if '## Researcher-provided L1 update' not in readme:
    readme+='''\n## Researcher-provided L1 update

The registry and author tables now retain researcher-provided languages separately from external evidence. Confidence status: verified (existing explicit source), probable (researcher-requested for Khamenei, Shapiro and Kirk), user_reported_unverified (Sanders, Zakharova, Naftali), unknown (other accounts). Only verified counts as externally documented. Naftali's Hebrew / English remains unresolved and is not encoded as confirmed bilingual L1. Original search outcomes remain in the registry. No new correlation or classifier run was performed for this metadata update.
'''
readme_path.write_text(readme,encoding='utf-8')

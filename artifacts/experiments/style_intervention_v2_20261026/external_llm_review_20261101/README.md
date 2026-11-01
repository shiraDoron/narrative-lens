# External LLM Evaluation / LLM External Review

הקובץ הגיע מהמשתמשת כתוצר בדיקת ChatGPT נפרדת. אין כאן אימות אנושי או הכרעת LLM חדשה.

- `LLM_EXTERNAL_REVIEW_30_20261101.csv`: העתק מקור זהה בבתים, כולל שמות שדותיו המקוריים.
- `external_llm_review_joined.csv`: תוצאות עם קידומת `external_`, מחוברות ל־ID ולפלטי הסינון הקיימים. `human_verified=False` בכל רשומה; אין כתיבה לטבלת אימות אנושי.
- `summary.json`: ספירות מדויקות, חיתוכי שימור משמעות/סגנון ומגבלות מקור ההערכה.
- `automatic_vs_external_llm.csv`: פערי דירוג מול החלטות הסינון, ללא החלפת החלטות.
- `EXTERNAL_LLM_REVIEW_SUMMARY_HE.md`: סיכום קריא, דוגמאות מיוחסות להערכה וכל 30 הדירוגים.
- `import_audit.json`: hash מקור והעתק, התאמת 30 מזהים ל־train והוכחה שקובצי הנתונים המוגנים לא השתנו בזמן הייבוא.

שחזור מהשורש:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/external_llm_review_20261101/import_review.py
python artifacts/experiments/style_intervention_v2_20261026/external_llm_review_20261101/update_docs.py
```

סקריפט הייבוא קורא את קובץ המקור מתיקיית Downloads; אין להחליף את העותק המיובא בתוכן אחר. שינוי בקובץ המקור דורש גרסת ייבוא נפרדת. `update_docs.py` משנה מסמכים בלבד, ונקרא גם כאשר מפיקים מחדש את דוח הניסוי. אף סקריפט אינו מפעיל מודל או אימון. גרסת מודל ההערכה, prompt ותאריך ביצוע ההערכה לא נמסרו; זמן הייבוא מתועד בנפרד.

הדירוגים אינם נכנסים ל־human_review.csv, אינם מחליפים את תוויות הדאטה ואינם עוקפים סינון. יש להשלים אימות של סוקר/ת אדם בנפרד. המדגם מכוון, קטן, מכותבי האימון ואינו עיוור, ולכן הספירות מתארות את 30 הדוגמאות בלבד.

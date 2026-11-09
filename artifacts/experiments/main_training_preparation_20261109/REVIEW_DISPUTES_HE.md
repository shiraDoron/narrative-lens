# ביקורת איכות: מקור דירוגים ומחלוקות — 2026-11-09

המשתמש דיווח שמילא Human Validation עם ספירות 30 meaning Yes,30 stance Yes,28 style Yes/2 Borderline,30 drift No. בבדיקה בפועל של הרפו ותיקיית Downloads לא נמצא קובץ אדם מלא חדש; `HUMAN_VALIDATION_30.md/.csv` ריקים לאחר הפרדת Claude. אין להסיק מהעדר קובץ שהמשתמש לא ביצע קריאה; פשוט אין בידינו מקור שניתן לייבא ולייחס ברמת ID.

הקובץ המלא הזמין הוא `EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md`, המצהיר Claude ו־LLM-based. הוא תועתק ל־[CLAUDE_REVIEW_PER_ID_IMPORTED.csv](CLAUDE_REVIEW_PER_ID_IMPORTED.csv) עם דירוגים והערות, ללא שינוי. ספירות הדיווח האנושי נשמרו בנפרד ב־[HUMAN_REVIEW_IMPORT_STATUS.json](HUMAN_REVIEW_IMPORT_STATUS.json), ולא כמילוי human fields. אין ביכולתנו להשוות אדם מול LLM לפי ID לפני קבלת הקובץ המלא.

סקירת LLM קודמת קיימת רק במצטבר: meaning24Yes/6Borderline; certainty26Yes/2Borderline/2No; rhetorical intensity19Yes/10Borderline/1No; drift3Yes/11Borderline/16No. Claude09Nov נותן meaning30Yes/drift30No. זו אי־הסכמה בין סקירות, לא majority vote ולא gold. ללא ID ratings של הסקירה המוקדמת אי אפשר לבנות confusion/agreement, לזהות 16 “clean IDs”, או לחשב agreement של בני אדם.

| ID | evidence ממקור→ChatGPT | מחלוקת לשימור | פעולה בלי שינוי דירוג |
|---|---|---|---|
| 421951 | No one fights like→Few people fight like | כמת מוחלט הוחלש; Claude מכיר caveat ומקבל | לשאול סוקר אדם אם השינוי מהותי; לשמור את שני השיפוטים בנפרד |
| 0105f26ef9f1 | will make you→can make you | שינוי modal certainty/עוצמה | לדרוש נימוק, לא להסתפק בדמיון גבוה |
| 421024 | don't have to→not supposed to | צורך מול נורמה | לבדוק עמדה/עוצמה בהקשר |
| 421279 | doing everything he can…day and night→works day after day | השמטת emphasis על מאמץ מקסימלי | לבדוק rhetorical intensity, לא רק כיוון העמדה |
| 417181 | attribution לכתב אישום נשמר/הובהר | לשמור הבחנה allegation מול assertion | לא להעתיק לכאן certainty failure של v2/v3 |
| 120669 | Obama מפורש במקום his | antecedent הובהר | לא לייבא בטעות Obama/Washington reversal מגרסה אחרת |
| 423315 | No one had stormed→had not yet been stormed | active→passive, לא riots→protests | העמדה לא בהכרח השתנתה; הטעות ההיסטורית בהערה תוקנה |
| 421853,418904 | שינוי מצומצם/near copy | Style Borderline, לא drift | לשמור Borderline; לא להרחיב acceptance בדיעבד |

attribution ו־quote fidelity צריכים להיבדק גם בפרפרזות; אין דירוג אדם אוטומטי משום שהסוקר ציין meaning Yes. פרוטוקול QC ייבדק בידי אנשים בלי תוצאות המודל. כל הערה כאן היא audit של העוזר, לא Human Validation ולא LLM review חדש לכל 30.

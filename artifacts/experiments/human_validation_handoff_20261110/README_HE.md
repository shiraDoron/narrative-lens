# הפעולה הבאה: אימות אדם, ללא סקירת AI נוספת

החבילה מרכזת **148 תוויות מקור: 105 Train ו-43 Validation**, וכן **210 זוגות: 105 Style ו-105 Paraphrase**. כל IDs והטקסטים נשמרים; אין כאן Test. כל שדות ההכרעה וזהות הסוקר ריקים. אין להעביר את הטפסים למודל כדי למלא human.

## איך לעבוד

1. צרו עותק עבודה של [LABELS_148.csv](forms/LABELS_148.csv) ושל [PAIRS_210.csv](forms/PAIRS_210.csv), ופתחו בעורך CSV התומך ב-UTF-8. השאירו את העותקים הריקים המקוריים ללא שינוי.
2. לקריאה נוחה, השתמשו ב-[אינדקס Markdown](forms/INDEX_HE.md): חוברות של עד 15 רשומות, טקסטים מלאים וזוגות זה לצד זה. CSV הוא מקור ההזנה לכלי הבדיקה; אם בחרתם לרשום ב-Markdown, יש להעביר את התשובות ל-CSV לפי ID ו-variant לפני בדיקה. אין לייבא Markdown אוטומטית ולסכן שיוך שגוי.
3. ב-PAIRS התחילו ב-30 רשומות Style הראשונות, ואז המשיכו לכל יתר Style ו-Paraphrase. הקדימות אינה הכרעת איכות. לא מוצגים scores, פסקי AI או נימוקיהם. סדר מבוסס סיכון אינו עיוור לחלוטין; אין להניח מראש שהשכתוב שגוי.
4. בכל רשומה מלאו reviewer_type=human, מזהה סוקר אמיתי ותאריך YYYY-MM-DD. אל תרשמו ChatGPT/Claude כאדם. כשיש סיוע AI תעדו אותו ב-notes; אין להציגו כסוקר עצמאי.
5. אל תשנו ID, variant, split, טקסטים, hash או הצעה. שמרו כל קובץ מקור שהתקבל מהסוקר. לתיעוד מספר סוקרים, שמרו קובצי מקור נפרדים; אפשר לאחד שורות לבדיקה. כפילויות/מחלוקות ידווחו ולא יוכרעו אוטומטית. קובץ סופי מוכרע חייב להכיל שורה אחת לכל מפתח, עם זהות האדם המכריע ונימוק, תוך שמירת המקורות בנפרד.

## הכרעות בזוגות

| שדה | פירוש |
|---|---|
| meaning | Yes: כל הטענות המהותיות נשמרו; No: שינוי מהותי; Borderline: ספק שדורש הכרעה. |
| stance | האם העמדה והמסגור של המספר נשמרו? אין להסיק זאת מזהות הכותב. |
| style_change | האם יש שינוי סגנוני ניכר מעבר לתיקון מקומי? נדרש ל-Style; אופציונלי לפרפרזה בהתאם לפרוטוקול. |
| semantic_drift | Yes: יש שינוי משמעות; No: לא זוהה; Borderline: לא הוכרע. הכיוון הפוך ל-meaning. |
| notes | מה השתנה ולמה הכרעתם כך? נימוק נדרש לגבוליות ולדחייה. |

בדקו כמתים, שלילה, ודאות, מי מייחס טענה למי, תפקידים, זמן וסיבתיות, פרטים מספריים, ישויות, ציטוטים ועוצמה רטורית. הבדילו בין שינוי תחבירי לבין שינוי claim. אין לבדוק אם המקור נכון בעולם ואין לתקן אותו.

No אינו שורה חסרה: דחייה מנומקת ומוכרעת יכולה להיכנס למדיניות ה-fallback הסימטרית הקיימת. Borderline נשאר חסם עד הכרעה; אין למזג אותו ל-Yes. קבלת Style דורשת meaning=Yes, stance=Yes, style_change=Yes, semantic_drift=No; קבלת Paraphrase אינה דורשת style_change. הספים והמדיניות לא שונו.

## תוויות Left/Right

קראו [הנחיות המחלקות והמקרים העמומים](LABELING_GUIDE_HE.md). human_label הוא Left-wing / Right-wing / Unclear / Mixed / Other. proposed_label_correct הוא Yes / No / Borderline. ההצעה אינה gold. לכל תווית בינארית מתועדת נדרשת evidence_span מדויקת מהמקור. במקרה עמום אפשר להשאיר ראיה ריקה ולהסביר; הכלי יסמן את הרשומה כלא סגורה ולא יכפה תווית. שוני מההצעה מחייב הכרעת corpus נפרדת, לא relabel אוטומטי.

## בדיקה ומוכנות

משורש הרפו, לאחר מילוי עותקי העבודה:

```powershell
python artifacts/experiments/human_validation_handoff_20261110/handoff.py check --labels "C:/human/LABELS_148.csv" --pairs "C:/human/PAIRS_210.csv" --output "C:/human/check_01"
```

הכלי יפיק READINESS_HE.md, READINESS.json ו-ISSUES.csv כשיש בעיות. הוא מדווח על חוסרים, כפילויות, מחלוקות, Borderline, שינוי טקסט/hash, סתירות בין שדות, ראיות חסרות ומקור שאינו אדם. exit code 2 פירושו שטרם נפתח gate מדעי, ולא שהקבצים אבדו. כל דוח נכתב בתיקייה חדשה בלבד.

כאשר intake הושלם, יופקו גם human_train_labels.csv, human_validation_labels.csv ו-human_pair_reviews.csv, ללא שינוי תשובות. אלה עדיין אינם snapshot מאושר. לאחר הכרעת מחלוקות יש למלא **בעותק נפרד** את [חתימת ההקפאה הקיימת](../main_training_runtime_20261110/SIGNED_FREEZE_TEMPLATE.json), ולהריץ אותה בדיקה עם `--signed-freeze "C:/human/signed_freeze.json"`. רק הצלחת policy_inputs הקפוא תחזיר scientific_training_ready=true. הכלי אינו מאמת זהות אדם באופן עצמאי ואינו מעניק הרשאת אימון.

השלב הבא לאחר מכן הוא prepare-human ב-[CLI הקיים](../main_training_runtime_20261110/README_HE.md), עם שלושת הקבצים המיוצאים והחתימה. רק snapshot מאושר, סגירת דרישות הפרוטוקול והרשאת הרצה מאפשרים להתחיל. החבילה אינה מפעילה prepare-human, אימון או Test.

## שחזור

`python artifacts/experiments/human_validation_handoff_20261110/handoff.py build` יוצר חבילה רק כשהתיקייה forms אינה קיימת. אין למחוק טפסים שמולאו כדי לשחזר. בדיקות: `python -m unittest discover -s artifacts/experiments/human_validation_handoff_20261110 -p test_handoff.py`.

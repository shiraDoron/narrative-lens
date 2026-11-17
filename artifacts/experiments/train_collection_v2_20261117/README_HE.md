# מאגר מועמדי Train — חבילת האימות הפעילה

**348 מועמדים ייחודיים**, לאחר איסוף158 מאמרים חדשים וסינון18 מקורות בשל חששות
זליגה/ייחוס.122 קיבלו תיעדוף פוליטי גבוה לפי מדד לשוני בלבד; אין תוויות מוצעות
חדשות ואין תיוג אדם שהושלם.200 הוא יעד Train בלבד.

להתחלה: [הדוח המלא והמגבלות](REPORT_HE.md) · [תכנון האיסוף](COLLECTION_DESIGN_HE.md).

לסוקרים יש למסור רק:

- [מדריך התיוג](ANNOTATION_GUIDE_HE.md).
- לסוקר א׳: [REVIEWER_A_BLIND.csv](REVIEWER_A_BLIND.csv) וחוברות reviewer_A.
- לסוקר ב׳: [REVIEWER_B_BLIND.csv](REVIEWER_B_BLIND.csv) וחוברות reviewer_B.

כל סוקר ממלא עותק נפרד; אין להחליף תשובות לפני סיום. [טופס הכרעה](ADJUDICATION_TEMPLATE.csv)
מיועד לסוקר שלישי במקרה של אי־הסכמה. PRIVATE_REVIEW_KEY, CANDIDATES, PRIORITY
ודוחות הקרדיט מכילים מטא־נתונים ואינם נמסרים למתייג עצמאי לפני השלמת תשובותיו.
הטקסטים הם Original, ללא שכתוב. השוואות ישנות וטפסי119/97 נשמרים כהיסטוריה;
אין לספור את אותן דוגמאות פעמיים אם כבר התקבל תיוג מטופס אחר.

בדיקת עותקים מלאים, בלי עדכון קורפוס או אימון:

```powershell
python artifacts/experiments/train_collection_v2_20261117/review_intake.py --reviewer-a C:/reviews/reviewerA.csv --reviewer-b C:/reviews/reviewerB.csv --adjudication C:/reviews/adjudication.csv --output C:/reviews/intake_report01.json
```

הבודק דורש התאמת hashes לנתוני החבילה, IDs נכונים, reviewer_type=human, סוקרים
שונים, ראיות בטקסט וגילוי סיוע; ההכרעות הראשוניות נשמרות. כשיש אי־הסכמה נדרשת
הכרעה נפרדת עם זהות ותאריך. Unclear אינו מקור בינארי. כל התבניות הנוכחיות ריקות;
INITIAL_REVIEW_STATUS מתעד את מצב ההתחלה בלבד. אין להפוך אותו לדוח תיוג אדם.

חשוב:9 מה־105 ההיסטוריים חסומים מחבילת הנתונים החדשה —5 עקב חפיפת גוף מאמר
ו־4 עקב קרדיט משותף/אורח. קובציהם לא השתנו.96 הישנים בחבילה עדיין טעונים אימות,
כמו252 האחרים. ההנחה הישנה105+95 אינה אישור כשירות. אין לבחור200 לפני קבלת gold
ובירור מקור/כפילויות. גם אחרי200 יישארו QC של שכתובים ואישור פרוטוקול נפרדים.

לשחזור: raw_sources נשמר מקומית ומוחרג מ־Git, כמו מקורות האיסוף הישן. כל URL,
זמן הורדה, byline, גילוי מקור ו־hash נשמרים ב־receipts וב־FETCH_LOG; snapshots
נדרשים לביקורת טקסט מלאה. אין להריץ איסוף על תיקייה זו לאחר MANIFEST: המשך
איסוף יתבצע בגרסה חדשה. prepare.py מסרב לדרוס חבילה מוכנה. MANIFEST קושר קלטים
ופלטים ראשוניים; RESULT_HASHES קושר גם את הדוחות והחוברות הסופיים.

בדיקות:

```powershell
python -m unittest discover -s artifacts/experiments/train_collection_v2_20261117 -p test_collection.py -v
python -m ruff check artifacts/experiments/train_collection_v2_20261117
```

אין כאן אימון/הערכת Test. בדיקת ההחזקה הוגבלה ל־fingerprints וכפילויות בלבד,
ללא ביצועי מסווג או בחירת שכתובים. אין הוכחה להיעדר חפיפה סמנטית/אירועית מעבר
לכללים המוגדרים. פיתוח Minimal נשאר עצור והממצא השלילי נשמר בתיעוד המחקר.

# חבילת המשך — שכתוב ותיוג

להתחלה: [הדוח הקצר](REPORT_HE.md). התכנון: [DESIGN_HE.md](DESIGN_HE.md).
זהו פיתוח על Train בלבד; ללא אימון מרכזי, הערכת Test או שינוי תקציב/פרוטוקול.

לסוקרי התוויות יש למסור רק [המדריך](LABEL_GUIDE_HE.md),
[LABEL_97_BLIND.csv](LABEL_97_BLIND.csv) וחמש חוברות LABEL_BOOKLET לקריאה.
אין למסור מראש את LABEL_97_PRIVATE_KEY.csv או AI_LABEL_SCREEN.csv.
טופס45 זוגות השכתוב: [PILOT_HUMAN_BLIND.csv](PILOT_HUMAN_BLIND.csv);
המפתח PILOT_HUMAN_KEY.csv נפרד. הכפילויות בין גרסאות נשמרות לצורך ההשוואה
והתחשבות בתלות בין זוגות; אין45 מקורות בלתי תלויים. שדות האדם ריקים.

AI_SCREEN_NOTES.tsv מתעד97 הכרעות העוזר עם מובאות מדויקות ונימוקים;
compile_labels.py רק מחבר אותן לטקסטים ולסיכומים ואינו מייצר gold.
check_labels.py בודק שלמות ו־provenance מוצהר בלבד. אין לו נתיב עדכון קורפוס.
גם טופס שמולא לא הופך אוטומטית למקור מאושר; נדרשת הכרעה והקפאה נפרדות.

```powershell
python artifacts/experiments/minimal_followup_20261117/check_labels.py C:/path/completed_labels97.csv
python -m unittest discover -s artifacts/experiments/minimal_followup_20261117 -p test_followup.py -v
python -m ruff check artifacts/experiments/minimal_followup_20261117
```

prepare.py ו־compile_labels.py מסרבים לדרוס פלט קיים. screen.py מפעיל את validate
הישן בלבד, עם54 זוגות של9 מקורות Train ובלי שום קריאה ל־evaluate/probe/train.
המודלים נטענים offline בגרסאות הקודמות. validation_method.json מכיל פרוטוקול
היסטורי שהוחזר כמות שהוא מהמנגנון; אינו מחליף את DESIGN_HE של הסבב הנוכחי.
טפסי rewrite_human_review שנוצרו בידי המנגנון נשמרים לשחזור; אין צורך למלאם
בנוסף לטופס PILOT_HUMAN_BLIND המורחב.

MANIFEST.json קושר קלטים וגרסאות פלט שנוצרו לפני הסקר; SCREEN_BINDINGS קושר
את קוד הסקר. SURFACE_STYLE_SUMMARY קושר את66 המאפיינים ואת ה־scaling הקפוא
שנלמד בעבר על Train בלבד. RESULT_HASHES.json קושר את קבצי הגרסה הסופית.
קבצי progress זמניים אינם נכללים ב־Git. כל ההיסטוריה הקודמת נשמרת.

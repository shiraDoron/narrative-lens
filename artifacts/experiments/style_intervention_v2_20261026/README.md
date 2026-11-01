# Style intervention V2 — הוראות הפעלה

התחילו ב־[EXPERIMENT_GUIDE_HE.md](EXPERIMENT_GUIDE_HE.md). כל התוצרים החדשים נשמרים בתיקייה זו בלבד. תוצרי הניסוי הקודם נקראים בלבד.

## סדר הרצה מתיקיית הפרויקט

Python 3.11 עם חבילות הפרויקט הקיימות: torch, transformers, sentence-transformers, numpy, pandas, sklearn, matplotlib. בסביבה הנוכחית Python נמצא ב־`C:/Users/P0039126/.pyenv/pyenv-win/versions/3.11.9/python.exe`.

```powershell
python artifacts/experiments/style_intervention_v2_20261026/study.py --stage prepare
python artifacts/experiments/style_intervention_v2_20261026/study.py --stage generate
python artifacts/experiments/style_intervention_v2_20261026/study.py --stage validate
python artifacts/experiments/style_intervention_v2_20261026/study.py --stage package
python artifacts/experiments/style_intervention_v2_20261026/study.py --stage report
```

אפשר להריץ `--stage all` במקום הרצף. הוא נעצר במכוון לפני אימון על תוויות לא מאומתות.

1. `prepare`: מקפיא 218 מקורות, חלוקת הכותבים, הפרפרזה הקודמת, prompt, ספים ו־hashes.
2. `generate`: יוצר 218 גרסאות Normalized חדשות; שומר כל תוצאה מיד ומאפשר resume. הפלט הוא `generated_rewrites.jsonl`. llama-server מקומי בפורט 18093 מופעל בחלון מוסתר ונעצר בסיום; המשקלים וה־exe נקראים מהניסוי הקודם בלבד. כל הלוגים החדשים תחת runtime/ כאן.
3. `validate`: מריץ את כל הבדיקות הקודמות, ללא הקלה. שומר `rewrite_validation.csv`, סיכומי מעבר ופסילה ו־NLI resume cache. נדרש שכל 218 הנרמולים נוצרו.
4. `package`: יוצר `human_review.csv`, מסמך קריאה `HUMAN_REVIEW_HE.md`, תיוג עיוור אופציונלי `human_labels_blind.csv`, מדדי שינוי ו־`explicit_style_changes.csv`. הפעלה חוזרת משמרת שדות סימון אנושי.
5. `report`: יוצר מסמך מרכזי בעברית, דוח קצר, גרפים, STATUS ובדיקת תקינות תוצרי העבר.

## אימות אנושי — פעולה שאדם חייב לבצע

לממשק נוח יותר, הריצו `python artifacts/experiments/style_intervention_v2_20261026/render_review.py` אחרי package, ופתחו `HUMAN_REVIEW.html` בדפדפן. הוא מציג רשומה אחת בכל פעם, שומר סימונים מקומית, ומאפשר הורדת CSV. אין בו קריאות רשת או מילוי אוטומטי של תשובות. אחרי ההורדה החליפו את human_review.csv בתיקיית הניסוי בקובץ שהורדתם. יש לגבות לאורך העבודה; שמירה בדפדפן לבדה אינה מעדכנת קובץ בדיסק. `--stage all` ו־finish_automatic.py יוצרים את הטופס גם כן.

פתחו `human_review.csv` ב־Excel או עורך CSV. לכל שורה:

- רשמו `reviewer` אמיתי, `reviewed_at` בפורמט ISO ותווית `human_narrative`: `Left-wing`, `Right-wing` או `Unclear`.
- לכל אחת משתי הגרסאות סמנו `yes`, `no` או `unclear` בכל שדות השימור. שדה ריק פירושו לא נבדק.
- `claim_added` ו־`claim_omitted`: `no` פירושו שאין שינוי כזה. `yes` או `unclear` פוסלים את השכתוב.
- confidence המוצג הוא הצעת AI בסולם 1–3, לא הסתברות. אפשר לדחות את התווית המוצעת.
- `human_labels_blind.csv` מאפשר תיוג ללא הצעת AI. מפתח נפרד ב־`human_labels_key.csv`. לפני evaluate יש להזין את ההכרעה הסופית ב־human_review.csv. הערכה משולבת בסיוע הצעת AI אינה תיוג עיוור.

אין למלא אוטומטית שדות אנושיים. אין להציג מסנן NLI כאימות אנושי. לא נדרשים ציוני המודל לצורך סימון.

## אחרי שהאדם השלים את הסימון

```powershell
python artifacts/experiments/style_intervention_v2_20261026/study.py --stage evaluate
python artifacts/experiments/style_intervention_v2_20261026/study.py --stage report
```

`evaluate` בודק שלמות כל 218 הסימונים; נעצר ללא אימון אם חסר סימון. הוא מפעיל חיתוך של סינון אוטומטי ואנושי, משתמש בתוויות האנושיות, משמר את חלוקת הכותבים, מסיר כפילויות חוצות split ומאמן 3×3 תנאים בחמישה seeds. נשמרים `retraining_results.csv`, `metrics_summary.csv`, `narrative_predictions.csv`, checkpoints ו־training histories. זיהוי כותב מאומן מחדש לכל תנאי על embeddings ועל מאפיינים מפורשים. ניתוח subset משמעותי מופעל רק אם יש כיסוי מינימלי; אחרת `evaluation_status.json` מסביר מדוע לא רץ.

כל שינוי בתוויות/ספים/שכתובים אחרי הערכה דורש תיקייה חדשה; אין לדרוס תוצאות כדי לבחור את הטובות.

## מפת הקוד והבדיקות

- `study.py`: השלבים הראשיים, מדידת שינוי ושער האימות האנושי.
- `report.py`: המסמך בעברית, סיכומי מעבר, גרפים ובדיקת hashes לתוצרי העבר.
- `render_review.py`: טופס HTML מקומי ללא שירות חיצוני.
- `finish_automatic.py`: מסיים validate/package/report/audit אחרי שיצירת השכתובים שכבר הופעלה מסתיימת; אינו מאמן מודלים ואינו ממלא שדות אנושיים.
- `audit.py`: בדיקות תוצרים לשלב האוטומטי, כולל עצירת אימון לפני אימות. מפיקים `artifact_audit.json`; הצלחה כאן אינה אימות מחקרי.

בדיקות ממשק ללא דפדפן נשמרות ב־`review_ui_test.json`; ניסיון הבדיקה החזותית מתועד ב־`browser_qa_status.json`. אלה אינם תיוגים אנושיים. גרסאות מודלים, prompt, ספים וספירות נשמרים בקובצי JSON וב־audit trail.

## שחזור מאפס

שחזור זה מתחיל מהמאגר הקפוא הקודם, לא מאיסוף מחדש מהאינטרנט. נדרשים `verified_human_style_followup_20261026` בשלמותו (כולל runtime weights), קוד הפרויקט, המודל המקורי ומודלי Hugging Face שכבר נמצאים ב־cache. README הקודם מתעד הורדת המשקלים וה־runtime לפי revision/hash. אין צורך ב־API חיצוני.

להרצה עצמאית נקייה העתיקו **רק** את כל קובצי ה־Python בתיקייה זו, README.md ו־.gitignore לתיקיית אחות חדשה תחת artifacts/experiments, והריצו את השלבים. התיקייה הקודמת הקפואה עדיין נדרשת כקלט. אל תעתיקו תוצרים/קבצי resume לריצה חדשה. לרפרודוקציה נומרית של שלב הערכה יש להשתמש באותם שכתובים מוקפאים ובאותו human_review.csv; הרצת LLM מחדש על חומרה אחרת אינה מבטיחה זהות ביטים. גרסאות חבילות, runtime hashes, prompts ו־input hashes נשמרים ב־environment.json וב־audit_trail.jsonl.

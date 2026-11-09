# חבילת השלמת נתונים — 2026-11-09

**עדכון QC — 10.11.2026:** [הדוח המלא](runs/extension_v1_run01/QC_REPORT_HE.md) ו־[תוצאות לפי ID](runs/extension_v1_run01/QC_COMPARISON_BY_ID_75.csv) מוכנים. כל75 השכתובים וכל75 הפרפרזות התואמות נבדקו באותם guards וספים. Style: שימור42/75, substantial71/75, שניהם39/75, exact copies0. Paraphrase: שימור43/75, substantial23/75, שניהם6/75, exact copies12. אלה תוצאות אוטומטיות בלבד; אין הכרעות אנושיות או אימון. לפי הצהרת המשתמשת, כל75 נוצרו ב־GPT-6 ב־9.11.2026; [תוספת metadata](runs/extension_v1_run01/GENERATION_METADATA_SUPPLEMENT_20261110.json) משלימה זאת בלי לשנות receipts. פרמטרים וגרסת מודל מדויקת אינם ידועים. דיווחי ההמתנה ל־QC ולשם המודל בהמשך הם היסטוריים.

לשחזור QC והשוואה ראו פקודות בדוח. בדיקת עקביות: `python artifacts/experiments/data_completion_20261109/verify_qc_results.py --run extension_v1_run01`. קובצי הניתוח והדגלים אינם חלק מהחבילה העיוורת לאדם. טפסים ריקים נוספים שה־validator מפיק אוטומטית אינם הגרסה למסירה; יש להשתמש בחבילת HUMAN_PAIR_REVIEW_NEW75 הקיימת.

**המצב העדכני: כל חמשת ה־batches התקבלו, 75/75 IDs צפויים וייחודיים.** נשמרו raw ו־receipts ללא עריכת שכתובים. [הקובץ המאוחד](runs/extension_v1_run01/received_rewrites_75.csv) ו־[חבילת אימות אנושי מלאה ל־75](runs/extension_v1_run01/HUMAN_PAIR_REVIEW_NEW75.md) מוכנים. אפשר למלא במקום Markdown את [ה־CSV המקביל](runs/extension_v1_run01/HUMAN_PAIR_REVIEW_NEW75.csv), לא את שניהם. הסוקר מקבל רק זוגות ושדות ריקים, ללא ציונים או תוויות.

קליטת run01 השתמשה ב־metadata template עם ערכי מודל/מועד null: זהו רישום מפורש של מידע חסר, לא metadata שהתקבל מהמשתמש ולא הוכחה לפרוטוקול היצירה בפועל. receipt מסמן `provenance_complete=false`. יש לשמור השלמת metadata בעתיד בנפרד, בלי לדרוס receipt מקורי. בוצע QC dry-run לבדיקת binding וקוד קפוא בלבד; **טרם הורצו guards סמנטיים או style metrics**, ולא התקבלו הכרעות אנושיות. אין אישור אימון. עדכוני הקליטה החלקיים בהמשך הם היסטוריים.

**מצב קליטה:** Batch 1 התקבל: [15 פלטים](received_batches/batch_01/BATCH_01_OUTPUT.csv), לצד ההדבקה המקורית ו־receipt באותה תיקייה. ה־IDs והסדר תואמים; אין כפילויות או טקסטים ריקים. הוסרה רק מעטפת Markdown. לא הורצו semantic QC או Human Validation. מודל ותאריך יצירה לא סופקו; batches 2–5 עדיין חסרים. קליטה חלקית אינה אישור ל־75 או לאימון.

לשחזור חילוץ הדבקה בלבד: `python artifacts/experiments/data_completion_20261109/import_pasted_batch.py --source <pasted-text.txt> --batch 1`. אין דריסה של batch קיים. לאחר קבלת כל החמישה משתמשים בקובצי `BATCH_*_OUTPUT.csv` כ־`--sources` בפקודת הקליטה המלאה שלהלן.

## מה להעביר ל־ChatGPT

**מצב עדכני לאחר Batch 4:** [15 פלטי Batch 4](received_batches/batch_04/BATCH_04_OUTPUT.csv) נקלטו עם התאמה מלאה ל־IDs ולסדר, ללא כפילויות או פלטים ריקים. raw ו־receipt נשמרו בנפרד, ללא עריכת השכתובים. סך הכול60 מתוך75; חסרים Batch 5 ופרטי היצירה. לא בוצעו semantic QC או אימות אנושי.

**מצב עדכני לאחר Batch 3:** [15 פלטי Batch 3](received_batches/batch_03/BATCH_03_OUTPUT.csv) נקלטו עם התאמה מלאה ל־IDs ולסדר, ללא כפילויות או טקסטים ריקים. המקור נשמר בנפרד ללא עריכה. סך הכול45 מתוך75; חסרים batches4–5 ופרטי היצירה. טרם בוצעו semantic QC או אימות אנושי.

**עדכון קליטה:** גם Batch 2 התקבל: [15 פלטים](received_batches/batch_02/BATCH_02_OUTPUT.csv), עם raw ו־receipt נפרדים. כל15 ה־IDs תואמים בסדר וללא פלטים ריקים. סך הכול נקלטו30 מתוך75; חסרים batches3–5. לא בוצעו בדיקות שימור משמעות או אימות אנושי, ופרטי המודל ומועד היצירה עדיין לא סופקו.

לפתוח שיחה חדשה לכל batch ולהשתמש **באותו מודל גלוי ובאותו prompt**:

1. [STYLE_REWRITE_PROMPT_V1.txt](STYLE_REWRITE_PROMPT_V1.txt) — הוראות קבועות. זהו prompt חדש לגרסת המשך, לא הפרומפט המקורי שאינו מתועד.
2. אחד מקובצי [chatgpt_batches](chatgpt_batches/): `BATCH_01_15.csv` עד `BATCH_05_15.csv`. חמישה batches, בכל אחד 15 מקורות; לא לצרף את כל75 בכל שיחה בנוסף ל־batch.
3. לבקש פלט CSV בלבד עם `id,chatgpt_style_rewrite`, ולשמור כל תשובה בקובץ נפרד. [תבנית פלט](STYLE_REWRITE_OUTPUT_TEMPLATE_75.csv) מתארת את הסכימה לכל75; היא אינה תשובה שנוצרה.

אפשר להשתמש ב־[STYLE_REWRITE_INPUT_75.csv](STYLE_REWRITE_INPUT_75.csv) כקובץ המקורות המלא, אבל החלוקה לחמישה מפחיתה סיכון לקטיעת תשובות. אין לשלוח את `PRIVATE_SPLIT_AND_LABEL_KEY_75.csv`, הערכות, שמות כותבים, תוצאות guards או מסווג.

לפני batch1 יש לתעד ב־[GENERATION_METADATA_TEMPLATE.json](GENERATION_METADATA_TEMPLATE.json) את interface, visible_model_name ומועד. להמשיך באותה בחירת מודל בכל חמש השיחות; אם השתנתה, לתעד ולסמן cohort נפרד. exact_model_revision ופרמטרים לא גלויים ב־UI נשארים null עם הסבר, לא ערכי ברירת מחדל מומצאים. ב־API לתעד את הפרמטרים והגרסה שנשלחו בפועל. לשמור raw replies ו־finish_reason אם זמין. [מניפסט קפוא](GENERATION_PROTOCOL.json) מכיל hashes של prompt ובאצ׳ים.

לא נוצרו כאן שכתובים. ה־30 הקיימים נשארים בדיוק כפי שהתקבלו. extension_v1 הוא הבדל מתועד: כעת יש prompt גלוי, התערבות מבנית מפורשת וכללים מדויקים לשימור כמתים/מודליות/ציטוטים. אין הבטחה שהוא שקול או עדיף על הפרוטוקול המקורי; אין לערוך את הפלטים או לבחור best-of לפי מודל.

## מה דורש אדם

- [NARRATIVE_LABEL_VALIDATION_105.md](NARRATIVE_LABEL_VALIDATION_105.md), או [ה־CSV](NARRATIVE_LABEL_VALIDATION_105.csv): כל105 Originals, תווית מוצעת והגדרות. למלא אחד מהם בלבד. ההצעה אינה gold; יש אפשרויות Unclear/Mixed/Other.
- קובץ האימות המלא שכבר מולא עבור legacy30: לשמור אותו כ־CSV/Markdown ולייבא עם הסוקר והתאריך, לפי ההוראות להלן. לא צריך למלא שוב אם קיים קובץ תקף. אם אין עותק זמין, [HUMAN_PAIR_REVIEW_LEGACY30.md](HUMAN_PAIR_REVIEW_LEGACY30.md)/[CSV](HUMAN_PAIR_REVIEW_LEGACY30.csv) הן תבניות ריקות של אותם זוגות.
- [HUMAN_PAIR_REVIEW_NEW75_TEMPLATE.md](HUMAN_PAIR_REVIEW_NEW75_TEMPLATE.md)/[CSV](HUMAN_PAIR_REVIEW_NEW75_TEMPLATE.csv): **עדיין לא למילוי** — Rewrite ריק ומסומן pending. אחרי קליטת התשובות תיווצר חבילה מלאה בשם `runs/<run>/HUMAN_PAIR_REVIEW_NEW75.md/.csv`, והיא הקובץ שיש למסור לאדם.
- פרפרזות105 ו־validation source labels43 עדיין דורשים QC/gold לפני ניסוי A–E; הקבצים הקיימים ב־main_training_preparation נשמרים. הבקשה הנוכחית אינה הופכת אותם למאומתים.

## ייבוא האימות שכבר מולא

לא נמצא ברפו או בקבצי Downloads הרלוונטיים `HUMAN_VALIDATION_30_FILLED.csv`; התבניות שעל הדיסק ריקות. קובץ מלא של Claude קיים בנפרד, והוא **אינו** מיובא כאדם. לשוניות IDE יכולות להציג קובץ שטרם נשמר; יש לשמור את קובץ התשובות לפני הפקודה.

```powershell
python artifacts/experiments/data_completion_20261109/import_review.py --source "C:/path/to/completed.csv" --kind pairs30 --reviewer-type human --reviewer-id "reviewer01" --review-date 2026-11-09 --name human30_reviewer01
```

התאריך צריך להיות תאריך הסקירה בפועל, לא העתקת הדוגמה אם שונה. המקור חייב לכלול ID, Original, ChatGPT_Style_Rewrite וחמשת שדות human כפי שבתבנית. תמיכה גם ב־Markdown של החבילה. מזהה/תאריך/סוג סוקר חובה; יש לתעד assistance באמצעות `--assistance-used`. ייבוא דורש את כל30 ה־IDs ובדיקת התאמת טקסטים, ערכים וכפילויות. raw file נשמר byte-for-byte בתיקיית `human_imports/<name>` עם receipt ו־hash; אין דריסה של היסטוריה או שינוי דירוגים.

ל־LLM משתמשים ב־`--reviewer-type llm`; הוא נשמר ב־`llm_imports`. מקור המצהיר במפורש Claude/AI יידחה אם ינסו לייחסו לאדם. סוג סוקר שמספק המשתמש מתועד כ־declaration; התוכנה אינה מוכיחה מי קרא בפועל. Notes ו־Borderline נשמרים; סתירות מסומנות, לא מתוקנות. עבור labels105 משתמשים ב־`--kind labels105`. עבור75 משתמשים ב־`--kind pairs75 --run <run>` לאחר קליטת פלטים.

## קליטת השכתובים ו־QC

```powershell
python artifacts/experiments/data_completion_20261109/receive_rewrites.py --sources "C:/path/batch1.csv" "C:/path/batch2.csv" "C:/path/batch3.csv" "C:/path/batch4.csv" "C:/path/batch5.csv" --metadata "C:/path/generation_metadata.json" --name extension_v1_run01
python artifacts/experiments/data_completion_20261109/automatic_qc.py --run extension_v1_run01 --dry-run
python artifacts/experiments/data_completion_20261109/automatic_qc.py --run extension_v1_run01
python artifacts/experiments/data_completion_20261109/compile_candidates.py --run extension_v1_run01
```

קליטה בודקת את כל75 IDs, טקסטים לא ריקים, כפילויות, אי־חפיפה עם legacy30 ו־prompt hash; שומרת את המקור ויוצרת חבילת אדם עיוורת. `automatic_qc` משתמש **באותו קוד/similarity/NLI/guards/metrics/scaling**, עם sink מבודד בתיקיית run ו־offline models. אין classifier inference/אימון, אין שינויים בספים ואין כתיבה לתוצאות הקודמות. ה־dry-run בודק wiring/hash ואינו טוען מודלים. הרצה מלאה מחייבת את המשאבים המקומיים הקיימים; אין הורדת מודל חלופי.

`compile_candidates` מחבר 30 קיימים ו־75 נקלטים ל־105 מקורות ולחמש זרועות טיוטה חדשות ב־`runs/<run>/candidate_105`, כולל configs וסדרי batches בתקציב שנקבע. הוא אינו משנה את snapshot ההכנה הישן, ואינו מאשר אימון: proposed labels, human QC ו־mixed-protocol provenance נשארים גלויים וממתינים לאישור. אין ערבוב עם test ואין החלפת legacy30.

[QC_RULES_HE.md](QC_RULES_HE.md) מקבע כלל קבלה לפני ביצועי Narrative Classifier. Auto pass אינו אישור אדם, ואין Human Validation כש־ChatGPT/Claude ממלאים את טופס הסקירה. הקליטה אינה נותנת אישור אוטומטי לאימון או לשימוש ב־test.

## שחזור החבילה

```powershell
python artifacts/experiments/data_completion_20261109/bundle.py
python -m unittest discover -s artifacts/experiments/data_completion_20261109 -p test_completion.py -v
```

יצירת החבילה משתמשת ב־stdlib בלבד ובמקורות קיימים. ה־source hashes מגינים על 30 השכתובים, התבניות, splits, validator ו־scaling. לא לשנות prompt תחת אותו protocol version לאחר תחילת batch. זו חבילת השלמה, לא שינוי בתכנון A–E ולא ניסוי סופי.

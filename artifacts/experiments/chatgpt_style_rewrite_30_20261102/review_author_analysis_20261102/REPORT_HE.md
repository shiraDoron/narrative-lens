# External review, human package and Author-ID diagnostic

תאריך 2026-11-02. יובאו רק ספירות review שסיפק המשתמש בשיחה. אין קובץ הכרעות לפי ID, שם/גרסת סוקר או prompt review; עצמאות הביקורת מדווחת על ידי המשתמש ולא נבדקה מהיסטוריית בקשות. לא נערך review חדש כאן.

| field | Yes | Borderline | No | N/A |
| --- | --- | --- | --- | --- |
| meaning_preserved | 24 | 6 | 0 | 0 |
| narrative_stance_preserved | 28 | 2 | 0 | 0 |
| attribution_preserved | 28 | 2 | 0 | 0 |
| certainty_preserved | 26 | 2 | 2 | 0 |
| participant_roles_preserved | 29 | 1 | 0 | 0 |
| event_characterization_preserved | 22 | 8 | 0 | 0 |
| rhetorical_intensity_preserved | 19 | 10 | 1 | 0 |
| quote_fidelity | 11 | 0 | 0 | 19 |
| style_change_valid | 24 | 6 | 0 | 0 |
| semantic_drift | 3 | 11 | 16 | 0 |

quote_fidelity: 11/11 Yes בין המקרים הרלוונטיים; 19 N/A. clean according to External LLM Review: 16/30 לפי semantic_drift=No בלבד. אין לקרוא להם human-validated; אין גם דרך לזהות את ה־IDs האלה או לחשב חפיפות בין שדות מהספירות בלבד. 6 Meaning Borderline ו־11 Drift Borderline נשארים נפרדים, ואינם בהכרח אותן רשומות.

## השוואת reviews

| Method | Auto_preservation | External_LLM_meaning_Yes | External_LLM_style_Yes | Clean_no_drift |
| --- | --- | --- | --- | --- |
| v2 | 6 | 10 | 30 | 10 |
| v3 | 9 | 5 | 27 | 5 |
| ChatGPT | 22 | 24 | 24 | 16 |

הספירות v2/v3 נלקחו מה־reviews הקיימים; Clean no-drift הוא אותו semantic_drift=No, לא כלל קבלה משולב. אין השוואה זוגית של שינוי ratings, בדיקת agreement או discrepancy מול guards ל־ChatGPT ללא הכרעות לפי ID. ההבדלים בין סוקרים/contexts אינם נשלטים, ולכן זו השוואה תיאורית ולא הוכחת עדיפות.

## Human Validation

[HUMAN_VALIDATION_30.md](HUMAN_VALIDATION_30.md) ו־[CSV](HUMAN_VALIDATION_30.csv) כוללים רק ID, Original, ChatGPT Style Rewrite וחמשת השדות הריקים המבוקשים. אין guards, גרסאות קודמות, scores, review או מחבר. כל 30 הזוגות נכללו. אין הכרעות אנושיות עדיין; Human Validation = Pending. פרטי הסוקר/ת ותאריך אפשר לתעד בנפרד. לא שונו שדות review קיימים.

כלל acceptance אפשרי לעתיד: Human meaning=Yes AND Human stance=Yes AND Human style=Yes, החל על כל 30. לא הוחל כעת, ולא נבחרו רק 16 מקרי no-drift.

## Author-ID — all 30 TRAIN pairs

| Author-ID evaluation | Accuracy mean | Macro-F1 mean | Accuracy seed SD | Macro-F1 seed SD |
| --- | --- | --- | --- | --- |
| Original | 0.2333 | 0.1964 | 0.0471 | 0.0487 |
| Rewrite | 0.2200 | 0.1867 | 0.0558 | 0.0339 |
| Original_fit_Rewrite_dev | 0.2800 | 0.2129 | 0.0380 | 0.0268 |

66 מאפייני סגנון קיימים + StandardScaler + LogisticRegression, ללא search/tuning. בכל seed שתי חלוקות stratified; כל זוג נשאר באותו צד. בגרסה הראשית אותו algorithm/hyperparameters אך fit נפרד לכל representation. הבדיקה הנוספת משתמשת בדיוק באותו fitted Original classifier. scaling מאומן רק בתוך fold.

זהו closed-set Author-ID על כותבים המופיעים ב־fit וב־dev, לא unseen-author evaluation ולא test המחקרי. תשעה כותבים, 2–4 דוגמאות לכותב; כל דוגמה מנובאת פעם אחת לכל seed (150 תחזיות לכל representation), לא 150 טקסטים עצמאיים. SD בין seeds אינו confidence interval. Majority accuracy: 0.1333; uniform chance: 0.1111.

שינוי Rewrite−Original במסלול matched: accuracy -1.33pp; Macro-F1 -0.97pp. הממוצע נמוך מעט יותר, אבל הירידה אינה יציבה: accuracy ירד רק ב־2/5 seeds. במסלול עם מסווג Original קבוע הוא דווקא עלה ל־28.0%. אין כרגע ראיה מספקת לירידה ברורה ב־author signal; אין לבחור seed או method שמייצר את הכיוון הרצוי.

| seed | accuracy delta Rewrite−Original | Macro-F1 delta |
| --- | --- | --- |
| 7 | +6.67pp | +0.0586 |
| 42 | -10.00pp | -0.0746 |
| 123 | +3.33pp | +0.0405 |
| 2026 | +3.33pp | -0.0049 |
| 31415 | -10.00pp | -0.0682 |

ירידה רק ב־Original-fit→Rewrite-dev עשויה להעיד על domain shift, גם אם מסווג שמאומן מחדש על rewrites עדיין מזהה כותבים. המדגם זעיר ואבחוני, ויש ערבוב אפשרי של תוכן, אורך, פרסום ונרטיב גם במאפייני style. אין כאן הסקת causal effect או שיפור narrative generalization.

[Protocol](author_id_protocol.json), [per-seed metrics](author_id_seed_metrics.csv), [predictions](author_id_predictions.csv), [fold IDs](author_id_fold_assignments.csv). Confusion matrices pooled across the same five seeds (rows=true, columns=predicted): [Original](confusion_Original.csv), [Rewrite](confusion_Rewrite.csv), [Original-fit→Rewrite-dev](confusion_Original_fit_Rewrite_dev.csv).

## שאלת המחקר והעצירה

החידוש אינו בהכרח Text Style Transfer חדש. השאלה היא האם Narrative Classifier משתמש ב־author style כ־shortcut, והאם הפחתת author-specific style תוך שמירת narrative משפרת generalization ל־unseen authors. ChatGPT rewrite הוא intervention candidate, לא contribution מוכחת בפני עצמו.

לא שונו rewrite prompt, guards, thresholds, filtering או חלוקת המחקר. אומנו רק מסווגי Author-ID זמניים בתוך folds של train; לא אומן Narrative Classifier, לא נשמרו weights ולא בוצעו test evaluation, LoRA או External LLM Review חדש. עוצרים לקבלת תיוג אנושי אמיתי.

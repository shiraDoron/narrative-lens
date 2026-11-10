# Trainer ל־A–E — תשתית מוכנה, ההרצה המדעית חסומה

10.11.2026. הקוד תומך בחמש הזרועות ובאותו פרוטוקול קפוא. בוצעה הרצה טכנית אמיתית על train בלבד. לא בוצע ניסוי A–E מדעי או test evaluation. העוזר הוא ChatGPT/Codex; סקירות AI אינן תוויות אדם.

## מה עובד

- טעינת105 Original/Paraphrase/Style, אותם IDs והצעות תווית, והפרדת9/4/6 כותבים. לא נמצאה חפיפה מדויקת של מקור/מאמר בין splits או של גרסת train עם validation Original. אין זו הוכחה שאין זליגה סמנטית/אירועים.
- יצירת snapshot מדעי רק אחרי תוויות אדם105 train +43 validation, QC אדם210 זוגות וחתימת freeze. Source labels שונים מן ההצעות עוצרים לבירור corpus; אינם משתנים בשקט.
- אותו production MiniLM קפוא מן המשקולות הקיימות, ראש חדש384→128→7, ReLU ו־dropout0.3, Adam lr0.001, batch16, seeds7/42/123/2026/31415.
- לכל105 מקורות: A–C עם105 שורות, D–E עם210;140 עדכונים ו־2240 דוגמאות מעובדות בכל זרוע/seed. אין CLI לשינוי hyperparameters או הפעלת test.
- אותה אתחלת ראש לכל זרוע באותו seed, schedules דטרמיניסטיים, forward/backward בראש בלבד, שמירת הראש וה־optimizer וטעינתם מחדש.
- Validation: אותם43 Originals עם gold. **לפי הפרוטוקול נבחר checkpoint בסוף התקציב הקבוע**, ולא ה־best validation. הדרישה לאותו validation מתקיימת בלי לשנות זאת. אין early stopping או בחירת שכתוב לפי score.
- Macro-F1 על Left/Right מתוך argmax על7, accuracy, per-class, inactive-output rate, confusion, per-author, mean/SD across seeds ו־C−B/D−E נקודתיים על validation. אין p-value/CI או test result מהמסלול הזה; ניתוח author-cluster הסופי נפרד וטעון הרשאה בעתיד.

## מה הורץ בפועל

[דוח smoke קריא](SMOKE_REPORT_HE.md) · [מצב המוכנות הנוכחי](TRAINER_READINESS.json).

[תוצאות smoke מובנות](smoke_runtime/SMOKE_RESULT.json):4 מקורות train שנבחרו בסדר ID קבוע,12 טקסטים ייחודיים, seed42, שני עדכונים בכל A–E. היעדים היו **סינתטיים לסירוגין5/6**, ללא שימוש בהצעות המכונה כ־gold. בכל זרוע32 דוגמאות מעובדות, gradients בראש, encoder קפוא ולוגיטים זהים לאחר reload. לא חושבו accuracy/F1 ולא נקרא validation/test ב־smoke. תוצאותיו אינן תוצאות מחקריות.

[Token audit](TOKEN_AUDIT_SUMMARY.json):315 גרסאות train ו־43 validation Originals נבדקו בטוקנייזר בלבד, ללא תחזיות. אותו vocab כמו ב־encoder ב־smoke, limit256, מקסימום151 tokens,0 truncations. [תקציב tokens לטיוטות25 הריצות](DRAFT_TOKEN_BUDGET_25.csv) מראה ששוויון דוגמאות אינו שוויון tokens/FLOPs. לאחר QC אנושי/fallback התקציב בפועל מתועד שוב בזמן האימון.

[דוח איכות](QUALITY_REPORT_HE.md):41 עברו את כל בדיקות ה־AI/האוטומציה הזמינות,57 גבוליים/איכות לא פתורה ו־7 בעלי חשש סמנטי מהותי לפי AI. **אף אחד אינו human-validated או accepted לאימון מכוח הדוח.** ה־grouping הוא דיווח בלבד; הוא אינו בשער הקבלה של ה־Trainer. ספי ה־QC לא שונו והפרפרזות עדיין דורשות QC אנושי משלהן.

## איך משלבים תוויות והכרעות אדם

1. לקבל את קובצי המקור המלאים עם reviewer_type=human, מזהה ותאריך. לתוויות, להשתמש ב־[import_review.py](../data_completion_20261109/import_review.py) ב־labels105/labels43 לקבלת reviews_by_id.csv עם hashes; לא להזין מקור AI כ־human. ל־pair QC יש [intake210](../research_completion_20261110/PAIRED_QC_INTAKE_210.csv) עם source/rewrite hashes, meaning/stance/style_change/semantic_drift/notes.
2. לשמור דירוגים מקוריים, להסדיר Borderline/מחלוקות בנפרד ולתעד החלטת שימוש. אין המרה אוטומטית ל־Yes. יש למלא את [SIGNED_FREEZE_TEMPLATE.json](SIGNED_FREEZE_TEMPLATE.json) בעותק נפרד רק לאחר סגירת gold/QC, provenance ופרוטוקול. unknown generation parameters נשארים unknown; חתימה אינה ממציאה אותם.
3. ליצור snapshot בלתי־ניתן־לדריסה באמצעות הפקודה למטה. `qc_contract.py` הקיים קובע fallback סימטרי ל־Original בשתי הגרסאות כשאחת אינה מתקבלת. נשמרים כל105 מקורות בניתוח הראשי ו־secondary common-accepted בנפרד; secondary שאיבד class/ריבוי כותבים נחסם.

```powershell
python artifacts/experiments/main_training_runtime_20261110/cli.py prepare-human --train-labels "C:/human/train105/reviews_by_id.csv" --validation-labels "C:/human/val43/reviews_by_id.csv" --pair-reviews "C:/human/completed_pair_qc210.csv" --signed-freeze "C:/human/signed_freeze.json" --name human_freeze_v1
```

**הפקודה הבאה מיועדת לעתיד בלבד, לאחר השלמת התנאים והרשאת הרצה; היא לא הופעלה:**

```powershell
python artifacts/experiments/main_training_runtime_20261110/cli.py train --approved-snapshot artifacts/experiments/main_training_runtime_20261110/approved/human_freeze_v1 --run-name primary_v1
```

כל25 הריצות מופעלות מאותו snapshot; הקוד בודק שוב hashes, התאמה לטקסטים הקנוניים, דירוגי אדם ו־freeze לפני טעינת מודל. אין auto-approve מטבלת איכות AI או מתוצאות validation. אין כרגע snapshot מאושר אמיתי. checkpoint כולל רק ראש ו־optimizer והפניה ב־hash ל־encoder; לא משכפלים משקולות encoder לכל זרוע.

כאשר קובצי reviews_by_id מגיעים מייבוא מתועד, נשמרים גם IMPORT_MANIFEST וקובצי received הזמינים לידם, לרבות תיעוד סיוע. manifest שמצהיר LLM נחסם גם אם מישהו שינה עמודת reviewer_type ב־CSV. פרטי אדם הם הצהרת provenance שנבדקת טכנית, לא אימות זהות עצמאי בידי התוכנה.

## שחזור הבדיקות הטכניות

```powershell
python artifacts/experiments/main_training_runtime_20261110/cli.py source-audit
python -m unittest discover -s artifacts/experiments/main_training_runtime_20261110 -p test_runtime.py -q
python -m pytest -q
python -m ruff check artifacts/experiments/main_training_runtime_20261110
```

לשחזור smoke בתיקייה חדשה בלי דריסת התוצאה הקיימת:

```powershell
python artifacts/experiments/main_training_runtime_20261110/smoke.py --output-dir artifacts/experiments/main_training_runtime_20261110/smoke_repeat_02
```

נדרשים משקולות production וקובצי MiniLM המקומיים הקיימים, PyTorch, sentence-transformers, transformers וה־dependencies הקיימים של הקוד. אין download אוטומטי או שינוי סביבת הפרויקט. נתוני הגרסאות/hashes נשמרו בתוצאת ה־smoke וב־FROZEN_BINDINGS.json. weights, caches ו־logs אינם ב־Git; trace וסיכום טכניים כן. לאחר שחזור Git ללא checkpoint מקומי, בדיקת טעינת checkpoint מסומנת skip עד ליצירתו ב־smoke; בהרצה הנוכחית היא עברה בפועל.

`quality_report.py` ו־`audit_tokens.py` משחזרים את דוחות האיכות והטוקנים. הראשון אינו נותן הרשאת אימון; השני משתמש ב־tokenizer revision הקיים ומשווה vocabulary ל־smoke. ראו [תוצאות בדיקות ומגבלות ארכיון](TEST_RESULTS_HE.md).

## מה עדיין חוסם התחלת אימון

חסרים105 labels אנושיים ל־train,43 ל־validation,210 pair QC והכרעות במחלוקות, וכן freeze מתועד של השימוש ב־30+75 protocol cohorts ופרטי provenance הלא ידועים. דרישות אלה נשארו ללא שינוי. אחרי קבלתם הקוד יכול לבנות את policy וה־snapshot; אין צורך להמציא gold או לשכתב שוב טקסטים כדי לבדוק שה־Trainer עובד.

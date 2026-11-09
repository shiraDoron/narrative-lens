# השלמת תשתית ואימות — 10.11.2026

**אין צורך לייצר שכתובים נוספים.** לכל105 מקורות train יש Original, Style Rewrite ו־Paraphrase. הבדיקות האוטומטיות ל־75 החדשים הסתיימו; האימון עדיין חסום באימות אנושי ובחיבור trainer לפרוטוקול הקיים. אין כאן תוצאת A–E חדשה.

## מה למסור לסוקר/ת

1. [Style — כל105 הזוגות, ללא דגלים](HUMAN_STYLE_REVIEW_105.md), או [CSV למילוי](HUMAN_STYLE_REVIEW_105.csv). אם כבר קיים אימות אדם מלא של30 הישנים, יש לייבא אותו עם provenance ולא למלא שוב סתם. החבילה של75 מהשלב הקודם נשמרה; לא חייבים למלא גם אותה וגם את full105.
2. [פרפרזות — כל105 הזוגות](HUMAN_PARAPHRASE_REVIEW_105.md). תוצאות QC אנושי לשתי הגרסאות אפשר לרכז ב־[PAIRED_QC_INTAKE_210.csv](PAIRED_QC_INTAKE_210.csv): שורה אחת לכל ID ו־variant, עם reviewer_type, reviewer_id ותאריך. לא למלא החלטות באמצעות ChatGPT/Claude ולקרוא להן אדם.
3. [אימות תוויות train105](NARRATIVE_LABEL_VALIDATION_105.md) או [CSV](NARRATIVE_LABEL_VALIDATION_105.csv); וכן [אימות תוויות validation43](NARRATIVE_LABEL_VALIDATION_43_VALIDATION.md) או [CSV](NARRATIVE_LABEL_VALIDATION_43_VALIDATION.csv). ההגדרות כלולות; התוויות המוצעות אינן gold. Unclear/Mixed/Other הם תשובות תקפות לסקירה, אך מחייבים החלטת corpus מפורשת לפני אימון, ולא relabel אוטומטי.

לשמור כל סוקר בגרסה נפרדת עם תאריך; Borderline נשאר Borderline ודורש נימוק. מחלוקת מוכרעת בנפרד בלי דריסת ratings. עדיף שני סוקרים עצמאיים ככל שניתן, לפי הפרוטוקול. אדם+LLM אינם שני בני אדם לצורך agreement.

[Style105 בסיוע QC](HUMAN_STYLE_REVIEW_105_QC_ASSISTED.md) מסמן ליד כל זוג את דגלי הסיכון האוטומטיים, **בלי ציון כאילו היה הכרעת אדם**. הוא אינו עיוור. עדיף למסור קודם את החבילה העצמאית; אין לחשב agreement כאילו שתי הסקירות עיוורות אם נחשפו לדגלים. שני הקבצים מציגים אותם טקסטים ללא עריכה.

## תוצאות וניתוח

- [QC וניתוח סיכונים](QC_FAILURE_ANALYSIS_HE.md): Style42/75 preservation,71/75 substantial,39/75 both; Paraphrase43/75,23/75,6/75. אלה signals, לא אימות משמעות.
- [Original / Style / Paraphrase — כל75 לקריאה](COMPARISON_75_READABLE.md).
- [מיון סיכונים לפי ID ושיטה](QC_FAILURE_TRIAGE_150.csv), כולל דוגמאות עריכה ורמזי כמתים. רמזי הכמתים תיאוריים בלבד; לא guard חדש ולא כלל קבלה.
- [מוכנות והחסמים](READINESS_HE.md), [תוצאות audit מובנות](READINESS.json), [תקציבי25 ההרצות המתוכננות](TRAINING_BUDGET_AUDIT.csv).
- [מיפוי/hash105, כולל מידע פרטי על כותב ותווית מוצעת](INPUT_BINDINGS_105.csv) — אינו חלק מחבילת הסוקר.

Style מתקבל לפי הכלל הקיים: human meaning=Yes, stance=Yes, style=Yes, drift=No. Paraphrase: meaning=Yes, stance=Yes, drift=No. יש לסקור את כולם, לא רק auto failures. אין קבלה לפי ביצועי המסווג. אותו shared-ID symmetric fallback וניתוח secondary accepted-only בפרוטוקול המקורי נשמרים.

## ייבוא ושחזור

מה־repo root, Python3.11.9; החבילה החדשה משתמשת ב־stdlib בלבד:

```powershell
python artifacts/experiments/data_completion_20261109/verify_qc_results.py --run extension_v1_run01
python artifacts/experiments/research_completion_20261110/audit_readiness.py
python -m unittest discover -s artifacts/experiments/main_training_preparation_20261109 -p test_preparation.py -v
python -m unittest discover -s artifacts/experiments/data_completion_20261109 -p test_completion.py -v
python -m unittest discover -s artifacts/experiments/research_completion_20261110 -p test_research_completion.py -v
```

שער המוכנות מחזיר exit2 בכוונה כל עוד חסרים תנאים; אין לו מסלול לאימון. ה־QC עצמו ניתן לשחזור בפקודות [הדוח הקודם](../data_completion_20261109/runs/extension_v1_run01/QC_REPORT_HE.md), עם מודלי semantic/NER/NLI המקומיים ואותן revisions. אין צורך לשוב ולהריץ מודלים רק כדי לקרוא או לבדוק את התוצרים.

לאחר מילוי אדם, דוגמת ייבוא לכל105 Style:

```powershell
python artifacts/experiments/data_completion_20261109/import_review.py --source "C:/path/completed105.csv" --kind pairs105 --run extension_v1_run01 --reviewer-type human --reviewer-id "actual-reviewer" --review-date 2026-11-10 --name human_style105_r1
```

לתוויות משתמשים ב־`--kind labels105` או `--kind labels43`. יש למסור את תאריך הסקירה האמיתי ולתעד assistance. ייבוא שומר raw, hashes ודירוגים ללא שינוי, מסרב ל־IDs/טקסטים לא תואמים ומפריד human_imports מ־llm_imports. דוגמת הפקודה אינה תיעוד של סקירה שבוצעה. ה־210 CSV הוא intake לחוזה QC הקיים; טרם יובא או אושר ואינו מאשר אימון בעצמו.

בניית candidate105: `python artifacts/experiments/data_completion_20261109/compile_candidates.py --run extension_v1_run01` — כבר בוצעה; snapshot קיים אינו נדרס. [טיוטות105](../data_completion_20261109/runs/extension_v1_run01/candidate_105/STATUS.json) מתעדות training_ready=false. טפסים נוצרים באמצעות `prepare_review_packages.py`; הוא מסרב לדרוס חבילה קיימת. לשחזור מלא בתיקייה חדשה יש להתחיל מה־Git snapshot/עותק עבודה נפרד, לא למחוק טפסים עם תשובות.

## שינויים טכניים וגבולות

[סקירת קוד מפורטת](INFRASTRUCTURE_REVIEW_HE.md) · [תיעוד עריכת התזה](THESIS_EDIT_AUDIT_HE.md) · [תוצאות50 הבדיקות](TEST_RESULTS.md) · [סיכום והמשך](HANDOFF_SUMMARY_HE.md).

תוקן דגל style_present שנשאר False ל־75 שכבר נקלטו. התיקון משנה metadata של זמינות בלבד, לא טקסטים, labels, acceptance או ספים. נוספו חיבורי יבוא pairs105/labels43 ובדיקות שמסרבות לטפסים ריקים או לא תואמים. `evaluation_contract.py` הוא עזר טהור עם fixtures לבדיקת שני labels פעילים, שבע הסתברויות ויישור A–E; אינו trainer ולא הורץ על תחזיות אמיתיות.

ה־historical trainer/evaluate אינם drop-in: הם עשויים לבחור checkpoint לפי validation, לסנן differently ולהפעיל test. אין להפעילם באמצעות `--stage all`. קוד המדדים החדש לא משנה את הפרוטוקול: argmax על כל7, Macro-F1 על Left/Right ו־inactive-output rate. bootstrap/uncertainty ו־trainer bridge מאושרים עדיין חסרים לפני הרצה מדעית.

Provenance: ל־75 GPT-6 /9.11.2026 לפי המשתמשת, פרומפט המשך קבוע. ל־30 הישנים מודל/פרומפט מדויקים אינם ידועים. decoding/finish_reason אינם ידועים בשני cohorts; אין להמציאם. אין מערבבים External LLM Review עם Human Validation או את המשימה הנוכחית עם שבעת הנרטיבים ההיסטוריים.

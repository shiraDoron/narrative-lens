# מוכנות לאימון — 10.11.2026

**מצב: נתונים זמינים, אימון מדעי חסום.** אין אימון או הערכת test.

## הושלם ונבדק

- 105 IDs ייחודיים; Original, Paraphrase ו־Style זמינים לכולם. 30 שכתובים ישנים ו־75 חדשים נשמרים כ־cohorts נפרדים.
- הצעות התוויות נשארו55 Left /50 Right; הן אינן gold.
- כותבים נפרדים:9 train /4 validation /6 test. אין overlap או exact text/article-hash collision בין splits. אין בכך הבטחה שאין דמיון סמנטי או חפיפת אירועים.
- טיוטות A–C:105 שורות; D–E:210 שורות. אותם מקורות ותוויות, בלי סינון נפרד לזרוע.
- 25 configs ו־25 schedules שוחזרו בדיוק. בכל זרוע/seed:140 עדכונים, batch16,2240 דוגמאות מעובדות; D/E זהים במיפוי source/index.
- אותם encoder/head/optimizer/seeds/config rules; זה אינו אימות של initialization או checkpoint בהתנהגות trainer שטרם אושר.
- מספר המילים המעובדות נמדד ב־TRAINING_BUDGET_AUDIT.csv; תקציב דוגמאות שווה אינו FLOPs/tokens זהים.
- QC מלא ל־75 החדשים ולפרפרזותיהם קיים; legacy30 נשמר ללא rerun. חבילות אדם ריקות לכל105 ולתוויות train/validation.

## חסמי אימון

1. 105 train source labels require attributable human validation; proposals are not gold
2. 43 validation source labels require attributable human validation
3. 105 Style pair judgments and105 Paraphrase pair judgments are missing; auto pass does not substitute
4. Resolve disagreements/Borderline and apply the preregistered shared-ID symmetric fallback before training approval
5. Legacy30 generator model/prompt remain unknown; document the mixed-protocol interpretation before scientific training
6. No approved end-to-end A-E trainer/evaluation bridge yet; historical evaluate()/train() must not be used as a drop-in

## זהירות בקוד ההיסטורי

הפקודה check_readiness.py בחבילת main_training_preparation היא snapshot היסטורי של common30 וממשיכה לדווח75 missing. אין להריץ prepare.py כדי לדרוס טפסים; הדוח הנוכחי מחובר ל־candidate105 ומתעד missing=0 בלי לעקוף את שערי האדם.

ה־trainer ההיסטורי בוחר checkpoint לפי validation ופונקציות evaluate ההיסטוריות כוללות test וסינון automatic-all-arms. הן אינן מימוש של תקציב A–E הנוכחי וכלל ה־human symmetric fallback. אין להפעיל אותן כאילו היו הניסוי החדש. הקוד והפרוטוקול ההיסטוריים נשארו ללא שינוי.

המשימה הנוכחית היא Left/Right ברמת טקסט. ראש7 נשמר מטעמי תאימות בלבד; Macro-F1 ראשי צריך להשתמש בשתי התוויות הפעילות, ולדווח inactive-output rate. אין לבצע renormalization שקט לשתיים או להציג זאת כרפליקציה של שבעת הנרטיבים ההיסטוריים.

## שער ובדיקות

`python artifacts/experiments/research_completion_20261110/audit_readiness.py` מחזיר exit2 כל עוד החסמים קיימים. זהו fail-closed צפוי, לא כשל QC ולא הרשאה לאימון. אין לו מסלול שמפעיל trainer.

חוסר provenance ב־legacy30 ואי־חשיפת decoding ב־UI מתועדים בנפרד. ל־75 החדשים GPT-6 /9.11.2026 לפי המשתמשת; exact revision/parameters/finish_reason אינם ידועים. אין להמציא אותם או להרחיב את ההצהרה ל־30 הישנים.

ה־test ההיסטורי כבר שימש בעבר. החלטה אם נדרש holdout חדש היא החלטה מחקרית עתידית עם המנחה; לא פותחים test כדי להחליט כעת.

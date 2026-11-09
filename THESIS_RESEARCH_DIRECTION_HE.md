# הכיוון המרכזי של התזה

החלטת מיקוד: 2026-11-09. זהו מסמך הכיוון המרכזי; [CURRENT_STATE](CURRENT_STATE.md) הוא דף המצב המשתנה, ו־[EXPERIMENTS](EXPERIMENTS.md) שומר את ההיסטוריה. אין במסמך הרשאה להעריך test או לייצר שכתובים בפרוטוקול חסר.

## שאלת המחקר

**Can meaning-preserving author-style interventions improve political narrative classification generalization to unseen authors?**

השערת עבודה: מאפייני סגנון מחבר עלולים להתלכד עם תוויות באימון; גיוון סגנוני המשמר את הנרטיב עשוי לשפר הכללה. זו השערה, לא ממצא. השיפור האפשרי והסברו באמצעות shortcut הם שני estimands שונים.

התרומה הנבחנת היא **אמפירית ומתודולוגית**: בדיקה מבוקרת של augmentation ושל גבולות הפרשנות שלו בנרטיב פוליטי. אין כוונה להמציא Style Transfer חדש. Style Pooling, CATO, Shortcut Maze ו־SCPN כבר מדגימים חלקים מהרציונל ומהפרוטוקול הכללי; ראו [הסקירה המעמיקה](RELATED_WORK_DEEP_REVIEW_HE.md) ו[מטריצת ההשוואה](RELATED_WORK_COMPARISON.md).

## הבעיה והגדרת המשימה

ביצוע טוב כשהכותב מוכר עלול להסתמך על נושא, תקופה, עמדה או סגנון הקשורים אליו. גם אם Author-ID מצליח, אין בכך ראיה שמסווג הנרטיב משתמש באותו מידע. מצד שני, certainty, quantifiers, תפקיד המשתתפים ועוצמה רטורית עשויים להיות מידע נרטיבי לגיטימי שאסור לנטרל.

הפרויקט ההיסטורי משתמש בשבע קטגוריות רחבות ובתוויות חשבון/ערוץ. הקורפוס הנוכחי של מאמרי דעה בוחן **Left-wing/Right-wing ברמת הטקסט**, כרגע כהצעות מכונה. זו operationalization מוגבלת של political narrative, קרובה לאידאולוגיה/stance, ולא טקסונומיית SemEval עשירה. אין לאחד את שתי המשימות או לפרש binary F1 כהצלחה בשבעה נרטיבים. נדרשות הנחיות תיוג ואימות מקור בידי אדם.

## מה כבר בוצע ומה נמצא

| קו ניסוי | ממצא קיים | מה אין להסיק |
|---|---|---|
| Random לעומת LOAO | ביצועי held-out account חלשים; חלק מהפער המדווח הישן משווה F1 ל־recall | אין effect size סיבתי נקי של style |
| entity masking, swaps ו־Group-DRO | תוצאות מעורבות או שליליות; לא נסגר פער ההכללה באופן יציב | לא נשלל כל תפקיד של ישויות או כל שיטת robustness |
| נרמול surface היסטורי | ירידה בחלק מ־author probes; mean fresh-author recall .3895→.3255 | ירידת author predictability אינה הוכחת הסרת shortcut מזיק |
| follow-up עם מחבר מזוהה | Normalized F1 .5437 מול Paraphrase .5903 באותו מדגם מסונן | לא הודגם יתרון normalization על פרפרזה |
| ניסויי v2/v3/ChatGPT | יותר שינוי סגנון עשוי להתלוות לסיכון משמעות; auto pass אינו gold | generator טוב יותר אינו מסקנה על הכללה |
| Author-ID מורחב | char TF-IDF .4842 accuracy; ירידת התערבות תלויה בייצוג | אין הסרה יציבה של זהות כותב או מנגנון המסווג הנרטיבי |
| frozen sensitivity על 30 train | ChatGPT ו־Paraphrase: כל אחד 1/30 flips, ב־IDs שונים | המקורות נראו באימון; לא unseen-author effect ולא proof of style dependence |
| few-shot | תועלת עם labeled target-author support; k10 mean recall .6565 | לא zero-shot ולא השפעת style rewrite |

כל המספרים וההסתייגויות ב[Evidence Matrix](EVIDENCE_MATRIX_HE.md) וב[פיילוט הקפוא](STYLE_SENSITIVITY_PILOT_HE.md). אין צורך למחוק תוצאות שליליות; הן חלק ממחקר אמפירי תקף.

## הנתונים הזמינים ושערי איכות

- 429 מקורות ייחודיים מ־19 כותבים; 202 מתשעה כותבי train זמינים לדיאגנוסטיקת מחבר.
- 105 מקורות train בעלי הצעת Left/Right; עוד 43 validation ו־70 test בתת־המשימה. הכותבים נפרדים: 9/4/6.
- 30 מקורות משותפים לשלוש הזרועות, כל תשעת כותבי train מיוצגים; קיימות פרפרזות לכל 105. חסרים 75 Style Rewrites.
- אין כרגע תוויות נרטיב מקור אנושיות מאומתות בקורפוס זה. חבילת האדם ל־30 על הדיסק ריקה; הספירות 30/30 ו־28/2 מופיעות בסקירת Claude הנפרדת. ההצהרה שנמסר אימות אדם נשמרה כ־user-reported summary, אך לא הומרה ל־30 הכרעות לפי ID.
- פרומפט ChatGPT המקורי, גרסת המודל והפרמטרים אינם זמינים. אין לשחזרם בדמיון או להחליף generator בשקט.

[Audit וטיוטות הנתונים](artifacts/experiments/main_training_preparation_20261109/REPRODUCTION.md). לא נערך אימון פיתוח חדש, כי שערי ה־gold/QC/provenance חסרים. התשתית מוכנה להכנת ניסוי; הניסוי המדעי אינו מוכן להרצה.

## הניסוי המרכזי

חמש זרועות באותם source IDs ותוויות: A Original, B Paraphrase, C Style Rewrite, D Original+Style, E Original+Paraphrase. ל־A–C אותו N, ל־D–E אותו 2N. אותו encoder, ראש חדש מאותה ארכיטקטורה, optimizer/seeds ותקציב עדכונים קבוע. יעד ההערכה הראשי הוא **Original של כותבים שלא נראו באימון**, ללא שכתוב test.

שני contrasts עיקריים: C−B ו־D−E ב־Macro-F1; השוואות ל־A מדווחות בנפרד. D−A לבדו עשוי להיות אפקט augmentation/כמות. [הפרוטוקול המלא](MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md) כולל תקציב, QC, validation, uncertainty ומניעת leakage.

## פירוש תוצאות

- **חיובית:** יתרון על פרפרזה בתקציב זהה, עם framing מאומת ו־coverage ראוי, תומך בתועלת ההתערבות במערך הזה. מנגנון author-style עדיין דורש evidence נפרד.
- **שלילית עם CI צר והתערבות תקפה:** אינה תומכת בתועלת מעשית בתנאים שנבדקו; אינה שוללת כל generator/משימה.
- **לא מובהקת/CI רחב:** חוסר דיוק, לא הוכחת שקילות ולא כישלון כולל של השערת style.
- **התערבות חלשה או drift:** אי אפשר לבחון נקי את ההשערה; כשל manipulation אינו תשובה על המנגנון.
- **רק D>A אך D≈E:** עדות אפשרית לתועלת augmentation כללי, לא יתרון סגנוני ספציפי.

## איומים מרכזיים על התוקף

תוויות מכונה/חשבון, גבול לא חד בין style ל־framing, שינויים בכמתים ובוודאות, selection לפי QC, תשעה כותבי train ושישה test בלבד, קטעים קצרים, topic/time confounding, seed dependence ו־generator provenance חסר. ה־holdout ההיסטורי כבר נבחן; ניסוי confirmatory חדש עשוי לדרוש כותבים חדשים באמת. אסור להשתמש בו לבחירת prompt, סף או שיטה.

## סדר העבודה הבא

1. לקבל קובץ הכרעות אנושיות מלא עם IDs, הערות, זהות/מועד סוקר ולהשלים source-label gold.
2. להכריע במחלוקות meaning/quantifiers/certainty בלי לשנות בדיעבד את דירוגי האדם המקוריים.
3. לשחזר provenance יצירה; אם אינו זמין, להגדיר generator version חדש במפורש לפני batch, בלי לטעון שכפול הפרוטוקול הקיים.
4. ליצור ולבדוק את 75 השכתובים רק לאחר סגירת החוסר; QC גם לפרפרזות כבקרה.
5. לקבע cohort, תקציב וסטטיסטיקה לפני אימון A–E. לפתח על train/validation בלבד.
6. להריץ הערכת unseen-author סופית רק לאחר freeze ואישור ניסוי נפרד; בלי fine-tuning על test.

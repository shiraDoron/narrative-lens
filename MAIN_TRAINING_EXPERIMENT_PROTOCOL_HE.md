# פרוטוקול הניסוי המרכזי — A–E

גרסה 1, נכתב 2026-11-09 לפני אימון A–E. **מצב: prepared / blocked, לא בוצע אימון.** התוצאות ההיסטוריות והפיילוט הקפוא כבר ידועות; אין לכנות פרוטוקול זה preregistration של ניסויים שכבר בוצעו. הוא קובע כללים להרצה עתידית בלבד.

## מטרה ואומדנים

האם meaning-preserving author-style intervention משפר הכללה פוליטית לכותבים חדשים מעבר לפרפרזה? Outcome ראשי: Macro-F1 על **Original בלבד** של כותבים מחוץ לאימון. C−B בוחן החלפת ייצוג סגנונית מול פרפרזה; D−E בוחן augmentation סגנוני מול augmentation רגיל בגודל זהה. זה אינו אומדן causal של “הסרת style shortcut”.

המשימה הזמינה היא Left/Right כתווית טקסט אידאולוגית גסה, לא איחוד עם יתר חמש הקטגוריות. ראש 384→128→7 קיים בארכיטקטורת הפרויקט; labels פעילים 5/6 בסדר הקיים. אין remapping שקט או הצגת score בינארי כהערכה מלאה בשבע קטגוריות. תחזית מחוץ לשתי הקטגוריות נספרת כשגיאה, ושיעורה מדווח.

## נתונים ונכונות התוויות

| pool | N מקורות | כותבים | Left / Right | שימוש |
|---|---:|---:|---|---|
| train raw | 202 | 9 | לא כולם eligible | audit/Author-ID, לא כולם Narrative gold |
| train eligible | 105 | 9 | 55 / 50 | יעד האימון, מותנה באימות |
| train common Original/P/Style | 30 | 9 | 14 / 16 | תשתית draft, לא gold ניסוי |
| validation eligible | 43 | 4 | 22 / 21 | Original בלבד, לאחר gold |
| test eligible | 70 | 6 | 37 / 33 | קפוא; לא נפתח להרצה זו |

אותן assignments קיימות נשמרות; אין split search או שינוי labels. שכפול מקור/מאמר וגרסאותיו נשארים באותה קבוצה. נבדקו hash collisions בין splits ולא נמצאו; audit near-duplicates הקודם כיסה train202 בלבד. העדר collision אינו שולל paraphrase/event leakage. בקרת topic/time מתועדת; אין להציג אותה כבידוד סיבתי מלא.

[ספירות class/author מלאות](artifacts/experiments/main_training_preparation_20261109/AUTHOR_CLASS_COUNTS.csv): ב־train105 יש לפחות חמישה מקורות לכותב (Marc Dion), וב־common30 יש כותבים עם שני זוגות בלבד. Left ו־Right מיוצגים בחמישה כותבי train כל אחד, עם חפיפה של Froma Harrop בשני ה־classes; אין “חמישה ועוד חמישה” כותבים נפרדים. זה מספיק לבניית pilot טכני, לא להבטחת כוח סטטיסטי או benchmark מאוזן. אם ה־secondary accepted intersection מאבד class או משאיר אותו בכותב יחיד, אין להציגו כמבחן הכללה יציב; יש לדווח attrition ולהימנע מהערכת יתר.

כרגע source human labels=0 ו־pair human judgments=0 בקבצים הזמינים. המשתמש דיווח ספירות סיכום; אין קובץ מלא חדש שניתן לייחס לאדם. סקירת Claude יובאה לפי ID בנפרד, כולל notes. לא מסיקים דירוגי אדם מהספירות ולא משנים human fields. נדרש reviewer_id/date/type והכרעה עצמאית; הערות מסייעות של AI אינן אדם שני לצורך agreement.

## חמש זרועות ובקרת תקציב

| תנאי | גרסאות לכל source ID | דוגמאות בטיוטת30 | דוגמאות ביעד105 |
|---|---|---:|---:|
| A | Original | 30 | 105 |
| B | Paraphrase | 30 | 105 |
| C | Style Rewrite | 30 | 105 |
| D | Original + Style Rewrite | 60 | 210 |
| E | Original + Paraphrase | 60 | 210 |

כל זרוע משתמשת באותם source IDs ואותן תוויות; אין סינון נפרד לזרוע. D/E הן הרחבה מזווגת באותו סדר source/variant. אין שכתובים של validation/test. Class priors נשמרים ללא איזון/oversampling שונה בין זרועות.

תכנון קבוע: frozen production MiniLM encoder, ראש חדש 384→128, ReLU, dropout .3, 7 outputs, Adam lr=.001, batch16, seeds `[7,42,123,2026,31415]`. כל seed משתמש באותו initialization של הראש בכל התנאים; לא משתמשים בראש מהפיילוט כמודל מאומן של תנאי A. Encoder משותף קפוא בכל התנאים. אין הבטחה שזו הארכיטקטורה המיטבית; היא נבחרה לשחזור והשוואה, לא מטעמי test performance.

**תקציב ראשי קבוע:** `updates = 20 × ceil(N_source/16)` בכל A–E; batch מלא באמצעות מחזורים shuffled דטרמיניסטיים. ל־30: 40 updates, 640 examples processed; ל־105: 140 updates, 2240 processed. ל־A–C כל dataset עובר בקירוב פי שניים מחזורים לעומת D–E; כך אין להכפיל updates רק בגלל augmentation. אותו batch/input-count, אך lengths שונים ולכן FLOPs/tokens אינם זהים; יש לשמור גם token counts וזמן בהרצה העתידית. אורך המודל ומדיניות truncation ייקבעו לפי tokenizer המקורי ולא לפי test. קלט שנקטע חייב להיות מסומן, לא מוסתר.

Checkpoint ראשי: סוף התקציב הקבוע, ללא early stopping נפרד. Validation originals עם gold משמשים רק לבדיקת כשלים ולתכנון לפני freeze, לא לבחירת שכתוב מוצלח או checkpoint טוב בדיעבד. כל שינוי hyperparameter דורש גרסת פרוטוקול חדשה על development, לא test. אין לקבע עכשיו target כגון +5pp לאחר שנצפו תוצאות קודמות.

אפשר להוסיף בעתיד F=Original repetition עם 2N rows כבקרת representation/indexing נפרדת; הוא אינו נדרש להשוואה D–E שכבר שוות בגודל ובתקציב. אין להסיק ייחוד סגנוני מ־D−A בלבד.

## כלל קבלה ו־QC — נקבע לעתיד

1. כל source label חייב להיות מאומת ברמת הטקסט; חוסר התאמה להצעה הישנה עוצר את הרשומה לבירור, לא משנה אותה בשקט. codebook ואוכלוסיית labels יקובעו לפני אימון.
2. לכל Style: human meaning=Yes, human stance=Yes, human style=Yes, human drift=No. Borderline נשמר בנפרד ומועבר ל־adjudication; אין להפכו ל־Yes אוטומטית.
3. לכל Paraphrase: human meaning=Yes, stance=Yes, drift=No; אין דרישה להתערבות author-style. שינוי/אי־שינוי ניסוח נמדד ומדווח בנפרד.
4. Guards וספיהם נשארים כפי שהם; פסילה היא risk signal. גם מעבר אינו מחליף אדם. הערכת אדם מול guard fail נשמרת עם הסבר, בלי לשנות את הסף.
5. שני סוקרים עצמאיים ככל שניתן; לשמור ratings מקוריים, agreement לפני הכרעה והכרעת שלישי/דיון בנפרד. אין לחשב agreement של שני אנשים מ־Claude+אדם.
6. QC נחתם לפני תחזיות הניסוי המרכזי; המסמנים לא רואים תוצאות מודל, author labels או reviews קודמים. ל־30 שכבר עברו פיילוט/דיון אין לטעון עיוורון היסטורי מלא או קביעה לפני כל תוצאה.

**מניעת selection bias:** כל 105 המקורות מדווחים ב־flow/coverage table, כולל missing/failed/Borderline לפי כותב/class. אין לבחור subset לפי תחזיות. ברגע שכל ניסיון היצירה המתוכנן הושלם, הניתוח הראשי של all-attempted sources משתמש ב־Original כ־fallback **בשתי** זרועות B/C כאשר אחת משתי הגרסאות לא עברה QC; D/E מקבלות גם הן את אותו fallback ומספר rows זהה. אין למלא 75 שכתובים שטרם נוסו ב־Original ולהציג זאת כהתערבות מלאה. ניתוח secondary per-protocol משתמש ב־intersection המשותף של אישורי P ו־Style, באותם IDs לכל A–E. לדווח שהראשי מעריך policy הכולל QC/fallback, והשני conditional על acceptance ואינו מייצג את כל המאגר.

## בקרות שימור ומניפולציה

בדיקה מפורשת של claims, attribution, certainty, quantifiers, negation, quotations, participant roles, event characterization, time, causality ו־rhetorical intensity. דוגמאות לדיון: `421951` No one→Few people; `0105f26ef9f1` will→can; `421024` don't have to→not supposed to; `421279` צמצום הדגשת המאמץ. אין לשנות את הכרעות הסוקר המקוריות; adjudication הוא שדה חדש עם provenance.

אותו style proxy קיים ו־Author-ID fixed-original-fitted משמשים manipulation checks, לא תחליף לאיכות. baseline content/topic/year לא אמור להיות מנותק על סמך label בלבד. Paraphrase הקיים נוצר ב־generator אחר ובחלקו כולל drift/פתיח מכונה; זו בקרה לא מושלמת. שינוי או ניקוי שלה יוצר גרסת התערבות חדשה, לא עריכה שקטה.

## הערכה וניתוח סטטיסטי

- מדד ראשי Macro-F1 על שתי הקטגוריות הפעילות עם zero_division=0; דיווח Accuracy, per-class precision/recall/F1/support, inactive-output rate, confusion, per-author accuracy ו־F1 עם תמיכות. כותב בעל class אחד אינו מספק הערכת generalization רב־מחלקתית לבדו.
- לחשב לכל seed ולכל תנאי על **אותם** evaluation IDs; לדווח mean/SD בחמש ריצות. seeds אינם חמישה datasets עצמאיים.
- primary contrasts C−B ו־D−E; Holm לשני p-values אם מבוצעת בדיקה תקפה. comparisons מול A הן secondary ומסומנות כך.
- paired author-cluster bootstrap (למשל 10,000 draws, seed20261109) על שורות תחזית מזווגות; בכל draw לדגום כותבים עם כל השורות/תנאים ולחשב את ההפרש הממוצע בין seeds. אין להתייחס לכל שכתוב או seed כיחידה עצמאית.
- עם שישה כותבים בלבד לדווח CIs תיאוריים, דפוסי per-author ו־leave-one-author-out sensitivity; exact cluster permutation יכול לשמש ניתוח קטן ומוגבל. אין הבטחת power או טענת שקילות מ־p>.05. Class coverage לאחר resampling עשויה להשתנות ויש לדווח.
- score משופר אינו הוכחת מנגנון: נדרשת גם התערבות ששמרה narrative, שינתה author cues ומועילה מעבר לבקרה. גם שילובם אינו causal identification מלא מול תוכן/זמן.

## פיתוח לעומת הערכה סופית

לא הורץ בניסוי ההכנה test; לא נשמרו טקסטי test בטיוטות האימון. ספירות/hash audits של splits הן metadata, לא הערכה. ה־70 ב־byline study וה־14-author social holdout הם מאגרים שונים; שניהם כבר שימשו לניסויים היסטוריים. אין לקרוא לשימוש חוזר confirmation חדש. לפני תוצאה סופית נדרש freeze חתום של cohort/labels/generator/QC/config, והחלטה עם המנחה אם דרושים כותבים חדשים באמת.

## שחזור ומצב ביצוע

[הוראות, קוד וטיוטות](artifacts/experiments/main_training_preparation_20261109/REPRODUCTION.md). קיימים 25 configs ו־25 סדרי batches משוחזרים לחמש זרועות וחמישה seeds. `check_readiness.py` מחזיר exit2 ומונה חסרים; אינו יכול להשיק אימון. **אין כאן trainer מאושר end-to-end או תוצאה חדשה של A–E.** חיבור ה־trainer להרצה ייעשה אחרי נעילת gold/QC/provenance, בלי להסתמך על configs כתחליף לשערים האלה.

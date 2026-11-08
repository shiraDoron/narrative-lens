# תוכנית לניסוי המרכזי — לא בוצע

מחזור פיתוח 8–9.11.2026. אין כאן הרשאה או הרצה של test, Narrative Classifier training, prompts חדשים או tuning של guards. זו תוכנית המשך המבוססת על מגבלות הנתונים והתוצאות, לא תוצאה מחקרית.

## שתי שאלות שונות

**דיאגנוסטיקה:** האם שינוי טקסטואלי, המשמר משמעות ועמדה, משנה את תחזיתו של *אותו* Narrative Classifier? השוואה זוגית של Original/Rewrite מודדת רגישות, ולא שיפור generalization. כיוון השינוי יכול להיות מועיל או מזיק.

**התערבות באימון:** האם מודל שאומן עם התערבות סגנונית משפר generalization לכותבים שלא נראו באימון, מול מודל זהה ללא ההתערבות? זו השוואה בין תהליכי אימון מבוקרים, עם holdout של כותבים; Author-ID אינו תחליף לה.

חידוש אפשרי הוא בדיקת author-style shortcut וההתערבות בו, לא המצאת Text Style Transfer. יכולת זיהוי כותב, הסרת cue והשפעה על סיווג נרטיב הם שלושה שלבים נפרדים שאינם גוררים זה את זה.

## תנאים לפני ניסוי מרכזי

1. להשלים Human Validation אמיתי לכל 30 הזוגות. חבילת השדות הריקים כבר מוכנה ואינה כוללת scores/reviews/מחבר. לשמור גם כישלונות ו־Borderline, ולתעד סוקר/ת ותאריך בנפרד. במידת האפשר שני סוקרים עצמאיים, ואז adjudication; רק אז למדוד agreement אנושי. לא להפוך הסכמת LLM ל־agreement בין אנשים.
2. לתיוג נרטיב של Original נדרש תהליך נפרד: שימור stance אינו מאמת שהתווית המקורית נכונה. מקור צריך להיבדק ברמת הטקסט, בלי לדעת מי הכותב. 0/429 source labels מולאו אנושית בריפו. לא לאמץ תווית לפי זהות הכותב ולא לכפות Unclear/תוויות אחרות לבינארי.
3. להשיג את ה־External LLM Review המלא של ChatGPT לפי ID, כולל notes ושם/גרסת סוקר, prompt ותאריך. המצרפים נשמרו אך אינם מספיקים ל־discrepancy analysis או לזיהוי 16 ה־clean. זהו מקור דיאגנוסטי נוסף, לא gate אנושי.
4. להשלים provenance של generation: ה־CSV הקיים אינו כולל את ה־prompt המקורי, גרסת ChatGPT, הגדרות sampling, היסטוריית בקשה או finish_reason. אין לטעון לשחזור generation זהה בלי המידע. עד אז אין ליצור batch בטענה שזו אותה שיטה, ואין להחליף בשקט למודל מקומי.
5. לקבע מראש protocol, branches, מדדים, דרכי עצירה וכללי acceptance/labeling. לא להשתמש בתחזיות Narrative/Author-ID לבחירת rewrites או לשיפור prompt. ה־guards והספים הקיימים נשארים ללא שינוי.

## כמה שכתובים חסרים — רשימות מוכנות, לא יצירה

| מסלול | יעד זוגות | חדשים מעבר ל־30 | שימוש |
|---|---:|---:|---|
| כל קוהורט train הבינארי הקיים | 105 | **75** | המינימום הישיר להרחבת אותו intervention candidate על כל ה־eligible train, בכפוף לתיוג המקור |
| כל הטקסטים של כותבי train | 202 | **172** | Author-ID ו־style development ללא צורך בנרטיב בינארי; לא כולם מתאימים לאימון Narrative |
| ביניים מאוזן ל־5 זוגות לכל אחד מ־9 הכותבים | 45 | **15** | batch פיתוח קטן, כולל כל 30 הקיימים, ללא סינון לפי הצלחה; מוגבל עדיין ל־45 זוגות |

`additional_75_rewrites_manifest.csv` מפרט בדיוק את כל 75 ה־IDs, המקורות והכותבים לפי סדר hash קבוע, ללא תוצאות review או classifier. נשמרו גם [manifest מאוזן ל־15](additional_15_balanced_rewrites_manifest.csv) ו[manifest ל־172 Author-ID בלבד](additional_172_author_only_manifest.csv). לא נוצרו outputs ולא נבחרו רק מקורות נוחים. הרחבה ל־105 מחזקת את אומדן הצלחת ההתערבות באותו train, אך אינה בהכרח חבילת Author-ID evaluation מאוזנת: יש כותבים עם 5–6 eligible sources בלבד. אם כל אלה משמשים להערכה, לא יישארו eligible Originals לאימון אותו כותב; אפשר להשתמש ב־raw train pool המקורי, תוך דיווח על שינוי אוכלוסייה, או לאסוף מקורות train נוספים.

במסלול 45: להוסיף 1 ל־Marc Dion, Jamie Stiehm, Froma Harrop, Chuck Norris ו־Lawrence Kudlow; 2 ל־David Harsanyi ול־Veronique de Rugy; ו־3 ל־Connie Schultz ול־Jim Hightower — 15 בסך הכול. הבחירה בתוך כותב תהיה לפי hash ID מתוך רשימת ה־75, לא לפי איכות rewrite צפויה. אין להפוך את batch הביניים למדגם מייצג של כלל המאגר.

בעת generation עתידי: Original בלבד בבקשה; IDs/logging נשמרים מקומית; לא לשלוח v2/v3, ratings, guard scores או תחזיות. לשמור raw request/output, prompt hash, model version/date/parameters/finish_reason, כולל כשלים ו־copies. אותה מדיניות ואותה כמות ניסיונות לכל ID. אם פרטי generation המקורי אינם ניתנים לשחזור, נדרש שם חדש לגרסת השיטה ופרוטוקול חדש — לא שינוי שקט של prompt קיים.

## ניסוי A — רגישות של Narrative Classifier

- קיבוע model והליך preprocessing מראש. להערכה שאינה in-sample, המקורות של זוגות ההערכה וכל אחיהם/גרסאותיהם חייבים להיות מחוץ לאימון. אין להשוות Original שהיה ב־fit ל־Rewrite כ“טקסט חדש” ולהסיק מכך שיפור/פגיעה.
- השוואה זוגית על אותם IDs: תחזיות, probabilities, correct→wrong / wrong→correct ו־label flip. לדווח Accuracy, Macro-F1, per-narrative recall, שינוי בסבירות לתווית gold, וכן stability בתוך author/event.
- עלייה ב־flip rate לבדה אינה style shortcut: היא יכולה לנבוע מ־semantic drift, format/domain shift, שגיאות תווית או רגישות לאורך. לכן לשלב Human-preserved pairs ובקרת paraphrase/formatting נפרדת, בלי לבחור rewrite על פי התחזית.
- ניתוח all-attempted לצד human-preserved subset שנקבע מראש; לא לייחס תוצאת subset לכל ה־IDs. Original/Rewrite נשארים יחד ב־fold גם בניסוי sensitivity.

## ניסוי B — controlled augmentation ו־unseen authors

לקבע אותם source IDs, תוויות gold ו־author splits לכל הזרועות. אין להכניס לטקסטים המיוצרים דוגמאות או משובים מכותבי test. להשוות לפחות:

| זרוע | אימון | מה היא בודקת |
|---|---|---|
| Original | מקורות train בלבד | baseline |
| Original repeated / compute matched | אותם מקורות שוב, בתקציב אימון זהה | השפעת כמות צעדים/דוגמאות בלי מידע חדש |
| Original + Formatting | שינוי פורמט בלבד | רגישות שטחית |
| Original + generic paraphrase | augmentation שאינו מכוון author-style | תועלת paraphrase כללית |
| Original + style-changed | ההתערבות המאומתת | התועלת מעבר לבקרות |

הארכיטקטורה, encoder, מספר צעדי optimization, seeds, class balancing ותקציב generation יהיו זהים או מותאמים במפורש. לא להציג ניצחון של זרוע גדולה יותר כניצחון סגנוני. שימוש ב־7-output head קיים בקורפוס בן שני נרטיבים חייב לדווח Macro-F1 לשני הנרטיבים הפעילים בנפרד מהשבעה; אין מכאן שחזור מלא של שאלת שבעת הנרטיבים במדיה החברתית.

בחירת hyperparameters/early stopping תהיה על development authors בלבד, עם קבוצות article/event כשאפשר. ה־val המוקצה כולל ארבעה כותבים; אין להעביר כותבים ל־train או לשנות את ה־split הקפוא כדי להשיג תוצאה. כותבי test אינם משמשים לבניית style centroids, TF-IDF vocabulary, thresholds, דוגמאות prompt או בחירת method.

## נטרול גורמי ערבוב והימנעות מבחירה מוטה

- לקבע מראש acceptance rule משותף: Human meaning=Yes AND stance=Yes AND style=Yes. Borderline אינו Yes. להחיל על כל ההפקות ולדווח coverage לפי כותב/נרטיב. אין כאן עדיין acceptance שהוחל.
- בניתוח all-attempted augmentation אפשר להשתמש ב־Original כ־fallback ל־rewrite שנכשל, עם compute/exposure control מפורש. Per-protocol human-preserved יהיה ניתוח משני על אותה קבוצת מקורות משותפת לכל השוואה; לא למחוק כותבים שקשה לשכתב ולספר על כלל המאגר.
- לשמור גם קריאות, אורך, ציטוטים, certainty, attribution, roles ו־event characterization. שינוי cue פוליטי אינו “style בלבד”. Human-preserved אינו fact-check של אמיתות הטענה בעולם.
- לבנות event/topic/time metadata על train/val בלבד ולתכנן השוואות event-matched כשיש תמיכה. כעת יש confounding גדול בין כותב לשנת פרסום. מקור טקסט חדש מאותו כותב ובאותה תקופה עדיף על הנחה שמאפיינים שנתפסו ב־2014 מייצגים סגנון מחבר כיום.
- לא לבחור את ה־function-word probe רק מפני שהוא נתן ירידה: ארבעת ה־probes מדווחים; רק אחד הראה אות חזק בחלק מההגדרות. ה־probe הוא כלי אבחון ולא criterion לייצור/סלקציה של הטקסט.

## מדדים והסקה

Primary: unseen-author Macro-F1 של style augmentation מול Original, יחד עם per-author recall ותקינות שימור אנושית. Secondary: מול paraphrase/compute controls, in-distribution accuracy, calibration ו־Author-ID probes. להגדיר מראש מעשיות/אי־נחיתות ב־in-distribution, משפחת השערות ותיקון multiplicity לפני evaluation. לא לבחור margin אחרי צפייה ב־test.

להשתמש ב־paired prediction comparisons על אותם IDs וב־bootstrap/permutation לפי author/event, לא לספור כמה seeds או כמה גרסאות טקסט כאנשים עצמאיים. להציג CI ואפקטים, עם caveat של 6 test authors ו־9 train authors בלבד. גודל מדגם לעוצמה יש לקבוע לפי אפקט מינימלי רלוונטי ושיעור discordant pairs מתוך development, לא להבטיח power מ־30 זוגות.

## ה־test אינו השלב הבא

לא הורץ test חדש. ה־test הקפוא כבר הופיע בניסויים היסטוריים של הפרויקט; “לא שימש בסבב הפיתוח הזה” אינו “מעולם לא נצפה”. תוצאה confirmatory עצמאית עשויה לדרוש כותבים חדשים ופרוטוקול frozen נוסף. תוצאת test קיימת, גם אם נשמרה החלוקה, אינה מאפשרת adaptive tuning בלתי מוגבל ואז טענת confirmation.

הפעולה המיידית היא איסוף judgments אנושיים והשלמת provenance, ואז אישור batch train-only מוגדר. אין עדיין סיבה לאמן Narrative Classifier מחדש או להרחיב ל־test.

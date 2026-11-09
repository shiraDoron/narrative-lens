# מיקוד התזה: ספרות, פער ותרומה אפשרית

תאריך בדיקה: 2026-11-09. שאלת המחקר: האם מסווג נרטיבים פוליטיים נשען על סגנון הכותב כ־shortcut, והאם התערבות השומרת על הנרטיב משפרת הכללה לכותבים חדשים?

**המלצה:** למקד את התרומה בהערכה אמפירית מבוקרת של השאלה, ולא בפיתוח Style Transfer חדש. יש תקדימים קרובים מאוד להתערבות בסגנון לשיפור משימת סיווג; אין בסיס לטענת “ראשונים להשתמש בשכתוב להסרת shortcut”. גם Author-disjoint evaluation אינו חדש.

## היקף הקריאה ואופן ביסוס הטענות

נקראו התיעוד המקומי [Related Work](docs/style_transfer_related_work_he.md), [הערכת כלים קיימים](docs/existing_style_transfer_tools_evaluation_he.md), דוחות הניסויים והמקורות הראשוניים המקושרים להלן. בוצע חיפוש ממוקד במונחי style obfuscation, counterfactual augmentation, caregiver/author-invariant classification, narrative/framing ו־OOD. זו סקירה ממוקדת, לא systematic review ממצה. “לא נבדק” להלן פירושו שלא הודגם **במאמר הנדון**, ולא טענה שאין עבודה אחרת בעולם. אין להשתמש בהיעדר תוצאת חיפוש כהוכחת ראשוניות.

המונחים שונים: style הוא אופן הביטוי; stance היא עמדה כלפי יעד; framing כולל בחירת היבטים, תפקידים, סיבתיות ועוצמה; narrative הוא מבנה פרשני רחב יותר. Left/Right אצלנו הן קטגוריות אידאולוגיות גסות, לא הטקסונומיה הסיפורית העשירה של SemEval. שינוי ניסוח כגון `riots`→`protests` עלול לשנות את האות הרלוונטי לתווית, ולא רק nuisance סגנוני.

## 1. Geirhos et al. — Shortcut Learning in Deep Neural Networks (2020)

[מאמר](https://doi.org/10.1038/s42256-020-00257-z), [גרסה פתוחה](https://arxiv.org/abs/2004.07780), [קוד ניסוי ההמחשה הרשמי](https://github.com/rgeirhos/shortcut-perspective).

- **שאלה:** מדוע הצלחה בבנצ׳מרק אינה מתורגמת להכללה?
- **שיטה:** מאמר Perspective המאחד כשלים דרך כללי החלטה קלים שאינם עוברים לתנאי בדיקה אחרים.
- **נתונים ופרוטוקול:** סינתזה של מחקרים ודוגמאות, לרבות ניסוי צעצוע; אינו ניסוי political narrative חדש.
- **תוצאות:** מסגרת להסבר כשלים והמלצות להערכה תחת shift; אין מספר יחיד המוכיח שכל מודל משתמש ב־shortcut.
- **מה הוכח/בוסס:** התאמה ל־IID אינה מספיקה לביסוס כלל ההחלטה הרצוי.
- **יחס אלינו:** מניע לביקורת author-disjoint, לא ראיה שסגנון דווקא הוא הסיבה לפער המקומי.
- **גבול:** לא נבחנה כאן התערבות המשמרת מסגור פוליטי על כותבים חדשים.

## 2. Veitch et al. — Counterfactual Invariance to Spurious Correlations in Text Classification (NeurIPS 2021)

[פרסום](https://papers.neurips.cc/paper_files/paper/2021/hash/8710ef761bbb29a6f9d12e4ef8e4379c-Abstract.html), [PDF מחברים, כותרת חלופית](https://arxiv.org/pdf/2106.00545). לא אומת repo מימוש רשמי בקריאה זו.

- **שאלה:** מתי אי־שינוי תחזית תחת התערבות לא רלוונטית קשור לעמידות OOD?
- **שיטה:** counterfactual invariance, ניתוח causal/anti-causal ורגולריזציה התלויה במבנה הסיבתי.
- **נתונים ופרוטוקול:** טענות פורמליות לצד ניסויי סיווג טקסט; לא ניסוי כותבי דעה פוליטיים שלנו.
- **תוצאות:** סוגי regularization וערבויות shift שונים למבנים סיבתיים שונים (§2–4).
- **מה הוכח:** הקשר בין stress test להכללה מותנה בהנחות, ולא אוטומטי.
- **יחס אלינו:** flip הוא מדד רגישות לשכתוב; כדי לכנותו style effect צריך להגן על הנחת שימור התוכן והתווית.
- **גבול:** אין ערובה לתוצאות שלנו ללא זיהוי התערבות ושימור framing.

## 3. Kaushik, Hovy & Lipton — Learning the Difference that Makes a Difference (ICLR 2020)

[מאמר](https://openreview.net/forum?id=Sklgs0NFvr), [נתונים וקוד מחברים](https://github.com/dkaushik96/counterfactually-augmented-data).

- **שאלה:** האם זוגות נגד־עובדתיים מפחיתים תלות בדפוסים מקריים?
- **שיטה:** בני אדם עורכים טקסט באופן מינימלי כדי **לשנות את התווית**, ואז משלבים מקור ועריכה באימון.
- **נתונים ופרוטוקול:** ביקורות sentiment ו־NLI; Original, edited ו־combined, עם בדיקה בין ההתפלגויות.
- **תוצאות:** מודלים המאומנים על צד אחד נכשלים יותר בצד השני; שילוב עוזר לשני התנאים ומחליש אותות לא רלוונטיים.
- **מה הוכח:** CAD מועיל בתנאים שנבדקו, לא בכל התערבות אוטומטית.
- **יחס אלינו:** augmentation מבוקר כבר קיים; אצלנו רוצים לשמור את התווית ולשנות style.
- **גבול:** אין כאן הוכחה לשימור נרטיב פוליטי או unseen-author benefit.

## 4. Mireshghallah & Berg-Kirkpatrick — Style Pooling (EMNLP 2021)

[מאמר ו־PDF](https://aclanthology.org/2021.emnlp-main.152/), [מימוש רשמי](https://github.com/mireshghallah/style-pooling).

- **שאלה:** האם הסתרת סגנון יכולה לשפר הוגנות מסווג downstream?
- **שיטה:** VAE עם priors של intersection/union ו־de-boosting; שכתוב הטקסט עצמו.
- **נתונים ופרוטוקול:** Yelp סינתטי ו־Blogs; בסיווג occupation משנים את המתאם עם גיל ומודדים utility ו־TPR gap (§4.2).
- **תוצאות:** Intersection מציג trade-off מועיל בין הוגנות לתועלת; Union אינו משפר הוגנות באותה בדיקה. נבדקים גם fluency/semantic consistency.
- **מה הוכח:** כבר הודגם שימוש ב־style obfuscation להפחתת הטיה בסיווג אחר.
- **יחס אלינו:** תקדים ישיר לרעיון הכללי; השוני האפשרי הוא מסגור פוליטי ופרוטוקול כותבים נפרדים.
- **גבול:** לא הודגמה אותה שאלת political narrative עם השכתובים והאילוצים שלנו. הירידה בזיהוי מאפיין רגיש אינה הסרת זהות כל כותב.

## 5. Feder, Wald, Shi, Saria & Blei — Causal-structure Driven Augmentations (NeurIPS 2023)

[עמוד מוסדי](https://research.google/pubs/causal-structure-driven-augmentations-for-text-ood-generalization/), [גרסה מעודכנת: Data Augmentations for Improved (Large) Language Model Generalization](https://arxiv.org/html/2310.12803v2). לא אומת מימוש רשמי; אין לייחס repo צד שלישי למחברים.

- **שאלה:** האם התערבות במאפיין המשויך לכותב יכולה לנתק מתאם כוזב ולשפר סיווג OOD?
- **שיטה:** CATO, שימוש במידע עזר ובהנחות סיבתיות/difference-in-differences להפקת counterfactuals בעזרת LM.
- **נתונים ופרוטוקול:** clinical narratives ב־MIMIC/i2b2, ביקורות CeBAB בתנאי מתאם מלאכותי וסימולציה; שימור מידע רפואי מול סגנון caregiver.
- **תוצאות:** שיפור OOD ביחס לבקרות במערכים שנבדקו; גרסת המחברים כוללת הנחות זיהוי ומגבלות יצירה (§3–5).
- **מה הוכח:** הרעיון של סגנון כותב כמבלבל במשימת סיווג והתערבות לשיפור הכללה **כבר פורסם**.
- **יחס אלינו:** התקדים הקרוב ביותר; מעבר מרפואה לפוליטיקה לבדו אינו חידוש אלגוריתמי.
- **גבול:** לא נבדק האם rhetorical intensity/מסגור הם חלק מהתווית הפוליטית שאסור להסיר. נדרש ניסוי כזה ולא אימוץ ערבויותיהם ללא הנחות.

## 6. Fisher et al. — StyleRemix (EMNLP 2024)

[מאמר](https://aclanthology.org/2024.emnlp-main.241/), [מימוש רשמי](https://github.com/jfisher52/StyleRemix).

- **שאלה:** כיצד להסוות זהות מחבר באופן נשלט וניתן לפרשנות?
- **שיטה:** פרופיל כותב והתערבות בצירי סגנון מפורשים באמצעות LoRA adapters.
- **נתונים ופרוטוקול:** AuthorMix: כ־30K טקסטים ארוכים, 14 כותבים וארבעה domains; DiSC: שבעה צירים ב־16 כיוונים; הערכה אוטומטית ואנושית.
- **תוצאות:** יתרון על baselines ו־LLMs גדולים במדדי המשימה ובתחומים שנבדקו.
- **מה הוכח:** כלי קיים לשינוי סגנון ספציפי למחבר; אין צורך להמציא מחדש obfuscation כתרומה שלנו.
- **יחס אלינו:** generator אפשרי בלבד; attribution attack success שונה מתועלת ל־Narrative Classifier.
- **גבול:** אין כאן הוכחה לשיפור נרטיב על unseen authors או לשימור כל ודאות/ציטוט בטקסטים הקצרים שלנו.

## 7. Altakrori, Cheung & Fung — The Topic Confusion Task (Findings EMNLP 2021)

[מאמר](https://aclanthology.org/2021.findings-emnlp.359/), [עמוד המחבר שאליו מפנה המאמר לקוד](https://malikaltakrori.github.io/). לא אומת כאן repo נקודתי.

- **שאלה:** כיצד להבחין בין זיהוי סגנון לזיהוי נושא ב־Author-ID?
- **שיטה:** החלפת שיוך author–topic בין אימון לבדיקה ופירוק סוגי טעויות.
- **נתונים ופרוטוקול:** גרסת Guardian מנוקה ומאוזנת, כמה נושאים לכל כותב; השוואת stylometry/POS, n-grams ו־BERT/RoBERTa.
- **תוצאות:** stylometry+POS פחות רגישים לשינוי נושא; שילוב features עוזר; מודלים גדולים אינם בהכרח עדיפים (§4–5).
- **מה הוכח:** Author-ID אינו מדד “סגנון טהור”, והפרדת content/style דורשת פרוטוקול.
- **יחס אלינו:** בקרות topic/time נחוצות גם אחרי accuracy גבוה ב־Author-ID.
- **גבול:** משימתם היא לזהות כותב; שלנו היא לשמור נרטיב ולהכליל לכותבים חדשים.

## 8. Koh et al. — WILDS (ICML 2021)

[מאמר](https://proceedings.mlr.press/v139/koh21a.html), [מימוש רשמי](https://github.com/p-lambda/wilds).

- **שאלה:** איך למדוד distribution shift מציאותי באופן סטנדרטי?
- **שיטה:** עשרה benchmarks, חלוקות domains ומדדי קבוצות; ERM מול שיטות robustness.
- **נתונים ופרוטוקול:** Amazon-WILDS מנבא 1–5 כוכבים מביקורות, עם כותבים נפרדים בין train/test ומדד 10th-percentile user accuracy.
- **תוצאות:** פערי OOD נשארים גם בשיטות robustness; בדוגמת Amazon בטבלה 2 המדד יורד מ־71.9 ל־53.8 בין תנאי ההערכה המוגדרים שם.
- **מה הוכח:** unseen-writer evaluation ושונות בין כותבים הם כבר benchmark מוכר.
- **יחס אלינו:** צריך ממוצע וכיסוי לפי כותב, לא רק pooled F1.
- **גבול:** המאמר אינו מוכיח style shortcut פוליטי ואינו מספק את התערבות השימור שלנו.

## 9. Card et al. — The Media Frames Corpus (ACL-IJCNLP 2015)

[מאמר](https://aclanthology.org/P15-2072/), [נתונים וכלי מחברים](https://github.com/dallascard/media_frames_corpus).

- **שאלה:** האם ניתן לאפיין framing באמצעות codebook מעבר לנושא יחיד?
- **שיטה:** 15 ממדי מסגור כלליים, annotation של spans ומסגור מרכזי.
- **נתונים ופרוטוקול:** אלפי כתבות על הגירה, עישון ונישואים חד־מיניים; שלבי annotation ומספר מסמנים בחלק מהכתבות.
- **תוצאות:** משאב מתויג ותיאור איכות/הסכמה בין מסמנים; לא טענת פתרון מושלם למסגור.
- **מה הוכח:** מסגור דורש הגדרה ואימות אנושי ברמת הטקסט, מעבר לזהות העיתון.
- **יחס אלינו:** תווית כותב/חשבון אינה תחליף ל־text-level narrative gold.
- **גבול:** left/right שלנו אינן 15 הקטגוריות שלהם; אין להשוות F1 ישירות או לאחד ontology.

## 10. Otmakhova, Khanehzar & Frermann — Media Framing: A Typology and Survey (ACL 2024)

[מאמר](https://aclanthology.org/2024.acl-long.822/), [מאגר הסקירה הרשמי](https://github.com/julia-nixie/awesome-media-framing).

- **שאלה:** מה מודדים בפועל מחקרי computational framing?
- **שיטה:** סקירה בין־תחומית וטיפול בהיבטים סמנטיים, קוגניטיביים ותקשורתיים.
- **נתונים ופרוטוקול:** מיפוי מחקרי framing והגדרותיהם; לא ניסוי סיווג יחיד.
- **תוצאות:** typology והצבעה על הפער בין topic לבין framing רחב יותר.
- **מה הוכח/בוסס:** יש אי־אחידות מושגית; דמיון סמנטי כללי אינו ממצה שימור מסגור.
- **יחס אלינו:** certainty, בחירת פעלים, quantifiers ועוצמה רטורית עלולים להיות חלק מהמשימה.
- **גבול:** הסקירה אינה מאמתת את הגדרת הנרטיב או את labels שלנו.

## 11. Piskorski et al. — SemEval-2025 Task 10

[מאמר](https://aclanthology.org/2025.semeval-1.331/), [אתר המשימה הרשמי](https://propaganda.math.unipd.it/semeval2025task10/). האתר הוא משאב/פרוטוקול רשמי, לא repo של מודל יחיד.

- **שאלה:** כיצד לאפיין נרטיבים ומסגור ישויות בחדשות רב־לשוניות?
- **שיטה:** entity framing, narrative classification והפקת הסבר לנרטיב.
- **נתונים ופרוטוקול:** מלחמת רוסיה–אוקראינה ואקלים בחמש שפות; טקסונומיה היררכית ו־train/development/test רשמיים.
- **תוצאות:** 66 צוותים הגישו תוצאות רשמיות בכלל המשימות; השוואת מערכות וביצועים לפי subtask ושפה (§6).
- **מה הוכח:** classification של נרטיבים פוליטיים/תקשורתיים אינו תחום חדש.
- **יחס אלינו:** ניתן ללמוד מה־codebook וההפרדה בין roles/narrative; אין לנו אותה רמת פירוט בתוויות.
- **גבול:** אין במאמר המשימה ניסוי זהה להתערבות author-style ששומרת framing ומושווית לפרפרזה תחת author-disjoint training.

## 12. Zhou, Tang, Yao & Zhu — Navigating the Shortcut Maze (Findings EMNLP 2024)

[מאמר](https://aclanthology.org/2024.findings-emnlp.146/), [מימוש רשמי](https://github.com/yuqing-zhou/shortcut-learning-in-text-classification).

- **שאלה:** האם מסווגי טקסט משתמשים ב־shortcuts מורכבים, לרבות סגנון כותב?
- **שיטה:** occurrence/style/concept shortcuts; Llama2-70B משכתב ל־formal/casual ולסגנונות Shakespeare/Hemingway, ואז משנים את המתאם style–label בין train ל־anti-test.
- **נתונים ופרוטוקול:** Yelp, תת־קבוצת GoEmotions ו־Beer; BERT בחמש ריצות, לצד LLMs ושיטות robustness (§2–3).
- **תוצאות:** ב־BERT יש פערים גדולים ומובהקים בין normal ל־anti-test בכל משפחות הקיצורים; גם LLMs אינם חסינים.
- **מה הוכח:** תלות ב־author-style shortcut והפגיעה בעקבות שינוי מתאם **כבר נבדקו ישירות** בבנצ׳מרק מבוקר.
- **יחס אלינו:** אין לטעון שעצם בדיקת style shortcut ב־NLP היא חידוש. אצלנו הכותבים אמיתיים, והמתאם אינו מוזרק מראש.
- **גבול:** לא נבחנה אותה משימת framing פוליטי עם human-gold preservation ו־unseen real authors; מניפולציה מלאכותית חזקה אינה זהה לשכתובים הקצרים שלנו.

## חפיפות שאין להציג כחידוש

| רעיון | תקדים | מה נשאר אפשרי אצלנו |
|---|---|---|
| שינוי style להחלשת מאפיין מחבר ולשיפור מסווג | Style Pooling; CATO | בדיקת מגבלות השיטה כשמסגור פוליטי עצמו תלוי בניסוח |
| Authorship obfuscation | StyleRemix ואחרים | שימוש בכלי כאמצעי מדידה, לא contribution של generator |
| אימון על counterfactuals | Kaushik; Feder | בקרת מקור/פרפרזה/סגנון עם label-preserving interventions |
| הערכה על כותבים חדשים | Amazon-WILDS | יישום אמפירי ממוקד בנרטיבים, בכפוף ל־gold ולבקרות |
| בדיקת שינוי תחזית תחת שינוי קלט | Veitch | ניתוח זוגי זהיר, בלי להסיק סיבתיות מ־flip |
| יצירת author-style shortcut ובדיקתו בסיווג טקסט | Zhou et al. 2024 | לבדוק האם הוא קיים ומזיק בנתונים פוליטיים טבעיים, לא להניח מראש |

לא אותר בקריאה הממוקדת מחקר המדגים בדיוק את כל הצירוף המקומי: כותבי דעה פוליטיים בעלי byline, אימות נפרד של stance/certainty/roles/quotes, בקרת פרפרזה באותם IDs, ומבחן generalization מבוקר. זהו **פער מועמד**, לא הצהרת ראשוניות. יש לבצע גם backward/forward citation search סביב CATO, Style Pooling ו־Shortcut Maze לפני ניסוח טענת novelty סופית.

## שלושה ניסוחים אפשריים לתרומה — דירוג

| עדיפות | ניסוח שאפשר להציג למנחה | חידוש יחסי | ראיות כיום | היתכנות |
|---|---|---|---|---|
| 1 | מחקר אמפירי המפריד בין יכולת זיהוי מחבר, רגישות לשכתוב ושיפור הכללה, ומראה את מגבלות הייחוס לסגנון בסיווג נרטיב פוליטי | בינוני, כיישום וניתוח מגבלות; העקרונות קיימים | החזק ביותר: פערי מחבר, בקרות ותוצאות שליליות/מעורבות; עדיין ללא זיהוי סיבתי | גבוהה יחסית, עם אימות אנושי ממוקד |
| 2 | פרוטוקול הערכה ברמת הטקסט להתערבות המשמרת מסגור פוליטי, עם audit של drift ובקרת paraphrase | בינוני; לא validator או TST חדש | תשתית ותיעוד קיימים, אך אדם עדיין לא אימת את 30 הזוגות | בינונית–גבוהה; צריך שני מסמנים/הכרעה במחלוקת |
| 3 | augmentation סגנוני משפר generalization לכותבים חדשים מעבר לפרפרזה ולבקרת תקציב | מוגבל כעיקרון מול CATO; עשוי להיות תרומה תחומית אם יוכח | כרגע חלש: ההתערבויות הקודמות לא הראו תועלת יציבה | בינונית–נמוכה במאגר הנוכחי; אין להבטיח תוצאה חיובית |

הניסוח המומלץ כיום הוא 1, בשילוב 2 כרכיב מתודולוגי. 3 היא השערה לניסוי, לא מסקנת התזה. אין צורך בתוצאה חיובית כדי להציג מחקר אמפירי שימושי, אם הגדרת המשימה, הבקרות והמגבלות ניתנות להגנה.

[מטריצת ראיות](EVIDENCE_MATRIX_HE.md) · [פיילוט רגישות ישיר](STYLE_SENSITIVITY_PILOT_HE.md)

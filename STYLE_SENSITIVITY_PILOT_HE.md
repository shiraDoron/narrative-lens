# פיילוט רגישות סגנונית של Narrative Classifier קפוא

2026-11-09. **הבדיקה בוצעה בפועל**: 90 תחזיות על 30 מקורות train בשלושה תנאים. אין אימון חדש ואין תחזיות על validation/test.

## התאמת המודל והגבלת ההסקה

נבחר מראש seed42 של `full_original_baseline_Original` מהניסוי עם מחברים מזוהים, לא לפי תוצאותיו. הראש הקיים אומן בעבר על 105 מקורות Original עם תוויות טקסט אוטומטיות Left/Right ונבחר בעבר על 43 מקורות validation. לכל 30 ה־IDs יש התאמה מדויקת למקור, לתווית ולחלוקת train. כל 30 המקורות **נראו באימון הראש**. זו בדיקת רגישות במשקולות קבועות על training sources, ואינה הערכה על held-out sources או unseen authors.

המודל כולל MiniLM קפוא מהמשקולות המקוריות ב־`models/best_model_sbert_only.pth`, וראש קפוא 384→128→7. סדר שבע התוויות נבדק מול config ומקור האימון; נשמר softmax מלא על שבע יחידות, בלי הגבלה או renormalization לשתי יחידות. התאמת ה־ontology כאן עדיפה על החלת checkpoint של חשבונות באופן עיוור, אבל משימה עם שתי תוויות פעילות אינה רפליקציה של שבעה נרטיבים עשירים.

## פרוטוקול

- כל 30 המקורות, ללא סינון לפי guards, reviewer judgments או הצלחת תחזית.
- אותם IDs ואותו encoder/head: Original, ChatGPT Style Rewrite, וה־Paraphrase שכבר נשמר בחבילת המקורות. לא נוצר טקסט חדש.
- מצב eval, CPU, ללא gradients/fit/optimizer; אותו סדר תוויות. SHA-256 של המשקולות, המקורות והקוד נשמר לפני inference ונבדק אחריו.
- פרוטוקול נכתב לפני שמירת תוצאות. ניסיון ראשון לא הצליח לשמור קבצים לאחר שתיקיית העבודה הוסרה בשינוי מקביל ברפו; השחזור השתמש באותה בחירת seed/model/arms, ללא בחירה לפי מדדים. אין תוצאות מספריות שמורות מהניסיון הכושל.
- Accuracy ו־Macro-F1 **לא חושבו**: תוויות המקור הן machine proposals, לא human-gold. גם סיווג נכון על מקור שנראה באימון לא יהיה תוצאת generalization.
- flip = שינוי argmax; TV = חצי סכום הפרשים מוחלטים בווקטור ההסתברות; JS בנאטים. confidence הוא max-softmax לא מכויל; delta אינו שינוי ודאות אנושי.
- CI תיאורי: 2,000 דגימות bootstrap של תשעת הכותבים, seed20261109. מדגם מכוון קטן אינו מייצג אוכלוסייה; אין מבחן superiority או causal effect.

## תוצאות

| תנאי מול Original | flips | TV ממוצע | JS ממוצע | שינוי בביטחון המרבי | שינוי בהסתברות התווית המקורית |
|---|---:|---:|---:|---:|---:|
| ChatGPT | 1/30 (3.33%) | 0.018185 | 0.000492 | -0.889pp | -0.938pp |
| Paraphrase | 1/30 (3.33%) | 0.018299 | 0.000632 | -0.503pp | -0.524pp |

בשני התנאים flip rate=3.33%; רווח ה־bootstrap התיאורי הוא 0%–10% לכל תנאי. ה־flips התרחשו ב־IDs שונים: 28 זוגות לא שינו תווית בשום זרוע, זוג אחד רק ב־ChatGPT וזוג אחד רק בפרפרזה. אין בסיס להכריז על שקילות או היעדר השפעה רק משום שהספירה זהה.

עוצמת הבקרה אינה מותאמת: word_edit_fraction ממוצע ChatGPT=0.2780, Paraphrase=0.1739. זהו 1−SequenceMatcher, לא שיעור החלפות מילולי. תכונות ו־drift עשויים להשתנות אחרת בכל זרוע. פרפרזה היא בקרה לא מושלמת, ולא placebo סגנוני טהור.

ב־Paraphrase של `0105f26ef9f1` נשמר גם פתיח המכונה `Sure, here's the paraphrased version...`, כפי שהיה בתוצר המקורי. אין להסירו בדיעבד; נוכחותו מדגימה שבקרת הפרפרזה כוללת גם artifacts שאינם style נקי. השוואת עוצמת עריכה ממוצעת אינה מאזנת semantic drift או artifacts לפי ID.

## מקרים וגבול החלטה

- `creators:114783`, ChatGPT: Left-wing→Right-wing; Original P(Right)=0.460844, P(Left)=0.467845; לאחר השכתוב P(Right)=0.469970, P(Left)=0.455250. אלה תחזיות מודל, לא תיקון/קלקול מול אמת אנושית.
- `creators:116358`, Paraphrase: Right-wing→Left-wing; Original P(Right)=0.456890, P(Left)=0.431678; לאחר השכתוב P(Right)=0.433476, P(Left)=0.439915. אלה תחזיות מודל, לא תיקון/קלקול מול אמת אנושית.

ההחלפות תואמות תזוזה קטנה ליד גבול החלטה. אין דרך לייחס אותן לסגנון בלבד: paraphrase שונה בעוצמתו, המקורות נראו באימון, והשתמרות ודאות/עוצמה אינה מוכחת אנושית. גם המקור עשוי להיות מסווג לא נכון.

## ניתוח כל 30 ה־IDs

O/C/P הם Original/ChatGPT/Paraphrase. שורת ID אינה מוצאת מהניתוח בגלל review או guard.

| ID | O | C | P | flip C/P | TV C | TV P |
|---|---|---|---|---|---:|---:|
| creators:0105f26ef9f1 | Left-wing | Left-wing | Left-wing | 0/0 | 0.00779 | 0.09869 |
| creators:421024 | Left-wing | Left-wing | Left-wing | 0/0 | 0.01343 | 0.03414 |
| creators:422329 | Right-wing | Right-wing | Right-wing | 0/0 | 0.01255 | 0.01756 |
| creators:417181 | Left-wing | Left-wing | Left-wing | 0/0 | 0.02311 | 0.03868 |
| creators:120177 | Right-wing | Right-wing | Right-wing | 0/0 | 0.03026 | 0.00089 |
| creators:212505 | Right-wing | Right-wing | Right-wing | 0/0 | 0.02262 | 0.04823 |
| creators:421951 | Left-wing | Left-wing | Left-wing | 0/0 | 0.02711 | 0.00427 |
| creators:422331 | Left-wing | Left-wing | Left-wing | 0/0 | 0.03183 | 0.00134 |
| creators:120669 | Left-wing | Left-wing | Left-wing | 0/0 | 0.03963 | 0.01197 |
| creators:216128 | Right-wing | Right-wing | Right-wing | 0/0 | 0.01271 | 0.00360 |
| creators:421279 | Left-wing | Left-wing | Left-wing | 0/0 | 0.02581 | 0.00000 |
| creators:419062 | Left-wing | Left-wing | Left-wing | 0/0 | 0.01799 | 0.00231 |
| creators:295188 | Left-wing | Left-wing | Left-wing | 0/0 | 0.00431 | 0.00311 |
| creators:423315 | Left-wing | Left-wing | Left-wing | 0/0 | 0.02708 | 0.00998 |
| creators:422146 | Left-wing | Left-wing | Left-wing | 0/0 | 0.00361 | 0.00937 |
| creators:421853 | Right-wing | Right-wing | Right-wing | 0/0 | 0.02379 | 0.01014 |
| creators:418620 | Left-wing | Left-wing | Left-wing | 0/0 | 0.00831 | 0.01223 |
| creators:114783 | Left-wing | Right-wing | Left-wing | 1/0 | 0.01260 | 0.01276 |
| creators:224770 | Right-wing | Right-wing | Right-wing | 0/0 | 0.01139 | 0.02725 |
| creators:8b0d99b23d03 | Left-wing | Left-wing | Left-wing | 0/0 | 0.01043 | 0.00210 |
| creators:97c9d6b9ac1b | Left-wing | Left-wing | Left-wing | 0/0 | 0.01112 | 0.01948 |
| creators:423545 | Left-wing | Left-wing | Left-wing | 0/0 | 0.01862 | 0.01101 |
| creators:298495 | Left-wing | Left-wing | Left-wing | 0/0 | 0.00931 | 0.02788 |
| creators:418904 | Left-wing | Left-wing | Left-wing | 0/0 | 0.00756 | 0.00923 |
| creators:2e34435c6ccf | Left-wing | Left-wing | Left-wing | 0/0 | 0.03229 | 0.02918 |
| creators:459e183c1d0d | Right-wing | Right-wing | Right-wing | 0/0 | 0.00353 | 0.02791 |
| creators:416436 | Left-wing | Left-wing | Left-wing | 0/0 | 0.01796 | 0.02481 |
| creators:116358 | Right-wing | Right-wing | Left-wing | 0/1 | 0.06417 | 0.02341 |
| creators:218236 | Right-wing | Right-wing | Right-wing | 0/0 | 0.00733 | 0.00570 |
| creators:418827 | Left-wing | Left-wing | Left-wing | 0/0 | 0.00731 | 0.02174 |

## מה מוסיף הפיילוט ומה אינו מוכיח

קיימת כבר בדיקת fixed-classifier היסטורית על 38 דוגמאות test בדוח byline. היא לא הורצה מחדש. הפיילוט הנוכחי מוסיף את 30 שכתובי ChatGPT החדשים יותר, על train בלבד; אין להשוות שיעורי flips משני המדגמים כאפקט של generator.

**מסקנה:** המסווג הקפוא רגיש מעט לשכתובים האלה; לא נצפה עודף flips ב־ChatGPT לעומת פרפרזה. אין כאן הוכחה לתלות בסגנון מחבר, להסרת shortcut, לשיפור accuracy או לשיפור generalization. היעדר עודף flips אינו הוכחת חסינות.

## הניסוי המכריע הבא — מתוכנן בלבד

ראשית להגדיר text-level narrative/stance gold ולהשלים Human Validation עצמאי לכל 30, עם הכרעה ב־quantifiers/certainty/intensity. בהמשך: מקורות development שלא נראו במודל, כמה כותבים בכל תווית, בקרת נושא/אירוע/תקופה, ואותם IDs ב־Original/Formatting/Paraphrase/Style. לקבוע מטריקות וכלל קבלה לפני תוצאות ולדווח all-attempted לצד accepted, בלי לבחור רק clean examples.

לאחר מעבר שערי המדידה ורק באישור ניסוי אימון נפרד: Original מול חזרה/תקציב אימון מותאם, augmentation פרפרזה ו־augmentation style, הערכה על **Original של כותבים חדשים** כיעד ראשי. לא להחליף בו־זמנית train וגם test כתנאי ראשי. לקבע encoder/תקציב/seeds/IDs; להוסיף worst-author ו־Macro-F1 לפי gold, רווחי סמך לפי כותב, וניתוח coverage. ה־holdout ההיסטורי כבר נבחן במספר מחקרים מקומיים; אינו confirmation חדש. ייתכן צורך בכותבים חדשים באמת.

## שחזור ותוצרים

[קוד/פרוטוקול/תוצאות גולמיות](artifacts/experiments/research_refocus_20261109/REPRODUCTION.md): 90 וקטורי הסתברות, 60 מעברים, 30 השוואות מלאות, hashes ובדיקות. לא נשמרו משקולות חדשות, caches או logs.

[Evidence Matrix](EVIDENCE_MATRIX_HE.md) · [פער מחקרי](RESEARCH_GAP_AND_NOVELTY_HE.md)

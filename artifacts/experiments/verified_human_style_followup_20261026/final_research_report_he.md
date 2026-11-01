# ניסוי המשך: סגנון כותב וזיהוי נרטיבים



## 1. מה בוצע

נאספו 456 קטעים ממאמרי דעה חתומים אישית, מתוך 19 כותבים. נשמרו קישור, תאריך, חתימה, ביוגרפיה ותצלום מקור. חתימה מאמתת ייחוס פומבי לאדם, אך אינה מוכיחה שלא הייתה עזרה בעריכה או כתיבת צללים.

לאחר הסרת פרסומים חוזרים נשמרו 429 קטעים ייחודיים לתיוג. מתוכם 203 סומנו לא ברורים; 218 קטעים בעלי הצעת תיוג Right-wing/Left-wing ברמת ביטחון 2–3 נכנסו לשכתובים. יתר התוויות לא הומרו לאחת משתי הקטגוריות.

זהו ניסוי מצומצם בשני נרטיבים: Right-wing ו־Left-wing. אין כאן כיסוי מספק לכל שבעת הנרטיבים המקוריים. שני הצדדים נלקחו מאותו מפרסם כדי לצמצם ערבוב בין נרטיב לבין אתר המקור.

בוצע תיוג עיוור לפי הטקסט בידי עוזר השיחה, ובנפרד הערכת מודל NLI. ההסכמה: 58.3%; Cohen κ=0.359. אלה שני מעריכים אוטומטיים, לא שני מתייגים אנושיים. ה־NLI אינו משנה את תוויות העוזר. לא בוצע אימות אנושי. תוויות החשבון/הקטגוריה באתר לא שימשו כתוויות אמת. ניסיון מוקדם של המודל המקומי נפסל אחרי בדיקת איכות, לפני תוצאות מסווג הנרטיבים.

לאחר סינון כל ארבע הזרועות נותרו 113 רשומות זהות להשוואה: {'train': 54, 'test': 38, 'val': 21}. אומנו ראשים חדשים באותה ארכיטקטורה בחמישה seeds עם אותו תקציב אימון; המודל המקורי ותוצרי הפיילוט לא שונו.

## 2. מה התקבל



| אימון ובדיקה באותו תנאי | Macro-F1 בשתי הקטגוריות, ממוצע ± סטיית תקן | Accuracy |
|---|---:|---:|
| Original | 0.5318 ± 0.0302 | 0.6053 |
| Formatting | 0.5318 ± 0.0302 | 0.6053 |
| Paraphrase | 0.5903 ± 0.0549 | 0.6368 |
| Normalized | 0.5437 ± 0.0293 | 0.6158 |



הפרש Normalized פחות Paraphrase: -0.0465; יתרון ב־0/5 seeds. ראו paired_seed_comparisons.csv ורווח סמך bootstrap לפי כותבי test, ולא לפי דוגמאות עצמאיות לכאורה.

המסווג שומר על שבע יחידות הפלט המקוריות. המדד המרכזי מחושב על שתי הקטגוריות הפעילות; נשמר גם Macro-F1 על שבע היחידות כדי למנוע בלבול עם מדדי הפיילוט.

## 3. מה ניתן להסיק

אפשר לתאר הבדלים בין תנאי השכתוב במדגם המסוים וביחס לתוויות המכונה, ולבדוק האם מידע שמאפשר זיהוי כותב נשאר ב־embeddings ובמאפייני סגנון מפורשים. תחזית שהשתנתה לאחר שכתוב שעבר סינון אוטומטי היא רגישות לשכתוב; אינה לבדה הוכחה לסגנון כגורם סיבתי.

## 4. מה לא ניתן להסיק

אין כרגע תמיכה מבוססת בהשערה לפי קריטריון ההצלחה המלא. גם יתרון מספרי, אם נמצא, אינו מספיק ללא אימות אנושי עצמאי של התוויות ושל שימור stance/framing. גם הסכמה בין מעריכים אוטומטיים עלולה להיות הסכמה על טעות. אין להכליל את התוצאה לשבעה נרטיבים או לכל כותבי הרשת.

## 5. מגבלות

ייחוס הכותב נסמך על חתימת המפרסם, לא הוכחה פורנזית. הקטעים הם חלקי מאמרים, ולכן ייתכן שחסר הקשר. תאריך המקור הוא תאריך הפרסום בעמוד, ולא בהכרח תאריך הכתיבה המקורית של טור שפורסם שוב. סינון אוטומטי עלול להחמיץ שינויי סוכנות, אירוניה, תחולת שלילה ומסגור. חלק ממאפייני הסגנון עצמם נושאים עמדה ומסגור, ולכן שימורם מגביל את עוצמת הנרמול. המדגם לאחר הסינון עשוי להיות קטן או מוטה; מספר הכותבים ב־test מוגבל. ייתכן בלבול בין כותב, נושא ותקופה גם באותו מפרסם. ירידה ב־author probe אינה מוכיחה הסרה של סגנון בלבד. NLI שימש גם להערכת תוויות נפרדת וגם לסינון שכתובים; ההערכה הנוספת אינה תווית האמת. הטקסונומיה הקיימת היא של מסגור פוליטי; Right-wing ו־Left-wing אינם מדד כללי להימצאות סיפור נרטיבי. לא נערך ניסוי LoRA/DoRA.

## 6. Verdict

- Generalization: השינוי המדוד של Normalized לעומת Original הוא +0.0119; לעומת Paraphrase הוא -0.0465, ביחס לתוויות מכונה בלבד.

- רגישות: נצפו שינויים בתחזיות לאחר שכתוב שעבר סינון; טרם הוכח שהגורם הוא סגנון בלבד.

- מידע על הכותב: לא נמצאה ירידה עקבית בכל המדדים ובשני סוגי הייצוג לעומת Original וגם Paraphrase. כל probe אומן ונבדק מחדש באותו תנאי. המספרים המלאים ב־author_probe_summary.csv.

- מקור הבעיה: לא ניתן להכריע בין גודל הדאטה, איכות השכתוב וההשערה עצמה ללא השלמת בדיקה אנושית. לא נכון לייחס תוצאה שלילית אוטומטית לגודל המדגם.

- LoRA/DoRA: אין הצדקה להתקדם כרגע. גם לא הוכח ש־prompting מספיק. השלב הבא הוא אימות אנושי עיוור והרחבת כיסוי הכותבים/הנרטיבים, ולא החלפת שיטת אימון.



כל הקביעות על זהות/חתימה מתועדות ב־author_registry.json וב־collected_texts.csv עם קישורי מקור. לא הוסקו שפת אם או מחנה פוליטי של אדם מהביוגרפיה.

## פירוט שיעזור לפרש את התוצאה

סיכום סינון השכתובים:

| condition | n | passed | pass_rate | changed_rate |
| --- | --- | --- | --- | --- |
| Concise | 32 | 26 | 0.8125 | 0.3125 |
| Conversational | 32 | 31 | 0.9688 | 0.1875 |
| Elaborate | 32 | 31 | 0.9688 | 0.2812 |
| Formal | 32 | 30 | 0.9375 | 0.4062 |
| Formatting | 218 | 218 | 1.0000 | 0.0000 |
| Normalized | 218 | 188 | 0.8624 | 0.4128 |
| Paraphrase | 218 | 120 | 0.5505 | 0.8119 |

בדיקות כיסוי לאחר הסינון:

| split | narrative | n_texts | n_authors | largest_author_fraction | passed |
| --- | --- | --- | --- | --- | --- |
| train | Right-wing | 23 | 5 | 0.3043 | True |
| train | Left-wing | 31 | 5 | 0.4194 | True |
| val | Right-wing | 11 | 3 | 0.4545 | True |
| val | Left-wing | 10 | 2 | 0.6000 | True |
| test | Right-wing | 17 | 3 | 0.5882 | True |
| test | Left-wing | 21 | 4 | 0.3333 | True |

יחס גודל המדגם המסונן לפיילוט הקודם (94 רשומות): 1.20. זהו יחס מספרי בלבד; המדגמים, הנרטיבים ויחידות הכותב שונים, ולכן אין להשוות את ציוני ה־F1 של שני המחקרים כאילו היו אותה משימה.

הפרשי probe מול שני תנאי הביקורת:

| representation | normalized_minus_original_accuracy | normalized_minus_paraphrase_accuracy | normalized_minus_original_macro_f1 | normalized_minus_paraphrase_macro_f1 |
| --- | --- | --- | --- | --- |
| embedding | 0.0000 | -0.0308 | -0.0048 | -0.0185 |
| explicit_style | -0.0154 | 0.0077 | -0.0278 | -0.0017 |

רווחי סמך תיאוריים להפרשי accuracy ב־probe, עם דגימה מחדש לפי כותב:

| scope | representation | comparison | accuracy_difference | ci95_low | ci95_high | n_author_clusters | bootstrap_replicates | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_writers | embedding | Normalized-Original | 0.0000 | -0.0231 | 0.0240 | 11 | 1000 | Exploratory paired author-cluster accuracy interval, equal weight per refitted probe seed; not independent human samples. |
| all_writers | embedding | Normalized-Paraphrase | -0.0308 | -0.0819 | 0.0000 | 11 | 1000 | Exploratory paired author-cluster accuracy interval, equal weight per refitted probe seed; not independent human samples. |
| all_writers | explicit_style | Normalized-Original | -0.0154 | -0.0720 | 0.0348 | 11 | 1000 | Exploratory paired author-cluster accuracy interval, equal weight per refitted probe seed; not independent human samples. |
| all_writers | explicit_style | Normalized-Paraphrase | 0.0077 | -0.0320 | 0.0462 | 11 | 1000 | Exploratory paired author-cluster accuracy interval, equal weight per refitted probe seed; not independent human samples. |

ציוני זיהוי כותב מוחלטים (ממוצע וסטיית תקן בחמש חלוקות probe):

| scope | condition | representation | accuracy_mean | accuracy_std | macro_f1_mean | macro_f1_std | n_authors | n_test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_writers | Normalized | embedding | 0.3846 | 0.0608 | 0.3104 | 0.0821 | 11 | 26.0000 |
| all_writers | Normalized | explicit_style | 0.2154 | 0.1039 | 0.1476 | 0.0829 | 11 | 26.0000 |
| all_writers | Original | embedding | 0.3846 | 0.0769 | 0.3153 | 0.0762 | 11 | 26.0000 |
| all_writers | Original | explicit_style | 0.2308 | 0.0720 | 0.1754 | 0.0609 | 11 | 26.0000 |
| all_writers | Paraphrase | embedding | 0.4154 | 0.0788 | 0.3289 | 0.0988 | 11 | 26.0000 |
| all_writers | Paraphrase | explicit_style | 0.2077 | 0.0699 | 0.1494 | 0.0518 | 11 | 26.0000 |

סיכום שינויי תחזיות במסווג קבוע:

| condition | label_flip_rate | correct_to_incorrect | incorrect_to_correct | true_probability_delta |
| --- | --- | --- | --- | --- |
| Formatting | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Normalized | 0.0211 | 0.0000 | 0.8000 | 0.0019 |
| Original | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Paraphrase | 0.0263 | 0.0000 | 1.0000 | 0.0019 |

בנפרד נשמר ב־fixed_full_original_summary.csv מסווג ה־Original של ה־baseline המלא, עם משקולות קבועות, שנבדק על אותן רשומות test מסוננות בכל ארבע הזרועות. זהו גם המסווג ששימש ל־counterfactuals. מסווג ה־Original במדגם האימון המשותף מוצג בנפרד; אין לייחס הבדל בין גדלי מדגמי האימון לשינוי סגנון.

תוצאות הביקורות הסגנוניות (מספר התחזיות כולל חמישה seeds לכל טקסט):

| condition | n_predictions | n_sources | label_flip_rate | correct_to_incorrect | incorrect_to_correct | confidence_delta |
| --- | --- | --- | --- | --- | --- | --- |
| Concise | 75 | 15 | 0.0000 | 0 | 0 | 0.0004 |
| Conversational | 75 | 15 | 0.0000 | 0 | 0 | -0.0007 |
| Elaborate | 75 | 15 | 0.0000 | 0 | 0 | -0.0012 |
| Formal | 75 | 15 | 0.0000 | 0 | 0 | -0.0029 |
| Paraphrase | 75 | 15 | 0.0133 | 0 | 1 | 0.0010 |

עקביות בין ארבעת הסגנונות ויציבות ביחס לתחזית המקור:

| seed | n_sources | narrative_consistency_rate | original_prediction_invariance_rate |
| --- | --- | --- | --- |
| 7 | 15 | 1.0000 | 1.0000 |
| 42 | 15 | 1.0000 | 1.0000 |
| 123 | 15 | 1.0000 | 1.0000 |
| 2026 | 15 | 1.0000 | 1.0000 |
| 31415 | 15 | 1.0000 | 1.0000 |

נשמרו גם ניתוח רגישות בתוויות confidence=3 בלבד, ביצועים לכל כותב, הפרשים מזווגים בכל seed ו־bootstrap לפי כותבי test. אין להתייחס לחמשת ה־seeds כחמישה מדגמים אנושיים בלתי תלויים.

נשמר גם ניתוח רגישות המוגבל לרשומות שבהן גם Paraphrase וגם Normalized שינו בפועל את רצף המילים. העתקת המקור אינה הוכחה לשימור נרטיב תחת שינוי סגנון; ראו intervention_strength_summary.csv ו־counterfactual_cohort_status.json. ניתוחים אלה משתמשים בכל תנאי על אותן רשומות בתוך כל מדגם, ומסומנים בנפרד מהניתוח המרכזי.

README.md מפרט שחזור. human_annotation_blind.csv ו־rewrite_human_review.csv מוכנים לבודקים אנושיים; המפתח נשמר בנפרד.

## נספח מקורות זיהוי הכותבים

הקישורים הבאים משמשים לאימות זהות וייחוס בלבד. אין להסיק מהם שפת אם, מחנה פוליטי או תפקיד נוכחי. קישורי כל המאמרים ותאריכיהם ב־collected_texts.csv; ראיות הביוגרפיה ב־identity_evidence.csv ובדיקת החתימות ב־full_byline_audit.csv.

| כותב ומקור ביוגרפי | קטעים ייחודיים שתויגו | קטעים לפני סינון שכתובים | קטעים במדגם המשותף | חלוקה |
| --- | --- | --- | --- | --- |
| [Ben Shapiro](https://www.creators.com/author/ben-shapiro) | 20 | 7 | 3 | test |
| [David Harsanyi](https://www.creators.com/author/david-harsanyi) | 24 | 13 | 4 | train |
| [Stephen Moore](https://www.creators.com/author/stephen-moore) | 24 | 14 | 10 | test |
| [Dennis Prager](https://www.creators.com/author/dennis-prager) | 24 | 12 | 5 | test |
| [Star Parker](https://www.creators.com/author/star-parker) | 24 | 5 | 2 | val |
| [Jim Hightower](https://www.creators.com/author/jim-hightower) | 24 | 21 | 13 | train |
| [Froma Harrop](https://www.creators.com/author/froma-harrop) | 24 | 10 | 7 | train |
| [Debra J. Saunders](https://www.creators.com/author/debra-j-saunders) | 24 | 11 | 5 | val |
| [Joe Conason](https://www.creators.com/author/joe-conason) | 16 | 11 | 7 | test |
| [Susan Estrich](https://www.creators.com/author/susan-estrich) | 24 | 10 | 6 | val |
| [Marc Dion](https://www.creators.com/author/marc-dion) | 24 | 5 | 2 | train |
| [Jamie Stiehm](https://www.creators.com/author/jamie-stiehm) | 24 | 17 | 10 | train |
| [Veronique de Rugy](https://www.creators.com/author/veronique-de-rugy) | 19 | 6 | 3 | train |
| [Chuck Norris](https://www.creators.com/author/chuck-norris) | 23 | 14 | 7 | train |
| [Lawrence Kudlow](https://www.creators.com/author/lawrence-kudlow) | 20 | 13 | 7 | train |
| [Connie Schultz](https://www.creators.com/author/connie-schultz) | 20 | 6 | 1 | train |
| [Robert Scheer](https://www.creators.com/author/robert-scheer) | 24 | 14 | 7 | test |
| [Mona Charen](https://www.creators.com/author/mona-charen) | 24 | 17 | 8 | val |
| [Jeff Robbins](https://www.creators.com/author/jeff-robbins-talent) | 23 | 12 | 6 | test |


<!-- RESULTS_DIGEST -->
# תמצית מספרית ודיון ממוקד

**לא התקבלה כרגע תמיכה מספקת בהשערה ש־Style Normalization מסיר קיצור דרך מזיק של Author Style ומשפר הכללה מעבר לפרפרזה.** לא הוכח שההשערה שגויה; תנאי ההצלחה לא התקיימו יחד.

זהו ניסוי ממוחשב בשני נרטיבים בלבד, Right-wing ו־Left-wing, על מאמרים בעלי חתימה אישית מאותו מפרסם. הייחוס הפומבי של 19 הכותבים מתועד; אין בכך הוכחה לכתיבה ללא עזרה. הצעות התיוג הן ברמת הטקסט ואינן תוויות אמת שאומתו בידי אדם.

נאספו 456 רשומות, מהן 429 קטעים ייחודיים. 218 קטעים קיבלו הצעת תיוג מתאימה לשתי הקטגוריות; נוצרו 436 שכתובים עיקריים ו־128 גרסאות counterfactual. לאחר הסינון המשותף נותרו 113 קטעים: 54 באימון, 21 ב־validation ו־38 ב־test. יש 6 כותבי test שאינם ב־train או validation, ולכל נרטיב נשארו כמה כותבים בכל חלוקה. ההתרחבות מול 94 בפיילוט היא כ־20% בלבד; היעד למדגם מסונן גדול משמעותית עדיין לא הושג.

## ההשוואה המרכזית: אותן רשומות, חמישה seeds

הטבלה היא Train condition → Test same condition. Macro-F1 מחושב על שתי הקטגוריות הפעילות, עם אותה ארכיטקטורת שבע יחידות פלט של הפרויקט. כל המדדים נמדדו מול הצעות התיוג האוטומטיות.

| train_condition | macro_f1_mean | macro_f1_std | accuracy_mean |
| --- | --- | --- | --- |
| Original | 0.5318 | 0.0302 | 0.6053 |
| Formatting | 0.5318 | 0.0302 | 0.6053 |
| Paraphrase | 0.5903 | 0.0549 | 0.6368 |
| Normalized | 0.5437 | 0.0293 | 0.6158 |

Normalized נמוך מ־Paraphrase ב־0.0465 בממוצע: ארבע ריצות נמוכות ואחת שווה. רווח הסמך התיאורי לפי ששת כותבי ה־test להפרש N−P הוא [-0.0875, 0.0267]; הוא כולל אפס, ולכן אין כאן טענה לעליונות מובהקת של אחד התנאים באוכלוסייה. יש יתרון מספרי קטן של N מול O, אך הוא קטן מהיתרון של פרפרזה רגילה.

כאשר בודקים את כל המודלים על טקסטי Original ללא נרמול ב־test, אימון על N נותן Macro-F1=0.5095, לעומת 0.5318 באימון על O ו־0.5543 באימון על P. לכן לא הודגם שיפור של המסווג על טקסטים מקוריים מכותבים חדשים בעקבות אימון על N בלבד.

## אין לבלבל בין גדלי מדגם שונים

ב־baseline המקורי המלא אומן הראש על 105 קטעי Original, נבחר על 43 קטעי validation ונבדק על 70 קטעים: Macro-F1=0.6578 ± 0.0300, Accuracy=0.6800. ההשוואה המרכזית לעיל מאמנת על 54 קטעים ובודקת על 38; אין לייחס את פער הציונים בין המדגמים לסגנון.

כדי למדוד רגישות במשקולות קבועות נשמר גם ראש ה־baseline המלא ונבדק על אותן 38 רשומות בכל ארבע הזרועות. הטבלה הבאה מציגה ממוצעים בין seeds; עמודות המעברים הן מספר מעברים ממוצע בכל ריצה:

| condition | macro_f1 | accuracy | label_flip_rate | correct_to_incorrect | incorrect_to_correct |
| --- | --- | --- | --- | --- | --- |
| Formatting | 0.6859 | 0.7105 | 0.0000 | 0.0000 | 0.0000 |
| Normalized | 0.6921 | 0.7158 | 0.0158 | 0.2000 | 0.4000 |
| Original | 0.6859 | 0.7105 | 0.0000 | 0.0000 | 0.0000 |
| Paraphrase | 0.7037 | 0.7263 | 0.0368 | 0.4000 | 1.0000 |

## זיהוי כותב וביקורות סגנון

ב־probe הגלובלי, עם 11 כותבים שנשארו להם מספיק קטעים, דיוק זיהוי הכותב מתוך embeddings נשאר 38.46% גם ב־Original וגם ב־Normalized. במאפייני הסגנון המפורשים ירד הדיוק מ־23.08% ל־21.54%; ב־Paraphrase הוא 20.77%. זו אינה ירידה עקבית וספציפית לנרמול מול שתי הביקורות ובשני הייצוגים. כל מסווג כותב אומן ונבדק מחדש באותו תנאי, והחלוקה שלו נפרדת ממשימת הכללת הנרטיב לכותבים חדשים.

ב־counterfactuals נבחרו 32 קטעים. 15 עברו את הסינון המשותף לכל הסגנונות ולזרועות העיקריות. בארבעת סגנונות היעד התקבלו 0 החלפות תווית מתוך 300 תחזיות (15 קטעים × 4 סגנונות × 5 seeds). בפרפרזה הרגילה הייתה החלפה אחת מתוך 75 תחזיות, מ־incorrect ל־correct. **רק שלושה קטעים השתנו בפועל בכל ארבעת הסגנונות**; גם בהם לא היו החלפות. זהו מדגם קטן מדי להוכחת חסינות לסגנון. שינויים קטנים בתחזיות לאחר שכתוב כללי אינם לבדם ראיה ל־Author Style shortcut.

## האם השכתוב באמת התערב בסגנון?

בכלל השכתובים, 99/218 גרסאות Normalized ו־30/218 גרסאות Paraphrase הועתקו ללא שינוי. במדגם המסונן, שיעור ההעתקה ב־Normalized עלה ל־50.4% לעומת 26.5% בפרפרזה. שיעור עריכת הטוקנים הממוצע במדגם זה הוא כ־2.55% ב־N וכ־8.09% ב־P. לכן איננו מניחים שעצם השם Normalized מעיד על הסרת סגנון; עוצמת ההתערבות מוגבלת והסינון מעשיר טקסטים שהשתנו מעט.

נפסלו 98/218 פרפרזות (45.0%) ו־30/218 נרמולים (13.8%). אלה **פסילות של מסנן אוטומטי**, לא הוכחה שכל שכתוב שנפסל אכן שגוי. מספרי הסיבות חופפים כאשר יש יותר מסיבה אחת לאותה רשומה:

| condition | reason | n |
| --- | --- | --- |
| Normalized | bidirectional_nli | 17 |
| Normalized | quotations | 10 |
| Normalized | negation | 5 |
| Normalized | certainty | 1 |
| Normalized | entities | 1 |
| Normalized | future_tense | 1 |
| Paraphrase | bidirectional_nli | 51 |
| Paraphrase | quotations | 28 |
| Paraphrase | entities | 27 |
| Paraphrase | certainty | 14 |
| Paraphrase | future_tense | 12 |
| Paraphrase | attribution | 11 |
| Paraphrase | negation | 11 |
| Paraphrase | similarity | 6 |
| Paraphrase | framing_anchors | 3 |
| Paraphrase | numbers | 3 |

## ניתוחי רגישות שנקבעו לפני תוצאות המסווג

להלן גם התוצאות שאינן תואמות לחלוטין את הדפוס המרכזי. אין להשוות תנאי ממדגם אחד לתנאי ממדגם אחר כאפקט סגנון; בתוך כל מדגם התנאים משתמשים באותן רשומות.

| cohort | train_condition | macro_f1_mean | macro_f1_std | n |
| --- | --- | --- | --- | --- |
| matched_confidence3 | Formatting | 0.5548 | 0.1234 | 31 |
| matched_confidence3 | Normalized | 0.5518 | 0.1198 | 31 |
| matched_confidence3 | Original | 0.5548 | 0.1234 | 31 |
| matched_confidence3 | Paraphrase | 0.5010 | 0.1102 | 31 |
| matched_nontrivial_rewrites | Formatting | 0.3967 | 0.2473 | 8 |
| matched_nontrivial_rewrites | Normalized | 0.3705 | 0.2265 | 8 |
| matched_nontrivial_rewrites | Original | 0.3967 | 0.2473 | 8 |
| matched_nontrivial_rewrites | Paraphrase | 0.3911 | 0.2517 | 8 |

ב־confidence=3 בלבד, N עדיף מספרית על P, אך אינו משפר את O. כלומר, הדפוס משתנה עם בחירת התוויות והמדגם, ואינו יתרון יציב של נרמול. במדגם שבו שני השכתובים שינו את רצף המילים נשארו רק 8 דוגמאות test וסטיות התקן גדולות מאוד; N אינו עדיף על P או O.

## Verdict

- **רגישות ל־Author Style:** לא נמצאה ראיה משכנעת לרגישות מזיקה לסגנון בלבד. יש רגישות קטנה לשכתוב כללי, בעוד שבביקורות הסגנון התקבלו אפס flips ומעט מאוד התערבויות לא מועתקות.
- **הסרת מידע על הכותב:** לא הודגמה ירידה עקבית מול Original וגם מול Paraphrase בשני סוגי הייצוג.
- **הכללה לכותבים חדשים:** יש שיפור מספרי קטן ב־N לעומת O במדגם המרכזי; הוא אינו מבסס יתרון של הסרת סגנון.
- **Normalized מול Paraphrase:** אין יתרון בניתוח המרכזי; P טוב יותר בארבע ריצות ושווה באחת. ניתוח confidence=3 משנה את הדפוס, אך גם בו N אינו עולה על O.
- **גודל דאטה, איכות שכתוב או ההשערה?** לא ניתן לייחס את התוצאה לאחד מהם בוודאות. תועדו התרחבות מדגם צנועה, התערבות סגנונית חלשה בחלק גדול מהטקסטים, ורמת הסכמה לא גבוהה בין מעריכי התוויות (58.3%, κ≈0.36). אין בסיס לדחיית ההשערה באופן כללי.
- **LoRA/DoRA:** אין הצדקה להתקדם כרגע. גם לא הוכח ש־prompting מספיק. נדרשים קודם אימות אנושי עיוור ושכתוב שמייצר שינוי סגנוני אמיתי ושומר משמעות, עמדה ומסגור.

כל הקוד, המקורות, החלוקות, הצעות התיוג, השכתובים, הפסילות, התחזיות, המדדים, רווחי הסמך וששת הגרפים נשמרו בתיקייה זו. תוצרי הפיילוט הקודם, קובצי המקור והמודל המקורי נבדקו ב־SHA-256 ולא שונו. אין טענה להוכחת סיבתיות.


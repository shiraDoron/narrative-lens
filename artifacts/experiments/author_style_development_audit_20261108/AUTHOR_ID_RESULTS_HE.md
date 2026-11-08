# Author-ID — ביקורת הניסוי הקודם ופרוטוקול משופר

## מה היה קודם

30 זוגות מתשעה כותבים, 2–4 טקסטים לכותב. נבחנו חמישה seeds של StratifiedKFold בשני folds; כ־15 טקסטים בלבד בכל fit, כלומר לרוב 1–2 דוגמאות לכותב, מול 66 features. StandardScaler אומן בתוך fold. החלוקות בין Original ל־Rewrite היו זהות, ולכל ID הופרדו fit/dev. בדיקת group/article החדשה לא מצאה siblings דולפים. אין עדות לזליגת אותו זוג בניסוי הקודם.

ההשוואה עם fit נפרד לכל representation הייתה הוגנת כשאלת “האם עדיין אפשר ללמוד לזהות כותב מתוך rewrites”, אך אינה זהה להשפעת rewrite על מסווג Original קבוע. בדיקת המסווג הקבוע נשמרה בנפרד. [הנתונים והקוד הקודמים](../chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPORT_HE.md): matched accuracy 23.3%→22.0%, F1 0.1964→0.1867; fixed-Original accuracy עלה ל־28%. הבסיס האחיד 1/9=11.1%; התפלגות רוב במדגם 13.3%.

אי־היציבות צפויה במדגם זעיר: שינוי בטקסט אחד הוא 3.33pp, לכל מחבר מעט מאוד דוגמאות, המדגם נבחר אבחונית לפי flags קודמים, ו־66 משתנים מתחרים על מעט דוגמאות. זו אינה הוכחה שהסגנון לא השתנה. גם אין להסיק מהממוצע השלילי הקטן שההתערבות הצליחה.

## ניסוי 1: יכולת ללמוד author-ID ממקורות חדשים

202 Originals מ־train בלבד, תשעה כותבים. חמישה folds group-aware לכל אחד מחמישה seeds. Article/near-duplicate groups אינם חוצים fold. ארבע שיטות הוגדרו לפני התוצאות: surface 66; פונקציות מילים ופיסוק ללא raw length; character TF-IDF 3–5; word TF-IDF 1–2 כבקרת תוכן. Logistic Regression C=1 זהה, ללא search, עם vectorizer/scaler מאומנים רק ב־fit.

| method | n | authors | accuracy mean | seed SD | Macro-F1 mean |
| --- | --- | --- | --- | --- | --- |
| surface_66 | 202 | 9 | 29.11% | 2.51pp | 0.2899 |
| function_punctuation | 202 | 9 | 26.44% | 2.17pp | 0.2637 |
| char_tfidf | 202 | 9 | 48.42% | 2.79pp | 0.4318 |
| word_content_control | 202 | 9 | 42.28% | 2.61pp | 0.4036 |

בסיס רוב המותאם בתוך כל fit הגיע ל־10.0% accuracy ו־0.0674 Macro-F1; בסיס אחיד תיאורטי 11.1%. ה־global majority frequency הוא 11.88%, ואינו תחליף ל־fold-fitted baseline. [Baselines](majority_cv_summary.csv). נתוני 202 שונים מה־30 הקודמים, ולכן 48.4% לעומת 23.3% אינם ניסוי שמבודד השפעת algorithm בלבד.

## רגישות לתת־קוהורט

| cohort | n | authors | method | accuracy | Macro-F1 |
| --- | --- | --- | --- | --- | --- |
| train_eligible_narrative | 105 | 9 | surface_66 | 36.57% | 0.2934 |
| train_eligible_narrative | 105 | 9 | function_punctuation | 32.95% | 0.2589 |
| train_eligible_narrative | 105 | 9 | char_tfidf | 31.81% | 0.1325 |
| train_eligible_narrative | 105 | 9 | word_content_control | 44.38% | 0.2691 |
| train_eligible_Left-wing | 55 | 5 | surface_66 | 57.45% | 0.3884 |
| train_eligible_Left-wing | 55 | 5 | function_punctuation | 57.09% | 0.4080 |
| train_eligible_Left-wing | 55 | 5 | char_tfidf | 58.55% | 0.2776 |
| train_eligible_Left-wing | 55 | 5 | word_content_control | 59.27% | 0.2781 |
| train_eligible_Right-wing | 50 | 5 | surface_66 | 38.40% | 0.3296 |
| train_eligible_Right-wing | 50 | 5 | function_punctuation | 41.60% | 0.3528 |
| train_eligible_Right-wing | 50 | 5 | char_tfidf | 54.80% | 0.3538 |
| train_eligible_Right-wing | 50 | 5 | word_content_control | 54.00% | 0.3581 |

אין לפרש accuracy בלי Macro-F1 ובסיס הרוב: הקוהורט המסונן אינו מאוזן. Within-narrative משתמש בהצעות label בלבד ואינו בקרה מלאה לתוכן; Froma Harrop מופיעה בשני הנרטיבים. תוצאות CV אלה מודדות author predictability, לא השפעת rewrite. Confusion matrices, per-seed scores, fold IDs וכל התחזיות נשמרו ללא models/weights. Seed SD אינו CI ואין להתייחס לחמש חזרות כאל חמישה קורפוסים עצמאיים.

## ניסוי 2: ההשפעה על אותו fitted classifier

לכל שיטה אומן **מסווג אחד על 172 Originals אחרים**; כל 30 המקורות של הזוגות וכל קבוצת source שלהם הוצאו מה־fit. אותו pipeline ממש ניבא את Original ואת Rewrite של כל זוג. ה־evaluation IDs נשארו קבועים בכל השיטות, ללא בחירת clean/accepted examples.

| method | Original accuracy | Rewrite accuracy | Original F1 | Rewrite F1 | delta accuracy | p exact | p Holm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| surface_66 | 46.67% | 33.33% | 0.4413 | 0.2783 | -13.33pp | 0.21875 | 0.65625 |
| function_punctuation | 50.00% | 26.67% | 0.4717 | 0.2083 | -23.33pp | 0.03906 | 0.15625 |
| char_tfidf | 53.33% | 53.33% | 0.4450 | 0.4979 | +0.00pp | 1.00000 | 1.00000 |
| word_content_control | 53.33% | 53.33% | 0.4878 | 0.4960 | +0.00pp | 1.00000 | 1.00000 |

המסווגים הלקסיקליים נשארו ב־53.3% accuracy אחרי השכתוב, אף שחלק מזהויות הטעויות השתנו. Surface יורד 46.7%→33.3%; פונקציות־מילים/פיסוק יורד 50.0%→26.7%. זהו **אות אבחוני תלוי representation**, לא הוכחה להסרת כלל author cues. Feature set מצומצם אינו “pure style”: pronouns/function words עשויים לשאת גם תוכן ועמדה.

ה־p הלא־מתוקן לפונקציות־מילים הוא 0.0391, אבל Holm לארבע ההשוואות הראשיות נותן 0.1563. יתר ה־p המתוקנים ≥0.656. אין תוצאה מובהקת ברמת 0.05 לאחר התיקון שנקבע. Exact McNemar מניח עצמאות זוגות; התלות בכותב היא מגבלה נוספת. ה־bootstrap המאוגד לפי תשעת הכותבים נותן CI לא מתוקן ל־delta accuracy: surface [-31.0, 3.0]pp; function/punctuation [-38.7, -7.1]pp. זהו interval תיאורי ללא התאמת multiplicity ועם מעט clusters, לא דרך לעקוף את תוצאת Holm.

## בדיקות יציבות שנקבעו מראש

| fit pool | method | mean delta, 80% train resampling | negative seeds |
| --- | --- | --- | --- |
| all_train_excluding_pairs | surface_66 | +3.33pp | 1/5 |
| all_train_excluding_pairs | function_punctuation | -7.33pp | 4/5 |
| all_train_excluding_pairs | char_tfidf | -0.67pp | 3/5 |
| all_train_excluding_pairs | word_content_control | -2.67pp | 3/5 |
| eligible_train_excluding_pairs | surface_66 | +6.00pp | 1/5 |
| eligible_train_excluding_pairs | function_punctuation | -2.00pp | 2/5 |
| eligible_train_excluding_pairs | char_tfidf | +0.00pp | 0/5 |
| eligible_train_excluding_pairs | word_content_control | -0.67pp | 3/5 |

הדגימה מחדש משנה רק את 172/75 מקורות האימון, לא את 30 זוגות ההערכה. ב־function/punctuation הירידה נחלשת לממוצע −7.33pp ו־4/5 seeds שליליים ב־pool הגדול. Surface נע בממוצע דווקא +3.33pp. ב־pool המצומצם של 75 eligible Originals התוצאה על כל האימון אף מתהפכת: surface 20%→30%, function/punctuation 16.7%→23.3%. ל־Marc Dion נשאר מקור eligible אחד לאימון; לכן sensitivity זה דל ולא שווה באיכות ל־172. אין לבחור רק את ה־pool/seed המוצלח.

## בקרת שנה משלימה — post-hoc

לאחר גילוי confounding בתאריכים נוספה בדיקה של שישה כותבים שכל מקורות ה־train שלהם משנת 2026. הבחירה מבוססת metadata בלבד, לא על הצלחת שכתוב. 139 Originals ב־CV; 119 מהם ב־fit מול 20 זוגות held-out. כל 30 הזוגות נשארו בניסוי הראשי. זו בדיקת רגישות נוספת, לא תנאי שהוגדר לפני התוצאות הראשיות ולא confirmation או בחירת method.

| method | Original accuracy | Rewrite accuracy | Original F1 | Rewrite F1 |
| --- | --- | --- | --- | --- |
| surface_66 | 40.0% | 35.0% | 0.3730 | 0.3214 |
| function_punctuation | 30.0% | 20.0% | 0.2738 | 0.1713 |
| char_tfidf | 60.0% | 65.0% | 0.5417 | 0.5853 |
| word_content_control | 50.0% | 50.0% | 0.4687 | 0.4556 |

צמצום לשנה אחידה אינו מבטל את author cues: char accuracy עולה 60%→65% בשכתובים; בקרת מילים נשארת 50%. יש ירידה קטנה יותר ב־surface/function probes, אבל n=20 עם שש מחלקות אינו מתן כוח לאישור סיבתי. Topic/event/selection עדיין יכולים לערבב את התוצאה. [Temporal protocol](temporal_control_protocol.json) ו[כל תוצאות CV](temporal_cv_summary.csv) נשמרו; לא שונה הפרוטוקול הראשי לאחר תוצאותיו.

**מסקנה:** הצלחנו לבצע author-ID תקף וחזק יותר כתשתית אבחון, ולהפריד למידה של זהות מהשפעת intervention. תוצאות ההתערבות מעורבות ותלויות ב־feature set ובמקורות האימון. אין כרגע אישור/הפרכה של השערת shortcut, ואין תוצאת Narrative Classifier או test חדש.

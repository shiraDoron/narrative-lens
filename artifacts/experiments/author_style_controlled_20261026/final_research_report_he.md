# ניסוי Author Style: דוח תוצאות בפועל

## תקציר התוצאות

בהשוואת האימון מחדש על אותן רשומות, Original→Original=0.0880, Normalized→Normalized=0.0836, Paraphrase→Paraphrase=0.0733. Normalized−Original=-0.0045; Normalized−Paraphrase=+0.0102. הנרמול היה נמוך מהמקור ב־3 מתוך 3 seeds, וגבוה מפרפרזה ב־2 מתוך 3 seeds.

כאשר טקסטי הבדיקה נשארים Original: Original→Original=0.0880, Paraphrase→Original=0.0830, Normalized→Original=0.0935. זהו שינוי קטן במדגם קטן; לא נקבעה מובהקות, והיתרון האפשרי אינו עקבי בין כל מדדי הביצוע והתנאים.

לאחר סינון נשארו 46 דוגמאות אימון, 24 אימות ו־24 בדיקה, עם ייצוג לא אחיד למחלקות. אין להשוות את ציון המקור בקבוצה זו ישירות ל־baseline המלא: זו קבוצת אימון ובדיקה שונה.

ב־Counterfactual המזווג שעבר סינון בשני השלבים נשארו 4 טקסטי מקור; שיעור flip לפני נרמול=0.0000, ואחריו=0.0000. לא הודגם שיפור ביציבות; המדגם קטן ואינו שולל shortcut שלא הופעל בהתערבות הזו.

מקורות המספרים: [תוצאות לפי תנאי](metrics_aggregated.csv), [הרכב קבוצות האימון והבדיקה](retraining_cohort_status.json), [בדיקת זיהוי כותב](author_probe_aggregated.csv), [עקביות Counterfactual](counterfactual_consistency_summary.csv).

**המסקנה בפיילוט הזה: אין תמיכה מספקת בטענה שנרמול הסגנון מסיר shortcut מזיק ומשפר הכללה.** הירידה בזיהוי כותב במאפייני פני שטח בקבוצה המסוננת זהה לירידה בפרפרזה רגילה, וב־embedding לא נמדדה ירידה. נמצא יתרון ממוצע קטן של Normalized על Paraphrase במבחן N→N מול P→P, אך לא שיפור מול Original→Original. זו אינה הוכחה שאין shortcut: המדגם קטן, הסינון אוטומטי ותוויות המקור אינן gold סמנטי עצמאי.

## 1. מה בוצע

בוצע פיילוט חישובי מקומי: 336 טקסטים שנדגמו מראש, 28 מזהי כותבים/חשבונות, 336 טקסטים לאחר ביקורת דמיון סמנטי של המקור. החלוקה היא 14 חשבונות אימון, 7 חשבונות אימות ו־7 חשבונות בדיקה; 12 טקסטים לכל כותב לפני סינונים, ובכל קבוצת בדיקה כותב אחד מכל נרטיב. נבחרו טקסטים באנגלית באורך 20–65 מילים. זהו תת־מדגם מהדאטה הקיים, ולא הרצה על כל הפרויקט.

נשמרו החלוקה, מזהי הרשומות וחתימות קובצי המקור. בוצעה ביקורת כפילויות כללית לפני הדגימה, וכן בדיקת דמיון סמנטי בין החלוקות לפני אימון וביקורת כפילויות שנוצרו בעקבות שכתוב. קבוצות דומות הוצאו באופן סימטרי. ספי הדמיון הם הגדרה תפעולית; הם אינם הוכחה שאין אף פרפרזה סמויה.

**יחידת הזהות היא חשבון מקור:** ה־split מפריד מזהי חשבונות לאחר איחוד הבדלי אותיות רישיות ו־@. אין בדאטה זיהוי מלא של הכותב האנושי לכל פרסום, ורבים מהחשבונות הם ארגונים. לכן זהו account-disjoint proxy ל־author-disjoint; לא ניתן להבטיח שאותו עורך אנושי לא כתב עבור שני חשבונות.

נעשה שימוש במקודד ובארכיטקטורת SBERT-only הקיימים: MiniLM קפוא, ראש MLP עם 128 יחידות ו־dropout 0.3. ראש הסיווג אומן מחדש על כותבי האימון בלבד. בכל תנאי נשמרו אותם פרמטרים, 20 epochs ושלושה seeds: 42, 7, 123. בחירת checkpoint התבססה רק על Macro-F1 של כותבי האימות. תחזיות ה־checkpoint הישן נשמרו בנפרד כנתון תיאורי שאינו author-disjoint. קובצי המקור והמודל המקורי לא הוחלפו.

נוצרו Original, Formatting באמצעות הפונקציה הקיימת, Paraphrase המשמר סגנון לפי ההנחיה, ו־Normalized לסגנון כתוב אחיד. השכתובים נעשו ב־Qwen2.5-0.5B-Instruct מקומי, בגרסת GGUF Q8_0 רשמית מקובעת, באמצעות llama.cpp ובפענוח דטרמיניסטי. המשקלים מכומתים, וכל הפלטים לניתוח נוצרו באותו מנוע. זהו מודל קטן שנבחר למשאבי CPU; אין כאן API מסחרי או אימון LoRA. שם הכותב ותווית הנרטיב לא נשלחו כמידע נלווה. ישויות שהופיעו בטקסט עצמו נשארו בטקסט.

מקורות הכלים: [כרטיס מודל Qwen הרשמי](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF), [תיעוד שרת llama.cpp](https://github.com/ggml-org/llama.cpp/blob/b11887/tools/server/README.md). גרסאות וחתימות המשקלים והמנוע שנעשה בהם שימוש בפועל מתועדות ב־llama_runtime_manifest.json.

בוצעו סינון באמצעות דמיון MPNet במקודד נפרד ממקודד מסווג הנרטיבים, הסקה דו־כיוונית במודל DeBERTa NLI, חילוץ ישויות ב־BERT NER, ובדיקות שמרניות של מספרים, שלילה, ודאות, ייחוס ומילות מסגור. אין כאן תיוג אנושי עצמאי של שימור עמדה ומסגור; עבר/נפסל פירושו עבר/נפסל בסינון האוטומטי בלבד. לא נבחר שכתוב על סמך תחזית מסווג הנרטיבים.

בוצעו מבחן מסווג קבוע, אימון מחדש בשלוש זרועות ומטריצת בדיקות ביניהן, זיהוי כותב שהותאם מחדש בכל ייצוג, ארבעה יעדי סגנון זהים לכל טקסט בקבוצת הנגד, נרמול נוסף של כל יעד, וניסיון לשינוי עמדה כביקורת חיובית. במטריצת האימון נשמרה אותה קבוצת רשומות בכל התנאים. אם הסינון הסיר מחלקה מאימון/אימות/בדיקה, השוואת שבע המחלקות בקבוצה המסוננת סומנה כבלתי ניתנת לאמידה.

## 2. מה התקבל

Baseline על כותבים שלא נראו: Macro-F1 **0.3934 ± 0.0224**, Accuracy **0.4008 ± 0.0248**. סטיית התקן משקפת שונות בין seeds באותה חלוקת כותבים, ולא אי־ודאות לגבי אוכלוסיית הכותבים.

| Narrative | Recall |
| --- | --- |
| Zionist | 0.5556 |
| Resistance | 0.3333 |
| Western | 0.3611 |
| Russian | 0.0000 |
| Ukrainian | 0.6111 |
| Right-wing | 0.4167 |
| Left-wing | 0.5278 |

### מדוע יש שלושה ציוני Original שונים?

| comparison | train | validation | test | Original Macro-F1 |
| --- | --- | --- | --- | --- |
| Full original baseline | 168 | 84 | 84 | 0.3934 |
| Frozen full-trained model on accepted C/D texts | 168 | 84 | 24 | 0.2189 |
| Matched retraining: same source rows for O/P/N | 46 | 24 | 24 | 0.0880 |

הבדלים בין שורות הטבלה נובעים גם מכמות דוגמאות האימון ומהרכב קבוצת הבדיקה; הם אינם אומדן להשפעת נרמול. את השפעת התנאי משווים בתוך אותה שורה וקבוצה בלבד.

### תקינות השכתובים

| condition | n | accepted | canonical_word_change_fraction | raw_change_fraction | failure_rate |
| --- | --- | --- | --- | --- | --- |
| Concise | 14 | 10 | 0.3571 | 0.8571 | 0.2857 |
| Conversational | 14 | 6 | 0.6429 | 0.8571 | 0.5714 |
| Elaborate | 14 | 7 | 0.6429 | 0.9286 | 0.5000 |
| Formal | 14 | 8 | 0.6429 | 0.9286 | 0.4286 |
| Formatting | 336 | 162 | 0.5298 | 0.8304 | 0.5179 |
| Normalized | 336 | 162 | 0.6042 | 0.9464 | 0.5179 |
| NormalizedConcise | 14 | 10 | 0.5000 | 0.7143 | 0.2857 |
| NormalizedConversational | 14 | 12 | 0.2143 | 0.2857 | 0.1429 |
| NormalizedElaborate | 14 | 11 | 0.3571 | 0.5714 | 0.2143 |
| NormalizedFormal | 14 | 10 | 0.2143 | 0.3571 | 0.2857 |
| Paraphrase | 336 | 119 | 0.8006 | 0.9792 | 0.6458 |
| StanceChanged | 7 | 4 | 0.4286 | 0.8571 | 0.4286 |

canonical_word_change_fraction משווה רצף מילים לאחר הסרת קישורים, אזכורים, אותיות רישיות וסימני פיסוק; raw_change_fraction משווה מחרוזות ללא ניקוי. אף אחד מהמדדים אינו הוכחה לנרמול סגנון מוצלח. גם העתקה של המקור יכולה לעבור סינון משמעות בלי לבצע את ההתערבות הרצויה.

לקבוצה המשותפת שבה Paraphrase ו־Normalized עברו את הסינון ונשמרה הפרדת כפילויות נכנסו **94** טקסטים, מהם **24** בבדיקה. השוואה מלאה עם נציגות לכל שבע המחלקות בכל החלוקות: **True**.

בהשוואת המסווג הקבוע על כל ארבע הזרועות נדרשת גם קבלה של Formatting; נשארו 10 טקסטי בדיקה. ההשוואה המרכזית C מול D משתמשת בקבוצה המשותפת C/D.

### מסווג קבוע: קבוצת C/D המשותפת שעברה סינון אוטומטי

| test_condition | macro_f1_mean | macro_f1_sd | n_test | label_flip_rate | correct_to_incorrect | incorrect_to_correct | true_probability_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Normalized | 0.2048 | 0.0082 | 24 | 0.0278 | 0.3333 | 0.0000 | -0.0071 |
| Original | 0.2189 | 0.0327 | 24 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Paraphrase | 0.2048 | 0.0082 | 24 | 0.0278 | 0.3333 | 0.0000 | -0.0050 |

### מסווג קבוע: כל הפלטים, כולל שכתובים שנפסלו

| test_condition | macro_f1_mean | macro_f1_sd | flip_rate | correct_to_incorrect | incorrect_to_correct | true_probability_delta |
| --- | --- | --- | --- | --- | --- | --- |
| Formatting | 0.3851 | 0.0427 | 0.0556 | 2.0000 | 1.3333 | -0.0013 |
| Normalized | 0.3632 | 0.0232 | 0.0873 | 4.0000 | 2.0000 | -0.0077 |
| Original | 0.3934 | 0.0224 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Paraphrase | 0.3504 | 0.0082 | 0.0794 | 4.6667 | 1.6667 | -0.0076 |

השינוי בהסתברות הוא שינוי ממוצע בהסתברות תווית המקור. Flip אינו מוכיח שינוי סגנון בלבד כאשר השכתוב נפסל.

### אימון מחדש: הקבוצה המשותפת שעברה סינון

| train_condition | test_condition | macro_f1_mean | macro_f1_std | accuracy_mean |
| --- | --- | --- | --- | --- |
| Normalized | Normalized | 0.0836 | 0.0172 | 0.1667 |
| Normalized | Original | 0.0935 | 0.0183 | 0.1806 |
| Normalized | Paraphrase | 0.0844 | 0.0167 | 0.1667 |
| Original | Normalized | 0.0922 | 0.0134 | 0.2083 |
| Original | Original | 0.0880 | 0.0166 | 0.1944 |
| Original | Paraphrase | 0.0878 | 0.0139 | 0.1944 |
| Paraphrase | Normalized | 0.0768 | 0.0086 | 0.2083 |
| Paraphrase | Original | 0.0830 | 0.0195 | 0.2083 |
| Paraphrase | Paraphrase | 0.0733 | 0.0041 | 0.1944 |

### אימון מחדש: תוצאות תיאוריות הכוללות שכתובים שנפסלו

| train_condition | test_condition | macro_f1_mean | macro_f1_std | accuracy_mean |
| --- | --- | --- | --- | --- |
| Normalized | Normalized | 0.3696 | 0.0426 | 0.3810 |
| Normalized | Original | 0.3702 | 0.0412 | 0.3770 |
| Normalized | Paraphrase | 0.3410 | 0.0309 | 0.3532 |
| Original | Normalized | 0.3632 | 0.0232 | 0.3770 |
| Original | Original | 0.3934 | 0.0224 | 0.4008 |
| Original | Paraphrase | 0.3504 | 0.0082 | 0.3651 |
| Paraphrase | Normalized | 0.3574 | 0.0251 | 0.3651 |
| Paraphrase | Original | 0.3678 | 0.0294 | 0.3770 |
| Paraphrase | Paraphrase | 0.3545 | 0.0250 | 0.3651 |

אין לפרש שיפור בקבוצה התיאורית כתועלת מהסרת סגנון: שינוי תוכן, עמדה או מילות מפתח יכול להסביר אותו.

### זיהוי כותב

| cohort | representation | condition | accuracy_mean | macro_f1_mean | narrative_groups | n_test | uniform_chance_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all_generated_descriptive | embedding | Normalized | 0.5357 | 0.5146 | 7 | 112 | 0.2500 |
| all_generated_descriptive | embedding | Original | 0.5625 | 0.5429 | 7 | 112 | 0.2500 |
| all_generated_descriptive | embedding | Paraphrase | 0.5000 | 0.4750 | 7 | 112 | 0.2500 |
| all_generated_descriptive | surface_style | Normalized | 0.3482 | 0.3400 | 7 | 112 | 0.2500 |
| all_generated_descriptive | surface_style | Original | 0.4643 | 0.4193 | 7 | 112 | 0.2500 |
| all_generated_descriptive | surface_style | Paraphrase | 0.4732 | 0.4755 | 7 | 112 | 0.2500 |
| matched_automated_pass | embedding | Normalized | 0.9167 | 0.8833 | 4 | 14 | 0.4583 |
| matched_automated_pass | embedding | Original | 0.9167 | 0.8833 | 4 | 14 | 0.4583 |
| matched_automated_pass | embedding | Paraphrase | 0.9167 | 0.8889 | 4 | 14 | 0.4583 |
| matched_automated_pass | surface_style | Normalized | 0.6250 | 0.4167 | 4 | 14 | 0.4583 |
| matched_automated_pass | surface_style | Original | 0.7083 | 0.5472 | 4 | 14 | 0.4583 |
| matched_automated_pass | surface_style | Paraphrase | 0.6250 | 0.4167 | 4 | 14 | 0.4583 |

הממוצעים חושבו בשקלול שווה של קבוצות הנרטיב. בכל קבוצה אומן מסווג כותבים חדש על אותם כותבים ועל טקסטים נפרדים לכל אחד מהייצוגים; זו אינה העברה ממסווג שאומן על Original. המבחן בתוך נרטיב מצמצם את השפעת תווית הנרטיב, אך נושא, ישויות ותוכן אישי עדיין עלולים לשמש לזיהוי. לכן ירידה ביכולת הזיהוי אינה הוכחה שהוסר דווקא סגנון.

ה־probe הוא LogisticRegression לינארי עם StandardScaler המותאם לנתוני האימון בלבד בכל תנאי. ירידה בדיוק של probe לינארי אינה הוכחה שמידע הכותב נמחק מכל ייצוג אפשרי או שלא ניתן לחלץ אותו במסווג חזק יותר.

הכינוי Style-preserving Paraphrase מתאר את ההנחיה למחולל, ולא תוצאה מאומתת של שימור סגנון אישי. surface_style_measurements.csv מכיל מדדי אורך, פיסוק ואותיות רישיות לכל ארבע הזרועות; הם אינם מכסים את כל ממדי הסגנון. נדרשת בדיקה אנושית גם לכך שזרוע הביקורת אכן משמרת סגנון ושהנרמול אכן מאחד אותו.

גם אי־ירידה בזיהוי כותב מתוך embedding אינה מוכיחה שנשמר הסגנון: ישויות ונושאים שנשמרו כדין יכולים לזהות חשבון. התאמה לפי אותה תווית נרטיב אינה התאמה לפי אותו אירוע או אותו תוכן.

### Counterfactual style

| scope | after_normalization | n_source_texts | n_predictions_including_seeds | label_flip_rate | correct_to_incorrect_rate | incorrect_to_correct_rate | mean_max_probability_delta | mean_true_probability_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_generated_descriptive | False | 14 | 168 | 0.0119 | 0.0119 | 0.0000 | -0.0082 | -0.0156 |
| all_generated_descriptive | True | 14 | 168 | 0.0536 | 0.0536 | 0.0000 | -0.0023 | -0.0048 |
| automated_pass_only | False | 11 | 93 | 0.0000 | 0.0000 | 0.0000 | -0.0013 | -0.0009 |
| automated_pass_only | True | 6 | 60 | 0.0000 | 0.0000 | 0.0000 | -0.0014 | -0.0001 |

| scope | after_normalization | n_source_texts | n_groups_including_seeds | narrative_consistency_rate | original_plus_variants_consistency_rate |
| --- | --- | --- | --- | --- | --- |
| all_generated_descriptive | False | 14 | 42 | 0.9762 | 0.9762 |
| all_generated_descriptive | True | 14 | 42 | 0.9286 | 0.9286 |
| all_four_targets_automated_pass | False | 4 | 12 | 1.0000 | 1.0000 |
| all_four_targets_automated_pass | True | 4 | 12 | 1.0000 | 1.0000 |
| matched_before_after_automated_pass | False | 4 | 12 | 1.0000 | 1.0000 |
| matched_before_after_automated_pass | True | 4 | 12 | 1.0000 | 1.0000 |

narrative_consistency_rate הוא שיעור קבוצות המקור שבהן כל ארבעת יעדי הסגנון קיבלו אותה תחזית. original_plus_variants_consistency_rate דורש גם התאמה לתחזית על טקסט המקור. מספר הקבוצות כולל seeds ואינו מספר טקסטים בלתי תלויים.

מספר טקסטי מקור עם כל ארבעת היעדים שעברו סינון גם לפני וגם אחרי הנרמול: **4**. קובץ counterfactual_consistency.csv מציג עקביות לכל טקסט, seed ושלב. שיעורי flip בשורות שונות של הטבלה אינם השוואה מזווגת אם קבוצות הקבלה שונות; ההשוואה המשותפת שמורה בקובץ counterfactual_matched_before_after.csv.

ביקורת שינוי עמדה: נוצרו 7 טקסטים; שיעור שינוי התחזית בממוצע על פני seeds היה 0.0476. לא נקבעה תווית נרטיב חדשה באופן עצמאי ולא אושר אנושית שהעמדה אכן הוחלפה. לכן זו בדיקת תגובתיות לניסיון שינוי, ולא הוכחה לרגישות נכונה לשינוי נרטיב. אין לחשב accuracy מול התווית הישנה.

## 3. מה ניתן להסיק

ההרצה מודדת התנהגות בפועל של הצינור, וכוללת ביקורת לעצם השכתוב באמצעות LLM. תוצאות הפיילוט מאפשרות לזהות בעיות שימור משמעות ולתאר רגישות לטרנספורמציות. רק השוואה מזווגת בין שכתובים תקינים יכולה לתמוך בפרשנות סגנונית, וגם אז נדרשת בדיקה אנושית של העמדה והמסגור.

בפיילוט לכל חשבון יש תווית מקור נרטיבית אחת. לכן הקשר בין חשבון לתווית מובנה בדאטה. קורלציה זו לבדה אינה מוכיחה כשל בזיהוי הנרטיב של הטקסט; לטענה כזו נדרש תיוג סמנטי שאינו נקבע לפי זהות המקור.

## 4. מה לא ניתן להסיק

לא הוכחה סיבתיות. אין בסיס להמיר שינוי בתחזית על שכתוב בעל תוכן שונה לראיה על Author Style. Confidence גבוה יותר אינו בהכרח שיפור; נשמרו גם NLL, Brier ו־ECE. אין לטעון למובהקות בין תנאים על בסיס שלושה seeds בלבד, ואין כאן ניסוי בלתי תלוי על חלוקות רבות של כותבים.

היעדר שיפור אינו מוכיח שהמודל אינו משתמש ב־shortcut. אם המחולל לא שינה בפועל את הסגנון, או לא הפחית את מידע הכותב בלי לפגוע בתוכן, ההתערבות אינה מבחן מספק להשערה.

## 5. מגבלות

התוויות הן שיוך נרטיבי של חשבונות, ולא gold ברמת כל טקסט; חשבון אינו תמיד אדם יחיד; נבדקה אנגלית בלבד; המדגם קטן וקצר; נבדק כותב אחד לכל מחלקה בבדיקה; הכותבים כבר נחקרו בעבר בפרויקט; המחולל קטן; אין אימות אנושי; סינון לקסיקלי עלול לפסול פרפרזה תקינה או להחמיץ שינוי סוכנות ומסגור; NLI ו־similarity הם כלי סינון ולא הוכחת שימור משמעות. ירידה בזיהוי כותב יכולה לנבוע גם מאובדן תוכן.

נשמר human_review_blind_queue.csv לבדיקת זוגות מקור–שכתוב ללא תנאי, שם כותב, תווית או תחזית מסווג. מפתח נפרד נמצא ב־human_review_key.csv. העמודות למילוי ריקות: **לא בוצע תיוג אנושי**. זו דגימת ביקורת משכבת לפי תנאי, נרטיב ותוצאת סינון; היא אינה מדגם מקרי לאמידת שיעור השימור באוכלוסייה.

## 6. Verdict

• **רגישות ל־Author Style:** שינויי תחזיות נמדדו, אך ייחוסם לסגנון בלבד מותנה בשימור משמעות ועמדה; הסינון האוטומטי לבדו אינו מספיק לקביעה סיבתית. בגרסאות שעברו סינון אוטומטי לפני נרמול נמדד flip rate של 0.0000 על 11 טקסטי מקור; זו רגישות נצפית תחת סינון אוטומטי, ללא אישור אנושי לשינוי סגנון בלבד.

• **ירידה בזיהוי כותב:** המספרים נמדדו במסווגים שהותאמו מחדש ומוצגים בטבלה. יש לפרש הבדל בקבוצה המסוננת בנפרד מהבדל הכולל שכתובים שנפסלו. all_generated_descriptive, embedding: Original=0.5625, Paraphrase=0.5000, Normalized=0.5357; Normalized−Original=-0.0268, Normalized−Paraphrase=+0.0357. all_generated_descriptive, surface_style: Original=0.4643, Paraphrase=0.4732, Normalized=0.3482; Normalized−Original=-0.1161, Normalized−Paraphrase=-0.1250. matched_automated_pass, embedding: Original=0.9167, Paraphrase=0.9167, Normalized=0.9167; Normalized−Original=+0.0000, Normalized−Paraphrase=+0.0000. matched_automated_pass, surface_style: Original=0.7083, Paraphrase=0.6250, Normalized=0.6250; Normalized−Original=-0.0833, Normalized−Paraphrase=+0.0000.

• **שיפור על unseen authors מעבר לפרפרזה:** לא נמדד שיפור מספרי בהשוואה המשותפת: Original→Original=0.0880, Normalized→Normalized=0.0836, הפרש=-0.0045. הבדל זה כפוף לסינון אוטומטי ולמגבלות המדגם; לא נקבעה מובהקות. נמדד יתרון מספרי מול Paraphrase→Paraphrase=0.0733; Normalized−Paraphrase=+0.0102. אין להסיק ממנו לבדו שהוסר Author Style.

• **LoRA/DoRA:** אין כרגע הצדקה מחקרית למעבר על סמך פיילוט זה. גם לא הוכח שה־prompting הנוכחי מספיק. הצעד הבא הוא מחולל איכותי יותר ואימות אנושי עיוור של שכתובים, לפני הגדלת המדגם ואימון נוסף.

## קבצים ושחזור

ראו README.md, config.json, prompts.json ו־generator_revision.json. split_definitions.csv ו־author_splits.csv מכילים את החלוקה; text_variants.csv מכיל את ארבע הגרסאות; generated_rewrites.jsonl מכיל גם את ביקורות הנגד; rewrite_validation.csv כולל ציון, החלטה וסיבות פסילה לכל שכתוב; metrics_summary.csv כולל תוצאות לכל seed; per_author_metrics.csv כולל תוצאות לכל כותב; checkpoints/ מכיל רק את ראשי המודלים החדשים. לא נדרס המודל המקורי. משקלי המחולל והמנוע המקומיים ב־runtime_llama/ ומשקלי ניסיונות ההיתכנות ב־runtime_generator/ מוחרגים מ־Git.

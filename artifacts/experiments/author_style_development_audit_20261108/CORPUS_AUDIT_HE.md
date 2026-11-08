# איכות המאגר וגבולות השימוש

מחזור עבודה 8–9 בנובמבר 2026. ניתוחי תוכן/features חדשים בוצעו רק בכותבי train. עבור val/test נבדקו מיפוי כותבים, ספירות ו־hashes קיימים; לא בוצעה עליהם בחירת שיטה, למידה או הערכת מודל.

| scope | train | validation | test | total |
| --- | --- | --- | --- | --- |
| unique annotated sources | 202 | 96 | 131 | 429 |
| two-narrative eligible sources | 105 | 43 | 70 | 218 |
| authors | 9 | 4 | 6 | 19 |
| ChatGPT pairs | 30 | 0 | 0 | 30 |

## מה נספר

456 רשומות נאספו מ־19 כותבים; יש בהן 429 text hashes שונים. לאחר הסרת חזרות נשמרו 429 קטעים מ־429 מאמרים שונים. v2/v3/ChatGPT הם גרסאות של מקורות קיימים, ולא מאות מאמרים חדשים. אין לחבר את שורות קובצי הניסויים כדי לאמוד גודל קורפוס. [Source inventory](source_inventory.csv).

בכל 429 הרשומות יש byline_verified=True: זוהי ראיית ייחוס פומבי, לא אימות אנושי לתווית הנרטיב ולא הוכחה לכתיבה ללא עורכים/עזרה. אין תוויות מקור אנושיות שמולאו: 0/429; גם חבילת המקור האנושית נבדקה ונמצאה ריקה. התוויות הן הצעות מכונה: Unclear=203, Right-wing=104, Left-wing=114, Zionist=7, Ukrainian=1. 218 טקסטים נבחרו לתת־משימה Right-wing/Left-wing; 211 אחרים אינם הופכים אוטומטית לתווית בינארית. זה אינו קורפוס מאומת לכל שבעת הנרטיבים.

| author | frozen split | unique sources | eligible narrative | current pairs | human labels |
| --- | --- | --- | --- | --- | --- |
| ben-shapiro | test | 20 | 7 | 0 | 0 |
| chuck-norris | train | 23 | 14 | 4 | 0 |
| connie-schultz | train | 20 | 6 | 2 | 0 |
| david-harsanyi | train | 24 | 13 | 3 | 0 |
| debra-saunders | val | 24 | 11 | 0 | 0 |
| dennis-prager | test | 24 | 12 | 0 | 0 |
| froma-harrop | train | 24 | 10 | 4 | 0 |
| jamie-stiehm | train | 24 | 17 | 4 | 0 |
| jeff-robbins | test | 23 | 12 | 0 | 0 |
| jim-hightower | train | 24 | 21 | 2 | 0 |
| joe-conason | test | 16 | 11 | 0 | 0 |
| lawrence-kudlow | train | 20 | 13 | 4 | 0 |
| marc-dion | train | 24 | 5 | 4 | 0 |
| mona-charen | val | 24 | 17 | 0 | 0 |
| robert-scheer | test | 24 | 14 | 0 | 0 |
| star-parker | val | 24 | 5 | 0 | 0 |
| stephen-moore | test | 24 | 14 | 0 | 0 |
| susan-estrich | val | 24 | 10 | 0 | 0 |
| veronique-de-rugy | train | 19 | 6 | 3 | 0 |

## כמה זמין לפיתוח

202 מקורות מתשעה כותבי train זמינים ל־Author-ID, שאינו דורש תווית נרטיב. מתוכם 105 בעלי הצעת תיוג בינארית מתאימה. יתר 97 רשומות train יכולות ללמד סגנון/כותב אך אינן narrative gold. 96 טקסטים מארבעה כותבי validation קיימים — בסך הכול 298 מקורות מ־13 כותבים שאינם test — אך לא השתמשנו בהם להרצת baseline זו. 131 טקסטים משישה כותבי test הוצאו מכל חישובי features/model/topic חדשים.

## כפילויות וזליגה

אין collisions של text hash או article hash בין author splits ב־429 הייחודיים, ואין חפיפת מחברים בין splits. בסריקה הלקסיקלית החדשה על 202 train נמצאו 0 זוגות near-duplicate לפי word-5-shingle Jaccard≥0.80 או word-TFIDF cosine≥0.95; הקיבוץ כולל גם מאמר/טקסט זהים. הספים הללו הם הגדרת audit חדשה, לא שינוי ב־preservation guards. כל הניסויים שומרים article/near-duplicate group בצד אחד.

ה־audit ההיסטורי של 218 דיווח שאין exact/cross-split duplicate removals, ו־generated_cross_split_duplicates.json ההיסטורי ריק. לא נערכה סריקת near-duplicate סמנטית חדשה מול test; לכן **אין כאן הוכחה שאין זליגה סמנטית/אותו אירוע בין splits**. Hashes אינם מזהים paraphrases או כיסוי אותו אירוע. אין להשתמש בתוצאה ריקה כהוכחה לעצמאות אירועים.

## אורך, זמן ונושאים

| author | n train | min words | median | max | under 50 | years |
| --- | --- | --- | --- | --- | --- | --- |
| chuck-norris | 23 | 39 | 55.0 | 74 | 5 | 2014\|2015 |
| connie-schultz | 20 | 35 | 52.0 | 100 | 8 | 2021 |
| david-harsanyi | 24 | 36 | 53.0 | 99 | 9 | 2026 |
| froma-harrop | 24 | 40 | 62.5 | 99 | 4 | 2026 |
| jamie-stiehm | 24 | 39 | 55.5 | 94 | 7 | 2026 |
| jim-hightower | 24 | 38 | 70.0 | 105 | 4 | 2026 |
| lawrence-kudlow | 20 | 36 | 44.5 | 98 | 12 | 2012\|2017\|2018 |
| marc-dion | 24 | 40 | 54.5 | 88 | 9 | 2026 |
| veronique-de-rugy | 19 | 38 | 60.0 | 93 | 5 | 2026 |

הקטעים קצרים, בערך 35–105 tokens מילוליים לפי regex, ונלקחו בדרך כלל כקטע ראשון ממאמר, לא כטקסט ארוך אקראי. זה מאפשר probes פשוטים אך הופך sentence length, פיסוק ו־function words לרועשים. מקור אחד/פרסום אחד עוזרים לקיבוץ תקף, אך אינם מחליפים הרבה כתיבה עצמאית לכל כותב. אל תאחדו Original וגרסאותיו כאילו היו תצפיות עצמאיות.

קיים ערבוב משמעותי בין תקופה לכותב: Norris מ־2014–2015, Schultz מ־2021, Kudlow מ־2012/2017/2018, ורוב האחרים מ־2026. NMI(year,author) ב־train הוא 0.583. זהו קשר תיאורי וגורם ערבוב אפשרי, לא תוצאת סיבתיות.

KMeans עם שישה אשכולות TF-IDF, שהוגדר מראש על train בלבד, נתן topic-author NMI=0.118. [אשכולות ומונחים](development_topics.csv) מצביעים על נטיות כגון taxes/economy ו־Texas/governor. האשכולות אינם labels נושא אנושיים; קשר נמוך באשכולות גסים אינו שולל topic shortcut. Word/char baselines קולטים גם תוכן, שמות ותקופה וגם בחירת מילים סגנונית. גם בתוך אותה הצעת נרטיב נשארים נושאים, תתי־נושאים וזמן כגורמי ערבוב.

## מסקנת התאמה

המאגר מספיק לקדם אבחון train-only, להשוות probes ולהכין ביקורת אנושית. הוא עדיין **אינו מספיק כבסיס לביסוס causal author-style shortcut או שיפור generalization**: חסרים labels אנושיים, intervention מאומת, איזון זמן/אירוע וכמות מספקת של זוגות. הזיהוי הציבורי של המחברים טוב יותר מהנחת “account=person”, אבל אין כאן זיהוי פורנזי של מחבר הטקסט.

בקרת שנה משלימה, שנוספה לאחר ה־audit: 139 מקורות משישה כותבי train שכל מקורותיהם מ־2026. Character Author-ID נשאר מעל chance גם כאן (56.8% accuracy; chance 16.7%), ולכן הבדל שנים גס אינו מסביר לבדו את כל ה־predictability. זו אוכלוסיית שש מחלקות אחרת, לא השוואה ישירה ל־48.4% בתשע מחלקות ולא הפרדה מלאה בין topic ל־style.

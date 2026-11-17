# בדיקת עומק של תשעת המקורות ההיסטוריים

17.11.2026. נבדקו שוב snapshots וקרדיטים של המקורות שכבר היו במאגר; **לא בוצע
איסוף מועמדים חדש ולא הוחזר אף מקור לחבילת348**. פרטי כל מקרה וקישורי מקור
מופיעים ב־[HISTORICAL_NINE_AUDIT.csv](HISTORICAL_NINE_AUDIT.csv).

## חמישה מקרי חפיפה — כולם מול Test

| מקור Train של Jim Hightower | מאמר | מקור ההחזקה המשויך ל־Joe Conason |
|---|---|---|
| creators:416490 | AI Billionaires to Grassroots People: Shut Up! | creators:416956 |
| creators:416964 | Shouldn't Public Protection Be for, You Know, the Public? | creators:417453 |
| creators:420447 | AI Billionaires Say: Get Out of Our Way, Fools! | creators:420899 |
| creators:419965 | Corporate Stupidity Sidetracked By Mad-as-Hell Farm Rebels | creators:420406 |
| creators:421736 | Big Tech Is the New Feudalism -- Here's How to Fight Back | creators:422148 |

בכל החמישה גוף המאמר המנורמל זהה ו־5-shingle Jaccard=1.0. זה אינו רק אזכור
אותו אירוע או ציטוט קצר משותף. דפי מקור בעלי URL/byline/מעטפת שונים יכולים
לייצר hashes שונים של HTML וקטעים, ולכן בדיקת ה־hash הקודמת לא הספיקה.
זהות הגוף אומתה מחדש מהקבצים המקומיים וקושרה ב־NINE_AUDIT_BINDINGS.

יש כאן גם סתירה בייחוס המקור: אותו גוף מופיע ברשומות של שני כותבים. הבדיקה
אינה קובעת מי המחבר המקורי, אם מדובר בפרסום אורח/סינדיקציה או בשגיאת מו״ל/איסוף.
אין לתקן שם כותב או להעביר את המקור בין חלוקות אוטומטית. לצורך האימות החדש,
הפעולה המגוננת היא להשאיר את חמשת מקורות Train בחוץ, תוך שמירת ההיסטוריה.

אין בין תשעת המקורות ההיסטוריים חפיפה מול Validation. חמש חפיפות ה־Validation
שדווחו באיסוף הרחב שייכות למקורות אחרים מתוך18 המוחרגים. אין לערבב בין הספירות.

## ארבעה מקרי ייחוס — קרדיט משותף למאמר

| מקור | מאמר | ממצא מעודכן |
|---|---|---|
| creators:222877 | Trump Needs a Return to King Dollar | רשימת המו״ל נותנת קרדיט ל־Kudlow, Laffer ו־Moore; גוף המקור מזכיר גם Kudlow/Moore |
| creators:223861 | Tariffs Are Taxes | אותו שילוב מחברים בפרסום המקביל ובקרדיט המקומי |
| creators:218236 | Republicans' Tax Plan Takes a Quirky Swipe at the Little Guys | פרסום מסונדיקט מציין Kudlow ו־Stephen Moore כמחברים |
| creators:209914 | Index Capital Gains for Inflation, Mr. President | פרסום מסונדיקט מציין Kudlow ו־James Carter כמחברים |

רישומי המו״ל המקביל תומכים בייחוס משותף של שני המאמרים הראשונים.
[רשימת Larry Kudlow ב־National Review](https://www.nationalreview.com/author/larry-kudlow/).
למאמר השלישי יש כותרת קרדיט משותפת מפורשת בפרסום המסונדיקט.
[Rasmussen Reports](https://www.rasmussenreports.com/public_content/political_commentary/commentary_by_lawrence_kudlow/republicans_tax_plan_takes_a_quirky_swipe_at_the_little_guys).
לרביעי יש כותרת קרדיט מפורשת לשני מחברים.
[RealClearPolitics](https://www.realclearpolitics.com/articles/2017/08/12/index_capital_gains_for_inflation_mr_president_134734.html).

Stephen Moore הוא כותב Test בחלוקה הקפואה. לכן שלושת המקרים הראשונים פוגעים
גם בהנחת "כותב יחיד מזוהה של Train" וגם בהפרדת הכותבים; אין צורך להוכיח זהות
מילולית למאמר Test כדי לזהות את סיכון הקרדיט. Laffer אינו כותב Train מוגדר.
James Carter אינו משויך לאחת החלוקות הקפואות; במקרה הרביעי אין ראיה לחפיפה
מול Validation/Test, אלא הפרה של תנאי הכתיבה בידי כותב Train יחיד.

**דיוק חשוב בדגל הרביעי:** המילים co-authored by Brian Domitrovic בגוף המקור
מתארות ספר של Kudlow. אין להסיק מהן ש־Domitrovic כתב את המאמר. הדגל המקורי
היה רחב מדי בנימוקו; הייחוס המשותף של המאמר נתמך כעת בנפרד בקרדיט Kudlow/Carter,
וגם בביו של Carter שבסיום. שיפור הראיות אינו סיבה להחזירו אוטומטית.

## החלטת שימוש

כל התשעה נשארים מוחרגים. ה־105 ההיסטוריים אינם נדרסים, וכותבים/תוויות/חלוקות
אינם משתנים. חבילת348 נשארת בדיוק כפי שנאספה לאחר החרגות:96 מהמקוריים ועוד252
מועמדים אחרים. כל הסקירות עודן ממתינות לאדם. הממצאים מחייבים הסתייגות לגבי
שימושים היסטוריים וטענות להכללה נקייה; הם אינם משנים בדיעבד תוצאה מספרית קיימת.

לא חושבו ביצועי מסווג על Test. השימוש במקורות ההחזקה הוגבל לאימות חפיפת גוף
מאמר וקרדיט, בלי שיפור שכתוב או בחירת תווית בעזרת מידע מההחזקה.

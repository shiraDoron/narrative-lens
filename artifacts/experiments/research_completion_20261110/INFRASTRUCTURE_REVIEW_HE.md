# סקירת תשתית — ממצאים וגבולות

10.11.2026. סקירה סטטית של קוד היסטורי, בדיקות fixtures ובדיקת תוצרים שמורים; ללא אימון מדעי או תחזיות חדשות.

| רכיב | ממצא | פעולה |
|---|---|---|
| compile_candidates.py | במיפוי הישן75 רשומות נשאו style_present=False; חיבור פלט לא עדכן את הדגל | תוקן הדגל בהתאם לטקסט בכל105. בדיקת regression מכשילה metadata שאינו תואם זמינות. המקורות והשכתובים לא שונו |
| יבוא אדם | היו מסלולי30/75 ו־train105, אך לא חבילת Style105 משולבת או validation43 | נוספו pairs105/labels43 תוך שימוש באותה התאמת ID/Original/Rewrite, ערכים, provenance ושמירת raw. טופס ריק נדחה |
| gate היסטורי | snapshot של common30 ממשיך לדווח75 חסרים | לא שונה snapshot קפוא. audit נוכחי מחובר ל־candidate105 ומדווח missing0, אך חוסם אימון מסיבות האדם/החיבור האמיתיות |
| תקציב |25 schedules שוחזרו בדיוק;140 updates ו־2240 slots לכל seed/arm | נבדקו מיפוי source/index/variant, תוויות ו־D/E. שוויון tokens/FLOPs לא נטען; מספר מילים מעובדות נשמר בנפרד |
| trainer היסטורי | author_style_controlled.train בוחר best validation checkpoint, ומספר batches נגזר מאורך dataset | אינו drop-in לתקציב העדכונים ול־final checkpoint של A–E. לא שונה ולא הורץ; חיבור trainer מאושר עדיין חסר |
| evaluate היסטורי | פונקציות evaluate ב־followup/study כוללות test וסינון all-arm אוטומטי | לא הופעלו. אינן מימוש ל־human symmetric fallback הנוכחי. אין להשתמש ב־--stage all לשלב זה |
| משימת ההערכה | ראש7 נשמר בפרוטוקול, אבל המשימה הנוכחית Left/Right | נוסף עזר evaluation טהור עם בדיקות: argmax על7, F1 על2, inactive-output rate, כיסוי IDs זהה בכל A–E/seeds. אין renormalization שקט ואין תחזיות אמיתיות |
| אי־ודאות | bootstrap/paired author-cluster comparisons מוגדרים בפרוטוקול, אך אינם trainer/evaluation bridge מאושר | מתועד כחיבור עתידי; fixtures אינם הוכחה לניתוח סטטיסטי תקף על נתוני התזה |
| semantic QC |75 זוגות לכל שיטה, שני כיווני NLI, אותם source/code/scaling hashes | בדיקה עצמאית מחברת כל score לדגל לפי0.6/0.85. תוצרי QC לא שונו או הורצו מחדש |
| complete flag | truncated=False לשכתובים חיצוניים הוא default; finish_reason חסר | תועדה המגבלה; לא הפך לראיית שלמות אמיתית ולא שונה guard |
| טקסט פרפרזה היסטורי | ב־0105f26ef9f1 קיים פתיח מכונה עם רווחי סוף שורה | נשמר verbatim גם בחבילת האדם. לא נוקה כדי לעבור Git whitespace check; החרגת קובץ המקור המתועד שומרת על הטקסט הקפוא |
| כמתים/עוצמה | ספירת negation ומילות certainty אינן scope/intensity validation | נוספו רמזי משטח תיאוריים בלבד וטקסטי עריכה, ללא סף/guard/acceptance חדש. Drift נותר not adjudicated |
| חבילות אדם | דגלי QC עלולים לפגוע בעצמאות הסוקר | חבילה עצמאית ללא דגלים וחבילה נפרדת בסיוע QC; האחרונה אינה blind. כל ההכרעות ריקות |
| provenance | GPT-6/9.11.2026 מתייחס רק ל־75 החדשים; legacy30 אינו מתועד באותה רמה | נשמרו שני cohorts. unknown revision/decoding/finish_reason נשארים unknown; סקירות Claude אינן אדם |

## מה נבדק ומה לא

הבדיקות מכסות יחסי ID/טקסט/hash, הפרדת כותבים, תקציב דוגמאות, schemas, ערכי מדדים ויישור תנאים. הן אינן מאשרות תוויות, שימור נרטיב, הסרת אותות כותב או יתרון בהכללה. אין trainer מאושר end-to-end, בדיקת initialization בפועל בחמש הרצות, או inference חדש. אין שינוי בפרוטוקול, QC thresholds, labels, splits או קוד האימון ההיסטורי.

לא הוערך test ולא נבחר דבר לפי תוצאותיו. בדיקת split/hashed metadata נעשתה read-only; אין טקסטי test בחבילות הסקירה החדשות. היעדר exact collisions אינו שולל זליגה סמנטית/אירועים.

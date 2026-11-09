# הכנת batch השכתובים — לא prompt מקורי ולא הרשאת יצירה

הקובץ [STYLE_REWRITE_MISSING_75.csv](STYLE_REWRITE_MISSING_75.csv) מכיל ID ו־Original של 75 מקורות train החסרים, ללא מחבר, תווית, scores או תוצאות מודל. לא יוצרו עבורם שכתובים כאן. פרפרזות קיימות לכולם; אין צורך לייצר עוד 75 פרפרזות רק כדי להגיע ל־105 shared IDs.

[GENERATOR_PROVENANCE.json](GENERATOR_PROVENANCE.json) מתעד את הידוע: ChatGPT לפי דיווח המשתמש, קובץ התקבל ב־2026-11-02, Original-only לפי דיווח. **המודל המדויק, נוסח system/user prompt, decoding parameters והיסטוריית בקשות אינם ידועים.** תאריך קבלת הקובץ אינו הוכחת מועד יצירה; אין finish_reason אמיתי שמוכיח שלמות.

אפשר לשחזר רק את הדרישות המדווחות: מקור בלבד; ללא v2/v3, guards או reviews; שימור עובדות, narrative/stance, attribution, certainty, participant roles, event characterization, rhetorical intensity, quotes, quantifiers, negation, entities, numbers, time ו־causality. **רשימה זו אינה שחזור מילולי של הפרומפט**, ואין להעתיקה כמסמך הטוען שזה ה־prompt המקורי.

לפני יצירה יש להשיג את הפרומפט/מודל/פרמטרים המקוריים, או להגדיר ניסוי generator חדש במפורש עם החלטת מחקר מתועדת; לא להחליף silently ולא לערבב 30 legacy ו־75 new כאילו אותו generator. אין להריץ batch עד שההחלטה הזו נסגרה.

לאחר הסגירה: batch manifest קפוא, attempt אחד לכל ID או retry policy טכני קבוע מראש (רק network/schema failure, בלי classifier feedback). לשמור request/response מקוריים, timestamps, exact model revision, raw output, finish reason וכל retry. הפלט יהיה CSV עם `id,chatgpt_style_rewrite`; אין לערוך פלטים ידנית או להשתמש בתוויות/מחבר/תוצאות מודל ביצירה. Original SHA-256 נשמר ב־source manifest.

כל 105 המקורות והניסיונות נשמרים. כשל/Borderline אינם נמחקים; QC ו־fallback symmetric בפרוטוקול. אין לשכתב val/test. קובץ generation חדש נשמר בתיקיית run חדשה, לא דורך על 30 התוצרים הקיימים.

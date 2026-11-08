# מוכנות Human Validation וחוסרים ב־External Review

זהו דוח לחוקר/ת, **לא חלק מהחבילה שנשלחת לסוקר האנושי**.

## החבילה מוכנה, אבל אימות אנושי טרם בוצע

- [HUMAN_VALIDATION_30.md](../chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md).
- [HUMAN_VALIDATION_30.csv](../chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.csv).

נבדקו 30 IDs ייחודיים, התאמה מלאה למקורות ולשכתובים השמורים, ושדות ריקים בכל הרשומות. החבילה מציגה רק ID, Original, ChatGPT Style Rewrite וחמשת שדות האדם: meaning, narrative/stance, style, drift, notes. אין author field, guards, scores, v2/v3, review ratings או מסקנות קודמות. אין בה קישורים לדוחות אבחון. זהות או אירועים המופיעים בטקסט המקורי אינם מוסרים/משוכתבים לצורך blinding.

לא מילאנו שדות ולא שינינו את 30 הטקסטים. ה־CSV וה־Markdown המקוריים מוגנים ב־source hashes. קוד replay הקודם מסרב לדרוס תשובות אנושיות אם ימולאו. אין לשלוח את דוח התוצאות/ה־comparison יחד עם חבילת האדם, ויש לתעד reviewer/date בנפרד. גם אדם שקרא את התוצאות הקודמות אינו סוקר עיוור לחלוטין.

## מה יובא ומה חסר

| review | נתונים לפי ID בריפו | מצב |
|---|---|---|
| Old Normalized | כן | LLM_EXTERNAL_REVIEW_30_20261101.csv, היסטורי |
| New Normalized v2 | כן | NEW_NORMALIZED_EXTERNAL_LLM_REVIEW_30_20261101.csv, היסטורי |
| v3 blind | כן | V3_BLIND_EXTERNAL_LLM_REVIEW_30_20261102.csv, היסטורי |
| ChatGPT Style Rewrite | **לא** | רק aggregate שסופק בשיחה: 24 Meaning Yes, ‏16 Drift No וכו׳ |

הספירות המצרפיות מיובאות בנפרד ב־[external_llm_review_aggregate.json](../chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/external_llm_review_aggregate.json). 16 נקראים **clean according to External LLM Review**, ולא human-validated. לא ידוע אילו IDs הם; אי אפשר לשחזר חפיפות, discrepancies עם guards או per-ID failure notes מתוך סכומי עמודות. [Inventory של קובצי review](review_file_inventory.csv).

חסרים בדיוק: טבלת ChatGPT review עם `id` ו־ratings/notes לכל 30, מודל/סוקר, prompt review, תאריך ו־context/blinding provenance. לא הומצאו ratings ולא הועברו דירוגי v2/v3 לשכתובים החדשים.

גם הגנרטור החיצוני אינו מתועד עד הסוף: חסרים ה־prompt המקורי, version/date, parameters, raw request ו־finish_reason. הנתונים השמורים מאפשרים לשחזר **מדידה**, לא את יצירת הטקסט ב־ChatGPT באופן זהה.

## מה צריך לסגור לפני central experiment

Human preservation של זוג אינו תיוג gold לנרטיב ה־Original. נדרש source-label review נפרד לפני אימון/הערכת Narrative Classifier מחקרי. כל 429 source human labels וה־429 source annotation forms עדיין ריקים בריפו; אלה אינם מתמלאים אוטומטית בעקבות source bylines או External LLM Review.

כל 30 הזוגות נשמרים. אין currently accepted subset. כלל עתידי חייב להיות מוגדר מראש ומוחל על כולם; יש לשמור rejects/Borderline ולהציג coverage לפי כותב ונרטיב. No-drift לפי LLM אינו criterion להחליף אימות אנושי.

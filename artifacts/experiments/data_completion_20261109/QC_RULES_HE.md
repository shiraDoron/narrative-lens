# QC וכלל קבלה — לפני ביצועי Narrative Classifier

גרסה קבועה 2026-11-09 עבור 75 מקורות train חדשים. לא הורץ עליהם מסווג נרטיבים ולא נוצר פלט. הפרוטוקול אינו משנה את ה־guards, הספים או את 30 הפלטים הישנים.

## סדר הפעולות

1. קליטה קשיחה: 75 IDs צפויים בלבד, פעם אחת לכל ID, כולם train; ללא legacy30; מקור ופלט נקשרים ב־SHA-256. נשמרים קובצי התשובה המקוריים וה־metadata ללא עריכה. פלט חסר/כפול אינו מומר אוטומטית ל־Original.
2. סינון אוטומטי באותו קוד של הניסוי הקודם: MPNet similarity≥.85; DeBERTa NLI בשני הכיוונים≥.6; entities, numbers, negation, certainty, attribution, framing anchors, future, quotations, input limits, length/completeness. אותם style metrics ו־66 features עם scaling קפוא. אין התאמת סף, scaler fit או classifier prediction.
3. סקירה אנושית עצמאית לכל 75 — גם כשנפסלו אוטומטית. חבילת האדם מכילה רק ID, Original, Rewrite ושדות ריקים; לא authors, labels, guards, scores, legacy rewrites או reviews קודמים.
4. לשמור דירוגים מקוריים; מחלוקת/Borderline מועברת להכרעה נפרדת עם סוקר/ת ומועד. אף תוצאה אינה “מתוקנת” בדיעבד כדי לשפר coverage.

## כלל קבלה קבוע

Style מתקבל אם **human meaning=Yes AND stance=Yes AND style_change=Yes AND semantic_drift=No**. הסימון הוא שיפוט אדם מתועד, לא פלט Claude. `Borderline` אינו Yes. Paraphrase נבדק באותו corpus בנפרד: meaning=Yes, stance=Yes, drift=No; אין חובה שיראה author-style intervention.

Auto pass הוא signal, לא gold. כאשר אדם מאשר ו־guard פסל, יש לשמור את הפסילה ואת נימוק ההכרעה; אין לשנות סף כדי להעלים אותה. כאשר guard עבר ואדם זיהה drift, אין לקבל על בסיס pass. exact copy עשוי לשמור משמעות אך להיכשל בדרישת style; אין ליצור retry משופר על בסיס ציון המסווג.

הסוקר בודק גם quantifiers, modal scope, causal/time relations, מי פועל כלפי מי, אירוניה, מטאפורות ועוצמת מסגור. “נשמר כיוון העמדה” אינו מספיק לשינוי `No one`→`Few people` או `will`→`can`. שלמות טקסט חיצוני אינה מובטחת אם finish_reason אינו זמין; `truncated=False` בממשק הישן הוא default טכני בלבד, וחוסר metadata יישמר בגלוי.

## קישור לחמש הזרועות

כל 105 המקורות נשארים בדוח attrition, לפי class/author/protocol cohort. אחרי שכל הניסיונות הושלמו, common acceptance של P ו־Style קובע fallback סימטרי ל־Original בשתי הזרועות כאשר אחד מהם לא עבר QC, לפי הפרוטוקול המרכזי. Secondary accepted-only משתמש באותה intersection לכל A–E ומדווח selection bias. אין לשנות IDs בין תנאים ואין למלא missing generation בשקט. אין להריץ את הניסוי לפני אימות תוויות המקור.

ה־30 הישנים ו־75 ההמשך מסומנים ב־protocol cohorts שונים: הפרומפט המקורי והמודל אינם ידועים, ולכן אין להציג pooled105 כהעתקה מדויקת של generator אחד. לפני אימון יש לתעד שימוש ב־mixed-protocol training או לתכנן ניתוח רגישות לפי cohort, בלי לבחור גרסה לפי test. לא משכתבים test.

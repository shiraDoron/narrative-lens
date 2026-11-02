# Semantic Verification + Structured Repair — debug subset

בדיקה טכנית בלבד על שש דוגמאות train קיימות. זו אינה הערכה מחקרית, External LLM Review או אימות אנושי. ה־style prompt, ה־guards והספים נשארו קבועים.

## אבחון המנגנון הקודם

11/30 כשלי verification היו כשלי ראיות מילוליות, ולא malformed JSON, שדות חסרים או schema לא תקין. בקובץ הניתוח יש שורה לכל ID ופירוט כל הראיות שנכשלו. 18 קבוצות תיקון שנדחו כללו 41 edits, ולא 18 edits בודדים. הסיבה העיקרית: שימוש בטקסט מה־Original כיעד בתוך Rewrite, לעיתים עם replacement שכבר קיים ב־Rewrite. היו גם patches רחבים ו־no-ops; כשל אחד ביטל קבוצה שלמה. יש להבחין בין כשל טכני זה לבין נכונות הטענה הסמנטית של המודל.

התיקון היחיד שהוחל בניסוי הקודם כלל no-op ומחיקת המשפט על fictitious entities, אף שהטענה קיימת במקור. מעבר בדיקת certainty בעקבות מחיקה כזו אינו ראיה לתיקון משמעות. החוזה החדש דוחה no-op ומחיקות ארוכות.

## תוצאות טכניות

Verification contract valid: 6/6; empty issue lists: 0/6; repair calls: 6; applied proposals: 5/9; changed texts: 4/6. Unit tests: 18 passed.

| ID | verification valid | proposed | applied | changed | old guard failures | new guard failures |
|---|---|---|---|---|---|---|
| creators:417181 | True | 3 | 2 | True | entities\|certainty\|quotations | entities\|certainty\|quotations\|bidirectional_nli |
| creators:421951 | True | 1 | 0 | False | none | none |
| creators:423315 | True | 1 | 1 | True | none | none |
| creators:8b0d99b23d03 | True | 1 | 1 | True | quotations\|bidirectional_nli | quotations\|bidirectional_nli |
| creators:298495 | True | 2 | 0 | False | negation\|attribution | negation\|attribution |
| creators:418904 | True | 1 | 1 | True | quotations\|bidirectional_nli | bidirectional_nli |

כל patch שהוחל שוחזר בדיוק לפי offsets, והטקסט מחוץ לטווח העריכה נשמר. אין החלפת פסקה שלמה ואין מחיקה של יותר משמונה מילים. פירוט היעדים, ההחלפות, הדחיות והפלטים המלאים נשמר ב־subset_model_outputs.json וב־subset_outputs.csv. בדיקות ה־guards הופעלו על כל השש, כולל fallback ללא שינוי. שינוי בדגלים הוא מידע אבחוני בלבד.

## מגבלות שנחשפו ב־debug

גם לאחר תיקון כיוון היעדים, המודל המקומי מציע תיקונים לא מספקים: ב־417181 patch אחד רק מסיר נקודה במקום להחזיר fighting, וב־423315 הוא משנה את מיקום yet במקום לתקן riots/protests או destined. ב־8b0d99b23d03 הוא מחליף רק תחילת ציטוט, משאיר אחריו את שארית הציטוט הישן ויוצר ציטוט פגום. ב־421951 הוצעה מחיקה עם replacement לא ריק והיא נדחתה. אלה תצפיות debug פנימיות על הטקסט וה־patch, ולא External LLM Review חדש. תקינות החוזה אינה מונעת repair סמנטי שגוי או בחירת גבולות עריכה לא מתאימים. בפרט אין לטעון ש־quote restoration הצליח במודל רק מפני שבדיקת היחידה עוברת.

החוזה וההחלה הוכיחו יכולת טכנית בסיסית ב־subset זה; אין מכאן ראיה לשימור משמעות או הצדקה אוטומטית להרצת 30.

תקינות schema אינה recall של verifier: רשימה ריקה עשויה להיות החמצה. הסכמה מונעת ראיות מומצאות אך אינה מונעת בחירת span לא רלוונטי או replacement שגוי. יש לבדוק זאת לפני החלטה על ניסוי נוסף. לא בוצעו retries או בחירת מועמד לפי ציוני guards.

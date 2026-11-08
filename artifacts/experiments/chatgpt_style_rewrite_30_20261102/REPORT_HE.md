# ChatGPT Style Rewrite — 30 train examples

עדכון סטטוס: External LLM Review שסוכם על ידי המשתמש יובא כספירות מצרפיות בלבד. Human Validation עדיין Pending; Author-ID לא מספק ראיה יציבה לירידת author signal. [הדוח העדכני וחבילת האימות האנושי](review_author_analysis_20261102/REPORT_HE.md). הסעיפים האוטומטיים להלן מתעדים את השלב שלפני ייבוא ה־review; סטטוס Pending של review בהם הוא היסטורי.


ניסוי generator חלופי על אותם 30 Original מ־train. ה־CSV התקבל מהמשתמש; לפי דיווחו ChatGPT ראה Original בלבד ולא ראה v2/v3, guards או review קודם. אין request history, גרסת מודל מדויקת, prompt מלא או decoding settings לאימות עצמאי. כאן לא נוצרו שכתובים ולא שונה שום output.

| Metric | v2 | v3 | ChatGPT Rewrite |
| --- | --- | --- | --- |
| automated preservation pass | 6/30 | 9/30 | 22/30 |
| substantial style change | 24/30 | 26/30 | 22/30 |
| both preservation + style | 6/30 | 9/30 | 15/30 |
| exact copies | 0/30 | 0/30 | 0/30 |

## מגבלות והפרדת מקורות ראיה

Automated pass הוא signal בלבד, לא קביעה שהמשמעות נשמרה. substantial הוא proxy תפעולי, לא הוכחה לשינוי author style. Human Validation ו־External LLM Review חדשים לא בוצעו; שניהם Pending. אין מכאן מסקנת generalization או הצלחת פתרון. השוואת generator אינה ניסוי מבוקר בגרסת מודל/תקציב/decoding: פרטים אלה חסרים ל־ChatGPT.

לא סופקו finish_reason או פרטי truncation: שדה truncated=False הוא ברירת ממשק ל־validator הקיים, ולא ראיה שהדור החיצוני הסתיים. בדיקות אורך הקלט המלא פועלות ללא שינוי; guard_complete אינו יכול לאמת עצמאית השלמת generation חיצוני.

## כשלי guards

| guard | v2 | v3 | ChatGPT | new guard type |
| --- | --- | --- | --- | --- |
| attribution | 2 | 2 | 1 | False |
| bidirectional_nli | 10 | 9 | 1 | False |
| certainty | 9 | 8 | 2 | False |
| entities | 2 | 0 | 2 | False |
| framing_anchors | 1 | 1 | 1 | False |
| future_tense | 2 | 0 | 1 | False |
| negation | 5 | 4 | 2 | False |
| numbers | 3 | 1 | 0 | False |
| quotations | 6 | 6 | 2 | False |
| similarity | 1 | 2 | 0 | False |

סוג guard חדש מוגדר ככשל שלא הופיע בשום ID ב־v2 או v3. בנפרד, כשל חדש ברמת ID הוא guard שנכשל כאן לאותו ID אך עבר בשתי הגרסאות הקודמות; אין בכך כשלעצמו הוכחה ל־drift חדש.

לא הופיע סוג guard חדש ברמה הגלובלית. כשלי ID/guard חדשים הופיעו ב־4 דוגמאות: creators:0105f26ef9f1 (negation), creators:421024 (quotations), creators:120177 (attribution|entities), creators:421951 (entities|negation).

כשלי ה־guards השכיחים ביותר ב־ChatGPT: negation, certainty, quotations, entities — 2 דוגמאות לכל guard (ייתכנו כמה כשלי guard לאותה רשומה).

## השוואה אוטומטית לפי ID

Outcome מבוסס Pareto על שני דגלים בלבד: preservation pass ו־substantial style. improved/worsened משמעם שיפור/ירידה בדגל אחד לפחות בלי תנועה הפוכה באחר; mixed משמעו trade-off; unchanged אינו שקילות טקסטים או סיכונים. עוצמת המדדים וכשלי guard מפורטים נשמרו בנפרד.

| Baseline | improved | worsened | unchanged | mixed |
| --- | --- | --- | --- | --- |
| v2 | 16 | 3 | 6 | 5 |
| v3 | 11 | 4 | 8 | 7 |

| ID | ChatGPT failures | new vs both | vs v2 | vs v3 |
| --- | --- | --- | --- | --- |
| creators:0105f26ef9f1 | negation\|certainty\|future_tense | negation | improved | worsened |
| creators:421024 | quotations | quotations | worsened | worsened |
| creators:422329 | none | none | improved | improved |
| creators:417181 | none | none | improved | improved |
| creators:120177 | entities\|attribution | attribution\|entities | unchanged | unchanged |
| creators:212505 | none | none | improved | unchanged |
| creators:421951 | entities\|negation | entities\|negation | worsened | worsened |
| creators:422331 | none | none | improved | unchanged |
| creators:120669 | none | none | unchanged | improved |
| creators:216128 | none | none | improved | unchanged |
| creators:421279 | bidirectional_nli | none | improved | improved |
| creators:419062 | none | none | unchanged | unchanged |
| creators:295188 | none | none | improved | improved |
| creators:423315 | none | none | unchanged | unchanged |
| creators:422146 | none | none | mixed | mixed |
| creators:421853 | none | none | mixed | mixed |
| creators:418620 | none | none | improved | improved |
| creators:114783 | none | none | mixed | mixed |
| creators:224770 | none | none | unchanged | unchanged |
| creators:8b0d99b23d03 | none | none | improved | improved |
| creators:97c9d6b9ac1b | none | none | improved | mixed |
| creators:423545 | none | none | improved | improved |
| creators:298495 | none | none | improved | improved |
| creators:418904 | none | none | mixed | mixed |
| creators:2e34435c6ccf | none | none | mixed | mixed |
| creators:459e183c1d0d | none | none | improved | mixed |
| creators:416436 | quotations | none | worsened | worsened |
| creators:116358 | none | none | improved | improved |
| creators:218236 | certainty | none | unchanged | unchanged |
| creators:418827 | framing_anchors | none | improved | improved |

ברמה האוטומטית יש יותר מעברי preservation ושני התנאים יחד לעומת v2/v3, אך פחות substantial-style flags. זו עדות לאיזון תפעולי אחר, לא הוכחה לשימור משמעות או להסרת סגנון כותב.

## תוצרים ועצירה

[השוואת טקסטים](COMPARISON_30.md), [CSV מזווג](comparison_v2_v3_chatgpt_30.csv), [כל מדדי style](style_metrics_v2_v3_chatgpt.csv), [66 מאפיינים](explicit_style_changes_v2_v3_chatgpt.csv), [guards](rewrite_validation.csv), [blind package](REVIEW_PACKAGE_BLIND_30.md), [שחזור](REPRODUCTION.md). חבילת הביקורת כוללת רק ID, Original ו־ChatGPT Style Rewrite, ללא מחבר, labels, גרסאות קודמות או מדדים. לא בוצע review כחלק מהריצה.

כל 30 הרשומות הן train; התוויות, החלוקה, השדות האנושיים הקודמים, guards, thresholds ו־scaling לא שונו. לא בוצעו retraining, LoRA או test evaluation. עוצרים לפני External LLM Review עצמאי.


## ChatGPT external review and author signals — 2026-11-02

נשמרו ספירות External LLM Review שסיפק המשתמש: Meaning 24 Yes / 6 Borderline / 0 No; Style 24 Yes / 6 Borderline / 0 No; Semantic drift 3 Yes / 11 Borderline / 16 No. **16 clean according to External LLM Review**, לפי drift=No בלבד — לא Human Validation ולא כלל קבלה משולב. אין הכרעות לפי ID, ולכן אין שיוך 16 אלה לרשומות או חישוב חפיפות בין שדות. כל הספירות הנוספות והמקור המצרפי נשמרו בדוח הניתוח. לא נערך review חדש כאן.

| Method | Auto_preservation | External_LLM_meaning_Yes | External_LLM_style_Yes | Clean_no_drift |
| --- | --- | --- | --- | --- |
| v2 | 6 | 10 | 30 | 10 |
| v3 | 9 | 5 | 27 | 5 |
| ChatGPT | 22 | 24 | 24 | 16 |

חבילת Human Validation נוצרה לכל 30 הזוגות עם חמשת השדות הריקים, ללא scores, guards, מחבר, גרסאות קודמות או review. טרם הוחזרה בדיקה אנושית: **Human Validation Pending**. לא נבחר subset של 16. כלל קבלה עתידי אפשרי: human meaning=Yes וגם stance=Yes וגם style=Yes, המוחל על כל ה־30; לא הוחל כעת.

| Author-ID setting | Accuracy | Macro-F1 |
| --- | --- | --- |
| Original | 23.33% | 0.1964 |
| Rewrite | 22.00% | 0.1867 |
| Original_fit_Rewrite_dev | 28.00% | 0.2129 |

Author-ID השתמש בכל 30 זוגות ה־train, בתשעה כותבים וב־66 מאפייני style קיימים. Logistic Regression זהה מבחינת pipeline/פרמטרים, עם fit נפרד לכל representation, שתי חלוקות stratified לכל אחד מחמישה seeds ו־scaling בתוך fold בלבד. במסלול המשני אותו fitted Original classifier נבחן על paired Rewrite. זהו development closed-set, לא test או unseen-author evaluation. הירידה הממוצעת קטנה: accuracy −1.33pp ו־Macro-F1 −0.0097; accuracy יורד רק ב־2/5 seeds, ובמסווג המקור הקבוע עולה ל־28%. **אין כרגע ראיה יציבה שה־author signal ירד.** אין להציג את הממוצע הקטן כהסרת סגנון כותב מוכחת או כהשפעה על narrative generalization.

החידוש אינו בהכרח Text Style Transfer חדש. השאלה המחקרית היא האם Narrative Classifier משתמש ב־author style כ־shortcut, והאם הפחתת author-specific style תוך שמירת narrative משפרת generalization ל־unseen authors. ChatGPT rewrite הוא intervention candidate, לא contribution בפני עצמו. לא שונו prompt/guards/thresholds/split, לא אומן Narrative Classifier ולא בוצעו LoRA או test evaluation. אומנו רק probes זמניים של Author-ID, ללא שמירת weights.

[Detailed analysis](review_author_analysis_20261102/REPORT_HE.md) · [Human package](review_author_analysis_20261102/HUMAN_VALIDATION_30.md) · [Reproduce](review_author_analysis_20261102/REPRODUCTION.md)
<!-- END_CHATGPT_REVIEW_AUTHOR_20261102 -->

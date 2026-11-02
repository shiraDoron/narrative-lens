# ChatGPT Style Rewrite — 30 train examples

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

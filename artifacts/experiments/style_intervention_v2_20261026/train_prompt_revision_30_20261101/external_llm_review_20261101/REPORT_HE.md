## New Normalized — External LLM Review 2026-11-01

יובא קובץ הבדיקה החיצונית של כל 30 ה־New Normalized, בהתאמת ID מלאה למדגם train בלבד. ההכרעות להלן הן דירוגי LLM שסופקו, לא שיפוט חדש של סוכן הייבוא ולא אימות אנושי. גרסת המודל, prompt ההערכה ומועד ההערכה המדויק לא סופקו. הקובץ אינו מכיל hash או טקסט שנסקר; שיוך הגרסאות נשען על ה־IDs והקשר המסירה. אין לטעון לבדיקה עיוורת או לעצמאות בין הסבבים.

**שם הבדיקה: External LLM Review — New Normalized.** היא נשמרת בנפרד מ־Human Validation ומבדיקת ה־Old Normalized הקודמת.

| שדה חיצוני | Yes | Borderline | No |
| --- | --- | --- | --- |
| meaning_preserved | 10 | 15 | 5 |
| stance_preserved | 29 | 1 | 0 |
| attribution_preserved | 29 | 0 | 1 |
| certainty_preserved | 28 | 2 | 0 |
| style_change_valid | 30 | 0 | 0 |
| semantic_drift | 20 | 0 | 10 |

Meaning Preserved: **10/30 Yes, ‏15/30 Borderline, ‏5/30 No**. שינוי style אמיתי לפי ה־External LLM Review: **30/30**; זהו דירוג הבודק החיצוני ולא אימות אנושי.

### סיווג פערים ביחס ל־LLM

"Positive" פירושו איתות לסיכון בשימור משמעות. True/False מתארים התאמה ל־LLM בלבד, לא אמת מחקרית מאומתת. פסילה אוטומטית ו־semantic_drift=Yes מסווגת True Positive; פסילה עם meaning=Yes ו־drift=No היא False Positive; מעבר עם אותו אישור הוא True Negative; מעבר עם drift=Yes או Borderline משמעותי הוא False Negative. כל 15 מקרי ה־Borderline בקובץ מסומנים גם semantic_drift=Yes במקור, ולכן הסיווג נשען על דגל מפורש, בלי להמיר meaning=Borderline ל־No. שדה המשמעות המקורי נשמר, וכן קובץ Borderline נפרד ופירוט בכל קטגוריה.

| סיווג ביחס ל־LLM | סה״כ | Meaning Yes | Meaning Borderline | Meaning No |
| --- | --- | --- | --- | --- |
| True Positive | 19 | 0 | 14 | 5 |
| False Positive | 5 | 5 | 0 | 0 |
| True Negative | 5 | 5 | 0 | 0 |
| False Negative | 1 | 0 | 1 | 0 |

פסילות שנראו מוצדקות לפי ה־LLM (True Positive): creators:422329, creators:417181, creators:422331, creators:216128, creators:421279, creators:295188, creators:422146, creators:421853, creators:114783, creators:8b0d99b23d03, creators:97c9d6b9ac1b, creators:423545, creators:298495, creators:418904, creators:2e34435c6ccf, creators:416436, creators:116358, creators:218236, creators:418827.

פסילות שנראו False Positives לפי ה־LLM: creators:0105f26ef9f1, creators:120177, creators:212505, creators:418620, creators:459e183c1d0d.

עברו אוטומטית אך קיבלו Borderline/No: creators:423315 — במקרה זה Borderline, ואין מקרה שעבר וקיבל No.

דוגמאות הכשל המרכזיות לפי הבודק: `417181` — semantic drift והתחזקות certainty, לצד שינוי ייחוס; `8b0d99b23d03` — שינוי הציטוט המיוחס ל־F. Scott Fitzgerald ושינוי מטאפורת “two countries”; `423545` — החלשת stance/המסגור באמצעות הסרת “right-wing hack” והחלשת המטאפורה (למרות שדה stance_preserved=Yes, שנשמר כמות שהוא); `298495` — שינוי עובדתי מ־strangers ל־anonymous sources; `418904` — שינוי ציטוט ישיר. אלו פירושים לתוצאות ה־LLM שסופקו, ולא הכרעות אנושיות חדשות או אימות פרטני של כל guard.

שימור מחמיר לצורך סיכום בלבד (meaning, stance, attribution, certainty כולם Yes וגם semantic_drift=No): **10/30**; שימור מחמיר ושינוי style=Yes יחד: **10/30**. זהו חיתוך תיאורי של שדות חיצוניים, לא שינוי סף קבלה או מסנן.

מבין הפסילות האוטומטיות, 5 דורגו כשימור מחמיר — מועמדים ל־false positives ביחס לבודק החיצוני, לא הוכחת תקינות. מבין המעברים האוטומטיים, 1 קיבלו meaning שאינו Yes. אין להמיר אי־הסכמה עם LLM ל־false positive/negative מאומת. Borderline נשמר בנפרד ואינו נספר כהצלחה; semantic_drift=Yes הוא קביעת ה־LLM בלבד.

`creators:120669`: הבודק מציין שהטעות Obama/Washington הקודמת תוקנה. `212505`: הבודק רואה ב־10→ten שינוי עיצוב בלבד ומאשר שימור. `419062` ו־`224770` מאושרים לשימור ולסגנון; לעומתם `423315`, שעבר בסינון, דורג Borderline בגלל riots→protests ו־going to lose→destined to lose. `421951` עבר אוטומטית ואושר חיצונית; זו עדיין אינה אמת אנושית. `298495` דורג No במשמעות בגלל strangers→anonymous sources, אף ששדה attribution דורג Yes; ההבדל בין השדות נשמר. `114783` דורג Borderline עם פגיעה בנאמנות לציטוט. אין להסיק מכך שדגלי negation/attribution שלו אומתו פרטנית.

ה־LLM דירג שינוי style כ־Yes בכל 30 המקרים. לעומת זאת ה־proxy האוטומטי סימן 24/30. בבדיקה החיצונית הקודמת של Old Normalized היו meaning=Yes ב־27/30 ו־style=Yes ב־9/30; אין זו השוואה מבוקרת בין מעריכים, ואין לערבב ספירות חיצוניות עם 23→6 ו־10→24 האוטומטיות. התמונה התיאורית היא שינוי סגנוני רחב יותר לצד יותר הסתייגויות משימור משמעות.

לא שונו prompt, guards, ספים, טקסטים, תוויות, split, test או שדות human review; לא הורצו מודל שופט, שכתוב נוסף או אימון. הבדיקה אינה פותחת את שער האימות האנושי לאימון. עוצרים לדיון בתוצאות לפני כל ניסוי או כוונון נוסף.

**ה־prompt החדש מצליח לייצר שינוי סגנוני משמעותי, אבל מגדיל את הסיכון ל־semantic drift. הבדיקות האוטומטיות מזהות חלק מהכשלים, אך יש גם false positives וגם מקרים שהן אינן מספיקות לבדן.** זו מסקנת הפיתוח הנוכחית על המדגם המכוון ובהסתמך על דירוגי ה־External LLM Review, לא אומדן על test.


| ID | Auto pass | Auto reasons | סיווג ביחס ל־LLM | meaning_preserved | stance_preserved | attribution_preserved | certainty_preserved | style_change_valid | semantic_drift | הערות LLM |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| creators:0105f26ef9f1 | False | certainty\|future_tense | False Positive | Yes | Yes | Yes | Yes | Yes | No | Meaning and stance preserved; substantial style change. |
| creators:421024 | True |  | True Negative | Yes | Yes | Yes | Yes | Yes | No | Meaning preserved; slight softening, but stance remains. |
| creators:422329 | False | bidirectional_nli | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Changes 'less than a decade' and reframes blame; mild drift. |
| creators:417181 | False | entities\|certainty\|quotations | True Positive | No | Yes | No | Borderline | Yes | Yes | Strengthens certainty and alters attribution structure. |
| creators:120177 | False | certainty | False Positive | Yes | Yes | Yes | Yes | Yes | No | Core meaning and framing preserved. |
| creators:212505 | False | numbers | False Positive | Yes | Yes | Yes | Yes | Yes | No | Safe rewrite; 10→ten is formatting only. |
| creators:421951 | True |  | True Negative | Yes | Yes | Yes | Yes | Yes | No | Meaning preserved with substantial style change. |
| creators:422331 | False | bidirectional_nli | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Adds interpretation about hard work/tradespeople. |
| creators:120669 | True |  | True Negative | Yes | Yes | Yes | Yes | Yes | No | Previous Obama/Washington error is fixed. |
| creators:216128 | False | entities | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | 'Bet' becomes 'strategy', altering nuance. |
| creators:421279 | False | certainty\|bidirectional_nli | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | 'Answer revealed' becomes 'explanation made public'. |
| creators:419062 | True |  | True Negative | Yes | Yes | Yes | Yes | Yes | No | Meaning and stance preserved. |
| creators:295188 | False | bidirectional_nli | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Final sentence is not fully equivalent. |
| creators:423315 | True |  | False Negative | Borderline | Yes | Yes | Borderline | Yes | Yes | 'Riots'→'protests' and 'going to lose'→'destined to lose'. |
| creators:422146 | False | negation\|bidirectional_nli | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Softens bullying framing and changes Epstein wording. |
| creators:421853 | False | negation | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Expands proverb with added interpretation. |
| creators:418620 | False | future_tense | False Positive | Yes | Yes | Yes | Yes | Yes | No | Meaning and certainty preserved. |
| creators:114783 | False | numbers\|negation\|attribution\|quotations | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Breaks quote fidelity; core meaning remains. |
| creators:224770 | True |  | True Negative | Yes | Yes | Yes | Yes | Yes | No | Meaning and stance preserved. |
| creators:8b0d99b23d03 | False | quotations\|bidirectional_nli | True Positive | No | Borderline | Yes | Yes | Yes | Yes | Alters direct quote and changes 'two countries' metaphor. |
| creators:97c9d6b9ac1b | False | certainty\|bidirectional_nli | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Shifts certainty and imagery. |
| creators:423545 | False | certainty\|quotations\|bidirectional_nli | True Positive | No | Yes | Yes | Yes | Yes | Yes | Removes 'right-wing hack' and weakens metaphor. |
| creators:298495 | False | negation\|attribution | True Positive | No | Yes | Yes | Yes | Yes | Yes | Changes 'strangers' to 'anonymous sources'. |
| creators:418904 | False | quotations\|bidirectional_nli | True Positive | No | Yes | Yes | Yes | Yes | Yes | Alters direct quote and rhetorical claim. |
| creators:2e34435c6ccf | False | negation\|certainty\|similarity | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Slightly strengthens inevitability/causal framing. |
| creators:459e183c1d0d | False | certainty | False Positive | Yes | Yes | Yes | Yes | Yes | No | Restores one-time uncertainty and preserves attribution. |
| creators:416436 | False | quotations | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Softens 'moral and economic superiority' to 'virtues'. |
| creators:116358 | False | numbers | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Mostly preserved, but relational framing shifts. |
| creators:218236 | False | certainty | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Normative claim is slightly reframed. |
| creators:418827 | False | framing_anchors\|bidirectional_nli | True Positive | Borderline | Yes | Yes | Yes | Yes | Yes | Framing is softened though factual structure remains. |

| Auto pass | Meaning LLM | N |
| --- | --- | --- |
| True | Yes | 5 |
| True | Borderline | 1 |
| True | No | 0 |
| False | Yes | 5 |
| False | Borderline | 14 |
| False | No | 5 |

מועמדי false positive ביחס ל־LLM: creators:0105f26ef9f1, creators:120177, creators:212505, creators:418620, creators:459e183c1d0d

מעבר אוטומטי עם הסתייגות חיצונית: creators:423315

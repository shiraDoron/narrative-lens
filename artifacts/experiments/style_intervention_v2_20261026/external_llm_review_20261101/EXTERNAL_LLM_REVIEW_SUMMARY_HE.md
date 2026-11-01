# External LLM Evaluation / LLM External Review — סיכום 30 דוגמאות

**מקור:** קובץ CSV שהמשתמשת העבירה מבדיקת ChatGPT נפרדת. התוצאות שלהלן הן דיווחי אותו LLM; לא בוצעה כאן הכרעה חדשה בתוכן.
**סטטוס:** הערכת LLM חיצונית בלבד. אין אימות אנושי חדש; human_verified נשאר False. אין שינוי בתוויות, בספים, בחלוקה, ב־test או בקוד האימון. לא בוצע אימון מחדש.

## הספירות כפי שהתקבלו

| שדה בהערכה | Yes / אושר | No / נכשל | Borderline | Unclear |
| --- | --- | --- | --- | --- |
| נכונות הצעת הנרטיב | 27 | 3 | 0 | 3 |
| paraphrase_meaning_preserved | 23 | 4 | 3 | — |
| normalized_meaning_preserved | 27 | 3 | 0 | — |
| paraphrase_style_change_valid | 14 | 14 | 2 | — |
| normalized_style_change_valid | 9 | 20 | 1 | — |

Unclear מתייחס לתווית שהציע ה־LLM החיצוני, ולא לשינוי שבוצע בתווית הדאטה. כל הספירות מתוך 30 הדוגמאות שנבחרו במכוון.

## השוואה למסננים האוטומטיים

| תנאי | עבר סינון אוטומטי | שימור משמעות לפי LLM | N |
| --- | --- | --- | --- |
| Paraphrase | False | Borderline | 3 |
| Paraphrase | False | No | 4 |
| Paraphrase | False | Yes | 7 |
| Paraphrase | True | Yes | 16 |
| Normalized | False | No | 3 |
| Normalized | False | Yes | 4 |
| Normalized | True | Yes | 23 |

אי־הסכמה אינה הוכחה שהמסנן טעה: הסינון דורש גם נאמנות מילולית לציטוטים, ישויות והסתייגויות, בעוד שיפוט LLM יכול להתייחס למשמעות כללית. הספים והפסילות המקוריים נשארו ללא שינוי.

## מקרים שה־LLM תיאר כסינון מחמיר או כפער בהגדרת השימור

- **creators:421024**: לפי ההערכה החיצונית: Both rewrites preserve the conservative/critical stance toward 'naked dressing'; automatic quotation rejection appears overly strict.
- **creators:423545**: לפי ההערכה החיצונית: Paraphrase is grammatically awkward ('been hoist') but semantic content is preserved; automatic NLI rejection looks too strict. Style barely changes.
- **creators:418904**: לפי ההערכה החיצונית: Changing 'celebrate' to 'mark' inside a quote is undesirable for quote fidelity but preserves propositional meaning; style is essentially unchanged.
- **creators:120177**: לפי ההערכה החיצונית: Meaning is preserved, but the rhetorical voice ('Folks', slippery slope, war on Christmas) remains strongly intact; proxy overstates style change.

## מקרים שסומנו כפגיעה במשמעות, certainty או attribution

- **creators:0105f26ef9f1** — Paraphrase: No; Normalized: Yes. הערת ה־LLM: Paraphrase contains an added meta-preface and slightly compresses meaning; normalized preserves the stance and meaning.
- **creators:417181** — Paraphrase: No; Normalized: No. הערת ה־LLM: Both rewrites shift certainty/attribution; paraphrase also adds 'supposed champion of civil rights'. Style changes are real but semantic preservation is not strict enough.
- **creators:120669** — Paraphrase: Yes; Normalized: No. הערת ה־LLM: Paraphrase preserves meaning. Normalized incorrectly shifts the Thanksgiving-address subject from Obama to Washington, a clear semantic failure.
- **creators:298495** — Paraphrase: Borderline; Normalized: Yes. הערת ה־LLM: Paraphrase adds specificity ('letters') not present in the original and slightly changes the God phrasing; normalized is unchanged.
- **creators:459e183c1d0d** — Paraphrase: No; Normalized: No. הערת ה־LLM: Paraphrase drops 'allegedly one-time', changes former Berkeley status, and turns a claimed 90% allocation into an asserted earmark. Normalized also drops the 'allegedly one-time' qualification.
- **creators:116358** — Paraphrase: No; Normalized: Yes. הערת ה־LLM: Paraphrase removes the important Obama relationship ('close friend and confidant'), so strict meaning preservation fails. Normalized is exact.
- **creators:218236** — Paraphrase: Borderline; Normalized: Yes. הערת ה־LLM: Paraphrase changes 'are supposed to be' into 'claim to be', subtly shifting stance/attribution. Normalized preserves the original claim closely.
- **creators:418827** — Paraphrase: Borderline; Normalized: Yes. הערת ה־LLM: Paraphrase turns rhetorical 'brandish X over Y' into the more concrete claim 'replace Y with X' and alters framing. Normalized is exact.

## שילוב שימור משמעות ושינוי סגנון לפי ה־LLM

| תנאי | צירוף דירוגים | N |
| --- | --- | --- |
| paraphrase | meaning_Borderline__style_Yes | 3 |
| paraphrase | meaning_No__style_Borderline | 1 |
| paraphrase | meaning_No__style_Yes | 3 |
| paraphrase | meaning_Yes__style_Borderline | 1 |
| paraphrase | meaning_Yes__style_No | 14 |
| paraphrase | meaning_Yes__style_Yes | 8 |
| normalized | meaning_No__style_No | 1 |
| normalized | meaning_No__style_Yes | 2 |
| normalized | meaning_Yes__style_Borderline | 1 |
| normalized | meaning_Yes__style_No | 19 |
| normalized | meaning_Yes__style_Yes | 7 |

## מסקנה ראשונית מהבדיקה החיצונית

לפי הערכת ה־LLM שהתקבלה, הבעיה אינה רק בסינון: במקרים רבים Normalized שומר משמעות אך כמעט אינו משנה סגנון. במקרים שבהם השינוי הסגנוני גדול יותר יש לעיתים פגיעה בפרטים סמנטיים. זו מסקנה אבחונית מהדירוגים שנמסרו, לא אימות עצמאי או מסקנה על כל הדאטה.
שינוי סגנון שסומן Yes אינו מוכיח הסרת מידע על הכותב או הגעה לסגנון יעד אחיד. הבדיקה אינה מודדת Author Identification, Macro-F1 או generalization, ואינה מצדיקה טענה חדשה להסרת shortcut או מעבר ל־LoRA.

## מה עדיין חסר

אימות של סוקר/ת אדם לתוויות ולשימור משמעות/סגנון עדיין ממתין. גרסת מודל ה־ChatGPT, prompt ההערכה ותאריך ההערכה לא סופקו ואין להשלים אותם בניחוש. הדירוג אינו עיוור: החבילה הציגה כותב, הצעת תווית ותוצאות מסננים. לא חושב agreement בין בני אדם, ולא ניתן להניח עצמאות מההצעות הקודמות.

## כל 30 הדוגמאות — כפי שדורגו חיצונית

| ID | נרטיב LLM | הצעת נרטיב אושרה | P משמעות | N משמעות | P סגנון | N סגנון | הערת LLM |
| --- | --- | --- | --- | --- | --- | --- | --- |
| creators:0105f26ef9f1 | Left-wing | Yes | No | Yes | Yes | Yes | Paraphrase contains an added meta-preface and slightly compresses meaning; normalized preserves the stance and meaning. |
| creators:421024 | Right-wing | Yes | Yes | Yes | Yes | Yes | Both rewrites preserve the conservative/critical stance toward 'naked dressing'; automatic quotation rejection appears overly strict. |
| creators:422329 | Unclear | No | Yes | Yes | Yes | Yes | Excerpt blames both parties for debt; the text itself does not cleanly support a right-wing narrative label. |
| creators:417181 | Right-wing | Yes | No | No | Yes | Yes | Both rewrites shift certainty/attribution; paraphrase also adds 'supposed champion of civil rights'. Style changes are real but semantic preservation is not strict enough. |
| creators:120177 | Right-wing | Yes | Yes | Yes | No | No | Meaning is preserved, but the rhetorical voice ('Folks', slippery slope, war on Christmas) remains strongly intact; proxy overstates style change. |
| creators:212505 | Right-wing | Yes | Yes | Yes | Yes | Yes | Main claim and pro-Trump/pro-tax-cut framing are preserved; style is meaningfully simplified. |
| creators:421951 | Unclear | No | Yes | Yes | No | Yes | The excerpt is historical/satirical and does not itself establish a left-wing political narrative. Paraphrase is essentially unchanged; normalized changes style. |
| creators:422331 | Right-wing | Yes | Yes | Yes | No | Yes | Both preserve the anti-DSA framing. Paraphrase barely changes; normalized changes diction and phrasing. |
| creators:120669 | Right-wing | Yes | Yes | No | Yes | Yes | Paraphrase preserves meaning. Normalized incorrectly shifts the Thanksgiving-address subject from Obama to Washington, a clear semantic failure. |
| creators:216128 | Right-wing | Yes | Yes | Yes | No | Yes | Both preserve the pro-growth tax-cut argument; paraphrase is nearly identical, normalized makes a modest real style change. |
| creators:421279 | Left-wing | Yes | Yes | Yes | No | No | Both rewrites are exact copies; no style intervention occurred. |
| creators:419062 | Left-wing | Yes | Yes | Yes | No | No | Only a tiny lexical substitution ('oozed'→'infiltrated'); not a meaningful style intervention. |
| creators:295188 | Left-wing | Yes | Yes | Yes | No | No | Only 'buttressed'→'bolstered'; meaning preserved but style essentially unchanged. |
| creators:423315 | Left-wing | Yes | Yes | Yes | No | No | Minor wording/negation changes only; no meaningful style neutralization. |
| creators:422146 | Left-wing | Yes | Yes | Yes | No | No | Meaning preserved; edits are tiny and leave the sarcastic/rhetorical voice intact. |
| creators:421853 | Right-wing | Yes | Yes | Yes | No | No | Meaning preserved; mostly synonym substitutions, with the rhetorical construction unchanged. |
| creators:418620 | Right-wing | Yes | Yes | Yes | Yes | No | Paraphrase restructures three sentences into one and preserves the anti-left framing; normalized is an exact copy. |
| creators:114783 | Right-wing | Yes | Yes | Yes | Yes | No | Paraphrase meaning is preserved and wording is noticeably changed; normalized is effectively unchanged. |
| creators:224770 | Right-wing | Yes | Yes | Yes | Borderline | No | Paraphrase preserves meaning but changes mainly lexical choices rather than deeper author style; normalized is exact. |
| creators:8b0d99b23d03 | Unclear | No | Yes | Yes | No | No | The excerpt contrasts two social worlds but does not clearly express a left/right stance by itself. Rewrites are effectively unchanged. |
| creators:97c9d6b9ac1b | Left-wing | Yes | Yes | Yes | No | No | Meaning remains essentially intact, including anti-Trump framing. Changes are too small to count as meaningful style intervention. |
| creators:423545 | Left-wing | Yes | Yes | Yes | No | No | Paraphrase is grammatically awkward ('been hoist') but semantic content is preserved; automatic NLI rejection looks too strict. Style barely changes. |
| creators:298495 | Left-wing | Yes | Borderline | Yes | Yes | No | Paraphrase adds specificity ('letters') not present in the original and slightly changes the God phrasing; normalized is unchanged. |
| creators:418904 | Left-wing | Yes | Yes | Yes | No | No | Changing 'celebrate' to 'mark' inside a quote is undesirable for quote fidelity but preserves propositional meaning; style is essentially unchanged. |
| creators:2e34435c6ccf | Left-wing | Yes | Yes | Yes | Yes | No | Both preserve the anti-Trump corruption framing. Paraphrase changes wording substantially; normalized is only a light lexical edit. |
| creators:459e183c1d0d | Right-wing | Yes | No | No | Yes | No | Paraphrase drops 'allegedly one-time', changes former Berkeley status, and turns a claimed 90% allocation into an asserted earmark. Normalized also drops the 'allegedly one-time' qualification. |
| creators:416436 | Right-wing | Yes | Yes | Yes | Yes | Borderline | Paraphrase and normalized preserve the anti-socialism/pro-capitalism stance. Paraphrase clearly changes style; normalized changes less and keeps much of the rhetoric. |
| creators:116358 | Right-wing | Yes | No | Yes | Borderline | No | Paraphrase removes the important Obama relationship ('close friend and confidant'), so strict meaning preservation fails. Normalized is exact. |
| creators:218236 | Right-wing | Yes | Borderline | Yes | Yes | No | Paraphrase changes 'are supposed to be' into 'claim to be', subtly shifting stance/attribution. Normalized preserves the original claim closely. |
| creators:418827 | Left-wing | Yes | Borderline | Yes | Yes | No | Paraphrase turns rhetorical 'brandish X over Y' into the more concrete claim 'replace Y with X' and alters framing. Normalized is exact. |

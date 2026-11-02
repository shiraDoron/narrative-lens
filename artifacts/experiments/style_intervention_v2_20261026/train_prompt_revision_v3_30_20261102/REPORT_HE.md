# Prompt Revision v3 — אותם 30 מקורות train בלבד

## תכנון מבוקר

ה־prompt של v2 נשמר בשלמותו ונוספה הרחבת הגנות ממוקדת: אפיון אירוע, עוצמה רטורית, ודאות בהקשר, תפקידי משתתפים, כמתים, ציטוטים verbatim, מטאפורות וללא פרשנות מומצאת. הקלט למודל כולל Original בלבד, לצד הוראות ה־prompt; בלי גרסאות קודמות, תוויות, כותבים, מדדים או דירוגי review. הדוגמאות בהרחבת ה־prompt הן הגנות שהתבקשו מתוך ניתוח שגיאות train, ולכן זהו ניסוי פיתוח על מקרים מוכרים ולא מבחן בלתי תלוי.

אותו Qwen2.5-3B-Instruct Q4_K_M קפוא, runtime, ארבעה slots, temperature=0, seed=20261026, max_tokens=320, repeat_penalty=1, top_k=1, top_p=1, min_p=0 ו־cache_prompt=True. מועמד יחיד לכל מקור; אין בחירה על פי ציונים ואין ניסיונות חוזרים לשיפור פלט. אותו קוד validator ואותם מודלי MPNet/NER/DeBERTa, ספי similarity≥0.85 ו־NLI≥0.6, בדיקות אורך/קטיעה ואותם מדדי style ו־66 מאפיינים מפורשים. לא הותאמו guards כדי לקבל מספרים במילים או חלופות לקסיקליות.

## תוצאות אוטומטיות בלבד

| Metric | v2 | v3 |
| --- | --- | --- |
| automatic_pass | 6 | 9 |
| substantial_style_proxy | 24 | 26 |
| both | 6 | 9 |
| exact_copies | 0 | 0 |

מעבר בדיקות אינו הוכחה ל־semantic-safe, ו־substantial style הוא proxy. רק בדיקה חיצונית נפרדת יכולה לספק דירוגים חדשים; אין כאן ספירות No/Borderline עבור v3. לא נמדדו generalization, Macro-F1 או Author Identification חדשים.

נוספו 4 מעברים אוטומטיים לעומת v2: creators:0105f26ef9f1, creators:212505, creators:422331, creators:216128. אבד מעבר קודם ב־creators:120669. אין להציג את ההפרש נטו כתיקון של כל שגיאות ה־review.

שחזורים מילוליים נקודתיים מתוך ה־error analysis, ללא הכרעה על כל הרשומה: creators:422329: doubling in less than a decade; creators:216128: the House and Senate; creators:422146: trade war; creators:422146: the Jeffrey Epstein files; creators:423545: the right-wing hack. בכל המקרים האלה proxy הסגנון עדיין substantial.

קטיעות פלט: 0; הפרות דיאגנוסטיקת תוכן ציטוט verbatim: 6. כשל זה נרשם בנפרד ואינו משנה את guard הציטוטים הקיים.

## הדוגמאות המרכזיות — בדיקות spans ראשוניות בלבד

| ID | תכונה | ביטוי מקור ב־v3 | תבנית סיכון ב־v2 | תבנית סיכון ב־v3 | v3 pass | v3 style |
| --- | --- | --- | --- | --- | --- | --- |
| creators:417181 | funding_rank | False | True | True | False | True |
| creators:417181 | ironic_fighting_quote | False | False | False | False | True |
| creators:8b0d99b23d03 | Fitzgerald_verbatim | False | True | True | False | True |
| creators:8b0d99b23d03 | countries_metaphor | False | True | False | False | True |
| creators:423545 | insult_intensity | True | True | False | False | True |
| creators:423545 | bomb_metaphor | False | True | False | False | True |
| creators:298495 | sender_property | False | True | True | False | True |
| creators:418904 | quoted_celebrate | False | True | True | False | True |
| creators:423315 | event_characterization | False | True | True | True | True |
| creators:423315 | inevitability | False | True | True | True | True |
| creators:418904 | new_branded_word | False | False | True | False | True |
| creators:418904 | new_specific_surrender_day | False | False | True | False | True |
| creators:417181 | new_pseudonymous_word | False | False | True | False | True |
| creators:8b0d99b23d03 | Saturday_retention | False | False | False | False | True |
| creators:8b0d99b23d03 | Sunday_retention | False | False | False | False | True |
| creators:120669 | Obama_Washington_reference | False | False | True | False | True |
| creators:421951 | participant_role | False | True | True | True | True |
| creators:212505 | quantifier | False | True | True | True | True |
| creators:459e183c1d0d | net_worth_eligibility | False | True | False | False | True |

התבניות והביטויים מפורטים ב־[targeted_textual_spotchecks.csv](targeted_textual_spotchecks.csv). הן מסמנות תופעות טקסטואליות, לא פוסקות אם המשמעות נשמרה. היעלמות תבנית בעייתית בלי שחזור ביטוי המקור מחייבת בדיקה חיצונית.

ממצאים מילוליים לבדיקת ההמשך: ב־423545 ניתן לבדוק אם right-wing hack הוחזר, בלי להסיק שכל המטאפורה או דרגת הוודאות שוחזרו. ב־423315 יש לבדוק בנפרד riots/protests ו־going to/destined; ב־298495 את strangers/anonymous sources; וב־8b0d99b23d03 וב־418904 את הציטוטים עצמם. הופעה חדשה של branded, pseudonymous או typically surrendered on this day, אובדן Saturday/Sunday, או החזרת President Washington's Thanksgiving addresses במקום הכינוי his, מסומנים כחשדות חדשים לבדיקה בלבד. אין כאן שיפוט LLM חיצוני או הכרעת semantic drift סופית.

| ID | סיכון קודם | Original span | v2 span | תצפית מילולית ב־v3 | v3 pass | v3 style |
| --- | --- | --- | --- | --- | --- | --- |
| creators:417181 | Likely modifies the original funding claim; the rewrite states financier status in an appositive and moves appears to the existence of allegations. | was likely the Southern Poverty Law Center | the SPLC, the primary financier | different_form_requires_external_review | False | True |
| creators:417181 | The quoted ironic fighting claim is removed. | denouncing and "fighting" the very same groups in public | while publicly denouncing them | v2_span_still_present | False | True |
| creators:417181 | Hiding funding from donors is not the same relation as obscuring donors' contributions. | hide funding from their donors | obscure its donors' contributions | different_form_requires_external_review | False | True |
| creators:417181 | Full organizational name and United States spelling are replaced with acronyms; identity may be equivalent, but literal preservation fails. | Southern Poverty Law Center | SPLC | both_spans_present_or_overlapping | False | True |
| creators:423315 | Violent/disorderly event characterization is broadened/softened to protests; lexical polarity and stance intensity change. | George Floyd riots | George Floyd protests | v2_span_still_present | True | True |
| creators:423315 | Retrospective future loss is reframed as destined/inevitable, strengthening fatalistic certainty. | the war we were going to lose in Afghanistan | the war we were destined to lose in Afghanistan | v2_span_still_present | True | True |
| creators:8b0d99b23d03 | Rewrites the directly attributed Fitzgerald quotation. | The rich are different from you and me. | The rich are distinct from the rest of us. | v2_span_still_present | False | True |
| creators:8b0d99b23d03 | Removes the class-divide countries metaphor in favor of geographic regions. | two countries, both inside America's borders | two distinct regions within America's borders | different_form_requires_external_review | False | True |
| creators:423545 | Removes the derogatory hack evaluation while retaining political direction. | the right-wing hack | the right-wing figure | original_span_restored_v2_span_absent | False | True |
| creators:423545 | Probable ignorance becomes possible unfamiliarity, weakening the likelihood claim. | probably doesn't know | may not be familiar | different_form_requires_external_review | False | True |
| creators:423545 | Generalizes away bomb maker and explosion; hoisted by a big one also becomes generic predicament. | a bomb maker being blown sky-high by his own creation | a creator being destroyed by the very thing they've devised | different_form_requires_external_review | False | True |
| creators:298495 | Unfamiliar people need not be anonymous, and anonymity does not imply being a stranger. | Most of the hate mail came from strangers | Most of the hate mail came from anonymous sources | v2_span_still_present | False | True |
| creators:298495 | Insistence/experience is reframed as a claim, potentially adding epistemic distance. | insisting she's acquainted with a different version of God | who claims to know a different version of God | different_form_requires_external_review | False | True |
| creators:418904 | Changes a directly quoted word, violating verbatim quotation preservation even if related in ordinary usage. | We didn't celebrate the Fourth of July, | We didn't mark the Fourth of July, | v2_span_still_present | False | True |
| creators:418904 | Removes the explicit bloody consequence and changes racialized rhetorical imagery; cruel is not the same detail. | Black backs whipped bloody | black backs who were beaten with cruel whips | different_form_requires_external_review | False | True |
| creators:423315 | event characterization | George Floyd riots | George Floyd protests | v2_span_still_present | True | True |
| creators:423315 | certainty in context | going to lose | destined to lose | v2_span_still_present | True | True |

original_span_restored_v2_span_absent מציין שחזור מילולי של הביטוי שנפגע, לא פתרון סמנטי סופי. v2_span_still_present מציין שהביטוי הבעייתי עדיין מופיע; different_form_requires_external_review אינו אישור או פסילה. למקרי Borderline הקודמים ולסיכוני ה־FP/TN ראו [כל בדיקות ה־spans](focused_span_checks.csv).

## דגלים שנפתרו או נוספו — לא הכרעת drift

| ID | Removed flags | Added flags | v2 pass | v3 pass | v3 style |
| --- | --- | --- | --- | --- | --- |
| creators:0105f26ef9f1 | certainty\|future_tense |  | False | True | True |
| creators:421024 |  |  | True | True | True |
| creators:422329 |  |  | False | False | True |
| creators:417181 | entities |  | False | False | True |
| creators:120177 |  | negation | False | False | True |
| creators:212505 | numbers |  | False | True | True |
| creators:421951 |  |  | True | True | True |
| creators:422331 | bidirectional_nli |  | False | True | True |
| creators:120669 |  | bidirectional_nli | True | False | True |
| creators:216128 | entities |  | False | True | True |
| creators:421279 |  |  | False | False | False |
| creators:419062 |  |  | True | True | True |
| creators:295188 |  |  | False | False | False |
| creators:423315 |  |  | True | True | True |
| creators:422146 | bidirectional_nli |  | False | False | True |
| creators:421853 |  |  | False | False | True |
| creators:418620 | future_tense | certainty | False | False | False |
| creators:114783 | negation\|numbers |  | False | False | True |
| creators:224770 |  |  | True | True | True |
| creators:8b0d99b23d03 |  |  | False | False | True |
| creators:97c9d6b9ac1b |  |  | False | False | True |
| creators:423545 |  |  | False | False | True |
| creators:298495 |  |  | False | False | True |
| creators:418904 |  |  | False | False | True |
| creators:2e34435c6ccf | certainty\|negation |  | False | False | True |
| creators:459e183c1d0d |  |  | False | False | True |
| creators:416436 |  |  | False | False | True |
| creators:116358 |  | similarity | False | False | True |
| creators:218236 |  |  | False | False | True |
| creators:418827 |  |  | False | False | False |

| v3 rejection reason | N (overlapping) |
| --- | --- |
| attribution | 2 |
| bidirectional_nli | 9 |
| certainty | 8 |
| framing_anchors | 1 |
| negation | 4 |
| numbers | 1 |
| quotations | 6 |
| similarity | 2 |

## מה נפתר ומה עדיין לא ידוע

הסיכום נשען על spans ודגלים בלבד. אין לייחס שיפור סמנטי סופי להסרת דגל, או drift חדש להוספת דגל. קטעי Original/v2/v3 בשלמותם מופיעים בטבלת ההשוואה ובחבילת הבדיקה; תוכן חדש, omission או שינויי scope שאינם ב־spans המוגדרים מראש יכולים להישאר גם אחרי שחזור ביטוי. יש לעיין בהם בבדיקה החיצונית הבאה, בלי לשנות את ה־prompt שוב לפי התוצאות כאן.

## תוצרים ושחזור

- [כל 30 ההשוואות](COMPARISON_V2_V3_30.md) ו־[CSV](comparison_v2_v3_30.csv).
- [כל תוצאות ה־guards](rewrite_validation.csv), [מדדי style](style_metrics_v2_v3.csv), [66 מאפיינים לשתי הגרסאות](explicit_style_changes_v2_v3.csv).
- [חבילת הבדיקה המלאה](REVIEW_PACKAGE_30.md); היא מכילה ציונים ולכן אינה עיוורת.
- [חבילה ללא ציונים/גרסה קודמת/שמות כותבים](REVIEW_PACKAGE_BLIND_30.md) לשלב החיצוני הנפרד.
- [ה־prompt](prompt_v3.txt), [תוספות לעומת v2](prompt_delta.diff), [פרוטוקול](protocol.json), [סיכום](summary.json), [תקינות קלטים](integrity_audit.json), [בקשות Original-only](request_integrity_audit.json).

לא נכתבו דירוגי External LLM Review, לא בוצע Human Validation, לא הוזנו שדות human-review, לא בוצעו threshold tuning, guard changes, retraining, LoRA או test evaluation. כל הגרסאות והביקורות הקודמות נשמרו. עוצרים לפני בדיקה חיצונית נוספת.

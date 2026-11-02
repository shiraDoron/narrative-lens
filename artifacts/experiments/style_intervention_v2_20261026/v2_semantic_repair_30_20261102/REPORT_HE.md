# v2 + Semantic Verification and Targeted Repair — 30 TRAIN examples

## למה עברנו לשני שלבים

v3 attempted to encode more semantic-preservation constraints in a single rewrite prompt, but external review showed overall degradation relative to v2. Therefore the next experiment separates style rewriting from semantic verification and minimal repair.

זהו **train-only intervention development**, לא final/test result, לא Human Validation ולא הוכחה להכללה משופרת. v2 הוא baseline הפיתוח המועדף לפי הסקירות שסופקו, בכפוף להבדלי מעריכים/הקשר. קלט שלב השכתוב הראשון הוא v2 הקיים: לא נוצר שכתוב ראשוני חדש.

## מה הורץ

אותו Qwen2.5-3B-Instruct Q4_K_M מקומי בשני תפקידים: verification על Original/v2, ואז repair מותנה על Original/v2/ממצאי האימות. נבדקו 17 קטגוריות ב־preserved/not_preserved/borderline. לא הועברו IDs, תוויות, ציונים או דירוגי External LLM Review. האימות המקומי הוא חלק ממערכת ההתערבות, **לא External LLM Review עצמאי**; אין להציג את preserved שלו כאישור משמעות.

ה־repair מחזיר patches ולא פסקה חדשה. רק החלפות של spans ייחודיים שאינם חופפים מיושמות, ללא החלפת כל הטקסט. אין בחירת מועמד לפי guards ואין retries לשיפור איכות. אם JSON/ראיות/patch אינו תקין, נשמר v2 והרשומה מסומנת ככשל תהליך, לא כהצלחת תיקון. זהו חוזה הפעלת patch, לא שינוי של automated filtering הקיים.

המודל/כימות נשמרו, אך זהו ניסוי ארכיטקטורת pipeline חדש: schema-constrained JSON, שני prompts, תקציבי פלט 1536/1024 ו־context של 16384 בארבעה slots. אין לייחס הבדל בתוצאה רק לנוסח prompt אחד. ה־guards, ספי MPNet≥0.85 / NLI≥0.6, קוד NER/lexical, מדדי style ו־66 מאפיינים וה־scaling נשארו ללא שינוי.

## תוצאות אוטומטיות בלבד

| Metric | v2 | v3 | v2 + Repair |
| --- | --- | --- | --- |
| automated_preservation_pass | 6 | 9 | 6 |
| substantial_style_change | 24 | 26 | 24 |
| both | 6 | 9 | 6 |
| exact_copies | 0 | 0 | 0 |

| Process measure | Value |
| --- | --- |
| repair_call_count | 19 |
| changed_count | 1 |
| fallback_count | 29 |
| process_completed_without_contract_error | 1 |
| changed_subset_automatic | {'n': 1, 'pass_count': 0, 'substantial_style_count': 1, 'both_count': 0} |
| applied_edit_count | 2 |
| effective_edit_count | 1 |
| noop_edit_count | 1 |
| verification_invalid_ids | ['creators:0105f26ef9f1', 'creators:120669', 'creators:295188', 'creators:114783', 'creators:97c9d6b9ac1b', 'creators:423545', 'creators:298495', 'creators:418904', 'creators:2e34435c6ccf', 'creators:416436', 'creators:418827'] |
| repair_invalid_ids | ['creators:421024', 'creators:422329', 'creators:120177', 'creators:212505', 'creators:421951', 'creators:422331', 'creators:216128', 'creators:421279', 'creators:419062', 'creators:423315', 'creators:422146', 'creators:421853', 'creators:418620', 'creators:224770', 'creators:8b0d99b23d03', 'creators:459e183c1d0d', 'creators:116358', 'creators:218236'] |
| verification_truncated | 0 |
| repair_truncated | 0 |
| issue_category_marked_preserved_count | 20 |
| mean_word_edit_fraction_from_v2 | 0.0036363636363636377 |

הטבלה הראשית כוללת את כל 30 הקלטים, גם fallback ל־v2. changed_subset_automatic הוא תיאור נפרד של הטקסטים שבהם הוחל שינוי, לא השוואה סיבתית או קבוצה שנבחרה לפי איכות. כאשר fallback גבוה, דמיון ל־baseline אינו ראיה שה־repair עובד: לעיתים לא הייתה התערבות בפועל. כשלי JSON/ראיות/patch מעידים על מגבלת מימוש/מודל בניסוי הזה, ואינם מפריכים כשלעצמם את הרעיון הדו־שלבי.

**מסקנת המימוש הנוכחי:** רק 1/30 טקסטים השתנו, ו־29/30 נשמרו ללא תיקון בגלל כשל בחוזה התהליך. לכן לא הודגם שיפור בשימור סמנטי, ואין בסיס לאמץ את המימוש הזה כ־semantic repair אמין. גם התיקון שהוחל דורש בדיקה חיצונית; אין להסיק מכאן שהארכיטקטורה הדו־שלבית כשלעצמה אינה יכולה לעבוד.



שינוי word_edit_fraction ביחס ל־v2 מתאר את היקף ההתערבות, לא מוכיח minimality אופטימלית. כל עריכה מיושמת נשמרת ב־[repairs_applied.csv](repairs_applied.csv). תיקון יכול להחזיר ביטויי מקור ולהפחית style; exact copies ביחס ל־Original מסוכמים בנפרד.

## סוגי התיקונים שהוחלו

| Verification issue category | Text-changing patch count |
| --- | --- |
| additions | 1 |

| ID | Detected category | Old span | New span | Caution |
| --- | --- | --- | --- | --- |
| creators:417181 | additions | Additionally, the SPLC allegedly established fake entities to obscure its donors' contributions. |  | Deletion: verify that no original claim was removed |

| Changed ID | Removed guard flags | Added guard flags |
| --- | --- | --- |
| creators:417181 | certainty | bidirectional_nli |

ב־417181 נעלם דגל certainty בעקבות מחיקת המשפט שמכיל allegedly, ונוסף bidirectional_nli. זהו מקרה שבו הסרת דגל אינה תיקון סמנטי: מילת marker נעלמה יחד עם הטענה כולה, והבדיקה הדו־כיוונית מסמנת סיכון לאי־שקילות. אין להציג זאת כשיפור certainty מאומת.



## דוגמאות רגישות — ללא fixes לפי ID

| ID | Verification issues | Applied repairs | Process errors | v2 pass | repair pass | repair style |
| --- | --- | --- | --- | --- | --- | --- |
| creators:417181 | [{"category": "negation", "original_span": "", "rewrite_span": "Indeed, the SPLC, the primary financier of white supremacist organizations in the U.S., appears to have been the target of allegations from the Department of Justice in its superseding indictment. The DOJ claims that the SPLC covertly funded and promoted racist groups through informants, while publicly denouncing them.", "explanation": "The original text uses 'likely' and 'alleges', which imply a degree of uncertainty. The rewrite removes these qualifiers, making the claim more definitive."}, {"category": "additions", "original_span": "", "rewrite_span": "Additionally, the SPLC allegedly established fake entities to obscure its donors' contributions.", "explanation": "The rewrite adds the phrase 'Additionally' at the beginning, which is not present in the original text."}] | [{"old": "Indeed, the SPLC, the primary financier of white supremacist organizations in the U.S., appears to have been the target of allegations from the Department of Justice in its superseding indictment. The DOJ claims that the SPLC covertly funded and promoted racist groups through informants, while publicly denouncing them.", "new": "Indeed, the SPLC, the primary financier of white supremacist organizations in the U.S., appears to have been the target of allegations from the Department of Justice in its superseding indictment. The DOJ claims that the SPLC covertly funded and promoted racist groups through informants, while publicly denouncing them.", "issue_index": 0}, {"old": "Additionally, the SPLC allegedly established fake entities to obscure its donors' contributions.", "new": "", "issue_index": 1}] |  | False | False | True |
| creators:421951 | [{"category": "additions", "original_span": "No one fights like mistreated men living on a diet of garbage, the lash and below-decks rape.", "rewrite_span": "No one fights like mistreated men, subsisting on meager rations of garbage, beaten by the lash, and subjected to rape below decks.", "explanation": "The addition of 'subsisting on meager rations of garbage' and the rephrasing of 'the lash and below-decks rape' to 'beaten by the lash, and subjected to rape below decks' are not exact matches."}, {"category": "omissions", "original_span": "the British conquered a big chunk of the world thanks to their navy, which was crewed by whip-scarred, toothless, unwilling sailors with untreated syphilis.", "rewrite_span": "", "explanation": "The sentence 'the British conquered a big chunk of the world thanks to their navy, which was crewed by whip-scarred, toothless, unwilling sailors with untreated syphilis' is omitted in the rewrite."}] | [] | old span not unique/nonempty\|old span not unique/nonempty | True | True | True |
| creators:120669 | [{"category": "omissions", "original_span": "\"Fox & Friends\" highlighted my most recent column, titled \"Neutering Religious Holidays\"", "rewrite_span": "\"Fox & Friends\" featured my latest column, \"Neutering Religious Holidays\"", "explanation": "Fox & Friends highlighted vs. Fox & Friends featured"}, {"category": "additions", "original_span": "So I decided to do a little research and see just how spiritual his past Thanksgiving addresses have been and compare them with the thoughts of our founding president, George Washington.", "rewrite_span": "So I decided to conduct some research and examine how spiritually his past Thanksgiving addresses have been, and compare them with the sentiments of our founding father, George Washington.", "explanation": "conduct some research vs. examine how spiritually"}] | [] |  | True | True | True |
| creators:423315 | [{"category": "factual_claims", "original_span": "No one had stormed the Capitol yet, there had been no George Floyd riots, we hadn't started the war we were going to lose in Afghanistan, and ICE hadn't killed anyone in the street.", "rewrite_span": "No one had yet stormed the Capitol, there were no George Floyd protests, we hadn't initiated the war we were destined to lose in Afghanistan, and ICE had not yet killed anyone on the streets.", "explanation": "The timeline of events and specific details differ. The original text mentions George Floyd riots, while the rewrite text refers to George Floyd protests. The original text uses 'stormed' and 'killed', while the rewrite uses 'stormed' and 'killed'."}, {"category": "additions", "original_span": "No one had stormed the Capitol yet, there had been no George Floyd riots, we hadn't started the war we were going to lose in Afghanistan, and ICE hadn't killed anyone in the street.", "rewrite_span": "", "explanation": "The rewrite text omits the timeline of events and specific details mentioned in the original text."}] | [] | old span not unique/nonempty\|old span not unique/nonempty | True | True | True |
| creators:8b0d99b23d03 | [{"category": "omissions", "original_span": "\"The rich are different from you and me.\" — F. Scott Fitzgerald", "rewrite_span": "\"The rich are distinct from the rest of us.\" — F. Scott Fitzgerald", "explanation": "Different vs. distinct"}, {"category": "omissions", "original_span": "I read two books in one weekend: \"Just Mercy\" by Bryan Stevenson on Saturday, \"Strangers\" by Belle Burden on Sunday.", "rewrite_span": "I recently read two books in a single weekend: \"Just Mercy\" by Bryan Stevenson on Saturday, and \"Strangers\" by Belle Burden on Sunday.", "explanation": "one weekend vs. single weekend"}] | [] | old span not unique/nonempty\|old span not unique/nonempty | False | False | True |
| creators:423545 | [{"category": "factual_claims", "original_span": "\"Greg Abbott, the right-wing hack who is governor of Texas, probably doesn't know what a \"petard\" is, but he's now been hoisted by a big one. \"", "rewrite_span": "\"Greg Abbott, the right-wing figure who serves as Texas's governor, may not be familiar with the term \"petard,\" but he's now caught in a significant predicament. \"", "explanation": "The text about Greg Abbott's role as governor and his knowledge of petard is changed to a more general description of his position and his unfamiliarity with the term."}, {"category": "additions", "original_span": "\"Hoist on a petard\" is a phrase from Shakespeare, indicating a creator being destroyed by the very thing they've devised.", "rewrite_span": "\"Hoist on a petard\" is a Shakespearean phrase for a bomb maker being blown sky-high by his own creation.", "explanation": "The specific context of the phrase 'hoist on a petard' is added in the rewrite, which is not present in the original."}, {"category": "omissions", "original_span": "\"Greg Abbott, the right-wing hack who is governor of Texas, probably doesn't know what a \"petard\" is, but he's now been hoisted by a big one. \"", "rewrite_span": "\"Greg Abbott, the right-wing figure who serves as Texas's governor, may not be familiar with the term \"petard,\" but he's now caught in a significant predicament. \"", "explanation": "The original text mentions that Abbott is a 'hack', which is omitted in the rewrite."}] | [] |  | False | False | True |
| creators:298495 | [{"category": "additions", "original_span": "I was long familiar with the bigotry in my home state.", "rewrite_span": "I was already well-acquainted with the bigotry in my home state.", "explanation": "The phrase 'long familiar' is replaced with 'already well-acquainted'."}, {"category": "additions", "original_span": "Most of the hate mail came from strangers, but I got my share of lectures from blood relatives, too.", "rewrite_span": "Most of the hate mail came from anonymous sources, but I also received lectures from family members.", "explanation": "The phrase 'strangers' is replaced with 'anonymous sources', and 'blood relatives' is replaced with 'family members'."}, {"category": "omissions", "original_span": "Back then, I was on staff at The Plain Dealer in Cleveland, and I was long familiar with the bigotry in my home state.", "rewrite_span": "", "explanation": "The first sentence is omitted in the rewrite."}, {"category": "omissions", "original_span": "I was employed at The Plain Dealer in Cleveland, and I was already well-acquainted with the bigotry in my home state.", "rewrite_span": "", "explanation": "The second sentence is omitted in the rewrite."}] | [] |  | False | False | True |
| creators:418904 | [{"category": "factual_claims", "original_span": "\"For us, it was the day Vicksburg fell.\"\nVicksburg, Mississippi, fell to Union troops on July 4, 1863.", "rewrite_span": "\"For us, it was the day Vicksburg fell.\"\nVicksburg, Mississippi, capitulated to Union forces on July 4, 1863.", "explanation": "The dates and actions are swapped, changing the meaning of the event."}, {"category": "additions", "original_span": "For us, it was the day Vicksburg fell.", "rewrite_span": "For us, it was the day Vicksburg fell.", "explanation": "The phrase 'For us, it was the day Vicksburg fell.' is repeated in the rewrite, which is not present in the original."}] | [] |  | False | False | True |
| creators:459e183c1d0d | [{"category": "additions", "original_span": "coauthored the proposition, estimates that the tax could raise about $100 billion and claims that 90% of the proceeds would go to health care.", "rewrite_span": "coauthored the proposition, estimates that the tax could generate approximately $100 billion and claims that 90% of the revenue would be allocated to healthcare.", "explanation": "The addition of 'approximately' in the rewrite is a minor change but does not preserve the exact wording."}] | [] | old span not unique/nonempty | False | False | False |
| creators:418827 | [{"category": "additions", "original_span": "\"White House Rose Garden\"", "rewrite_span": "\"Rose Garden\"", "explanation": "Removed 'White House' from the original text."}, {"category": "additions", "original_span": "\"stately East Wing\"", "rewrite_span": "\"stately East Wing\"", "explanation": "No change in this case, but the original text has 'stately' and the rewrite has 'stately'."}, {"category": "additions", "original_span": "\"guests gathered and mingled\"", "rewrite_span": "\"guests once mingled\"", "explanation": "Changed 'gathered and mingled' to 'once mingled'."}, {"category": "additions", "original_span": "\"marble wall of the national performing arts center\"", "rewrite_span": "\"marble wall of the national performing arts center\"", "explanation": "No change in this case, but the original text has 'marble' and the rewrite has 'marble'."}, {"category": "omissions", "original_span": "No, friends, Romans, countrymen, it wasn't enough to murder the White House Rose Garden.", "rewrite_span": "No, friends, Romans, countrymen, it wasn't enough to slash the White House Rose Garden.", "explanation": "Removed 'murdered' and changed 'stately East Wing' to 'slashed'."}, {"category": "omissions", "original_span": "No, friends, Romans, countrymen, it wasn't enough to tear down its stately East Wing, where guests gathered and mingled.", "rewrite_span": "No, friends, Romans, countrymen, it wasn't enough to topple its stately East Wing, where guests once mingled.", "explanation": "Changed 'tear down' to 'toppled' and 'gathering and mingling' to 'once mingled'."}, {"category": "omissions", "original_span": "No, friends, Romans, countrymen, it wasn't enough to brandish \"Donald J. Trump\" over \"John F. Kennedy\" on the marble wall of the national performing arts center.", "rewrite_span": "No, friends, Romans, countrymen, it wasn't enough to display \"Donald J. Trump\" above \"John F. Kennedy\" on the marble wall of the national performing arts center.", "explanation": "Changed 'brandish' to 'display'."}] | [] |  | False | False | False |

## האם נוצרו בעיות חדשות?

לא בוצעה בדיקה סמנטית חיצונית לאחר התיקון, ולכן אין כאן קביעה שאין drift חדש או ספירות No/Borderline חדשות. כל `old→new` ב־repairs_applied.csv הוא תצפית טקסטואלית לבדיקה; המודל המקומי יכול לפספס הפרות, להצביע על הפרה שגויה או להציע תיקון שמוסיף בעיה. דגלי guards שהתווספו אינם כשלעצמם הוכחה ל־drift, ומעבר אינו הוכחת תקינות. כשל תהליך נשאר מפורש, בלי להסתירו באמצעות הפקת מועמד נוסף. החבילה העיוורת מוכנה לשלב הבא בלבד.

בפרט, מחיקת משפט על הקמת ישויות/הסתרת מימון, כאשר גם במקור יש טענה על יצירת ישויות פיקטיביות, היא סיכון חדש להשמטת טענה — לא תיקון משמעות מאומת. התצפית היא השוואת טקסטים, ללא תיוג Human/External חדש. יש לשמר גם את הפלט הכושל כדי שהבודק החיצוני יוכל להעריכו.

## קישורים

- [השוואה מלאה לכל ID](COMPARISON_30.md), [CSV](comparison_v2_v3_repair.csv).
- [אימות מקומי](verification_results.csv), [פלטים מתוקנים](repaired_outputs.csv), [guards ללא שינוי](rewrite_validation.csv).
- [style metrics](style_metrics_v2_v3_repair.csv), [66 מאפיינים](explicit_style_changes_v2_v3_repair.csv).
- [חבילת ID/Original/Repaired בלבד](REVIEW_PACKAGE_BLIND_30.md).
- [Prompt תיקון](SEMANTIC_REPAIR_PROMPT.txt), [Prompt אימות](SEMANTIC_VERIFICATION_PROMPT.txt), [פרוטוקול](protocol.json), [סיכום](summary.json), [תקינות](integrity_audit.json), [שחזור](REPRODUCTION.md).

לא שונו split, labels, human-review fields או קוד אימון. לא הורצו retraining, test evaluation, LoRA, External LLM Review חדש או Human Validation. עוצרים לפני הבדיקה החיצונית העיוורת של Repaired v2.

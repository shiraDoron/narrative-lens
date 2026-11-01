# חבילת בדיקה חיצונית — 30 טקסטים מכותבי האימון בלבד

## מה יש כאן

30 דוגמאות קיימות: 10 עם שינוי משמעותי לפי proxy אוטומטי, 10 עם שינוי מזערי שעברו את כל המסננים, ו־10 שנפסלו לפחות באחת מזרועות השכתוב/Formatting. כל רשומה מופיעה פעם אחת. קבוצות הבחירה נפרדות, אך דוגמה בקבוצת השינוי המשמעותי יכולה גם להיות פסולה אוטומטית.

הבחירה נעשתה לפי ציונים ודגלים קיימים בלבד, בסבב בין כותבים ובסדר hash קבוע. לא בוצעה הכרעה אם הנרטיב נכון, אם המשמעות נשמרה או אם השינוי הסגנוני אמיתי. זה מדגם אבחוני מכוון, לא מדגם מייצג להערכת שיעורי הצלחה. ה־test וה־validation לא נכללו ולא שונו.

## הוראות למי שמקבל את החבילה

הצעת הנרטיב והמדדים הם פלט מכונה, לא אמת מאומתת. confidence הוא ציון AI בסולם 1–3, לא הסתברות מכוילת. passed=True פירושו מעבר בסינון אוטומטי בלבד. שדות guard הם בדיקות אוטומטיות; human_verified=False הוא שדה מקור קיים, לא הכרעה חדשה.

לכל רשומה יש שישה שדות ריקים בסופה. החבילה הוכנה ללא מילוי שלהם וללא שימוש ב־LLM נוסף לשיפוט. אפשר להחזיר טבלת תוצאות עם ID וששת השדות. שמרו על ניסוח המקור והשכתובים ללא עריכה.

**הבחנה מחקרית:** בדיקה על ידי ChatGPT היא בדיקת LLM חיצונית, גם אם נקראת בשיחה “Human Review”. היא אינה אימות אנושי או agreement בין בני אדם. יש לתעד מי/איזה מודל ביצע את הבדיקה, ולא להציג תשובת ChatGPT כתיוג אנושי. אימות אנושי מחקרי דורש סוקר/ת אדם.

## פירוש מדדי הסגנון

word_edit_fraction הוא אי־דמיון סימטרי של רצף מילים (1 פחות SequenceMatcher), ולא שיעור מילים שהוחלפו מילולית. אחוזי החלפה/מחיקה/הוספה נשמרים בנפרד. sentence_mean_relative_change הוא proxy לפי אורך משפט, לא ניתוח תחבירי. punctuation_l1_per100 הוא שינוי בתדירות סימני פיסוק ל־100 מילים. formality_proxy_delta מבוסס על כיווצים ומילות דיבור ואינו מדד פורמליות מתוקף. substantial_style_change הוא דגל תפעולי קיים, לא אימות סגנון.

כלל substantial: word_edit_fraction ≥0.15 וגם לפחות אחד: שינוי יחסי בממוצע אורך משפט ≥0.15, מרחק פיסוק ≥1 ל־100 מילים, או שינוי מוחלט בכיווצים ≥1 ל־100 מילים. minimal: עריכת מילים <0.05 ללא עמידה בכלל substantial. הספים לא שונו.


## אינדקס

| # | ID | Author | קבוצת בחירה | הצעת נרטיב |
|---|---|---|---|---|
| 1 | creators:0105f26ef9f1 | Marc Dion | substantial_style_proxy | Left-wing |
| 2 | creators:421024 | Froma Harrop | substantial_style_proxy | Right-wing |
| 3 | creators:422329 | Veronique de Rugy | substantial_style_proxy | Right-wing |
| 4 | creators:417181 | David Harsanyi | substantial_style_proxy | Right-wing |
| 5 | creators:120177 | Chuck Norris | substantial_style_proxy | Right-wing |
| 6 | creators:212505 | Lawrence Kudlow | substantial_style_proxy | Right-wing |
| 7 | creators:421951 | Marc Dion | substantial_style_proxy | Left-wing |
| 8 | creators:422331 | Froma Harrop | substantial_style_proxy | Right-wing |
| 9 | creators:120669 | Chuck Norris | substantial_style_proxy | Right-wing |
| 10 | creators:216128 | Lawrence Kudlow | substantial_style_proxy | Right-wing |
| 11 | creators:421279 | Jamie Stiehm | minimal_style_proxy | Left-wing |
| 12 | creators:419062 | Jim Hightower | minimal_style_proxy | Left-wing |
| 13 | creators:295188 | Connie Schultz | minimal_style_proxy | Left-wing |
| 14 | creators:423315 | Marc Dion | minimal_style_proxy | Left-wing |
| 15 | creators:422146 | Froma Harrop | minimal_style_proxy | Left-wing |
| 16 | creators:421853 | Veronique de Rugy | minimal_style_proxy | Right-wing |
| 17 | creators:418620 | David Harsanyi | minimal_style_proxy | Right-wing |
| 18 | creators:114783 | Chuck Norris | minimal_style_proxy | Right-wing |
| 19 | creators:224770 | Lawrence Kudlow | minimal_style_proxy | Right-wing |
| 20 | creators:8b0d99b23d03 | Jamie Stiehm | minimal_style_proxy | Left-wing |
| 21 | creators:97c9d6b9ac1b | Jamie Stiehm | automatic_screen_rejected | Left-wing |
| 22 | creators:423545 | Jim Hightower | automatic_screen_rejected | Left-wing |
| 23 | creators:298495 | Connie Schultz | automatic_screen_rejected | Left-wing |
| 24 | creators:418904 | Marc Dion | automatic_screen_rejected | Left-wing |
| 25 | creators:2e34435c6ccf | Froma Harrop | automatic_screen_rejected | Left-wing |
| 26 | creators:459e183c1d0d | Veronique de Rugy | automatic_screen_rejected | Right-wing |
| 27 | creators:416436 | David Harsanyi | automatic_screen_rejected | Right-wing |
| 28 | creators:116358 | Chuck Norris | automatic_screen_rejected | Right-wing |
| 29 | creators:218236 | Lawrence Kudlow | automatic_screen_rejected | Right-wing |
| 30 | creators:418827 | Jamie Stiehm | automatic_screen_rejected | Left-wing |

## דוגמה 01 — creators:0105f26ef9f1
**Author:** Marc Dion | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/marc-dion/10/26/big-menu | **תאריך:** 2026-10-09
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** three things that disgust me

### Original
Good examples of that are Donald Trump, escargot and gang rape, three things that disgust me, but are keenly desired by some people. Just knowing that will make you look around for a long time before you sit next to a stranger on the bus. The fact that I can type the word "bus" without automatically putting the word "school" in front of it indicates that I might have at least some history with people whose wants and needs are not only disgusting, but poorly concealed.

### Paraphrase
Sure, here's the paraphrased version of your input:  
Good examples are Donald Trump, escargot, and gang rape, three things that disgust me but are desired by some. Knowing this will make you hesitate before sitting next to a stranger on the bus. The fact that I can type "bus" without thinking of "school" suggests I might have some acquaintance with people whose wants and needs are not only disgusting but poorly concealed.

### Normalized
Good examples are Donald Trump, escargot, and gang rape, three things that disgust me but are desired by some people. Knowing this will make you look around for a long time before sitting next to a stranger on the bus. The fact that I can type "bus" without automatically thinking of "school" suggests I might have some history with people whose wants and needs are not only disgusting but poorly concealed.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.9761423468589783 | 0.42153918743133545 | 0.8176378607749939 |
| rejection_reasons |  | similarity\|bidirectional_nli |  |
| semantic_similarity | 1.0 | 0.7242907881736755 | 0.9562333822250366 |
| entailment_forward | 0.9761423468589783 | 0.7313209176063538 | 0.9865928292274475 |
| entailment_reverse | 0.9761423468589783 | 0.42153918743133545 | 0.8176378607749939 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | True | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["donald trump"] | ["donald trump"] | ["donald trump"] |
| rewrite_entities | ["donald trump"] | ["donald trump"] | ["donald trump"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | False | True |
| guard_bidirectional_nli | True | False | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: similarity|bidirectional_nli

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.28301886792452835 | 0.15923566878980888 |
| original_words_replaced_pct | 23.25581395348837 | 13.953488372093023 |
| original_words_deleted_pct | 10.465116279069768 | 9.30232558139535 |
| inserted_words_per100_original | 10.465116279069768 | 0.0 |
| word_length_change_pct | -15.116279069767442 | -17.441860465116278 |
| mean_sentence_words_original | 28.666666666666668 | 28.666666666666668 |
| mean_sentence_words_rewrite | 24.333333333333332 | 23.666666666666668 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.1511627906976745 | 0.1744186046511628 |
| punctuation_l1_per100 | 2.198152277795476 | 0.42581067802161865 |
| formality_proxy_delta | -1.36986301369863 | 0.0 |
| contraction_rate_delta | 1.36986301369863 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.38609596046848155 | 0.28233963364005127 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 02 — creators:421024
**Author:** Froma Harrop | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/froma-harrop/08/26/naked-dressing-from-studio-54-to-the-bridal-procession | **תאריך:** 2026-08-06
**הצעת נרטיב:** Right-wing | **confidence:** 2/3
**Evidence שמור מהמערכת:** lamentable even at nightclubs

### Original
Brides should know that they already have a man. They don't have to use their wedding to attract a date for Saturday night. They've supposedly secured one for the foreseeable future. Thus, it's hard to figure how the fashion trend of "naked dressing," lamentable even at nightclubs, has invaded the precincts of ancient social custom. Displaying one's privates — or underwear — in public started as a fashion trend pushed by attention-hungry celebrities. Now it's walking down the aisle.

### Paraphrase
Brides should be aware they already have a man; they don't need their wedding to find a date for Saturday night. They've supposedly secured one for the future. So, it's puzzling how the "naked dressing" trend, deplorable even at clubs, has infiltrated wedding customs. This started as a fashion move by celebrities seeking attention, now it's happening on the aisle.

### Normalized
Brides should know they already have a man; they don't need their wedding to find one for Saturday night. They've supposedly secured one for the foreseeable future, making it hard to understand how the fashion trend of "naked dressing," lamentable even at nightclubs, has invaded ancient social customs. Displaying one's privates — or underwear — in public began as a trend pushed by attention-hungry celebrities, now extending to weddings.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.981316089630127 | 0.9167015552520752 | 0.9407398700714111 |
| rejection_reasons |  | quotations |  |
| semantic_similarity | 1.0 | 0.9167015552520752 | 0.9407398700714111 |
| entailment_forward | 0.981316089630127 | 0.9894583225250244 | 0.9859695434570312 |
| entailment_reverse | 0.981316089630127 | 0.9420108199119568 | 0.9421596527099609 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | [] | [] | [] |
| rewrite_entities | [] | [] | [] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | False | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: quotations

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.37414965986394555 | 0.20779220779220775 |
| original_words_replaced_pct | 37.34939759036145 | 19.27710843373494 |
| original_words_deleted_pct | 7.228915662650603 | 7.228915662650603 |
| inserted_words_per100_original | 2.4096385542168677 | 0.0 |
| word_length_change_pct | -22.89156626506024 | -14.457831325301205 |
| mean_sentence_words_original | 13.833333333333334 | 13.833333333333334 |
| mean_sentence_words_rewrite | 16.0 | 23.666666666666668 |
| sentence_count_original | 6 | 6 |
| sentence_count_rewrite | 4 | 3 |
| sentence_mean_relative_change | 0.15662650602409633 | 0.7108433734939759 |
| punctuation_l1_per100 | 7.812499999999999 | 4.0386899711522135 |
| formality_proxy_delta | -0.22590361445783103 | 1.798744272866113 |
| contraction_rate_delta | 0.22590361445783103 | -1.798744272866113 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.38288061026545156 | 0.24797727329217792 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 03 — creators:422329
**Author:** Veronique de Rugy | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/veronique-de-rugy/08/26/truths-and-omissions-as-us-hits-40-trillion-in-debt | **תאריך:** 2026-08-27
**הצעת נרטיב:** Right-wing | **confidence:** 2/3
**Evidence שמור מהמערכת:** they'll keep driving us into the same wall together

### Original
The U.S. national debt just crossed the $40 trillion threshold, doubling in less than a decade. Washington politicians have responded with their favorite fiscal game: blaming the other party. Democrats say Republican tax cuts are the culprit. Republicans say Democratic spending is the root cause. But both parties are responsible, with both hiding behind a lie of omission. And if we let them, they'll keep driving us into the same wall together.

### Paraphrase
The U.S. national debt now exceeds $40 trillion, doubling in less than a decade. Politicians on both sides have reacted with typical fiscal games: finger-pointing. Democrats blame Republican tax cuts, while Republicans blame Democratic spending. But both parties are culpable, each hiding behind a lie of omission. And if we let them, they'll keep us crashing into the same fiscal wall together.

### Normalized
The U.S. national debt has just surpassed the $40 trillion mark, doubling in less than a decade. Washington politicians have reacted with their usual fiscal games: shifting blame to the other party. Democrats attribute the increase to Republican tax cuts. Republicans blame Democratic spending. Yet, both parties are culpable, each hiding behind a lie of omission. If left unchecked, they will continue to drive us into the same financial crisis together.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.9531381726264954 | 0.5 | 0.9177806973457336 |
| rejection_reasons |  | entities |  |
| semantic_similarity | 1.0 | 0.966119647026062 | 0.9564323425292969 |
| entailment_forward | 0.9531381726264954 | 0.9858129620552063 | 0.9641433358192444 |
| entailment_reverse | 0.9531381726264954 | 0.8357934355735779 | 0.9177806973457336 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 0.5 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["u s", "washington"] | ["u s", "washington"] | ["u s", "washington"] |
| rewrite_entities | ["u s", "washington"] | ["u s"] | ["u s", "washington"] |
| guard_entities | True | False | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: entities

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.3093525179856115 | 0.3561643835616438 |
| original_words_replaced_pct | 25.675675675675677 | 31.08108108108108 |
| original_words_deleted_pct | 9.45945945945946 | 5.405405405405405 |
| inserted_words_per100_original | 6.756756756756757 | 1.3513513513513513 |
| word_length_change_pct | -12.162162162162161 | -2.7027027027027026 |
| mean_sentence_words_original | 9.25 | 9.25 |
| mean_sentence_words_rewrite | 9.285714285714286 | 9.0 |
| sentence_count_original | 8 | 8 |
| sentence_count_rewrite | 7 | 8 |
| sentence_mean_relative_change | 0.0038610038610039435 | 0.02702702702702703 |
| punctuation_l1_per100 | 3.8253638253638256 | 1.5390390390390385 |
| formality_proxy_delta | -0.18711018711018723 | 1.3513513513513513 |
| contraction_rate_delta | 0.18711018711018723 | -1.3513513513513513 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.2744396583332783 | 0.21604190014829808 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 04 — creators:417181
**Author:** David Harsanyi | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/david-harsanyi/06/26/the-splcs-real-scam | **תאריך:** 2026-06-05
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** the most generous funder of white supremacist groups

### Original
It turns out that the most generous funder of white supremacist groups in the United States was likely the Southern Poverty Law Center. At least that's what the Department of Justice's superseding indictment against the SPLC alleges. The organization secretly paid informants to engage in the active promotion and funding of racist groups while denouncing and "fighting" the very same groups in public. The SPLC purportedly created fictitious entities to hide funding from their donors.

### Paraphrase
It seems the Southern Poverty Law Center, a supposed champion of civil rights, might have secretly funded white supremacist groups. According to a superseding indictment by the Department of Justice, the SPLC allegedly paid informants to promote and fund racist groups while publicly denouncing them. The organization also created fake entities to conceal its funding from donors.

### Normalized
It turns out that the Southern Poverty Law Center, the most generous funder of white supremacist groups in the United States, was allegedly secretly paying informants to promote and fund these groups while publicly denouncing them. The SPLC allegedly created fictitious entities to hide its funding from donors. This is what the Department of Justice's superseding indictment alleges.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | False |
| validation_score | 0.9831134080886841 | 0.75 | 0.26110243797302246 |
| rejection_reasons |  | entities\|certainty\|quotations | certainty\|quotations\|bidirectional_nli |
| semantic_similarity | 1.0000001192092896 | 0.8985673189163208 | 0.8829523324966431 |
| entailment_forward | 0.9831134080886841 | 0.9834933280944824 | 0.9606943130493164 |
| entailment_reverse | 0.9831134080886841 | 0.7683054208755493 | 0.26110243797302246 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | True |
| entity_recall | 1.0 | 0.75 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["department of justice", "southern poverty law center", "splc", "united states"] | ["department of justice", "southern poverty law center", "splc", "united states"] | ["department of justice", "southern poverty law center", "splc", "united states"] |
| rewrite_entities | ["department of justice", "southern poverty law center", "splc", "united states"] | ["department of justice", "southern poverty law center", "splc"] | ["department of justice", "southern poverty law center", "splc", "united states"] |
| guard_entities | True | False | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | False | False |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | False | False |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | False |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: entities|certainty|quotations

**Normalized:** נפסל אוטומטית: certainty|quotations|bidirectional_nli

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.5970149253731343 | 0.6029411764705883 |
| original_words_replaced_pct | 58.44155844155844 | 11.688311688311689 |
| original_words_deleted_pct | 6.4935064935064934 | 53.246753246753244 |
| inserted_words_per100_original | 1.2987012987012987 | 6.4935064935064934 |
| word_length_change_pct | -25.974025974025974 | -23.376623376623378 |
| mean_sentence_words_original | 19.25 | 19.25 |
| mean_sentence_words_rewrite | 19.0 | 19.666666666666668 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.012987012987012988 | 0.021645021645021707 |
| punctuation_l1_per100 | 5.2631578947368425 | 3.389830508474576 |
| formality_proxy_delta | 2.5974025974025974 | 0.9024873431653093 |
| contraction_rate_delta | -2.5974025974025974 | -0.9024873431653093 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.5617306907676356 | 0.39431709596772146 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 05 — creators:120177
**Author:** Chuck Norris | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/chuck-norris/11/14/neutering-religious-holidays | **תאריך:** 2014-11-18
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** the war on Christmas is underway

### Original
Folks, our country is heading down a slippery slope. We have to stop it before it is too late. We haven't even hit Thanksgiving, and already the war on Christmas is underway. This time, one of the largest public school systems in the U.S. is eliminating every mention of religious holidays on its official calendar.

### Paraphrase
Folks, our country is on a slippery slope. We need to stop it before it's too late. We haven't even hit Thanksgiving, and already the war on Christmas is in full swing. One of the largest public school systems in the U.S. is now eliminating every reference to religious holidays from its official calendar.

### Normalized
Folks, our country is on a slippery slope. We must stop it before it's too late. Not even Thanksgiving has passed when the war on Christmas is already underway. In fact, one of the largest public school systems in the U.S. is now eliminating all references to religious holidays from its official calendar.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | False |
| validation_score | 0.9565006494522095 | 0.8987276554107666 | 0.7108489871025085 |
| rejection_reasons |  |  | certainty |
| semantic_similarity | 1.0 | 0.9843456149101257 | 0.966966986656189 |
| entailment_forward | 0.9565006494522095 | 0.9195945858955383 | 0.9564151167869568 |
| entailment_reverse | 0.9565006494522095 | 0.8987276554107666 | 0.7108489871025085 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["u s"] | ["u s"] | ["u s"] |
| rewrite_entities | ["u s"] | ["u s"] | ["u s"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | False |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** נפסל אוטומטית: certainty

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.17543859649122806 | 0.2857142857142857 |
| original_words_replaced_pct | 17.54385964912281 | 28.07017543859649 |
| original_words_deleted_pct | 0.0 | 1.7543859649122806 |
| inserted_words_per100_original | 1.7543859649122806 | 3.508771929824561 |
| word_length_change_pct | 0.0 | -3.508771929824561 |
| mean_sentence_words_original | 9.5 | 9.5 |
| mean_sentence_words_rewrite | 9.5 | 9.166666666666666 |
| sentence_count_original | 6 | 6 |
| sentence_count_rewrite | 6 | 6 |
| sentence_mean_relative_change | 0.0 | 0.035087719298245675 |
| punctuation_l1_per100 | 1.7543859649122813 | 1.6267942583732062 |
| formality_proxy_delta | -1.7543859649122806 | -0.06379585326953752 |
| contraction_rate_delta | 1.7543859649122806 | 0.06379585326953752 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.1835252978494413 | 0.2774176218072696 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 06 — creators:212505
**Author:** Lawrence Kudlow | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/lawrence-kudlow/09/17/trump-turnaround-puts-new-tax-cut-writing-on-the-wall | **תאריך:** 2017-09-16
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** shrewd moves by President Trump

### Original
Financial markets and most media pundits are missing the new writing on the wall. For a variety of reasons surrounding shrewd moves by President Trump, the chances for significant tax cuts in the next 10 weeks have risen sharply.

### Paraphrase
Financial markets and most media pundits are overlooking the new trends. With shrewd moves by President Trump, the likelihood of significant tax cuts in the next 10 weeks has sharply increased.

### Normalized
Financial markets and most media pundits are overlooking the new developments. Various reasons, including shrewd moves by President Trump, have increased the likelihood of significant tax cuts in the next 10 weeks.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.9853206276893616 | 0.04459798336029053 | 0.6125305891036987 |
| rejection_reasons |  | bidirectional_nli |  |
| semantic_similarity | 0.9999999403953552 | 0.9449348449707031 | 0.869260847568512 |
| entailment_forward | 0.9853206276893616 | 0.994491457939148 | 0.9942989349365234 |
| entailment_reverse | 0.9853206276893616 | 0.04459798336029053 | 0.6125305891036987 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | True | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["trump"] | ["trump"] | ["trump"] |
| rewrite_entities | ["trump"] | ["trump"] | ["trump"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | False | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: bidirectional_nli

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.3142857142857143 | 0.323943661971831 |
| original_words_replaced_pct | 38.46153846153846 | 30.76923076923077 |
| original_words_deleted_pct | 0.0 | 7.6923076923076925 |
| inserted_words_per100_original | 2.5641025641025643 | 5.128205128205129 |
| word_length_change_pct | -20.512820512820515 | -17.94871794871795 |
| mean_sentence_words_original | 19.5 | 19.5 |
| mean_sentence_words_rewrite | 15.5 | 16.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.20512820512820512 | 0.1794871794871795 |
| punctuation_l1_per100 | 0.6617038875103387 | 3.6858974358974357 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.36940265282218954 | 0.2436597693477069 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 07 — creators:421951
**Author:** Marc Dion | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/marc-dion/08/26/the-song-of-the-whip | **תאריך:** 2026-08-21
**הצעת נרטיב:** Left-wing | **confidence:** 2/3
**Evidence שמור מהמערכת:** No one fights like mistreated men

### Original
Way back there in the 1700s and the 1800s, the British conquered a big chunk of the world thanks to their navy, which was crewed by whip-scarred, toothless, unwilling sailors with untreated syphilis. That's who you want to fight your wars. No one fights like mistreated men living on a diet of garbage, the lash and below-decks rape.

### Paraphrase
Way back there in the 1700s and the 1800s, the British conquered a big chunk of the world thanks to their navy, which was crewed by whip-scarred, toothless, unwilling sailors with untreated syphilis. That's who you want to fight your wars. No one fights like mistreated men living on a diet of garbage, the lash, and below-decks rape.

### Normalized
Way back in the 1700s and 1800s, the British conquered a vast portion of the world with their formidable navy, manned by whipped, toothless, unwilling sailors suffering from untreated syphilis. These were the men you wanted to fight your wars. No one fights like mistreated men on a diet of garbage, beaten with the lash, and subjected to below-decks rape.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9885315895080566 | 0.9891024827957153 | 0.937676191329956 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 0.9997397661209106 | 0.937676191329956 |
| entailment_forward | 0.9885315895080566 | 0.9893746376037598 | 0.9909706115722656 |
| entailment_reverse | 0.9885315895080566 | 0.9891024827957153 | 0.9915221929550171 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | [] | [] | [] |
| rewrite_entities | [] | [] | [] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | False | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.0 | 0.2786885245901639 |
| original_words_replaced_pct | 0.0 | 22.950819672131146 |
| original_words_deleted_pct | 0.0 | 4.918032786885246 |
| inserted_words_per100_original | 0.0 | 8.19672131147541 |
| word_length_change_pct | 0.0 | 0.0 |
| mean_sentence_words_original | 20.333333333333332 | 20.333333333333332 |
| mean_sentence_words_rewrite | 20.333333333333332 | 20.333333333333332 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.0 | 0.0 |
| punctuation_l1_per100 | 1.639344262295083 | 3.278688524590165 |
| formality_proxy_delta | 0.0 | 1.639344262295082 |
| contraction_rate_delta | 0.0 | -1.639344262295082 |
| exact_copy | False | False |
| substantial_style_change | False | True |
| style_change_group | minimal | substantial |
| explicit_style_mean_abs_standardized_change | 0.009549197708892109 | 0.2700524773133456 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 08 — creators:422331
**Author:** Froma Harrop | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/froma-harrop/08/26/few-democratic-socialists-are-blue-collar-most-everyone-knows-it | **תאריך:** 2026-08-27
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** candidates who play-act as tradespeople

### Original
Classic Labor Day imagery shows men wearing hard hats and tough women in uniforms. These are Americans who did not build their muscles at a wellness club. By contrast, actual photos of the Democratic Socialists of America show seas of white faces belonging to college graduates. The only work most of them have done with their hands is typing. But the DSA is run by leaders who pretend otherwise, pushing forward candidates who play-act as tradespeople.

### Paraphrase
Classic Labor Day imagery shows men in hard hats and tough women in uniforms. These are Americans who did not build their muscles at a wellness club. In contrast, actual photos of the Democratic Socialists of America show seas of white faces belonging to college graduates. The only work most of them have done with their hands is typing. But the DSA is run by leaders who pretend otherwise, pushing forward candidates who play-act as tradespeople.

### Normalized
Classic Labor Day imagery depicts men in hard hats alongside tough women in uniforms. These are Americans who did not sculpt their muscles at a wellness club. In contrast, actual photos of the Democratic Socialists of America reveal a sea of white faces belonging to college graduates. Most of them have only typed with their hands. However, the DSA is led by figures who pretend otherwise, pushing forward candidates who pretend to be tradespeople.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9682194590568542 | 0.9795300364494324 | 0.9664673805236816 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0000001192092896 | 0.9991017580032349 | 0.9664673805236816 |
| entailment_forward | 0.9682194590568542 | 0.9795300364494324 | 0.984155535697937 |
| entailment_reverse | 0.9682194590568542 | 0.9798572659492493 | 0.9778061509132385 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["dsa"] | ["dsa"] | ["dsa"] |
| rewrite_entities | ["dsa"] | ["dsa"] | ["dsa"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.025974025974025983 | 0.23178807947019864 |
| original_words_replaced_pct | 2.5974025974025974 | 20.77922077922078 |
| original_words_deleted_pct | 0.0 | 3.896103896103896 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 0.0 | -3.896103896103896 |
| mean_sentence_words_original | 15.4 | 15.4 |
| mean_sentence_words_rewrite | 15.4 | 14.8 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.0 | 0.03896103896103894 |
| punctuation_l1_per100 | 0.0 | 2.7553527553527557 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | True |
| style_change_group | minimal | substantial |
| explicit_style_mean_abs_standardized_change | 0.05038796466566049 | 0.31623635396533656 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 09 — creators:120669
**Author:** Chuck Norris | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/chuck-norris/11/14/president-obama-versus-george-washington-on-thanksgiving | **תאריך:** 2014-11-25
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** liberals came out of the woodwork

### Original
Last week, when "Fox & Friends" highlighted my most recent column, titled "Neutering Religious Holidays," liberals came out of the woodwork to try to defend President Barack Obama's record. So I decided to do a little research and see just how spiritual his past Thanksgiving addresses have been and compare them with the thoughts of our founding president, George Washington.

### Paraphrase
Last week, when "Fox & Friends" discussed my latest column, "Neutering Religious Holidays," liberals sprang into action to defend President Barack Obama's record. So I decided to investigate and see how spiritually his Thanksgiving addresses have been in the past and compare them with those of our founding president, George Washington.

### Normalized
Last week, when "Fox & Friends" highlighted my most recent column titled "Neutering Religious Holidays," liberals sprang into action to defend President Barack Obama's record. So I decided to conduct some research and examine how spiritually President Washington's Thanksgiving addresses were, and compare them to the thoughts of our founding father, George Washington.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | False |
| validation_score | 0.9732277393341064 | 0.8842733502388 | 0.0135065708309412 |
| rejection_reasons |  |  | bidirectional_nli |
| semantic_similarity | 1.0 | 0.9766348004341125 | 0.9576212167739868 |
| entailment_forward | 0.9732277393341064 | 0.9908545017242432 | 0.0135065708309412 |
| entailment_reverse | 0.9732277393341064 | 0.8842733502388 | 0.0930963084101677 |
| added_claim_risk | False | False | True |
| removed_claim_risk | False | False | True |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["barack obama", "fox friends", "george washington"] | ["barack obama", "fox friends", "george washington"] | ["barack obama", "fox friends", "george washington"] |
| rewrite_entities | ["barack obama", "fox friends", "george washington"] | ["barack obama", "fox friends", "george washington"] | ["barack obama", "fox friends", "george washington"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | False |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** נפסל אוטומטית: bidirectional_nli

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.2792792792792793 | 0.2807017543859649 |
| original_words_replaced_pct | 28.333333333333332 | 31.666666666666668 |
| original_words_deleted_pct | 5.0 | 0.0 |
| inserted_words_per100_original | 5.0 | 0.0 |
| word_length_change_pct | -15.0 | -10.0 |
| mean_sentence_words_original | 30.0 | 30.0 |
| mean_sentence_words_rewrite | 25.5 | 27.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.15 | 0.1 |
| punctuation_l1_per100 | 1.1764705882352935 | 0.7407407407407405 |
| formality_proxy_delta | -0.2941176470588234 | -2.037037037037037 |
| contraction_rate_delta | 0.2941176470588234 | 2.037037037037037 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.22967645386513852 | 0.31410500593305574 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 10 — creators:216128
**Author:** Lawrence Kudlow | **Split:** train | **קבוצה:** substantial_style_proxy
**מקור:** https://www.creators.com/read/lawrence-kudlow/11/17/a-pro-growth-tax-bill-is-on-the-way | **תאריך:** 2017-11-11
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** Both plans are pro-growth

### Original
As the House and Senate work their way through the tax cut and reform effort, let me make one thing clear: Both plans are pro-growth, with the economic power coming from the business side. And where it comes from the personal side, there will be very little growth. That was always been the bet.

### Paraphrase
As the House and Senate work through the tax cut and reform effort, let me make one thing clear: Both plans are pro-growth, with the economic power coming from the business side. But where it comes from the personal side, there will be very little growth. That was always the bet.

### Normalized
As the House and Senate work through the tax cut and reform effort, let me clarify one thing: both plans are pro-growth, with economic power stemming from the business side. Where growth comes from the personal side, it will be minimal. That has always been the bet.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9766932129859924 | 0.9728032350540161 | 0.9724737405776978 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0000001192092896 | 0.9942405223846436 | 0.9724737405776978 |
| entailment_forward | 0.9766932129859924 | 0.977977991104126 | 0.9933133721351624 |
| entailment_reverse | 0.9766932129859924 | 0.9728032350540161 | 0.9947302341461182 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["house", "senate"] | ["house", "senate"] | ["house", "senate"] |
| rewrite_entities | ["house", "senate"] | ["house", "senate"] | ["house", "senate"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.04672897196261683 | 0.18446601941747576 |
| original_words_replaced_pct | 1.8181818181818181 | 14.545454545454545 |
| original_words_deleted_pct | 5.454545454545454 | 9.090909090909092 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -5.454545454545454 | -12.727272727272727 |
| mean_sentence_words_original | 18.333333333333332 | 18.333333333333332 |
| mean_sentence_words_rewrite | 17.333333333333332 | 16.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.05454545454545455 | 0.1272727272727272 |
| punctuation_l1_per100 | 0.524475524475525 | 1.3257575757575766 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | True |
| style_change_group | minimal | substantial |
| explicit_style_mean_abs_standardized_change | 0.1514551344573879 | 0.19648855019753816 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 11 — creators:421279
**Author:** Jamie Stiehm | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/jamie-stiehm/08/26/an-immodest-proposal-for-trump | **תאריך:** 2026-08-12
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** to destroy faith in democracy

### Original
You may wonder why President Donald Trump is doing everything he can, day by day, to destroy faith in democracy in little and large ways, on the job day and night. I have an answer that will presently be revealed.

### Paraphrase
You may wonder why President Donald Trump is doing everything he can, day by day, to destroy faith in democracy in little and large ways, on the job day and night. I have an answer that will presently be revealed.

### Normalized
You may wonder why President Donald Trump is doing everything he can, day by day, to destroy faith in democracy in little and large ways, on the job day and night. I have an answer that will presently be revealed.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9772352576255798 | 0.9772352576255798 | 0.9772352576255798 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 1.0 | 1.0 |
| entailment_forward | 0.9772352576255798 | 0.9772352576255798 | 0.9772352576255798 |
| entailment_reverse | 0.9772352576255798 | 0.9772352576255798 | 0.9772352576255798 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["donald trump"] | ["donald trump"] | ["donald trump"] |
| rewrite_entities | ["donald trump"] | ["donald trump"] | ["donald trump"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | False | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.0 | 0.0 |
| original_words_replaced_pct | 0.0 | 0.0 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 0.0 | 0.0 |
| mean_sentence_words_original | 20.0 | 20.0 |
| mean_sentence_words_rewrite | 20.0 | 20.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.0 | 0.0 |
| punctuation_l1_per100 | 0.0 | 0.0 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | True | True |
| substantial_style_change | False | False |
| style_change_group | minimal | minimal |
| explicit_style_mean_abs_standardized_change | 0.0 | 0.0 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 12 — creators:419062
**Author:** Jim Hightower | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/jim-hightower/07/26/of-course-the-system-is-rigged-look-at-elon-musk | **תאריך:** 2026-07-08
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** wealth and power to flow uphill

### Original
From Q-Anon nuttiness to JD Vance's "Deep State" quackery, wacko right-wing conspiracies have oozed into the center of Republican politics. But don't let their goofiness obscure the fact that there is indeed a very real plot to rig America's economic and political system, causing wealth and power to flow uphill — from the workaday majority to moneyed elites.

### Paraphrase
From Q-Anon nuttiness to JD Vance's "Deep State" quackery, wacko right-wing conspiracies have infiltrated the center of Republican politics. But don't let their goofiness obscure the fact that there is indeed a very real plot to rig America's economic and political system, causing wealth and power to flow uphill — from the workaday majority to moneyed elites.

### Normalized
From Q-Anon nuttiness to JD Vance's "Deep State" quackery, wacko right-wing conspiracies have infiltrated the center of Republican politics. But don't let their goofiness obscure the fact that there is indeed a very real plot to rig America's economic and political system, causing wealth and power to flow uphill — from the workaday majority to moneyed elites.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.990483283996582 | 0.9545474648475647 | 0.9545474648475647 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 0.9985112547874451 | 0.9985112547874451 |
| entailment_forward | 0.990483283996582 | 0.9900602102279663 | 0.9900602102279663 |
| entailment_reverse | 0.990483283996582 | 0.9545474648475647 | 0.9545474648475647 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["america", "d vance", "j"] | ["america", "d vance", "j"] | ["america", "d vance", "j"] |
| rewrite_entities | ["america", "d vance", "j"] | ["america", "d vance", "j"] | ["america", "d vance", "j"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.024390243902439046 | 0.024390243902439046 |
| original_words_replaced_pct | 3.225806451612903 | 3.225806451612903 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -1.6129032258064515 | -1.6129032258064515 |
| mean_sentence_words_original | 31.0 | 31.0 |
| mean_sentence_words_rewrite | 30.5 | 30.5 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.016129032258064516 | 0.016129032258064516 |
| punctuation_l1_per100 | 0.1322051824431525 | 0.1322051824431525 |
| formality_proxy_delta | -0.07932310946589105 | -0.07932310946589105 |
| contraction_rate_delta | 0.07932310946589105 | 0.07932310946589105 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | minimal | minimal |
| explicit_style_mean_abs_standardized_change | 0.014586838794473393 | 0.014586838794473393 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 13 — creators:295188
**Author:** Connie Schultz | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/connie-schultz/01/21/we-have-our-marching-orders | **תאריך:** 2021-01-21
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** I felt hopeful watching Joe Biden and Kamala Harris

### Original
Many of us are feeling a lot of excitement, buttressed by wave after wave of relief. We are a nation of survivors. On Inauguration Day, I felt hopeful watching Joe Biden and Kamala Harris take their oaths of office. They appeared to understand what we were asking of them and accepted without reservation.

### Paraphrase
Many of us are feeling a lot of excitement, bolstered by wave after wave of relief. We are a nation of survivors. On Inauguration Day, I felt hopeful watching Joe Biden and Kamala Harris take their oaths of office. They appeared to understand what we were asking of them and accepted without reservation.

### Normalized
Many of us are feeling a lot of excitement, bolstered by wave after wave of relief. We are a nation of survivors. On Inauguration Day, I felt hopeful watching Joe Biden and Kamala Harris take their oaths of office. They appeared to understand what we were asking of them and accepted without reservation.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9693341255187988 | 0.9815154075622559 | 0.9815154075622559 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 0.996624767780304 | 0.9966247081756592 |
| entailment_forward | 0.9693341255187988 | 0.9815154075622559 | 0.9815154075622559 |
| entailment_reverse | 0.9693341255187988 | 0.9815645813941956 | 0.9815645813941956 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["a harris", "joe biden", "kamal"] | ["a harris", "joe biden", "kamal"] | ["a harris", "joe biden", "kamal"] |
| rewrite_entities | ["a harris", "joe biden", "kamal"] | ["a harris", "joe biden", "kamal"] | ["a harris", "joe biden", "kamal"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.018867924528301883 | 0.018867924528301883 |
| original_words_replaced_pct | 1.8867924528301887 | 1.8867924528301887 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 0.0 | 0.0 |
| mean_sentence_words_original | 13.25 | 13.25 |
| mean_sentence_words_rewrite | 13.25 | 13.25 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 4 | 4 |
| sentence_mean_relative_change | 0.0 | 0.0 |
| punctuation_l1_per100 | 0.0 | 0.0 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | minimal | minimal |
| explicit_style_mean_abs_standardized_change | 0.0009904319845487172 | 0.0009904319845487172 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 14 — creators:423315
**Author:** Marc Dion | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/marc-dion/09/26/dont-let-the-terrorists-win | **תאריך:** 2026-09-11
**הצעת נרטיב:** Left-wing | **confidence:** 2/3
**Evidence שמור מהמערכת:** ICE hadn't killed anyone in the street

### Original
I was working at a medium-sized city newspaper on Sept. 11, 2001. No one had stormed the Capitol yet, there had been no George Floyd riots, we hadn't started the war we were going to lose in Afghanistan, and ICE hadn't killed anyone in the street.

### Paraphrase
I was working at a medium-sized city newspaper on Sept. 11, 2001. No one had stormed the Capitol yet, there hadn't been any George Floyd riots, we hadn't started the war we were going to lose in Afghanistan, and ICE hadn't killed anyone in the street.

### Normalized
I was working at a medium-sized city newspaper on Sept. 11, 2001. No one had stormed the Capitol, there had been no George Floyd riots, we hadn't started the war we were going to lose in Afghanistan, and ICE hadn't killed anyone in the street.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9889260530471802 | 0.9892561435699463 | 0.9767842888832092 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0000001192092896 | 0.9988418817520142 | 0.9944577813148499 |
| entailment_forward | 0.9889260530471802 | 0.9892561435699463 | 0.9836245775222778 |
| entailment_reverse | 0.9889260530471802 | 0.9893134236335754 | 0.9767842888832092 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["afghanistan", "capitol", "george floyd", "ice"] | ["afghanistan", "capitol", "george floyd", "ice"] | ["afghanistan", "capitol", "george floyd", "ice"] |
| rewrite_entities | ["afghanistan", "capitol", "george floyd", "ice"] | ["afghanistan", "capitol", "george floyd", "ice"] | ["afghanistan", "capitol", "george floyd", "ice"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.0505050505050505 | 0.010309278350515427 |
| original_words_replaced_pct | 4.081632653061225 | 0.0 |
| original_words_deleted_pct | 0.0 | 2.0408163265306123 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 2.0408163265306123 | -2.0408163265306123 |
| mean_sentence_words_original | 16.333333333333332 | 16.333333333333332 |
| mean_sentence_words_rewrite | 16.666666666666668 | 16.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.02040816326530627 | 0.02040816326530605 |
| punctuation_l1_per100 | 0.20408163265306145 | 0.21258503401360596 |
| formality_proxy_delta | -1.9183673469387754 | -0.08503401360544238 |
| contraction_rate_delta | 1.9183673469387754 | 0.08503401360544238 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | minimal |
| explicit_style_mean_abs_standardized_change | 0.02992373350205184 | 0.0182997492450934 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 15 — creators:422146
**Author:** Froma Harrop | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/froma-harrop/08/26/insulting-canada-is-sick-economic-policy | **תאריך:** 2026-08-25
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** big-league bullying

### Original
Oh good, another war. This time a trade war with Canada and for no other reason than ... what? To give Donald Trump a new stage for big-league bullying? To divert attention from the Jeffrey Epstein files? Who knows. Whatever. Trying to humiliate our closest ally does not serve American interests, ya think?

### Paraphrase
Oh good, another war. This time a trade war with Canada and for no other reason than ... what? To give Donald Trump a new stage for big-league bullying? To divert attention from the Jeffrey Epstein files? Who knows. Whatever. Trying to humiliate our closest ally does not serve American interests, does it?

### Normalized
Oh good, another war. This time a trade war with Canada and for no other reason than ... to give Donald Trump a new stage for big-league bullying? To divert attention from the Jeffrey Epstein files? Who knows. Whatever. Trying to humiliate our closest ally does not serve American interests, does it?

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.975837230682373 | 0.871429443359375 | 0.9197399616241455 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 0.9979168176651001 | 0.9913294315338135 |
| entailment_forward | 0.975837230682373 | 0.937386691570282 | 0.9555895924568176 |
| entailment_reverse | 0.975837230682373 | 0.871429443359375 | 0.9197399616241455 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["canada", "donald trump", "jeffrey epstein"] | ["canada", "donald trump", "jeffrey epstein"] | ["canada", "donald trump", "jeffrey epstein"] |
| rewrite_entities | ["canada", "donald trump", "jeffrey epstein"] | ["canada", "donald trump", "jeffrey epstein"] | ["canada", "donald trump", "jeffrey epstein"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.037735849056603765 | 0.04761904761904767 |
| original_words_replaced_pct | 3.7735849056603774 | 3.7735849056603774 |
| original_words_deleted_pct | 0.0 | 1.8867924528301887 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 0.0 | -1.8867924528301887 |
| mean_sentence_words_original | 6.625 | 6.625 |
| mean_sentence_words_rewrite | 6.625 | 7.428571428571429 |
| sentence_count_original | 8 | 8 |
| sentence_count_rewrite | 8 | 7 |
| sentence_mean_relative_change | 0.0 | 0.12129380053908359 |
| punctuation_l1_per100 | 0.0 | 1.886792452830189 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | minimal | minimal |
| explicit_style_mean_abs_standardized_change | 0.15826447700067398 | 0.20257240089358322 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 16 — creators:421853
**Author:** Veronique de Rugy | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/veronique-de-rugy/08/26/those-who-build-and-the-politicians-who-take | **תאריך:** 2026-08-20
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** Those who can't, devise ways for the government to take shares

### Original
There's an old saying: Those who can, do; those who can't, teach. A similar idea underscores the debate over wealth taxes in California and elsewhere: Those who can, build companies. Those who can't, devise ways for the government to take shares in what others have built.

### Paraphrase
There's an old saying: Those who can, do; those who can't, teach. A similar idea underlies the discussion about wealth taxes in California and elsewhere: Those who can, build companies. Those who can't, find ways for the government to take shares in what others have built.

### Normalized
There's an old saying: Those who can, do; those who can't, teach. A similar idea underlies the debate over wealth taxes in California and elsewhere: Those who can, build companies. Those who can't, find ways for the government to take shares in what others have built.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9737749695777893 | 0.952980637550354 | 0.9171125292778015 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0000001192092896 | 0.9887046813964844 | 0.9931656718254089 |
| entailment_forward | 0.9737749695777893 | 0.9814886450767517 | 0.9617086052894592 |
| entailment_reverse | 0.9737749695777893 | 0.952980637550354 | 0.9171125292778015 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["california"] | ["california"] | ["california"] |
| rewrite_entities | ["california"] | ["california"] | ["california"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.08163265306122447 | 0.04081632653061229 |
| original_words_replaced_pct | 8.16326530612245 | 4.081632653061225 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 0.0 | 0.0 |
| mean_sentence_words_original | 16.333333333333332 | 16.333333333333332 |
| mean_sentence_words_rewrite | 16.333333333333332 | 16.333333333333332 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.0 | 0.0 |
| punctuation_l1_per100 | 0.0 | 0.0 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | minimal |
| explicit_style_mean_abs_standardized_change | 0.0010129426031462545 | 0.0040606510427162726 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 17 — creators:418620
**Author:** David Harsanyi | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/david-harsanyi/06/26/the-socialist-revolution-will-eat-the-democratic-party | **תאריך:** 2026-06-26
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** New York City has already fallen to a champion of Third Worldism

### Original
The next mayor of Washington, D.C. is likely to be a Marxist. In Los Angeles, the Mensheviks and Bolsheviks are battling it out for control. New York City has already fallen to a champion of Third Worldism.

### Paraphrase
The next mayor of Washington, D.C. is likely to be a Marxist, as Los Angeles sees a battle between Mensheviks and Bolsheviks for control, and New York City has already succumbed to a champion of Third Worldism.

### Normalized
The next mayor of Washington, D.C. is likely to be a Marxist. In Los Angeles, the Mensheviks and Bolsheviks are battling it out for control. New York City has already fallen to a champion of Third Worldism.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9857280850410461 | 0.8691766262054443 | 0.9857280850410461 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 0.8691766262054443 | 1.0 |
| entailment_forward | 0.9857280850410461 | 0.9828004837036133 | 0.9857280850410461 |
| entailment_reverse | 0.9857280850410461 | 0.9970740079879761 | 0.9857280850410461 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["los angeles", "new york city", "washington d c"] | ["los angeles", "new york city", "washington d c"] | ["los angeles", "new york city", "washington d c"] |
| rewrite_entities | ["los angeles", "new york city", "washington d c"] | ["los angeles", "new york city", "washington d c"] | ["los angeles", "new york city", "washington d c"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.1842105263157895 | 0.0 |
| original_words_replaced_pct | 7.894736842105263 | 0.0 |
| original_words_deleted_pct | 10.526315789473685 | 0.0 |
| inserted_words_per100_original | 2.6315789473684212 | 0.0 |
| word_length_change_pct | 0.0 | 0.0 |
| mean_sentence_words_original | 7.6 | 7.6 |
| mean_sentence_words_rewrite | 12.666666666666666 | 7.6 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 3 | 5 |
| sentence_mean_relative_change | 0.6666666666666666 | 0.0 |
| punctuation_l1_per100 | 2.6315789473684204 | 0.0 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | True |
| substantial_style_change | True | False |
| style_change_group | substantial | minimal |
| explicit_style_mean_abs_standardized_change | 0.28248672311995193 | 0.0 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 18 — creators:114783
**Author:** Chuck Norris | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/chuck-norris/09/14/america-at-the-tipping-point-part-2 | **תאריך:** 2014-09-09
**הצעת נרטיב:** Right-wing | **confidence:** 2/3
**Evidence שמור מהמערכת:** no-strategy strategy for stopping Islamic extremists

### Original
We said on 9/11 that we'd "never forget." But when our president has a no-strategy strategy for stopping Islamic extremists, isn't Washington sidestepping our commitment of remembrance, in addition to its duty to protect our land and liberties?

### Paraphrase
We said on 9/11 that we'd "never forget." But with our president's no-strategy approach to combating Islamic extremists, doesn't Washington seem to be ignoring its commitment to our remembrance, as well as its duty to safeguard our land and liberties?

### Normalized
We said on 9/11 that we'd "never forget." But when our president has a no-strategy strategy for stopping Islamic extremists, isn't Washington sidestepping its commitment of remembrance, in addition to its duty to protect our land and liberties?

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.973131000995636 | 0.9561827778816223 | 0.9284310936927795 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 0.9561827778816223 | 0.9965701103210449 |
| entailment_forward | 0.973131000995636 | 0.9908340573310852 | 0.9284310936927795 |
| entailment_reverse | 0.973131000995636 | 0.987631618976593 | 0.959873616695404 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["washington"] | ["washington"] | ["washington"] |
| rewrite_entities | ["washington"] | ["washington"] | ["washington"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.3563218390804598 | 0.023809523809523836 |
| original_words_replaced_pct | 28.571428571428573 | 2.380952380952381 |
| original_words_deleted_pct | 4.761904761904762 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 7.142857142857143 | 0.0 |
| mean_sentence_words_original | 21.0 | 21.0 |
| mean_sentence_words_rewrite | 22.5 | 21.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.07142857142857142 | 0.0 |
| punctuation_l1_per100 | 0.6349206349206344 | 0.0 |
| formality_proxy_delta | -1.904761904761905 | 0.0 |
| contraction_rate_delta | 1.904761904761905 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | False |
| style_change_group | substantial | minimal |
| explicit_style_mean_abs_standardized_change | 0.45537581150426026 | 0.04346429632176252 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 19 — creators:224770
**Author:** Lawrence Kudlow | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/lawrence-kudlow/03/18/understanding-the-trump-trade-doctrine | **תאריך:** 2018-03-13
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** Good decision

### Original
Last week, Donald Trump dialed back his earlier call for a punitive and blanket tariff on imported steel and aluminum. Good decision. The financial markets rallied, as the new plan specifically targets countries that are cheating and stealing, such as China and Russia, and provides exemptions for allies.

### Paraphrase
Last week, Donald Trump scaled back his initial call for a punitive and blanket tariff on steel and aluminum. Good move. The financial markets responded positively, as the revised plan focuses on countries that are cheating and stealing, notably China and Russia, while offering exemptions to allies.

### Normalized
Last week, Donald Trump dialed back his earlier call for a punitive and blanket tariff on imported steel and aluminum. Good decision. The financial markets rallied, as the new plan specifically targets countries that are cheating and stealing, such as China and Russia, and provides exemptions for allies.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9796739220619202 | 0.9722265005111694 | 0.9796739220619202 |
| rejection_reasons |  |  |  |
| semantic_similarity | 1.0 | 0.9722265005111694 | 1.0 |
| entailment_forward | 0.9796739220619202 | 0.9962692260742188 | 0.9796739220619202 |
| entailment_reverse | 0.9796739220619202 | 0.9888519644737244 | 0.9796739220619202 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["china", "donald trump", "russia"] | ["china", "donald trump", "russia"] | ["china", "donald trump", "russia"] |
| rewrite_entities | ["china", "donald trump", "russia"] | ["china", "donald trump", "russia"] | ["china", "donald trump", "russia"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.26315789473684215 | 0.0 |
| original_words_replaced_pct | 25.0 | 0.0 |
| original_words_deleted_pct | 2.0833333333333335 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -2.0833333333333335 | 0.0 |
| mean_sentence_words_original | 16.0 | 16.0 |
| mean_sentence_words_rewrite | 15.666666666666666 | 16.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.02083333333333337 | 0.0 |
| punctuation_l1_per100 | 0.17730496453900635 | 0.0 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | True |
| substantial_style_change | False | False |
| style_change_group | intermediate | minimal |
| explicit_style_mean_abs_standardized_change | 0.2463251898060954 | 0.0 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 20 — creators:8b0d99b23d03
**Author:** Jamie Stiehm | **Split:** train | **קבוצה:** minimal_style_proxy
**מקור:** https://www.creators.com/read/jamie-stiehm/10/26/a-tale-of-two-americas-2a9c4 | **תאריך:** 2026-10-07
**הצעת נרטיב:** Left-wing | **confidence:** 2/3
**Evidence שמור מהמערכת:** about two countries, both inside America's borders

### Original
"The rich are different from you and me." — F. Scott Fitzgerald I read two books in one weekend: "Just Mercy" by Bryan Stevenson on Saturday, "Strangers" by Belle Burden on Sunday. They're true stories, told well, about two countries, both inside America's borders: Death Row in Alabama, Martha's Vineyard in Massachusetts.

### Paraphrase
"The rich are different from you and me." — F. Scott Fitzgerald. I read two books in one weekend: "Just Mercy" by Bryan Stevenson on Saturday, "Strangers" by Belle Burden on Sunday. They're true stories, told well, about two countries, both inside America's borders: Death Row in Alabama, Martha's Vineyard in Massachusetts.

### Normalized
"The rich are different from you and me." — F. Scott Fitzgerald I read two books in one weekend: "Just Mercy" by Bryan Stevenson on Saturday, "Strangers" by Belle Burden on Sunday. They're true stories, told well, about two countries, both inside America's borders: Death Row in Alabama, Martha's Vineyard in Massachusetts.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | True |
| validation_score | 0.9657033085823059 | 0.9768226146697998 | 0.9657033085823059 |
| rejection_reasons |  |  |  |
| semantic_similarity | 0.9999999403953552 | 0.9934455156326294 | 0.9999999403953552 |
| entailment_forward | 0.9657033085823059 | 0.9815694093704224 | 0.9657033085823059 |
| entailment_reverse | 0.9657033085823059 | 0.9768226146697998 | 0.9657033085823059 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["alabama", "america", "belle burden", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] | ["alabama", "america", "belle burden", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] | ["alabama", "america", "belle burden", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] |
| rewrite_entities | ["alabama", "america", "belle burden", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] | ["alabama", "america", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] | ["alabama", "america", "belle burden", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | False | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.0 | 0.0 |
| original_words_replaced_pct | 0.0 | 0.0 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 0.0 | 0.0 |
| mean_sentence_words_original | 13.5 | 13.5 |
| mean_sentence_words_rewrite | 10.8 | 13.5 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 5 | 4 |
| sentence_mean_relative_change | 0.19999999999999996 | 0.0 |
| punctuation_l1_per100 | 0.0 | 0.0 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | True |
| substantial_style_change | False | False |
| style_change_group | minimal | minimal |
| explicit_style_mean_abs_standardized_change | 0.006845134270159179 | 0.0 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 21 — creators:97c9d6b9ac1b
**Author:** Jamie Stiehm | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/jamie-stiehm/10/26/my-kingdom-for-another-golf-course | **תאריך:** 2026-10-14
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** before Donald Trump destroyed it

### Original
WASHINGTON — Something told me to get me over to East Potomac Park before Donald Trump destroyed it. Sure enough, I did, on a rainy Sunday morning, for a rally to protect the waterfront parkland from his axe. On the next weekend, he cut down 430 trees — for a fancy golf course, of course. He sneakily started on a Saturday morning on the three-day holiday weekend.

### Paraphrase
WASHINGTON — Something told me to get to East Potomac Park before Donald Trump could destroy it. Sure enough, I did on a rainy Sunday morning for a rally to protect the waterfront parkland from his axe. The next weekend, he cut down 430 trees — for a fancy golf course, of course. He sneakily started on a Saturday morning during the three-day holiday weekend.

### Normalized
WASHINGTON — Something told me to get to East Potomac Park before Donald Trump destroyed it. Sure enough, I did on a rainy Sunday morning for a rally to protect the waterfront parkland from his axe. On the next weekend, he cut down 430 trees — for a fancy golf course, of course. He sneakily started on a Saturday morning during the three-day holiday weekend.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.98273104429245 | 0.9633696675300598 | 0.9616901874542236 |
| rejection_reasons |  | certainty |  |
| semantic_similarity | 1.0 | 0.9910916090011597 | 0.9950330853462219 |
| entailment_forward | 0.98273104429245 | 0.9633696675300598 | 0.9882811903953552 |
| entailment_reverse | 0.98273104429245 | 0.9774188995361328 | 0.9616901874542236 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["donald trump", "east potomac park", "washington"] | ["donald trump", "east potomac park", "washington"] | ["donald trump", "east potomac park", "washington"] |
| rewrite_entities | ["donald trump", "east potomac park", "washington"] | ["donald trump", "east potomac park"] | ["donald trump", "east potomac park"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | False | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: certainty

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.06153846153846154 | 0.03076923076923077 |
| original_words_replaced_pct | 3.0303030303030303 | 1.5151515151515151 |
| original_words_deleted_pct | 4.545454545454546 | 3.0303030303030303 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -3.0303030303030303 | -3.0303030303030303 |
| mean_sentence_words_original | 16.5 | 16.5 |
| mean_sentence_words_rewrite | 16.0 | 16.0 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 4 | 4 |
| sentence_mean_relative_change | 0.030303030303030304 | 0.030303030303030304 |
| punctuation_l1_per100 | 3.0303030303030307 | 3.0303030303030307 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | minimal |
| explicit_style_mean_abs_standardized_change | 0.12110800945897034 | 0.09270720469874293 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 22 — creators:423545
**Author:** Jim Hightower | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/jim-hightower/09/26/gregs-folly-governor-abbott-gets-hoisted-on-his-own-petard | **תאריך:** 2026-09-16
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** the right-wing hack who is governor of Texas

### Original
Greg Abbott, the right-wing hack who is governor of Texas, probably doesn't know what a "petard" is, but he's now been hoisted by a big one. "Hoist on a petard" is a Shakespearean phrase for a bomb maker being blown sky-high by his own creation.

### Paraphrase
Greg Abbott, the right-wing hack who is governor of Texas, probably doesn't know what a "petard" is, but he's now been hoist on a petard. "Hoist on a petard" is a Shakespearean phrase for a bomb maker being blown sky-high by his own creation.

### Normalized
Greg Abbott, the right-wing hack who is governor of Texas, probably doesn't know what a "petard" is, but he's now been hoisted by a big one. "Hoist on a petard" is a Shakespearean phrase meaning a bomb maker being blown sky-high by his own creation.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.9857694506645203 | 0.15865349769592285 | 0.9858945608139038 |
| rejection_reasons |  | bidirectional_nli |  |
| semantic_similarity | 1.0 | 0.9757769107818604 | 0.9984816312789917 |
| entailment_forward | 0.9857694506645203 | 0.9570881724357605 | 0.9858945608139038 |
| entailment_reverse | 0.9857694506645203 | 0.15865349769592285 | 0.9885536432266235 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | True | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["greg abbott", "texas"] | ["greg abbott", "texas"] | ["greg abbott", "texas"] |
| rewrite_entities | ["greg abbott", "texas"] | ["greg abbott", "texas"] | ["greg abbott", "texas"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | False | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: bidirectional_nli

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.07216494845360821 | 0.020408163265306145 |
| original_words_replaced_pct | 8.16326530612245 | 2.0408163265306123 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -2.0408163265306123 | 0.0 |
| mean_sentence_words_original | 24.5 | 24.5 |
| mean_sentence_words_rewrite | 24.0 | 24.5 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.02040816326530612 | 0.0 |
| punctuation_l1_per100 | 0.21258503401360596 | 0.0 |
| formality_proxy_delta | -0.08503401360544238 | 0.0 |
| contraction_rate_delta | 0.08503401360544238 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | minimal |
| explicit_style_mean_abs_standardized_change | 0.11263132530202727 | 0.027572651993659308 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 23 — creators:298495
**Author:** Connie Schultz | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/connie-schultz/03/21/praise-jesus-but-not-really | **תאריך:** 2021-03-11
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** those who brandished God as a weapon in opposing LGBTQ rights

### Original
After I first started writing a column, in the fall of 2002, it wasn't long before I heard regularly from those who brandished God as a weapon in opposing LGBTQ rights. This was not surprising. Back then, I was on staff at The Plain Dealer in Cleveland, and I was long familiar with the bigotry in my home state. Most of the hate mail came from strangers, but I got my share of lectures from blood relatives, too. Few things anger right-wing Christians more than a family member insisting she's acquainted with a different version of God.

### Paraphrase
After I began writing a column in the fall of 2002, it wasn't long before I received regular letters from those who used God as a cudgel against LGBTQ rights. This was unsurprising. At the time, I was on staff at The Plain Dealer in Cleveland, and I was well acquainted with the bigotry in my home state. Most of the hate mail came from strangers, but I also got lectures from family members. Few things infuriate right-wing Christians more than a relative insisting they know a different God.

### Normalized
After I first started writing a column in the fall of 2002, it wasn't long before I heard regularly from those who brandished God as a weapon in opposing LGBTQ rights. This was not surprising. Back then, I was on staff at The Plain Dealer in Cleveland, and I was long familiar with the bigotry in my home state. Most of the hate mail came from strangers, but I got my share of lectures from blood relatives, too. Few things anger right-wing Christians more than a family member insisting she's acquainted with a different version of God.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.988586962223053 | 0.9082664847373962 | 0.9924595952033997 |
| rejection_reasons |  | negation |  |
| semantic_similarity | 1.0 | 0.9082664847373962 | 0.998643696308136 |
| entailment_forward | 0.988586962223053 | 0.992043673992157 | 0.9924595952033997 |
| entailment_reverse | 0.988586962223053 | 0.9681627154350281 | 0.9947239756584167 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["cleveland", "god", "the plain dealer"] | ["cleveland", "god", "the plain dealer"] | ["cleveland", "god", "the plain dealer"] |
| rewrite_entities | ["cleveland", "god", "the plain dealer"] | ["cleveland", "god", "the plain dealer"] | ["cleveland", "god", "the plain dealer"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | False | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: negation

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.25654450261780104 | 0.0 |
| original_words_replaced_pct | 24.0 | 0.0 |
| original_words_deleted_pct | 5.0 | 0.0 |
| inserted_words_per100_original | 1.0 | 0.0 |
| word_length_change_pct | -9.0 | 0.0 |
| mean_sentence_words_original | 20.0 | 20.0 |
| mean_sentence_words_rewrite | 18.2 | 20.0 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.09000000000000004 | 0.0 |
| punctuation_l1_per100 | 1.703296703296703 | 1.0 |
| formality_proxy_delta | 0.901098901098901 | 0.0 |
| contraction_rate_delta | -0.901098901098901 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | False |
| style_change_group | substantial | minimal |
| explicit_style_mean_abs_standardized_change | 0.28784806333371604 | 0.005880298775574856 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 24 — creators:418904
**Author:** Marc Dion | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/marc-dion/07/26/the-fall-of-vicksburg | **תאריך:** 2026-07-03
**הצעת נרטיב:** Left-wing | **confidence:** 2/3
**Evidence שמור מהמערכת:** Long memories still mourn the Lost Cause

### Original
"We didn't celebrate the Fourth of July," he told me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, fell to Union troops on July 4, 1863. The Confederates surrendered, as was their habit. Long memories still mourn the Lost Cause of Black backs whipped bloody.

### Paraphrase
"We didn't mark the Fourth of July," he told me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, fell to Union troops on July 4, 1863. The Confederates surrendered, as was their habit. Long memories still mourn the Lost Cause of Black backs whipped bloody.

### Normalized
"We didn't celebrate the Fourth of July," he told me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, fell to Union troops on July 4, 1863. The Confederates surrendered, as was their habit. Long memories still mourn the Lost Cause of Black backs whipped bloody.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.9838917851448059 | 0.8919214010238647 | 0.9838917851448059 |
| rejection_reasons |  | quotations |  |
| semantic_similarity | 1.0 | 0.988548755645752 | 1.0000001192092896 |
| entailment_forward | 0.9838917851448059 | 0.8919214010238647 | 0.9838917851448059 |
| entailment_reverse | 0.9838917851448059 | 0.920892596244812 | 0.9838917851448059 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["mississippi", "vicksburg"] | ["mississippi", "vicksburg"] | ["mississippi", "vicksburg"] |
| rewrite_entities | ["mississippi", "vicksburg"] | ["mississippi", "vicksburg"] | ["mississippi", "vicksburg"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | False | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: quotations

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.02083333333333337 | 0.0 |
| original_words_replaced_pct | 2.0833333333333335 | 0.0 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 0.0 | 0.0 |
| mean_sentence_words_original | 9.6 | 9.6 |
| mean_sentence_words_rewrite | 9.6 | 9.6 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.0 | 0.0 |
| punctuation_l1_per100 | 0.0 | 0.0 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | True |
| substantial_style_change | False | False |
| style_change_group | minimal | minimal |
| explicit_style_mean_abs_standardized_change | 0.005913316976794756 | 0.0 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 25 — creators:2e34435c6ccf
**Author:** Froma Harrop | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/froma-harrop/10/26/guilfoyle-never-mastered-the-art-of-the-shakedown | **תאריך:** 2026-10-15
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** Trump's money-grabbing corruption

### Original
About three weeks before Republicans expect an electoral beating, Donald Trump had to get rid of Kimberly Guilfoyle, his ambassador to Greece. He simply had to. Trump's money-grabbing corruption was wearing thin even on devoted fans, but the president knew how to wrap his mob-like patter in foggy euphemisms and double meanings.

### Paraphrase
About three weeks before Republicans expected an electoral setback, Donald Trump had to remove Kimberly Guilfoyle, his ambassador to Greece. He simply had to. Trump's money-grubbing corruption was becoming tiresome even to his loyal supporters, but the president knew how to cloak his mob-like patter in foggy euphemisms and double meanings.

### Normalized
About three weeks before Republicans expected an electoral defeat, Donald Trump had to remove Kimberly Guilfoyle, his ambassador to Greece. He simply had to. Trump's corrupt money-grabbing was wearing thin even on devoted fans, but the president knew how to wrap his mob-like patter in foggy euphemisms and double meanings.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | True | False |
| validation_score | 0.990394651889801 | 0.972994863986969 | 0.9767442941665649 |
| rejection_reasons |  |  | framing_anchors |
| semantic_similarity | 0.9999998807907104 | 0.972994863986969 | 0.9767442941665649 |
| entailment_forward | 0.990394651889801 | 0.9928680658340454 | 0.9960858821868896 |
| entailment_reverse | 0.990394651889801 | 0.9861352443695068 | 0.9916681051254272 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["donald trump", "greece", "kimberly guilfoyle", "trump"] | ["donald trump", "greece", "kimberly guilfoyle", "trump"] | ["donald trump", "greece", "kimberly guilfoyle", "trump"] |
| rewrite_entities | ["donald trump", "greece", "kimberly guilfoyle", "trump"] | ["donald trump", "greece", "kimberly guilfoyle", "trump"] | ["donald trump", "greece", "kimberly guilfoyle", "trump"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | False |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Normalized:** נפסל אוטומטית: framing_anchors

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.21100917431192656 | 0.09259259259259256 |
| original_words_replaced_pct | 21.818181818181817 | 9.090909090909092 |
| original_words_deleted_pct | 0.0 | 1.8181818181818181 |
| inserted_words_per100_original | 0.0 | 1.8181818181818181 |
| word_length_change_pct | -1.8181818181818181 | -3.6363636363636362 |
| mean_sentence_words_original | 18.333333333333332 | 18.333333333333332 |
| mean_sentence_words_rewrite | 18.0 | 17.666666666666668 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.01818181818181812 | 0.03636363636363624 |
| punctuation_l1_per100 | 0.1683501683501687 | 0.3430531732418527 |
| formality_proxy_delta | -0.03367003367003374 | -0.06861063464837058 |
| contraction_rate_delta | 0.03367003367003374 | 0.06861063464837058 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | intermediate |
| explicit_style_mean_abs_standardized_change | 0.09110113841889048 | 0.03417557176948872 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 26 — creators:459e183c1d0d
**Author:** Veronique de Rugy | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/veronique-de-rugy/10/26/france-should-export-a-warning-not-its-tax-ideas | **תאריך:** 2026-10-22
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** a familiar French solution to a fiscal problem

### Original
French economist Gabriel Zucman has come to California bearing a familiar French solution to a fiscal problem: another tax. Once based at the University of California, Berkeley, Zucman is back and campaigning for Proposition 40, which would impose an allegedly one-time 5% tax on the net worth of Californians worth more than $1 billion. Zucman, who coauthored the proposition, estimates that the tax could raise about $100 billion and claims that 90% of the proceeds would go to health care.

### Paraphrase
French economist Gabriel Zucman has returned to California with a familiar French solution to a fiscal issue: another tax. Based at UC Berkeley, Zucman now supports Proposition 40, which would impose a 5% tax on Californians with net worth over $1 billion. Zucman, coauthor of the proposition, estimates that this tax could raise about $100 billion, with 90% of the proceeds earmarked for healthcare.

### Normalized
French economist Gabriel Zucman has come to California with a familiar French solution to a fiscal problem: another tax. Once based at the University of California, Berkeley, Zucman is back and campaigning for Proposition 40, which would impose a 5% tax on the net worth of Californians worth more than $1 billion. Zucman, who coauthored the proposition, estimates that the tax could raise about $100 billion and claims that 90% of the proceeds would go to health care.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | False |
| validation_score | 0.9813358783721924 | 0.05327240377664566 | 0.03809588775038719 |
| rejection_reasons |  | entities\|certainty\|attribution\|bidirectional_nli | certainty\|bidirectional_nli |
| semantic_similarity | 1.0 | 0.9818807244300842 | 0.9933991432189941 |
| entailment_forward | 0.9813358783721924 | 0.9465685486793518 | 0.9793237447738647 |
| entailment_reverse | 0.9813358783721924 | 0.05327240377664566 | 0.03809588775038719 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | True | True |
| entity_recall | 1.0 | 0.8333333333333334 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["berkeley", "california", "gabriel zucman", "university of california", "zuc", "zucman"] | ["berkeley", "california", "gabriel zucman", "university of california", "zuc", "zucman"] | ["berkeley", "california", "gabriel zucman", "university of california", "zuc", "zucman"] |
| rewrite_entities | ["berkeley", "california", "gabriel zucman", "university of california", "zuc", "zucman"] | ["california", "gabriel zucman", "zucman"] | ["berkeley", "california", "gabriel zucman", "university of california", "zucman"] |
| guard_entities | True | False | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | False | False |
| guard_attribution | True | False | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | False | False |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: entities|certainty|attribution|bidirectional_nli

**Normalized:** נפסל אוטומטית: certainty|bidirectional_nli

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.3517241379310345 | 0.04402515723270439 |
| original_words_replaced_pct | 40.74074074074074 | 6.172839506172839 |
| original_words_deleted_pct | 1.2345679012345678 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -20.987654320987655 | -3.7037037037037037 |
| mean_sentence_words_original | 27.0 | 27.0 |
| mean_sentence_words_rewrite | 21.333333333333332 | 26.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.2098765432098766 | 0.037037037037037035 |
| punctuation_l1_per100 | 3.2021604938271606 | 1.5194681861348533 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | False |
| style_change_group | substantial | minimal |
| explicit_style_mean_abs_standardized_change | 0.3163338162505402 | 0.09405660713319497 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 27 — creators:416436
**Author:** David Harsanyi | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/david-harsanyi/05/26/jeff-bezos-is-right-about-capitalism-wrong-about-taxes | **תאריך:** 2026-05-22
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** Socialism will always find an audience because it appeals to base envy

### Original
Socialism will always find an audience because it appeals to base envy and resentment. Ginning up a mob to be mad at "oligarchs," "Wall Street barons," "kulaks" or "billionaires" is cheap and easy. So, it was refreshing to hear Amazon founder Jeff Bezos, the fourth richest man on the planet, offer unadulterated praise of the moral and economic superiority of capitalism in his recent interview with CNBC's Andrew Ross Sorkin.

### Paraphrase
Socialism always finds an audience, appealing to base envy and resentment. Labeling "oligarchs," "Wall Street barons," "kulaks," or "billionaires" as scapegoats is easy and cheap. It was refreshing to hear Jeff Bezos, the fourth richest man, praise capitalism's moral and economic superiority in his recent interview with Andrew Ross Sorkin on CNBC.

### Normalized
Socialism will always find an audience because it appeals to base envy and resentment. Mobilizing a mob against "oligarchs," "Wall Street barons," "kulaks," or "billionaires" is easy and cheap. Thus, it was refreshing to hear Amazon founder Jeff Bezos, the fourth richest man on the planet, offer unadulterated praise for the moral and economic superiority of capitalism in his recent interview with CNBC's Andrew Ross Sorkin.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | False |
| validation_score | 0.9855889678001404 | 0.8 | 0.9653693437576294 |
| rejection_reasons |  | entities\|future_tense\|quotations | quotations |
| semantic_similarity | 1.0 | 0.9153156280517578 | 0.9954436421394348 |
| entailment_forward | 0.9855889678001404 | 0.994411289691925 | 0.9936578869819641 |
| entailment_reverse | 0.9855889678001404 | 0.8549492359161377 | 0.9653693437576294 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 0.8 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] |
| rewrite_entities | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] | ["andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] |
| guard_entities | True | False | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | False | True |
| guard_quotations | True | False | False |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: entities|future_tense|quotations

**Normalized:** נפסל אוטומטית: quotations

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.32258064516129037 | 0.1159420289855072 |
| original_words_replaced_pct | 19.718309859154928 | 14.084507042253522 |
| original_words_deleted_pct | 21.12676056338028 | 0.0 |
| inserted_words_per100_original | 8.450704225352112 | 2.816901408450704 |
| word_length_change_pct | -25.35211267605634 | -5.633802816901408 |
| mean_sentence_words_original | 23.666666666666668 | 23.666666666666668 |
| mean_sentence_words_rewrite | 17.666666666666668 | 22.333333333333332 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.2535211267605634 | 0.05633802816901418 |
| punctuation_l1_per100 | 4.27850119585437 | 1.9129703594702532 |
| formality_proxy_delta | -0.4783417486048367 | -0.0840866092074839 |
| contraction_rate_delta | 0.4783417486048367 | 0.0840866092074839 |
| exact_copy | False | False |
| substantial_style_change | True | False |
| style_change_group | substantial | intermediate |
| explicit_style_mean_abs_standardized_change | 0.4017712942377944 | 0.1573158372512416 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 28 — creators:116358
**Author:** Chuck Norris | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/chuck-norris/09/14/supreme-court-justice-eric-holder | **תאריך:** 2014-09-30
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** a sinister and strategic plan

### Original
After 5 1/2 bumpy years of controversial service, the besieged but bolstered attorney general, Eric Holder, resigned. But is this close friend and confidant of President Barack Obama's really stepping down for some benign reason at a critical time for our country, or is there a sinister and strategic plan behind it all?

### Paraphrase
After 5 1/2 bumpy years of controversial service, the besieged but bolstered attorney general, Eric Holder, resigned. But is Eric Holder really stepping down for some benign reason at a critical time for our country, or is there a sinister and strategic plan behind it all?

### Normalized
After 5 1/2 bumpy years of controversial service, the besieged but bolstered attorney general, Eric Holder, resigned. But is this close friend and confidant of President Barack Obama's really stepping down for some benign reason at a critical time for our country, or is there a sinister and strategic plan behind it all?

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.9849591851234436 | 0.02130117639899254 | 0.9849591851234436 |
| rejection_reasons |  | entities\|bidirectional_nli |  |
| semantic_similarity | 1.0 | 0.9755910634994507 | 1.0 |
| entailment_forward | 0.9849591851234436 | 0.9865330457687378 | 0.9849591851234436 |
| entailment_reverse | 0.9849591851234436 | 0.02130117639899254 | 0.9849591851234436 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | True | False |
| entity_recall | 1.0 | 0.5 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["barack obama", "eric holder"] | ["barack obama", "eric holder"] | ["barack obama", "eric holder"] |
| rewrite_entities | ["barack obama", "eric holder"] | ["eric holder"] | ["barack obama", "eric holder"] |
| guard_entities | True | False | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | False | True |
| changed_text | False | True | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: entities|bidirectional_nli

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.11764705882352944 | 0.0 |
| original_words_replaced_pct | 18.181818181818183 | 0.0 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -14.545454545454545 | 0.0 |
| mean_sentence_words_original | 27.5 | 27.5 |
| mean_sentence_words_rewrite | 23.5 | 27.5 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.14545454545454545 | 0.0 |
| punctuation_l1_per100 | 1.5473887814313347 | 0.0 |
| formality_proxy_delta | 1.8181818181818181 | 0.0 |
| contraction_rate_delta | -1.8181818181818181 | 0.0 |
| exact_copy | False | True |
| substantial_style_change | False | False |
| style_change_group | intermediate | minimal |
| explicit_style_mean_abs_standardized_change | 0.1979024656824606 | 0.0 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 29 — creators:218236
**Author:** Lawrence Kudlow | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/lawrence-kudlow/12/17/republicans-tax-plan-takes-a-quirky-swipe-at-the-little-guys | **תאריך:** 2017-12-12
**הצעת נרטיב:** Right-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** the party that cuts the job-killing capital gains tax

### Original
Republicans are supposed to be the party that cuts the job-killing capital gains tax, not raises it. But because of a quirk in the Senate-passed tax bill, the tax on capital gains may go up — and for some types of long-held assets, fairly substantially.

### Paraphrase
Republicans claim to be the party that cuts the job-killing capital gains tax, not raises it. However, due to a quirk in the Senate-passed tax bill, the tax on capital gains might go up — and for some types of long-held assets, it could rise substantially.

### Normalized
Republicans are supposed to be the party that cuts the job-killing capital gains tax, not raises it. However, due to a quirk in the Senate-passed tax bill, the tax on capital gains may go up — and for some types of long-held assets, it could rise fairly substantially.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | False |
| validation_score | 0.9914523363113403 | 0.969977080821991 | 0.9848408102989197 |
| rejection_reasons |  | certainty | certainty |
| semantic_similarity | 1.0 | 0.9944941997528076 | 0.9966722130775452 |
| entailment_forward | 0.9914523363113403 | 0.9932460784912109 | 0.9848408102989197 |
| entailment_reverse | 0.9914523363113403 | 0.969977080821991 | 0.9944348931312561 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | False | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | [] | [] | [] |
| rewrite_entities | [] | [] | [] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | False | False |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | True | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | True | True |
| changed_text | False | True | True |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: certainty

**Normalized:** נפסל אוטומטית: certainty

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.1578947368421053 | 0.09278350515463918 |
| original_words_replaced_pct | 14.893617021276595 | 6.382978723404255 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 6.382978723404255 |
| word_length_change_pct | 2.127659574468085 | 6.382978723404255 |
| mean_sentence_words_original | 23.5 | 23.5 |
| mean_sentence_words_rewrite | 24.0 | 25.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.02127659574468085 | 0.06382978723404255 |
| punctuation_l1_per100 | 2.1276595744680855 | 2.127659574468085 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | False |
| style_change_group | substantial | intermediate |
| explicit_style_mean_abs_standardized_change | 0.39863659742167856 | 0.3731913849562967 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

## דוגמה 30 — creators:418827
**Author:** Jamie Stiehm | **Split:** train | **קבוצה:** automatic_screen_rejected
**מקור:** https://www.creators.com/read/jamie-stiehm/07/26/trumps-tawdry-and-gaudy-birthday-party | **תאריך:** 2026-07-01
**הצעת נרטיב:** Left-wing | **confidence:** 3/3
**Evidence שמור מהמערכת:** it wasn't enough to murder the White House Rose Garden

### Original
WASHINGTON — No, friends, Romans, countrymen, it wasn't enough to murder the White House Rose Garden. It wasn't enough to tear down its stately East Wing, where guests gathered and mingled. It wasn't enough to brandish "Donald J. Trump" over "John F. Kennedy" on the marble wall of the national performing arts center.

### Paraphrase
WASHINGTON — No, friends, Romans, countrymen, it wasn't enough to destroy the White House Rose Garden. It wasn't enough to tear down the stately East Wing, where guests once mingled. It wasn't enough to replace "John F. Kennedy" with "Donald J. Trump" on the national performing arts center's marble wall.

### Normalized
WASHINGTON — No, friends, Romans, countrymen, it wasn't enough to murder the White House Rose Garden. It wasn't enough to tear down its stately East Wing, where guests gathered and mingled. It wasn't enough to brandish "Donald J. Trump" over "John F. Kennedy" on the marble wall of the national performing arts center.

### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית

| בדיקה/שדה | Formatting | Paraphrase | Normalized |
|---|---|---|---|
| passed | True | False | True |
| validation_score | 0.9675588011741638 | 0.43278768658638 | 0.9675588011741638 |
| rejection_reasons |  | framing_anchors\|bidirectional_nli |  |
| semantic_similarity | 0.9999999403953552 | 0.9542156457901001 | 0.9999999403953552 |
| entailment_forward | 0.9675588011741638 | 0.9360917210578918 | 0.9675588011741638 |
| entailment_reverse | 0.9675588011741638 | 0.43278768658638 | 0.9675588011741638 |
| added_claim_risk | False | False | False |
| removed_claim_risk | False | True | False |
| entity_recall | 1.0 | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 | 1.0 |
| original_entities | ["east wing", "john f kennedy", "shington", "white house rose garden"] | ["east wing", "john f kennedy", "shington", "white house rose garden"] | ["east wing", "john f kennedy", "shington", "white house rose garden"] |
| rewrite_entities | ["east wing", "john f kennedy", "shington", "white house rose garden"] | ["east wing", "john", "shington", "trump", "white house rose garden"] | ["east wing", "john f kennedy", "shington", "white house rose garden"] |
| guard_entities | True | True | True |
| guard_numbers | True | True | True |
| guard_negation | True | True | True |
| guard_certainty | True | True | True |
| guard_attribution | True | True | True |
| guard_framing_anchors | True | False | True |
| guard_future_tense | True | True | True |
| guard_quotations | True | True | True |
| guard_full_classifier_input | True | True | True |
| guard_full_semantic_input | True | True | True |
| guard_full_nli_input | True | True | True |
| guard_length | True | True | True |
| guard_complete | True | True | True |
| guard_similarity | True | True | True |
| guard_bidirectional_nli | True | False | True |
| changed_text | False | True | False |
| human_verified | False | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

**Formatting:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

**Paraphrase:** נפסל אוטומטית: framing_anchors|bidirectional_nli

**Normalized:** עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.

### מדדי style שמורים

| מדד | Paraphrase | Normalized |
|---|---|---|
| word_edit_fraction | 0.2222222222222222 | 0.0 |
| original_words_replaced_pct | 9.090909090909092 | 0.0 |
| original_words_deleted_pct | 14.545454545454545 | 0.0 |
| inserted_words_per100_original | 5.454545454545454 | 0.0 |
| word_length_change_pct | -3.6363636363636362 | 0.0 |
| mean_sentence_words_original | 11.0 | 11.0 |
| mean_sentence_words_rewrite | 10.6 | 11.0 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.0363636363636364 | 0.0 |
| punctuation_l1_per100 | 0.41166380789022283 | 0.0 |
| formality_proxy_delta | -2.0926243567753007 | 0.0 |
| contraction_rate_delta | 2.0926243567753007 | 0.0 |
| exact_copy | False | True |
| substantial_style_change | True | False |
| style_change_group | substantial | minimal |
| explicit_style_mean_abs_standardized_change | 0.10240179486341724 | 0.0 |

### שדות למילוי חיצוני — הושארו ריקים

| שדה | תשובה |
|---|---|
| human_narrative_label | |
| narrative_label_correct | |
| paraphrase_meaning_preserved | |
| normalized_meaning_preserved | |
| style_change_valid | |
| human_notes | |

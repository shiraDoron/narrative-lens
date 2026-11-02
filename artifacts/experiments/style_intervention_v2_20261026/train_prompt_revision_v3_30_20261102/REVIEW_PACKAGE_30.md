# Review package — 30 TRAIN examples, v2 versus v3

This diagnostic package exposes prior rewrites, automatic scores and style metrics. It is not blind. For a separate less-cued external review, use REVIEW_PACKAGE_BLIND_30.md, which contains only ID, Original and v3. No new external/human review has been filled. Existing v2 judgments must not transfer to v3.

## 01 — creators:0105f26ef9f1

### Original

Good examples of that are Donald Trump, escargot and gang rape, three things that disgust me, but are keenly desired by some people. Just knowing that will make you look around for a long time before you sit next to a stranger on the bus. The fact that I can type the word "bus" without automatically putting the word "school" in front of it indicates that I might have at least some history with people whose wants and needs are not only disgusting, but poorly concealed.

### New v2

Examples of this include Donald Trump, escargot, and gang rape, three things that I find repulsive, yet are desired by some individuals. Simply knowing this fact can make you hesitate for a long time before sitting next to a stranger on the bus. The mere ability to type "bus" without immediately thinking of "school" suggests that I may have some familiarity with people whose desires and needs are not only repulsive but also poorly concealed.

### New v3

Good examples are Donald Trump, escargot, and gang rape. Three things that disgust me, but are desired by some. Just knowing this will make you hesitate before sitting next to a stranger on the bus. The fact that I can type "bus" without immediately thinking of "school" suggests I might have some familiarity with individuals whose wants and needs are not only repulsive but also poorly hidden.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:0105f26ef9f1 | creators:0105f26ef9f1 |
| condition | Normalized | Normalized |
| passed | False | True |
| validation_score | 0.8564411401748657 | 0.8784990310668945 |
| rejection_reasons | certainty\|future_tense |  |
| semantic_similarity | 0.8564411401748657 | 0.8784990310668945 |
| entailment_forward | 0.9940474033355713 | 0.9912739396095276 |
| entailment_reverse | 0.9356308579444885 | 0.9154402017593384 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["donald trump"] | ["donald trump"] |
| rewrite_entities | ["donald trump"] | ["donald trump"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | False | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | False | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.4285714285714286 | 0.28104575163398693 |
| original_words_replaced_pct | 41.86046511627907 | 26.74418604651163 |
| original_words_deleted_pct | 4.651162790697675 | 9.30232558139535 |
| inserted_words_per100_original | 1.1627906976744187 | 1.1627906976744187 |
| word_length_change_pct | -12.790697674418604 | -22.093023255813954 |
| mean_sentence_words_original | 28.666666666666668 | 28.666666666666668 |
| mean_sentence_words_rewrite | 25.0 | 16.75 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 4 |
| sentence_mean_relative_change | 0.12790697674418608 | 0.41569767441860467 |
| punctuation_l1_per100 | 0.6821705426356584 | 0.17355085039916762 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | True |
| style_change_group | intermediate | substantial |
| explicit_style_mean_abs_standardized_change | 0.4337591839579467 | 0.4387623587829548 |

## 02 — creators:421024

### Original

Brides should know that they already have a man. They don't have to use their wedding to attract a date for Saturday night. They've supposedly secured one for the foreseeable future. Thus, it's hard to figure how the fashion trend of "naked dressing," lamentable even at nightclubs, has invaded the precincts of ancient social custom. Displaying one's privates — or underwear — in public started as a fashion trend pushed by attention-hungry celebrities. Now it's walking down the aisle.

### New v2

Brides should realize they already have a partner. They don't need their wedding to find someone for a Saturday night. They've supposedly found one for the foreseeable future. Consequently, it's puzzling how the fashion trend of "naked dressing," even at nightclubs, has infiltrated the domain of traditional social customs. Initially, it was a fashion trend driven by celebrities seeking attention. Now, it's becoming a part of the wedding procession.

### New v3

Brides should realize they already have a partner. They don't need their wedding to find a date for the next night. They've supposedly found one for the foreseeable future. Consequently, it's puzzling how the fashion trend of "naked dressing," already considered inappropriate at nightclubs, has infiltrated the realms of traditional social customs. Initially, this trend was driven by celebrities seeking attention. Now, it's becoming a part of the wedding procession.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:421024 | creators:421024 |
| condition | Normalized | Normalized |
| passed | True | True |
| validation_score | 0.8720514178276062 | 0.8762078285217285 |
| rejection_reasons |  |  |
| semantic_similarity | 0.9091870784759521 | 0.9163079261779785 |
| entailment_forward | 0.9787566661834717 | 0.9554753303527832 |
| entailment_reverse | 0.8720514178276062 | 0.8762078285217285 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | [] | [] |
| rewrite_entities | [] | [] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.3846153846153846 | 0.4140127388535032 |
| original_words_replaced_pct | 36.144578313253014 | 42.16867469879518 |
| original_words_deleted_pct | 6.024096385542169 | 2.4096385542168677 |
| inserted_words_per100_original | 2.4096385542168677 | 2.4096385542168677 |
| word_length_change_pct | -12.048192771084338 | -10.843373493975903 |
| mean_sentence_words_original | 13.833333333333334 | 13.833333333333334 |
| mean_sentence_words_rewrite | 12.166666666666666 | 12.333333333333334 |
| sentence_count_original | 6 | 6 |
| sentence_count_rewrite | 6 | 6 |
| sentence_mean_relative_change | 0.12048192771084346 | 0.10843373493975904 |
| punctuation_l1_per100 | 6.8493150684931505 | 6.756756756756757 |
| formality_proxy_delta | 0.5446443307476487 | 0.6186909801367637 |
| contraction_rate_delta | -0.5446443307476487 | -0.6186909801367637 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.2641363813990636 | 0.2610804660652968 |

## 03 — creators:422329

### Original

The U.S. national debt just crossed the $40 trillion threshold, doubling in less than a decade. Washington politicians have responded with their favorite fiscal game: blaming the other party. Democrats say Republican tax cuts are the culprit. Republicans say Democratic spending is the root cause. But both parties are responsible, with both hiding behind a lie of omission. And if we let them, they'll keep driving us into the same wall together.

### New v2

The U.S. national debt has now surpassed the $40 trillion mark, doubling in just a decade. Washington politicians have reacted with their usual fiscal games: pinning the blame on whichever party is in power. Democrats argue that Republican tax cuts are the main issue. Republicans contend that Democratic spending is the root cause. Yet, both parties are culpable, each hiding behind a deceitful omission. And if we allow them to continue, they will keep us driving toward the same fiscal cliff together.

### New v3

The U.S. national debt has now surpassed the $40 trillion mark, doubling in less than a decade. Politicians in Washington have once again resorted to their usual fiscal games: pinning the blame on whichever party is in power. Democrats argue that Republican tax cuts are the primary issue. Republicans contend that Democratic spending is the root cause. Yet, both parties are culpable, each hiding behind a veil of omission. And if we allow them to continue, they will keep us careening toward the same fiscal cliff together.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:422329 | creators:422329 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.2959902584552765 | 0.3092098534107208 |
| rejection_reasons | bidirectional_nli | bidirectional_nli |
| semantic_similarity | 0.9702205657958984 | 0.9663116931915283 |
| entailment_forward | 0.2959902584552765 | 0.3092098534107208 |
| entailment_reverse | 0.705357015132904 | 0.7990521788597107 |
| added_claim_risk | True | True |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["u s", "washington"] | ["u s", "washington"] |
| rewrite_entities | ["u s", "washington"] | ["u s", "washington"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.36305732484076436 | 0.37037037037037035 |
| original_words_replaced_pct | 32.432432432432435 | 28.37837837837838 |
| original_words_deleted_pct | 0.0 | 2.7027027027027026 |
| inserted_words_per100_original | 8.108108108108109 | 9.45945945945946 |
| word_length_change_pct | 12.162162162162161 | 18.91891891891892 |
| mean_sentence_words_original | 9.25 | 9.25 |
| mean_sentence_words_rewrite | 10.375 | 11.0 |
| sentence_count_original | 8 | 8 |
| sentence_count_rewrite | 8 | 8 |
| sentence_mean_relative_change | 0.12162162162162163 | 0.1891891891891892 |
| punctuation_l1_per100 | 0.9117551286225984 | 0.7063882063882063 |
| formality_proxy_delta | 1.3513513513513513 | 1.3513513513513513 |
| contraction_rate_delta | -1.3513513513513513 | -1.3513513513513513 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.21975339484676754 | 0.26113425427684095 |

## 04 — creators:417181

### Original

It turns out that the most generous funder of white supremacist groups in the United States was likely the Southern Poverty Law Center. At least that's what the Department of Justice's superseding indictment against the SPLC alleges. The organization secretly paid informants to engage in the active promotion and funding of racist groups while denouncing and "fighting" the very same groups in public. The SPLC purportedly created fictitious entities to hide funding from their donors.

### New v2

Indeed, the SPLC, the primary financier of white supremacist organizations in the U.S., appears to have been the target of allegations from the Department of Justice in its superseding indictment. The DOJ claims that the SPLC covertly funded and promoted racist groups through informants, while publicly denouncing them. Additionally, the SPLC allegedly established fake entities to obscure its donors' contributions.

### New v3

It appears that the Southern Poverty Law Center, a major funder of white supremacist groups in the United States, may have been secretly supporting these groups through informants and pseudonymous entities. According to a superseding indictment by the Department of Justice, the SPLC allegedly engaged in active promotion and funding of racist organizations while publicly denouncing them. The organization allegedly created fake entities to obscure its funding from donors.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:417181 | creators:417181 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.5 | 0.7702270150184631 |
| rejection_reasons | entities\|certainty\|quotations | certainty\|quotations |
| semantic_similarity | 0.8831478357315063 | 0.8874514102935791 |
| entailment_forward | 0.9530072212219238 | 0.9829195737838745 |
| entailment_reverse | 0.7925833463668823 | 0.7702270150184631 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 0.5 | 1.0 |
| entity_precision | 0.5 | 1.0 |
| original_entities | ["department of justice", "southern poverty law center", "splc", "united states"] | ["department of justice", "southern poverty law center", "splc", "united states"] |
| rewrite_entities | ["department of justice", "doj", "splc", "u s"] | ["department of justice", "southern poverty law center", "splc", "united states"] |
| guard_entities | False | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | False | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | False | False |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.6376811594202898 | 0.5342465753424658 |
| original_words_replaced_pct | 67.53246753246754 | 48.05194805194805 |
| original_words_deleted_pct | 0.0 | 7.792207792207792 |
| inserted_words_per100_original | 5.194805194805195 | 1.2987012987012987 |
| word_length_change_pct | -20.77922077922078 | -10.38961038961039 |
| mean_sentence_words_original | 19.25 | 19.25 |
| mean_sentence_words_rewrite | 12.2 | 23.0 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 5 | 3 |
| sentence_mean_relative_change | 0.36623376623376624 | 0.19480519480519481 |
| punctuation_l1_per100 | 8.19672131147541 | 4.3478260869565215 |
| formality_proxy_delta | 2.5974025974025974 | 2.5974025974025974 |
| contraction_rate_delta | -2.5974025974025974 | -2.5974025974025974 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.363915812799261 | 0.4270798940347802 |

## 05 — creators:120177

### Original

Folks, our country is heading down a slippery slope. We have to stop it before it is too late. We haven't even hit Thanksgiving, and already the war on Christmas is underway. This time, one of the largest public school systems in the U.S. is eliminating every mention of religious holidays on its official calendar.

### New v2

Ladies and gentlemen, our nation is careening towards a precipice. We must halt this descent before it's too late. We haven't even reached Thanksgiving yet, and the war on Christmas has already begun. In fact, one of the largest public school systems in the U.S. is now scrubbing all references to religious holidays from its official calendar.

### New v3

Ladies and gentlemen, our nation is on a perilous trajectory. We must act now to prevent a slide into irreversibility. It's barely Thanksgiving, and already the battle over Christmas is raging. In one of the biggest school districts in the U.S., they've decided to remove all references to religious holidays from their official calendar.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:120177 | creators:120177 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.9090394973754883 | 0.8534104228019714 |
| rejection_reasons | certainty | negation\|certainty |
| semantic_similarity | 0.9090394973754883 | 0.8534104228019714 |
| entailment_forward | 0.9571309685707092 | 0.9806522130966187 |
| entailment_reverse | 0.9464792609214783 | 0.9261319637298584 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["u s"] | ["u s"] |
| rewrite_entities | ["u s"] | ["u s"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | False |
| guard_certainty | False | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.4017094017094017 | 0.5789473684210527 |
| original_words_replaced_pct | 36.8421052631579 | 57.89473684210526 |
| original_words_deleted_pct | 1.7543859649122806 | 0.0 |
| inserted_words_per100_original | 1.7543859649122806 | 0.0 |
| word_length_change_pct | 5.2631578947368425 | 0.0 |
| mean_sentence_words_original | 9.5 | 9.5 |
| mean_sentence_words_rewrite | 10.0 | 9.5 |
| sentence_count_original | 6 | 6 |
| sentence_count_rewrite | 6 | 6 |
| sentence_mean_relative_change | 0.05263157894736842 | 0.0 |
| punctuation_l1_per100 | 0.2631578947368425 | 0.0 |
| formality_proxy_delta | -1.5789473684210529 | -1.7543859649122806 |
| contraction_rate_delta | 1.5789473684210529 | 1.7543859649122806 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.27074127764024686 | 0.36300069785693645 |

## 06 — creators:212505

### Original

Financial markets and most media pundits are missing the new writing on the wall. For a variety of reasons surrounding shrewd moves by President Trump, the chances for significant tax cuts in the next 10 weeks have risen sharply.

### New v2

Financial markets and many media analysts are overlooking the emerging trends. Various factors, including President Trump's strategic maneuvers, have increased the likelihood of substantial tax cuts within the next ten weeks.

### New v3

Financial markets and many media pundits are overlooking the new developments. Various factors, including shrewd moves by President Trump, have increased the likelihood of substantial tax cuts in the upcoming 10 weeks.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:212505 | creators:212505 |
| condition | Normalized | Normalized |
| passed | False | True |
| validation_score | 0.9374085664749146 | 0.8659044504165649 |
| rejection_reasons | numbers |  |
| semantic_similarity | 0.9374085664749146 | 0.9168146848678589 |
| entailment_forward | 0.9960049986839294 | 0.9959249496459961 |
| entailment_reverse | 0.9403371810913086 | 0.8659044504165649 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["trump"] | ["trump"] |
| rewrite_entities | ["trump"] | ["trump"] |
| guard_entities | True | True |
| guard_numbers | False | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.6056338028169015 | 0.43661971830985913 |
| original_words_replaced_pct | 56.41025641025641 | 41.02564102564103 |
| original_words_deleted_pct | 7.6923076923076925 | 7.6923076923076925 |
| inserted_words_per100_original | 12.820512820512821 | 5.128205128205129 |
| word_length_change_pct | -17.94871794871795 | -17.94871794871795 |
| mean_sentence_words_original | 19.5 | 19.5 |
| mean_sentence_words_rewrite | 16.0 | 16.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.1794871794871795 | 0.1794871794871795 |
| punctuation_l1_per100 | 3.6858974358974357 | 3.6858974358974357 |
| formality_proxy_delta | -3.125 | 0.0 |
| contraction_rate_delta | 3.125 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.32816264219532876 | 0.2475004310732711 |

## 07 — creators:421951

### Original

Way back there in the 1700s and the 1800s, the British conquered a big chunk of the world thanks to their navy, which was crewed by whip-scarred, toothless, unwilling sailors with untreated syphilis. That's who you want to fight your wars. No one fights like mistreated men living on a diet of garbage, the lash and below-decks rape.

### New v2

Way back in the 1700s and 1800s, the British secured vast territories through their formidable navy, which was manned by sailors who were whipped, toothless, and unwilling, suffering from untreated syphilis. These were the men you wanted to face in battle. No one fights like mistreated men, subsisting on meager rations of garbage, beaten by the lash, and subjected to rape below decks.

### New v3

Way back in the 1700s and 1800s, the British amassed a vast empire through their formidable navy, manned by sailors who were beaten, toothless, and unwilling, many suffering from untreated syphilis. These were the men you should face in battle. No one fights like these mistreated men, surviving on meager rations of garbage, whipped, and subjected to rape below decks.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:421951 | creators:421951 |
| condition | Normalized | Normalized |
| passed | True | True |
| validation_score | 0.8635053634643555 | 0.8938974738121033 |
| rejection_reasons |  |  |
| semantic_similarity | 0.8635053634643555 | 0.8938974738121033 |
| entailment_forward | 0.9351502060890198 | 0.944972813129425 |
| entailment_reverse | 0.9823945164680481 | 0.9748245477676392 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | [] | [] |
| rewrite_entities | [] | [] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.4516129032258065 | 0.5041322314049587 |
| original_words_replaced_pct | 39.34426229508197 | 45.90163934426229 |
| original_words_deleted_pct | 4.918032786885246 | 4.918032786885246 |
| inserted_words_per100_original | 11.475409836065573 | 9.836065573770492 |
| word_length_change_pct | 3.278688524590164 | -1.639344262295082 |
| mean_sentence_words_original | 20.333333333333332 | 20.333333333333332 |
| mean_sentence_words_rewrite | 21.0 | 20.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.0327868852459017 | 0.01639344262295076 |
| punctuation_l1_per100 | 7.780379911527453 | 8.415300546448089 |
| formality_proxy_delta | 1.639344262295082 | 1.639344262295082 |
| contraction_rate_delta | -1.639344262295082 | -1.639344262295082 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.48398540103558063 | 0.5672941156141772 |

## 08 — creators:422331

### Original

Classic Labor Day imagery shows men wearing hard hats and tough women in uniforms. These are Americans who did not build their muscles at a wellness club. By contrast, actual photos of the Democratic Socialists of America show seas of white faces belonging to college graduates. The only work most of them have done with their hands is typing. But the DSA is run by leaders who pretend otherwise, pushing forward candidates who play-act as tradespeople.

### New v2

Traditional Labor Day scenes depict men in hard hats alongside women in uniforms, embodying the hard work of the American workforce. In stark contrast, photographs from the Democratic Socialists of America reveal a sea of white faces belonging to college graduates. These individuals have primarily used their hands for typing. However, the leadership of DSA insists on portraying them as tradespeople, engaging in activities they have not actually performed.

### New v3

Traditional Labor Day scenes depict men in hard hats and women in tough uniforms. These are Americans who did not work out at a fitness center. In stark contrast, photographs of the Democratic Socialists of America reveal a sea of white faces belonging to college graduates. Most of them have only typed with their hands. However, the DSA is led by figures who pretend otherwise, pushing candidates who act as if they are tradespeople.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:422331 | creators:422331 |
| condition | Normalized | Normalized |
| passed | False | True |
| validation_score | 0.4449494779109955 | 0.95621657371521 |
| rejection_reasons | bidirectional_nli |  |
| semantic_similarity | 0.8796279430389404 | 0.95621657371521 |
| entailment_forward | 0.9871861338615417 | 0.9924837946891785 |
| entailment_reverse | 0.4449494779109955 | 0.981793999671936 |
| added_claim_risk | False | False |
| removed_claim_risk | True | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["dsa"] | ["dsa"] |
| rewrite_entities | ["dsa"] | ["dsa"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.6027397260273972 | 0.32450331125827814 |
| original_words_replaced_pct | 62.33766233766234 | 25.974025974025974 |
| original_words_deleted_pct | 0.0 | 7.792207792207792 |
| inserted_words_per100_original | 12.987012987012987 | 5.194805194805195 |
| word_length_change_pct | -10.38961038961039 | -3.896103896103896 |
| mean_sentence_words_original | 15.4 | 15.4 |
| mean_sentence_words_rewrite | 17.25 | 14.8 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 4 | 5 |
| sentence_mean_relative_change | 0.1201298701298701 | 0.03896103896103894 |
| punctuation_l1_per100 | 4.498400150574064 | 2.7553527553527557 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.5502946944789452 | 0.32412394332387257 |

## 09 — creators:120669

### Original

Last week, when "Fox & Friends" highlighted my most recent column, titled "Neutering Religious Holidays," liberals came out of the woodwork to try to defend President Barack Obama's record. So I decided to do a little research and see just how spiritual his past Thanksgiving addresses have been and compare them with the thoughts of our founding president, George Washington.

### New v2

Last week, when "Fox & Friends" featured my latest column, "Neutering Religious Holidays," liberals sprang into action to defend President Barack Obama's record. So I decided to conduct some research and examine how spiritually his past Thanksgiving addresses have been, and compare them with the sentiments of our founding father, George Washington.

### New v3

Last week, when "Fox & Friends" aired my latest column, "Neutering Religious Holidays," liberals rushed to defend President Barack Obama's record. So I decided to delve into the research and examine how spiritually President Washington's Thanksgiving addresses were, and how they compare to those of our founding father, George Washington.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:120669 | creators:120669 |
| condition | Normalized | Normalized |
| passed | True | False |
| validation_score | 0.9641770124435425 | 0.010270827449858189 |
| rejection_reasons |  | bidirectional_nli |
| semantic_similarity | 0.9796105623245239 | 0.9509595632553101 |
| entailment_forward | 0.9786596894264221 | 0.010270827449858189 |
| entailment_reverse | 0.9641770124435425 | 0.12253013998270035 |
| added_claim_risk | False | True |
| removed_claim_risk | False | True |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["barack obama", "fox friends", "george washington"] | ["barack obama", "fox friends", "george washington"] |
| rewrite_entities | ["barack obama", "fox friends", "george washington"] | ["barack obama", "fox friends", "george washington", "washington"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.2678571428571429 | 0.3873873873873874 |
| original_words_replaced_pct | 30.0 | 41.666666666666664 |
| original_words_deleted_pct | 1.6666666666666667 | 1.6666666666666667 |
| inserted_words_per100_original | 0.0 | 3.3333333333333335 |
| word_length_change_pct | -13.333333333333334 | -15.0 |
| mean_sentence_words_original | 30.0 | 30.0 |
| mean_sentence_words_rewrite | 26.0 | 25.5 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.13333333333333333 | 0.15 |
| punctuation_l1_per100 | 2.948717948717948 | 3.1372549019607847 |
| formality_proxy_delta | -0.2564102564102564 | -2.2549019607843137 |
| contraction_rate_delta | 0.2564102564102564 | 2.2549019607843137 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.18646793423368746 | 0.42530936858940993 |

## 10 — creators:216128

### Original

As the House and Senate work their way through the tax cut and reform effort, let me make one thing clear: Both plans are pro-growth, with the economic power coming from the business side. And where it comes from the personal side, there will be very little growth. That was always been the bet.

### New v2

As the legislative bodies deliberate on the tax cut and reform, let me clarify one point: Both plans are aimed at fostering growth, with the economic benefits stemming from the corporate sector. Conversely, any growth attributed to individuals will be minimal. That has always been the strategy.

### New v3

As the House and Senate navigate the tax cut and reform, let me be unequivocal: both plans aim to boost growth, with the economic benefit stemming from corporate sectors. Conversely, the personal side will yield minimal growth. That has always been the strategy.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:216128 | creators:216128 |
| condition | Normalized | Normalized |
| passed | False | True |
| validation_score | 0.0 | 0.9087741374969482 |
| rejection_reasons | entities |  |
| semantic_similarity | 0.8509975671768188 | 0.9087741374969482 |
| entailment_forward | 0.9716148972511292 | 0.9641848802566528 |
| entailment_reverse | 0.9322081208229065 | 0.977112889289856 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 0.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["house", "senate"] | ["house", "senate"] |
| rewrite_entities | [] | ["house", "senate"] |
| guard_entities | False | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.5098039215686274 | 0.4285714285714286 |
| original_words_replaced_pct | 52.72727272727273 | 45.45454545454545 |
| original_words_deleted_pct | 1.8181818181818181 | 3.6363636363636362 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -14.545454545454545 | -21.818181818181817 |
| mean_sentence_words_original | 18.333333333333332 | 18.333333333333332 |
| mean_sentence_words_rewrite | 15.666666666666666 | 14.333333333333334 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.14545454545454542 | 0.2181818181818181 |
| punctuation_l1_per100 | 3.056092843326886 | 3.8477801268498952 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.3904775208317226 | 0.3496880298518207 |

## 11 — creators:421279

### Original

You may wonder why President Donald Trump is doing everything he can, day by day, to destroy faith in democracy in little and large ways, on the job day and night. I have an answer that will presently be revealed.

### New v2

You might ponder why President Donald Trump is doing everything in his power, day in and day out, to undermine trust in democracy, both big and small. I have an explanation that will soon be made public.

### New v3

You might ponder why President Donald Trump is doing everything in his power, day in and day out, to undermine trust in democracy, both big and small. I have an explanation that will be made public shortly.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:421279 | creators:421279 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.1988021731376648 | 0.20718173682689667 |
| rejection_reasons | certainty\|bidirectional_nli | certainty\|bidirectional_nli |
| semantic_similarity | 0.8843997716903687 | 0.8748179078102112 |
| entailment_forward | 0.9952017068862915 | 0.993523359298706 |
| entailment_reverse | 0.1988021731376648 | 0.20718173682689667 |
| added_claim_risk | False | False |
| removed_claim_risk | True | True |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["donald trump"] | ["donald trump"] |
| rewrite_entities | ["donald trump"] | ["donald trump"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | False | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.48051948051948057 | 0.48051948051948057 |
| original_words_replaced_pct | 50.0 | 47.5 |
| original_words_deleted_pct | 0.0 | 2.5 |
| inserted_words_per100_original | 2.5 | 2.5 |
| word_length_change_pct | -7.5 | -7.5 |
| mean_sentence_words_original | 20.0 | 20.0 |
| mean_sentence_words_rewrite | 18.5 | 18.5 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.075 | 0.075 |
| punctuation_l1_per100 | 0.6081081081081088 | 0.6081081081081088 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | intermediate |
| explicit_style_mean_abs_standardized_change | 0.19342450280592033 | 0.19568864929490878 |

## 12 — creators:419062

### Original

From Q-Anon nuttiness to JD Vance's "Deep State" quackery, wacko right-wing conspiracies have oozed into the center of Republican politics. But don't let their goofiness obscure the fact that there is indeed a very real plot to rig America's economic and political system, causing wealth and power to flow uphill — from the workaday majority to moneyed elites.

### New v2

From Q-Anon's far-out theories to JD Vance's "Deep State" nonsense, fringe right-wing conspiracies have crept into the heart of Republican politics. But don't let their absurdity distract from the reality that there is a serious plot to manipulate America's economic and political landscape, funneling wealth and power upwards — from the everyday majority to the moneyed elite.

### New v3

From Q-Anon's nuttiness to JD Vance's "Deep State" quackery, fringe right-wing conspiracies have crept into the heart of Republican politics. But don't let their absurdity overshadow the stark reality that there is indeed a serious plot to manipulate America's economic and political landscape, funneling wealth and power upwards — from the everyday majority to the moneyed elite.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:419062 | creators:419062 |
| condition | Normalized | Normalized |
| passed | True | True |
| validation_score | 0.9547183513641357 | 0.9618977308273315 |
| rejection_reasons |  |  |
| semantic_similarity | 0.9547183513641357 | 0.9618977308273315 |
| entailment_forward | 0.9926890730857849 | 0.9948006868362427 |
| entailment_reverse | 0.9860575795173645 | 0.9899430274963379 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["america", "d vance", "j"] | ["america", "d vance", "j"] |
| rewrite_entities | ["america", "d vance", "j", "q anon"] | ["america", "anon", "d vance", "j", "q"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.31200000000000006 | 0.25806451612903225 |
| original_words_replaced_pct | 29.032258064516128 | 25.806451612903224 |
| original_words_deleted_pct | 1.6129032258064515 | 0.0 |
| inserted_words_per100_original | 1.6129032258064515 | 3.225806451612903 |
| word_length_change_pct | 1.6129032258064515 | 0.0 |
| mean_sentence_words_original | 31.0 | 31.0 |
| mean_sentence_words_rewrite | 31.5 | 31.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.016129032258064516 | 0.0 |
| punctuation_l1_per100 | 1.6129032258064517 | 0.0 |
| formality_proxy_delta | -1.5104966717869939 | -1.612903225806451 |
| contraction_rate_delta | 1.5104966717869939 | 1.612903225806451 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.08204619397579813 | 0.04925057155291083 |

## 13 — creators:295188

### Original

Many of us are feeling a lot of excitement, buttressed by wave after wave of relief. We are a nation of survivors. On Inauguration Day, I felt hopeful watching Joe Biden and Kamala Harris take their oaths of office. They appeared to understand what we were asking of them and accepted without reservation.

### New v2

Many of us have felt a surge of excitement, bolstered by successive waves of relief. As a nation of survivors, we watched with hope as Joe Biden and Kamala Harris took their oaths of office on Inauguration Day. Their acceptance appeared genuine and without any reluctance.

### New v3

Many of us have felt an overwhelming surge of joy, bolstered by successive waves of relief. We are a people of survivors. On Inauguration Day, I felt a glimmer of hope as I watched Joe Biden and Kamala Harris take their oaths. They seemed to grasp what we were expecting of them and accepted without any hesitation.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:295188 | creators:295188 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.15237948298454285 | 0.2158372402191162 |
| rejection_reasons | bidirectional_nli | bidirectional_nli |
| semantic_similarity | 0.9105724096298218 | 0.9224379062652588 |
| entailment_forward | 0.9788658022880554 | 0.2158372402191162 |
| entailment_reverse | 0.15237948298454285 | 0.9885397553443909 |
| added_claim_risk | False | True |
| removed_claim_risk | True | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["a harris", "joe biden", "kamal"] | ["a harris", "joe biden", "kamal"] |
| rewrite_entities | ["a harris", "joe biden", "kamal"] | ["a harris", "joe biden", "kamal"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.4949494949494949 | 0.36363636363636365 |
| original_words_replaced_pct | 50.943396226415096 | 30.18867924528302 |
| original_words_deleted_pct | 1.8867924528301887 | 3.7735849056603774 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -13.20754716981132 | 7.547169811320755 |
| mean_sentence_words_original | 13.25 | 13.25 |
| mean_sentence_words_rewrite | 15.333333333333334 | 14.25 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 3 | 4 |
| sentence_mean_relative_change | 0.15723270440251577 | 0.07547169811320754 |
| punctuation_l1_per100 | 0.5742411812961441 | 0.2648129758358162 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | False |
| style_change_group | substantial | intermediate |
| explicit_style_mean_abs_standardized_change | 0.4606119005712889 | 0.2142415558329778 |

## 14 — creators:423315

### Original

I was working at a medium-sized city newspaper on Sept. 11, 2001. No one had stormed the Capitol yet, there had been no George Floyd riots, we hadn't started the war we were going to lose in Afghanistan, and ICE hadn't killed anyone in the street.

### New v2

I was employed at a mid-sized city newspaper on September 11, 2001. No one had yet stormed the Capitol, there were no George Floyd protests, we hadn't initiated the war we were destined to lose in Afghanistan, and ICE had not yet killed anyone on the streets.

### New v3

I was employed at a mid-sized city newspaper on September 11, 2001. No one had stormed the Capitol building yet, there hadn't been George Floyd protests, we hadn't initiated the war we were destined to lose in Afghanistan, and ICE hadn't killed anyone on the streets.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:423315 | creators:423315 |
| condition | Normalized | Normalized |
| passed | True | True |
| validation_score | 0.9473156332969666 | 0.9322510957717896 |
| rejection_reasons |  |  |
| semantic_similarity | 0.9563169479370117 | 0.9663867950439453 |
| entailment_forward | 0.9888874888420105 | 0.9807587265968323 |
| entailment_reverse | 0.9473156332969666 | 0.9322510957717896 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["afghanistan", "capitol", "george floyd", "ice"] | ["afghanistan", "capitol", "george floyd", "ice"] |
| rewrite_entities | ["afghanistan", "capitol", "george floyd", "ice"] | ["afghanistan", "capitol", "george floyd", "ice"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.26530612244897955 | 0.21212121212121215 |
| original_words_replaced_pct | 24.489795918367346 | 18.367346938775512 |
| original_words_deleted_pct | 2.0408163265306123 | 2.0408163265306123 |
| inserted_words_per100_original | 2.0408163265306123 | 2.0408163265306123 |
| word_length_change_pct | 0.0 | 2.0408163265306123 |
| mean_sentence_words_original | 16.333333333333332 | 16.333333333333332 |
| mean_sentence_words_rewrite | 24.5 | 25.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.5000000000000001 | 0.5306122448979593 |
| punctuation_l1_per100 | 0.0 | 0.20408163265306145 |
| formality_proxy_delta | 2.0408163265306123 | -1.9183673469387754 |
| contraction_rate_delta | -2.0408163265306123 | 1.9183673469387754 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.21502987020692402 | 0.11598467997229193 |

## 15 — creators:422146

### Original

Oh good, another war. This time a trade war with Canada and for no other reason than ... what? To give Donald Trump a new stage for big-league bullying? To divert attention from the Jeffrey Epstein files? Who knows. Whatever. Trying to humiliate our closest ally does not serve American interests, ya think?

### New v2

Oh, good, another war. This time a trade spat with Canada, ostensibly for reasons that are unclear—perhaps to provide Donald Trump with a platform for his more aggressive behavior? To shift focus from the Jeffrey Epstein scandal? Who knows. Whatever. Targeting our closest ally doesn’t serve American interests, do you think?

### New v3

Oh, good, another trade war. This time it's with Canada, and the reason? Perhaps to give Donald Trump a new platform for his big-league bullying? To shift focus from the Jeffrey Epstein files? Who knows. Whatever. Humiliating our closest ally doesn't serve American interests, does it?

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:422146 | creators:422146 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.5310763716697693 | 0.9197419285774231 |
| rejection_reasons | negation\|bidirectional_nli | negation |
| semantic_similarity | 0.9545409083366394 | 0.9197419285774231 |
| entailment_forward | 0.9848292469978333 | 0.9894576668739319 |
| entailment_reverse | 0.5310763716697693 | 0.9343767166137695 |
| added_claim_risk | False | False |
| removed_claim_risk | True | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["canada", "donald trump", "jeffrey epstein"] | ["canada", "donald trump", "jeffrey epstein"] |
| rewrite_entities | ["canada", "donald trump", "jeffrey epstein"] | ["canada", "donald trump", "jeffrey epstein"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | False | False |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.41509433962264153 | 0.3137254901960784 |
| original_words_replaced_pct | 41.509433962264154 | 33.9622641509434 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 1.8867924528301887 | 3.7735849056603774 |
| word_length_change_pct | 0.0 | -7.547169811320755 |
| mean_sentence_words_original | 6.625 | 6.625 |
| mean_sentence_words_rewrite | 8.833333333333334 | 7.0 |
| sentence_count_original | 8 | 8 |
| sentence_count_rewrite | 6 | 7 |
| sentence_mean_relative_change | 0.3333333333333334 | 0.05660377358490566 |
| punctuation_l1_per100 | 9.433962264150944 | 5.15979976896419 |
| formality_proxy_delta | -1.8867924528301887 | -4.081632653061225 |
| contraction_rate_delta | 1.8867924528301887 | 4.081632653061225 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.5182270668469666 | 0.29994505382111325 |

## 16 — creators:421853

### Original

There's an old saying: Those who can, do; those who can't, teach. A similar idea underscores the debate over wealth taxes in California and elsewhere: Those who can, build companies. Those who can't, devise ways for the government to take shares in what others have built.

### New v2

A well-known adage goes: Those who have the ability to succeed, do; those who lack that capability, teach. This sentiment also resonates in the ongoing discussions about wealth taxes in California and other regions: Those who have the means to start companies, do so. Those who don't, come up with strategies for the government to seize a portion of what others have achieved.

### New v3

A well-worn adage goes: Those who have the skills and resources do; those who lack them teach. This sentiment echoes in the discourse about wealth taxes in California and beyond: Those who have the means to build companies do; those who can't, come up with schemes for the government to seize a portion of what others have constructed.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:421853 | creators:421853 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.9287477731704712 | 0.9431890249252319 |
| rejection_reasons | negation | negation |
| semantic_similarity | 0.9287477731704712 | 0.9431890249252319 |
| entailment_forward | 0.9525521993637085 | 0.972088634967804 |
| entailment_reverse | 0.9933344125747681 | 0.9955326318740845 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["california"] | ["california"] |
| rewrite_entities | ["california"] | ["california"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | False | False |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.5614035087719298 | 0.7431192660550459 |
| original_words_replaced_pct | 48.97959183673469 | 71.42857142857143 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 4.081632653061225 | 0.0 |
| word_length_change_pct | 32.6530612244898 | 22.448979591836736 |
| mean_sentence_words_original | 16.333333333333332 | 16.333333333333332 |
| mean_sentence_words_rewrite | 21.666666666666668 | 30.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 2 |
| sentence_mean_relative_change | 0.32653061224489816 | 0.8367346938775512 |
| punctuation_l1_per100 | 5.054945054945055 | 10.204081632653061 |
| formality_proxy_delta | 4.583987441130298 | 4.4557823129251695 |
| contraction_rate_delta | -4.583987441130298 | -4.4557823129251695 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.5619326487142567 | 0.5037558090573118 |

## 17 — creators:418620

### Original

The next mayor of Washington, D.C. is likely to be a Marxist. In Los Angeles, the Mensheviks and Bolsheviks are battling it out for control. New York City has already fallen to a champion of Third Worldism.

### New v2

It seems probable that the next mayor of Washington, D.C. will be a Marxist. In Los Angeles, the Mensheviks and Bolsheviks are engaged in a struggle for dominance. New York City has already been taken over by a proponent of Third Worldism.

### New v3

The impending mayor of Washington, D.C. may well be a Marxist. In Los Angeles, the Mensheviks and Bolsheviks are locked in a struggle for dominance. New York City has already succumbed to the sway of a Third Worldist champion.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:418620 | creators:418620 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.9820675253868103 | 0.9607425332069397 |
| rejection_reasons | future_tense | certainty |
| semantic_similarity | 0.9820675253868103 | 0.9607425332069397 |
| entailment_forward | 0.9950950145721436 | 0.9929798245429993 |
| entailment_reverse | 0.9912118315696716 | 0.979414165019989 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["los angeles", "new york city", "washington d c"] | ["los angeles", "new york city", "washington d c"] |
| rewrite_entities | ["los angeles", "new york city", "washington d c"] | ["los angeles", "new york city", "washington d c"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | False | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.308641975308642 | 0.33333333333333337 |
| original_words_replaced_pct | 26.31578947368421 | 23.68421052631579 |
| original_words_deleted_pct | 0.0 | 7.894736842105263 |
| inserted_words_per100_original | 10.526315789473685 | 13.157894736842104 |
| word_length_change_pct | 13.157894736842104 | 5.2631578947368425 |
| mean_sentence_words_original | 7.6 | 7.6 |
| mean_sentence_words_rewrite | 8.6 | 8.0 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.13157894736842105 | 0.052631578947368474 |
| punctuation_l1_per100 | 0.6119951040391678 | 0.2631578947368425 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | intermediate |
| explicit_style_mean_abs_standardized_change | 0.2853150199012075 | 0.17737499656174752 |

## 18 — creators:114783

### Original

We said on 9/11 that we'd "never forget." But when our president has a no-strategy strategy for stopping Islamic extremists, isn't Washington sidestepping our commitment of remembrance, in addition to its duty to protect our land and liberties?

### New v2

We declared on September 11 that we would never forget the horrors of that day. Yet, when our president opts for a strategy that lacks any clear plan to combat Islamic extremists, doesn't Washington seem to be avoiding its pledge of remembrance, as well as its obligation to safeguard our nation and freedoms?

### New v3

We declared on 9/11 that we would never forget the horrors of that day. But when our president opts for a no-strategy approach to combatting Islamic extremists, isn't Washington failing to honor its pledge of remembrance, alongside its obligation to safeguard our nation and freedoms?

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:114783 | creators:114783 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.9447147846221924 | 0.9357248544692993 |
| rejection_reasons | numbers\|negation\|attribution\|quotations | attribution\|quotations |
| semantic_similarity | 0.9447147846221924 | 0.9357248544692993 |
| entailment_forward | 0.9907621741294861 | 0.9886825084686279 |
| entailment_reverse | 0.986943244934082 | 0.98414546251297 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["washington"] | ["washington"] |
| rewrite_entities | ["washington"] | ["washington"] |
| guard_entities | True | True |
| guard_numbers | False | True |
| guard_negation | False | True |
| guard_certainty | True | True |
| guard_attribution | False | False |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | False | False |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.5625 | 0.4444444444444444 |
| original_words_replaced_pct | 47.61904761904762 | 40.476190476190474 |
| original_words_deleted_pct | 2.380952380952381 | 0.0 |
| inserted_words_per100_original | 0.0 | 11.904761904761905 |
| word_length_change_pct | 28.571428571428573 | 14.285714285714286 |
| mean_sentence_words_original | 21.0 | 21.0 |
| mean_sentence_words_rewrite | 27.0 | 24.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.2857142857142857 | 0.14285714285714285 |
| punctuation_l1_per100 | 3.7037037037037033 | 1.1904761904761898 |
| formality_proxy_delta | 2.91005291005291 | 2.6785714285714284 |
| contraction_rate_delta | -2.91005291005291 | -2.6785714285714284 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.4797516604679875 | 0.2905157965819611 |

## 19 — creators:224770

### Original

Last week, Donald Trump dialed back his earlier call for a punitive and blanket tariff on imported steel and aluminum. Good decision. The financial markets rallied, as the new plan specifically targets countries that are cheating and stealing, such as China and Russia, and provides exemptions for allies.

### New v2

Just recently, Donald Trump moderated his previous stance advocating for a harsh and all-encompassing tariff on steel and aluminum imports. A wise move. The stock markets responded positively, as the revised proposal focuses on those nations that are engaging in deceptive and exploitative practices, notably China and Russia, while offering exemptions to close allies.

### New v3

Last week, Donald Trump scaled back his initial proposal for a harsh and all-encompassing tariff on steel and aluminum imports. A wise move. The stock markets responded positively, as the revised plan singles out nations that are cheating and stealing, notably China and Russia, while offering exemptions to close allies.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:224770 | creators:224770 |
| condition | Normalized | Normalized |
| passed | True | True |
| validation_score | 0.6815944910049438 | 0.9609174728393555 |
| rejection_reasons |  |  |
| semantic_similarity | 0.9498361945152283 | 0.9630264043807983 |
| entailment_forward | 0.9748687148094177 | 0.9609174728393555 |
| entailment_reverse | 0.6815944910049438 | 0.9967079162597656 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["china", "donald trump", "russia"] | ["china", "donald trump", "russia"] |
| rewrite_entities | ["china", "donald trump", "russia"] | ["china", "donald trump", "russia"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.5533980582524272 | 0.41414141414141414 |
| original_words_replaced_pct | 50.0 | 37.5 |
| original_words_deleted_pct | 2.0833333333333335 | 2.0833333333333335 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 14.583333333333334 | 6.25 |
| mean_sentence_words_original | 16.0 | 16.0 |
| mean_sentence_words_rewrite | 18.333333333333332 | 17.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.14583333333333326 | 0.0625 |
| punctuation_l1_per100 | 2.87878787878788 | 2.450980392156864 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.35051551132336084 | 0.24760282593828845 |

## 20 — creators:8b0d99b23d03

### Original

"The rich are different from you and me." — F. Scott Fitzgerald I read two books in one weekend: "Just Mercy" by Bryan Stevenson on Saturday, "Strangers" by Belle Burden on Sunday. They're true stories, told well, about two countries, both inside America's borders: Death Row in Alabama, Martha's Vineyard in Massachusetts.

### New v2

"The rich are distinct from the rest of us." — F. Scott Fitzgerald I recently read two books in a single weekend: "Just Mercy" by Bryan Stevenson on Saturday, and "Strangers" by Belle Burden on Sunday. Both are compelling true stories, narrated well, about two distinct regions within America's borders: Death Row in Alabama and Martha's Vineyard in Massachusetts.

### New v3

"The rich are distinct from the rest of us." — F. Scott Fitzgerald I recently read two books in a single weekend: "Just Mercy" by Bryan Stevenson and "Strangers" by Belle Burden. Both are compelling true stories, each detailing the experiences of two distinct nations, albeit within America's borders. "Just Mercy" focuses on Death Row in Alabama, while "Strangers" explores Martha's Vineyard in Massachusetts.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:8b0d99b23d03 | creators:8b0d99b23d03 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.003732154844328761 | 0.5175889134407043 |
| rejection_reasons | quotations\|bidirectional_nli | quotations\|bidirectional_nli |
| semantic_similarity | 0.9179810285568237 | 0.9295227527618408 |
| entailment_forward | 0.8865281939506531 | 0.935153067111969 |
| entailment_reverse | 0.003732154844328761 | 0.5175889134407043 |
| added_claim_risk | False | False |
| removed_claim_risk | True | True |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["alabama", "america", "belle burden", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] | ["alabama", "america", "belle burden", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "row", "scott fitzgerald"] |
| rewrite_entities | ["alabama", "america", "belle bur", "bryan stevenson", "f", "martha s vineyard", "massachusetts", "scott fitzgerald"] | ["alabama", "america", "belle bur", "bryan stevenson", "death row", "f", "martha s vineyard", "massachusetts", "scott fitzgerald"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | False | False |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.24561403508771928 | 0.37815126050420167 |
| original_words_replaced_pct | 20.37037037037037 | 31.48148148148148 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 5.555555555555555 | 14.814814814814815 |
| word_length_change_pct | 11.11111111111111 | 20.37037037037037 |
| mean_sentence_words_original | 13.5 | 13.5 |
| mean_sentence_words_rewrite | 15.0 | 13.0 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 4 | 5 |
| sentence_mean_relative_change | 0.1111111111111111 | 0.037037037037037035 |
| punctuation_l1_per100 | 4.814814814814815 | 7.122507122507123 |
| formality_proxy_delta | 2.222222222222222 | 2.4786324786324783 |
| contraction_rate_delta | -2.222222222222222 | -2.4786324786324783 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.2939894725084025 | 0.5054554614996639 |

## 21 — creators:97c9d6b9ac1b

### Original

WASHINGTON — Something told me to get me over to East Potomac Park before Donald Trump destroyed it. Sure enough, I did, on a rainy Sunday morning, for a rally to protect the waterfront parkland from his axe. On the next weekend, he cut down 430 trees — for a fancy golf course, of course. He sneakily started on a Saturday morning on the three-day holiday weekend.

### New v2

WASHINGTON — Something prompted me to visit East Potomac Park before Donald Trump could dismantle it. Indeed, I did so on a dreary Sunday morning, to rally against the erosion of waterfront parkland by his bulldozers. The following weekend, he felled 430 trees — for a golf course, of course. He began on a Saturday morning during the three-day holiday weekend, covertly.

### New v3

WASHINGTON — Something nudged me to head to East Potomac Park before Donald Trump could do it. Sure enough, I made it there on a dreary Sunday, to protest the destruction of the waterfront parkland. The next weekend, he chopped down 430 trees — for a golf course, of course. He began on a Saturday morning, during the three-day holiday weekend.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:97c9d6b9ac1b | creators:97c9d6b9ac1b |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.007799229584634304 | 0.016585243865847588 |
| rejection_reasons | certainty\|bidirectional_nli | certainty\|bidirectional_nli |
| semantic_similarity | 0.9524300694465637 | 0.9835411310195923 |
| entailment_forward | 0.007799229584634304 | 0.9507778882980347 |
| entailment_reverse | 0.02999739721417427 | 0.016585243865847588 |
| added_claim_risk | True | False |
| removed_claim_risk | True | True |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["donald trump", "east potomac park", "washington"] | ["donald trump", "east potomac park", "washington"] |
| rewrite_entities | ["donald trump", "east potomac park"] | ["donald trump", "east potomac park"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | False | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.3228346456692913 | 0.2857142857142857 |
| original_words_replaced_pct | 33.333333333333336 | 18.181818181818183 |
| original_words_deleted_pct | 1.5151515151515151 | 13.636363636363637 |
| inserted_words_per100_original | 6.0606060606060606 | 0.0 |
| word_length_change_pct | -7.575757575757576 | -9.090909090909092 |
| mean_sentence_words_original | 16.5 | 16.5 |
| mean_sentence_words_rewrite | 15.25 | 15.0 |
| sentence_count_original | 4 | 4 |
| sentence_count_rewrite | 4 | 4 |
| sentence_mean_relative_change | 0.07575757575757576 | 0.09090909090909091 |
| punctuation_l1_per100 | 0.9935419771485337 | 1.2121212121212126 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | True |
| style_change_group | intermediate | substantial |
| explicit_style_mean_abs_standardized_change | 0.233235188488008 | 0.24485756341798873 |

## 22 — creators:423545

### Original

Greg Abbott, the right-wing hack who is governor of Texas, probably doesn't know what a "petard" is, but he's now been hoisted by a big one. "Hoist on a petard" is a Shakespearean phrase for a bomb maker being blown sky-high by his own creation.

### New v2

Greg Abbott, the right-wing figure who serves as Texas's governor, may not be familiar with the term "petard," but he's now caught in a significant predicament. "Hoist on a petard" is a phrase from Shakespeare, indicating a creator being destroyed by the very thing they've devised.

### New v3

Greg Abbott, the right-wing hack who governs Texas, might not recognize the term "petard," but he's now found himself in a bit of a bind. "Hoist on a petard" is a Shakespearean expression meaning someone is being destroyed by the very thing they created.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:423545 | creators:423545 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.022370370104908943 | 0.008270232938230038 |
| rejection_reasons | certainty\|quotations\|bidirectional_nli | certainty\|quotations\|bidirectional_nli |
| semantic_similarity | 0.9261665344238281 | 0.9026480913162231 |
| entailment_forward | 0.9830102920532227 | 0.691616952419281 |
| entailment_reverse | 0.022370370104908943 | 0.008270232938230038 |
| added_claim_risk | False | False |
| removed_claim_risk | True | True |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["greg abbott", "texas"] | ["greg abbott", "texas"] |
| rewrite_entities | ["greg abbott", "texas"] | ["greg abbott", "texas"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | False | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | False | False |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.5353535353535354 | 0.5157894736842106 |
| original_words_replaced_pct | 48.97959183673469 | 51.02040816326531 |
| original_words_deleted_pct | 4.081632653061225 | 2.0408163265306123 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 2.0408163265306123 | -6.122448979591836 |
| mean_sentence_words_original | 24.5 | 24.5 |
| mean_sentence_words_rewrite | 25.0 | 23.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.02040816326530612 | 0.061224489795918366 |
| punctuation_l1_per100 | 3.959183673469388 | 2.3070097604259097 |
| formality_proxy_delta | -1.9183673469387754 | 1.9077196095829638 |
| contraction_rate_delta | 1.9183673469387754 | -1.9077196095829638 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.45979088066336055 | 0.2549354187853899 |

## 23 — creators:298495

### Original

After I first started writing a column, in the fall of 2002, it wasn't long before I heard regularly from those who brandished God as a weapon in opposing LGBTQ rights. This was not surprising. Back then, I was on staff at The Plain Dealer in Cleveland, and I was long familiar with the bigotry in my home state. Most of the hate mail came from strangers, but I got my share of lectures from blood relatives, too. Few things anger right-wing Christians more than a family member insisting she's acquainted with a different version of God.

### New v2

After I began writing a column in the fall of 2002, it wasn't long before I received regular correspondence from individuals who used God as a tool to oppose LGBTQ rights. This was unsurprising. At the time, I was employed at The Plain Dealer in Cleveland, and I was already well-acquainted with the bigotry in my home state. Most of the hate mail came from anonymous sources, but I also received lectures from family members. Few things infuriate right-wing Christians more than a family member who claims to know a different version of God.

### New v3

After I began writing a column in the fall of 2002, it wasn't long before I received regular correspondence from individuals who used God as a tool to oppose LGBTQ rights. This was unsurprising. At the time, I was employed at The Plain Dealer in Cleveland, and I was well-acquainted with the bigotry in my home state. Most of the hate mail came from anonymous sources, but I also received lectures from family members. Few things infuriate right-wing Christians more than a relative who claims to know a different God.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:298495 | creators:298495 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.9203753471374512 | 0.9225066900253296 |
| rejection_reasons | negation\|attribution | negation\|attribution |
| semantic_similarity | 0.9203753471374512 | 0.9225066900253296 |
| entailment_forward | 0.9902580976486206 | 0.9908578991889954 |
| entailment_reverse | 0.9591318964958191 | 0.9523329734802246 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["cleveland", "god", "the plain dealer"] | ["cleveland", "god", "the plain dealer"] |
| rewrite_entities | ["cleveland", "god", "the plain dealer"] | ["cleveland", "god", "the plain dealer"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | False | False |
| guard_certainty | True | True |
| guard_attribution | False | False |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.29949238578680204 | 0.3264248704663213 |
| original_words_replaced_pct | 31.0 | 33.0 |
| original_words_deleted_pct | 0.0 | 2.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -3.0 | -7.0 |
| mean_sentence_words_original | 20.0 | 20.0 |
| mean_sentence_words_rewrite | 19.4 | 18.6 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.030000000000000072 | 0.06999999999999992 |
| punctuation_l1_per100 | 2.9381443298969074 | 2.849462365591398 |
| formality_proxy_delta | 0.9690721649484537 | 0.924731182795699 |
| contraction_rate_delta | -0.9690721649484537 | -0.924731182795699 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.2793689666736837 | 0.3065303118450737 |

## 24 — creators:418904

### Original

"We didn't celebrate the Fourth of July," he told me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, fell to Union troops on July 4, 1863. The Confederates surrendered, as was their habit. Long memories still mourn the Lost Cause of Black backs whipped bloody.

### New v2

"We didn't mark the Fourth of July," he informed me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, capitulated to Union forces on July 4, 1863. The Confederates surrendered, as they often did. Deep-seated memories still mourn the Lost Cause of black backs who were beaten with cruel whips.

### New v3

"We didn't mark the Fourth of July," he informed me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, capitulated to Union forces on July 4, 1863. The Confederates typically surrendered on this day. Deeply felt memories still grieve the Lost Cause of those who were once whipped and branded.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:418904 | creators:418904 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.11667945235967636 | 0.1778912991285324 |
| rejection_reasons | quotations\|bidirectional_nli | quotations\|bidirectional_nli |
| semantic_similarity | 0.9624490141868591 | 0.9514915943145752 |
| entailment_forward | 0.11667945235967636 | 0.5282347202301025 |
| entailment_reverse | 0.31395915150642395 | 0.1778912991285324 |
| added_claim_risk | True | True |
| removed_claim_risk | True | True |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["mississippi", "vicksburg"] | ["mississippi", "vicksburg"] |
| rewrite_entities | ["mississippi", "vicksburg"] | ["mississippi", "vicksburg"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | False | False |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.24752475247524752 | 0.30000000000000004 |
| original_words_replaced_pct | 20.833333333333332 | 27.083333333333332 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 2.0833333333333335 |
| word_length_change_pct | 10.416666666666666 | 8.333333333333334 |
| mean_sentence_words_original | 9.6 | 9.6 |
| mean_sentence_words_rewrite | 10.6 | 10.4 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.10416666666666667 | 0.08333333333333341 |
| punctuation_l1_per100 | 3.0660377358490574 | 2.884615384615385 |
| formality_proxy_delta | 0.19654088050314478 | 0.16025641025641035 |
| contraction_rate_delta | -0.19654088050314478 | -0.16025641025641035 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.27175010793884435 | 0.35250878628967586 |

## 25 — creators:2e34435c6ccf

### Original

About three weeks before Republicans expect an electoral beating, Donald Trump had to get rid of Kimberly Guilfoyle, his ambassador to Greece. He simply had to. Trump's money-grabbing corruption was wearing thin even on devoted fans, but the president knew how to wrap his mob-like patter in foggy euphemisms and double meanings.

### New v2

Just three weeks before Republicans were expected to suffer a significant electoral setback, Donald Trump found himself in the unenviable position of having to remove Kimberly Guilfoyle, his ambassador to Greece. It was an inevitability he could not avoid. Trump's penchant for money-grubbing corruption had begun to grate even on his most loyal supporters. However, the president was adept at cloaking his mob-like rhetoric in a haze of ambiguous and evasive language.

### New v3

Just three weeks before Republicans were set to suffer an electoral defeat, Donald Trump found himself in the awkward position of having to oust Kimberly Guilfoyle, his ambassador to Greece. It was an inevitability. Trump's penchant for money-grubbing corruption had begun to grate even on his most loyal supporters, but the president knew how to cloak his mob-like rhetoric in a haze of ambiguous doublespeak.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:2e34435c6ccf | creators:2e34435c6ccf |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.8251128792762756 | 0.8197739124298096 |
| rejection_reasons | negation\|certainty\|similarity | similarity |
| semantic_similarity | 0.8251128792762756 | 0.8197739124298096 |
| entailment_forward | 0.9799659848213196 | 0.9655657410621643 |
| entailment_reverse | 0.9860442876815796 | 0.9911802411079407 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["donald trump", "greece", "kimberly guilfoyle", "trump"] | ["donald trump", "greece", "kimberly guilfoyle", "trump"] |
| rewrite_entities | ["donald trump", "greece", "kimberly guilfoyle", "trump"] | ["donald trump", "greece", "kimberly guilfoyle", "trump"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | False | True |
| guard_certainty | False | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | False | False |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.5692307692307692 | 0.49593495934959353 |
| original_words_replaced_pct | 49.09090909090909 | 43.63636363636363 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 10.909090909090908 | 3.6363636363636362 |
| word_length_change_pct | 36.36363636363637 | 23.636363636363637 |
| mean_sentence_words_original | 18.333333333333332 | 18.333333333333332 |
| mean_sentence_words_rewrite | 18.75 | 22.666666666666668 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 4 | 3 |
| sentence_mean_relative_change | 0.022727272727272794 | 0.2363636363636365 |
| punctuation_l1_per100 | 2.424242424242424 | 1.7379679144385016 |
| formality_proxy_delta | 0.48484848484848486 | 0.34759358288770037 |
| contraction_rate_delta | -0.48484848484848486 | -0.34759358288770037 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.42451244614437145 | 0.25351142508863167 |

## 26 — creators:459e183c1d0d

### Original

French economist Gabriel Zucman has come to California bearing a familiar French solution to a fiscal problem: another tax. Once based at the University of California, Berkeley, Zucman is back and campaigning for Proposition 40, which would impose an allegedly one-time 5% tax on the net worth of Californians worth more than $1 billion. Zucman, who coauthored the proposition, estimates that the tax could raise about $100 billion and claims that 90% of the proceeds would go to health care.

### New v2

French economist Gabriel Zucman has returned to California with a proposal that echoes a familiar French approach to fiscal challenges: a new tax. Zucman, who was previously based at the University of California, Berkeley, is now advocating for Proposition 40, which would impose a purported one-time 5% tax on the net worth of Californians with more than $1 billion in assets. Zucman, who coauthored the proposition, estimates that the tax could generate approximately $100 billion and claims that 90% of the revenue would be allocated to healthcare.

### New v3

French economist Gabriel Zucman has returned to California with a familiar French proposal for addressing fiscal challenges: a new tax. Previously based at the University of California, Berkeley, Zucman is now advocating for Proposition 40, which would introduce a purportedly one-time 5% tax on Californians with net worth exceeding $1 billion. Zucman, who coauthored the proposition, estimates that this tax could generate approximately $100 billion. He claims that 90% of the collected funds would be allocated to healthcare.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:459e183c1d0d | creators:459e183c1d0d |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.98289555311203 | 0.9817113876342773 |
| rejection_reasons | certainty | certainty |
| semantic_similarity | 0.98289555311203 | 0.9817113876342773 |
| entailment_forward | 0.9843782782554626 | 0.9880080223083496 |
| entailment_reverse | 0.9864643812179565 | 0.9872525334358215 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["berkeley", "california", "gabriel zucman", "university of california", "zuc", "zucman"] | ["berkeley", "california", "gabriel zucman", "university of california", "zuc", "zucman"] |
| rewrite_entities | ["california", "gabriel zucman", "university of california", "zucman"] | ["berkeley", "california", "gabriel zucman", "university of california", "zucman"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | False | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.2781065088757396 | 0.3375 |
| original_words_replaced_pct | 23.45679012345679 | 34.5679012345679 |
| original_words_deleted_pct | 1.2345679012345678 | 0.0 |
| inserted_words_per100_original | 4.938271604938271 | 0.0 |
| word_length_change_pct | 8.641975308641975 | -2.4691358024691357 |
| mean_sentence_words_original | 27.0 | 27.0 |
| mean_sentence_words_rewrite | 29.333333333333332 | 19.75 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 4 |
| sentence_mean_relative_change | 0.0864197530864197 | 0.26851851851851855 |
| punctuation_l1_per100 | 0.8417508417508417 | 0.21878418502891117 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | False | True |
| style_change_group | intermediate | substantial |
| explicit_style_mean_abs_standardized_change | 0.20795711369620618 | 0.2659541256471809 |

## 27 — creators:416436

### Original

Socialism will always find an audience because it appeals to base envy and resentment. Ginning up a mob to be mad at "oligarchs," "Wall Street barons," "kulaks" or "billionaires" is cheap and easy. So, it was refreshing to hear Amazon founder Jeff Bezos, the fourth richest man on the planet, offer unadulterated praise of the moral and economic superiority of capitalism in his recent interview with CNBC's Andrew Ross Sorkin.

### New v2

Socialism will always have its supporters, as it taps into deep-seated feelings of envy and resentment. Stirring up a mob to be angry at "oligarchs," "Wall Street barons," "kulaks," or "billionaires" is a simple and effective tactic. Hence, it was noteworthy to hear Amazon's founder, Jeff Bezos, the fourth wealthiest individual, extol the virtues of capitalism in his recent interview with CNBC's Andrew Ross Sorkin.

### New v3

Socialism will always have its adherents, as it taps into deep-seated feelings of envy and resentment. Stirring up a mob to vent anger at "oligarchs," "Wall Street barons," "kulaks," or "billionaires" is a simple and effective tactic. Hence, it was noteworthy to hear Amazon's Jeff Bezos, the fourth wealthiest individual, extolling the virtues of capitalism's moral and economic superiority in his recent interview with CNBC's Andrew Ross Sorkin.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:416436 | creators:416436 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.9556514024734497 | 0.9521763920783997 |
| rejection_reasons | quotations | quotations |
| semantic_similarity | 0.9556514024734497 | 0.9521763920783997 |
| entailment_forward | 0.9968581199645996 | 0.996586799621582 |
| entailment_reverse | 0.9653240442276001 | 0.9759334921836853 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] |
| rewrite_entities | ["amazon", "andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] | ["andrew ross sorkin", "cnbc", "jeff bezos", "wall street"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | False | False |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.3525179856115108 | 0.35664335664335667 |
| original_words_replaced_pct | 36.61971830985915 | 32.394366197183096 |
| original_words_deleted_pct | 0.0 | 2.816901408450704 |
| inserted_words_per100_original | 1.408450704225352 | 0.0 |
| word_length_change_pct | -4.225352112676056 | 1.408450704225352 |
| mean_sentence_words_original | 23.666666666666668 | 23.666666666666668 |
| mean_sentence_words_rewrite | 22.666666666666668 | 24.0 |
| sentence_count_original | 3 | 3 |
| sentence_count_rewrite | 3 | 3 |
| sentence_mean_relative_change | 0.04225352112676056 | 0.014084507042253471 |
| punctuation_l1_per100 | 6.193040596520299 | 4.068857589984349 |
| formality_proxy_delta | -1.5327257663628835 | -2.758215962441315 |
| contraction_rate_delta | 1.5327257663628835 | 2.758215962441315 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.28478896564237366 | 0.2854314646759075 |

## 28 — creators:116358

### Original

After 5 1/2 bumpy years of controversial service, the besieged but bolstered attorney general, Eric Holder, resigned. But is this close friend and confidant of President Barack Obama's really stepping down for some benign reason at a critical time for our country, or is there a sinister and strategic plan behind it all?

### New v2

Following five and a half tumultuous years in office, besieged yet fortified Attorney General Eric Holder has tendered his resignation. Yet, is this loyal ally and confidant of President Barack Obama stepping aside for a benign reason at a pivotal moment for our nation, or is there a hidden and strategic motive lurking beneath the surface?

### New v3

Following five and a half tumultuous years, besieged but fortified, Eric Holder, a close ally of President Barack Obama, tendered his resignation. Yet, is this voluntary departure at a pivotal moment for our nation merely benign, or is there a hidden and strategic motive lurking beneath the surface?

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:116358 | creators:116358 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.7019900679588318 | 0.8411165475845337 |
| rejection_reasons | numbers | numbers\|similarity |
| semantic_similarity | 0.898902177810669 | 0.8411165475845337 |
| entailment_forward | 0.9897342920303345 | 0.9913454055786133 |
| entailment_reverse | 0.7019900679588318 | 0.8961362838745117 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["barack obama", "eric holder"] | ["barack obama", "eric holder"] |
| rewrite_entities | ["barack obama", "eric holder"] | ["barack obama", "eric holder"] |
| guard_entities | True | True |
| guard_numbers | False | False |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | False |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.49549549549549554 | 0.6116504854368932 |
| original_words_replaced_pct | 45.45454545454545 | 56.36363636363637 |
| original_words_deleted_pct | 3.6363636363636362 | 7.2727272727272725 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | 1.8181818181818181 | -12.727272727272727 |
| mean_sentence_words_original | 27.5 | 27.5 |
| mean_sentence_words_rewrite | 28.0 | 24.0 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.01818181818181818 | 0.12727272727272726 |
| punctuation_l1_per100 | 1.948051948051948 | 5.492424242424243 |
| formality_proxy_delta | 1.8181818181818181 | 1.8181818181818181 |
| contraction_rate_delta | -1.8181818181818181 | -1.8181818181818181 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.24426000642051454 | 0.2468905067949268 |

## 29 — creators:218236

### Original

Republicans are supposed to be the party that cuts the job-killing capital gains tax, not raises it. But because of a quirk in the Senate-passed tax bill, the tax on capital gains may go up — and for some types of long-held assets, fairly substantially.

### New v2

Republicans are expected to advocate for lowering the job-sapping capital gains tax, not increasing it. However, due to a quirk in the Senate-approved tax legislation, the tax on capital gains might rise — and for certain long-held assets, it could go up significantly.

### New v3

Republicans are often expected to slash the job-sapping capital gains tax, not to hike it. However, thanks to a quirk in the Senate-approved tax legislation, the capital gains tax might indeed rise — and for certain long-held assets, it could go up quite a bit.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:218236 | creators:218236 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.9421830177307129 | 0.9500718712806702 |
| rejection_reasons | certainty | certainty |
| semantic_similarity | 0.9421830177307129 | 0.9500718712806702 |
| entailment_forward | 0.9975481629371643 | 0.9942355751991272 |
| entailment_reverse | 0.9923833012580872 | 0.9965113997459412 |
| added_claim_risk | False | False |
| removed_claim_risk | False | False |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | [] | [] |
| rewrite_entities | [] | [] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | False | False |
| guard_attribution | True | True |
| guard_framing_anchors | True | True |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | True | True |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.4347826086956522 | 0.4893617021276596 |
| original_words_replaced_pct | 44.680851063829785 | 44.680851063829785 |
| original_words_deleted_pct | 0.0 | 4.25531914893617 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -4.25531914893617 | 0.0 |
| mean_sentence_words_original | 23.5 | 23.5 |
| mean_sentence_words_rewrite | 22.5 | 23.5 |
| sentence_count_original | 2 | 2 |
| sentence_count_rewrite | 2 | 2 |
| sentence_mean_relative_change | 0.0425531914893617 | 0.0 |
| punctuation_l1_per100 | 2.884160756501183 | 2.127659574468085 |
| formality_proxy_delta | 0.0 | 0.0 |
| contraction_rate_delta | 0.0 | 0.0 |
| exact_copy | False | False |
| substantial_style_change | True | True |
| style_change_group | substantial | substantial |
| explicit_style_mean_abs_standardized_change | 0.5233367924306669 | 0.5271801819740751 |

## 30 — creators:418827

### Original

WASHINGTON — No, friends, Romans, countrymen, it wasn't enough to murder the White House Rose Garden. It wasn't enough to tear down its stately East Wing, where guests gathered and mingled. It wasn't enough to brandish "Donald J. Trump" over "John F. Kennedy" on the marble wall of the national performing arts center.

### New v2

WASHINGTON — No, friends, Romans, countrymen, it wasn't enough to slash the White House Rose Garden. It wasn't enough to topple its stately East Wing, where guests once mingled. It wasn't enough to display "Donald J. Trump" above "John F. Kennedy" on the marble wall of the national performing arts center.

### New v3

WASHINGTON — No, friends, Romans, countrymen, it wasn't enough to slash the White House Rose Garden. It wasn't enough to topple its stately East Wing, where guests once mingled. It wasn't enough to rewrite "Donald J. Trump" over "John F. Kennedy" on the marble wall of the national performing arts center.

### Automatic checks — not human validation

| Field | v2 | v3 |
| --- | --- | --- |
| row_id | creators:418827 | creators:418827 |
| condition | Normalized | Normalized |
| passed | False | False |
| validation_score | 0.28179290890693665 | 0.10045375674962997 |
| rejection_reasons | framing_anchors\|bidirectional_nli | framing_anchors\|bidirectional_nli |
| semantic_similarity | 0.9656988382339478 | 0.9456658959388733 |
| entailment_forward | 0.28179290890693665 | 0.10045375674962997 |
| entailment_reverse | 0.8050693869590759 | 0.3115755021572113 |
| added_claim_risk | True | True |
| removed_claim_risk | False | True |
| entity_recall | 1.0 | 1.0 |
| entity_precision | 1.0 | 1.0 |
| original_entities | ["east wing", "john f kennedy", "shington", "white house rose garden"] | ["east wing", "john f kennedy", "shington", "white house rose garden"] |
| rewrite_entities | ["east wing", "shington", "white house rose garden"] | ["east wing", "john f kennedy", "shington", "trump", "white house rose garden"] |
| guard_entities | True | True |
| guard_numbers | True | True |
| guard_negation | True | True |
| guard_certainty | True | True |
| guard_attribution | True | True |
| guard_framing_anchors | False | False |
| guard_future_tense | True | True |
| guard_quotations | True | True |
| guard_full_classifier_input | True | True |
| guard_full_semantic_input | True | True |
| guard_full_nli_input | True | True |
| guard_length | True | True |
| guard_complete | True | True |
| guard_similarity | True | True |
| guard_bidirectional_nli | False | False |
| changed_text | True | True |
| human_verified | False | False |
| stance_framing_status | automated screen only, independent human adjudication pending | automated screen only, independent human adjudication pending |

### Style metrics — operational proxies

| Metric | v2 | v3 |
| --- | --- | --- |
| word_edit_fraction | 0.11111111111111116 | 0.09259259259259256 |
| original_words_replaced_pct | 12.727272727272727 | 10.909090909090908 |
| original_words_deleted_pct | 0.0 | 0.0 |
| inserted_words_per100_original | 0.0 | 0.0 |
| word_length_change_pct | -3.6363636363636362 | -3.6363636363636362 |
| mean_sentence_words_original | 11.0 | 11.0 |
| mean_sentence_words_rewrite | 10.6 | 10.6 |
| sentence_count_original | 5 | 5 |
| sentence_count_rewrite | 5 | 5 |
| sentence_mean_relative_change | 0.0363636363636364 | 0.0363636363636364 |
| punctuation_l1_per100 | 0.41166380789022283 | 0.41166380789022283 |
| formality_proxy_delta | -0.20583190394511153 | -0.20583190394511153 |
| contraction_rate_delta | 0.20583190394511153 | 0.20583190394511153 |
| exact_copy | False | False |
| substantial_style_change | False | False |
| style_change_group | intermediate | intermediate |
| explicit_style_mean_abs_standardized_change | 0.04311121015323896 | 0.044301790467498235 |

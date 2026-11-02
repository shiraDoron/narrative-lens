# Error Analysis — External LLM Review — New Normalized

30 דוגמאות train בלבד; 2026-11-01. זהו ניתוח איכותני חדש של הסוכן על בסיס הטקסטים, הקוד והציונים השמורים — לא Human Validation, לא סבב External LLM Review נוסף ולא אימות עובדתי של המאמרים. הכרעות המקור נשארו 19 TP, ‏5 FP, ‏5 TN ו־1 FN ביחס ל־LLM. ‏15 מקרי Borderline נשמרים בנפרד (14 TP ו־1 FN); כולם נושאים גם semantic_drift=Yes בקובץ שסופק. אין לשנות את דירוגם לפי הניתוח הזה.

## מה נמצא ולמה הסיווג לבדו אינו מספיק

**פסילת רשומה אינה הוכחה שה־guard זיהה את השגיאה הסמנטית.** למשל 116358 הוא TP ברמת הרשומה אך נפסל רק בשל צורת מספר שקולה; 298495 נפסל בלי לזהות ישירות את החלפת strangers ב־anonymous sources; 416436 נפסל בשל פסיק בתוך ציטוט בעוד השמטת העליונות המוסרית והכלכלית לא נתפסה ישירות.

נמצאו גם סיכונים שלא הוזכרו בדירוגים חיוביים של ה־LLM: ב־421951 יש חשד להיפוך תפקיד מ־fight your wars ל־face in battle; ב־421024 הושמטו lamentable והטענה המפורשת על חשיפת איברים/תחתונים; ב־212505 most הפך ל־many ו־sharply הושמט; ב־459e183c1d0d net-worth eligibility הפך ל־assets; ב־224770 last week הפך ל־recently. אלה תצפיות הסוכן המחייבות בדיקה ממוקדת, **לא תיוגים אנושיים ולא שינוי של ה־FP/TN החיצוניים**. גם 120669 כולל ניואנס founding president/founding father, בלי להחזיר את טעות Obama/Washington שתוקנה.

## סוגי שגיאות — הסיכום המבוקש

הטבלה מתייחסת רק ל־20 הרשומות שסומנו כסיכון ב־LLM, לא למועמדי הסיכון החדשים ב־FP/TN. count = מספר IDs ייחודיים עם הקטגוריה; קטגוריות חופפות ואין לסכום אותן ל־20. caught_by_guard = קיימת פסילה רלוונטית או רלוונטית חלקית לפי הניתוח; missed_by_guard = אין פסילה כזו. אם שני ניואנסים מאותה קטגוריה שונים באותו ID, זיהוי אחד מספיק לספירת caught ולכן זו אינה טענת כיסוי מלא. NLI/similarity הם אותות כלליים בלבד ולא מסבירים איזה span גרם לציון. קובץ ה־issues שומר caught/partial/missed לכל שינוי בנפרד; טבלת הסוגים כוללת IDs של זיהוי ישיר לעומת חלקי.

likely_source הוא השערה אבחונית, לא ניסוי סיבתי: prompt-induced פירושו סיכון שנוצר בפלט השכתוב, בלי לקבוע אם מקורו ב־prompt, במודל, בכימות או בפענוח. guard-too-weak פירושו כיסוי חסר במקרה שנבדק. לא נבדק prompt חלופי או סף חלופי. number_change/negation_change/causal_relation_change יכולים להישאר אפס: שינוי טוקן מספר/שלילה אינו בהכרח שינוי ערך/קוטביות/סיבתיות. temporal_change כולל less than a decade; אין צורך להמציא קטגוריה מספרית נוספת.

| error_type | count | examples | caught_by_guard | missed_by_guard | likely_source |
| --- | --- | --- | --- | --- | --- |
| stance_or_framing_change | 16 | creators:116358\|creators:216128\|creators:218236\|creators:298495\|creators:416436\|creators:417181\|creators:418827\|creators:418904\|creators:421279\|creators:421853\|creators:422146\|creators:422331\|creators:423315\|creators:423545\|creators:8b0d99b23d03\|creators:97c9d6b9ac1b | 10 | 6 | ambiguous\|guard-too-weak\|prompt-induced |
| factual_change | 16 | creators:218236\|creators:295188\|creators:298495\|creators:2e34435c6ccf\|creators:416436\|creators:417181\|creators:418827\|creators:421279\|creators:421853\|creators:422146\|creators:422329\|creators:422331\|creators:423315\|creators:423545\|creators:8b0d99b23d03\|creators:97c9d6b9ac1b | 10 | 6 | ambiguous\|guard-too-weak\|prompt-induced |
| omission | 10 | creators:116358\|creators:216128\|creators:295188\|creators:416436\|creators:417181\|creators:418827\|creators:418904\|creators:421279\|creators:422331\|creators:423545 | 8 | 2 | ambiguous\|prompt-induced |
| certainty_change | 7 | creators:114783\|creators:216128\|creators:2e34435c6ccf\|creators:417181\|creators:423315\|creators:423545\|creators:97c9d6b9ac1b | 4 | 3 | ambiguous\|guard-too-weak\|prompt-induced |
| attribution_change | 7 | creators:114783\|creators:116358\|creators:295188\|creators:298495\|creators:2e34435c6ccf\|creators:417181\|creators:422329 | 5 | 2 | ambiguous\|prompt-induced |
| addition | 6 | creators:114783\|creators:295188\|creators:2e34435c6ccf\|creators:421853\|creators:422331\|creators:97c9d6b9ac1b | 5 | 1 | ambiguous\|prompt-induced |
| quote_change | 4 | creators:114783\|creators:417181\|creators:418904\|creators:8b0d99b23d03 | 4 | 0 | prompt-induced |
| entity_change | 2 | creators:216128\|creators:417181 | 2 | 0 | prompt-induced |
| temporal_change | 2 | creators:2e34435c6ccf\|creators:422329 | 2 | 0 | ambiguous\|prompt-induced |
| other | 2 | creators:216128\|creators:421279 | 1 | 1 | ambiguous\|prompt-induced |
| number_change | 0 |  | 0 | 0 | ambiguous |
| negation_change | 0 |  | 0 | 0 | ambiguous |
| causal_relation_change | 0 |  | 0 | 0 | ambiguous |

## 19 True Positives — ראיות ורלוונטיות הדגל

### creators:422329 — Borderline

דגלי פסילה: `bidirectional_nli`. קטגוריות: `attribution_change|factual_change|temporal_change`.

- `doubling in less than a decade` → `doubling in just a decade`: A strict duration upper bound becomes a roughly decade-long duration. סוגים: temporal_change, factual_change; alignment=partial; guards=bidirectional_nli.
- `blaming the other party` → `pinning the blame on whichever party is in power`: The target of blame changes from the opposing party to the governing party. סוגים: attribution_change, factual_change; alignment=partial; guards=bidirectional_nli.

NLI flags non-equivalence, but its sentence-pair score cannot prove which span caused rejection. NLI is relevant to changed time bound and blame target; numbers passes because digit sets do not encode less than.

המלצה עתידית בלבד: Candidate claim alignment for temporal comparators and attribution targets; review first, no new rule now.

### creators:417181 — No

דגלי פסילה: `entities|certainty|quotations`. קטגוריות: `attribution_change|certainty_change|entity_change|factual_change|omission|quote_change|stance_or_framing_change`.

- `was likely the Southern Poverty Law Center` → `the SPLC, the primary financier`: Likely modifies the original funding claim; the rewrite states financier status in an appositive and moves appears to the existence of allegations. סוגים: certainty_change, attribution_change; alignment=partial; guards=certainty.
- `denouncing and "fighting" the very same groups in public` → `while publicly denouncing them`: The quoted ironic fighting claim is removed. סוגים: quote_change, omission, stance_or_framing_change; alignment=caught; guards=quotations.
- `hide funding from their donors` → `obscure its donors' contributions`: Hiding funding from donors is not the same relation as obscuring donors' contributions. סוגים: factual_change, attribution_change; alignment=missed; guards=none.
- `Southern Poverty Law Center` → `SPLC`: Full organizational name and United States spelling are replaced with acronyms; identity may be equivalent, but literal preservation fails. סוגים: entity_change, omission; alignment=caught; guards=entities.

Clear claim-scope/relationship risks, consistent with external No. Entity alias failure alone is not proof of drift. Certainty fires on added allegedly, not directly on removal of likely, which is absent from CERT. Quotations directly catches deletion; certainty is partially relevant but scope-blind; attribution passes because its boolean merely sees attribution vocabulary somewhere.

המלצה עתידית בלבד: Prioritize claim-scoped modality/attribution, donor relation and verbatim quote preservation in future rewrite work.

### creators:422331 — Borderline

דגלי פסילה: `bidirectional_nli`. קטגוריות: `addition|factual_change|omission|stance_or_framing_change`.

- `Classic Labor Day imagery shows men wearing hard hats and tough women in uniforms.` → `Traditional Labor Day scenes depict men in hard hats alongside women in uniforms, embodying the hard work of the American workforce.`: Adds an explicit interpretation of imagery as embodying workforce hard work. סוגים: addition, stance_or_framing_change; alignment=partial; guards=bidirectional_nli.
- `These are Americans who did not build their muscles at a wellness club.` → `embodying the hard work of the American workforce`: Drops the explicit wellness-club negation; the replacement is not an equivalent claim. סוגים: omission, factual_change; alignment=partial; guards=bidirectional_nli.
- `The only work most of them have done with their hands is typing.` → `These individuals have primarily used their hands for typing.`: Only work for most becomes primarily used by these individuals; exclusivity and quantification change. סוגים: factual_change, stance_or_framing_change; alignment=partial; guards=bidirectional_nli.

NLI provides a relevant broad signal. Negation count happens to remain equal because another not is introduced later; it does not preserve proposition-level negation. NLI relevant, not localized. Negation count passes despite removed wellness-club denial, illustrating scope weakness.

המלצה עתידית בלבד: Candidate proposition coverage, quantifier/exclusivity and negation-scope checks; no tuning now.

### creators:216128 — Borderline

דגלי פסילה: `entities`. קטגוריות: `certainty_change|entity_change|omission|other|stance_or_framing_change`.

- `the House and Senate` → `the legislative bodies`: Drops explicit named institutions in favor of a generic description. סוגים: entity_change, omission; alignment=caught; guards=entities.
- `Both plans are pro-growth` → `Both plans are aimed at fostering growth`: Asserted property/effect becomes an intended aim. סוגים: certainty_change, stance_or_framing_change; alignment=missed; guards=none.
- `the bet` → `the strategy`: A standing wager/expectation is reframed as a strategy. סוגים: stance_or_framing_change, other; alignment=missed; guards=none.

Entity rejection is relevant to missing names, but does not identify the reviewer's bet/strategy nuance. entities catches a separate literal requirement; certainty has no representation of effect versus intention.

המלצה עתידית בלבד: Candidate claim-level effect/intention and metaphor/expectation preservation; named-entity requirement remains unchanged.

### creators:421279 — Borderline

דגלי פסילה: `certainty|bidirectional_nli`. קטגוריות: `factual_change|omission|other|stance_or_framing_change`.

- `to destroy faith in democracy in little and large ways, on the job day and night` → `to undermine trust in democracy, both big and small`: Softens destroy to undermine and loses the explicit day-and-night effort clause. סוגים: stance_or_framing_change, omission; alignment=partial; guards=bidirectional_nli.
- `an answer that will presently be revealed` → `an explanation that will soon be made public`: Revealing an answer in the discourse becomes making an explanation public; scope of disclosure changes. סוגים: factual_change, other; alignment=partial; guards=bidirectional_nli.

certainty fires on may/might in a reader-directed question, not on the reviewer's disclosure nuance. NLI plausible broad match; certainty is an incidental lexical flag rather than evidence for the identified drift.

המלצה עתידית בלבד: Document mild discourse ambiguity; candidate scoped framing/omission diagnostic rather than a may/might blacklist.

### creators:295188 — Borderline

דגלי פסילה: `bidirectional_nli`. קטגוריות: `addition|attribution_change|factual_change|omission`.

- `I felt hopeful watching Joe Biden and Kamala Harris` → `we watched with hope as Joe Biden and Kamala Harris`: Personal experience is generalized into a collective watching/hope claim. סוגים: attribution_change, addition; alignment=partial; guards=bidirectional_nli.
- `They appeared to understand what we were asking of them and accepted without reservation.` → `Their acceptance appeared genuine and without any reluctance.`: Apparent understanding of the request disappears; genuine acceptance is added and the scope of appeared shifts. סוגים: omission, factual_change; alignment=partial; guards=bidirectional_nli.

NLI flags potentially non-equivalent experiential attribution and final clause. No localization claim can be made from the score. NLI relevant; attribution boolean ignores I/we ownership and appeared's proposition scope.

המלצה עתידית בלבד: Candidate experiencer/claim ownership alignment; preserve first person when changing it adds a group claim.

### creators:422146 — Borderline

דגלי פסילה: `negation|bidirectional_nli`. קטגוריות: `factual_change|stance_or_framing_change`.

- `trade war` → `trade spat`: Downscales the conflict metaphor; bullying and humiliation are also softened to aggressive behavior and targeting. סוגים: stance_or_framing_change; alignment=partial; guards=bidirectional_nli.
- `the Jeffrey Epstein files` → `the Jeffrey Epstein scandal`: A specific documentary referent becomes a broader scandal. סוגים: factual_change, stance_or_framing_change; alignment=partial; guards=bidirectional_nli.

Negation count rejects loss of no other reason plus reformulation; main does not serve proposition remains negative. The flag alone does not locate the substantive framing shifts. NLI plausible relevance; negation is partial because the restrictive no-other-reason construction is lost, not because the final denial is reversed.

המלצה עתידית בלבד: Candidate referent and evaluative-strength alignment; inspect restriction scope rather than negation count alone.

### creators:421853 — Borderline

דגלי פסילה: `negation`. קטגוריות: `addition|factual_change|stance_or_framing_change`.

- `Those who can, do; those who can't, teach.` → `Those who have the ability to succeed, do; those who lack that capability, teach.`: Specifies ability as ability to succeed, adding an interpretation to the proverb. סוגים: addition, factual_change; alignment=missed; guards=none.
- `Those who can, build companies.` → `Those who have the means to start companies, do so.`: Ability to build becomes possession of means to start, shifting the implied contrast. סוגים: factual_change, stance_or_framing_change; alignment=missed; guards=none.

Negation counter loses can't when expressed as lack capability; this is not a positive/negative reversal. The row is rejected incidentally while the new proverb interpretation is not directly captured. negation flag is not relevant to the identified added interpretation; NLI and framing pass.

המלצה עתידית בלבד: Candidate proposition-level interpretation check; lack/cannot equivalence belongs in a separate future diagnostic, not a negation-threshold adjustment.

### creators:114783 — Borderline

דגלי פסילה: `numbers|negation|attribution|quotations`. קטגוריות: `addition|attribution_change|certainty_change|quote_change`.

- `"never forget."` → `never forget the horrors of that day`: Direct quoted content is unquoted and expanded with horrors of that day. סוגים: quote_change, addition; alignment=caught; guards=quotations.
- `our president has a no-strategy strategy` → `our president opts for a strategy that lacks any clear plan`: Having a no-strategy strategy becomes choosing it, adding intentional agency; doesn't seem also softens the accusation. סוגים: attribution_change, certainty_change; alignment=missed; guards=none.

9/11 to September 11 preserves the intended date but the digit-set check fails; said to declared preserves speech attribution but ATTR omits declared; negation tokens shift between no/not/lacks constructions. None of these establishes the core meaning was reversed. quotations directly relevant; numbers technical; attribution lexical false signal for said/declared; negation scope not directly resolved.

המלצה עתידית בלבד: Keep quote fidelity requirement; candidate speech-act normalization and agency checks, with separate date representation diagnostic.

### creators:8b0d99b23d03 — No

דגלי פסילה: `quotations|bidirectional_nli`. קטגוריות: `factual_change|quote_change|stance_or_framing_change`.

- `The rich are different from you and me.` → `The rich are distinct from the rest of us.`: Rewrites the directly attributed Fitzgerald quotation. סוגים: quote_change; alignment=caught; guards=quotations.
- `two countries, both inside America's borders` → `two distinct regions within America's borders`: Removes the class-divide countries metaphor in favor of geographic regions. סוגים: stance_or_framing_change, factual_change; alignment=partial; guards=bidirectional_nli.

Quote fidelity breach is directly observable; NLI is a relevant but nonlocalizing signal for the altered metaphor. quotations directly catches rewritten words; stance/framing anchor list does not represent this metaphor.

המלצה עתידית בלבד: Preserve quoted spans verbatim and rhetorical class-divide metaphor in any future prompt version.

### creators:97c9d6b9ac1b — Borderline

דגלי פסילה: `certainty|bidirectional_nli`. קטגוריות: `addition|certainty_change|factual_change|stance_or_framing_change`.

- `before Donald Trump destroyed it` → `before Donald Trump could dismantle it`: Changes expected destruction to ability/possibility; the before-clause alone does not assert already completed destruction. סוגים: certainty_change; alignment=caught; guards=certainty,bidirectional_nli.
- `from his axe` → `by his bulldozers`: Changes the axe image to specific bulldozers, introducing an instrument not stated in the source. סוגים: addition, factual_change, stance_or_framing_change; alignment=partial; guards=bidirectional_nli.

certainty flags added could at the relevant clause; NLI may detect this or the invented instrument, but scores do not localize it. certainty directly relevant; NLI partial; numbers correctly preserves 430 but cannot detect bulldozers.

המלצה עתידית בלבד: Preserve modal status and avoid inventing physical instruments when rewriting metaphors.

### creators:423545 — No

דגלי פסילה: `certainty|quotations|bidirectional_nli`. קטגוריות: `certainty_change|factual_change|omission|stance_or_framing_change`.

- `the right-wing hack` → `the right-wing figure`: Removes the derogatory hack evaluation while retaining political direction. סוגים: stance_or_framing_change, omission; alignment=partial; guards=bidirectional_nli.
- `probably doesn't know` → `may not be familiar`: Probable ignorance becomes possible unfamiliarity, weakening the likelihood claim. סוגים: certainty_change; alignment=caught; guards=certainty.
- `a bomb maker being blown sky-high by his own creation` → `a creator being destroyed by the very thing they've devised`: Generalizes away bomb maker and explosion; hoisted by a big one also becomes generic predicament. סוגים: factual_change, omission, stance_or_framing_change; alignment=partial; guards=bidirectional_nli.

Quoted petard gains a comma inside its quotation marks: a literal fidelity failure, but not evidence for the insult or metaphor drift. Supplied stance=Yes is retained alongside the more specific framing analysis. certainty relevant; NLI partial; quotations rejects punctuation only in this row, not the actual framing change.

המלצה עתידית בלבד: Preserve stance intensity and metaphor content; do not treat punctuation-only quote flag as a semantic explanation.

### creators:298495 — No

דגלי פסילה: `negation|attribution`. קטגוריות: `attribution_change|factual_change|stance_or_framing_change`.

- `Most of the hate mail came from strangers` → `Most of the hate mail came from anonymous sources`: Unfamiliar people need not be anonymous, and anonymity does not imply being a stranger. סוגים: factual_change; alignment=missed; guards=none.
- `insisting she's acquainted with a different version of God` → `who claims to know a different version of God`: Insistence/experience is reframed as a claim, potentially adding epistemic distance. סוגים: attribution_change, stance_or_framing_change; alignment=partial; guards=attribution.

Attribution fires because claims is in ATTR, while insisting is not. Negation rejects not surprising versus unsurprising without any polarity reversal. Neither specifically detects strangers/anonymous sources. Factual substitution missed; attribution partly relevant to a separate nuance, not proof it caught the factual error. NLI passes.

המלצה עתידית בלבד: Prioritize factual-role/property alignment; keep not-surprising/unsurprising as a local equivalence diagnostic.

### creators:418904 — No

דגלי פסילה: `quotations|bidirectional_nli`. קטגוריות: `omission|quote_change|stance_or_framing_change`.

- `We didn't celebrate the Fourth of July,` → `We didn't mark the Fourth of July,`: Changes a directly quoted word, violating verbatim quotation preservation even if related in ordinary usage. סוגים: quote_change; alignment=caught; guards=quotations.
- `Black backs whipped bloody` → `black backs who were beaten with cruel whips`: Removes the explicit bloody consequence and changes racialized rhetorical imagery; cruel is not the same detail. סוגים: stance_or_framing_change, omission; alignment=partial; guards=bidirectional_nli.

Quotation guard is directly relevant; NLI supplies an additional broad risk signal. Do not weaken quote rules merely because celebrate/mark could be ordinary paraphrases outside quotes. quotes direct; NLI partial; surrender-as-habit versus often is another rhetorical nuance, not a factual verification claim.

המלצה עתידית בלבד: Keep verbatim quotes; preserve violent consequence and rhetorical intensity.

### creators:2e34435c6ccf — Borderline

דגלי פסילה: `negation|certainty|similarity`. קטגוריות: `addition|attribution_change|certainty_change|factual_change|temporal_change`.

- `About three weeks before Republicans expect an electoral beating` → `Just three weeks before Republicans were expected to suffer a significant electoral setback`: Approximate interval becomes exact-looking; Republicans' own expectation becomes a passive expectation with unspecified holder, and tense changes. סוגים: temporal_change, attribution_change, factual_change; alignment=partial; guards=similarity.
- `He simply had to.` → `It was an inevitability he could not avoid.`: Necessity is expanded into explicit inevitability; this may intensify the original, but overlap with had to makes severity uncertain. סוגים: certainty_change, addition; alignment=partial; guards=certainty,negation,similarity.

Could under could not avoid expresses inability to avoid, not uncertainty about an outcome. CERT's token-set trigger does not distinguish modal scope. Added not changes count while preserving the broad necessity claim. similarity partial/nonlocal; certainty and negation are weak scope-blind signals, not demonstrated logical reversals.

המלצה עתידית בלבד: Document ambiguous necessity intensity; candidate interval and expectation-holder alignment, not blanket could/not restrictions.

### creators:416436 — Borderline

דגלי פסילה: `quotations`. קטגוריות: `factual_change|omission|stance_or_framing_change`.

- `unadulterated praise of the moral and economic superiority of capitalism` → `extol the virtues of capitalism`: Drops explicit comparative superiority and moral/economic dimensions; refreshing also becomes merely noteworthy. סוגים: stance_or_framing_change, omission; alignment=missed; guards=none.
- `cheap and easy` → `a simple and effective tactic`: Low cost is replaced by asserted effectiveness. סוגים: factual_change, stance_or_framing_change; alignment=missed; guards=none.

Only rejecting quotations guard detects kulaks versus kulaks, after a comma moves inside the quote. That is a literal fidelity issue, not capture of the substantive omissions; NLI passes. quotations is unrelated to the principal semantic drift; framing and claim-completeness checks are weak.

המלצה עתידית בלבד: Preserve explicit evaluative dimensions and comparisons; separately document punctuation-only quote flags.

### creators:116358 — Borderline

דגלי פסילה: `numbers`. קטגוריות: `attribution_change|omission|stance_or_framing_change`.

- `close friend and confidant of President Barack Obama's` → `loyal ally and confidant of President Barack Obama`: Personal friendship/closeness becomes political loyalty/alliance, which is not the same relation. סוגים: attribution_change, stance_or_framing_change; alignment=missed; guards=none.
- `a sinister and strategic plan` → `a hidden and strategic motive`: Sinister evaluation and plan are replaced by hidden motive, softening valence and changing intent structure. סוגים: stance_or_framing_change, omission; alignment=missed; guards=none.

Only numbers rejects 5 1/2 versus five and a half, the same duration. This TP is row-level agreement with an incidental technical signal, not evidence that numbers recognized relational drift. numbers unrelated/technical; attribution boolean ignores non-speech personal relationship predicates; framing lacks sinister.

המלצה עתידית בלבד: Candidate relational-predicate and evaluative-intensity comparison; numeric value equivalence should be assessed separately.

### creators:218236 — Borderline

דגלי פסילה: `certainty`. קטגוריות: `factual_change|stance_or_framing_change`.

- `are supposed to be the party that cuts` → `are expected to advocate for lowering`: Expected party conduct in cutting taxes becomes advocacy for lowering them; action and advocacy are different predicates. סוגים: stance_or_framing_change, factual_change; alignment=missed; guards=none.

certainty rejects may versus might plus added could, which can preserve possibility here. It does not identify the normative action-to-advocacy change. Numerical strength fairly substantially becomes significantly, a minor intensity nuance. certainty is an incidental modal-word signal; NLI and framing pass the substantive normative shift.

המלצה עתידית בלבד: Document minor normative nuance; candidate predicate/obligation alignment rather than a may/might ban.

### creators:418827 — Borderline

דגלי פסילה: `framing_anchors|bidirectional_nli`. קטגוריות: `factual_change|omission|stance_or_framing_change`.

- `murder the White House Rose Garden` → `slash the White House Rose Garden`: Changes the accusatory murder metaphor; slash/topple/display shifts rhetorical imagery and intensity. סוגים: stance_or_framing_change; alignment=caught; guards=framing_anchors,bidirectional_nli.
- `where guests gathered and mingled` → `where guests once mingled`: Drops gathered; adds a once temporal cue, probably mild but not exact clause retention. סוגים: omission, factual_change; alignment=partial; guards=bidirectional_nli.

FRAME directly registers loss of murder; NLI also rejects without identifying a span. Quoted names remain unchanged. A concrete success for a listed framing anchor, not proof of coverage for riots/protests or unlisted metaphors.

המלצה עתידית בלבד: Keep current anchor signal; future context-sensitive framing coverage should be evaluated separately.

## 5 False Positives — מה טכני ומה עדיין דורש בדיקה

סיווג מנגנון FP נשמר בנפרד מטקסונומיית semantic drift. לא נמצא מקרה שבו ניתן לייחס את הפסילה לסף similarity/NLI קשיח מדי: חמשת ה־FP החיצוניים נפסלו רק ב־guards לקסיקליים/מספריים. אין מכאן הצדקה להקלה בספים.

### creators:0105f26ef9f1

פסילה: `certainty|future_tense`; מנגנון: lexical variation|guard logic issue.

`will make you look around for a long time` → `can make you hesitate for a long time`.

הכרעת ה־LLM: Meaning and stance preserved; substantial style change.

certainty rejects might/may by exact token-set equality; future_tense rejects will/can. The reviewer accepts the core meaning, but will/can also weakens modality, so this is not an unqualified technical FP. certainty flag on might/may is weak evidence; future_tense flag is plausibly relevant to the unreviewed modal weakening, not just tense.

סיכון נפרד שלא הוכרע: Prediction will becomes possibility can; keenly desired loses keenly. Keep external Yes unchanged; these are new assistant-identified risks, not adjudicated drift.

המלצה עתידית בלבד: Document uncertainty and seek targeted review before any modal-equivalence relaxation.

### creators:120177

פסילה: `certainty`; מנגנון: lexical variation|guard logic issue.

`We have to stop it` → `We must halt this descent`.

הכרעת ה־LLM: Core meaning and framing preserved.

The reviewer accepts the same necessity, calendar timing and war-on-Christmas framing. Have to becomes must; CERT recognizes only must. certainty rejects a multiword obligation paraphrase, without demonstrating a change of certainty.

המלצה עתידית בלבד: No rewrite repair needed for have to/must alone; future semantic modal-phrase diagnostic should distinguish obligation from probability.

### creators:212505

פסילה: `numbers`; מנגנון: technical false positive|formatting variation|guard logic issue.

`next 10 weeks` → `next ten weeks`.

הכרעת ה־LLM: Safe rewrite; 10→ten is formatting only.

The only rejecting guard compares digit strings; the quantity ten weeks equals 10 weeks. The external reviewer explicitly treats this as formatting only. numbers rejection is technical for this span, not evidence of a changed quantity. No threshold issue.

סיכון נפרד שלא הוכרע: The whole rewrite also changes most to many and drops sharply; these are separate quantifier/intensity risks the supplied review did not mention. Formatting-only applies to 10/ten, not blanket approval of the row.

המלצה עתידית בלבד: Candidate number-value normalization with units and comparative scope; retain current rejection until an explicit future experiment.

### creators:418620

פסילה: `future_tense`; מנגנון: lexical variation|guard logic issue.

`The next mayor of Washington, D.C. is likely to be a Marxist.` → `It seems probable that the next mayor of Washington, D.C. will be a Marxist.`.

הכרעת ה־LLM: Meaning and certainty preserved.

Likely next mayor and seems probable that next mayor will be retain a future prediction with qualification; only explicit will causes the future boolean mismatch. future_tense recognizes will/shall but not future reference in next mayor; no evidence of new temporal content from will alone.

המלצה עתידית בלבד: No rewrite correction for explicit/implicit futurity alone; candidate time-and-modality semantic comparison in a future guard study.

### creators:459e183c1d0d

פסילה: `certainty`; מנגנון: lexical variation|guard logic issue.

`an allegedly one-time 5% tax` → `a purported one-time 5% tax`.

הכרעת ה־LLM: Restores one-time uncertainty and preserves attribution.

The reviewer accepts restored one-time uncertainty and attribution: allegedly becomes purported, with could and claims retained. CERT includes allegedly but not purported. certainty rejects near-equivalent evidential wording. This does not establish the whole rewrite is exact.

סיכון נפרד שלא הוכרע: Eligibility changes from Californians worth more than $1 billion to Californians with more than $1 billion in assets; assets need not equal net worth because liabilities are omitted. Re-review despite external Yes, without relabelling it.

המלצה עתידית בלבד: No repair for allegedly/purported alone; candidate scoped evidential equivalence diagnostic only after review.

## False Negative — creators:423315

`riots`→`protests` משנה event characterization, framing, lexical polarity ו־stance intensity; התיאור אינו שקול במדויק גם אם האירוע נשאר מזוהה. `going to lose`→`destined to lose` מוסיף גוון הכרחי/פטליסטי של certainty. זו עדיין הכרעת Borderline של הבודק, לא No חדש.

CERT אינו מכיל אף אחד מהביטויים האלו, FRAME אינו מכיל riots/protests, ובדיקת עתיד מחפשת will/shall/ll ולא going to/destined. שוויון ישויות, מספרים ושלילות אינו בודק אפיון אירוע או inevitability. ציוני similarity=0.9563, NLI forward=0.9889, reverse=0.9473 עברו בספים הקיימים; אין לייחס להם הבחנת framing שלא נמדדה. מועמדים למחקר עתידי: השוואת אפיון אירוע/קוטביות בהקשר ו־claim-scoped certainty/inevitability. הוספת מילים לרשימה לבדה אינה פתרון מוכח.

## 15 Borderline — נשמרים כקבוצה חופפת, לא הכרעה בינארית

| ID | סיווג קיים | מה השתנה | סוג הניואנס | האם הדגל רלוונטי | guard חדש או תיעוד |
| --- | --- | --- | --- | --- | --- |
| creators:422329 | True Positive | A strict duration upper bound becomes a roughly decade-long duration.; The target of blame changes from the opposing party to the governing party. | semantic risk קטן\|attribution nuance\|lexical nuance | NLI is relevant to changed time bound and blame target; numbers passes because digit sets do not encode less than. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate claim alignment for temporal comparators and attribution targets; review first, no new rule now. |
| creators:422331 | True Positive | Adds an explicit interpretation of imagery as embodying workforce hard work.; Drops the explicit wellness-club negation; the replacement is not an equivalent claim.; Only work for most becomes primarily used by these individuals; exclusivity and quantification change. | framing shift\|lexical nuance | NLI relevant, not localized. Negation count passes despite removed wellness-club denial, illustrating scope weakness. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate proposition coverage, quantifier/exclusivity and negation-scope checks; no tuning now. |
| creators:216128 | True Positive | Drops explicit named institutions in favor of a generic description.; Asserted property/effect becomes an intended aim.; A standing wager/expectation is reframed as a strategy. | certainty shift\|lexical nuance | entities catches a separate literal requirement; certainty has no representation of effect versus intention. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate claim-level effect/intention and metaphor/expectation preservation; named-entity requirement remains unchanged. |
| creators:421279 | True Positive | Softens destroy to undermine and loses the explicit day-and-night effort clause.; Revealing an answer in the discourse becomes making an explanation public; scope of disclosure changes. | semantic risk קטן\|stance intensity\|lexical nuance | NLI plausible broad match; certainty is an incidental lexical flag rather than evidence for the identified drift. | documentation_only_for_now; targeted review before proposing a new guard; Document mild discourse ambiguity; candidate scoped framing/omission diagnostic rather than a may/might blacklist. |
| creators:295188 | True Positive | Personal experience is generalized into a collective watching/hope claim.; Apparent understanding of the request disappears; genuine acceptance is added and the scope of appeared shifts. | attribution nuance\|semantic risk קטן | NLI relevant; attribution boolean ignores I/we ownership and appeared's proposition scope. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate experiencer/claim ownership alignment; preserve first person when changing it adds a group claim. |
| creators:423315 | False Negative | Violent/disorderly event characterization is broadened/softened to protests; lexical polarity and stance intensity change.; Retrospective future loss is reframed as destined/inevitable, strengthening fatalistic certainty. | framing shift\|certainty shift\|stance intensity\|lexical nuance | Similarity and NLI pass the pair. Need phrase/scope-aware event characterization and inevitability analysis, not just more isolated keywords. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate event-characterization/polarity and scoped inevitability diagnostic; no new guard or threshold deployed. |
| creators:422146 | True Positive | Downscales the conflict metaphor; bullying and humiliation are also softened to aggressive behavior and targeting.; A specific documentary referent becomes a broader scandal. | framing shift\|stance intensity\|lexical nuance | NLI plausible relevance; negation is partial because the restrictive no-other-reason construction is lost, not because the final denial is reversed. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate referent and evaluative-strength alignment; inspect restriction scope rather than negation count alone. |
| creators:421853 | True Positive | Specifies ability as ability to succeed, adding an interpretation to the proverb.; Ability to build becomes possession of means to start, shifting the implied contrast. | lexical nuance\|framing shift | negation flag is not relevant to the identified added interpretation; NLI and framing pass. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate proposition-level interpretation check; lack/cannot equivalence belongs in a separate future diagnostic, not a negation-threshold adjustment. |
| creators:114783 | True Positive | Direct quoted content is unquoted and expanded with horrors of that day.; Having a no-strategy strategy becomes choosing it, adding intentional agency; doesn't seem also softens the accusation. | quote fidelity\|attribution nuance\|certainty shift | quotations directly relevant; numbers technical; attribution lexical false signal for said/declared; negation scope not directly resolved. | candidate_scoped_guard_study; not a validated or deployed guard; Keep quote fidelity requirement; candidate speech-act normalization and agency checks, with separate date representation diagnostic. |
| creators:97c9d6b9ac1b | True Positive | Changes expected destruction to ability/possibility; the before-clause alone does not assert already completed destruction.; Changes the axe image to specific bulldozers, introducing an instrument not stated in the source. | certainty shift\|framing shift | certainty directly relevant; NLI partial; numbers correctly preserves 430 but cannot detect bulldozers. | candidate_scoped_guard_study; not a validated or deployed guard; Preserve modal status and avoid inventing physical instruments when rewriting metaphors. |
| creators:2e34435c6ccf | True Positive | Approximate interval becomes exact-looking; Republicans' own expectation becomes a passive expectation with unspecified holder, and tense changes.; Necessity is expanded into explicit inevitability; this may intensify the original, but overlap with had to makes severity uncertain. | certainty shift\|attribution nuance\|lexical nuance | similarity partial/nonlocal; certainty and negation are weak scope-blind signals, not demonstrated logical reversals. | documentation_only_for_now; targeted review before proposing a new guard; Document ambiguous necessity intensity; candidate interval and expectation-holder alignment, not blanket could/not restrictions. |
| creators:416436 | True Positive | Drops explicit comparative superiority and moral/economic dimensions; refreshing also becomes merely noteworthy.; Low cost is replaced by asserted effectiveness. | framing shift\|stance intensity\|lexical nuance | quotations is unrelated to the principal semantic drift; framing and claim-completeness checks are weak. | candidate_scoped_guard_study; not a validated or deployed guard; Preserve explicit evaluative dimensions and comparisons; separately document punctuation-only quote flags. |
| creators:116358 | True Positive | Personal friendship/closeness becomes political loyalty/alliance, which is not the same relation.; Sinister evaluation and plan are replaced by hidden motive, softening valence and changing intent structure. | attribution nuance\|framing shift\|stance intensity | numbers unrelated/technical; attribution boolean ignores non-speech personal relationship predicates; framing lacks sinister. | candidate_scoped_guard_study; not a validated or deployed guard; Candidate relational-predicate and evaluative-intensity comparison; numeric value equivalence should be assessed separately. |
| creators:218236 | True Positive | Expected party conduct in cutting taxes becomes advocacy for lowering them; action and advocacy are different predicates. | framing shift\|lexical nuance | certainty is an incidental modal-word signal; NLI and framing pass the substantive normative shift. | documentation_only_for_now; targeted review before proposing a new guard; Document minor normative nuance; candidate predicate/obligation alignment rather than a may/might ban. |
| creators:418827 | True Positive | Changes the accusatory murder metaphor; slash/topple/display shifts rhetorical imagery and intensity.; Drops gathered; adds a once temporal cue, probably mild but not exact clause retention. | framing shift\|stance intensity\|lexical nuance | A concrete success for a listed framing anchor, not proof of coverage for riots/protests or unlisted metaphors. | candidate_scoped_guard_study; not a validated or deployed guard; Keep current anchor signal; future context-sensitive framing coverage should be evaluated separately. |

## 5 True Negatives — ביקורת עצמית על מקור ההשוואה

| ID | מה תומך באישור | סיכון חדש לבדיקה, בלי שינוי תווית |
| --- | --- | --- |
| creators:421024 | External TN: reviewer allows slight softening. All guards pass; that does not validate complete preservation. | Lamentable is omitted, man becomes partner, and the claim about displaying privates or underwear in public is removed. Strong candidate omission/framing risks despite external Yes. |
| creators:421951 | External TN and all checks pass, but close reading raises an actor-role contradiction not recognized by the supplied review. | The original wants these sailors to fight one's wars; the rewrite wants to face them as opponents. This is a candidate role reversal, not a change to the saved external label. |
| creators:120669 | External TN; the prior Obama/Washington subject error is absent: his now refers back to Barack Obama. Names and quoted titles are retained. | Founding president becomes founding father, and tried-to-defend is rendered as defend. Document these nuances without relabelling the externally accepted case. |
| creators:419062 | External TN; transfers of wealth/power, political targets and the quoted Deep State remain. Lexical insults are changed but the hostile evaluation remains explicit. | No additional concern identified in this focused review; not human verified. |
| creators:224770 | External TN; core tariff approval and China/Russia targeting remain. Retain the supplied rating but document exactness concerns instead of calling every TN a no-action case. | Last week loses specificity; financial markets narrows to stock markets; allies becomes close allies. These are separate assistant-identified temporal/scope risks despite external Yes. |

## אילו guards עובדים, ואילו אותות מטעים

ספירות הרלוונטיות כאן מתייחסות רק לקידוד 20 סיכוני ה־LLM. סיכונים נוספים שזוהו ב־FP/TN נשארים בנפרד; אפס בעמודה זו אינו הוכחה שדגל על FP הוא בלתי רלוונטי (למשל will/can ב־0105f26ef9f1).

| guard | פסילות | TP חיצוני | FP חיצוני | רלוונטי/חלקי בסיכוני LLM | ישיר בסיכוני LLM |
| --- | --- | --- | --- | --- | --- |
| attribution | 2 | 2 | 0 | 1 | 0 |
| bidirectional_nli | 10 | 10 | 0 | 10 | 0 |
| certainty | 9 | 6 | 3 | 4 | 2 |
| entities | 2 | 2 | 0 | 2 | 2 |
| framing_anchors | 1 | 1 | 0 | 1 | 1 |
| future_tense | 2 | 0 | 2 | 0 | 0 |
| negation | 5 | 5 | 0 | 1 | 0 |
| numbers | 3 | 2 | 1 | 0 | 0 |
| quotations | 6 | 6 | 0 | 4 | 4 |
| similarity | 1 | 1 | 0 | 1 | 0 |

- **Quotations:** מזהה ישירות שינוי/מחיקת תוכן ב־417181, ‏114783, ‏8b0d99b23d03 ו־418904. ב־423545 וב־416436 הוא מתריע רק על פסיק בתוך הציטוט, ולא על השינוי הרטורי המרכזי. דרישת verbatim עדיין הופכת זאת להפרת חוזה טקסטואלית; אין להתייחס אליה אוטומטית כ־semantic drift. הקוד מנרמל case/רווחים וממיין ציטוטים, ולכן גם אינו בדיקת בתים או סדר מלאה.
- **NLI:** אות סיכון רחב בכמה החלפות טענה/השמטות. אינו מאמת את שימור ה־stance, אינו מסביר את span השגיאה, ומפספס את 423315 ואת factual strangers/anonymous ב־298495. אין כאן ניסוי שתומך בשינוי סף.
- **Framing anchors:** מספק אות ממוקד ב־418827 בעקבות אובדן murder. כיסוי לקסיקלי מוגבל: אינו מזהה riots/protests, hack/figure או superiority/virtues.
- **Numbers:** שלוש פסילות על ייצוגים שקולים ברמת הערך: 212505 (10/ten), ‏114783 (9/11/September 11), ‏116358 (5 1/2/five and a half). האחרון TP רק בגלל סיכון אחר. יש לשמר יחידה, תאריך ו־scope בעת מחקר על נרמול, לא רק למחוק ספרות.
- **Certainty/future:** exact token set/נוכחות will מייצרים FP ב־120177, ‏418620 ו־459e183c1d0d; ב־0105f26ef9f1 might/may עשוי להיות שקול אך will/can הוא סיכון מודלי אמיתי לבדיקה. CERT מפספס likely/destined/aimed at. הוא מסמן correctly סיכון ב־probably→may ובתוספת could של 97c9d6b9ac1b, אך אינו מבין scope כמו could not avoid.
- **Negation/attribution:** not surprising/unsurprising, can't/lack capability ו־said/declared מייצרים שינוי ספירה/רשימה ללא היפוך משמעות הכרחי. attribution הוא boolean על קיום מילת ייחוס בכל הטקסט: ב־417181 אפילו United States מספק states. אינו יישור של מי טוען מה. אין לייחס לו זיהוי ישיר של strangers→anonymous sources.
- **Entities:** תופס השמטת House/Senate ב־216128; ראשי תיבות ושמות חלופיים ב־417181 עלולים להיות כשל שימור מילולי בלי שינוי זהות. NER אינו בודק תפקידי נושא/מושא, חברות/ברית, או asset/net worth.

## המלצות נפרדות — אינן שינוי מיושם

### Prompt issues

- לחקור בעתיד שימור טענות לפי actor–predicate–object–time–modality–attribution, ובפרט הבדל בין אפקט לכוונה, בעל הציפייה, יחסי חברות/ברית ו־assets/net worth. לא לשנות first person כשהדבר יוצר טענה על קבוצה.
- להגן על spans מצוטטים, טענות והשוואות מפורשות, comparators כגון less than, quantifiers כגון most/only, עוצמת הערכה ומטאפורות פוליטיות. אין להוסיף כלי עבודה או פרשנות לפתגם.
- לשמור היפותזות אלו לניסוי train חדש בלבד, אם יאושר; לא הוכח שהוראות prompt נוספות יפתרו את כשלי המודל הקטן.

### Guard issues

- לתכנן בעתיד אבחון שקילות ערכים מספריים/תאריכים ושקילות ביטויי שלילה/חובה/עתיד; להפריד דיווח על הפרת literal fidelity מסיכון סמנטי.
- לחקור יישור טענה, תפקידי משתתפים, שייכות ייחוס, scope מודלי ואפיון אירוע/קוטביות. לא להסתפק במילון מילות רגש רחב יותר.
- להעריך כל guard מול שגיאה ממוקדת, לא מול פסילת רשומה בלבד; להפריד טעות מספרית טכנית ב־TP מסיבה סמנטית אחרת. NLI דורש הערכה ממוקדת, לא כוונון סף על סמך 30 הדוגמאות.
- לבקש בדיקה אנושית ממוקדת גם ל־FP/TN שה־LLM אישר למרות עדות טקסטואלית לסיכון. אין להגדיר את ה־LLM כ־gold לצורך קביעת precision/recall של guards.

### No-action cases

- אין צורך לתקן את ערך הזמן ב־10→ten או 5 1/2→five and a half, את not surprising→unsurprising, או את have to→must כשלעצמם. אין בכך אישור של יתר הרשומה או היתר לשנות את guard כעת.
- אין צורך לפתוח מחדש את תיקון Obama/Washington ב־120669; ב־419062 לא זוהה כשל נוסף בניתוח הממוקד. לשמור כדוגמאות חיוביות אבחוניות, בלי להציגן כמאומתות אנושית.
- אין לשנות כעת split/test, labels, human-review fields, prompt, filtering, thresholds או training code. אין למחוק ספי NLI או להקל דרישת ציטוט מילולי כדי להגדיל N.

## מגבלות ושחזור

זהו מדגם אבחוני מכוון של 30 טקסטי train, ללא סוקר אדם וללא הכרעה עצמאית בעובדות העולם. רלוונטיות guard ו־likely_source הן הערכות הסוכן. הראיות הן substrings מדויקים שנבדקים בתוכנית; טוקני CERT/ATTR/FRAME, מספרים, שלילות וציטוטים מחושבים מחדש לצורכי הסבר בלבד ומושווים לדגלים השמורים. לא הורץ מודל שופט, לא נוצרו שכתובים ולא בוצעו training/test evaluation.

קלט הניתוח: `error_analysis_annotations.json` לצד הטקסטים/דירוגים השמורים. לשחזור הדוחות בלבד, מתיקיית הרפו:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/build_error_analysis.py
```

התוצרים: [כל 30 הרשומות](ERROR_ANALYSIS_30.csv), [ראיות לכל שינוי](ERROR_ANALYSIS_ISSUES.csv), [15 מקרי Borderline](ERROR_ANALYSIS_BORDERLINE_15.csv), [סוגי שגיאה](ERROR_ANALYSIS_BY_TYPE.csv), [ניתוח guards](ERROR_ANALYSIS_BY_GUARD.csv), [מנגנוני FP](ERROR_ANALYSIS_FP_MECHANISMS.csv), [ספירות](ERROR_ANALYSIS_COUNTS.json), [בדיקת תקינות](ERROR_ANALYSIS_AUDIT.json). ספירת הקטגוריות ניתנת לשחזור מן ההערות, אך אינה הערכת שכיחות באוכלוסייה. הרצה חוזרת אינה משחזרת שיפוט אנושי; היא משחזרת את החישוב על ההערות האיכותניות הקפואות.

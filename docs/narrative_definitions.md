# Narrative Definitions & Labeling Audit

Status: **audit and definition only** - no labels in the existing dataset were changed while
writing this document. Grounded in real data: `src/narrative_lens/data/audit_narratives.py`
(per-narrative counts/authors/samples, see `reports/results/narrative_audit/narrative_audit.txt`)
and the actual `sbert_only` random-split confusion matrix
(`reports/results/confusion_matrix_sbert_only_random_test.csv`), used to identify each
narrative's empirically-closest neighbor rather than guessing.

Current account rosters (source of truth: `NARRATIVES_ACCOUNTS` in
[`build_twitter_dataset.py`](../src/narrative_lens/data/build_twitter_dataset.py) and
`NARRATIVES_CHANNELS` in
[`build_telegram_dataset.py`](../src/narrative_lens/data/build_telegram_dataset.py)) are listed
under each narrative below. Synthetic `gemini`/`gpt` rows have no per-row author and are
excluded from the account rosters.

Confusion matrix (rows=true, cols=predicted, `sbert_only`, random split test set):

| true\pred | Zionist | Resistance | Western | Russian | Ukrainian | Right-wing | Left-wing |
|---|---|---|---|---|---|---|---|
| Zionist | 295 | 44 | 7 | 12 | 10 | 18 | 12 |
| Resistance | 30 | 272 | 7 | 22 | 14 | 10 | 11 |
| Western | 9 | 11 | 196 | 15 | 24 | 15 | 15 |
| Russian | 11 | 28 | 10 | 317 | 42 | 9 | 7 |
| Ukrainian | 10 | 22 | 12 | 31 | 266 | 12 | 6 |
| Right-wing | 19 | 12 | 16 | 5 | 8 | 264 | 40 |
| Left-wing | 12 | 16 | 13 | 1 | 1 | 35 | 203 |

Empirically closest-neighbor pairs (sum of both confusion directions): **Right-wing ↔ Left-wing**
(75), **Zionist ↔ Resistance** (74), **Russian ↔ Ukrainian** (73) — the three "two sides of the
same conflict" pairs, as expected. **Western** has no single dominant confusion partner; its
largest confusions are with **Ukrainian** (36), **Right-wing** (31) and **Russian** (25) — a
signal that Western content overlaps in vocabulary/topic with several blocs rather than having
one clean ideological opposite. This is explored in detail in the Western section below.

---

## Zionist

**Definition**: Content produced by, or clearly aligned with, official Israeli state
institutions, Israel-advocacy organizations, and pro-Israel citizen-journalism/diaspora-advocacy
accounts. Frames Israel's military/political actions (Gaza, Iran, Lebanon) and national identity
as legitimate/self-evidently justified.

**Accounts**: `Israel`, `IDF`, `StandWithUs`, `AIPAC`, `IsraelMFA`, `AJCGlobal`, `JNS_org`
(Twitter); `southfirstresponders`, `TheJerusalemPost`, `BringThemHomeNow`, `abualiexpress`,
`HananyaNaftali`, `OpenSourceIntel` (Telegram).

**Inclusion criteria**: (a) posted by an official Israeli government/military account, an
Israel-advocacy NGO, or a Jewish-diaspora advocacy org; (b) content affirms Israeli
legitimacy/security narrative, commemorates Oct 7/hostages, reports IDF operations
sympathetically, or defends Israel against "delegitimization."

**Exclusion criteria (recommended, not yet applied)**: routine administrative/service
announcements with zero national-identity or conflict framing (e.g. a blood-donation PSA) should
be flagged as low-signal, not treated as equally representative as identity-affirming content.
Content from a listed account that is entirely off-topic from Israel/Zionism (e.g. unrelated
conspiracy-theory content) should be excluded — see borderline example 4 below, a real,
concerning case found in the audit.

**Distinguishing from Resistance (its empirically closest narrative, 74 total confusions)**:
same underlying conflict (Israel/Gaza/Iran/Lebanon), opposite legitimacy framing — Zionist
content asserts Israel's actions are defensive/justified and its adversaries are terrorists;
Resistance asserts the opposite (Israel/US as aggressor, armed resistance as legitimate).

**5 representative examples**:
1. `[StandWithUs]` "Fragments of an Iranian missile hit a kindergarten in central Israel. This is what we are facing."
2. `[BringThemHomeNow]` "One year ago today, Sasha Trupanov, Yair Horn and Shagyi Dekel Chen returned home... we watched them fall into the arms of their loved ones."
3. `[IDF]` "ELIMINATED: Esmaeil Khatib, the Iranian terrorist regime Minister of Intelligence, in a targeted strike in Tehran."
4. `[AIPAC]` "Here's the true test... Will @PramilaJayapal call out J Street? ... Principle vs hypocrisy."
5. `[IsraelMFA]` "PM Netanyahu... 'Israel does not accept the 15-point document. The IDF will not carry out any withdrawal until Hamas is genuinely disarmed...'"

**Borderline examples (real, found in the audit)**:
1. `[JNS_org]` a blood-donation-drive PSA — zero ideological/conflict content, labeled Zionist purely by account provenance.
2. `[IsraelMFA]` a soft-diplomacy post about MASHAV social-entrepreneurship training for African trainees — reads like generic institutional diplomacy content, not identity-affirming Zionist framing; arguably closer in *register* to the Western narrative's institutional voice.
3. `[gemini_synthetic]` "You know, Zionism is actually quite diverse; there are religious Zionists, secular ones, all kinds." — meta/analytical tone about Zionism rather than an in-group identity-affirming statement.
4. `[OpenSourceIntel]` a COVID-vaccine-conspiracy post ("The COVID Orchestra") — **completely unrelated topic**, mislabeled Zionist purely because the account is in the roster; this is labeling noise, not a genuine borderline case, and is worth a real fix.

---

## Resistance

**Definition**: Content from Iran and the Iran-aligned "Axis of Resistance" (Hezbollah/Houthi/
Hamas-adjacent media) framing military action against Israel/US/West as legitimate resistance to
occupation/aggression.

**Accounts**: `khamenei_ir`, `PressTV`, `QudsNen`, `IrnaEnglish`, `TehranTimes79`,
`MayadeenEnglish` (Twitter); `ResistanceNewsNetwork`, `AlJazeeraEnglish`, `TasnimNewsEN`,
`AlMayadeenEnglish`, `PressTV`, `QudsNen`, `Palestine_Chronicle` (Telegram).

**Inclusion criteria**: posted by Iranian state media/leadership, or by regional
resistance-aligned outlets; content asserts Israeli/US/Western aggression and Iranian/
Hezbollah/Palestinian military-political legitimacy.

**Exclusion criteria (recommended)**: `AlJazeeraEnglish` is already flagged in-repo (code
comment in `build_telegram_dataset.py`) as methodologically borderline — much of its output is
neutral wire-style news, not resistance-framed content (see borderline examples below); this
audit independently confirms that concern with real samples. Channel-outage/seizure placeholder
messages (e.g. `ResistanceNewsNetwork`'s "seized by IDF" notices) carry no narrative content and
should be excluded as noise.

**Distinguishing from Zionist (empirically closest, 74 total confusions)**: same conflict,
opposite legitimacy framing (see Zionist section).

**5 representative examples**:
1. `[AlMayadeenEnglish]` "The Israeli occupation forces have begun carrying out airstrikes targeting the Southern Suburb of Beirut..."
2. `[QudsNen]` "IRGC Aerospace Force displays a missile bearing a sarcastic message reading: 'F-35 stealth? Don't joke with me...'"
3. `[khamenei_ir]` "...the US and the Zionist regime, thinking that the Iranian people were implementing the enemy's vision... used their mercenaries to create countless disasters."
4. `[TasnimNewsEN]` Defense Council statement on Strait of Hormuz coordination/countermeasures.
5. `[PressTV]` "An Iranian source says there was no contact... with Trump, adding he backed down after being warned their targets would include power plants..."

**Borderline examples (real)**:
1. `[AlJazeeraEnglish]` "How is Trump likely to shape his policies in next four years? | Inside Story" — plain neutral news-show promo, no resistance framing.
2. `[AlJazeeraEnglish]` "Gaza aid surge will be challenging, ex-UN official says" — neutral wire-style headline.
3. `[ResistanceNewsNetwork]` "This channel has been seized by the Israeli Defense Force Cybercrime Division..." — ironic case: this is literally IDF-authored text appearing under a Resistance-labeled channel; clear noise, not resistance content.
4. `[MayadeenEnglish]` a story about a Ukrainian drone strike on a Russian oil refinery — off-topic from the Israel/Iran resistance framing entirely.

---

## Western

This narrative gets the deeper audit requested. See the Q&A subsection below for the specific
questions.

**Definition**: Official communications from Western (US/EU/UK/Germany/NATO) government and
inter-governmental institutions, plus mainstream Western wire-service/media reporting. Currently
defined **by account/outlet provenance**, not by a documented ideological content criterion — see
the methodological gap flagged below.

**Accounts**: `NATO`, `EU_Commission`, `POTUS`, `StateDept`, `FCDOGovUK`, `GermanyDiplo`
(Twitter); `WashingtonPost`, `Bloomberg`, `spectatorindex`, `euronews_eng` (Telegram).

**Inclusion criteria (current, implicit)**: posted by one of the above official-institution or
mainstream-media accounts, regardless of the individual post's topic or ideological content.

**Exclusion criteria (recommended)**: topically neutral, apolitical human-interest/cultural/
trivia content from these accounts (see borderline examples) does not carry a "Western
institutional narrative" signal and is arguably mislabeled noise under a stricter definition —
though removing it outright would shrink an already-smaller narrative (994 human-authored rows,
the smallest of the 7), so this is a real trade-off to decide, not a unilateral fix.

**Distinguishing from its closest empirical neighbors**:
- **vs. Ukrainian** (36 confusions, its largest): Western govt statements about Ukraine
  (EU_Commission's loan proposal, FCDOGovUK's sanctions announcement) share vocabulary with
  Ukrainian institutional content, but the speaker differs — Ukrainian narrative = Ukraine's own
  institutions/media speaking about its own war; Western = a third-party government/alliance
  expressing solidarity/policy position.
- **vs. Right-wing** (31 confusions): `POTUS`'s official account sits right at this boundary —
  "AMERICA IS BACK... I will not rest until we have delivered the strong, safe and prosperous
  America..." is institutionally official (White House account) but reads as partisan/nationalist
  rhetoric indistinguishable in tone from Right-wing pundit content. The distinguishing test:
  Western = *official government capacity* statements (regardless of which party holds office);
  Right-wing = partisan media/pundit commentary (Fox News, Ben Shapiro, Heritage) with no
  official government role.
- **vs. Russian** (25 confusions): opposite alliance bloc — both speak in an institutional/
  diplomatic register about the same conflicts (Ukraine, Iran), just from opposing sides.

### Western — specific questions answered

**Is it an ideological narrative?** Only implicitly. Unlike Right-wing/Left-wing (which openly
argue for a domestic political ideology) or Zionist/Resistance/Russian/Ukrainian (which assert a
combatant's legitimacy), Western content mostly does not argue a position — it *performs* an
institutional register (alliance solidarity, "shared values," diplomatic statements, sanctions
announcements) that carries a background liberal-internationalist/transatlantic-alliance
worldview without stating it as an argument.

**Is it institutional/mainstream framing?** Yes, overwhelmingly — of the 12 accounts, 6 are
literal government/IGO accounts and the other 6 are mainstream wire-service/media outlets. There
is currently no non-institutional (think-tank, independent-analyst) voice in the narrative at
all — this is itself a diversity gap (see shortlist below).

**What makes a text "Western" rather than just neutral/mainstream news?** The audit surfaced a
real gap here: several current Western-labeled rows are just topically-neutral content that
happens to come from a Western outlet (see borderline examples 3-5 below — a cultural piece
about Kazakh folklore, a birthday-interview human-interest story, a viral inspirational quote
tweet). None of these carry any institutional/alliance-framing signal; they are "Western" only in
the trivial sense that the account is headquartered in a Western country. A cleaner criterion
going forward: a text is "Western narrative" if it expresses (a) an official government/IGO
position, or (b) alliance-solidarity/sanctions/rules-based-order framing — not merely "published
by a Western outlet."

**Do NATO / WashingtonPost / AtlanticCouncil / Ian Bremmer really belong to the same narrative
concept?**
- `NATO` — yes, the clearest case: literally the alliance's own official institutional voice.
- `WashingtonPost` — partially. Its Ukraine/Russia wire reporting (e.g. "Zelensky confirms
  Russian counteroffensive...") is neutral journalism, not institutional-alignment framing — it's
  "Western" only by outlet nationality, the same gap noted above.
- `AtlanticCouncil` (not yet in the dataset, verified as a scraping candidate) — arguably a
  *better* fit than several current media accounts: it's an explicitly transatlantic-order
  advocacy think tank, producing institutional-aligned analysis rather than neutral reporting.
- `Ian Bremmer` (`ianbremmer`, verified candidate) — genuinely borderline. He is an independent
  geopolitical analyst, sometimes critical of US/Western policy, not speaking for any institution.
  He is better described as "Western-establishment-adjacent commentary" than "Western
  institutional narrative" — worth watching during QC to confirm his posts actually carry
  alliance-aligned framing rather than neutral/critical analysis.

**5 representative examples**:
1. `[FCDOGovUK]` "The ongoing suffering in Gaza... Our government is committed to supporting #Palestine and working towards a lasting peace and a two-state solution." (note: shows Western ≠ automatically pro-Zionist)
2. `[NATO]` "Repost to join us in celebrating our Ally Bulgaria on their National Day! #WeAreNATO"
3. `[EU_Commission]` "...we table our proposal for a €90 billion loan for 2026 and 2027. For a strong Ukraine on the battlefield and at the negotiating table."
4. `[StateDept]` "Just 90 miles off our shores, Cuba exports terrorism and extremism. @SecRubio is right in imposing sanctions..."
5. `[GermanyDiplo]` "We condemn today's launch of a ballistic missile by North Korea... We urge the #DPRK to immediately stop..."

**Borderline examples (real)**:
1. `[POTUS]` "AMERICA IS BACK... this will truly be the golden age of America." — official capacity but partisan/nationalist tone, overlaps Right-wing (see above).
2. `[WashingtonPost]` "Zelensky confirms Russian counteroffensive in Ukrainian-controlled Kursk" — straight wire reporting, no institutional-framing signal beyond outlet nationality.
3. `[euronews_eng]` a piece on a traditional Kazakh goat-puppet dance — entirely apolitical cultural content.
4. `[Bloomberg]` a birthday human-interest interview with Malaysia's ex-PM — apolitical, no Western-narrative signal.
5. `[spectatorindex]` a generic inspirational "you did not choose your birthplace..." quote tweet — viral content with zero connection to institutional/alliance framing.

### Western — final operational definition (2026-09-22 revision)

Supersedes the informal criterion above. This is the definition to actually hand to human
annotators and to use for any future re-labeling decision (not yet applied to existing labels).

**Core distinction: Western institutional/alliance framing vs. mainstream neutral reporting.**
A text is **only** "Western narrative" if it does (a) or (b) below — being published by a
Western government account or Western media outlet is **necessary but not sufficient**.

**(a) Western institutional/alliance framing** — the text does at least one of:
  - States or reports an official government/IGO **position, decision, or policy** (sanctions,
    aid packages, treaties, statements of condemnation/support) in first person or on behalf of
    the institution ("we condemn...", "we table our proposal...", "our government is committed
    to...").
  - Invokes **alliance/bloc solidarity** language ("our Ally," "#WeAreNATO," "shared values,"
    "standing with our partners," "the West must...").
  - Frames an event through a **rules-based-order / transatlantic-institutional lens**
    (referencing international law, sanctions regimes, alliance obligations) even without an
    explicit institutional speaker (e.g. a think-tank analysis arguing NATO should respond a
    certain way).

**(b) Mainstream neutral reporting** (the DEFAULT for outlet-published content) — wire-style
factual reporting, human-interest stories, cultural pieces, or viral/trivia content. This is
**NOT** Western narrative even when published by `WashingtonPost`, `euronews_eng`, `Bloomberg`,
or `spectatorindex` — label it `Other/Neutral` at the text level (see
`NARRATIVE_ANNOTATION_GUIDE.md`).

**Decision checklist for an annotator** (answer in order, stop at first "yes"):
1. Is the account posting in an **official government/IGO capacity** (NATO, EU_Commission,
   POTUS, StateDept, FCDOGovUK, GermanyDiplo, or an equivalent institution) **and** does the text
   state a position/decision/policy (not just an announcement of an unrelated event, e.g. a
   national-day greeting is borderline-weak; a sanctions/aid/condemnation statement is a clear
   yes)? → **Western**.
2. Does the text explicitly invoke alliance/bloc solidarity or a rules-based-order frame,
   regardless of speaker (this is what makes `AtlanticCouncil`/`CFR_org`/`ChathamHouse`-style
   think-tank analysis count, even though they're not government accounts)? → **Western**.
3. Is the text a **partisan/nationalist argument** with no institutional-position content (e.g.
   `POTUS`'s "AMERICA IS BACK... golden age of America")? → do **not** default to Western; treat
   as the Right-wing/Western boundary case and prefer whichever framing dominates the text (here,
   Right-wing-style rhetoric, even from an official account) — flag `ambiguous_flag=yes`.
4. Otherwise (plain wire reporting, human-interest, culture, trivia, viral content) → **not**
   Western; use `Other/Neutral`.

**Why this matters**: under the old (implicit) account-provenance-only criterion, a sizeable
fraction of "Western"-labeled rows are actually category (b) — see borderline examples 2-5 above.
Applying this checklist consistently would likely **shrink** the Western narrative's already-
smallest row count further, which is precisely why this must be validated via the 300-row human
pilot (Part 1) before touching any label, and is exactly the kind of signal the source-derived
labeling audit below is designed to quantify.

---

## Russian

**Definition**: Pro-Kremlin framing of the Ukraine war and broader geopolitics — Russian state
media, MFA, and military accounts presenting Russian actions as justified/defensive and the West
as hypocritical/aggressive.

**Accounts**: `KremlinRussia_E`, `mfa_russia`, `RussiaUN`, `RT_com`, `SputnikInt`,
`tassagency_en` (Twitter); `Rybar`, `IntelSlavaZ`, `DDGeopolitics`, `Slavyangrad`,
`mod_russia_en`, `MariaZakharova`, `Readovka`, `geopolitics_live` (Telegram).

**Inclusion criteria**: posted by a Russian state/military/MFA account or a pro-Kremlin
commentary channel; asserts Russian military/political legitimacy or criticizes Western
hypocrisy.

**Exclusion criteria (recommended)**: purely local human-interest/accident news with no
geopolitical framing at all (see borderline examples) adds noise without narrative signal.

**Distinguishing from Ukrainian (empirically closest, 73 total confusions)**: opposite sides of
the same war — Russian narrative asserts Russian legitimacy/Western hypocrisy; Ukrainian asserts
Ukrainian sovereignty/Russian aggression.

**5 representative examples**:
1. `[RussiaUN]` Lavrov: "New centres of rapid economic growth... are emerging. The world is changing, yet the West is reluctant to relinquish its formerly dominant positions."
2. `[mfa_russia]` "#Zakharova: Former UK PM John Major has recently strongly criticized the US & Israel for attacking Iran... Apparently, he conveniently forgot how eager he was to invade Iraq in 2003... Staggering hypocrisy."
3. `[mod_russia_en]` daily military operational briefing (UAV/drone-operator combat updates).
4. `[DDGeopolitics]` "🇮🇱 Satan's Spawn talking to reporters and urging other nations to join in his personal war on Iran."
5. `[KremlinRussia_E]` "Telephone conversation with Crown Prince of Saudi Arabia Mohammed bin Salman Al Saud."

**Borderline examples (real)**:
1. `[Readovka]` "Two Nivas collided near Smolensk" / "a hang-glider crashed during takeoff" — pure local accident news, zero ideological content.
2. `[SputnikInt]` "India's green energy sprint leaves old records behind" — unrelated topic, no pro-Russian/anti-Western framing.
3. `[RussiaUN]` a procedural statement on the UN's MONUSCO (DR Congo) peacekeeping mandate — weak ideological signal, routine diplomatic business.
4. `[gpt_synthetic]` "Not everything is propaganda—some of it is perspective." — meta-commentary, doesn't itself assert a pro-Russian position.

---

## Ukrainian

**Definition**: Pro-Ukraine framing of the war — Ukrainian state, military, and media voices
reporting on Russian aggression, mobilization, and international-support appeals.

**Accounts**: `ZelenskyyUa`, `Ukraine`, `DefenceU`, `MFA_Ukraine`, `GeneralStaffUA`,
`United24media` (Twitter); `UkraineNow`, `SuspilneNews`, `United24Media`, `Babel`,
`UkraineWorld`, `ukraine_inc`, `KyivIndependent` (Telegram).

**Inclusion criteria**: posted by Ukrainian government/military/media accounts; asserts
Ukrainian sovereignty/resistance to Russian aggression, reports combat/mobilization, or appeals
for international support.

**Exclusion criteria (recommended)**: satirical/mocking content directed *at* Ukrainian
leadership (see `ukraine_inc` example below) does not represent a "pro-Ukraine narrative" voice
despite the channel name, and purely procedural EU/international legal news with no Ukrainian
first-person framing is weak signal.

**Distinguishing from Russian (empirically closest, 73 total confusions)** and **from Western
(36 confusions with Western)**: Ukrainian is the first-person combatant voice; Western is the
third-party institutional-solidarity voice (see Western section).

**5 representative examples**:
1. `[ZelenskyyUa]` "We welcomed President Volodymyr Zelenskyy back to Parliament this week..."
2. `[DefenceU]` "In today's war, survival is a skill you train for every day. Each destroyed drone is a life protected and an attack stopped."
3. `[GeneralStaffUA]` "Operational information as of 08:00... regarding the Russian invasion. In total, over the past day, 254 combat engagements have been recorded."
4. `[MFA_Ukraine]` "...all these children's deaths are a direct result of Russia's war of aggression against Ukraine. By presenting these casualties without this essential context, UNICEF creates a false [impression]..."
5. `[Babel]` "In one week, Russia launched almost 1,550 attack drones, more than 1,260 anti-aircraft missiles and two missiles over Ukraine, President... Zelenskyi said."

**Borderline examples (real)**:
1. `[UkraineWorld]` "The executive body of the Kyiv City Council ordered a Hanukkah from the United Jewish Community of Ukraine for UAH 17.3 million. No comments." — sarcastic domestic-corruption snark, actually critical of a Ukrainian institution.
2. `[UkraineWorld]` "The EU Court decided to lift the sanctions on corruption charges against Viktor Yanukovych..." — procedural EU legal news, no Ukrainian first-person framing.
3. `[ukraine_inc]` "Ukraine inc HIT ELENDSKY 🤣😂🫵" — mocking/satirical content about Zelensky, arguably not a pro-Ukraine-narrative voice at all despite the channel's name.
4. `[Babel]` a report on Russian oil-export logistics at Novorossiysk — economic wire reporting, weak ideological framing.

---

## Right-wing

**Definition**: US-centric (with one notable Israeli outlier, see below) conservative/populist
commentary — anti-immigration, anti-"woke," pro-Trump, culture-war framing, skepticism of
mainstream/left institutions.

**Accounts**: `FoxNews`, `BenShapiro`, `dailywire`, `Heritage`, `TPUSA` (Twitter);
`BreitbartNews`, `TheEpochTimes`, `Newsmax`, `OneAmericaNews`, `CharlieKirk`,
`ThePostMillennial`, `WesternJournal`, `@KoheletForum` (Telegram).

**Inclusion criteria**: posted by a US conservative media/pundit/advocacy account; argues for a
conservative/populist position on immigration, culture-war topics, or defends Trump/the
Republican party.

**Exclusion criteria (recommended)**: empty/placeholder posts and pure administrative
"first post!" content (see borderline examples) carry no ideological signal.

**Real outlier flagged**: `@KoheletForum` is an **Israeli** right-wing/free-market think tank
(Knesset legislation, Israeli economic policy) — topically unrelated to the US culture-war
content that defines the rest of this narrative's accounts. It fits the label only under a
*country-agnostic ideological* definition of "Right-wing" (conservative/nationalist,
regardless of country), which is a real methodological choice worth stating explicitly rather
than leaving implicit — mixing US-culture-war content with Israeli-domestic-economic-policy
content may dilute how coherent/learnable this narrative is.

**Distinguishing from Left-wing (empirically closest, 75 total confusions, the single largest
pair in the whole matrix)**: opposite partisan valence on the same domestic US political topics
(immigration, Trump, culture war).

**5 representative examples**:
1. `[CharlieKirk]` "...Zohran Mamdani promises to empty the jails in NYC. Mamdani will spark a 1990s style crime wave..."
2. `[FoxNews]` "BREAKING: President Trump says he'll put I.C.E. agents at airports for security if Democrats don't sign DHS deal."
3. `[Heritage]` "A website advertising 'Have Your Baby in Texas' isn't a glitch in the system. It's proof the system is being exploited."
4. `[TPUSA]` "MEN IN WOMEN'S SPORTS: The debate over biological males competing in women's sports just reignited..."
5. `[BenShapiro]` "WATCH: DSA activists vile response to Charlie Kirk's assassination... Neither he, nor any member of DSA should be anywhere near elected office."

**Borderline examples (real)**:
1. `[@KoheletForum]` congratulating a researcher on an academic writing-competition win — purely social/celebratory, zero ideological content, and topically Israeli not US.
2. `[TheEpochTimes]` "Scientists Say They Have Solved the Mystery of What Killed More Than 5 Billion Sea Stars" — pure science news.
3. `[OneAmericaNews]` a post whose entire text is just "@OneAmericaNews" — empty/placeholder, no content.
4. `[dailywire]` "our first post into the twitter world!" — administrative/meta, zero ideological content.
5. `[BreitbartNews]` "Hugh Laurie Rips Republicans, Trump At Golden Globes (Video)" — the *bare text* just reports someone else's criticism; the right-wing framing (if any) is implicit in why Breitbart chose to cover it, not stated in the text itself.

---

## Left-wing

**Definition**: US/UK-centric progressive/socialist commentary — pro-labor, anti-Trump,
pro-Palestinian-solidarity framing on Israel-Gaza, pro-asylum/immigration, anti-inequality.

**Accounts**: `novaramedia`, `BernieSanders`, `jacobin`, `democracynow`, `thenation` (Twitter);
`TheIntercept`, `ViceNews`, `DemocracyDocket`, `@MiddleEastEye_TG` (Telegram).

**Inclusion criteria**: posted by a progressive/socialist media, politician, or advocacy account;
argues for a progressive position on labor/inequality/immigration, criticizes Trump/Republicans,
or reports pro-Palestinian solidarity content.

**Exclusion criteria (recommended)**: spam/placeholder fragments (see borderline examples 1-2)
and cross-language data artifacts (example 3) carry no ideological content and should be
excluded.

**Note on `@MiddleEastEye_TG`**: topically overlaps with Resistance (both cover Israel/Gaza), but
is positioned here as a Western-audience progressive/pro-Palestinian-solidarity outlet rather
than a regional Axis-of-Resistance actor — the distinguishing test vs. Resistance is *who is
speaking* (a Western-based progressive outlet vs. an Iran/Hezbollah-aligned regional actor), not
just *what topic* is covered. Several of its Israel/Gaza posts read as plain factual wire
reporting (see borderline example 5) with no distinctly "left-wing" ideological marker in the
bare text — the same "outlet identity vs. framing content" gap flagged for Western.

**Distinguishing from Right-wing (empirically closest, 75 total confusions)**: opposite partisan
valence on the same domestic US political topics.

**5 representative examples**:
1. `[BernieSanders]` "Starting Saturday, millions will see health costs skyrocket because of Trump's 'Big Beautiful Bill.'... Fight back."
2. `[novaramedia]` "Asylum seekers arriving in the UK will now face reassessment every 30 months for 20 years, making permanent asylum an unattainable dream."
3. `[jacobin]` "The Left can't sit out the 2028 Democratic primary... socialists should run a working-class candidate... who can inject anti-billionaire politics into the race."
4. `[TheIntercept]` "Eight International Students at ASU Have Had Their Visas Revoked"
5. `[democracynow]` "Israel has charged a settler in the death of Palestinian activist Awdah Hathaleen... after the rights group Al-Haq compiled evidence and urged the ICC to step in."

**Borderline examples (real)**:
1. `[DemocracyDocket]` "high price 🍻" — nonsensical fragment, no content signal.
2. `[DemocracyDocket]` a Telegram-bot referral spam link — pure spam, not content.
3. `[gpt_synthetic]` "תגובה: some groups are still overlooked." — a Hebrew word ("תגובה" = "comment/response") leaking into an English synthetic generation; a data-quality artifact, not a real statement.
4. `[ViceNews]` "Extremists are using climate change disasters as opportunities—rolling in as volunteers and exploiting communities..." — reads as centrist-alarmist framing about "extremists," ambiguous progressive alignment.
5. `[@MiddleEastEye_TG]` a factual report of an Iran missile strike on Israel — plain wire-style reporting with no distinct left-wing ideological marker in the bare text (see note above).

---

## Summary of cross-cutting findings from this audit

1. **A recurring "outlet identity vs. framing content" gap** exists in Western,
   Left-wing (`@MiddleEastEye_TG`), and to a lesser extent Zionist/Right-wing/Russian: a
   meaningful fraction of rows in every narrative are topically neutral or off-topic content that
   is labeled purely by account provenance, not because the text itself carries the narrative's
   ideological framing. This is a real, systemic labeling-methodology question, not isolated
   noise in one narrative.
2. Two of the seven narratives (`Zionist`/`OpenSourceIntel`, `Resistance`/`ResistanceNewsNetwork`)
   contain at least one clearly mislabeled/off-topic account-level content stream, worth a
   dedicated cleanup pass separate from this Phase-1 pilot.
3. `Western` is the smallest human-authored narrative (994 rows) and the *only* one built
   entirely from institutional/mainstream-media voices with zero independent-analyst or
   think-tank perspective — this is the concrete gap the Phase-1 shortlist (see
   `docs/dataset_v2_pilot_status.md` or the delivered chat report) targets.

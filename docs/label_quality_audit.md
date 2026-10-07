# Label Quality Audit & Cleanup Plan (Dataset V2, Phase 0)

Status: **flagging and proposals only** — no labels in `data/raw/*.csv` were changed while
producing this document. This is the pre-scraping "clean labels first" pass requested before any
new Left-wing/Western collection or matched-event benchmark construction.

Produced by `src/narrative_lens/data/audit_label_quality.py` (heuristic keyword-based text/label
consistency check) plus manual review of the accounts it surfaced. Outputs:
`artifacts/experiments/narrative_audit/label_quality_{per_text,narrative_summary,account_flags}.csv`.

## 1. How the heuristic works, and its real limitation (read this first)

For each text, we count hits against a small (~10-15 term) list of **framing markers** per
narrative (opinion/legitimacy-assertion phrases, not topic nouns like "Israel"/"Iran" — see
`FRAMING_MARKERS` in the script). A text is `strongly_aligned` if its own narrative's markers
score highest, `potentially_neutral` if no narrative's markers hit at all, and
`potentially_mismatched` if some *other* narrative's markers score higher.

**Important finding about the heuristic itself**: `strongly_aligned` rates are low across the
board (2%–29%, see table below) — including for accounts we know from manual reading are
genuinely, strongly ideological (e.g. `BernieSanders` 34%, `khamenei_ir` 19%, `NATO` 18%,
`PressTV` 26%). **This does not mean these accounts are unreliable** — it means natural-language
ideological framing is far more varied than any short keyword list can capture (tone, implicit
argument, named entities, sarcasm). **`potentially_neutral` should be read as "the heuristic found
no explicit marker," not "this text has no narrative framing."** The one heuristic signal we DO
trust as meaningful is `potentially_mismatched` (an opposing narrative's specific framing markers
scored higher) — a much more specific, lower-false-positive signal — and, combined with manual
reading, extreme/sustained `potentially_neutral` rates on **specific, checkable accounts** (below).

## 2. Per-narrative summary (heuristic counts, human-authored data only)

| Narrative | strongly_aligned | potentially_neutral | potentially_mismatched | total | % aligned |
|---|---|---|---|---|---|
| Zionist | 497 | 1155 | 90 | 1742 | 28.5% |
| Resistance | 398 | 1070 | 52 | 1520 | 26.2% |
| Left-wing | 95 | 830 | 88 | 1013 | 9.4% |
| Western | 77 | 848 | 69 | 994 | 7.7% |
| Russian | 91 | 1558 | 233 | 1882 | 4.8% |
| Ukrainian | 56 | 1397 | 186 | 1639 | 3.4% |
| Right-wing | 34 | 1395 | 111 | 1540 | 2.2% |

Zionist/Resistance score highest on this heuristic because their framing markers (hostage,
terrorist, occupation, martyr, etc.) are more concrete/lexical than the others' (e.g. Western's
"alliance/sanctions/committed to" or Right-wing's "woke/deep state" are rarer per-text even in
genuinely aligned content). **Read the ranking as an artifact of marker specificity, not a
genuine narrative-quality ranking.**

`potentially_mismatched` rate is the more useful column: **Russian (12.4%)** and **Ukrainian
(11.3%)** stand out as highest — consistent with these being the empirically-closest-confused
pair (see `docs/narrative_definitions.md`), i.e. Russian- and Ukrainian-labeled texts sometimes
literally contain the *other* side's framing markers (a Russian-labeled account quoting/reporting
Ukrainian claims, or vice versa) — worth spot-checking during the 300-row human validation.

## 3. Account-level review — the two named accounts, plus 3 more with a similar pattern

The heuristic's raw "non-aligned fraction" flags 59/83 accounts (too broad to be useful as-is —
see limitation above). Below are 5 accounts manually inspected because they combine an extreme
heuristic signal with a **directly checkable, real content problem** (not just a keyword-coverage
gap). 20-text (or full, if fewer) samples read for each; current label; assessment; recommendation.

### `OpenSourceIntel` (labeled Zionist) — 200 texts, 0% aligned, 97.5% neutral, 2.5% mismatched
**Sample content (real, from the corpus)**: near-entirely COVID-vaccine conspiracy material —
"356 Athlete Cardiac Arrests... After COVID Shot," "mRNA vaccine... reprograms adaptive and
innate immune responses," "Contaminants in the Vaccines," "5G radiofrequency... coronavirus,"
"world's first vaccine murder case against Bill Gates" — plus general US-populist/conspiracy
content unrelated to Israel: Tucker Carlson on immigration/"Cloward-Piven strategy," "Bonhoeffer's
Theory of Stupidity," NIH funding conspiracy threads.
**Does it fit Zionist?** No. Across the full 200-text sample, essentially none of the content
concerns Israel, Zionism, or the Israel-Iran/Gaza conflict at all.
**Recommendation: REMOVE** this account's rows from the Zionist narrative entirely (not
relabel — the content doesn't cleanly fit any of the other 6 narratives either; it's generic
conspiracy-media content, out of scope for this dataset). This is the clearest, highest-confidence
mislabel in the corpus.

### `ResistanceNewsNetwork` (labeled Resistance) — 2 texts, 0% aligned, 100% neutral
**Sample content (full — only 2 rows exist)**: both rows are the identical text: "⚠️ This channel
has been seized by the Israeli Defense Force Cybercrime Division. For any questions or concerns,
please contact the IDF for explanation."
**Does it fit Resistance?** No — this is (ironically) IDF-authored placeholder text left on a
seized/dead channel, not Resistance content at all.
**Recommendation: REMOVE** both rows (trivial — 2 rows, zero information value, arguably actively
misleading since the text reads as pro-Israel/anti-Resistance in tone despite the Resistance
label).

### `OneAmericaNews` (labeled Right-wing) — 5 texts, 0% aligned, 100% neutral
**Sample content (full — only 5 rows)**: two rows are literally just `@OneAmericaNews`, two rows
are just the channel's own t.me link, and one row is genuine content (GOP senators on COVID
mandate defunding).
**Does it fit Right-wing?** The 1 real row does; the other 4 are empty self-referential
spam/placeholder text.
**Recommendation: REMOVE the 4 placeholder/spam rows**; keep the 1 genuine row, but the account
overall has too little real signal (1/5 usable) to be a meaningful contributor — consider it a
low priority for future re-scraping too.

### `Readovka` (labeled Russian) — 200 texts, 0% aligned, 98% neutral, 2% mismatched — reviewed as a control/comparison case
**Sample content**: overwhelmingly hyperlocal Smolensk-region news — traffic accidents ("Two
Nivas collided," "a moose jumped under the wheels of a car"), weather, minor local corruption
cases, a rescued-drowning-children story. Essentially no anti-Western/pro-Kremlin framing in the
sample read.
**Does it fit Russian (the narrative, i.e. pro-Kremlin framing)?** Mostly no, but differently
from `OpenSourceIntel` — `Readovka` is a real, legitimate Russian regional news outlet; its
content is simply **local human-interest news**, not ideological framing. This is NOT a mislabel
in the sense of "wrong topic/fake account" — it's a **low-narrative-signal** account.
**Recommendation: KEEP the account (legitimate, real, Russian-published) but flag for MANUAL
REVIEW / down-weighting** in any future retraining — the bulk of its rows likely teach the model
"Russian regional news style" rather than "pro-Kremlin narrative framing," which could dilute the
narrative's learnability. Do not delete outright without a targeted look for its more clearly
framed minority of posts.

### `TheEpochTimes` (labeled Right-wing) — 200 texts, 0% aligned, 98.5% neutral, 1.5% mismatched — reviewed as a heuristic false-positive check
**Sample content**: Trump State of the Union / cabinet meeting livestreams, "Truth Under Fire: The
Framing of Charlie Kirk," Brownstone Institute conference (anti-lockdown/vaccine-skeptic
advocacy), "How Race-Based Policies Are Harming South Africa," "From Cultural Revolution to
Cultural Revival: ...'How to Save the West'," CCP organ-harvesting exposés.
**Does it fit Right-wing?** Yes, on manual reading — this is clearly right-coded content
(pro-Trump coverage, anti-CCP, vaccine-skepticism-adjacent, culture-war-adjacent framing) that
simply doesn't contain any of our ~10 literal keyword phrases. **This is a heuristic
false-negative, not a real mislabel.**
**Recommendation: KEEP, no action needed.** Included here specifically as a control case to show
the heuristic's `potentially_neutral` bucket must always be manually spot-checked before treating
it as "no narrative signal," per the limitation noted in section 1.

### Pattern found
Two genuinely bad accounts (`OpenSourceIntel`, `ResistanceNewsNetwork`) — both clear, high-
confidence removals. One low-value account (`OneAmericaNews`, mostly spam by row count but tiny).
One real-but-low-signal account (`Readovka`) needing down-weighting, not removal. One heuristic
false-positive (`TheEpochTimes`) needing no action — **demonstrating why every account flagged by
this script must be manually read before any label/removal decision**, exactly as instructed.

## 4. Matched-event benchmark — shortlist of 4 (not built yet, per instruction)

From the already-computed `artifacts/experiments/narrative_audit/matched_event_candidates_full.csv`
(systematic mining across 5 topics × every month, human-authored data only), ranked by how many
narratives are present, author diversity, and per-narrative text volume:

| Rank | Event | Narratives (count) | Per-narrative texts/authors | Notes |
|---|---|---|---|---|
| 1 | `us_politics_trump_2026-03` | **7/7** | Left-wing 20/2, Resistance 23/3, Right-wing 92/2, Russian 17/2, Ukrainian 12/2, Western 10/2, Zionist 23/3 | Cleanest possible case — every narrative clears both the ≥2-author and ≥10-text bar. |
| 2 | `iran_2026-03` | **7/7** | Left-wing 22/2, Resistance 221/3, Right-wing 38/2, Russian 38/2, Ukrainian 22/2, Western 9/2, Zionist 231/4 | Near-perfect; Western is 1 text under the ~10 target (9) — still usable, flag as borderline. |
| 3 | `israel_hezbollah_gaza_2026-03` | 5/7 (missing Ukrainian, Western) | Left-wing 27/2, Resistance 151/3, Right-wing 13/2, Russian 14/2, Zionist 279/4 | Missing 2 narratives entirely, but the 5 present are all well above threshold (13-279 texts, 2-4 authors) — good for a 5-narrative comparison, not a full 7-narrative one. |
| 4 | `russia_ukraine_2026-02` | 3/7 (Russian, Ukrainian, Western only) | Russian 70/2, Ukrainian 99/2, Western 23/2 | Smaller narrative set but very clean numbers; the only strong candidate that centers the Russia-Ukraine war specifically rather than US/Iran politics — useful for coverage diversity across benchmark events. |

**Recommendation**: build the full benchmark from events #1 and #2 first (both 7/7 narratives);
optionally add #3 and #4 as secondary, narrower-scope benchmark events once the primary two are
validated. Do not build yet, per instruction — this is a shortlist for approval.

## 5. Dataset cleanup policy proposal

Not applied yet — proposal for approval before any label is touched.

**Neutral texts** (heuristically `potentially_neutral` AND confirmed by human validation as
carrying no narrative framing): do not delete outright (this would shrink already-small
narratives like Western further and lose real text volume). Instead, **introduce a new label
value, `Unclear/Neutral`**, and move confirmed-neutral rows there. Keep them in the raw corpus but
**exclude `Unclear/Neutral` rows from the main 7-way classification task** (train/val/test) by
default — they remain available for future auxiliary tasks (e.g. narrative-detection-as-binary,
"has framing or not").

**Ambiguous texts** (defensibly fits 2+ narratives per human validation): keep the original label
but add a `multi_narrative_candidate` flag/column rather than dropping or reassigning — these are
valuable for a future soft-label or multi-label extension, but keep single-label training clean by
defaulting to the original account-provenance label unless a reviewer's confidence is high that a
different single label fits better.

**Mislabeled texts** (like `OpenSourceIntel`, `ResistanceNewsNetwork` above — content doesn't fit
any narrative or clearly fits a different one): **remove from the main dataset entirely** (not
relabel into a wrong bucket) if off-topic/generic; **relabel** only if a human reviewer confirms a
specific different narrative fits clearly and consistently across that account's content.

**Account-level vs. text-level label**: adopt a **hybrid policy** — keep account-level label as
the *default*, but require it to be **corroborated by text-level framing** for any row entering
the primary training set. Concretely: an account whose `strongly_aligned`-after-human-validation
rate falls below some threshold (e.g. <20-30% once real human labels replace the heuristic) should
have its low-signal rows moved to `Unclear/Neutral` rather than counted as full-strength training
examples for that narrative, even though the account itself may still legitimately belong to that
narrative's roster.

**Net effect**: this shrinks the effective *usable* size of every narrative somewhat (especially
Western, already the smallest), which is precisely why "clean labels first, more data second" is
the right order — pursuing new Western/Left-wing scraping without this pass would just add more
of the same provenance-only-labeled noise.

## 6. Explicitly NOT done yet (per instruction)

- No labels in `data/raw/*.csv` were changed.
- No accounts were removed from the live roster.
- No new scraping was performed (Left-wing/Western expansion, matched-event benchmark
  construction, and the V2 pilot scraper all remain paused pending label-quality validation).
- No model was trained or retrained.

## Next step

A blind human-validation protocol has since been built on top of this audit (see
`docs/NARRATIVE_ANNOTATION_GUIDE.md` and `build_blind_validation_sample.py` /
`analyze_human_validation.py`) — annotators judge `data/annotation/human_validation_pilot_300_blind.csv`
from text alone (no narrative/author/platform shown), with a 100-row stratified second-annotator
overlap for Cohen's kappa. Once that completes, `analyze_human_validation.py` replaces this
heuristic proxy with real human labels, and only then do we decide: (a) whether to actually create
an `Unclear/Neutral` label and apply the cleanup policy above, (b) whether to remove
`OpenSourceIntel`/`ResistanceNewsNetwork` outright, (c) which 2-4 matched events to build into the
final benchmark, before resuming any new scraping.

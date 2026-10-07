# Narrative Annotation Guide (Blind Human-Validation Pilot)

For reviewers annotating `data/annotation/human_validation_pilot_300_blind.csv` (annotator 1,
all 300 rows) or `human_validation_pilot_300_blind_second_annotator_subset.csv` (annotator 2, a
stratified 100-row subset used to measure inter-annotator agreement). Full reasoning and real
examples backing every rule here are in
[`docs/narrative_definitions.md`](narrative_definitions.md) — read that first if a case doesn't
seem to fit.

## This is a BLIND study — read this first

The file you are annotating has **only** `annotation_id` and `text`. It does **not** show you the
account/handle that posted it, the platform (Twitter/Telegram), or the narrative label our
scraper originally assigned. This is intentional. Your task is:

> Read the text. Decide which narrative, if any, it expresses — based on the text alone.

You are **not** confirming or rejecting an existing label — you do not know what it is, and you
should not try to guess it from writing style or platform conventions. Do not search for the text
online to identify its source. The comparison against the original source-derived label happens
only afterward, programmatically, via `annotation_id` — you never need to think about it while
annotating.

You'll see `[USER]` and `[URL]` placeholders in some texts — these replace @handles and links that
were stripped only to prevent source identification; nothing else about the text was changed
(named entities like Trump, Israel, NATO, Hezbollah, etc. are always left as-is since they're part
of the actual content/framing, not metadata). Judge the text as if those placeholders were simply
"a link" / "a mentioned account", without trying to guess what they originally said.

One remaining known limitation: on rare rows a self-reference may still read as a plain name in
running prose rather than an `@handle` or link (so it wasn't caught by the redaction). If you spot
something that feels like it's naming its own source, judge the content on its merits anyway —
don't look it up, and don't treat its mere presence as evidence of a narrative.

## Columns to fill in

- **`reviewer_label`**: exactly one of the 7 narrative names below (see table), OR leave blank if
  you set `neutral_or_no_clear_narrative = True` instead. Don't write anything else in this column
  (no "Other", no free text — use the neutral flag for that).
- **`confidence`**: an integer, `3` / `2` / `1`:
  | Value | Meaning |
  |---|---|
  | `3` | Clear narrative — framing is explicit and unambiguous. |
  | `2` | Probable but some uncertainty — you lean toward this narrative but aren't fully sure. |
  | `1` | Weak / highly uncertain — you're mostly guessing, or the signal is very thin. |
- **`neutral_or_no_clear_narrative`**: `True` if the text carries **no narrative framing at all** —
  plain factual reporting, human-interest content, spam, an empty/placeholder post, or content
  totally unrelated to any of the 7 narratives (e.g. health/science trivia). If `True`, you can
  leave `reviewer_label` blank.
- **`ambiguous_flag`**: `True` if the text is a genuinely defensible fit for **more than one**
  narrative (not just "hard to tell" — "a reasonable person could argue either way"). If `True`,
  put your primary choice in `reviewer_label` and the second-best fit in `secondary_narrative`.
- **`secondary_narrative`**: only fill in when `ambiguous_flag = True` — the second narrative that
  plausibly fits. Leave blank otherwise.
- **`notes`**: free text — anything worth flagging (data-quality artifact, suspicious content,
  can't classify for a reason worth recording, etc.). Optional but useful.

## The 7 narratives, in one line each

| Narrative | One-line test |
|---|---|
| Zionist | Asserts Israeli state/military legitimacy, security, or identity |
| Resistance | Asserts Iran/Hezbollah/Hamas-aligned "Axis of Resistance" legitimacy against Israel/US/West |
| Western | Official Western (US/EU/UK/Germany/NATO) government/IGO position, or alliance-solidarity framing |
| Russian | Asserts Russian state legitimacy in the Ukraine war / anti-Western-hypocrisy framing |
| Ukrainian | Asserts Ukrainian sovereignty/resistance to Russian aggression, first-person Ukrainian voice |
| Right-wing | US-centric conservative/populist argument (immigration, culture war, pro-Trump) |
| Left-wing | US/UK-centric progressive/socialist argument (labor, inequality, anti-Trump, pro-Palestinian solidarity) |

See `docs/narrative_definitions.md` for the full definition, inclusion/exclusion criteria, and
which narrative each one is most often confused with, per narrative.

## Content patterns worth knowing (judge the text, not the source)

These patterns turned up during the source-derived audit — they describe what to look for **in
the text**, not which accounts to watch for (you can't see the account anyway):

1. **Fully off-topic content happens.** Some texts labeled under a given narrative are, on
   reading, about something else entirely (e.g. medical/conspiracy content with no connection to
   the narrative's topic, or purely local human-interest news). If the text itself carries no
   framing for its apparent topic, mark `neutral_or_no_clear_narrative = True` — don't force it
   into a narrative because you assume the source usually posts that way.
2. **Wire-style/neutral reporting is common even from ideological outlets.** A bare factual report
   ("X missile struck Y") with no evaluative framing should be marked
   `neutral_or_no_clear_narrative = True` even if the phrasing or topic makes you suspect a
   particular side — judge only what's actually written.
3. **Spam/placeholder text**: empty posts, bot referral links, channel-seizure notices, or
   nonsensical fragments → `neutral_or_no_clear_narrative = True`, with a note.
4. **Cross-language artifacts**: some texts have stray non-English words leaking in — if this
   makes the framing unclear, note it and judge what you can still read.
5. **Western specifically — use this checklist** (full reasoning in
   `docs/narrative_definitions.md` "final operational definition"): being published by a
   well-known outlet is NOT enough by itself.
   1. States an official government/IGO position/decision/policy (sanctions, aid, condemnation,
      treaty) → **Western**.
   2. Explicit alliance/bloc-solidarity or rules-based-order framing (from any speaker, including
      think tanks) → **Western**.
   3. Partisan/nationalist rhetoric with no institutional-position content → do not default to
      Western; consider `ambiguous_flag = True`.
   4. Plain wire reporting / human-interest / culture / trivia → **not** Western, mark
      `neutral_or_no_clear_narrative = True`.

## Ambiguous/edge cases

If a text is a bare factual news report with no evaluative framing at all, and you genuinely
cannot tell which narrative (if any) it expresses, mark `ambiguous_flag = True` with
`confidence = 1`, or `neutral_or_no_clear_narrative = True` if it truly reads as free of any
framing. Don't guess based on writing style or platform conventions you think you recognize —
judge only the text in front of you.

## Second annotator (inter-annotator agreement)

100 of the 300 rows (stratified across the 7 narratives, ~14-15 each) are annotated independently
by a second reviewer via the `_second_annotator_subset.csv` file, using the exact same
instructions above. Neither annotator sees the other's answers or the original label while
annotating. After both are complete, `analyze_human_validation.py` computes raw agreement,
Cohen's kappa, per-narrative agreement, agreement-by-confidence, and a confusion matrix between
the two annotators — this is the basis for judging how reliable a single annotator's judgment is
before trusting the full 300-row comparison against the original labels.

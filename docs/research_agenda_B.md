# Research Agenda B: Dataset and Methodology Novelty

Scope: publishable directions that reuse only the existing corpus (16,510 rows:
10,330 human-authored, 3,453 Twitter plus 6,877 Telegram; 6,180 synthetic, 5,600
Gemini plus 580 GPT) and existing audit outputs. No new scraping, no new data
collection. Design only; each direction is actionable on artifacts already in
the repo.

Source artifacts (all verified present):

- `artifacts/experiments/narrative_audit/label_quality_per_text.csv`,
  `label_quality_narrative_summary.csv`, `label_quality_account_flags.csv`
- `artifacts/experiments/narrative_audit/matched_event_candidates_full.csv`
  and `matched_event_candidates_summary.csv`
- `data/annotation/human_validation_pilot_300_blind.csv` (300 rows, blind),
  `human_validation_pilot_300_blind_second_annotator_subset.csv` (100-row
  stratified overlap), `human_validation_pilot_300_key.csv`
  (annotation_id to provenance label map), `docs/NARRATIVE_ANNOTATION_GUIDE.md`
- `data/candidates/v2_pilot/matched_event_pilot.csv`
- `artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json`
  (14 frozen authors, 2 per narrative)

Context: `docs/label_quality_audit.md` established that (a) two accounts are
high-confidence removals (`OpenSourceIntel`, 200 Zionist-labeled rows of
off-topic conspiracy content; `ResistanceNewsNetwork`, 2 rows of IDF seizure
placeholder text), (b) Russian (12.4%) and Ukrainian (11.3%) have the highest
heuristic cross-narrative mismatch rates, (c) the keyword heuristic itself has
low recall (2 to 29% strongly-aligned rates even on genuinely ideological
accounts, with `TheEpochTimes` as the documented false-negative control), so
all heuristic flags require blind human corroboration before any label action.
The negative-result arc (EXPERIMENTS.md Sections 18 to 28) showed that
unseen-author generalization fails and that neither entity masking nor style
normalization fixes it. A plausible contributor, never yet isolated, is label
noise: if provenance labels partly encode account identity rather than
text-level framing (Section 27 showed within-narrative author prediction far
above chance), then part of the "generalization gap" may be evaluation against
noisy labels rather than model failure. These three directions test exactly
that, and convert the audit from a cleanup chore into publishable methodology.

---

## Direction B1: A label-noise-aware benchmark for narrative classification

**Hypothesis.** A nonzero share of provenance (account-level) labels is not
supported by text-level framing, and model rankings on the standard random
split differ from rankings on the human-validated clean stratum. Concretely,
removing or stratifying human-confirmed noisy rows (off-topic, neutral wire
copy, spam/placeholder) changes per-narrative recall by an amount comparable
to the modeling interventions already tried and failed (Sections 23, 24, 28),
which would reattribute part of the reported generalization gap from model
weakness to benchmark noise.

**Protocol (concrete slices, existing data only).**

1. Complete the frozen blind pilot: annotator 1 finishes all 300 rows of
   `human_validation_pilot_300_blind.csv` under
   `docs/NARRATIVE_ANNOTATION_GUIDE.md`; annotator 2 independently completes
   the 100-row stratified overlap
   (`human_validation_pilot_300_blind_second_annotator_subset.csv`, about 14
   to 15 rows per narrative). Neither annotator sees provenance labels.
2. Join to provenance labels via `human_validation_pilot_300_key.csv` only
   after both annotations lock. Compute per-narrative provenance support
   rates (share of rows where blind text-level judgment matches the
   account-derived label), with the 100-row overlap scored first for
   inter-annotator reliability.
3. Adjudicate disagreements by a fixed rule written before the join (for
   example: confidence-3 agreement wins; residual ties go to a third blind
   read of that row only). Emit three frozen strata over the 300 rows:
   `clean` (blind agrees with provenance), `neutral` (blind marks
   `neutral_or_no_clear_narrative`), `ambiguous_or_mismatched` (blind picks a
   different narrative or flags `ambiguous_flag`).
4. Cross-reference the strata with the heuristic audit:
   `label_quality_per_text.csv` (does heuristic `potentially_mismatched`
   predict human-confirmed mismatch, especially the Russian/Ukrainian pair?),
   plus the five manually reviewed accounts (`OpenSourceIntel`,
   `ResistanceNewsNetwork`, `OneAmericaNews`, `Readovka`, `TheEpochTimes`) as
   fixed calibration points the strata must reproduce (removals confirmed,
   controls kept).
5. Evaluation: score every existing trained checkpoint (Sections 20, 25, 28
   reuse, no retraining required for v1) separately on `clean` versus full,
   and retrain once with `neutral` rows excluded per the audit Section 5
   policy proposal, comparing against the provenance-only baseline on the
   frozen 14-author confirmatory set.

**Annotation plan.** No new sampling. Finish the in-flight 300 plus 100 design
(estimated residual work: annotator-1 completion plus full annotator-2 pass,
both blind, same guide). Budget a third-reader adjudication pass capped at
disagreement rows only (expected minority if kappa is acceptable; see
falsification). All outputs versioned as new frozen CSVs alongside the pilot,
never overwriting the blind files.

**Metrics.** Inter-annotator raw agreement and Cohen's kappa overall,
per-narrative, and by confidence (3/2/1); per-narrative provenance support
rate with exact binomial confidence intervals; heuristic-to-human precision
for `potentially_mismatched`; model accuracy and macro-F1 on `clean` versus
full pilot; rank-stability of checkpoints across strata (Spearman rank
correlation); per-narrative recall deltas from excluding `neutral` rows.

**Falsification criteria.** If inter-annotator kappa on the 100-row overlap is
below 0.4 (fair or worse), the blind protocol is unreliable and no benchmark
claims follow; the finding is then about annotation-guide vagueness, and the
guide must be revised before any cleanup policy is applied. If
per-narrative provenance support exceeds 90% in all 7 narratives, label noise
is too small to matter and B1 reduces to a validation note rather than a new
benchmark. If model rankings on `clean` versus full are identical (rank
correlation near 1.0) and exclusion of `neutral` rows moves macro-F1 by less
than 1 point, noise does not confound evaluation and the generalization gap
stands as a pure modeling problem.

**What new knowledge this yields beyond the current audit.** The audit gives
heuristic flag rates plus five hand-checked accounts; it cannot say whether
noise changes any modeling conclusion. B1 converts that into a measured,
human-grounded noise-stratified benchmark: per-narrative support rates with
error bars, a validated mapping from cheap heuristic flags to expensive human
judgments (do future audits need 300 blind rows, or does the mismatch flag
suffice for the Russian/Ukrainian pair?), and a quantitative answer to
whether the Sections 18 to 28 gap survives clean-label evaluation. That is a
methods contribution reusable by any distant-supervision narrative dataset,
not just this corpus.

---

## Direction B2: Matched-event cross-narrative evaluation (topic-controlled benchmark)

Cross-pointer: B2 owns the matched-event benchmark defined below, while research_agenda_A.md Direction 1 consumes it for entanglement analysis. See research_agenda_A.md Direction 1 for the consumer; B2 here is the benchmark definition both directions link to.

**Hypothesis.** Random-split accuracy partly reflects topic priors (which
events each narrative's accounts happened to cover) rather than framing
understanding. When narratives are compared on the same event in the same
time window, accuracy drops relative to the random split and cross-narrative
confusion concentrates on the empirically closest pairs (Russian/Ukrainian
first, per the 11 to 12% heuristic mismatch rates and
`docs/narrative_definitions.md` confusion notes).

**Protocol (concrete slices, existing data only).**

1. Build the eval-only benchmark from the audit's two 7/7 shortlisted events
   (`us_politics_trump_2026-03`, all 7 narratives at 10 to 92 texts and 2 to
   3 authors each; `iran_2026-03`, all 7 narratives, Western borderline at 9
   texts) mined from `matched_event_candidates_full.csv`, human-authored rows
   only. Hold out every benchmark row from all training sets (author- and
   event-disjoint by construction: filter training rows by event topic and
   month, not just by author).
2. Add the two narrower events as secondary suites once the primary pair
   validates: `israel_hezbollah_gaza_2026-03` (5 narratives, 13 to 279 texts
   each) and `russia_ukraine_2026-02` (Russian 70/2, Ukrainian 99/2, Western
   23/2, the only war-centered suite).
3. Annotation: blind-validate a stratified sample of benchmark rows for
   (a) event membership (is this text actually about the event?) and
   (b) framing presence (does it carry narrative framing, or is it neutral
   wire copy per the annotation guide?), reusing the B1 annotator pool and
   guide with an added event-membership checkbox. Rows failing (a) are
   dropped from the suite; rows failing (b) move to a reported `neutral`
   stratum rather than silently counting as errors.
4. Score all existing checkpoints (Sections 20, 25, 28) on the frozen suites
   with zero retraining for v1; the optional v2 retrains once with benchmark
   events excluded from training to test whether topic leakage inflated the
   published random-split numbers.

**Annotation plan.** Bounded: a stratified sample (target about 20 rows per
narrative per primary event, about 280 rows total, blind, dual-read on a
50-row overlap for kappa continuity with B1). No new corpus sampling beyond
rows already shortlisted in `matched_event_candidates_full.csv`.

**Metrics.** Per-event accuracy and macro-F1 versus the same checkpoints'
random-split scores (the topic-control gap); per-event 7-way confusion
matrices with closest-pair confusion rates (Russian/Ukrainian,
Western/Ukrainian, Left-wing/Resistance); author-diversity sensitivity (does
the gap persist when restricted to multi-author narratives); neutral-stratum
rate per event (how much of each suite is actually frameless reporting).

**Falsification criteria.** If per-event macro-F1 matches random-split
macro-F1 within 2 points on both primary events, topic priors do not inflate
reported accuracy and the matched-event suite is redundant with the random
split (publish as a null result with the suites released for reuse). If the
confusion concentrates on pairs other than the audit-predicted ones with no
interpretable pattern across both events, the "closest-pair" claim fails and
only the aggregate gap stands. If more than 40% of either primary suite is
adjudicated non-member or neutral, the mining precision is too low and the
suites must be rebuilt with tighter windows before any model comparison.

**What new knowledge this yields beyond the current audit.** The audit
shortlists candidate events with text/author counts but builds nothing and
tests no claim. B2 turns the shortlist into the first topic-controlled
evaluation for this narrative taxonomy, disentangling "knows the framing"
from "knows who covers what." It also directly extends the negative-result
arc: Sections 18 to 28 tested unseen authors without controlling topic, so
an author gap and a topic gap are currently confounded. Matched events break
that confound, which determines whether future work should pursue
author-robust or topic-robust methods.

---

## Direction B3: Synthetic-versus-human gap study (does synthetic augmentation help or hurt?)

**Hypothesis.** The 6,180 synthetic rows (balanced: 800 per narrative Gemini,
about 83 per narrative GPT) are cleaner and more separable than the 10,330
human rows (imbalanced: 994 Western to 1,882 Russian; account-concentrated,
with documented off-topic and spam rows), so mixed training inflates
in-distribution accuracy while contributing little or nothing to human-only
unseen-author generalization. The predicted signature: synthetic-only
training scores high on synthetic-held-out but poorly on human-held-out, and
human-only training matches or beats mixed training on the frozen 14-author
confirmatory set and the B1 `clean` stratum.

**Protocol (concrete slices, existing data only).**

1. Three training conditions on identical architecture and splits, differing
   only in training rows: human-only (10,330), synthetic-only (6,180),
   mixed (16,510 as today). All conditions share one fixed human-only test
   partition (random split over the human rows) plus a fixed synthetic-only
   test partition, so every condition is evaluated on both distributions.
2. Generalization probes with no retraining beyond the three conditions:
   the frozen 14-author confirmatory set (human authors only), the B1
   `clean` stratum, and the B2 matched-event suites. This reuses Sections 25
   and 28 infrastructure with training composition as the single varied
   factor.
3. Characterization (no new labels): per-narrative separability proxies
   computable from existing artifacts, including heuristic
   `strongly_aligned` rates on synthetic versus human rows (expect synthetic
   to score higher if it uses more explicit framing markers), length and
   marker-diversity statistics, and the Section 27 within-narrative
   author-predictability test rerun with synthetic rows included (synthetic
   rows have no author, so they should dilute the author signature if the
   signature is human-account-specific).
4. Annotation: none new. B1's blind strata serve as the human-quality
   reference (are synthetic rows judged `confidence = 3` at higher rates
   than human rows under the same guide? scoreable from the pilot only if
   synthetic rows were sampled into it; otherwise report as a designed
   follow-up using already-generated synthetic rows, still no new
   collection).

**Annotation plan.** Zero new annotation for v1; B3 consumes B1 and B2
outputs. Any synthetic blind-reading follow-up reuses frozen generated rows
and the locked annotation guide.

**Metrics.** For each condition: accuracy and macro-F1 on human-only test,
synthetic-only test, confirmatory authors, B1 `clean`, and B2 suites (a 3 by
5 matrix); per-narrative recall deltas between mixed and human-only training
(which narratives gain or lose from synthetic data, with Western as the
predicted largest mover since it is the smallest human narrative at 994
rows); human-to-synthetic transfer ratio (human-test over synthetic-test
score) as the headline portability number; Section 27 author-signature F1
with and without synthetic rows in training.

**Falsification criteria.** If mixed training beats human-only training on
the human-only test AND on the confirmatory author set by more than 2 points
macro-F1, synthetic augmentation genuinely helps and the hypothesis is
wrong; the result becomes a positive synthetic-data finding with the
per-narrative breakdown showing where. If synthetic-only training matches
human-only training on human-held-out within 2 points, the distributions are
functionally interchangeable for this task and the gap study collapses to a
cost argument (synthetic is cheaper). If removing the two confirmed-bad
accounts (`OpenSourceIntel` 200 rows, `ResistanceNewsNetwork` 2 rows)
changes the human-only baseline more than adding or removing all 6,180
synthetic rows does, label noise dominates data-source effects and B3
defers to B1.

**What new knowledge this yields beyond the current audit.** The audit never
compares synthetic and human rows; `data/README.md` documents their
provenance and counts but says nothing about interchangeability. Yet over a
third of the training corpus (6,180 of 16,510) is synthetic, so every
published accuracy number silently depends on the assumption that synthetic
framing stands in for human framing. B3 tests that assumption with a
controlled 3-by-5 evidence matrix, yielding either a caution (synthetic
inflates in-distribution scores without transferring) or a validated
augmentation recipe (which narratives benefit, by how much, on which
evaluation). Either outcome is publishable and directly informs the
"more data second" half of the audit's clean-labels-first sequencing.

---

## Sequencing and shared dependencies

B1 comes first: its strata (`clean`/`neutral`/`ambiguous_or_mismatched`) and
its kappa gate are inputs to B2 (framing-presence judgments) and B3
(human-quality reference). B2 and B3 are independent of each other once B1
lands and can run in parallel. Total new annotation is bounded: finish the
300 plus 100 pilot (B1), about 280 event-validation rows (B2), zero (B3 v1).
No new scraping, no new generation, no corpus mutation until B1 adjudication
locks; the audit Section 5 cleanup policy (including the `Unclear/Neutral`
label and the two account removals) is the consumer of these results, not
their prerequisite.

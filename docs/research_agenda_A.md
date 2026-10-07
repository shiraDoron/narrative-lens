# Research Agenda A: Shortcut-Learning Follow-ups to the Negative-Result Arc (§18-§28)

Status: pre-registered proposals only. No results are claimed. Each direction below is
grounded in measured failures from EXPERIMENTS.md §§18-28 and framed as a falsifiable
protocol that could be run on this repo's 16,510-text corpus and author-stratified
evaluation machinery. Related-work bucket numbers in novelty claims refer to the four
buckets of `docs/related_work.md`: (1) narrative/framing classification, (2) cross-author
and domain generalization, (3) entity/style shortcuts and de-biasing, (4) topic modeling
for ideology (BERTopic vs LDA).

## Shared premises (all numbers traceable to EXPERIMENTS.md)

- P1 (§18): LOAO recall drops 20-38pp vs random-split per-narrative F1 (IDF 53.5% vs
  0.7354; MariaZakharova 31.0% vs 0.6930; BernieSanders 28.0% vs 0.6231). Maria (57.5%)
  and Bernie (50.0%) misroute specifically to Right-wing. NER module weight stays 44-47%
  across runs, so the gap is not a module-reweighting artifact.
- P2 (§25): on 14 frozen fresh authors (2 per narrative, seed 42; 12 with n=200 plus PressTV (n=400) and NATO (n=209), totaling 12x200+400+209=3009 test examples), the Section 24
  selective-masking candidate scores mean recall 37.1% vs baseline 39.0% and median 32.7%
  vs 38.8%. NON-INFERIOR is FALSE on the median condition alone (32.7% vs the 35.8% bar,
  a 3.1pp shortfall against the 3pp margin (bar 35.8%, candidate median 32.7%; the 6.1pp figure is the gap to the baseline median 38.8%, not to the bar)). The guardrail passes (1/14 authors degrade
  more than 10pp) but mean dominant-error concentration is not reduced (45.8% vs 44.2%).
- P3 (§27): author identity is recoverable from 28 surface features far above baselines,
  including within a fixed narrative (global 47.3% vs 4.0% majority and 2.0% chance on
  50 authors and 10,091 rows; within-narrative best cases Western 85.1%, Left-wing 81.5%,
  Russian 76.0%, Right-wing 71.9%, Resistance 68.3%, Ukrainian 56.9%, Zionist 48.3%).
  Top features are style and formatting (length, punctuation, URL/mention/hashtag counts),
  not semantic content.
- P4 (§28): deterministic style normalization measurably strips author signal (global OOF
  accuracy -9.70pp; per-narrative macro-F1 down in 6/7 narratives, Right-wing worst at
  -18.33pp, Zionist the lone exception at +3.24pp) yet fresh-author recall gets worse for
  13/14 authors (mean -6.40pp, median difference -10.8pp (difference of group medians; median of paired per-author deltas is -2.1pp, see docs/figures.md); worst case BringThemHomeNow -29.5pp; only
  @MiddleEastEye_TG improves, +0.5pp), while random-split macro-F1 stays inside the 3pp
  non-inferiority margin (-2.57pp). Removing style signal hurts generalization instead of
  helping it.
- P5 (§26): per-example error prediction under author-grouped cross-validation never beats
  the 59.9% majority baseline (depths 3/4/5 score 56.7%/57.3%/59.0%), so the failure is
  author-global and diffuse rather than decomposable into a few per-example features.
- P6 (§§19-21): shortcut effects are author-dependent, not uniform. Soft topics cut
  Right-wing misrouting (avg 20.8% to 16.7%, Bernie 57.5% to 46.0%) without beating
  SBERT-only on mean recall (§§19-20); full entity masking helps Bernie (recall 24.5% to
  30.5%, Right-wing rate 57.5% to 42.0%) but hurts IDF (63.5% to 38.5%) and MariaZakharova
  (89.5% to 76.5%) (§21).

## Direction 1: Measuring content-style entanglement with matched-event counterfactuals

**Hypothesis.** Author style and narrative content are entangled in this corpus (P3, P4):
the surface features that identify authors also carry narrative-discriminative content
signal (outlet conventions, event selection, framing vocabulary), so naive removal
destroys signal the classifier needs. Concretely: the LOAO recall gap (P1) will be
substantially smaller for author pairs covering the *same real-world event* than for
random cross-author pairs, because holding content constant isolates the pure style
penalty from the content-shift penalty.

**Protocol.**
- Splits: reuse the 43-author eligible pool (≥200 examples each, §25) from the 16,510-text
  corpus. Build matched-event strata by pairing texts about the same event across authors
  (same BERTopic soft-topic top-1 plus overlapping 7-day posting window, verified by manual
  inspection of a 100-pair sample before freezing). Target at least 20 matched events with
  ≥2 authors each and ≥30 texts per author-event cell (power note: with per-cell n≥30,
  a 10pp recall difference is detectable at roughly the same resolution as the §25 3pp
  non-inferiority margin aggregated over 14 authors).
- Controls: (a) event-matched LOAO (train on author A covering event E, test on author B
  covering E) vs (b) event-mismatched LOAO (same author pair, disjoint events) vs
  (c) the §25 frozen-14 LOAO as the unmatched reference. Same `AblationDetector` (SBERT-only)
  architecture, hyperparameters, and seed 42 as §§20/25 throughout.
- Counterfactual evaluation: paraphrase-based style transfer that holds event content fixed
  (entity-preserving paraphrase of each test text, author markers removed by construction
  rather than by the §28 token rules); measure recall change on paraphrased vs original
  test sets within each stratum.
- Metrics: true-narrative recall per stratum (mean, median, IQR, worst-author, as in §25);
  dominant-error concentration (§25 secondary endpoint); paraphrase-induced recall delta
  with the §25 3pp non-inferiority margin applied symmetrically.

**Falsification criteria.** The entanglement hypothesis is rejected if (a) event-matched
LOAO gaps are no smaller than event-mismatched gaps (difference < 3pp in both mean and
median across strata), or (b) content-preserving paraphrase changes fresh-author recall
by less than 3pp in either direction while §28-style token normalization still costs
≥6pp, which would imply the §28 damage comes from token-distribution shift rather than
from entangled content signal.

**Novelty.** Buckets (2) and (3) survey generalization gaps and removal-based de-biasing
(masking, normalization), which this repo already tried and closed as negative (P2, P4).
No removal is proposed here. The contribution is a *measurement design* (matched-event
stratification plus content-fixed counterfactuals) that quantifies how much of the LOAO
gap is content shift vs style shift, a decomposition §§18-28 never performed. It converts
the §28 puzzle (signal removed, performance worse) from a dead end into an estimand.

## Direction 2: Per-instance causal attribution of entity shortcuts via counterfactual swaps

**Hypothesis.** Entity identity is causally relevant content for some author-narrative
pairs (IDF, MariaZakharova: removing entities destroys recall, P6) and a spurious
attractor for others (BernieSanders: removing entities cuts Right-wing misrouting, P6).
Uniform train-time masking therefore cannot work (P2), because the average causal effect
of entity identity has opposite signs across instances. A test-time counterfactual
measurement can separate the two cases per instance before any training intervention is
attempted.

**Protocol.**
- Splits: the §25 frozen 14 authors (3,009 test examples) as the confirmatory test bed,
  with the §18 original 3 authors (IDF, MariaZakharova, BernieSanders) as hypothesis
  generators only. No new training in the confirmatory phase; reuse frozen `sbert_original`
  checkpoints (§25), so this is a pure measurement on fixed models.
- Controls: for each test example, generate (a) same-type cross-narrative entity swaps
  (replace each PER/ORG/LOC with a frequency-matched entity of the same type drawn from a
  different narrative's training data), (b) same-narrative entity swaps (placebo control:
  identity changes but narrative association is preserved), and (c) §21-style generic
  placeholder masking (reference arm). All swaps use the §24 `mask_entities` implementation
  extended with a frozen entity gazetteer built from train splits only.
- Metrics: per-instance prediction-flip rate for (a) vs (b); average causal effect (ACE)
  of cross-narrative identity on the predicted narrative; correlation between per-author
  ACE magnitude and that author's LOAO recall gap (P1) and §25 recall delta; Right-wing
  attractor flip rate specifically (fraction of Bernie/Maria-type misroutes corrected by
  the swap). Sample size: 3,009 examples gives ±1.8pp binomial resolution on global flip
  rates and ±5pp per-author resolution at n=200 (PressTV n=400, NATO n=209 as frozen).
- Pre-registration: fix the gazetteer, swap counts (3 swaps per example per arm), and the
  3pp materiality threshold before running; reuse §25 non-inferiority logic (mean and
  median across the 14 authors, ≤20%-of-authors guardrail) for any claim that an
  attribution-guided selective policy preserves recall.

**Falsification criteria.** The hypothesis is rejected if (a) cross-narrative swaps and
same-narrative (placebo) swaps produce flip rates within 3pp of each other, meaning the
model is insensitive to entity identity rather than shortcutting on it; or (b) per-author
ACE shows no rank correlation with per-author LOAO gaps (Spearman < 0.3), meaning entity
causality does not explain the author-dependence in P6; or (c) the swap-corrected
Right-wing attractor rate is unchanged (±3pp) for the authors where §21 masking helped,
meaning the attractor is not entity-driven at all.

**Novelty.** Bucket (3) covers training-time de-biasing (masking augmentation), which §§21-25
exhausted to a confirmatory negative (P2). This direction inverts the approach: test-time
causal measurement with a placebo-controlled swap design, producing per-instance
attribution scores instead of another uniform training policy. It is also distinct from
bucket (4): topic representations (§§19-20) are held fixed as background while entity
identity is the manipulated variable. A publishable output is an attribution method plus
the finding that shortcut sign varies by instance, which explains *why* P2 failed.

## Direction 3: Author-stratified evaluation as the primary benchmark (methods contribution)

**Hypothesis.** Random-split accuracy (≈67% for `baseline_fusion`, ≈73% for SBERT-only
per `docs/results.md`) is inflated by author leakage and misranks modeling choices
relative to author-stratified evaluation: interventions that look neutral or positive on
random splits (soft topics tied with hard at -0.03pp, §20; normalization non-inferior at
-2.57pp, §28 Part B) are negative under LOAO. An author-stratified benchmark with
pre-registered non-inferiority rules should therefore replace random-split reporting as
the primary model-selection criterion for narrative classification.

**Protocol.**
- Splits: formalize the §25 design into a reusable benchmark over the 43-author eligible
  pool (≥200 examples each): frozen uniform sampling of 2 authors per narrative at seed 42
  (the existing 14-author set ships as version 1.0 of the benchmark), LOAO training per
  author with the §25 architecture and hyperparameters fixed, plus the §18 3-author set
  retained as a documented development split that must never be used for confirmatory
  claims (anti-contamination rule derived from §§19-24 being test-informed).
- Controls: every candidate model reports both random-split (3 seeds, 42/7/123, as in
  §§20/28) and author-stratified results side by side; model selection uses the
  stratified numbers. Include the §26 grouped-CV requirement (group by author, never
  plain random folds) as a reporting rule, motivated by P5.
- Metrics (all pre-registered, inherited from §25): mean, median, IQR, and worst-author
  true-narrative recall across the 14 authors; 3pp non-inferiority margin on mean AND
  median; ≤20%-of-authors-with->10pp-degradation guardrail; mean dominant-error
  concentration as the robustness endpoint. Publish the frozen author set, seeds, and
  per-author caches (`fresh_author_confirmatory_set.json` pattern) as versioned artifacts.
- Sample sizes: benchmark v1.0 is exactly the §25 scale (14 authors, 3,009 test examples);
  benchmark v2.0 extends to all 43 eligible authors without changing rules, giving
  per-narrative resolution of 6 authors each instead of 2.

**Falsification criteria.** The methods claim is rejected if (a) model rankings under
random-split and author-stratified evaluation agree (same pairwise winner in at least
4 of 5 candidate comparisons, e.g. the §20 hard/soft/LDA/none set plus the §28
normalized variant), meaning stratification adds no decision-relevant information; or
(b) the stratified benchmark's own test-retest reliability fails (re-frozen author sets
at two additional seeds produce mean-recall rankings that disagree on the top model),
meaning the benchmark measures sampling noise rather than generalization.

**Novelty.** Buckets (1) and (2) survey narrative classifiers and generalization-aware
evaluation, but this repo's distinctive asset is a fully worked negative-result arc with
frozen artifacts: a pre-registered 14-author confirmatory protocol (P2), a grouped-CV
anti-leakage lesson (P5), and side-by-side random vs LOAO rankings for six model
variants (§§18-28). The contribution is methodological infrastructure (benchmark plus
reporting standard with margins and guardrails), not another model or de-biasing trick,
and it is directly reusable by anyone working on the 7 narratives in this corpus. It
turns the arc's painful lesson (random-split numbers mislead) into the paper's central
artifact.

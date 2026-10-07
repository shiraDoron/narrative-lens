# Experiments Log

This document consolidates all experiments actually run on the BERTopic topic-modeling
pipeline (`saved_topic_model_soft_v2`) and its supporting preprocessing/analysis tooling. It
covers only work that was actually executed and measured (not proposals that were never run).

Scope note: none of these experiments touched `fusion.py`, `train.py`, `config.py`'s narrative
classifier, `models/saved_topic_model` (the legacy/pinned model used by the trained
classification checkpoints), or any `.pth` checkpoint. All of them operate on the topic model
used for soft/multi-topic scoring (`models/saved_topic_model_soft_v2`) or on read-only corpus
analysis, and every risky change was first validated on a separate path before ever touching
`saved_topic_model_soft_v2` itself.

All BERTopic configurations described below start from library defaults unless a change is
explicitly called out: `embedding_model="sentence-transformers/all-MiniLM-L6-v2"`, default UMAP
(`n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine"`, no `random_state` unless noted),
default HDBSCAN (`min_cluster_size=min_topic_size`, `metric="euclidean"`,
`cluster_selection_method="eom"`), default `CountVectorizer()` (no stopwords, unigrams only),
default `ClassTfidfTransformer(bm25_weighting=False, reduce_frequent_words=False)`, and
`representation_model=None` (label = single top c-TF-IDF word).

---

## 1. Soft (multi-topic) clustering added to BERTopic

**Files:** [src/narrative_lens/topic_modeling/stance.py](src/narrative_lens/topic_modeling/stance.py), [src/narrative_lens/evaluation/analyze_soft_topics.py](src/narrative_lens/evaluation/analyze_soft_topics.py)

**Goal:** Give the existing BERTopic pipeline the ability to return more than one topic per text
(a probability distribution over topics), without touching `fusion.py`/`train.py` or breaking the
already-trained classification checkpoints.

**What we changed:** Added `TopicAnalysisPipeline.get_topic_distribution(text, top_n=3)`, using
BERTopic's `approximate_distribution()` (chosen over `calculate_probabilities=True` because it
works read-only on an already-fit model with no expensive HDBSCAN posterior recompute, and needs
no refit-time flag). Added `process_text_with_distribution()` as a convenience wrapper, and a new
standalone demo/CLI `analyze_soft_topics.py` that prints dominant + top-N soft topics for sample
texts and writes `reports/results/profiler_prototype/soft_topic_examples.csv`. `process_text()` (used by
the classifier pipeline) was left fully unchanged.

**Baseline:** No soft/multi-topic capability existed before this; only a single hard `topic_id`
per text (via `process_text()`).

**Data/sample:** Small manual smoke test (~300 texts) to validate the mechanism, then the full
16,510-text corpus (all 4 natural datasets: twitter/telegram/gemini/gpt) once a real BERTopic
re-fit was performed (see below).

**Metrics before/after:** Not a metric-driven experiment — this step only added the *capability*.
The re-fit performed to enable it changed topic count 369 → 310 and outlier count 6,493 → 5,786
(out of 16,510 docs).

**Qualitative findings:** `approximate_distribution()` only works if the saved model retains a
fitted `vectorizer_model.vocabulary_`/`c_tf_idf_` — this requires `save_ctfidf=True` at save time
(see Experiment 2 below); without it, it raises `NotFittedError`.

**Conclusion:** The mechanism works and produces real, re-normalized top-N soft distributions
(e.g. topic_10 "tax" 0.45 / topic_118 "wealth" 0.38 / topic_165 "inflation" 0.16 for a wealth-tax
example).

**Decision:** Adopted as new tooling. However, re-fitting BERTopic to add this capability
non-deterministically renumbers all topic ids, which would silently invalidate the
already-trained classification checkpoints' learned `topic_id → narrative` associations (see
Experiment 2 for how this was contained).

---

## 2. Model-versioning split + the `save_ctfidf=True` fix

**Files:** [src/narrative_lens/topic_modeling/stance.py](src/narrative_lens/topic_modeling/stance.py), [src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py), [src/narrative_lens/config.py](src/narrative_lens/config.py)

**Goal:** Fix the `NotFittedError` blocking soft clustering, and prevent the underlying BERTopic
re-fit (needed to get a ctfidf-saved model) from corrupting the topic ids relied upon by existing
trained checkpoints.

**What we changed:**
- Confirmed that `approximate_distribution()` requires `.save()` to have been called with
  `save_ctfidf=True` (in addition to `serialization="safetensors"`).
- Since a re-fit needed to produce the first ctfidf-saved model, and BERTopic re-fits
  non-deterministically renumber topic ids, split the topic model into two permanently separate
  artifacts: `models/saved_topic_model` (pinned legacy model, byte-restored to the exact state
  the classifier checkpoints were trained against — 369 topics, no ctfidf, soft scoring
  unavailable by design) and `models/saved_topic_model_soft_v2` (the new re-fit, 310 topics, saved
  with `save_ctfidf=True`, used only for soft scoring, not consumed by any classification
  checkpoint).
- Added `TOPIC_MODEL_PATH_LEGACY` / `TOPIC_MODEL_PATH_SOFT` constants to `config.py`;
  `TopicAnalysisPipeline.__init__` gained a `model_path` parameter defaulting to the legacy path
  (so all existing callers are unaffected by default).

**Baseline:** Before the fix, there was no ctfidf-saved BERTopic model at all — soft scoring was
architecturally impossible regardless of code, and the only existing model
(`models/saved_topic_model`, 369 topics) was the sole artifact in use by both the classifier and
any future soft-clustering work, creating a real risk of silently corrupting trained checkpoints
if it were ever overwritten.

**Data/sample:** Full 16,510-text corpus (fit performed once during this session).

**Metrics before/after:** Topic count 369 → 310, outlier count 6,493 → 5,786 (this is the same
re-fit noted in Experiment 1 — a real renumbering, not just an additive save-format change).

**Qualitative findings:** After `BERTopic.load()`, `tm.umap_model`/`tm.hdbscan_model` become stub
placeholder objects — the true fit-time UMAP/HDBSCAN parameters are not recoverable from a saved
model and must be read from the script that built it. This became relevant for every later
experiment's reproducibility.

**Conclusion:** The two-path split fully isolates soft-clustering work from the classifier's
frozen dependency, at the cost of maintaining two BERTopic artifacts going forward.

**Decision:** Adopted permanently. `models/saved_topic_model` must never be re-fit in place;
`train_topics.py` now saves to `models/saved_topic_model_soft_v2` by default. Verified after the
split: the legacy pipeline still returns the same topic id (347) for a fixed regression sentence,
and `analyze_soft_topics.py` (pointed at soft_v2) produces real normalized distributions.

---

## 3. Preprocessing for URLs / mentions / hashtags (+ bare shortlinks)

**Files:** [src/narrative_lens/topic_modeling/topic_preprocessing.py](src/narrative_lens/topic_modeling/topic_preprocessing.py), [src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py), [src/narrative_lens/topic_modeling/stance.py](src/narrative_lens/topic_modeling/stance.py)

**Goal:** A quality-analysis pass (`analyze_soft_topic_quality.py`, see below) found that raw
Twitter handles and hashtag blobs were leaking into BERTopic as their own junk topics (e.g. a
tweet mentioning `@DDGeopolitics` produced a soft top-1 topic literally labeled "ddgeopolitics",
score 0.51) because `train_topics.py` had no `MENTION_RE`/`HASHTAG_RE` cleaning step before
`BERTopic().fit()`, unlike `analyze_agendas.py`'s existing `clean_text()`.

**What we changed:** Added `URL_RE`, `MENTION_RE = r"@\w+"`, `HASHTAG_RE = r"#(\w+)"`,
`_split_camel_case()`, `clean_text_for_topic_model()` (URL removal → mention removal → hashtag
strip + camelCase split → whitespace normalize) and a `MIN_WORDS_AFTER_CLEAN=3` filter dropping
texts with fewer than 3 real alphabetic tokens after cleaning, applied to the training texts
before `BERTopic().fit()`. Later in the same line of work, a `BARE_SHORTLINK_RE` (explicit
domain allowlist: bit.ly, tinyurl.com, t.co, ow.ly, buff.ly, dlvr.it, goo.gl, is.gd, rebrand.ly)
was added because bare (scheme-less) shortlinks like `bit.ly/4bngYSJ` were not matched by
`URL_RE` and were leaking as literal "bit"/"ly" tokens (root cause of a "bit ly telephone
conversation" artifact found in Experiment 6/C). Finally, this cleaning function was consolidated
into a single shared module (`topic_preprocessing.py`, imported by both `train_topics.py` and
`stance.py`) to guarantee train-time and inference-time text cleaning can never drift apart
again — previously, `stance.py`'s inference path did not apply the same cleaning as training,
a train/inference mismatch bug that was found and fixed in this same effort.

**Baseline:** `saved_topic_model_soft_v2` before cleaning (369→310-topic re-fit from Experiment
2), no `MENTION_RE`/`HASHTAG_RE`/`URL_RE`/shortlink handling at all.

**Data/sample:** Full corpus, 16,510 raw texts → 16,341 after the mention/hashtag/URL cleaning
(169 dropped as empty/near-empty post-clean). Quality re-measured on the same stratified sample
(n=280, 40/narrative, seed=42) used throughout this line of experiments.

**Metrics before → after cleaning:**

| metric | before | after |
|---|---|---|
| topic count (excl. -1), full corpus | 310 | 305 |
| outlier % (full corpus) | 35.0% (5,786/16,510) | 34.0% (5,551/16,341) |
| dominant_single_topic (sample) | 20.7% | 21.4% |
| spread_multi_topic (sample) | 77.1% | 76.8% |
| no_soft_signal (sample) | 2.1% | 1.8% |
| hard/soft top-1 agreement (sample) | 55.0% (154/280) | 56.1% (157/280) |

**Qualitative findings:** The "ddgeopolitics" topic disappeared entirely (0 occurrences
post-clean). The hashtag-blob "bringthemhomenow" topic also disappeared — the hashtag now splits
into real words ("Bring Them Home Now") and contributes to existing word-topics instead of
forming its own topic. All deltas were modest improvements with no regressions.

**Conclusion:** Preprocessing cleanup is a small, unambiguous, low-risk quality win — it removes
concrete junk topics without materially shifting overall clustering structure.

**Decision:** Adopted permanently in `train_topics.py` (feeds `saved_topic_model_soft_v2`); the
legacy model was not touched. The train/inference consistency fix (shared
`topic_preprocessing.py` module, `stance.py`'s `use_cleaned_preprocessing` flag gated on
`model_path != TOPIC_MODEL_PATH_LEGACY`) was also adopted, keeping the legacy pipeline's
behavior byte-identical (verified via the same fixed regression sentence still returning
topic_id 347).

---

## 4. Near-duplicate analysis + retrain test at threshold=0.7

**Files:** [src/narrative_lens/data/text_dedup.py](src/narrative_lens/data/text_dedup.py), [src/narrative_lens/evaluation/analyze_text_duplicates.py](src/narrative_lens/evaluation/analyze_text_duplicates.py), [src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py)

**Goal:** Determine whether corpus duplication was a significant driver of topic-model noise/size,
and whether removing near-duplicates before fitting improves soft-clustering quality.

**What we changed:** Built a MinHash/LSH near-duplicate detector (`text_dedup.py`: word-3-gram
shingling, MinHash k=64, LSH banding b=16/r=4, candidate pairs verified by exact Jaccard, merged
via Union-Find), first as a read-only analysis tool (`analyze_text_duplicates.py`), then wired
into `train_topics.py` as an actual training-time step: `deduplicate_texts(texts_list,
threshold=0.7)` applied in-memory (raw CSVs on disk were never modified) after the
mention/hashtag/URL cleaning and before `BERTopic().fit()`, keeping the lowest-original-index
member of each near-duplicate cluster.

**Baseline:** `saved_topic_model_soft_v2` after preprocessing cleanup (Experiment 3), before any
deduplication — 16,341 cleaned texts, 305 topics, 34.0% outliers.

**Data/sample:** Read-only analysis on the full 16,510 raw texts; the actual dedup+retrain used
the 16,341 cleaned texts. Same stratified quality sample (n=280, seed=42).

**Read-only analysis results (16,510 raw texts, threshold sensitivity):**

| threshold | clusters | texts removed | % of corpus |
|---|---|---|---|
| 0.5 | 357 | 500 | 3.03% |
| 0.6 | 290 | 385 | 2.33% |
| **0.7 (chosen)** | **231** | **288** | **1.74%** |
| 0.8 | 173 | 208 | 1.26% |

Exact duplicates alone: 97 groups, 215 texts (1.30% of corpus), would remove 118. Threshold=0.7
was chosen because inspected examples were genuine paraphrases (not false positives), and going
below 0.6 started risking merges of genuinely-distinct-but-topically-similar opinions.

**Actual retrain (16,341 cleaned texts → 16,063 after dedup at threshold=0.7, 278 removed, 232
clusters):**

| metric | before dedup | after dedup |
|---|---|---|
| topic count (excl. -1), full corpus | 304 | 293 |
| outlier % (full corpus) | 34.0% (5,551/16,341) | 34.0% (5,460/16,063) |
| dominant_single_topic (sample) | 21.4% | 20.0% |
| spread_multi_topic (sample) | 76.8% | 77.1% |
| no_soft_signal (sample) | 1.8% | 2.9% |
| hard/soft top-1 agreement (sample) | 56.1% (157/280) | 53.9% (151/280) |

**Qualitative findings:** All before/after deltas are small (1–3 percentage points) and go in
both directions — consistent with normal BERTopic run-to-run stochastic variance (UMAP/HDBSCAN
were not seeded at this point), not a clear systematic effect. Top co-occurring topic pairs
stayed thematically consistent. A specific hypothesis — that the large "maria/lying" topic (198
docs, from ~187 sarcastic troll-reply tweets to @MariaVladimirovnaZakharova) was a
near-duplicate-text artifact — was investigated and **rejected**: only 2 of 187 texts mentioning
that handle formed a near-duplicate cluster at threshold=0.7; the other 185 are genuinely
distinct texts sharing only a short recurring hashtag/phrase, so BERTopic is clustering them by
embedding similarity, not duplicate content. Dedup does not meaningfully shrink this topic.

**Conclusion:** Corpus duplication is small (~1.3–3% depending on threshold) and removing it at
threshold=0.7 produces changes within normal run-to-run noise — not a measurable, consistent
quality improvement, and not a fix for large thematically-coherent topics like maria/lying.

**Decision:** Kept dedup in `train_topics.py` anyway, as a defensible training-hygiene practice
(prevents templated/boilerplate near-duplicate content from getting outsized influence on
cluster formation) — **not** because it showed a significant metric improvement, and explicitly
not sold as a fix for the outlier rate or hard/soft agreement, which are driven by other factors
(embedding model, HDBSCAN granularity, single-word labels).

---

## 5. Experiment C — topic representation / label-quality improvement

**Files:** [experiments/topic_modeling/experiment_c_representation.py](experiments/topic_modeling/experiment_c_representation.py), [src/narrative_lens/topic_modeling/topic_preprocessing.py](src/narrative_lens/topic_modeling/topic_preprocessing.py) (`build_multiword_label`), [src/narrative_lens/topic_modeling/stance.py](src/narrative_lens/topic_modeling/stance.py) (`get_topic_label` optional `top_n_words`), [src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py) (`load_deduplicated_training_texts` extraction)

**Goal:** Root-cause analysis (grounded in reading the live model + `train_topics.py`, not
guesses) found three independent causes of vague/uninformative topic labels: (a) the default
`CountVectorizer()` has no stopword removal and unigrams only, (b) the default
`ClassTfidfTransformer(reduce_frequent_words=False)` doesn't down-weight cross-topic-frequent
words, (c) `representation_model=None` plus `stance.py`'s `get_topic_label()` only ever showed the
single top c-TF-IDF word. Experiment C tests fixing (a)+(b)+(c) — representation only, no
re-embedding/re-clustering.

**What we changed:** Called `topic_model.update_topics(docs, vectorizer_model=CountVectorizer(
stop_words="english", ngram_range=(1,2)), ctfidf_model=ClassTfidfTransformer(
reduce_frequent_words=True, bm25_weighting=True), representation_model=
MaximalMarginalRelevance(diversity=0.3))` on the *already-fitted* `saved_topic_model_soft_v2`
(cheap — no UMAP/HDBSCAN re-run). Added `build_multiword_label()` to deduplicate repeated tokens
across the top phrases (e.g. "gaza ceasefire gaza humanitarian" → "gaza ceasefire humanitarian").
Result saved to a **separate** path, `models/experiments/soft_v2_expC_representation` —
`saved_topic_model_soft_v2` itself was not touched by this experiment.

**Baseline:** `saved_topic_model_soft_v2` (post-cleaning, post-dedup) with default
vectorizer/ctfidf/representation — single-word labels only.

**Data/sample:** 26 hand-picked topics: 4 previously-flagged vague-label watch-words
(rulesbased ×2 topic ids, call ×2, hard, era), 15 smallest topics, and 5 largest topics
(control group, to check large/good topics don't regress).

**Metrics before/after:** Clustering itself verified 100% unchanged (293 topics before/after,
per-topic document counts byte-identical) — this experiment only changes representation, as
designed, so topic count / outlier % / hard-soft agreement are expected and confirmed unchanged.

**Qualitative findings:**
- Clear wins: "rulesbased"→"based order rules" / "global rules based"; "hard"→"american dream
  work"; "call"→"maintaining control prefer" / "terrorists really land"; "era"→"inevitable like
  era"; several small noisy topics gained real thematic signal (e.g. "korean"→"north korean
  troops", "nato"→"paper tiger bad").
- No improvement on genuinely mixed-content small clusters (e.g. "forum"→"ecclesiastical forum
  arena" stayed word-salad) — representation changes cannot manufacture coherence in a cluster
  that isn't thematically coherent, a clustering-granularity problem instead.
- The two "rulesbased" topics got individually better labels but remained near-duplicates of
  *each other* — label improvement cannot merge/de-duplicate topics; that requires a clustering
  change (motivated Experiment 6).
- Minor artifact found (not fixed here): a leaked `bit.ly` URL-shortener fragment in one topic's
  top bigram, later fixed by the `BARE_SHORTLINK_RE` addition documented in Experiment 3.

**Conclusion:** Representation-only changes clearly and safely improve topic-label
interpretability for the large majority of vague topics, at zero cost/risk to clustering.

**Decision:** Adopted. The improved vectorizer/ctfidf/representation config, plus
`get_topic_label(top_n_words=3)` via `build_multiword_label()`, is the recommended labeling
approach going forward and was carried into all subsequent Experiment A/A2 runs. `stance.py`'s
default (`top_n_words=1`) was left unchanged for full backward compatibility with the legacy
model and any existing caller.

---

## 6. Experiment A — `min_topic_size` sweep (10 / 25 / 35)

**Files:** [experiments/topic_modeling/experiment_a_min_topic_size.py](experiments/topic_modeling/experiment_a_min_topic_size.py), [src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py) (`build_bertopic_model`)

**Goal:** Test whether raising `min_topic_size` (HDBSCAN granularity only, nothing else changed)
fixes the remaining quality issues found in root-cause analysis — most notably the "rulesbased"
duplicate-topic pair and a long tail of tiny (10–12 doc), often-incoherent topics.

**What we changed:** First pinned `UMAP(..., random_state=42)` (BERTopic's default UMAP is
otherwise unseeded, making re-fits non-deterministic and un-comparable) via a new
`build_bertopic_model(min_topic_size, random_state=42)` helper in `train_topics.py` — purely
additive, `saved_topic_model_soft_v2`'s real (unseeded) production training path is untouched.
Built a fresh seeded baseline at `min_topic_size=10` and two sweep points at 25 and 35, each with
Experiment C's representation improvement applied, each saved to its own separate path
(`models/experiments/soft_v2_baseline_seeded`, `soft_v2_expA_mts25`, `soft_v2_expA_mts35`).

**Baseline:** The new seeded `min_topic_size=10` run (`soft_v2_baseline_seeded`) — same
data/preprocessing/dedup as `saved_topic_model_soft_v2`, but with UMAP seeded for a reproducible
comparison point.

**Data/sample:** 16,062 deduplicated, cleaned texts (same corpus for all 3 configs). Quality
sample n=280, seed=42, same as prior experiments.

**Metrics (baseline mts=10 vs. mts=25 vs. mts=35):**

| metric | mts=10 (baseline) | mts=25 | mts=35 |
|---|---|---|---|
| topic count (excl. -1) | 282 | 100 | 50 |
| outlier % | 35.8% (5,750) | 38.1% (6,126) | 27.5% (4,422) |
| avg / median topic size | 36.6 / 25.5 | 99.4 / 58.0 | 232.8 / 100.5 |
| topics ≤15 docs (absolute) | 53 | 0 | 0 |
| topics ≤ own-floor+10 | 98 | 29 | 3 |
| hard/soft agreement (True/False/no-signal) | 86/57/137 | 55/20/205 | 35/11/234 |
| agreement rate among texts *with* a signal | 60.1% | 73.3% | 76.1% |
| % of sample with any soft signal | 51.1% | 26.8% | 16.4% |
| largest single topic | 240 (2.3% of clustered docs) | 911 (9.2%) | 2,523 (21.7%) |
| top-2 topics combined | ~449 (4.4%) | ~1,712 (17.2%) | 5,014 (**43.1%**) |

**Qualitative findings:**
- The duplicate "rulesbased order" topic pair (n=31 + n=18 at baseline) genuinely **merges into
  one topic** at both mts=25 (n=114) and mts=35 (n=318) — confirms raising `min_topic_size` does
  fix this specific over-segmentation problem.
- Some previously-good control topics held up (gaza: 191→171→203; home/bring-home: 209→208→208;
  maria/lying: 195→195→195, with an improved label).
- **Critical negative finding:** severe mega-topic over-merging, worse at higher `min_topic_size`.
  At mts=35, two topics (Iran-related, n=2,523; Russia/Ukraine-military, n=2,491) together
  swallow 43% of all clustered documents — 7+ previously-distinct Ukraine-war sub-topics
  (negotiations, force formations, sanctions package, Kursk, pilots, Wagner, etc., each 25–75
  docs at baseline) collapsed into one undifferentiated blob. The pattern is already visible
  (milder) at mts=25 (top-3 topics = 25% of the clustered corpus). The "telephone conversation"
  control topic disappeared as a standalone topic by mts=35 (absorbed into the mega-topic).
- Smallest-topic quality does genuinely improve with higher `min_topic_size` (more substantial,
  still-coherent small topics) — but this benefit is outweighed by the large-topic collapse.

**Conclusion:** Raising `min_topic_size` trades one real, visible problem (micro-topic
fragmentation and duplicate-topic pairs) for a different, more damaging one (mega-topic collapse
of previously well-differentiated, narrative-relevant content — Iran, Russia-Ukraine military
operations, US politics) — worse at 35 than at 25. This is a serious loss of exactly the topical
granularity a narrative-agenda analysis needs.

**Decision: rejected both 25 and 35.** `min_topic_size=10` (current default) remains the
recommendation. **Why not 25/35:** the hard/soft-agreement and small-topic-fragmentation gains
are real but come at the cost of collapsing distinct major themes into a handful of catch-all
topics, which directly damages the topic model's usefulness for narrative-agenda analysis — a
bigger cost than the problems it would solve. `saved_topic_model_soft_v2` (mts=10) was **not**
changed by this experiment; only the 3 new paths under `models/experiments/` were created.

---

## 7. Experiment A2 — additional sweep point at `min_topic_size=15`

**Files:** [experiments/topic_modeling/experiment_a2_mts15.py](experiments/topic_modeling/experiment_a2_mts15.py)

**Goal:** Experiment A found mts=25/35 too aggressive; test one more conservative point
(`min_topic_size=15`) to see if a smaller granularity increase gets some of the benefits (fewer
tiny topics, better agreement) without the severe mega-topic collapse.

**What we changed:** Reused the exact seeded mts=10 baseline from Experiment A (not refit) and
fit one new config at `min_topic_size=15` (same UMAP `random_state=42`, same Experiment C
representation improvement), saved to `models/experiments/soft_v2_expA_mts15`. Added an "iran"
control theme on top of Experiment A's original 5, and switched control-topic lookup to
substring matching (Experiment A's exact top-3-word match under-reported bigram/MMR-diversified
labels).

**Baseline:** The same seeded `min_topic_size=10` baseline from Experiment A
(`soft_v2_baseline_seeded`).

**Data/sample:** Same 16,062-text corpus, same n=280/seed=42 quality sample.

**Metrics (mts=10 baseline vs. mts=15):**

| metric | mts=10 (baseline) | mts=15 |
|---|---|---|
| topic count (excl. -1) | 282 | 209 |
| outlier % | 35.8% (5,750) | 38.8% |
| avg / median topic size | 36.6 / 25.5 | 47.0 / 31.0 |
| topics ≤15 docs (absolute) | 53 | 3 |
| topics ≤ own-floor+10 | 98 | 70 |
| hard/soft agreement (True/False/no-signal) | 86/57/137 | 80/39/161 |
| agreement rate among texts *with* a signal | 60.1% | 67.2% |
| % of sample with any soft signal | 51.1% | 42.5% |
| top-2 topics combined | 4.4% | 4.5% |
| "rulesbased" duplicate topic | 2 separate topics | still 2 separate topics (not merged) |
| control topics (gaza/ukraine/iran/telephone/home/maria) | all distinct | all distinct (incl. telephone, under a renamed representation) |

**Qualitative findings:**
- The top-2-combined mega-topic metric barely moved (4.4%→4.5%) — mts=15 does **not** show the
  severe mega-topic collapse seen at mts=25/35, which is the main thing this sweep point was
  meant to check.
- However, the "rulesbased" duplicate-topic pair **did not merge** at mts=15 (still 2 separate
  topic ids, same as baseline) — unlike the confirmed full merge at mts=25/35. So mts=15 does not
  actually fix the specific problem that originally motivated Experiment A.
- The "telephone conversation" control topic (present at baseline and preserved as a
  standalone topic through mts=25/35's other control topics) **disappeared** at mts=15 already —
  an early, milder sign of the same absorption pattern seen more severely at higher
  `min_topic_size`, on a topic that survived fine at the more extreme mts=35 setting for other
  controls.
- Gaza, Ukraine, Iran, home/bring-home, and maria/lying control topics all stayed distinct and
  reasonably sized at mts=15.
- Coverage cost: fewer texts get any soft signal at all (51.1%→42.5%), and the sample's
  no_soft_signal rate rose from ~49% to ~57.5% (case_pct), a real usability regression for the
  soft-scoring feature specifically.

**Conclusion:** mts=15 is a genuine middle ground on the mega-topic-collapse axis (much milder
than mts=25/35), but it (a) doesn't actually solve the rulesbased duplicate-topic problem that
motivated the whole sweep, (b) already shows an early instance of a good control topic being
absorbed, and (c) meaningfully reduces the fraction of texts receiving any soft signal — a
direct cost to the very feature this whole track of experiments serves.

**Decision: rejected.** `min_topic_size=10` remains the choice. **Why we stayed with 10 instead
of moving to 15:** the improvements at 15 are smaller/less consistent than hoped (duplicate topic
persists, one control topic already lost) while introducing a real, measurable drop in soft-signal
coverage — not a clearly favorable trade-off over the current default. No production model was
changed by this experiment; `soft_v2_expA_mts15` is an isolated, separate experiment path.

**Experiment A is now closed:** across all sweep points tried (15, 25, 35), none improve on the
default `min_topic_size=10` enough to justify adopting them — `min_topic_size=10` remains final.
The `min_topic_size=15` model (`models/experiments/soft_v2_expA_mts15`) was deleted after this
decision (kept only long enough to run the comparison) — not committed to git, not kept locally.

---

## 8. Experiment B — embedding model swap (`all-MiniLM-L6-v2` → `all-mpnet-base-v2`)

**Files:** [experiments/topic_modeling/experiment_b_embedding_model.py](experiments/topic_modeling/experiment_b_embedding_model.py), [src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py) (`build_bertopic_model` gained an optional `embedding_model` parameter)

**Goal:** With `min_topic_size` sweeps closed (Experiments 6-7) without solving the original
"rulesbased" duplicate-topic problem, test a different lever entirely: hold `min_topic_size=10`,
UMAP `random_state=42`, preprocessing/dedup, and Experiment C's representation improvement all
fixed, and swap only the sentence-embedding model — from BERTopic's default
`sentence-transformers/all-MiniLM-L6-v2` (384-dim) to `sentence-transformers/all-mpnet-base-v2`
(768-dim, generally stronger semantic embeddings, ~2-3x slower on CPU, ~438MB vs. ~90MB on disk).

**What we changed:** Added an `embedding_model` parameter to `build_bertopic_model()` in
`train_topics.py` (defaults to `None`, in which case BERTopic falls back to its own default -
100% behavior-identical to before this parameter existed, zero risk to any existing caller). Fit
a fresh model with `embedding_model="sentence-transformers/all-mpnet-base-v2"`,
`min_topic_size=10`, `random_state=42`, and Experiment C's representation improvement, saved to
its own separate path, `models/experiments/soft_v2_expB_mpnet`. Reused the existing seeded
`min_topic_size=10` MiniLM baseline (`soft_v2_baseline_seeded`) unchanged as the comparison point.

**Baseline:** The same seeded `min_topic_size=10` MiniLM baseline used throughout Experiments
A/A2 (`soft_v2_baseline_seeded`).

**Data/sample:** Same 16,062-text corpus, same n=280/seed=42 quality sample.

**Metrics (MiniLM baseline vs. mpnet):**

| metric | MiniLM (baseline) | mpnet |
|---|---|---|
| topic count (excl. -1) | 282 | 309 |
| outlier % | 35.8% (5,750/16,062) | **34.7%** (5,581/16,062) |
| avg / median topic size | 36.6 / 25.5 | 33.9 / 24.0 |
| topics ≤15 docs (absolute) | 53 | 74 |
| topics ≤ own-floor+10 | 98 | 131 |
| hard/soft agreement (True/False/no-signal) | 86/57/137 | **100/50/129** |
| % of sample with any soft signal | 51.1% | **53.9%** |
| top-2 topics combined | 449 (4.4%) | 430 (**4.1%**) — no mega-topic |
| "rulesbased" duplicate topic | 2 separate topics (n=31 + n=18) | **merged into 1 topic** (n=122, "rules based / international law / international order") |
| control topics (gaza/ukraine/iran/telephone/home/maria) | all distinct | all distinct, but gaza/ukraine/iran/telephone fragmented into smaller, more specific sub-topics (home/maria stayed stable in size) |

**Qualitative findings:**
- **`rulesbased` initially reported as "not found" (empty list) by the substring search** -
  manually verified (per the established gotcha: never trust an automated "not found" without
  checking) by dumping every topic's top-10 words and searching for "rule"/"based"/"order". Found
  Topic 8 (n=122, top words "rules based", "international law", "global rules", "international
  order") - confirmed the two baseline duplicate topics (n=31 + n=18 = 49 combined) **merged into
  one single, larger, well-labeled topic** under mpnet. This is the first time across all of
  Experiment A/A2/B that the original motivating duplicate-topic problem has actually been fixed
  **without** the mega-topic collapse seen at `min_topic_size` 25/35 - the top-2-combined metric
  stayed low (4.1%, even slightly better than baseline's 4.4%).
- Real, consistent improvements across three independent quality signals simultaneously: outlier
  rate down, hard/soft agreement counts up on both True and (proportionally) down on False, and
  soft-signal coverage up - no other experiment (A, A2) improved all three at once.
- The cost: more topics overall (282→309) and more small/fragmented topics (≤15 docs: 53→74;
  ≤floor+10: 98→131). Several control topics (gaza, ukraine, iran, telephone) shrank noticeably
  as they split into more specific sub-topics (e.g. gaza 191→54, ukraine 149→88, telephone's
  "telephone conversation" broad topic split into more specific ones like "president france
  macron" n=20) - more granularity, not absorption/loss (no control topic disappeared or got
  swallowed by a giant blob, unlike the mts=25/35 mega-topic pattern).
- Practical cost: `all-mpnet-base-v2` is a larger (~438MB vs ~90MB), slower (roughly 2-3x on CPU,
  no GPU available in this environment) model to embed and re-embed with on every future re-fit.

**Conclusion:** Embedding model swap is, so far, the single most promising lever tried across
Experiments A/A2/B - it is the only change that fixes the original `rulesbased` duplicate-topic
problem while *simultaneously* improving outlier rate, hard/soft agreement, and soft-signal
coverage, and without triggering the mega-topic collapse that ruined `min_topic_size` 25/35. The
trade-off (more, smaller topics; heavier/slower model) is real but qualitatively different from
A/A2's trade-offs - it looks like added granularity rather than lost coverage or damaged themes.

**Decision: NOT YET FINAL - mpnet is the strongest candidate so far, but not yet adopted.**
`saved_topic_model_soft_v2` (MiniLM, unseeded) was **not** touched or replaced by this experiment.
`models/experiments/soft_v2_expB_mpnet` is being kept locally (unlike the deleted mts=15 model)
because it is a serious candidate that may end up selected - but it is intentionally **not**
committed to git (only the experiment code, `EXPERIMENTS.md`, and the `.expB_mpnet.*`-suffixed
result/comparison files are). Before finalizing a switch to mpnet in production, still need to
check: reproducibility across multiple seeds (only random_state=42 tested so far), manual
label-quality spot-check on a larger sample of topics (not just the 5 largest + watch-words +
controls), actual wall-clock/resource cost of a full production re-fit + inference-time impact on `stance.py`'s
runtime pipeline, (4) whether the higher topic count/fragmentation affects
`analyze_agendas.py`'s narrative-agenda aggregation downstream.

**UPDATE: see "9. Experiment B seed-stability check" below - the single-seed (42) result above
turned out to be partly optimistic; the outlier-rate improvement and the rulesbased merge did NOT
fully replicate across additional seeds.**

---

## 9. Experiment B seed-stability check (`random_state` 7, 123, in addition to 42)

**Files:** [experiments/topic_modeling/experiment_b_seed_stability.py](experiments/topic_modeling/experiment_b_seed_stability.py)

**Goal:** Answer one question directly, per explicit user request: is mpnet consistently better
than MiniLM across UMAP seeds, or was the original Experiment B result (seed=42) a lucky roll?
Everything else held fixed: `min_topic_size=10`, same preprocessing/dedup, same Experiment C
representation, same 16,062-text corpus.

**What we changed:** Fit 4 new models (MiniLM x seed 7/123, mpnet x seed 7/123), reusing the
existing seed=42 models for both embeddings unchanged (`soft_v2_baseline_seeded`,
`soft_v2_expB_mpnet`). Saved the 4 new models to their own separate paths under
`models/experiments/soft_v2_seedstab_<embedding>_seed<N>`. Added a robust `find_rulesbased_topics()`
helper that matches BOTH tokenizations seen so far (MiniLM's concatenated `rulesbased`, mpnet's
bigram `rules based`), requiring both "rule" and "based" substrings to co-occur in a topic's
top-10 words (avoids false positives like an unrelated "rule law"/judicial-fairness topic).

**Data/sample:** Same 16,062-text corpus, same n=280/seed=42 quality sample, for all 6
(embedding x seed) combinations.

**Full 3-seed x 2-embedding results:**

| seed | embedding | topics | outlier% | agreement T/F/None | soft-signal% | small≤15 | largest topic | top2% | rulesbased# |
|---|---|---|---|---|---|---|---|---|---|
| 42 | MiniLM | 282 | 35.8 | 86/57/137 | 51.1 | 53 | 240 | 4.4 | 2 |
| 7 | MiniLM | 288 | 33.5 | 99/55/125 | 55.4 | 58 | 300 | 4.8 | 2 |
| 123 | MiniLM | 301 | 34.2 | 92/66/122 | 56.4 | 76 | 217 | 4.1 | 2 |
| **avg MiniLM** | | **290.3** | **34.5** | **92.3/59.3/128.0** | **54.3** | **62.3** | **252.3** | **4.43** | **2/2/2** |
| 42 | mpnet | 309 | 34.7 | 100/50/129 | 53.9 | 74 | 220 | 4.1 | **1 (merged)** |
| 7 | mpnet | 309 | 35.9 | 103/56/120 | 57.1 | 69 | 226 | 4.3 | **1 (merged)** |
| 123 | mpnet | 312 | 36.2 | 107/53/119 | 57.5 | 71 | 206 | 3.9 | **2 (NOT merged)** |
| **avg mpnet** | | **310.0** | **35.6** | **103.3/53.0/122.7** | **56.2** | **71.3** | **217.3** | **4.1** | **1/1/2** |

**Qualitative findings:**
- **Consistent mpnet wins (true in all 3 seeds):** hard/soft agreement True-count (100/103/107 vs.
  86/99/92), soft-signal coverage (53.9/57.1/57.5% vs. 51.1/55.4/56.4%), largest single topic
  smaller (220/226/206 vs. 240/300/217), top-2-combined % lower (4.1/4.3/3.9% vs. 4.4/4.8/4.1%) -
  no mega-topic risk in either embedding model at any seed tested.
- **NOT consistent - outlier %:** at seed=42 alone, mpnet looked better (34.7% vs. 35.8%). Averaged
  over all 3 seeds, mpnet is actually **worse** (35.6% vs. 34.5%) - the original single-seed
  result was partly a lucky draw, not a real, repeatable improvement.
- **NOT consistent - "rulesbased" merge:** merged into one topic at seed=42 and seed=7, but
  reverted to 2 separate topics (`based order`/`rules based`, n=19+19) at seed=123 - the SAME
  outcome pattern as MiniLM (which never merged it in any of the 3 seeds). mpnet clearly increases
  the *probability* of this merge (2/3 vs. 0/3) but does not guarantee it.
- **Control-topic instability under mpnet:** "gaza" fragmented drastically and consistently across
  all 3 mpnet seeds (n=46-54 vs. MiniLM's stable ~163-191), and "ukraine"'s largest matching topic
  picked a different specific angle each seed (zelensky-focused at 42/123, a
  europe/belarus-shield-focused topic at seed 7) - MiniLM's gaza/ukraine/maria/home control topics
  stayed thematically stable and consistently sized across all 3 seeds.
- **False-positive substring match caught and fixed:** at mpnet seed=123, the automated
  `home_bring` search matched Topic 65 (n=39, "occupied west bank / israeli settlers / palestinian
  homes") purely because "palestinian homes" contains the substring "home" - manually verified
  (per the established gotcha) this was NOT the real hostages/bring-home topic. The genuine
  hostages/bring-home topic was found separately at Topic 5 (n=157, "hostages captivity kidnapped
  abductee"), a reasonable size consistent with the other 2 seeds (220, 226). Reinforces the
  lesson: automated substring matches need spot verification even when they DO return a match
  (not just when they report "not found").

**Conclusion:** mpnet is **not** consistently better than MiniLM across seeds. The two headline
findings that motivated adopting it - lower outlier rate and a fixed "rulesbased" duplicate - both
failed to fully replicate: outlier rate reverses on average, and the rulesbased merge only
happened in 2 of 3 seeds. What DOES replicate consistently: better hard/soft agreement, better
soft-signal coverage, and no mega-topic risk in either model at any seed. Large control themes
(gaza, ukraine) are also less stable under mpnet, splitting into different specific sub-topics
from seed to seed.

**Decision: mpnet is NOT adopted.** The seed=42 result that originally looked like a clear win was
partly a lucky draw - `min_topic_size=10` with the original `all-MiniLM-L6-v2` embedding remains
the production choice (`saved_topic_model_soft_v2` untouched throughout). mpnet's consistent wins
(agreement, soft-signal coverage) are real but do not, on their own, justify the cost of a larger/
slower model and less stable large-topic structure - especially since neither of the two problems
that originally motivated trying mpnet (outliers, rulesbased duplication) is reliably solved by it.
If the "rulesbased" duplicate is still considered worth fixing, a targeted post-hoc merge of just
that confirmed pair (not a full embedding-model swap) is the more promising next step. All 4 newly
fit models (`models/experiments/soft_v2_seedstab_*`) are being kept locally for now, alongside
`soft_v2_expB_mpnet` and `soft_v2_baseline_seeded` - none committed to git (only the experiment
code, `EXPERIMENTS.md`, and suffixed result files are).

---

## 10. Experiment D — targeted duplicate-topic detection + rulesbased merge test

**Files:** [experiments/topic_modeling/experiment_d_duplicate_topics.py](experiments/topic_modeling/experiment_d_duplicate_topics.py),
[reports/results/profiler_prototype/expD_duplicate_topic_candidates.json](reports/results/profiler_prototype/expD_duplicate_topic_candidates.json),
[reports/results/profiler_prototype/expD_merge_rulesbased_comparison.json](reports/results/profiler_prototype/expD_merge_rulesbased_comparison.json)

**Goal:** Instead of a blanket `min_topic_size` increase or embedding-model swap (both tried and
rejected/inconclusive in Experiments 6, 7, 8, 9), directly detect which topic pairs in the
production baseline (`soft_v2_baseline_seeded`, MiniLM, seed=42, 282 topics) are true near-duplicates,
and test what a targeted `BERTopic.merge_topics()` call on ONLY a confirmed-duplicate pair does to:
topic count, outlier count, the merged topic's own representation, and every OTHER topic. No
automatic merging beyond the already-known rulesbased pair was performed, per explicit request.

**Stage 1 - detection methodology:** For every one of the 39,621 possible topic pairs (282
topics), computed 3 signals and combined the first two: `semantic_sim` (cosine similarity of
BERTopic's `topic_embeddings_`, i.e. SBERT-space centroid similarity), `lexical_sim` (cosine
similarity of `c_tf_idf_` rows), `top10_jaccard` (word-set overlap of the top-10 c-TF-IDF words -
reported but NOT included in `combined_score`, since two duplicate topics can have near-identical
meaning while BERTopic's MMR diversifies their displayed word lists differently).
`combined_score = mean(semantic_sim, lexical_sim)`. Ranked all pairs, saved the top 20 plus 3
example source documents per topic for manual inspection.

**Stage 1 - results:** Score distribution over all 39,621 pairs: median 0.116, p90 0.223, p95
0.260, p99 0.332, p99.5 0.365, p99.9 0.417, max 0.512. Manually inspected the top-20 pairs
(scores 0.444-0.512): the overwhelming majority are **same-domain-but-genuinely-distinct**
topics - e.g. the #1-ranked pair (combined=0.512) is "armoured vehicles/artillery/brigades"
vs. "Russian defence ministry footage/air-defense strikes" - both military-equipment-adjacent,
clearly different sub-topics, not duplicates. The known **rulesbased** pair (topics 96 and 209,
"rules-based order" framed as Western hypocrisy vs. as legitimate global governance) scored
0.461 - inside the top 20, above p99.9, but NOT the highest-scoring pair overall. This shows
`combined_score` alone has limited discriminative power: it is a reasonable **recall filter for
human review**, not a reliable automatic duplicate detector - most high-scoring pairs are related
but legitimately separate topics.

**Proposed threshold:** 0.42 (~p99.9). Pairs scoring above this are worth a human look; pairs
below are very unlikely to be duplicates given this corpus. **Caveat (important):** scoring above
threshold is not sufficient evidence of duplication by itself - of the ~40 pairs above 0.42 in this
corpus, manual inspection found exactly ONE genuine duplicate (rulesbased). No other pairs are
recommended for merging based on this run.

**Stage 2 - targeted merge test methodology:** Loaded a fresh copy of the baseline model (with
the embedding model explicitly re-specified on load - see Problem Resolution note below), called
`topic_model.merge_topics(texts, topics_to_merge=[96, 209])`, and compared before/after on a
separate saved copy (`models/experiments/soft_v2_expD_merge_rulesbased`, `soft_v2_baseline_seeded`
and `saved_topic_model_soft_v2` never touched).

**Stage 2 - results:**
- Topic count: 282 -> 281 (as expected, exactly one topic removed by merging two into one).
- Outlier count: 5,750 -> 5,750, unchanged (correct - merging never reassigns outlier -> non-outlier).
- Merged topic (n=49, renumbered id 50 after frequency-based resort): words become
  `('rules based', 'based order', 'rules', 'order just', 'based', 'order', 'global rules',
  'order isn', 'order talk', 'just fancy')` - a sensible combined representation of both original
  sub-framings.
- **All 280 other (non-merged) topics: document membership is proven IDENTICAL before/after**
  (verified via exact document-index-set matching, not count or word-based matching, which are
  ambiguous/unreliable after ID renumbering) - 280/280 topics matched by their exact set of member
  documents, confirming `merge_topics()` never reassigns any document belonging to a non-merged
  topic.
- **However, their DISPLAYED top-10 words often changed anyway** (mean Jaccard overlap of
  before/after top-10 word sets = 0.240, median = 0.250, 0/280 topics have an identical top-10
  word set). This is a genuine, previously undocumented side effect: `merge_topics()`'s internal
  `_extract_topics()` recomputes `ClassTfidfTransformer` + MaximalMarginalRelevance representation
  for the **entire corpus**, since c-TF-IDF's frequency normalization depends on all classes'
  document-count distribution - so removing one topic (redistributing its weight) can shift the
  ranked/diversified word list of unrelated topics even though not a single document moved.
  Examples of large drift on document-membership-verified-unchanged topics: a "trickle-down
  economics" topic's top words shifted from `('trickledown', 'trickledown economics', ...)` to
  `('trickle', 'trickle economics', 'rich richer', ...)` (jaccard=0.0) - same underlying meaning,
  different exact n-gram tokenization ranking, not a substantive change in topic identity.
- Quality metrics (`analyze_soft_topic_quality.py`, same n=280 seed=42 sample): hard/soft
  agreement improved modestly, True 86->92, False 57->52, None 137->136; `hard_is_outlier_pct`
  unchanged (0.0 in both); `dominant_single_topic` case % 49.3->50.0. A small, plausible
  improvement consistent with removing one genuinely-duplicate topic pair, not a dramatic shift.

**Problem resolved along the way:** `BERTopic.load(path)` without an explicit `embedding_model=`
argument silently drops the embedding-model reference (prints a warning), which then produces a
`config.json` missing the `"embedding_model"` key on the next `.save()`, breaking any later
`.transform()` call ("No embedding model was found to embed the documents"). Fix: always pass
`embedding_model="sentence-transformers/all-MiniLM-L6-v2"` explicitly when loading a model that
will later be re-saved. Also: after any `merge_topics()` call, topic ids are renumbered by
frequency, so identifying "the merged topic" or matching "the same topic before/after" must be
done by CONTENT (a robust content-search helper) or by exact document-membership set, never by
count or id alone (a count-collision was caught during development: an unrelated topic
coincidentally also had n=49).

**Conclusion:** Of all 39,621 topic pairs in the production baseline, only the already-known
rulesbased pair (topics 96/209) is a confirmed genuine duplicate; no other pairs among the top-20
highest-scoring candidates are recommended for merging. A targeted merge of just this one pair is
clean: it does not touch any other topic's document membership, produces a sensible combined
representation, and modestly improves hard/soft agreement - but it does perturb the *displayed*
representation of unrelated topics (a real, now-documented `merge_topics()` side effect, not a
bug) which should be expected and accepted, not treated as a red flag, if this merge is adopted.

**Decision: adoption is deferred to the user.** This experiment only demonstrates that the
merge is safe and beneficial when tested in isolation on `soft_v2_expD_merge_rulesbased` - it was
deliberately NOT applied to `saved_topic_model_soft_v2` (production) or `soft_v2_baseline_seeded`.
If adopted, the same `merge_topics(texts, topics_to_merge=[<rulesbased ids in that model>])` call
should be applied directly to the production model as a one-off post-hoc fix, independent of any
future `min_topic_size`/embedding-model decision.

---

## 11. Experiment D2 — soft-distribution stability check for the rulesbased merge

**Files:** [experiments/topic_modeling/experiment_d2_soft_stability_check.py](experiments/topic_modeling/experiment_d2_soft_stability_check.py),
[reports/results/profiler_prototype/expD2_soft_stability_check.json](reports/results/profiler_prototype/expD2_soft_stability_check.json)

**Goal:** Experiment D validated the rulesbased `merge_topics()` call on hard-cluster/outlier/
topic-count metrics. This closes the remaining gap: does the merge also stay safe for the SOFT
(`approximate_distribution()`) feature specifically, not just the hard cluster assignment?
`saved_topic_model_soft_v2` was deliberately NOT touched by this check.

**Methodology:** Reused the same deterministic 280-text stratified sample (seed=42) throughout.
Built a document-membership-based topic-id map between `soft_v2_baseline_seeded` (before) and
`soft_v2_expD_merge_rulesbased` (after) — generalizing Experiment D's technique into a reusable
`build_topic_id_map()` that also *automatically discovers* which two topic ids were merged
(the ones whose document set has no exact match after renumbering; their union matches a new
frozenset instead), with no hardcoded topic ids. Ran `analyze_soft_topic_quality.analyze()` on
both models over the same sample, excluded the small number of texts that actually touch the
merged topics (these are expected to change and aren't part of the "should stay stable" check),
then compared Top-1 soft topic id (after mapping), Top-3 soft-topic-set Jaccard overlap, and
Top-1 score magnitude change on the remainder.

**Results (n=278/280 unaffected by the merge directly, 2 excluded):**
- Top-1 soft topic unchanged (after id-mapping): 260/278 (93.5%).
- Top-3 soft topic set Jaccard: mean=0.919, median=1.000 (245/278 texts have an identical top-3
  set).
- Top-1 score magnitude change: mean Δ=0.036, median Δ=0.000 (121/135 texts with a defined score
  had Δ≤0.15).
- Hard cluster: unchanged for 278/278 (100%) — confirms Experiment D's document-membership proof
  extends correctly to this independent 280-text sample too.
- **33/278 (11.9%) texts have hard cluster unchanged but a meaningfully-changed soft distribution**
  (top-3 set changed AND/OR |Δscore|>0.15) — a real, quantified drift rate, consistent in kind
  with Experiment D's already-documented finding that `merge_topics()` recomputes c-TF-IDF/
  representation for the whole corpus (not just the merged pair), so even unrelated topics'
  *soft* scores can shift slightly even when hard membership never moves.

**Conclusion:** The rulesbased merge is safe for soft clustering in the large majority of cases
(88.1% fully stable by both Top-3-set and score-magnitude criteria), with a real but modest
(~12%) minority showing soft-distribution drift despite an unchanged hard cluster — this is the
expected, already-understood side effect of `merge_topics()`'s corpus-wide c-TF-IDF recompute, not
a sign of a broken merge. No case was found where the soft distribution changed drastically
(e.g. flipped to an unrelated topic) among the unaffected texts.

**Decision:** Confirms Experiment D's merge is safe to adopt for the soft feature too, if/when the
user decides to adopt it. `soft_v2_baseline_seeded` and `soft_v2_expD_merge_rulesbased` remain
untouched, read-only experiment artifacts; `saved_topic_model_soft_v2` was not modified.

---

## 12. `recommend_min_topic_size(corpus_size)` — a corpus-size-aware heuristic

**Files:** [src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py) (function `recommend_min_topic_size`,
alongside `build_bertopic_model`)

**Goal:** `min_topic_size=10` (the value validated for the current ~16K-text corpus across
Experiments 6/7) was hardcoded everywhere. Before scaling to a much larger future corpus (the
eventual narrative-classification comparison may use substantially more data), provide a single
explainable function that recommends a starting `min_topic_size` as a function of corpus size.

**Original heuristic (superseded — see Experiment F below):** `min_topic_size = round(10 *
sqrt(corpus_size / 16062))`, clamped to `[10, 100]`. This mirrored the classic "K ≈ sqrt(N/2)"
rule of thumb used to pick a cluster count for k-means as data grows, adapted here to HDBSCAN's
minimum-cluster-size threshold — a plausible-sounding heuristic, but at the time this section was
written it was explicitly **untested**: it was never checked against a real sweep at smaller/larger
corpus sizes, only reasoned about by analogy.

**UPDATE — this heuristic was empirically tested and found wrong for the downscaling direction.**
Experiment F (section 16) ran a real subsampling sweep at 4K/8K/12K/16K and found the empirically
best `min_topic_size` stayed at 10 across every one of those sizes — the sqrt formula above would
have recommended ~5/7/9 at 4K/8K/12K, all of which scored *worse* in the actual sweep (more
fragmented micro-topics, lower coherence/diversity, worse hard/soft agreement, lower soft-signal
coverage) than just keeping `min_topic_size=10`. `recommend_min_topic_size()` in
[src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py) has been rewritten accordingly: it now returns the
constant 10 for any corpus size up to the largest size actually tested (~16,062), and only applies
a small, explicitly-flagged-as-**unvalidated** log-scaled increase beyond that point (see
Experiment F for the full reasoning and the updated example-output table). This section is kept
for historical context; treat Experiment F as the current source of truth.

**Decision:** Superseded by Experiment F. The corpus-size-aware heuristic remains a pure utility
function; does not change any existing model's behavior (`build_and_save_topics()` /
`saved_topic_model_soft_v2` still uses the unchanged, hardcoded `min_topic_size=10` — this
function is opt-in for future/new experiments only).

---

## 13. Experiment E — classic LDA baseline vs. BERTopic Hard / Soft

**Files:** [experiments/topic_modeling/experiment_e_lda_baseline.py](experiments/topic_modeling/experiment_e_lda_baseline.py),
[reports/results/profiler_prototype/expE_lda_baseline.json](reports/results/profiler_prototype/expE_lda_baseline.json),
`models/experiments/lda_baseline/` (new, separate artifact — never read by any other code)

**Goal:** Add a classic (pre-embedding) topic-modeling baseline — `gensim`'s LDA — on the exact
same corpus/preprocessing pipeline as `soft_v2_baseline_seeded`, to give the eventual
narrative-classification comparison a non-BERTopic reference point. Explicitly not a replacement
for BERTopic.

**Methodology:** Same 16,062-text corpus (`load_deduplicated_training_texts()`). LDA-specific
bag-of-words tokenization (lowercase, alphabetic tokens ≥3 chars, sklearn English stopwords
removed) → a single shared `gensim.corpora.Dictionary` (`no_below=5, no_above=0.5, keep_n=10000`,
final vocab 7,538 words) used both to fit LDA and to score BERTopic's own topics with the *same*
coherence metric (u_mass — chosen because it needs no external reference corpus, unlike `c_v`,
keeping this tractable on CPU). Number of LDA topics (K) was chosen via a coherence sweep over
K∈{50,100,150,200} rather than copied from BERTopic's topic count. Seed-stability was checked by
refitting the chosen-K model with a second seed and matching topics via best-Jaccard (both
document-membership-based, the same style of technique as Experiment D2, and top-10-word-based).

**Engineering note:** `gensim.models.LdaMulticore` was tried first but measured far *slower* than
single-process `LdaModel` on this machine (Windows `multiprocessing` "spawn" re-imports/re-pickles
the whole corpus per worker per fit: ~158s for a tiny K=50/passes=1/iterations=20 config vs. ~2s
single-process; ~8s single-process for a much larger K=200/passes=3/iterations=50). Switched to
single-process `LdaModel` (`passes=5, iterations=100`) — the full sweep + seed-stability check
completed in well under 2 minutes end-to-end.

**Results:**

| K | u_mass coherence | topic diversity |
|---|---|---|
| 50 | **−7.64** (best) | 0.916 |
| 100 | −11.24 | 0.944 |
| 150 | −14.08 | **0.125 (collapsed)** |
| 200 | −15.59 | **0.005 (collapsed)** |

- **K=150/200 diversity collapse** is a real, important finding: past a certain topic count, this
  corpus's ~7,500-word bag-of-words vocabulary can no longer support that many *distinct* LDA
  topics — most of the extra topics converge onto nearly-identical top-word lists (diversity→0),
  a structural limitation of classic LDA on this corpus, not a tuning artifact. K=50 was selected.
- **Seed-stability at K=50 is poor**: doc-membership best-Jaccard mean=0.110/median=0.092;
  top-10-word best-Jaccard mean=0.120/median=0.111 — LDA's topics on this corpus are substantially
  less reproducible across random seeds than BERTopic's (whose seeded UMAP already gives fully
  reproducible hard clusters by construction, see `build_bertopic_model`'s `random_state`).
- **Coherence: BERTopic Hard (u_mass=−6.08 on its own 282 topics, filtered to single-word terms
  present in the shared dictionary) is more coherent than LDA-K=50 (−7.64)**, despite having ~5.6x
  more topics — a meaningful advantage for BERTopic on this corpus.
- **Diversity: BERTopic Hard = 0.988** (near-perfect — almost no repeated words across 282 topics'
  top-10 lists) vs. LDA-K50's 0.916, and vastly better than LDA's own collapse at higher K —
  BERTopic's embedding+c-TF-IDF representation scales to many more topics without word reuse in a
  way classic bag-of-words LDA does not on this corpus.
- **Interpretability (manual read of LDA-K50's top-10 topics):** broadly on-theme (Israel/Gaza/
  Ukraine/media/military discourse recognizable throughout) but noticeably less crisp than
  BERTopic's topics — many LDA topics share generic high-frequency words (`israeli`, `israel`,
  `western`) across several topics, whereas BERTopic's per-topic word lists are more differentiated.
- **Document-topic distribution (280-sample):** LDA's per-document distributions are highly
  diffuse — mean top-1 topic probability only 0.258, mean normalized entropy 0.605 (of max
  possible, 0=fully concentrated / 1=uniform over all 50 topics), and 70.7% of texts have *no*
  dominant topic (top-1 probability <0.3). This is the expected consequence of short social-media
  texts under a sparse bag-of-words model. By contrast, BERTopic's soft distribution (already
  measured, `soft_topic_quality_summary.json`) is bimodal rather than diffuse: ~49% of texts get
  no soft signal at all, but when they DO get a signal it's usually highly concentrated
  (dominance ratio mean=0.90, median=1.0) — the two methods fail differently (LDA: uncertain-but-
  present everywhere; BERTopic soft: absent-or-confident), not simply "better/worse".
- **Coverage/outliers:** LDA has no outlier concept — every document always gets a full
  distribution over all K topics by construction. BERTopic Hard's TRUE full-corpus outlier rate
  (from `.topics_`, the fit-time assignment) is 35.8% — consistent with the already-documented
  ~34-36% range in this file's Open Problems section (not a new number). **A genuinely new,
  previously-undocumented nuance found while computing this**: BERTopic's `.transform()` (used
  for ALL new/inference-time text, e.g. by `stance.py`) essentially eliminates the outlier label
  in practice — of 300 documents that WERE outliers (-1) in the original training fit, calling
  `.transform()` on those same texts reassigns 297/300 (99%) to a real topic, only 3/300 remain -1.
  This explains why every sample-based soft-quality report in this project (Experiments 5-10)
  consistently shows ~0% `hard_is_outlier_pct` despite ~35% of the actual training corpus being
  labeled -1 at fit time — `.transform()` structurally cannot reproduce fit-time outlier detection
  for new text (it assigns nearest-topic, no density/outlier check), so downstream consumers of
  hard topic ids at inference time (`TopicStanceLayer` via `stance.py`) should not expect to ever
  see -1 in practice, regardless of the training corpus's real outlier rate.
- **Runtime:** LDA's own fit times were measured directly (see engineering note above). BERTopic's
  training time was NOT re-measured (re-fitting `soft_v2_baseline_seeded` was out of scope/wasteful
  here) — only BERTopic's *inference* time on the same 280-text sample was measured for a
  partial, inference-side comparison (see `expE_lda_baseline.json` for the raw numbers);
  training-time comparison is explicitly left unmeasured rather than guessed.

**Conclusion:** BERTopic (Hard) outperforms this classic LDA baseline on this corpus on coherence,
diversity (especially at higher topic counts, where LDA structurally collapses), and per-document
concentration/confidence — consistent with BERTopic's embedding-based representation being better
suited to this heterogeneous, mixed-length social-media corpus than bag-of-words LDA. LDA remains
useful as a reference point (never previously measured in this project) and surfaced one valuable,
previously-undocumented nuance about BERTopic's `.transform()`-vs-fit-time outlier behavior.

**Decision:** LDA is NOT adopted to replace BERTopic — kept purely as a separate benchmark
artifact (`models/experiments/lda_baseline/`), consistent with the explicit instruction not to
replace BERTopic. No existing file was modified.

---

## 14. LLM-ITL feasibility research (Xiaohao-Yang/LLM-ITL, ACL 2025) — not built

**Goal:** Research whether `https://github.com/Xiaohao-Yang/LLM-ITL` (an LLM-in-the-loop Neural
Topic Model framework) is feasible to adopt as a 4th, fully separate topic-modeling experiment,
checking GPU/memory/dependencies BEFORE attempting to run anything, per explicit instruction.

**What the method is:** LLM-ITL pairs a classic (VAE-style) Neural Topic Model — one of NVDM,
PLDA, SCHOLAR, ETM, NSTM, CLNTM, WeTe, ECRTM (**not BERTopic**) — with an LLM that refines the
NTM's learned topic-word distributions via an Optimal-Transport-based alignment objective,
weighted dynamically by the LLM's own confidence in its suggested topical words. In plain terms:
the NTM learns topics/document representations as usual, and the LLM is consulted *repeatedly
during training* (not a one-shot post-hoc labeling pass) to nudge the topic-word distributions
toward more human-interpretable words, with the OT objective controlling how much to trust the
LLM's suggestions at each step. This is a substantively different mechanism from this project's
existing lightweight adaptation (`llm_topic_refiner.py`, a single Gemini API call per topic to
relabel BERTopic's already-fixed top words, no training-loop integration at all).

**Feasibility check (this session, direct verification, not assumption):**
- **GPU: none available.** `torch.cuda.is_available()` → `False`; installed torch build is
  `2.13.0+cpu`. LLM-ITL's own smallest supported LLM (Phi-3-mini-128k-instruct, ~3.8B params) is
  still meant to run *repeatedly inside the NTM training loop* — CPU-only inference at this scale,
  called many times per training run, would make even a modest topic count (K=50) prohibitively
  slow (likely many hours-to-days, vs. LDA's <2 minutes end-to-end in Experiment E above).
- **Memory: 16.65 GB total physical RAM.** Tight even for a single Phi-3-mini (~3.8B) inference
  call in isolation (weights alone ≈7-8GB in fp16, before KV-cache/activations/OS overhead) —
  clearly insufficient headroom for the repeated in-the-loop calls the method requires.
  supported LLMs range up to Qwen1.5-32B-Chat / LLAMA3-8B / Mistral-7B — all further out of reach.
- **Dependencies/engineering scope, beyond the LLM itself:** requires a Java runtime + the
  bundled `palmetto-0.1.5-exec.jar` + a downloaded Wikipedia background-document corpus
  (`Wikipedia_bd.zip`, external download) for its own coherence evaluation; fixed built-in dataset
  loaders (20News/AGNews/DBpedia/R8 only) — plugging in this project's narrative corpus would
  require writing custom dataset-integration code, not just a config flag; and none of its 8
  supported NTMs are BERTopic-compatible, so adopting it would mean fitting an entirely separate,
  unrelated topic-modeling architecture from scratch, on top of everything else above.

**Conclusion: not feasible to build as a genuinely-running experiment in this local, CPU-only,
16GB-RAM environment.** Every one of the three checks the user asked for (GPU / memory /
dependencies) independently rules it out, and the engineering cost (custom dataset integration +
a wholly separate non-BERTopic NTM implementation + a Java/Wikipedia evaluation toolchain) would
be substantial even ignoring the hardware constraint. This is consistent with — and now directly
re-verified rather than assumed — this project's prior conclusion that a full LLM-ITL adoption is
"too heavy"; the existing lightweight `llm_topic_refiner.py` (Colab/API-based) remains the
practical way this project incorporates LLM-based topic refinement.

**Decision: do not build.** No code was written for this experiment; this is a documented
"researched, infeasible, skipped" entry, not an implementation gap. If GPU access ever becomes
available (e.g. a Colab session with a GPU runtime, already used elsewhere in this project for
`llm_topic_refiner.py`), this conclusion should be re-checked there rather than assumed permanent.

---

## 15. Narrative Classification — does a Topic *distribution* beat a single hard Topic id?

**Goal (separate track from every experiment above — this is about the *classifier*, not the
topic model):** the topic-modeling phase is closed; this experiment starts the Narrative
Classification phase. Question: does feeding the classifier a **distribution** over several
Topics (soft/multi-topic) improve Narrative classification compared to a single hard Topic id -
and if so, by how much? A controlled 4-way comparison, same data/splits/training conditions:
1. **Baseline** — no Topic feature at all.
2. **BERTopic Hard** — a single `topic_id` (today's production mechanism).
3. **BERTopic Soft** — the existing-but-unused top-K topic distribution
   (`stance.py`'s `get_topic_distribution`, never wired into `fusion.py`/`train.py` until now).
4. **LDA** — the K=50 document-topic distribution from Experiment E's already-fitted baseline.

Explicitly separate from — and does not touch — the BERT Actors/Role/Agency/Relations track
(reserved for after this experiment), and does not touch `fusion.py`, `train.py`, any existing
checkpoint (`models/best_*.pth`), any existing cache (`data/cache/cached_features_*.pt` other
than a brand-new one), or `reports/tables/model_comparison_results.json`.

**Pre-code research (how the Topic feature enters the pipeline today, checked before writing
any code, as required):** every existing classifier (`NarrativeDetector`/`baseline_fusion` and
`HybridNarrativeDetector`/`hybrid` in `fusion.py`) uses the Topic feature in exactly one way: a
single hard `topic_id` from `TopicAnalysisPipeline.process_text()` (stance.py, `.transform()`
under the hood) is looked up in `TopicStanceLayer`, an `nn.Embedding(NUM_TOPICS=500,
NUM_NARRATIVES)` initialized uniformly in [0,1], with -1/OOV/out-of-range clamped to the last
row. `SBERTOnlyDetector`/`sbert_only` uses no Topic feature (and no other engineered feature
either, so it's not usable as-is for "Baseline, no Topic feature" — it would also silently drop
NER/SRL/Emotion/Reliability, which must stay unchanged per the fairness requirement). A soft
method already exists and is fully implemented (`TopicAnalysisPipeline.get_topic_distribution`,
`approximate_distribution()`-based, top-N re-normalized to sum to 1.0) but was **never** wired
into any classifier before this experiment.

**Proposed representation for Soft (and, analogously, LDA) — not just reusing a single
`topic_id`:** a new `TopicFeatureLayer` generalizes `TopicStanceLayer`'s mechanism instead of
replacing it. It is a `[vec_size, NUM_NARRATIVES]` table, same uniform(0,1) init convention as
production. Hard = a one-hot vector (single row, weight 1.0) fed through `dense_vec @ table` —
mathematically identical to `TopicStanceLayer`'s single lookup. Soft = a sparse vector with up
to 5 non-zero entries (the top-5 re-normalized `get_topic_distribution` scores) at their topic
indices, fed through the exact same `dense_vec @ table` operation — a genuine score-weighted
combination of up to 5 table rows, not a single id. LDA = the FULL K=50 dense probability vector
(gensim's `get_document_topics(minimum_probability=0.0)`) through its own same-shaped table
(no OOV row needed — LDA always yields a distribution over all K topics, no outlier concept).
This design keeps the "Topics arm" architecturally identical in kind across Hard/Soft/LDA (same
class, same init, same output shape) — Hard is the one-hot special case of Soft/LDA — so
"single id vs. distribution" is the one true independent variable, not confounded by an
unrelated architecture change. "Baseline, no Topic feature" uses the same `TopicFeatureLayer`
class in a `mode="none"` state with **zero learnable parameters** (the arm always contributes a
constant zero vector) — the cleanest way to represent "no Topic feature" without altering the
surrounding fusion architecture's shape.

**Base architecture chosen:** `fusion.py`'s `NarrativeDetector` (`baseline_fusion`) — the linear
weighted-fusion architecture (4 learned module weights over NER/Topics/SRL/Emotion, softmax-
normalized, multiplied by a reliability factor) — reusing `NarrativeFusionNetwork` **unmodified,
imported directly** from `fusion.py`. Chosen over `HybridNarrativeDetector` because it isolates
the Topics-representation question most cleanly: the module-weight interpretation directly
answers "how much does the Topics arm matter", without an SBERT-embedding + MLP diluting/
entangling that signal. A Hybrid-architecture version of this same comparison is a natural,
separate follow-up if this baseline_fusion-based result looks promising.

**Fairness / controlled-comparison methodology:**
- **Same data + same split, by construction, not just "the same code path":**
  `train.load_raw_data()` and `train.split_random()` are imported **unmodified** and called
  directly (not reimplemented) — identical `random_state=42` shuffle and train/val/test row
  membership across all 4 configs × all seeds, by construction.
- **Same NER/SRL/Emotion/Reliability values, not just "the same processors":** reused **by
  position** from the existing `data/cache/cached_features_hybrid.pt` (baseline_fusion's own
  cache) — verified byte-for-byte-equivalent-membership via an exhaustive label-sequence
  comparison across all 16,510 rows (train: 11,557, val: 2,476, test: 2,477 — all matched)
  before trusting the reuse; the script raises instead of silently reusing if this check ever
  fails on a future re-run (e.g. after raw CSVs change).
- **Same fusion architecture, same training loop/hyperparameters:** `EPOCHS`/`BATCH_SIZE`/
  `LEARNING_RATE` from `config.py`, Adam + `NLLLoss`, gradient accumulation over `BATCH_SIZE`,
  early stopping on Val Macro-F1 (patience=3) — identical to `train.py`'s `train()`.
  Only the Topics arm (representation + its own small table) varies between configs.
- **Seed:** `torch.manual_seed(seed)` fixes model-init/dropout randomness only — the split
  itself is already fixed independently of `seed` (via the hardcoded `random_state=42` inside
  `load_raw_data`/`split_random`), so multi-seed runs are a pure training-variance check, never
  a data-leakage risk. 3 seeds used: 42, 7, 123 (matches this project's established seed set).
- **Isolated artifacts:** every (config, seed) gets its own checkpoint
  (`models/experiments/narrative_topic_compare/{mode}_seed{seed}.pth`) and its own confusion
  matrix; results accumulate in a brand-new `reports/results/narrative_topic_compare/results.json`
  (never `reports/tables/model_comparison_results.json`). Re-running an existing (mode, seed)
  checkpoint is refused (`RuntimeError`), not silently overwritten.

**Known, inherited limitation (not introduced by this experiment):** both the BERTopic model
used here (`models/experiments/soft_v2_baseline_seeded` — the validated Experiments A-E
baseline, deliberately **not** the actual production `models/saved_topic_model_soft_v2`, so that
Hard and Soft are compared on the SAME, best-available underlying topic model rather than
conflating "soft vs. hard" with "which topic model") and the LDA model
(`models/experiments/lda_baseline/lda_k50_seed42`) were originally fit on a corpus that overlaps
with this experiment's "random"-split rows — the same accepted limitation `train.py` already
documents for `split_mode="random"` (only `leave_one_topic` mode actively avoids it). Neither
topic model is re-fit here; both are reused strictly as frozen feature extractors, exactly like
production's `TopicAnalysisPipeline` already does.

**Implementation:** `experiments/feature_ablation/narrative_topic_compare.py` (fully new, self-contained script).
Builds one combined feature cache (`data/cache/cached_features_narrative_topic_compare.pt`,
new file) shared by all 4 configs — NER/SRL/Emotion/Reliability reused as above, plus freshly-
computed Hard/Soft/LDA dense topic vectors (BERTopic's `.transform()`/`.approximate_distribution()`
called batched across each split for efficiency; LDA's `get_document_topics` looped per text,
cheap/no neural inference). `TopicFeatureLayer`/`TopicAblationDetector` implement the design
above; `compute_metrics()` extends `train.py`'s metrics with Weighted P/R/F1 (Accuracy, Macro
P/R/F1, Weighted P/R/F1, per-narrative P/R/F1/support, and confusion matrix are all reported,
per the required comparison criteria). Additional analyses implemented: (a) whether Soft's
benefit over Hard is larger specifically on texts whose soft distribution is NOT dominated by a
single topic (dominance ratio < 0.7), (b) per-Narrative Hard→Soft→LDA F1 deltas, to see whether
some Narratives benefit disproportionately from a richer Topic representation.

**Results.** All 4 configs × 3 seeds (42/7/123) completed; full numbers in
`reports/results/narrative_topic_compare/results.json`, per-seed confusion matrices in
`reports/results/narrative_topic_compare/confusion_matrix_{mode}_seed{seed}_test.csv`. Test-set metrics,
mean±std across the 3 seeds:

| Config | Accuracy | Macro-F1 | Weighted-F1 |
|---|---|---|---|
| `none` (no topic feature) | 50.49% ± 0.31 | 0.4951 ± 0.0033 | 0.5080 ± 0.0029 |
| `hard` (single BERTopic id) | **65.91% ± 0.27** | **0.6522 ± 0.0027** | **0.6580 ± 0.0026** |
| `soft` (top-5 BERTopic distribution) | 61.16% ± 0.17 | 0.6066 ± 0.0014 | 0.6119 ± 0.0020 |
| `lda` (full K=50 LDA distribution) | 53.02% ± 0.30 | 0.5212 ± 0.0029 | 0.5315 ± 0.0028 |

**Headline finding — Hard beats Soft, not the other way around.** Across all 3 seeds, `hard`
outperforms `soft` by a wide, seed-noise-dwarfing margin: **+4.75pp Accuracy, +0.0456 Macro-F1,
+0.0461 Weighted-F1** (per-seed std is only ~0.002-0.003, i.e. the gap is roughly 15-20x larger
than the run-to-run noise — this is a robust effect, not a fluke of one seed). `lda`'s full
50-dim distribution does even worse than `soft`'s 5-dim BERTopic distribution, and only modestly
beats `none`. Ranking: **Hard > Soft > LDA > None**. Any topic feature at all is clearly
valuable (+15pp Accuracy / none→hard), but *how* the topic feature is represented matters a lot,
and a single confident hard id beat every distributional alternative tried here.

**Does Soft help specifically on multi-topic (ambiguous) texts?** Yes — but that population is
small. Splitting the test set by whether the Soft distribution's top score is below the 0.7
dominance threshold: 219/2477 rows (8.8%) are "multi-topic", 2258/2477 (91.2%) are
"single-dominant".
- Multi-topic subset: Soft 72.1% acc **beats** Hard 69.4% acc (+2.7pp) — confirms the intuitive
  hypothesis that a distribution is more informative exactly when no single topic dominates.
- Single-dominant subset (the vast majority): Hard 66.0% acc **beats** Soft 60.0% acc (-6.0pp for
  Soft) — for texts BERTopic is already confident about, spreading the signal across the top-5
  topics adds noise rather than value.
- Net effect over the whole test set is negative for Soft because the subset where it helps
  (8.8%) is far smaller than the subset where it hurts (91.2%).

**Do some Narratives benefit more from Soft?** No — `soft_minus_hard` F1 is **negative for all 7
Narratives** (Zionist -0.136, Left-wing -0.034, Western -0.044, Ukrainian -0.042, Right-wing
-0.041, Resistance -0.038, Russian -0.015 — Russian is the least hurt, Zionist the most). There
is no Narrative for which the richer BERTopic representation is worth adopting; Zionist in
particular is classified noticeably worse with Soft than with Hard.

**Does LDA give similar or lesser value than BERTopic Soft?** Strictly lesser, and by a large
margin — `lda_minus_soft` F1 is negative for 6/7 Narratives (Left-wing -0.210, Right-wing -0.120,
Russian -0.109, Ukrainian -0.089, Western -0.080, Resistance -0.028), with Zionist the sole
exception (+0.056, LDA slightly beats Soft there). Classic LDA's 50 coarse topics carry
substantially less narrative-discriminating signal than BERTopic's 282 fine-grained clusters,
even when LDA is given as a full dense distribution (no top-K truncation).

**Is the added complexity worth it?** No. `soft` and `lda` are strictly more complex to compute
(batched `.approximate_distribution()` / `get_document_topics()` at both train and inference
time) and both perform *worse* than the simple one-hot `hard` representation already used in
production. The most likely mechanism: `TopicFeatureLayer`'s weighted-sum-over-embedding-rows
dilutes the strongest, most narrative-discriminative row whenever probability mass is spread
across multiple topics — and since ~91% of texts already have one dominant topic, this dilution
mostly adds noise rather than resolving genuine ambiguity. Soft distributions only pay off for
the minority of genuinely multi-topic texts, which isn't enough to offset the loss elsewhere.

**Final answer to "does Soft Topic Distribution improve Narrative Classification vs. Hard Topic,
and by how much?": No — it makes it worse, by about 4.7 points of Accuracy and ~0.046 points of
Macro-F1, averaged across 3 seeds with a robust, noise-dwarfing margin. Soft only wins on the
~9% of texts with no single dominant topic (+2.7pp Accuracy there); on the other ~91% of texts
it costs -6.0pp Accuracy, and it never helps any individual Narrative. The existing single hard
`topic_id` (`TopicStanceLayer`) representation already used in production is the better design
choice; classic LDA topic distributions are worse still. No change to the production model is
recommended based on this experiment.**

---

## 16. Experiment F — corpus-size × `min_topic_size` scaling validation

**Files:** [experiments/topic_modeling/corpus_subsampling.py](experiments/topic_modeling/corpus_subsampling.py) (stratified subsampling utility),
[experiments/topic_modeling/experiment_f_corpus_scaling.py](experiments/topic_modeling/experiment_f_corpus_scaling.py) (the sweep itself),
[experiments/topic_modeling/experiment_f_analysis.py](experiments/topic_modeling/experiment_f_analysis.py) (scoring/selection + scaling-law fit),
raw results in `reports/results/profiler_prototype/expF_corpus_scaling_results.json`,
`expF_stratification_report.json`, `expF_selection_and_scaling_law.json`.

**Goal:** Section 12's `recommend_min_topic_size()` heuristic (sqrt-scaling anchored at the
current 16,062-text corpus) was never actually tested against real data at other corpus sizes —
it was reasoned about by analogy to a k-means rule of thumb. This experiment empirically tests it:
build real corpus-size subsamples, sweep `min_topic_size` at each size, and let the data (not an
assumption) determine which scaling law — constant, linear, sqrt, log, or another simple form —
actually fits.

**Methodology:**
- **Corpus & preprocessing:** Same cleaning (`clean_text_for_topic_model` + `has_enough_content`)
  and near-duplicate removal (`deduplicate_texts`, threshold=0.7) as the production pipeline,
  applied to all 4 raw datasets (gemini/gpt/twitter/telegram) with `narrative_name`/
  `dataset_source` kept aligned per row (`load_cleaned_labeled_corpus()`, new — the existing
  `load_deduplicated_training_texts()` discards this alignment). Result: 16,510 raw → 16,341 after
  cleaning → 16,062 after dedup — matches the corpus size Experiments 6/7/12 already validated.
- **Sampling strategy:** 4 corpus sizes — 4,000 / 8,000 / 12,000 / "full" (16,062) — each drawn via
  `stratified_subsample()`, which allocates rows proportionally across all 28
  (dataset_source × narrative_name) strata using the largest-remainder method (avoids the
  systematic rounding bias naive per-stratum rounding would cause), then samples without
  replacement per stratum. Verified fidelity: max absolute deviation between the full corpus's and
  every subsample's per-source and per-narrative percentages was **≤0.03 percentage points** at
  every tested size — the 4-source/7-narrative mix is preserved essentially exactly. Subsample
  membership uses a *fixed* seed (42), independent of the UMAP seed swept below, so seed-stability
  comparisons at a given size are never confounded by also silently resampling different data.
- **Grid tested** (as proposed, not modified — already spans below/above/around the
  previously-validated mts=10 at every size): 4K→{5,10,15,20}, 8K→{5,10,15,20,25},
  12K→{5,10,15,20,25,30}, 16K(full)→{5,10,15,20,25,30,35}. 22 (corpus_size, min_topic_size)
  combinations × 2 UMAP seeds (42, 7) = **44 total fitted models**.
- **Everything else held fixed:** embedding model (`all-MiniLM-L6-v2`), UMAP
  (`n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine"`), the same representation
  pipeline validated in Experiment 5/C (`CountVectorizer(stop_words="english", ngram_range=(1,2))`
  + `ClassTfidfTransformer(reduce_frequent_words=True, bm25_weighting=True)` +
  `MaximalMarginalRelevance(diversity=0.3)`).
- **Runtime optimization:** SBERT embeddings are computed **once per corpus size** (cached to
  `data/cache/expF_embeddings_<size>.npy`) and passed into every `BERTopic.fit_transform(...,
  embeddings=...)` call for that size — embeddings don't depend on `min_topic_size` or the UMAP
  seed, only on the corpus itself, so this avoids 44 redundant re-encoding passes. All 44 configs
  ran end-to-end (fit + representation + metrics) in well under an hour of wall-clock time.
- **Metrics computed per config** (averaged across the 2 seeds for scoring): topic count, outlier
  %, micro-topic count/fraction (topics within `min_topic_size+10` docs of the floor), avg/median
  topic size, largest-topics + "top-2-combined %" mega-topic check, u_mass Topic Coherence and
  Topic Diversity (same method as Experiment 13/E — `gensim.CoherenceModel`, BERTopic's top-word
  phrases decomposed into single dictionary tokens), and hard/soft agreement + soft-signal
  coverage on the **same fixed n=280 stratified evaluation sample** (seed=42) reused by every prior
  experiment in this project (Experiments 6/7/9/10/11) — evaluated **in-memory** directly against
  each freshly-fitted `BERTopic` object (a tiny adapter class reusing
  `analyze_soft_topic_quality.run_batch_analysis`/`compute_summary_stats` verbatim), avoiding both
  `BERTopic.load()`'s documented embedding-resolution flakiness and saving 44 full model
  directories to disk.
- **Scoring rule (defined *before* looking at results, to avoid post-hoc metric shopping):** per
  (corpus_size, min_topic_size) candidate, seed-averaged metrics are combined into one composite
  score, each metric min-max normalized *within that corpus size's own candidate set*:
  `0.20·coherence + 0.10·diversity + 0.15·(1−outlier%) + 0.15·(1−micro_topic_frac) +
  0.10·(1−mega_topic%) + 0.10·agreement_rate + 0.10·soft_signal% + 0.10·(1−cross_seed_instability)`.
  **Hard vetoes** (excluded from selection regardless of score): top-2-combined % > 12.0 in either
  seed (mega-topic/over-merging, threshold set well below Experiment 6's already-rejected mts=25
  result of 17.2%), or topic count < 3 in either seed (degenerate collapse).

**Results — full per-candidate table** (seed-averaged; `outl%`=outlier %, `top2%`=mega-topic
top-2-combined %, `coh`=u_mass coherence, `div`=topic diversity, `agree%`=hard/soft agreement rate,
`soft%`=soft-signal coverage, `instab`=cross-seed instability, lower is more stable):

| size | mts | n_topics | outl% | top2% | coh | div | agree% | soft% | instab | score | |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4K | 5 | 167.0 | 33.8 | 4.3 | −9.101 | 0.615 | 60.9 | 65.9 | 0.038 | 0.359 | |
| 4K | **10** | 83.0 | 41.6 | 8.7 | −8.726 | 0.767 | 72.7 | 37.9 | 0.215 | **0.391** | **← selected** |
| 4K | 15 | 49.5 | 41.9 | 15.5 | −8.762 | 0.832 | 80.7 | 24.4 | 0.172 | 0.447 | vetoed (mega-topic) |
| 4K | 20 | 19.0 | 21.4 | 63.1 | −5.967 | 0.926 | 93.8 | 9.3 | 1.589 | 0.700 | vetoed (mega-topic) |
| 8K | 5 | 311.5 | 31.7 | 3.8 | −8.325 | 0.546 | 64.2 | 71.2 | 0.046 | 0.350 | |
| 8K | **10** | 172.5 | 38.2 | 4.5 | −8.028 | 0.660 | 78.2 | 53.8 | 0.023 | **0.634** | **← selected** |
| 8K | 15 | 89.0 | 37.4 | 16.4 | −8.255 | 0.752 | 76.6 | 35.8 | 0.021 | 0.497 | vetoed (mega-topic) |
| 8K | 20 | 66.5 | 39.4 | 16.8 | −8.139 | 0.786 | 72.5 | 25.4 | 0.034 | 0.483 | vetoed (mega-topic) |
| 8K | 25 | 48.5 | 35.8 | 22.4 | −8.085 | 0.821 | 82.6 | 19.1 | 0.022 | 0.678 | vetoed (mega-topic) |
| 12K | 5 | 427.0 | 32.0 | 4.0 | −8.270 | 0.501 | 64.8 | 71.8 | 0.051 | 0.394 | |
| 12K | **10** | 232.5 | 36.9 | 4.4 | −7.753 | 0.616 | 73.0 | 55.5 | 0.009 | **0.570** | **← selected** |
| 12K | 15 | 165.5 | 40.1 | 8.0 | −7.634 | 0.665 | 78.8 | 45.0 | 0.294 | 0.521 | |
| 12K | 20 | 101.0 | 39.4 | 18.8 | −7.438 | 0.728 | 74.3 | 34.9 | 0.071 | 0.597 | vetoed (mega-topic) |
| 12K | 25 | 65.5 | 35.0 | 26.0 | −8.033 | 0.790 | 72.3 | 24.1 | 0.278 | 0.467 | vetoed (mega-topic) |
| 12K | 30 | 44.0 | 28.5 | 40.3 | −7.634 | 0.848 | 75.7 | 13.8 | 0.382 | 0.631 | vetoed (mega-topic) |
| 16K(full) | 5 | 564.0 | 32.0 | 3.6 | −7.716 | 0.460 | 66.2 | 72.2 | 0.024 | 0.508 | |
| 16K(full) | **10** | 293.0 | 35.6 | 4.0 | −7.544 | 0.591 | 76.2 | 55.2 | 0.012 | **0.641** | **← selected** |
| 16K(full) | 15 | 212.5 | 38.5 | 4.5 | −7.475 | 0.647 | 74.2 | 47.2 | 0.090 | 0.590 | |
| 16K(full) | 20 | 155.5 | 41.2 | 7.3 | −7.301 | 0.698 | 80.7 | 41.2 | 0.184 | 0.617 | |
| 16K(full) | 25 | 103.5 | 39.2 | 16.1 | −7.235 | 0.744 | 80.7 | 31.2 | 0.198 | 0.651 | vetoed (mega-topic) |
| 16K(full) | 30 | 72.5 | 32.3 | 31.3 | −7.910 | 0.795 | 72.8 | 25.9 | 0.384 | 0.450 | vetoed (mega-topic) |
| 16K(full) | 35 | 56.5 | 31.2 | 37.4 | −7.990 | 0.826 | 75.0 | 20.0 | 0.205 | 0.509 | vetoed (mega-topic) |

**Final table (as requested):**

| corpus_size | best_min_topic_size | ratio_to_corpus | main_metrics |
|---|---|---|---|
| 4,000 | 10 | 0.00250 | n_topics=83.0, outlier%=41.6, coherence=−8.726, diversity=0.767 |
| 8,000 | 10 | 0.00125 | n_topics=172.5, outlier%=38.2, coherence=−8.028, diversity=0.660 |
| 12,000 | 10 | 0.00083 | n_topics=232.5, outlier%=36.9, coherence=−7.753, diversity=0.616 |
| 16,062 (full) | 10 | 0.00062 | n_topics=293.0, outlier%=35.6, coherence=−7.544, diversity=0.591 |

**The empirically best `min_topic_size` was 10 at *every single tested corpus size*** — it did not
need to shrink for smaller corpora (contradicting the untested sqrt heuristic from section 12,
which would have suggested ~5/7/9 at 4K/8K/12K) nor grow for the largest tested size. `mts=5`
scored worst at every size (far more micro-topics, visibly lower coherence/diversity, much lower
hard/soft agreement) — going below 10 is empirically never a win in this corpus. Larger values
(15+) generally score *reasonably* on coherence/diversity alone but get vetoed for mega-topic risk
at 4K/8K, and only become "safe" (non-vetoed) at 12K/16K without actually beating mts=10's
composite score — i.e., the hard veto (chosen conservatively from Experiment 6's precedent) is
doing most of the selection work here, not a strong intrinsic trend in the underlying score.

**Scaling-law fit:** with the resulting 4 points — (4000,10), (8000,10), (12000,10), (16062,10) —
fitting constant / linear-proportional / sqrt / log / general-power-law forms is almost a trivial
exercise since the y-value never moved: the **constant law (`min_topic_size = 10`) fits the tested
range essentially perfectly**, while sqrt/linear/log/power all fit strictly worse (any non-zero
slope necessarily overshoots or undershoots the flat empirical line). This is the headline,
data-driven answer to "how should `min_topic_size` change as corpus size grows": **within the
range we could actually test (4K–16K, a 4× range), it should not change at all.**

**Limitations (explicit):**
- Only 2 UMAP seeds per config (42, 7), not the ideal 2–3, for CPU-runtime reasons — cross-seed
  instability was generally low at mts=10 (0.009–0.215 across sizes) but this is a smaller
  stability check than Experiment 9's dedicated 3-seed study.
- Only 4 corpus-size data points, all landing on the same y-value — this makes the "constant"
  conclusion very solid *for the tested range*, but means there is **zero empirical evidence for
  corpus sizes beyond ~16,062 texts** (e.g. 100K, 1M). A mild, explicitly-flagged-as-unvalidated
  log-based extrapolation is applied beyond that point in the updated
  `recommend_min_topic_size()` (see below) purely as a conservative placeholder, not a finding.
- The evaluation sample for hard/soft agreement/soft-signal coverage (n=280, fixed across all 44
  configs and all 4 corpus sizes) is the same fixed sample used throughout this project, not a
  per-corpus-size-scaled sample — reused deliberately for comparability with all prior experiments,
  but means agreement/coverage numbers at different corpus sizes are evaluated against literally
  the same texts rather than a size-proportional held-out set.
- Models are evaluated purely in-memory (never saved) — this sidesteps `BERTopic.load()`'s
  flakiness but also means these 44 fitted models cannot be manually re-inspected later without
  re-running the sweep (results are recorded numerically in the JSON files above, not as browsable
  model artifacts).
- The interesting secondary observation that the "safe" (non-vetoed) `min_topic_size` ceiling
  itself crept up with corpus size (safe up to ~10–14 at 4K/8K, ~15–19 at 12K, ~20–24 at 16K) is
  based on only one veto-boundary crossing per size and was not itself statistically modeled —
  noted as a plausible hint for why *larger* corpora might eventually want a larger
  `min_topic_size`, not treated as a validated trend.

**`recommend_min_topic_size()` updated accordingly** (see
[src/narrative_lens/train_topics.py](src/narrative_lens/train_topics.py)): now returns the constant 10 for any corpus size up to
~16,062 (empirically validated by this experiment), and only applies a small, explicitly-flagged
log-based increase beyond that anchor (`10 + 5·ln(corpus_size / 16062)`, e.g. ≈19 at 100K, ≈31 at
1M — much gentler than the old sqrt formula's 25/79) as a clearly-labeled, unvalidated
extrapolation placeholder for corpora this project has not tested. As before, this remains a
**starting point**, not a guaranteed optimum — a substantially different future corpus (in size,
domain, or language mix) should still be re-validated with the same sweep methodology used here.

**Decision:** Supersedes section 12's heuristic. Pure utility-function change — does not touch
`fusion.py`, `train.py`, any checkpoint, or the production `min_topic_size=10` used by
`build_and_save_topics()`/`saved_topic_model_soft_v2`.

---

## 17. Narrative Classification — Hybrid Hard/Soft Topic Representation

**Goal (direct follow-up to section 15):** section 15 found that a single hard `topic_id`
beats the full top-5 Soft distribution overall (65.91% vs. 61.16% Accuracy), but that Soft wins
specifically on the ~8.8% of texts whose Soft distribution has no single dominant topic (72.1%
vs. 69.4% Accuracy on that subset, using a fixed, post-hoc `dominance_threshold=0.7`). This
raises the natural question: can a **per-example Hybrid rule** — Hard when the topic is
dominant enough, Soft otherwise — combine the best of both and beat the Hard-only baseline
overall? Critically, the threshold that defines "dominant enough" must be chosen **without any
test-set leakage** (validation set only), otherwise any apparent gain would be an artifact of
threshold-shopping on the test set. Per the explicit user constraint, the Topic Modeling phase
itself (BERTopic tuning, `min_topic_size`, embedding model) is closed and untouched — this
experiment only changes how the already-fixed BERTopic output is fed to the classifier.

**Representation mechanics verified before designing Hybrid (`experiments/feature_ablation/narrative_topic_compare.py`,
read in full, unmodified):** `TopicFeatureLayer` is a single `nn.Embedding(vec_size,
NUM_NARRATIVES)` table consumed via `dense_vec @ table.weight`. Hard's one-hot vector and Soft's
top-5-renormalized distribution vector already live in the exact same `bertopic_vec_size=283`-
dimensional space — so a "Hybrid" representation requires **no new layer type**, only a
per-example choice of which precomputed dense vector (Hard's one-hot or Soft's distribution) to
feed into the identical table for that example.

**Hybrid design:**
- **Routing rule:** for each example, if the Soft distribution is "dominant enough" (per a
  chosen criterion/threshold below), feed the Hard one-hot vector; otherwise feed the Soft
  distribution vector. Both vectors already exist in `narrative_topic_compare.py`'s cache
  (`hard_dense`, `soft_dense`) — Hybrid only builds a third `hybrid_dense` array by selecting,
  row-by-row, one of the two, and reuses `TopicFeatureLayer`/`TopicAblationDetector` unmodified
  via `import narrative_topic_compare as ntc` (with an in-process-only
  `ntc.TOPIC_MODES = ntc.TOPIC_MODES + ("hybrid",)` extension — the file on disk is never
  edited). Rest of the architecture (fusion network, NER/SRL/Emotion/Reliability arms, training
  loop, hyperparameters, seeds 42/7/123) identical to section 15, by direct reuse/import.
- **Dominance criteria tested:** (a) `top1_score` — the Soft distribution's own highest score,
  swept over `{0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9}`; (b) `margin` — top1 score minus
  top2 score, swept over `{0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5}`.

**Leakage-free threshold selection (validation set only, no retraining required):** the
already-trained reference checkpoints `hard_seed42.pth`/`soft_seed42.pth` from section 15 are
loaded **read-only, for inference only** (never retrained) and evaluated on the VAL split only.
For each candidate threshold, a hybrid prediction is *simulated* by swapping per-row between the
Hard model's prediction and the Soft model's prediction according to the dominance rule
(`hard_pred[i] if dominant else soft_pred[i]`), and VAL Macro-F1 of this simulated swap is
recorded. The threshold/criterion combination that maximizes VAL Macro-F1 is selected — the test
set is never touched during this step (see `reports/results/narrative_topic_hybrid/threshold_selection.json`
for the full candidate table and an explicit note confirming this). This avoids training N
separate hybrid models just to search thresholds, and cannot leak test information into the
selection.

**Threshold sweep result:** every one of the 17 candidates (9 `top1_score` + 8 `margin`) scored
a VAL Macro-F1 in the narrow range **0.612–0.618** — notably, *none* of them approached Hard-
only's own typical Macro-F1 (~0.65). The best candidate was `top1_score=0.3` (VAL Macro-F1 =
0.6181), routing 52.4% of VAL rows to Hard and 47.6% to Soft. This was selected as the final
threshold. **This sweep result was itself an early warning sign:** even the best possible
per-row swap between two independently-trained Hard/Soft models never matched Hard-only's own
solo performance — foreshadowing that a genuinely mixed representation was unlikely to help.

**Artifacts (separate from section 15, no existing files touched):** new cache
(`data/cache/cached_features_narrative_topic_hybrid.pt`), new checkpoints
(`models/experiments/narrative_topic_hybrid/hybrid_seed{42,7,123}.pth`), new results file
(`reports/results/narrative_topic_hybrid/results.json`), new threshold-selection file
(`reports/results/narrative_topic_hybrid/threshold_selection.json`). Nothing under
`models/experiments/narrative_topic_compare/`, `reports/results/narrative_topic_compare/results.json`,
or `data/cache/cached_features_narrative_topic_compare.pt` was modified.

**Results.** Hybrid trained across the same 3 seeds (42/7/123); test-set metrics, mean±std,
alongside all section-15 configs for direct comparison:

| Config | Accuracy | Macro-F1 | Weighted-F1 |
|---|---|---|---|
| `none` (no topic feature) | 50.49% ± 0.31 | 0.4951 ± 0.0033 | 0.5080 ± 0.0029 |
| `hard` (single BERTopic id) | **65.91% ± 0.27** | **0.6522 ± 0.0027** | **0.6580 ± 0.0026** |
| `soft` (top-5 BERTopic distribution) | 61.16% ± 0.17 | 0.6066 ± 0.0014 | 0.6119 ± 0.0020 |
| `lda` (full K=50 LDA distribution) | 53.02% ± 0.30 | 0.5212 ± 0.0029 | 0.5315 ± 0.0028 |
| `hybrid` (dominant→Hard, else→Soft, threshold from VAL only) | 60.79% ± 0.30 | 0.6036 ± 0.0026 | 0.6080 ± 0.0026 |

**Headline finding — Hybrid does not beat Hard, and barely differs from Soft.** Hybrid scores
60.79% Accuracy / 0.6036 Macro-F1, essentially tied with (fractionally below) plain `soft`
(61.16% / 0.6066) and well below `hard` (65.91% / 0.6522): **-5.13pp Accuracy, -0.0487 Macro-F1
vs. Hard**. Ranking is unchanged from section 15: **Hard > Soft ≈ Hybrid > LDA > None.**

**Subset analysis (test set, reference seed=42) — % routed to Soft and single-topic vs.
ambiguous breakdown:** with the VAL-selected threshold (`top1_score=0.3`), **47.96% of the test
set (1,188/2,477 rows) was routed to Soft** ("ambiguous"), and 52.04% (1,289/2,477) was routed to
Hard ("single-topic/dominant") — a near-even split, very different from section 15's illustrative
8.8%/91.2% split (which used a fixed, not VAL-selected, `dominance_threshold=0.7`).

| Subset | n | Hard-only acc | Soft-only acc | Hybrid acc |
|---|---|---|---|---|
| Single-topic (dominant) | 1,289 (52.0%) | 71.37% | 69.74% | 70.67% |
| Ambiguous (non-dominant) | 1,188 (48.0%) | **60.77%** | 51.60% | 50.93% |
| Overall | 2,477 | 66.29% | 61.04% | 61.20% |

**Is the ambiguous-group improvement (if any) enough to help overall? No — because there is no
ambiguous-group improvement.** Unlike section 15's illustrative subset (where Soft beat Hard on
the multi-topic slice), here **Hard wins on *both* subsets**, including the "ambiguous" one
(60.77% vs. 51.60% for Soft, vs. 50.93% for Hybrid — Hybrid is even fractionally worse than pure
Soft on the exact subset it's supposed to specialize in). The VAL-only threshold search
identified a much larger "ambiguous" population (48% vs. 8.8%) than section 15's fixed
threshold, and — critically — this larger population is *not* one where Soft/Hybrid actually
helps; Hard remains superior even there. This is the direct, honest consequence of choosing the
threshold in an unbiased way (maximizing VAL Macro-F1 of the swap simulation) rather than
picking `dominance_threshold=0.7` because it happened to show a Soft win on the test set.

**Per-Narrative comparison:** `hybrid_minus_hard` F1 is **negative for all 7 Narratives**
(Zionist -0.124, Resistance -0.047, Western -0.050, Russian -0.020, Ukrainian -0.047, Right-wing
-0.027, Left-wing -0.027 — Russian is the least hurt, Zionist the most, mirroring section 15's
`soft_minus_hard` pattern). No Narrative benefits from the Hybrid representation.

**Why didn't Hybrid help, given the routing rule is theoretically sound?** Two compounding
reasons, both traceable to the threshold-selection step itself: (1) the swap-simulation sweep
(the leakage-free, VAL-only search) never found *any* candidate threshold whose simulated
Macro-F1 approached Hard-only's own solo Macro-F1 — meaning even an oracle-free combination of
two independently-trained Hard/Soft models is a worse strategy than just always trusting Hard,
for this dataset; (2) training a **single shared `TopicFeatureLayer` table** on a mix of one-hot
(Hard-routed) and distributed (Soft-routed) input vectors dilutes what the table learns compared
to two separately specialized tables — the trained Hybrid model performs close to (and even
fractionally below) the simple `soft`-only model, not between `hard` and `soft` as hoped.

**Final answer to "does Hybrid Hard/Soft succeed in beating the Hard-only baseline of ~65.9%
Accuracy / 0.652 Macro-F1?": No.** Hybrid scores 60.79% ± 0.30% Accuracy and 0.6036 ± 0.0026
Macro-F1 — **-5.13pp Accuracy and -0.0487 Macro-F1 below Hard-only**, with the gap far larger
than the ~0.003 run-to-run seed noise (a robust, non-marginal result, not a fluke of one seed).
The leakage-free, VAL-only threshold search itself already signaled this outcome (no candidate
threshold's simulated swap ever matched Hard-only's solo Macro-F1), and the subset analysis
confirms it directly: Hard wins on **both** the single-topic subset (71.37% vs. 70.67% Hybrid)
**and** the ambiguous subset (60.77% vs. 50.93% Hybrid) — there is no population segment where
routing to Soft helps once the threshold is chosen honestly rather than cherry-picked. The
existing production representation (single hard `topic_id`, i.e. `TopicStanceLayer`) remains the
best design found across sections 15 and 17 combined. No change to the production model is
recommended based on this experiment.**

---

## 18. Narrative Classification — Leave-One-Author-Out (LOAO) generalization test

**Question:** the production model (`baseline_fusion`) is always evaluated on a **random**
train/val/test split, where a given author's posts can appear in both train and test. This
leaves a genuine open question: does the model actually learn generalizable *narrative* signal
(entities, stance, rhetoric patterns), or does it partly memorize *author-specific* style, such
that its ~67% random-split accuracy is inflated by having already seen that same author's
"voice" during training? This is a real risk given `NER Weight` is consistently the single
heaviest learned module (~44–47% across all runs) — named entities can behave as an author/
account fingerprint (e.g. an account that always mentions the same handful of people/places)
rather than as a narrative signal that would transfer to a never-seen author.

**Baseline (for comparison):** the existing random-split `baseline_fusion` results
(`reports/tables/comparison_random_test.md`): overall Accuracy=67.06%, Macro-F1=0.6643; per-narrative
F1 for the three narratives tested here: Zionist=0.7354, Russian=0.6930, Left-wing=0.6231
(Right-wing's own F1, relevant below, is 0.6602).

**Change:** used `train.py`'s existing (previously untested end-to-end) `--split
leave_one_author` CLI mode. For one real account per narrative — chosen to have ~200 samples
and, where possible, direct relevance to existing open problems — **every single post by that
account** is held out as the test set, and the model is trained from scratch on all other
authors' posts (val also drawn from the remaining authors). Three accounts were run: `IDF`
(Zionist, Twitter), `MariaZakharova` (Russian, Telegram — the account at the center of the
pre-existing "maria/lying" open problem below), and `BernieSanders` (Left-wing, Twitter). Because
`build_shared_vocab()` is deliberately fit on train-only data (leak prevention), each held-out
author requires a **fully independent feature-extraction pass over the entire ~16,510-row
corpus** (~5–23h wall-clock each depending on machine load) — no cache/vocab reuse across runs
was attempted, to avoid introducing vocab-level leakage between splits.

**Success criterion (declared before running):** a recall drop of ≲10pp vs. the random-split
per-narrative F1 would be an acceptable generalization gap; a drop of >15–20pp would be
considered a concerning sign of author-style memorization rather than narrative generalization.

**Results:**

| Held-out account | Narrative | Test n | Baseline F1 (random split) | LOAO Test Accuracy/Recall | Gap | Dominant misroute |
|---|---|---|---|---|---|---|
| `IDF` | Zionist | 200 | 0.7354 | 53.50% | **-20.0pp** | → Resistance (62/200, 31.0%) |
| `MariaZakharova` | Russian | 200 | 0.6930 | 31.00% | **-38.3pp** | → Right-wing (115/200, **57.5%**) |
| `BernieSanders` | Left-wing | 200 | 0.6231 | 28.00% | **-34.3pp** | → Right-wing (100/200, **50.0%**) |

(Test-set Macro-F1/Macro-Precision/Macro-Recall figures reported by `train.py` for these runs —
e.g. BernieSanders' Macro-F1=0.0625 — are **not meaningful**: as `train.py` itself warns at
split time, a LOAO test set is by construction ~100% one narrative, so 6 of 7 classes have zero
support and drag the macro-average to near-zero. The single-narrative **recall** column above,
compared directly against that narrative's random-split F1, is the metric that actually answers
the generalization question.)

Module importance (learned fusion weights) stayed essentially constant across all three LOAO
runs and matched the random-split model's own profile — NER 44–47%, Stance 29–36%, SRL 13–23%,
Emotion 4–5% — so the drop is not explained by a shift in which module the model leans on; the
same (NER-heavy) architecture simply fails to transfer for these held-out authors.

**Finding 1 — all three accounts show a severe generalization gap, well past the "concerning"
threshold.** Every one of the three held-out authors lost **20 to 38 percentage points** of
recall relative to their narrative's balanced-split F1 — none came close to the ≲10pp
"acceptable" bar declared above. This is strong, consistent evidence that `baseline_fusion`
relies on signal that does not transfer cleanly to an unseen author within the same narrative —
i.e., meaningful author-specific memorization, not purely narrative-level generalization.

**Finding 2 — two of three accounts fail in the *same specific* way: mass misrouting to
Right-wing.** `MariaZakharova` (Russian) and `BernieSanders` (Left-wing) don't just score lower —
a majority of their test posts (57.5% and 50.0% respectively) are funneled into a single wrong
narrative, **Right-wing**, rather than spread across errors or confused with topically-adjacent
narratives. Right-wing is not an unusually "easy"/large catch-all class on the random split
(its own F1, 0.6602, is mid-pack, not the highest), which makes this a specific, non-trivial
attractor effect tied to these two held-out accounts rather than a generic majority-class bias.
This directly reinforces and sharpens the pre-existing "maria/lying" open problem — the concern
there was that a large topic cluster of troll-replies aimed at `@MariaVladimirovnaZakharova`
might be acting as an author-specific fingerprint rather than genuine Russian-narrative content;
this experiment shows that when that exact account is held out, the model doesn't just get
uncertain, it actively mispredicts Right-wing for the majority of her posts. `IDF` (Zionist)
fails differently — its errors go mostly to Resistance (31.0%), not Right-wing — showing the
attractor effect is not universal across all held-out authors, only specific to (at least) these
two.

**Final answer to "does `baseline_fusion` generalize to unseen authors, or memorize account
style?": mostly the latter.** All three tested accounts exceeded the pre-declared "concerning"
generalization-gap threshold (20–38pp recall loss vs. random-split F1), and two of three show a
qualitatively distinct failure mode — systematic misrouting into Right-wing rather than diffuse
uncertainty — rather than merely lower-confidence correct predictions. This is evidence the
model has learned some amount of author-specific/stylistic signal (plausibly entity-fingerprint-
driven, given NER's consistently dominant module weight) in addition to genuine narrative
content signal. No architecture change is made as a direct result of this experiment (it is a
diagnostic, not a fix), but it is a materially important caveat on the ~67% random-split accuracy
figure quoted elsewhere in this document, and it sharpens (without resolving) the existing
"maria/lying" open problem into a concrete, reproducible symptom (57.5% same-target misroute).
Investigating *why* Right-wing specifically acts as an attractor for two different held-out
narratives — and whether down-weighting NER or adding author-invariance regularization would
close the gap — is a natural, currently unexplored next step (see open problems below).

---

## 19. Feature Ablation + Soft Topics on unseen (LOAO) authors — which feature helps/hurts generalization?

**Status: COMPLETE.** All 3 authors × 7 variants trained/evaluated, aggregate summary and a
Right-wing "shortcut" forensic analysis both run — see `experiments/author_generalization/narrative_ablation_loao.py`,
`experiments/author_generalization/narrative_ablation_rw_shortcut.py`, `reports/results/narrative_ablation_loao/`.

**Research question.** Section 18 showed `baseline_fusion` generalizes poorly to unseen
authors (20–38pp recall loss vs. random-split F1), with 2 of 3 held-out accounts
systematically misrouted to Right-wing. *Which* feature group is responsible — does NER
(entity/style memorization) hurt generalization, does any feature help, do Soft Topics
(a distribution over topics instead of one hard id) improve generalization or reduce the
Right-wing bias, and which combination gives the best unseen-author result? Per explicit user
instruction, this is an ablation-only diagnostic — no Domain-Adversarial Training or other
architecture change is introduced at this stage.

**Hypothesis.** NER (or another author-identifying, near-lexical feature) contributes
disproportionately to the unseen-author generalization gap and to the Right-wing attractor
effect, because it is the module fusion.py's own printed weights (section 18) show as
consistently dominant; a semantic-only signal (SBERT) or a smoother, less identity-specific
topic signal (Soft Topic Distribution) should generalize better than hard, near-lexical
features (NER/Stance-hard-topic).

**Setup.** Same 3 held-out real accounts as section 18 (`IDF` → Zionist, `MariaZakharova` →
Russian, `BernieSanders` → Left-wing), same exact train/val/test split per author
(`train.split_leave_one_author`, unmodified, imported directly — same `random_state=42`, byte-
identical row membership to section 18's runs, verified by a by-position label-alignment check
against section 18's own cache before any reuse). NER/SRL/Emotion/Reliability features are
reused **by position** from section 18's own cache
(`data/cache/cached_features_baseline_fusion_loao_{author}.pt`) — only SBERT embeddings and
hard/soft BERTopic features are computed fresh, both from the SAME single BERTopic model
(`models/experiments/soft_v2_baseline_seeded`, the model `narrative_topic_compare.py` also
uses), so "hard id vs. soft distribution" is isolated as the only difference between the two
topic variants. One fixed seed (42) is used for every variant/author (fair, simple
comparison, not a variance study). Checkpoints are selected purely by validation Macro-F1;
the held-out author's test rows are never used for tuning. All outputs go to dedicated,
non-overwriting paths: `data/cache/cached_features_ablation_loao_{author}.pt`,
`models/experiments/narrative_ablation_loao/{variant}_{author}.pth`,
`reports/results/narrative_ablation_loao/` (confusion matrices + `results.json` + `ablation_summary.csv`).
Nothing from section 18 (or any other canonical file) is touched.

**Variants** (all "SBERT + X", identical MLP architecture — `Linear(combined_dim,128) → ReLU →
Dropout(0.3) → Linear(128,7) → Softmax` — only the concatenated feature arms differ):

| # | Variant | Arms concatenated with SBERT |
|---|---|---|
| 1 | `sbert_only` | *(none — SBERT embedding alone)* |
| 2 | `sbert_ner` | NER |
| 3 | `sbert_stance_hard_topic` | Stance (hard BERTopic topic id) — **note:** in this codebase "Stance" *is* the hard topic id (`TopicStanceLayer`/`features["stance"]`); there is no separate stance signal, so this variant also stands in for the optional "SBERT+Hard Topic" request — same model/result, not duplicated |
| 4 | `sbert_srl` | SRL |
| 5 | `sbert_all_engineered` | NER + SRL + Emotion + Stance/Hard-Topic + Reliability (mirrors `HybridNarrativeDetector`'s engineered set, minus `agenda_ideology`) |
| 6 | `sbert_soft_topic` | Soft Topic Distribution (top-5 `approximate_distribution()`, re-normalized) |
| 7 | `sbert_all_engineered_plus_soft` | variant 5's arms + Soft Topic Distribution added on top |

**Metrics** (per variant × per author, plus a 3-author average): Accuracy, Macro-Precision/
Recall/F1 (macro figures are **not** the primary comparison metric here — same caveat as
section 18: each author's test set is ~100% one narrative, so per-class macro figures mostly
reflect that one class), **Recall of the true/held-out-author narrative** (= test accuracy,
the primary comparison metric, consistent with section 18), confusion matrix (CSV per
variant/author), **% of test examples misclassified as Right-wing**.

**Results.** Recall of the true/held-out-author narrative (= test accuracy) and % of test
examples misclassified as "Right-wing", per variant × author, plus the 3-author average
(full numbers, including macro-precision/recall/F1, in `reports/results/narrative_ablation_loao/
results.json` and `ablation_summary.csv`; confusion matrices per variant/author as CSV):

| Variant | IDF recall | IDF →RW% | Maria recall | Maria →RW% | Bernie recall | Bernie →RW% | **Avg recall** | **Avg →RW%** | Avg macro-F1 |
|---|---|---|---|---|---|---|---|---|---|
| `sbert_only` (baseline) | 63.5% | 2.5% | 89.5% | 2.5% | 24.5% | **57.5%** | 59.2% | 20.8% | 0.1218 |
| `sbert_ner` | 73.0% | 2.0% | 84.5% | 2.5% | 21.0% | 57.0% | 59.5% | 20.5% | 0.1076 |
| `sbert_stance_hard_topic` | 52.5% | 3.0% | 77.0% | 7.5% | 26.5% | 52.0% | 52.0% | 20.8% | 0.1044 |
| `sbert_srl` | 52.5% | 4.0% | 79.0% | 1.0% | 36.0% | 45.0% | 55.8% | 16.7% | 0.1000 |
| **`sbert_all_engineered`** | 67.0% | 3.5% | **91.5%** | 4.0% | 23.0% | 54.0% | **60.5%** | 20.5% | 0.1197 |
| `sbert_soft_topic` | 51.5% | 3.0% | **91.5%** | **1.0%** | 34.0% | 46.0% | 59.0% | **16.7%** | 0.1191 |
| `sbert_all_engineered_plus_soft` | 67.5% | 2.5% | 66.5% | 20.5% | 35.0% | 42.0% | 56.3% | 21.7% | 0.1011 |

(macro-F1 is the same low-hundreds-of-a-point figure as section 18 for the same reason: each
author's test set is ~100% one narrative, so macro figures mostly reflect one class — not the
primary comparison metric here, reported only for completeness.)

**Right-wing "shortcut" forensic analysis** (`experiments/author_generalization/narrative_ablation_rw_shortcut.py`, using the
`sbert_all_engineered` variant's predictions — closest to production `HybridNarrativeDetector`
— comparing entities/words/hard-topics in each author's Right-wing-misclassified test rows
against a 500-example sample of Right-wing's own training data; full lists in
`reports/results/narrative_ablation_loao/rw_shortcut_forensic.json`):

- **MariaZakharova**: only 8/200 test rows misclassified as Right-wing under this variant — too
  small a sample for a reliable lexical/entity signal. The one notable overlap: **all 8** of her
  misclassified rows land in hard-topic id 2 ("lying world, god diplomat, diplomat, madame
  forgive, world russianstatterrorist") — this is the same "maria/lying" topic flagged as an
  open problem earlier in this document — but that topic has only 1 Right-wing training
  example, so the topic feature itself is not pulling these rows toward Right-wing; something
  else in the combined feature vector is.
- **BernieSanders**: 108/200 test rows misclassified as Right-wing — a much larger, more
  reliable sample. Here the overlap is strong and consistent: the top shared **entities** are
  `trump` (45 occurrences in Bernie's misclassified rows vs. 64 in Right-wing's own training
  sample), `americans` (24 vs. 11), `congress` (11 vs. 5), `america` (11 vs. 10), `american`
  (10 vs. 15), `republicans` (7 vs. 5) — i.e. exactly the entities most central to Right-wing's
  own training corpus. The top shared **hard topics** are Bernie-specific policy topics
  (topic 62 "working people / democratic primary", topic 138 "health care / medicaid /
  republicans", topic 13 "wealth tax / billionaires") that have only a handful (2–6) of
  Right-wing training examples each — so, like Maria, the *topic* signal is not the shared
  driver. The **entity** overlap is the standout signal: Bernie (a US senator) and Right-wing's
  training corpus (largely US right-wing political commentary) both discuss Trump, Congress,
  Republicans and "Americans" heavily — same entities, opposite stance — and the NER-based
  entity-embedding arm has no stance/sentiment signal, only entity identity, so it pushes both
  toward the same narrative vector regardless of which side of the argument the text is on.

**Interpretation.**
1. **Does NER hurt generalization?** Mixed, not a clean "yes" — `sbert_ner` actually helps IDF
   substantially (63.5%→73.0% recall) but slightly hurts MariaZakharova (89.5%→84.5%) and
   BernieSanders (24.5%→21.0%), and does not meaningfully change either author's Right-wing
   misrouting rate on its own. The forensic analysis, however, shows NER (inside
   `sbert_all_engineered`) *is* the most plausible mechanism behind BernieSanders' Right-wing
   misrouting specifically — not because NER is "bad" in general, but because Right-wing's own
   training corpus and Bernie's genuinely different-narrative content share the same top
   entities (Trump, Congress, Republicans, Americans) with opposite stance, and the entity
   arm has no stance signal to tell them apart. So: NER doesn't hurt generalization *on average*,
   but it is a specific, identifiable driver of the Right-wing attractor for at least one author.
2. **Does anything help?** `sbert_all_engineered` gives the best average recall (60.5%, vs.
   59.2% baseline) — a modest, not dramatic, improvement — driven mostly by MariaZakharova
   (89.5%→91.5%) and IDF (63.5%→67.0%); it does not help BernieSanders (23.0% vs. 24.5%
   baseline) and does not reduce his Right-wing misrouting (54.0% vs. 57.5%). No single
   engineered feature or combination produces a clear win across all 3 authors simultaneously.
3. **Do Soft Topics beat Hard Topics?** Yes, clearly, on both metrics tested here:
   `sbert_soft_topic` (avg recall 59.0%, avg →RW 16.7%) beats `sbert_stance_hard_topic` (avg
   recall 52.0%, avg →RW 20.8%) for every one of the 3 authors individually on recall, and on
   Right-wing misrouting for Maria (7.5%→1.0%) and Bernie (52.0%→46.0%). A smoother distribution
   over topics generalizes better to an unseen author than a single hard topic id.
4. **Do Soft Topics reduce the Right-wing bias?** Yes, specifically for the two authors that
   showed it in section 18: MariaZakharova 2.5%→1.0%, BernieSanders 57.5%→46.0% (comparing
   `sbert_soft_topic` to the `sbert_only` baseline) — the largest Right-wing-misrouting
   reduction of any single variant tested, though it costs IDF's own recall (63.5%→51.5%, IDF
   never showed the Right-wing pattern to begin with, so this is an acceptable trade for the
   authors that actually need it).
5. **Which combination gives the best unseen-author result?** No variant dominates on every
   metric/author — this is itself a finding, not an omission. `sbert_all_engineered` wins on
   average recall; `sbert_soft_topic` wins on average Right-wing-bias reduction; combining both
   (`sbert_all_engineered_plus_soft`) is the **worst** choice tested — MariaZakharova's recall
   collapses (91.5%→66.5%) and her Right-wing rate jumps (4.0%→20.5%) when every arm is stacked
   together, a clear overfitting/feature-conflict symptom, not an additive improvement. Simpler,
   single-arm additions to SBERT generalize more reliably than throwing every feature in at once.

**Decision / next step.** No production change made — per the explicit scope of this
experiment, this was diagnostic/ablation only, not a fix. The clearest actionable findings for
a future iteration: (a) Soft Topic Distribution is the single most promising feature addition
for reducing the specific Right-wing-misrouting failure mode, and is a strong candidate to
integrate into `fusion.py` if unseen-author generalization becomes a priority (still gated by
the same open problem noted in this document — soft distribution is not yet wired into the
classifier); (b) the NER entity arm's lack of a stance/sentiment signal is a concrete,
falsifiable mechanism (not just a hypothesis) behind at least one author's Right-wing
misrouting, and is a natural first target if the user later revisits Domain-Adversarial
Training or a stance-aware entity representation; (c) feature-stacking without validation per
added arm (`sbert_all_engineered_plus_soft`) is actively harmful for at least one author and
should not be assumed safe by default in future ablations.

---

## Open problems (not resolved by any experiment above)

- **~34–36% outlier rate** persists across every configuration tried (preprocessing cleanup,
  dedup, mts=10/15/25/35, MiniLM vs. mpnet across 3 seeds each) — root-cause analysis attributes
  this most likely to real embedding-space sparsity/heterogeneity of a very mixed corpus (short
  tweets vs. long GPT/Gemini paragraphs), not to `min_topic_size` or the specific embedding model.
  Experiment B's seed=42 result looked like a modest improvement (35.8%→34.7%), but Experiment B's
  seed-stability check (Experiment 9) showed this reverses on average across seeds (mpnet's
  3-seed average, 35.6%, is actually worse than MiniLM's, 34.5%) - still a fully open problem.
  **Important nuance found in Experiment E (13):** this ~35% rate is the FIT-TIME outlier rate
  (`.topics_`) - BERTopic's `.transform()`, used for all new/inference-time text, essentially
  never reproduces it (99% of previously-outlier docs get reassigned to a real topic when
  re-transformed) - so this open problem affects the TRAINING corpus's clustering quality, not
  what downstream consumers (`stance.py`'s `TopicAnalysisPipeline`) see at inference time.
- **Hard/soft top-1 agreement ceiling around 54–76%** (varies by `min_topic_size` but with a
  large coverage cost at higher settings) is partly structural — hard labels come from
  HDBSCAN density clustering over UMAP-reduced embeddings, while soft scores come from
  token-level c-TF-IDF word overlap over raw text, a fundamentally different signal pathway.
- **Duplicate "rulesbased order" topic pair** was fixed via `min_topic_size` 25+ (rejected due to
  mega-topic collapse, Experiments 6-7). The embedding-model swap (Experiment B) merged it in 2
  of 3 seeds tested (not at seed=123) - a probability increase, not a reliable fix. Experiment D
  confirmed a targeted `merge_topics()` on just this one pair is clean (no other topic's document
  membership affected, modest quality improvement) and found NO other genuine duplicate pairs
  among the top-20 highest-scoring candidates out of all 39,621 pairs checked - but adoption on
  the production model is deferred to the user, so this remains technically open until applied.
- **The large "maria/lying" topic** (~195–198 docs of genuinely distinct troll-reply texts to
  @MariaVladimirovnaZakharova) is confirmed NOT a duplication artifact (Experiment 4) and is not
  affected by any `min_topic_size` setting tested — if still considered undesirable as a
  classifier feature, it would need a different, targeted approach (e.g. explicit
  troll-reply/near-target-mention down-weighting), not attempted here. **Section 18's LOAO test
  sharpened this into a concrete symptom:** holding out `MariaZakharova` entirely causes 57.5% of
  her posts to be misclassified as Right-wing (not just lower confidence) — consistent with, but
  not proof of, the classifier having partly fingerprinted her account rather than the Russian
  narrative itself. Root cause (NER-driven author fingerprinting vs. genuine content overlap
  between Russian-troll-reply rhetoric and Right-wing rhetoric) remains unestablished.
- **Author-style memorization vs. narrative generalization (Section 18, LOAO test):** all 3
  held-out authors tested (`IDF`, `MariaZakharova`, `BernieSanders`) lost 20–38pp of recall vs.
  their random-split F1, and 2 of 3 showed systematic misrouting into Right-wing specifically
  (57.5%, 50.0%) rather than diffuse errors. **Section 19's feature ablation + forensic analysis
  partially resolved this:** for BernieSanders, the mechanism is identifiable — the NER entity
  arm has no stance/sentiment signal, and his heavy mentions of Trump/Congress/Republicans/
  Americans (also the top entities in Right-wing's own training data, with opposite stance) get
  routed toward Right-wing regardless of stance; Soft Topic Distribution measurably reduces
  (not eliminates) this specific failure mode (Bernie 57.5%→46.0%, Maria 2.5%→1.0%) at some cost
  to authors that didn't show the pattern (IDF). Still not investigated: whether this
  generalizes to more held-out authors beyond these 3, or whether a full fix (down-weighting
  NER, a stance-aware entity representation, author-invariance/adversarial training, more
  authors per narrative in training) would close the remaining gap — no fix attempted, section
  19 was diagnostic/ablation only, per explicit user scope.
- **Soft distribution is still not integrated as a classification feature** in `fusion.py`/
  `train.py` — every experiment above was explicitly scoped to stay out of the classifier. Doing
  so would also need to apply `clean_text_for_topic_model()` at inference time for
  `saved_topic_model_soft_v2` (already handled by `stance.py`'s `use_cleaned_preprocessing` flag)
  and would require re-deciding the `min_topic_size`/embedding-model questions above with the
  classifier's needs in mind, not just topic-model-internal quality metrics.
- Experiment B (embedding model swap) and a possible targeted post-hoc merge of only confirmed
  duplicate topic pairs (instead of a blanket `min_topic_size` increase) remain proposed,
  unimplemented next steps.

---

## 20. Hard Topic vs. Soft Topic Distribution vs. LDA Distribution for Narrative Classification — SBERT-backbone, controlled comparison

**Status: COMPLETE.** All 4 Topic representations (`none`/`hard`/`soft`/`lda`) × 3 seeds
(random split) + 3 authors (LOAO, `lda` mode only — `none`/`hard`/`soft` reused from Section 19)
trained/evaluated; completeness verified programmatically; 4 sanity-check categories run and
passed; full reports built. See
`experiments/feature_ablation/narrative_topic_sbert_backbone.py`,
`reports/results/narrative_topic_sbert_backbone/`.

**Research question.** Section 15 compared Hard/Soft/LDA inside `baseline_fusion`'s full
linear-weighted-fusion architecture (NER+Topics+SRL+Emotion arms) and found **Hard > Soft > LDA
> None** on a random split. Section 19 separately found, inside a *different*, simpler
"SBERT + single engineered arm" architecture, that on unseen authors (LOAO) **Soft clearly
beat Hard** on both recall (59.0% vs. 52.0%) and Right-wing bias (16.7% vs. 20.8%) — the
opposite ranking. This experiment isolates the Topic-representation question as cleanly as
possible from *both* confounds at once: (a) a single, minimal, SBERT-only backbone (no NER/SRL/
Emotion/Stance arms at all, so the Topics arm cannot be diluted or entangled by other engineered
features, unlike Section 15/19's architectures) and (b) **both** evaluation regimes — random
split (3 seeds, for statistical robustness) *and* the same 3 held-out authors used in Sections
18/19 (for generalization) — run side-by-side under the identical architecture, so any
random-vs-LOAO ranking reversal can be attributed to the evaluation regime itself, not to an
architecture difference.

**Setup.** `SBERTTopicDetector`: `sbert_embedding` (384-dim, frozen SBERT) optionally
concatenated with one Topic arm's `TopicFeatureLayer(mode, vec_size)` output (7-dim, same
`dense_vec @ table` mechanism as Sections 15/17/19 — see their write-ups for the design
rationale), then `Linear(combined_dim,128) → ReLU → Dropout(0.3) → Linear(128,7) → Softmax`.
Four modes: `none` (no Topic arm, zero learnable parameters in that arm — the SBERT-only
control), `hard` (BERTopic one-hot id), `soft` (top-5 `approximate_distribution()`,
re-normalized — `SOFT_TOP_N=5`), `lda` (full K=50 gensim distribution,
`models/experiments/lda_baseline/lda_k50_seed42`, the same frozen baseline Experiment E fit).

- **Random split:** `train.load_raw_data()`+`train.split_random()` imported unmodified and
  called directly (identical `random_state=42` row membership to Section 15's own random-split
  runs). Features are a zero-recomputation **recombination** of two already-existing caches —
  `sbert_embedding` from `train.py`'s own `cached_features_sbert_only.pt`, `hard_dense`/
  `soft_dense`/`lda_dense` from `narrative_topic_compare.py`'s
  `cached_features_narrative_topic_compare.pt` (Section 15's own cache) — both verified
  byte-for-byte row-aligned (by a fresh label-sequence reconstruction check) before being
  trusted, not assumed. 3 seeds (42/7/123, this project's standard set) × 4 modes = 12 runs,
  20 epochs each, Adam + NLLLoss, early stopping on Val Macro-F1 (patience=3), matching
  `train.py`'s training loop exactly.
- **LOAO (unseen author):** same 3 held-out real accounts as Sections 18/19 (`IDF`→Zionist,
  `MariaZakharova`→Russian, `BernieSanders`→Left-wing), same `train.split_leave_one_author`
  (unmodified, imported directly, internally calls `verify_no_leakage()` — re-confirmed leak-free
  for all 3 authors during this experiment's own fresh-split reconstruction). `none`/`hard`/
  `soft` results are **reused, not re-trained** — Section 19's `sbert_only`/
  `sbert_stance_hard_topic`/`sbert_soft_topic` variants are architecturally identical to this
  script's `none`/`hard`/`soft` modes (same `combined_dim` formula, same `TopicFeatureLayer`
  class, same MLP shape, same EPOCHS/BATCH_SIZE/LEARNING_RATE/seed=42/patience=3 — verified
  programmatically by `verify_loao_reuse_validity()`, not just asserted), so re-running them
  would be pure duplication. Only `lda` is genuinely new per author: the existing
  `cached_features_ablation_loao_{author}.pt` cache (SBERT/NER/SRL/Emotion/Reliability/hard/
  soft, from Section 19) is augmented with a freshly-computed `lda_dense` field only (LDA
  inference is cheap, no neural computation) — nothing already-cached is recomputed. One fixed
  seed=42 per author (matches Section 19's own convention, not a variance study).

**Fairness / dimensionality note.** Soft's underlying BERTopic table has 283 rows (282 topics +
1 OOV) vs. LDA's 50 rows (K=50) — a real difference in `TopicFeatureLayer`'s *parameter count*
(283×7=1,981 vs. 50×7=350). This does **not** advantage either variant at the classifier level:
`TopicFeatureLayer` always projects its (possibly much larger) input distribution down to a
7-dim (`NUM_NARRATIVES`) vector via `dense_vec @ table` before concatenation with SBERT, so the
final MLP sees the exact same `sbert_dim + 7` input dimensionality for `hard`/`soft`/`lda` alike
— only the number of *learnable table rows* differs, an inherent property of each topic model's
own vocabulary size, not an experimental design choice.

**Verification performed before trusting any result (per explicit requirement):**
1. `verify_random_split_completeness()` — confirmed all 4×3=12 (mode, seed) random-split runs
   completed with valid (finite, in-range) accuracy/Macro-F1 and an on-disk checkpoint. **PASSED.**
2. `verify_loao_reuse_validity()` — confirmed the reused `none`/`hard`/`soft` LOAO results come
   from an architecturally-equivalent model (same `combined_dim` formula, same feature-arm
   class, same training convention) to this script's own `lda` runs, for all 3 authors.
   **PASSED.**
3. `run_sanity_checks()` — 4 categories, all **PASSED**:
   - Random-split cache: 11,557/2,476/2,477 train/val/test rows, no zero-count narrative class
     in any split, `sbert_dim=384`, `bertopic_vec_size=283`, `lda_vec_size=50`.
   - Non-degeneracy: `lda_dense` sums to 1.0 for all 2,477 test rows (never all-zero, as
     expected — LDA has no outlier concept). `soft_dense` is all-zero for 1,187/2,477 (47.9%)
     test rows — **investigated, not dismissed:** this is a documented, pre-existing property
     of the underlying BERTopic model/corpus, not a bug introduced here — it matches Section 9's
     "soft-signal%" finding almost exactly (51–58% of documents get *any* positive-score topic
     from `approximate_distribution()`, i.e. ~42–49% get an all-zero distribution) and Section
     15's dominance-threshold finding (only 8.8% of rows are genuinely "multi-topic" — the vast
     majority, whether zero-signal or not, are single-topic-dominated). Among the 1,290 rows
     that DO have a soft signal, the mean nonzero-entry count is 1.39 (of a possible top-5) —
     consistent with the same finding, not a new anomaly.
   - LOAO+lda caches (all 3 authors): correct row counts, correct single-narrative test-set
     composition (matches Section 18/19's known 100%-one-narrative LOAO test sets by design),
     non-degenerate `lda_dense` (sum=1.0, 0 all-zero rows, for all 3 authors' 200-row test sets).
   - Author leakage: structurally enforced by `split_leave_one_author()`'s internal
     `verify_no_leakage()` call, re-confirmed for all 3 authors during this experiment's cache
     construction (no assertion raised).
4. Full test suite (`pytest tests/`, 48 tests) re-run clean, 0 failures — see below.

**Results — Random split (mean ± std across 3 seeds, test set, n=2,477):**

| Variant | Macro-F1 | Accuracy | Δ Macro-F1 vs. SBERT (`none`) | Δ Accuracy vs. SBERT (`none`) | Δ Macro-F1 vs. Hard | Δ Accuracy vs. Hard |
|---|---|---|---|---|---|---|
| `none` (SBERT-only) | 0.7275 ± 0.0008 | 72.98 ± 0.05% | — (baseline) | — (baseline) | −0.0046 ± 0.0031 | −0.48 ± 0.29pp |
| **`hard`** | **0.7321 ± 0.0029** | **73.46 ± 0.29%** | **+0.0046 ± 0.0031** | **+0.48 ± 0.29pp** | — (baseline) | — (baseline) |
| `soft` | 0.7319 ± 0.0032 | 73.44 ± 0.29% | +0.0044 ± 0.0025 | +0.46 ± 0.25pp | −0.0002 ± 0.0054 | −0.03 ± 0.49pp |
| `lda` | 0.7299 ± 0.0020 | 73.22 ± 0.21% | +0.0024 ± 0.0028 | +0.24 ± 0.26pp | −0.0022 ± 0.0033 | −0.24 ± 0.34pp |

**Hard and Soft are tied on the random split.** The Hard-vs-Soft gap (−0.03pp Accuracy, −0.0002
Macro-F1) is roughly an order of magnitude smaller than the ±0.29–0.32pp / ±0.0029–0.0032
seed-to-seed std (computed legitimately across 3 seeds, a real if small measure of run-to-run
stability for this in-distribution split) — there is **no evidence of an advantage for Soft
over Hard in this in-distribution evaluation**, and none should be claimed. `hard`/`none` and
`lda`/`none` gaps (+0.48pp and +0.24pp respectively) are likewise small — real and consistent in
direction across all 3 seeds, but modest, not dramatic, effects.

**Results — LOAO / unseen-author (avg across IDF/MariaZakharova/BernieSanders, n=200 each):**

| Variant | Avg held-out recall | Avg Macro-F1 | Avg Right-wing bias (% misrouted) | Δ recall vs. SBERT (`none`) | Δ recall vs. Hard |
|---|---|---|---|---|---|
| `none` (SBERT-only) | 59.2% | 0.1218 | 20.8% | — (baseline) | +7.2pp |
| `hard` | 52.0% | 0.1044 | 20.8% | −7.2pp | — (baseline) |
| **`soft`** | 59.0% | 0.1191 | **16.7%** | −0.2pp | **+7.0pp** |
| `lda` | 57.8% | 0.1210 | 19.7% | −1.3pp | +5.8pp |

**Reading this table precisely.** Soft clearly beats Hard on both primary LOAO metrics (+7.0pp
recall, −4.1pp Right-wing bias). But Soft does **not** beat SBERT-only (`none`) on average
recall — 59.0% vs. 59.2%, i.e. essentially tied, marginally lower — so "Soft improves
generalization" would overstate the finding. The precise claim supported by this table: **Soft
topic distributions avoid much of the generalization degradation caused by hard topic IDs and
reduce systematic Right-wing misclassification, while maintaining SBERT-level average recall.**
Note also that the 3 LOAO authors are 3 distinct held-out accounts, not repeated random draws
of the same distribution (unlike the random split's 3 seeds) — there is no seed-style variance
estimate for the LOAO numbers above; each is a single point estimate per author, and "avg"
simply means the unweighted mean across the 3 authors, not a mean±std.

**Why LOAO Macro-F1 is low (~0.10–0.12) for every variant, and why it is a supplementary
metric here, not primary.** Each held-out author's LOAO test set is, by construction (Sections
18/19), ~100% a single narrative (e.g. IDF's 200 test rows are 100% Zionist). Macro-F1 is
nonetheless computed over all `NUM_NARRATIVES=7` classes: the 6 narratives absent from a given
author's test set mechanically contribute precision=recall=F1=0 (no true or predicted examples
of most classes ever appear in a single-author test set), which drags every variant's Macro-F1
down into the ~0.10–0.19 range regardless of how good the model's actual held-out-narrative
recall is — e.g. MariaZakharova's `soft` row scores 91.5% recall (a strong result) yet only
0.159 macro-F1, purely because 6 of 7 classes contribute 0. This is a structural property of
averaging over classes that were never present in a single-narrative test set, not a sign the
models are performing poorly. **The primary LOAO metrics in this experiment are therefore
recall of the true/held-out narrative and the % misclassified as Right-wing (the specific
failure mode Section 19 identified); avg Macro-F1 is reported for completeness/comparability
with Section 19's own table but should be treated as supplementary**, not as the main basis for
ranking variants on LOAO (see LDA in Q3 below, where Macro-F1 and recall/Right-wing-bias
disagree on the ranking).

**Per-author LOAO breakdown (recall of the true/held-out narrative, i.e. test accuracy, and %
misclassified as Right-wing):**

| Variant | IDF recall | IDF →RW% | Maria recall | Maria →RW% | Bernie recall | Bernie →RW% |
|---|---|---|---|---|---|---|
| `none` (SBERT-only) | 63.5% | 2.5% | 89.5% | 2.5% | 24.5% | 57.5% |
| `hard` | 52.5% | 3.0% | 77.0% | 7.5% | 26.5% | 52.0% |
| `soft` | 51.5% | 3.0% | **91.5%** | **1.0%** | 34.0% | 46.0% |
| `lda` | 58.0% | 2.0% | 89.0% | 3.0% | 26.5% | 54.0% |

(`none`/`hard`/`soft` rows above are reused verbatim from Section 19's `sbert_only`/
`sbert_stance_hard_topic`/`sbert_soft_topic` variants, verified architecturally equivalent —
see "Verification performed" above; `lda` is the only newly-trained row.)

**Answering the 6 questions directly:**

1. **Hard vs. SBERT-only (`none`) — does adding a Topic feature at all help?** On the random
   split, yes, but only modestly in this SBERT-only-backbone architecture: Hard beats SBERT-only
   by +0.48pp Accuracy / +0.0046 Macro-F1 — a real but small effect (roughly the same order as
   the seed-to-seed std, i.e. a soft rather than dramatic signal), a much smaller gap than
   Section 15's fusion-architecture result (+15pp Accuracy for `hard` vs. `none` there). On
   LOAO, Hard is *worse* than SBERT-only by −7.2pp recall — adding the Topic feature actively
   hurts unseen-author generalization here, the opposite of the random-split finding.
2. **Soft vs. Hard — does a distribution beat a single id?** No evidence of a Soft advantage
   (or a Hard advantage) on the random split: Hard and Soft are **tied** (−0.03pp Accuracy,
   −0.0002 Macro-F1, an order of magnitude smaller than the ±0.29–0.32pp seed-to-seed std) —
   this is best read as consistent with Section 15's "Hard ≥ Soft" *direction*, but the
   magnitude here gives no basis for claiming either representation is better in-distribution.
   **Yes on LOAO**, and by the largest margin in this table: Soft beats Hard by +7.0pp recall
   and by 4.1pp lower Right-wing bias (16.7% vs. 20.8%) — consistent with, and now replicated
   independently of, Section 19's finding that Soft was the best Right-wing-bias reducer there
   too. Soft does **not**, however, beat SBERT-only (`none`) on average LOAO recall (59.0% vs.
   59.2%) — see the precise framing in the LOAO results section above.
3. **LDA vs. BERTopic (both distributional) — does the specific topic model matter, not just
   "hard vs. soft"?** Yes, but LDA is a **middle ground**, not a clear loser. On the random
   split, LDA trails both Soft (−0.22pp Accuracy, −0.0020 Macro-F1) and Hard (−0.24pp Accuracy,
   −0.0022 Macro-F1) — same ranking direction as Section 15's `Hard > Soft > LDA > None`, though
   the gaps are much smaller here. On LOAO, LDA sits between Hard and Soft on recall (57.8%, vs.
   Hard 52.0% and Soft 59.0%) and on Right-wing bias (19.7%, between Hard's 20.8% and Soft's
   16.7%) — **but LDA's avg Macro-F1 (0.1210) is actually the highest of the four variants,
   slightly above even Soft's (0.1191)**, despite LDA's worse recall and worse Right-wing bias
   than Soft. This disagreement between Macro-F1 and recall/Right-wing-bias is itself informative
   (see the Macro-F1 note above) and means LDA should not be characterized as worse than Soft "in
   every metric." Overall: the specific topic model matters, not just "hard vs. distributional" —
   LDA is a usable middle-ground distributional alternative, not a substitute for BERTopic's soft
   distribution specifically.
4. **Random vs. unseen-author (LOAO) — does the ranking actually reverse, and does this
   architecture explain Section 15 vs. Section 19's apparent contradiction?** **Yes, confirmed,
   not smoothed over:** under this single, minimal, controlled architecture, Hard is (weakly)
   ahead of Soft on the random split (tied, no real evidence either way — Q2) while Soft is
   clearly ahead of Hard on LOAO — the exact same reversal Sections 15 and 19 showed, but this
   time isolated from any architecture difference between the two regimes (same
   `SBERTTopicDetector` class used for both). This confirms the reversal is attributable to the
   **evaluation regime itself** (in-distribution random split vs. out-of-distribution
   unseen-author generalization), not to Section 15 using a different (fusion) architecture than
   Section 19 (SBERT+single-arm) as previously hypothesized. **One possible interpretation**
   (a hypothesis, not something this experiment establishes causally) is that Hard's one-hot id
   can partly memorize author-specific topic co-occurrence patterns that don't transfer to an
   unseen author, while preserving a topic *distribution* rather than collapsing it to a single
   id reduces reliance on this kind of brittle topic shortcut. This experiment does not isolate
   or test that mechanism directly (e.g. no probing of what the model actually relies on) — it
   only establishes the *outcome* (the ranking reversal itself, Q2/Q4 above), not the causal
   reason for it. (Methodological note: the random-split comparison rests on 3
   seeds, a legitimate — if small — sample for estimating run-to-run stability; the LOAO
   comparison rests on 3 held-out **authors**, which are not repeated random draws of the same
   distribution and so cannot be used to estimate variance the same way — the LOAO numbers are
   single point estimates per author, not a seed-averaged mean±std.)
5. **Does Soft help accuracy, or mainly generalization/robustness?** Mainly the latter, and even
   there its concrete, defensible benefit is bias reduction rather than a raw recall gain. On the
   random split, Soft's Accuracy/Macro-F1 are tied with Hard (Q2) — it does not improve raw
   classification accuracy on data resembling the training distribution. On LOAO, Soft's
   advantage over Hard is real (+7.0pp recall, a much bigger swing than the random split's
   ±0.29pp seed std) and is concentrated in reducing the Right-wing misrouting failure mode
   (Section 19's own "shortcut" finding) — but Soft does not raise average recall above the
   SBERT-only baseline (59.0% vs. 59.2%). So Soft's contribution on LOAO is a reduction in a
   specific systematic error (Right-wing misrouting), not a general recall improvement over
   using no Topic feature at all.
6. **Is there a performance/robustness trade-off, and is the added complexity justified?** Yes,
   and it favors Soft once unseen-author generalization is a concern — but the justification is
   narrower than "Soft is generally better." Hard gives a small, seed-stable random-split
   improvement over SBERT-only (+0.48pp Accuracy) yet costs −7.2pp recall on LOAO relative to
   SBERT-only, i.e. it actively hurts generalization to an unseen author. Soft gives essentially
   the same random-split performance as Hard (no evidence of a difference, Q2) while avoiding
   most of Hard's LOAO recall degradation and additionally reducing systematic Right-wing bias
   relative to both Hard and SBERT-only (20.8% → 16.7%). On accuracy/recall alone, Hard and Soft
   are indistinguishable in effect on the random split, and neither beats SBERT-only's own LOAO
   recall by a meaningful margin (Hard is clearly worse; Soft is about equal). The added
   complexity of a distributional Soft Topic representation is therefore best justified as a
   **robustness/bias-reduction measure for deployment scenarios where generalization to unseen
   authors matters** (a real, currently-unsolved production concern per Sections 18/19) — **not**
   as a general in-distribution accuracy upgrade, and **not** as a LOAO recall upgrade over doing
   nothing (SBERT-only).

**Limitation: the Soft Topic feature is inactive for a large share of the corpus.** The sanity
check found `soft_dense` is all-zero for 1,187/2,477 (47.9%) of random-split test rows —
consistent with Section 9's previously-documented ~42–49% no-soft-signal rate
(`approximate_distribution()` finding no topic with positive overlap for that text), so this is
not a new defect introduced here. It does mean that for close to half the corpus the Soft Topic
arm contributes a constant zero vector — functionally identical to `mode="none"` for those rows
— so Soft's measured effects (both the random-split tie with Hard and the LOAO recall/
Right-wing-bias results) are driven entirely by the roughly half of rows that DO receive a
non-trivial soft signal. This caps how much benefit a coverage-limited Soft representation can
realistically provide and is a plausible contributing factor in why Soft ties (rather than
beats) SBERT-only on LOAO average recall. It is a natural target for improvement (e.g. a lower
`approximate_distribution()` threshold, or falling back to Hard's id when Soft is all-zero)
before considering production integration.

**Overall conclusion (bounded to what the data shows).**
- Hard topics give a small, seed-stable improvement on the random split (+0.48pp Accuracy vs.
  SBERT-only) but meaningfully hurt unseen-author (LOAO) generalization (−7.2pp recall vs.
  SBERT-only).
- Soft topics give essentially the same in-distribution performance as Hard (tied — no evidence
  of an advantage either way) but are far more robust when the author is unseen during training,
  avoiding most of Hard's LOAO recall degradation.
- Compared to SBERT-only, Soft Topics do **not** improve average LOAO recall (59.0% vs. 59.2%),
  but they **do** reduce systematic Right-wing misclassification (20.8% → 16.7%).
- The main current, evidence-backed contribution of Soft Topics is therefore **robustness /
  Right-wing-bias reduction**, not raw classification accuracy — any recommendation to adopt
  Soft should be scoped to that specific benefit, not stated as a general performance upgrade.

**What this does NOT resolve (explicitly, not smoothed over):** this experiment used a
deliberately minimal SBERT-only backbone to isolate the Topics-representation question; Section
15's much larger Hard-vs-Soft gap (+4.75pp Accuracy, `hard` vs `soft`, in the full
`baseline_fusion` architecture with NER/SRL/Emotion arms) is NOT reproduced here (this
experiment's random-split Hard-vs-Soft gap is ≈0pp, within noise) — architecture clearly still
matters for the *magnitude* of the Hard-vs-Soft gap, even though the *direction* of the
random-vs-LOAO reversal is architecture-independent (finding #4 above). Whether Soft Topic
Distribution would still help LOAO generalization if wired into the full production
`HybridNarrativeDetector`/`baseline_fusion` (rather than this SBERT-only diagnostic backbone)
remains untested — a natural next step given Soft's demonstrated, replicated (Section 19 + this
section) Right-wing-bias-reduction benefit.

**Implementation:** `experiments/feature_ablation/narrative_topic_sbert_backbone.py`. Reuses
`train.py`'s `load_raw_data()`/`split_random()`/`split_leave_one_author()` unmodified; reuses
Section 15's `cached_features_narrative_topic_compare.pt` and Section 19's
`cached_features_ablation_loao_{author}.pt` caches by position (verified, not assumed); adds
zero new heavy feature extraction beyond LDA inference for the 3 LOAO+lda runs. All results in
`reports/results/narrative_topic_sbert_backbone/` (`results_random.json`,
`results_loao_lda.json`, `random_split_summary_table.csv`, `loao_summary_table.csv`,
`per_narrative_summary_random.csv`, `per_narrative_summary_loao.csv`,
`unified_comparison.json`); checkpoints in
`models/experiments/narrative_topic_sbert_backbone/`. Full test suite (`pytest tests/`, 48
tests across `test_train_topics_cli.py`, `test_topic_preprocessing.py`, `test_text_dedup.py`,
`test_soft_topic_distribution.py`, `test_recommend_min_topic_size.py`,
`test_loao_split_leakage.py`, `test_config_loading.py`) re-run clean after this experiment's
code additions — 0 failures.

---

## 21. Entity Shortcut Test — does entity IDENTITY (not just topic/stance) drive the LOAO Right-wing shortcut?

**Status: COMPLETE.** All 3 LOAO authors run; masked-text cache built once over the full
corpus (16,394 unique texts) and reused across authors; 2 new variants trained per author (6
trainings total); 3 variants reused verbatim from Section 19 after a programmatic reuse-validity
check. See `experiments/author_generalization/narrative_entity_shortcut.py`,
`reports/results/narrative_entity_shortcut/`.

**Research question.** Section 19's Right-wing-shortcut forensic analysis
(`narrative_ablation_rw_shortcut.py`) found that BernieSanders' Right-wing-misclassified rows
share the same top entities (`trump`, `americans`, `congress`, `america`, `republicans`) with
Right-wing's own training corpus — Bernie and Right-wing discuss the same entities with
opposite stance, and the NER arm encodes entity *identity* only, with no stance signal. This
experiment tests that mechanism directly, by removing entity identity from the model's input
via masking and observing whether that changes recall of the true/held-out narrative and/or the
Right-wing-misclassification rate. This is a test of one specific, narrow hypothesis (identity
without stance can create a spurious cross-narrative association for entities two narratives
both discuss) — it is not a general claim about whether entities matter for classification
overall.

**Setup.** Every named entity mention (`PER`/`ORG`/`LOC`/`MISC`, from the same
`dslim/bert-base-NER` model already used by the production NER arm) is replaced by a generic
placeholder token before computing the SBERT embedding, e.g. `"Trump criticized Biden"` →
`"[PERSON] criticized [PERSON]"` (`mask_entities()`, `narrative_lens/features/ner.py`; entity
spans reconstructed via `reconstruct_fragmented_entities()` first so one fragmented name isn't
masked as several separate tokens). 5 variants compared on the same 3 LOAO authors, same
`split_leave_one_author` split, seed=42, as Sections 19/20:

1. **`sbert_only`** — REUSED verbatim from Section 19 (SBERT on original, unmasked text; no
   explicit entity arm — entity identity is only whatever the SBERT embedding implicitly
   encodes).
2. **`sbert_ner`** — REUSED verbatim from Section 19 (SBERT on unmasked text + an explicit
   NER-identity arm on top — entity identity maximally present).
3. **`sbert_masked` (NEW)** — SBERT embedding computed on entity-**masked** text, no other arm.
   This is the primary comparison: `sbert_only` (identity present) vs. `sbert_masked` (identity
   removed) isolates the effect of removing entity identity from the input.
4. **`sbert_soft_topic`** — REUSED verbatim from Section 19 (SBERT on unmasked text + Soft
   Topic Distribution arm).
5. **`sbert_masked_soft_topic` (NEW)** — SBERT on entity-masked text + Soft Topic Distribution
   arm (tests whether Soft Topics can compensate once entity identity is removed).

Variants 1/2/4 are reused, not retrained: they are architecturally identical (same
`AblationDetector` class, same arms, same hyperparameters, same split, same seed) to Section
19's own runs — retraining would only reproduce the same numbers with sampling noise, not a new
result. `verify_reuse_validity()` checks programmatically that Section 19's `results.json`
actually contains all 3 reused variants for all 3 authors before allowing reuse. Masking runs
**once** over the full corpus's 16,394 unique texts (all 3 authors' train sets are large,
overlapping subsets of the same corpus), cached to
`data/cache/cached_raw_entities_masked_text.pt`, and looked up by exact text match per author —
avoiding a repeat ~16k-call NER pass per author. Only `sbert_masked`/`sbert_masked_soft_topic`
are newly trained (2 variants × 3 authors = 6 trainings); the Soft Topic arm's `soft_dense`
feature is reused by position from Section 19's own
`cached_features_ablation_loao_{author}.pt` cache (masking does not change topic features, only
the SBERT input).

**Verification performed.** (1) Masking logic spot-checked on hand-written examples before the
full run (`"Trump criticized Biden"` → `"[PERSON] criticized [PERSON]"`,
`"The United Nations condemned the actions taken by NATO forces"` →
`"The [ORG] condemned the actions taken by [ORG] forces"`) — confirmed entity spans are
replaced correctly and non-entity text is untouched. (2) Per-split label alignment re-verified
against a fresh `load_raw_data()`+`split_leave_one_author()` reconstruction before reusing
`soft_dense` by position (same pattern as Sections 19/20 — refuses to run silently on a
mismatch). (3) `verify_reuse_validity()` confirms Section 19's 3 reused variants exist for all 3
authors before any run. (4) Masking-coverage stats computed and saved alongside the cache (see
Limitation below), not just eyeballed on a few examples.

**Results — per author (recall of true/held-out narrative, % test rows misclassified as
Right-wing):**

| Variant | IDF recall / →RW% | MariaZakharova recall / →RW% | BernieSanders recall / →RW% |
|---|---|---|---|
| `sbert_only` | 63.5% / 2.5% | 89.5% / 2.5% | 24.5% / 57.5% |
| `sbert_ner` | 73.0% / 2.0% | 84.5% / 2.5% | 21.0% / 57.0% |
| `sbert_masked` | 38.5% / 5.0% | 76.5% / 6.5% | 30.5% / 42.0% |
| `sbert_soft_topic` | 51.5% / 3.0% | 91.5% / 1.0% | 34.0% / 46.0% |
| `sbert_masked_soft_topic` | 36.0% / 4.0% | 63.0% / 4.5% | 37.0% / 30.5% |

**Averaged across the 3 authors** (reported only as a secondary summary — see below for why
the average is not representative of any single author here):

| Variant | Avg recall | Avg →RW% | Avg Macro-F1 |
|---|---|---|---|
| `sbert_only` | 59.2% | 20.8% | 0.1218 |
| `sbert_ner` | 59.5% | 20.5% | 0.1076 |
| `sbert_masked` | 48.5% | 17.8% | 0.1065 |
| `sbert_soft_topic` | 59.0% | 16.7% | 0.1191 |
| `sbert_masked_soft_topic` | 45.3% | 13.0% | 0.1025 |

**Reading this precisely — the effect of masking is author-dependent, not uniform.** For IDF
and MariaZakharova, masking **hurts**: recall drops sharply (63.5%→38.5% and 89.5%→76.5%) and
the Right-wing-misclassification rate *increases* (2.5%→5.0% and 2.5%→6.5%). For these two
authors, removing entity identity removes signal that appears to be legitimately informative for
their held-out narrative (Zionist, Russian) — not a shortcut being cut away. For BernieSanders —
the one author Section 19's forensic analysis specifically implicated — masking helps on both
axes: recall improves (24.5%→30.5%) and the Right-wing-misclassification rate drops
substantially (57.5%→42.0%). Adding Soft Topics on top of masking pushes both directions further
for every author: it improves Right-wing-bias further in all 3 cases (IDF 5.0%→4.0%, Maria
6.5%→4.5%, Bernie 42.0%→30.5%, so `sbert_masked_soft_topic` gives the lowest Right-wing rate of
any variant tested for all 3 authors) but costs more recall for IDF/Maria (38.5%→36.0%,
76.5%→63.0%) while giving Bernie its best recall of any variant (37.0%). Because the 3 authors
move in different directions, the averaged table above is a poor summary of what actually
happens to any one of them — it should not be read as "masking helps" or "masking hurts" in
general.

**What this is (and is not) evidence for.** For BernieSanders specifically, the result is
consistent with Section 19's forensic hypothesis: identity-without-stance can create a spurious
cross-narrative pull for entities two narratives both discuss heavily (Bernie/Right-wing both
discuss Trump/Congress/America/Republicans), and removing that identity signal reduces the
pull. This experiment does not, on its own, prove that mechanism causally — masking removes
identity but does not isolate *why* removing it helps (e.g., it is also possible some other
correlated property of entity-bearing sentences changed). For IDF and MariaZakharova, the
opposite direction of the result argues against treating "mask entities" as a general-purpose
fix: whatever the NER arm/implicit SBERT identity signal was contributing for those two authors
was, on net, legitimate narrative signal, not a shortcut, and removing it made generalization
worse. The honest reading is that an entity-identity shortcut is **plausible and
author/narrative-pair-specific**, not a universal property of this classifier.

**Limitation.** Masking coverage over the full corpus: only **69.6%** of unique texts had at
least one entity detected and masked (entity group counts: LOC 22,616, MISC 13,500, PER 9,313,
ORG 12,558) — the remaining ~30% of texts are unchanged by masking because
`dslim/bert-base-NER` found nothing to mask in them (either genuinely no named entities, or
missed collective/abstract identity-carrying phrases like "the West"/"the regime", a known
model limitation documented in `narrative_lens/features/ner.py`). Separately, NER span
boundaries are sometimes imperfect even when an entity is caught at all — e.g. `"Zelenskyy"` is
tagged as only `"Zelensky"`, so the masked output is `"[PERSON]y met with..."`, leaving a
one-character fragment of the real name in the text. Both effects mean masking is a partial,
not complete, removal of entity-identity information — the true effect of *fully* removing
identity could be larger (in whichever direction) than what is measured here.

**Overall conclusion (bounded to what the data shows).** Entity-identity masking does not
uniformly help or hurt LOAO generalization across held-out authors — it helped exactly the one
author (`BernieSanders`) for which a concrete entity-overlap-with-opposite-stance mechanism was
previously documented (Section 19), and hurt the other two, where entity identity appears to
carry real narrative signal. This is directionally consistent with, but does not prove, the
hypothesis that the LOAO Right-wing shortcut for Bernie specifically is at least partly
attributable to entity identity being learned without stance. It is not evidence that entity
identity is harmful in general.

**What this does NOT resolve.** Whether a *stance-aware* entity representation (Experiment 22,
proposed but not started — restoring entity information while attaching sentiment/stance toward
that entity, rather than removing entity identity outright) could recover IDF/Maria's lost
recall while keeping Bernie's Right-wing-bias reduction remains untested. Whether the ~30%
masking-coverage gap materially understates the effect (in either direction) is also untested —
would require a more exhaustive entity/identity-phrase detector, not attempted here.

**Implementation:** `experiments/author_generalization/narrative_entity_shortcut.py`;
`mask_entities()` added to `narrative_lens/features/ner.py` (uses
`EntityAnalysisPipeline.extract_raw_entities()` + `reconstruct_fragmented_entities()`, both
unmodified/pre-existing). Reuses `train.py`'s `load_raw_data()`/`split_leave_one_author()`/
`evaluate()`/`save_confusion_matrix_csv()` and `narrative_ablation_loao.AblationDetector`
unmodified. Masked-text cache: `data/cache/cached_raw_entities_masked_text.pt`. Per-author
feature caches: `data/cache/cached_features_entity_shortcut_{author}.pt`. Checkpoints:
`models/experiments/narrative_entity_shortcut/{variant}_{author}.pth`. Results:
`reports/results/narrative_entity_shortcut/results.json`, `entity_shortcut_summary.csv`,
`confusion_matrix_{variant}_{author}_test.csv`.

---

## 22. Stance-Aware Entity Representation — representation-validation gate (NOT reached: LOAO training)

**Status: STOPPED at the representation-validation gate — negative finding / future work. No
LOAO classification training was run.** This section documents a pre-training feasibility study
only: whether *any* off-the-shelf stance-extraction method can reliably tell, for a given named
entity mention, whether the author's attitude toward that specific entity is positive, negative,
or neutral. The plan (agreed in advance) was to validate this signal in isolation before ever
wiring it into `AblationDetector`/LOAO training — training was never reached because the
signal failed validation.

**Research question.** Section 21 showed that entity-identity masking helps BernieSanders
(reduces Right-wing-misrouting) but hurts IDF and MariaZakharova (removes legitimate signal) —
consistent with Section 19's hypothesis that the NER arm encodes entity *identity* with no
*stance*, creating a shortcut specifically where two narratives discuss the same entities with
opposite attitudes. The natural next step, proposed at the end of Section 21, is not to remove
entity identity but to **attach entity-targeted stance** to it (e.g. `Trump:NEGATIVE` vs.
`Trump:POSITIVE` instead of a bare `Trump` identity token), so the shortcut-prone entities keep
their identity but the model additionally sees whose attitude points which way. **Before
investing in that architecture change**, this experiment asks a narrower, prior question: does
any accessible stance-extraction method produce accurate, target-sensitive, cross-author
predictions on our actual corpus?

**Motivation from Experiment 21.** Experiment 21 is the sole reason this direction was
considered at all — it identified a concrete mechanism (identity without stance) for one author
and, symmetrically, a concrete cost (loss of legitimate identity signal) for the other two. This
experiment is a direct, disciplined follow-up: rather than assuming a stance signal would be
reliable and building it straight into the classifier, its quality was validated on hand-labeled
data first.

**De-risking strategy (pre-registered, followed in order).** Each stage below was a go/no-go
checkpoint agreed on *before* running it, not after seeing results:
1. Audit the repo's existing stance-adjacent modules (rule-based lexicon scoring, generic
   sentence sentiment) — none were target-conditioned (they score a sentence, not "attitude
   toward entity X" when several entities co-occur) — rejected as unusable without modification.
2. Select one accessible, target-conditioned candidate:
   `yangheng/deberta-v3-base-absa-v1.1` (Aspect-Based Sentiment Analysis; entity passed as
   `text_pair`, i.e. genuinely target-conditioned, not just sentence sentiment).
3. Build a balanced ~180-mention validation sample across the 3 LOAO authors
   (`IDF`/`MariaZakharova`/`BernieSanders`), inspect 20–30 qualitative examples.
4. Build a **30-mention pilot** (10 per author, with 4 deliberately forced "suspicious" cases:
   `IDF_011`, `IDF_023`, `IDF_024`, `MariaZakharova_039`) and have it **manually gold-labeled by
   the researcher** (`gold_stance`, `error_category`, `annotator_notes` — one label per row, not
   model-assisted).
5. Only then measure accuracy/confusion/error-buckets against the gold labels, run a
   context-width sweep, and — since the single ABSA candidate did not clear its own gate — run a
   5-method mini-benchmark, all still on the same 30 gold rows, before any decision to scale up
   to the full 180-mention sample or touch LOAO training at all.

**The gate criteria below (Step 6) were fixed in writing *before* the 5-method benchmark was
run, and are unchanged from that pre-registration. The FAIL decision at the end of this section
follows directly from applying those pre-declared numbers — it was not a judgment call made
after looking at the results.**

### 30-row manually annotated pilot

10 mentions per author (`IDF`, `MariaZakharova`, `BernieSanders`), each hand-labeled with
`gold_stance` (positive/negative/neutral), `error_category` (one of 11 predefined values), and
free-text `annotator_notes`. Saved at
`reports/results/narrative_stance_entity/pilot_sample_30_annotated.csv` (git-tracked, the
authoritative ground truth for every result in this section — never regenerated or overwritten
after annotation).

**ABSA baseline accuracy on the pilot (sentence-level context):** 60.0% overall (18/30).

| Author | Accuracy |
|---|---|
| IDF | 70.0% (7/10) |
| BernieSanders | 70.0% (7/10) |
| MariaZakharova | 40.0% (4/10) |

**Error-category breakdown (30 rows, 12 wrong):**

| `error_category` | Count | Bucket |
|---|---|---|
| `none` (correct) | 18 | — |
| `insufficient_context` | 6 | `insufficient_context` |
| `action_vs_entity` | 2 | `absa_prediction_error` |
| `wrong_entity_boundary` | 2 | `ner_entity_error` |
| `multiple_entities` | 1 | `absa_prediction_error` |
| `other` | 1 | `absa_prediction_error` |

i.e. of the 12 errors: 6 are the local sentence genuinely lacking the information needed (the
supportive/critical clause is in a *different* sentence of the same post), 4 are the ABSA model
itself misreading an in-context signal (e.g. `action_vs_entity`: IDF_023/IDF_024 — "the IDF is
striking Hezbollah" gets read as negative-toward-IDF/Israel because of the violent vocabulary,
when the text actually frames IDF/Israel as the party defending itself), and 2 are upstream
NER-boundary errors (not the stance model's fault).

**Context-width follow-up** (still on the ABSA model only, before the 5-method benchmark):
widening context from current-sentence → ±1-sentence window → full post gave 60.0% → 53.3% →
66.7%. Full-post context recovered 4 of the 6 `insufficient_context` errors, but introduced a
**new** failure mode: 3 previously-correct neutral IDF predictions (`IDF_002`/`IDF_003`/`IDF_004`
— headline-style factual mentions of a location/org) flipped to negative once the surrounding
violent-conflict paragraph was included — i.e. wider context helps recover missing signal but
also lets the model over-generalize sentiment from surrounding text onto entities the local
sentence treats neutrally. Full results:
`reports/results/narrative_stance_entity/context_width_experiment.csv`.

### 5 stance-extraction methods benchmarked (same 30 gold rows, same target entity per row)

Because the single ABSA candidate did not clear the pre-declared gate on its own, 3 additional,
fundamentally different candidates were benchmarked on the identical 30 rows before concluding
anything about the underlying idea:

1. **`absa_sentence`** — `yangheng/deberta-v3-base-absa-v1.1`, current-sentence context
   (baseline, reused from the pilot analysis above).
2. **`absa_full`** — same ABSA model, full-post context (reused from the context-width
   experiment).
3. **`semeval`** — `krishnagarg09/stance-detection-semeval2016`, a real (text, target) →
   FAVOR/AGAINST/NONE stance classifier trained on SemEval-2016 Task 6 (not a sentiment model).
4. **`nli`** — `MoritzLaurer/deberta-v3-large-zeroshot-v2.0`, a generic NLI/zero-shot model
   repurposed via 3 explicit target-conditioned hypotheses ("The author supports/opposes/has no
   clear attitude toward {target}.") — documented explicitly as a zero-shot heuristic, not a
   trained stance signal.
5. **`procon`** — `NLP-Debater-Project/debertav3-stance-detection`, a real PRO/CON debate-stance
   model (IBM ArgKP-2023) with **no native neutral class**; a fixed, pre-declared abstention
   margin (`|P(PRO)-P(CON)| < 0.15` → predict neutral) was set *before* looking at any gold label
   in this pilot, specifically to avoid tuning a threshold against the same 30 labels it would be
   scored on.

**Gate criteria, fixed in writing before running the benchmark.** PASS requires at least one
method to simultaneously: (a) reach ≥70–75% overall accuracy, (b) not depend almost entirely on
one author, (c) not introduce a new systematic failure mode, (d) work reasonably across
positive/negative/**and** neutral (not just the majority class), and (e) show genuine
target-sensitivity (different predictions for different targets in the same sentence when their
true stances differ) rather than being sentence-level sentiment in disguise.

**Full comparison table:**

| Method | Overall acc. | BernieSanders | IDF | MariaZakharova | Neutral P / R | Target-sensitive? | New systematic failure mode |
|---|---|---|---|---|---|---|---|
| `absa_sentence` (baseline) | 60.0% | 70% | 70% | 40% | 0.40 / 0.57 | Partial (differentiated correctly in 2/3 multi-target contexts) | None new (see pilot error buckets above) |
| `absa_full` | 66.7% | 90% | **40%** | 70% | 1.00 / **0.14** | Weak (near-constant per context group) | **Yes** — neutral recall collapses (7 IDF `neutral` rows → `negative`); IDF accuracy drops sharply |
| `semeval` | 60.0% | 60% | 50% | 70% | 0.50 / 0.71 | Weak | Positive-class recall collapses (30%; several genuine `positive` endorsements → `neutral`) |
| `nli` | 56.7% | 60% | 70% | 40% | 0.33 / 0.43 | Weak–moderate | Negative-class recall drops (46%; several `negative` rows softened to `neutral`) |
| `procon` | 33.3% | 60% | 40% | **0%** | undefined / 0.00 | **No** — near-constant "positive" output | **Yes** — degenerates to an almost-constant predictor (10/10 `positive` rows correct, but 0/13 `negative` and 0/7 `neutral` rows correct) |

**Target-sensitivity analysis.** 9 pilot contexts contain ≥2 distinct target entities in the
same sentence; in 4 of these the gold stance genuinely differs by target (e.g.
`"...worried about Estonia"` — `Estonia`=neutral vs. `MariaVladimirovnaZakharova`=negative in the
same sentence; `"...defeat @ZohranKMamdani..."` — `Bill Ackman`=negative vs. `ZohranKM`=positive).
Only `absa_sentence` differentiated its predictions in most of these gold-differing groups (2/3
checked in detail); `absa_full`, `semeval`, and `procon` collapsed to a single prediction across
different targets in nearly every group regardless of whether gold differed — i.e. for most
candidates the "target" argument is not doing meaningful work, the prediction is closer to
generic sentence sentiment than to true target-conditioned stance. `nli` showed intermittent
target-sensitivity but not reliably tied to the correct direction.

**Fixed-vs-regressed vs. the `absa_sentence` baseline.** Every alternative method that fixed some
of the baseline's errors introduced a comparable or larger number of *new* errors on previously-
correct rows (`absa_full`: +5 fixed / −3 new; `semeval`: +7 / −7; `nli`: +4 / −5; `procon`: +4 /
−12) — none of the 4 alternatives represents a net improvement; each just relocates the error
pattern.

**Row-by-row inspection of the critical/flagged cases** (full detail in
`stance_benchmark_run.log`): `IDF_023`/`IDF_024` (the `action_vs_entity` cases) were only fixed by
`nli` and `procon` — but `procon`'s "fix" is an artifact of it predicting `positive` almost
unconditionally, not evidence of understanding. `MariaZakharova_039` (forced suspicious case) was
correctly predicted **only** by `semeval` (`neutral`); all 4 other methods got it wrong.
`BernieSanders_002`/`BernieSanders_005` (`insufficient_context`, sentence-level context omits a
later "Stand with Zohran"/"proud to endorse" clause) were recovered by `absa_full` and `procon`
but not by `semeval`/`nli`. `BernieSanders_007` (`insufficient_context`) was not recovered by any
of the 5 methods.

**Full artifacts:** `reports/results/narrative_stance_entity/stance_method_benchmark.csv`
(per-row, all 5 methods) and `reports/results/narrative_stance_entity/stance_benchmark_run.log`
(complete run output: all per-method reports, confusion matrices, fixed/regressed breakdowns,
and the target-sensitivity groups).

### Gate Decision: **FAIL**

No method reaches the pre-declared bar. The best raw accuracy (`absa_full`, 66.7%) fails
criteria (b)/(c)/(d): it is heavily author-dependent (90% BernieSanders vs. 40% IDF) and
collapses neutral recall to 0.14, a new systematic failure mode not present in the sentence-level
baseline. `procon` fails hardest and most informatively: an accuracy-only read (33.3%, with a
perfect 100% "recall" on the positive class) would look almost plausible in isolation, but the
per-row and target-sensitivity checks show it is a near-constant predictor with no real
entity-targeting behavior — a concrete illustration of why the gate required target-sensitivity
and cross-class balance, not just overall accuracy. `semeval` and `nli` are more balanced across
authors but plateau at 56.7–60.0%, well under the 70–75% bar, and neither shows reliable
target-sensitivity either.

**This decision was reached by applying the pre-declared gate criteria (Step 6, fixed in writing
before the benchmark was run) to the measured numbers above — it was not a post-hoc judgment
made after seeing which numbers came out. The threshold and success conditions did not change
after the results were known.**

### Conclusion

> The stance-aware entity hypothesis was not tested end-to-end because no evaluated
> stance-extraction method produced a sufficiently reliable and target-sensitive signal. Rather
> than injecting systematic label noise into the narrative classifier, the experiment was
> stopped at the representation-validation gate.

To state this precisely:
- **There is no evidence that the stance-aware-entity *idea* itself is wrong.** Experiment 21's
  underlying motivation (entity identity without stance can create a shortcut for some
  author/narrative pairs, while still being legitimate signal for others) is untouched by this
  result.
- **There is evidence that the specific stance-extraction *methods* evaluated here are not
  reliable enough for this corpus** — informal, code-mixed, multi-entity social-media text,
  across 3 stylistically very different authors — even though 3 of the 5 (`absa`, `semeval`,
  `procon`) are real, purpose-built target/stance classifiers, not generic sentiment models.
- **This direction therefore remains future work, not a closed/refuted research question.** A
  better outcome would require either a stance model fine-tuned on in-domain, entity-targeted
  examples (the 30-row pilot + the existing 180-row validation sample would be a starting point
  for such fine-tuning data, itself a nontrivial follow-up project), or a fundamentally different
  representation of "attitude toward an entity" that does not depend on a single pretrained
  target-stance classifier's output being correct.

### Limitations

- **Small pilot (n=30).** 10 mentions per author is enough to reject the pre-declared gate with
  reasonable confidence (all 5 methods fail by a wide margin, not a close call), but far too
  small to finely rank or calibrate any candidate method, or to detect rarer error modes.
- **Domain mismatch of all 3 pretrained stance candidates.** None were fine-tuned on informal,
  code-mixed, multi-clause social-media posts about ongoing geopolitical conflicts — `semeval`
  was trained on short tweet-length text via a `bertweet-base` tokenizer (max 130 tokens),
  `procon` on formal topic/argument pairs from structured debate corpora (IBM ArgKP-2023), and
  `absa` on general-domain aspect-based-sentiment benchmarks, not political entity stance.
- **NER boundary/type errors upstream of the stance model.** 2 of the pilot's 12 baseline errors
  (`wrong_entity_boundary`) were caused by the entity span itself being truncated
  (`"MUHAMMAD ZID"` instead of `"MUHAMMAD ZIDAN"`), not by the stance model — a ceiling on how
  much any stance-model swap alone can fix.
- **Author/domain differences in how attitude is expressed.** MariaZakharova's Twitter-reply
  corpus (short, reactive, heavily sarcastic/mocking replies) was the hardest for every method
  (40% or worse for 4 of 5 methods) — the same architecture that handles IDF's declarative
  military-update style reasonably cannot be assumed to transfer to a sarcasm-heavy reply corpus.
- **"Stance toward the entity" vs. general sentence sentiment.** The target-sensitivity analysis
  is direct evidence that most candidates (`absa_full`, `semeval`, `procon`) collapse toward
  scoring the sentence as a whole rather than conditioning on the specific target argument, even
  though all 3 are architecturally designed to take a target/aspect as input.
- **Neutral-class instability.** Every method's neutral precision/recall is materially worse and
  less stable than its positive/negative numbers (e.g. `absa_full`'s neutral recall collapses to
  0.14, `procon`'s neutral recall is 0.00) — "no clear attitude" appears to be the hardest class
  for all 5 methods, which is a particular concern since a large share of entity mentions in this
  corpus are plausibly neutral (headline-style factual references).

**Implementation:** `experiments/author_generalization/narrative_stance_entity.py` (single script
for the full Phase-1 pipeline: validation-sample building, pilot building, pilot analysis,
context-width experiment, and the 5-method benchmark — CLI flags `--build-sample`,
`--build-pilot`, `--analyze-pilot`, `--context-experiment`, `--stance-benchmark`). Artifacts (all
git-tracked, none regenerated after annotation):
`reports/results/narrative_stance_entity/validation_sample.csv` (180-row validation sample),
`STANCE_ANNOTATION_GUIDE.md` (annotation instructions/label definitions),
`pilot_sample_30_annotated.csv` (gold-labeled ground truth for this whole section),
`context_width_experiment.csv`, `stance_method_benchmark.csv`, `stance_benchmark_run.log`.

---

## 23. Entity-Masking Augmentation — can training-time invariance capture Bernie's gain without paying IDF/Maria's cost?

**Status: COMPLETE.** All 3 LOAO authors run; 3 variants reused verbatim from Section 21
(themselves partly reused from Section 19) after a programmatic reuse-validity check; 3 new
variants trained per author (9 trainings total), built entirely from 2 already-existing
per-author feature caches with **zero new NER/SBERT/BERTopic inference**. See
`experiments/author_generalization/narrative_entity_masking_augmentation.py`,
`reports/results/narrative_entity_masking_augmentation/`.

**Research question.** Section 21 showed entity-identity masking is not a universal fix: full
masking (replacing every entity mention with a generic placeholder before encoding) helps
BernieSanders (recall 24.5%→30.5%, Right-wing-misrouting 57.5%→42.0%) but hurts IDF and
MariaZakharova (recall 63.5%→38.5% and 89.5%→76.5%), because — for those two authors — entity
identity carries real narrative signal, not a shortcut. Rather than choosing between the
original and masked representations, this experiment tests whether **training-time
augmentation** — showing the model both the original and the entity-masked version of every
training example, under the same label — can teach label-invariance to entity-identity
presence/absence without erasing identity information at inference time altogether.

**Audit performed before writing any new code (per explicit instruction).** (1)
`reports/results/narrative_entity_shortcut/results.json` already contains `sbert_only`,
`sbert_masked`, and `sbert_soft_topic` for all 3 LOAO authors, computed under the exact
split/seed/architecture this experiment needs — `verify_reuse_validity()` confirms this
programmatically; all 3 reused verbatim, not retrained. (2) `narrative_lens/features/ner.py`'s
masking pipeline (`mask_entities()`/`EntityAnalysisPipeline`/`reconstruct_fragmented_entities()`)
does not need to run again: the per-author **original** feature cache
(`data/cache/cached_features_ablation_loao_{author}.pt`, Section 19/20 — `sbert_embedding` on
unmasked text + `soft_dense`) and the per-author **masked** feature cache
(`data/cache/cached_features_entity_shortcut_{author}.pt`, Section 21 — `sbert_embedding` on
masked text + the same `soft_dense` reused by position) already exist for all 3 authors. A
direct label-by-position comparison between the two caches (done once, ad hoc, then re-checked
programmatically by `load_author_caches()` at run time — raises `RuntimeError` on any mismatch)
confirmed exact train/val/test alignment for all 3 authors (e.g. IDF: 13,863/2,447/200 rows,
labels identical row-for-row). Consequence: the 3 new variants below are built purely by
**interleaving rows already sitting in these two existing caches** — no new inference, only 9
lightweight `AblationDetector` MLP trainings (same architecture/hyperparameters as Sections
19-21, unmodified).

**Variants compared** (same 3 LOAO authors, same `split_leave_one_author` split/seed=42, same
SBERT backbone, same `AblationDetector` architecture/hyperparameters as Sections 18-21 —
architecture is unchanged, only which rows are concatenated into train/val differs):

1. **`sbert_original`** — REUSED verbatim from Section 21 (`sbert_only`). SBERT on original,
   unmasked text. Baseline.
2. **`sbert_masked_only`** — REUSED verbatim from Section 21 (`sbert_masked`). SBERT on
   entity-masked text only, no original text ever seen. The "full masking" comparison point.
3. **`sbert_soft_topic`** — REUSED verbatim from Section 21 (itself reused from Section 19).
   SBERT (unmasked) + Soft Topic Distribution arm. Existing robustness baseline.
4. **`sbert_duplicated_original_control` (NEW)** — every training/validation example
   duplicated **twice**, both copies original/unmasked, no masking at all. Isolates "more
   training rows" (with zero new information) from "masking augmentation" as an explanation
   for any effect.
5. **`sbert_masked_aug` (NEW)** — every training/validation example contributes **both** its
   original and its entity-masked version, both under the same label. Test stays
   original-only.
6. **`sbert_masked_aug_soft_topic` (NEW)** — same augmentation as (5), + Soft Topic
   Distribution arm on top.

**Fairness / leakage constraints.** Masked/duplicated copies are created only from rows
already inside the per-author caches' `train`/`val` lists — since both source caches are
themselves scoped to `split_leave_one_author`'s train/val/test partition (verified at their own
construction time in Sections 19-21), a held-out author's row can never be duplicated or
masked into training; it was never in the `train`/`val` list to begin with. **Test is always
the untouched, single-copy, original test split** (`orig_cache["test"]`, n=200/author) for
every variant, including the 3 new ones — no augmentation, no masking, ever applied at test
time, so all 6 variants are compared on identical test data. Original and masked (or
duplicated) rows are **interleaved** as `[row0_a, row0_b, row1_a, row1_b, ...]`, not
concatenated as `[all_a..., all_b...]` — the training loop (reused unmodified from Sections
19-21) does not shuffle between epochs, so concatenation would put ~13.9k original-only
gradient steps before any masked/duplicated ones each epoch; interleaving is applied
**identically** to `sbert_masked_aug` and `sbert_duplicated_original_control`, so the two
variants differ only in whether the second copy of each example is masked or an exact
duplicate, never in batch composition/order.

**Effective training/validation size** (2x the original split, as expected for the 3 new
variants; test unchanged): for all 3 authors, `n_train_original=13,863 → n_train_effective=
27,726`, `n_val_original=2,447 → n_val_effective=4,894`, `n_test=200` (unchanged, original-only).

**Results — per author (recall of true/held-out narrative, %):**

| Variant | IDF Recall | Maria Recall | Bernie Recall | Avg Recall | Bernie→RW |
|---|---|---|---|---|---|
| `sbert_original` | 63.5% | 89.5% | 24.5% | 59.2% | 57.5% |
| `sbert_duplicated_original_control` | 58.0% | 85.0% | 28.0% | 57.0% | 56.0% |
| `sbert_masked_only` | 38.5% | 76.5% | 30.5% | 48.5% | 42.0% |
| `sbert_masked_aug` | 39.0% | 81.5% | 40.5% | 53.7% | 41.5% |
| `sbert_soft_topic` | 51.5% | 91.5% | 34.0% | 59.0% | 46.0% |
| `sbert_masked_aug_soft_topic` | 42.0% | 90.0% | 39.0% | 57.0% | 38.0% |

**Secondary metrics (accuracy = recall here, since both are computed as fraction of test rows
predicted as the true narrative; Macro-F1, averaged across authors):**

| Variant | Avg Macro-F1 |
|---|---|
| `sbert_original` | 0.1218 |
| `sbert_duplicated_original_control` | 0.1103 |
| `sbert_masked_only` | 0.1065 |
| `sbert_masked_aug` | 0.1015 |
| `sbert_soft_topic` | 0.1191 |
| `sbert_masked_aug_soft_topic` | 0.1075 |

Full per-author confusion matrices: `reports/results/narrative_entity_masking_augmentation/
confusion_matrix_{variant}_{author}_test.csv`.

**Analysis — the 4 required questions:**

**1) Does Bernie's Right-wing bias decrease?** Yes, and augmentation captures **more** than
full masking's benefit: Right-wing-misrouting drops 57.5% (`sbert_original`) → 42.0%
(`sbert_masked_only`) → 41.5% (`sbert_masked_aug`) → **38.0%** (`sbert_masked_aug_soft_topic`,
the lowest Right-wing rate of any variant tested in Sections 19-23 for BernieSanders). Bernie's
recall follows the same pattern but goes further: 24.5% → 30.5% (masked-only) → **40.5%**
(masked-aug) — augmentation alone exceeds full masking's recall improvement by +10pp, and
`sbert_masked_aug_soft_topic` (39.0%) is close behind.

**2) Is IDF/Maria degradation smaller for masked-aug than for masked-only (relative to
original)?** Mixed, and author-dependent. For **MariaZakharova**, yes — degradation shrinks
from −13.0pp (masked-only: 89.5%→76.5%) to −8.0pp (masked-aug: 89.5%→81.5%), and with the
Soft Topic arm added it nearly vanishes (89.5%→90.0%, +0.5pp — Maria's recall is essentially
fully preserved). For **IDF**, no — degradation is −25.0pp for masked-only vs. −24.5pp for
masked-aug, i.e. effectively unchanged; the Soft Topic arm helps somewhat (39.0%→42.0%,
still −21.5pp vs. original) but IDF's cost remains large and is not resolved by augmentation.

**3) Does the duplicated-original control give a similar improvement — if so, the effect is
not (necessarily) due to masking?** No — the control's effect is much smaller than masked-aug's
on every axis that matters. For Bernie, the effect the user asked to disentangle is clear:
recall moves +3.5pp under pure duplication (24.5%→28.0%) vs. **+16.0pp** under masked-aug
(24.5%→40.5%); Right-wing rate moves −1.5pp under duplication vs. **−16.0pp** under masked-aug.
This confirms Bernie's improvement is attributable to the masking augmentation itself, not
merely to having twice as many training rows. For IDF and Maria, duplication alone causes a
small drop even with **zero new information** (IDF 63.5%→58.0%, −5.5pp; Maria 89.5%→85.0%,
−4.5pp) — a training-dynamics artifact (more gradient steps/epoch interacting with
early-stopping/checkpoint selection), not a masking effect. This means a small fraction of
masked-aug's IDF/Maria cost is attributable to "more rows" rather than "masked content", but
the bulk is not: masked-aug's IDF drop (−24.5pp) vastly exceeds the control's (−5.5pp), so most
of IDF's cost under augmentation is specifically about the masked content, not row count.

**4) Does augmentation affect the 3 authors differently?** Yes, sharply so: `sbert_masked_aug`
vs. `sbert_original` recall delta is **+16.0pp** for BernieSanders, **−8.0pp** for
MariaZakharova, and **−24.5pp** for IDF. Augmentation is not author-neutral — it trades a large
part of IDF's identity-dependent signal for Bernie's shortcut-reduction benefit, with Maria in
between (a real but much smaller cost, further reduced to near-zero once Soft Topics are added).

**Critical question: does `sbert_masked_aug` achieve (a) recall close to original for IDF/Maria
AND (b) capture part of mask-only's Bernie improvement?** Partially. **(b) is answered
unambiguously yes — and exceeded:** `sbert_masked_aug`'s Bernie recall (40.5%) and Right-wing
reduction (41.5%) meet or beat `sbert_masked_only`'s on both axes, not just "part of" the
benefit. **(a) is answered yes for Maria, no for IDF:** Maria's recall (81.5%, or 90.0% with
Soft Topics) is reasonably close to original (89.5%), but IDF's recall (39.0%, or 42.0% with
Soft Topics) is nearly as far from original (63.5%) as full masking is (38.5%) — augmentation
does not rescue IDF.

**`sbert_masked_aug_soft_topic` is NOT the best model overall — it is a robustness/bias
trade-off, not a strict improvement.** On **average recall**, it is not competitive:
`sbert_original` 59.2%, `sbert_soft_topic` 59.0%, `sbert_masked_aug_soft_topic` **57.0%** — the
augmented-plus-soft-topic variant has the *lowest* average recall of these three, because IDF's
large loss is not offset by Bernie's gain once averaged. Its value is specific and narrow: it
(1) improves Bernie substantially (recall 24.5%→39.0%, Right-wing rate 57.5%→38.0%, the best
Bernie Right-wing result of any experiment in this project), (2) preserves Maria almost fully
(89.5%→90.0%), but (3) costs IDF a large amount of recall (63.5%→42.0%, barely better than full
masking's 38.5%) — a real, unresolved degradation, not a minor side effect. Whether this
trade-off is worth taking depends entirely on how much weight is placed on Bernie/Right-wing-bias
reduction vs. IDF's recall — it is not a win on the primary average-recall metric, and should
not be presented as one.

**What this is (and is not) evidence for.** This supports the hypothesis that training-time
invariance (seeing both entity-identity-present and entity-identity-absent versions of the same
example under the same label) can partially decouple "reduce reliance on an entity-identity
shortcut for one author" from "erase entity identity as a feature for all authors" — Bernie's
benefit is captured (and exceeded) while Maria's cost is nearly eliminated. It is **not**
evidence that this fully resolves the underlying trade-off: IDF's cost is barely reduced
relative to full masking, so for IDF specifically, augmentation behaves almost like full
masking, not like a compromise. The mechanism for *why* IDF is unaffected by the "both versions
present" framing while Maria is not remains unexplained by this experiment — a candidate
hypothesis (not tested here) is that IDF's held-out narrative (Zionist) may depend on
entity-heavy phrasing more densely/uniformly across its posts than Maria's (Russian), so even a
50%-of-training-rows entity-masked exposure meaningfully erodes the model's reliance on that
signal for IDF specifically, but this is speculative and not verified.

**Limitations.** (1) Only one interleaving pattern was tested (strict alternation,
1 original : 1 masked); other ratios (e.g. 3:1, 1:3) were not swept and might shift the
IDF/Bernie trade-off differently — not attempted here (would be a hyperparameter sweep,
explicitly out of scope for this experiment). (2) The small but real degradation observed even
under the zero-information `sbert_duplicated_original_control` (IDF −5.5pp, Maria −4.5pp)
indicates some sensitivity to training-set size/step-count interacting with early stopping that
is not specific to masking — this experiment did not isolate that mechanism further. (3) As in
Section 21, masking coverage over the corpus is ~69.6% (some texts have no entity detected to
mask), inherited unchanged from the existing masked-text cache — not re-measured here. (4) No
new stance features, no new architecture, and no post-hoc hyperparameter tuning were used, per
the explicit constraint on this experiment — the robustness/bias-trade-off variant here should
not be read as a fully-tuned, or overall-best, production candidate; it loses to `sbert_original`
and `sbert_soft_topic` on average recall, and IDF's large recall cost remains unexplained and
unresolved (root-cause audit proposed as future work).

**Implementation:** `experiments/author_generalization/narrative_entity_masking_augmentation.py`.
Reuses `narrative_ablation_loao.AblationDetector` and `train.py`'s `evaluate()`/
`save_confusion_matrix_csv()` unmodified. Builds new variants entirely from 2 existing caches
(`data/cache/cached_features_ablation_loao_{author}.pt`,
`data/cache/cached_features_entity_shortcut_{author}.pt` — no new cache-building step).
Checkpoints: `models/experiments/narrative_entity_masking_augmentation/{variant}_{author}.pth`.
Results: `reports/results/narrative_entity_masking_augmentation/results.json`,
`entity_masking_augmentation_summary.csv`, `confusion_matrix_{variant}_{author}_test.csv`,
per-author run logs (`run_{author}.log`).

### Root-Cause Audit — why does masking hurt IDF? (test-informed, exploratory — not blind)

**Methodological caveat, stated explicitly and up front.** This audit was performed by
evaluating 4 already-trained models on IDF's held-out LOAO **test** set (the same 200 rows
used to compute this section's own reported metrics) and comparing their predictions
row-by-row. Any hypothesis or masking policy derived from this audit is therefore
**test-informed, not blind** — it does not constitute an independent, pre-registered
confirmatory test. Section 24 (which trains new variants based on this audit's hypothesis and
evaluates them on the SAME IDF/MariaZakharova/BernieSanders authors) must accordingly be read
as **exploratory evidence**, not a validated or confirmed result. A genuinely confirmatory test
of any policy that looks promising here would require evaluating it on **fresh held-out
authors that were never used for hypothesis generation in Sections 19-24**.

**Method.** `sbert_original`, `sbert_soft_topic` (both from Section 19/21), `sbert_masked_aug`,
and `sbert_masked_aug_soft_topic` (Section 23) were all evaluated on the same 200 IDF test rows
(`orig_cache["test"]`, original/unmasked text, identical to how each was already scored — no
re-training). The **regression set** is defined as rows where `sbert_original` AND
`sbert_soft_topic` both predicted correctly, but `sbert_masked_aug` did not: **31/200 (15.5%)**
of IDF's test rows. Entities in each regression row's original text were freshly extracted
(`EntityAnalysisPipeline.extract_raw_entities()` + `reconstruct_fragmented_entities()`, both
unmodified) and compared against the same extraction run over all 200 test rows (baseline
prevalence), so the regression set's entity-type composition can be read as an enrichment (or
not) relative to the full test set, not in isolation.

**Finding 1 — where the errors go.** Of the 31 regressions, **87.1% are misclassified as
"Resistance"** specifically (the remaining 12.9% split across Ukrainian/Left-wing/Russian) —
essentially the same pattern as Section 19/21's Bernie→Right-wing shortcut, but for the
IDF/Resistance pair (the two narratives describing opposite sides of the same conflict).

**Finding 2 — entity-type composition of the regression set vs. the full test-set baseline:**

| Entity type | % of regression rows containing this type | % of all 200 test rows containing this type |
|---|---|---|
| LOC | 90.3% | 78.0% |
| ORG | 87.1% | 79.0% |
| MISC | 25.8% | 36.5% |
| PER | 16.1% | 19.0% |

LOC and ORG are present in the large majority of regression rows, and modestly enriched
relative to the full test set (+12.3pp / +8.1pp) — but PER and MISC are **not** enriched; MISC
is actually **less** common in the regression set than in the baseline (−10.7pp), and PER is
essentially flat (−2.9pp).

**Finding 3 — qualitative pattern.** The regression rows are overwhelmingly IDF's characteristic
"operational report" style text — e.g. *"As part of IDF activities in Lebanon, IDF special
forces operated overnight..."* (entities: `ORG:IDF` ×4, `LOC:Lebanon`, `PER:Ron Arad`) and
*"...the IDF struck a command center... belonging to the Syrian regime in southern Syria"*
(entities: `MISC:Druze`, `ORG:IDF`, `MISC:Syrian`, `LOC:Syria`) — where the ORG token `IDF`
itself and specific conflict-zone place names (Lebanon, Syria, Gaza-region toponyms) recur
constantly. Unlike Bernie's Trump/Congress mentions (Section 19's forensic finding, where
identity-without-stance created a plausible spurious shortcut), IDF mentioning the organization
"IDF" and specific Levant place names looks like a **direct, legitimate identity marker** of
who is writing (an IDF-affiliated account), not merely a topic the account happens to share
with its narrative "opponent." Masking-augmentation training teaches invariance to exactly
this ORG/LOC identity signal, which appears to cost IDF specifically because — for this
narrative pair — that signal is unusually reliable, not spurious.

**Hypothesis for Section 24 (test-informed, not yet tested independently).** If ORG/LOC
identity is legitimate signal being eroded by full masking, while PER (and, less certainly,
MISC) are not enriched in the regression set (i.e., masking them is less implicated in IDF's
cost), then a **selective masking policy that masks only PER (or PER+MISC) while leaving
ORG/LOC identity intact** might retain more of IDF's signal than full masking, while still
providing some of the training-time invariance that helped Bernie. This is a hypothesis to
test, not a conclusion — it was generated by looking at the same test set Section 24 will be
evaluated on, so any result in Section 24 supporting it is exploratory corroboration, not
independent proof.

**Implementation:** `experiments/author_generalization/narrative_idf_masking_regression_audit.py`.
Results: `reports/results/narrative_idf_masking_regression_audit/` (`idf_masked_aug_regressions_full.csv`
[31 rows], `idf_masked_aug_regressions_sample.csv` [30-row qualitative sample],
`entity_type_summary.csv`, `audit_summary.json`).

---

## 24. Selective Entity-Masking Augmentation — exploratory test of a test-informed hypothesis

**Methodological status: EXPLORATORY, NOT CONFIRMATORY.** The masking-policy hypothesis this
experiment tests (mask only PER, or PER+MISC, while leaving ORG/LOC intact) was generated by
Section 23's root-cause audit, which looked at IDF's held-out LOAO test set — the SAME 200
rows this experiment is evaluated on. This is test-set-informed hypothesis generation, not
blind experimental design. Accordingly, every result below is reported as **exploratory
evidence**, and the words "validated"/"confirmed" are deliberately not used anywhere in this
section. If a selective policy looks promising here, the required next step (not attempted in
this section) is to test it on fresh held-out authors never used for hypothesis generation in
Sections 19-24.

**Research question:** Can selective entity masking retain the robustness benefit seen for
Bernie while avoiding the loss of legitimate ORG/LOC narrative signal observed for IDF?

**Variants (7, same 3 LOAO authors/split/seed=42/architecture/hyperparameters as Sections
18-23).** 3 reused verbatim from Section 23 (`sbert_original`, `sbert_duplicated_original_control`,
`sbert_full_masked_aug` = Section 23's `sbert_masked_aug`); 4 newly trained, with the masking
policy FIXED in advance (per explicit instruction, not changed after seeing results, no
additional policies added mid-experiment): `sbert_person_masked_aug`, `sbert_person_misc_masked_aug`,
and their `+soft_topic` combinations. (A previously-discussed "Variant 5" — a plain PER+MISC
masked-aug without soft topics — was a duplicate of `sbert_person_misc_masked_aug` as first
described and was canceled; it does not appear in the 7 variants actually run.)

**Results (Primary metrics: true-narrative recall per author, average recall, Bernie→Right-wing
rate, IDF→Resistance rate — a new metric, not tracked in Section 23):**

| Variant | IDF recall | IDF→Resistance | Maria recall | Bernie recall | Bernie→RW | Avg recall |
|---|---|---|---|---|---|---|
| `sbert_original` | 63.5% | 27.0% | 89.5% | 24.5% | 57.5% | 59.2% |
| `sbert_duplicated_original_control` | 58.0% | 31.0% | 85.0% | 28.0% | 56.0% | 57.0% |
| `sbert_full_masked_aug` | 39.0% | 51.0% | 81.5% | 40.5% | 41.5% | 53.7% |
| `sbert_person_masked_aug` | 61.0% | 28.0% | 87.0% | 25.0% | 56.5% | 57.7% |
| `sbert_person_masked_aug_soft_topic` | 54.0% | 32.5% | 83.5% | 40.0% | 40.0% | 59.2% |
| `sbert_person_misc_masked_aug` | 56.5% | 31.5% | 83.5% | 31.0% | 52.0% | 57.0% |
| `sbert_person_misc_masked_aug_soft_topic` | 48.0% | 34.0% | 88.0% | 41.0% | 39.0% | 59.0% |

Secondary metrics (Macro-F1, confusion matrices per variant/author) saved alongside these —
see Implementation below.

**Pre-registered success pattern (multi-condition, not a single-metric winner).** A variant is
only "interesting" if it simultaneously: (a) improves Bernie's recall vs. `sbert_original`; (b)
reduces Bernie's →Right-wing rate vs. `sbert_original`; (c) hurts IDF's recall significantly
LESS than `sbert_full_masked_aug` does (vs. original); (d) preserves Maria's recall (within
5pp of original); AND (e) is not fully explained by `sbert_duplicated_original_control` alone.
Checked against all 4 new variants:

| Variant | (a) Bernie↑ | (b) Bernie→RW↓ | (c) IDF cost < full-masking cost | (d) Maria preserved | (e) not just duplication | All 5? |
|---|---|---|---|---|---|---|
| `sbert_person_masked_aug` | True | True | True (2.5pp vs 24.5pp) | True | **False** | No |
| `sbert_person_misc_masked_aug` | True | True | True (7.0pp vs 24.5pp) | **False** (−6.0pp) | True | No |
| `sbert_person_masked_aug_soft_topic` | True | True | True (9.5pp vs 24.5pp) | **False** (−6.0pp) | True | No |
| `sbert_person_misc_masked_aug_soft_topic` | True | True | True (15.5pp vs 24.5pp) | True (−1.5pp) | True | **Yes** |

**Finding.** Only `sbert_person_misc_masked_aug_soft_topic` meets all 5 pre-registered
conditions. Relative to `sbert_original`, it improves Bernie's recall (24.5%→41.0%, the best
of any variant tested including full masking) and lowers Bernie's →Right-wing rate the most
(57.5%→39.0%), while preserving Maria almost exactly (89.5%→88.0%) and costing IDF
substantially less than full masking (63.5%→48.0%, a 15.5pp drop, vs. full masking's 24.5pp
drop). It is not attributable to the duplicated-original control (which alone only moves
Bernie 24.5%→28.0% and Bernie→RW 57.5%→56.0% — far short of this variant's effect). IDF's
IDF→Resistance rate still rises (27.0%→34.0%), and IDF still pays a real, non-trivial cost —
this is a better trade-off point than full masking, not an elimination of the trade-off.
Average recall across the 3 authors (59.0%) is essentially tied with `sbert_original` (59.2%)
and `sbert_person_masked_aug_soft_topic` (59.2%) — the distinguishing story here is entirely
about the per-author trade-off shape, not raw average recall.

**Limitations.** (1) This entire experiment is exploratory evidence for a hypothesis derived
from looking at IDF's own held-out test set — it is not an independent confirmatory test, and
should not be cited as one. (2) IDF still loses a substantial 15.5pp of recall even under the
"interesting" variant — selective masking reduces, but does not eliminate, IDF's cost. (3) No
variant tested here beats `sbert_original` on average recall by a meaningful margin; the case
for `sbert_person_misc_masked_aug_soft_topic` rests entirely on the Bernie/bias-vs-IDF-cost
trade-off, which is a value judgment, not a strict improvement. (4) Only 3 authors were
evaluated, all already used for hypothesis generation across Sections 19-24 — no claim is
made about how this policy would behave on any other unseen author.

**Proposed next step (not executed here).** If this trade-off is judged worth pursuing, the
required validation step is to evaluate `sbert_person_misc_masked_aug_soft_topic` (or the
underlying PER+MISC-masking-augmentation idea) on fresh held-out authors that were never used
for hypothesis generation in Sections 19-24, to obtain genuinely confirmatory (non-test-informed)
evidence — out of scope for this experiment.

**Implementation:** `experiments/author_generalization/narrative_selective_entity_masking_augmentation.py`.
Reuses `narrative_ablation_loao.AblationDetector` and `train.py`'s `evaluate()`/
`save_confusion_matrix_csv()` unmodified; reuses Section 23's 3 variants verbatim via
`reports/results/narrative_entity_masking_augmentation/results.json`. New corpus-wide raw
(type-annotated) entity cache: `data/cache/cached_raw_entities_by_text.pt` (built once, reused
to derive both masking policies by simple type-filtering, no repeated NER runs). Per-author,
per-policy feature caches: `data/cache/cached_features_selective_masking_{policy}_{author}.pt`
(train/val only — test is never masked in this experiment). Masking-isolation verified on real
corpus examples before training (`--verify-masking`): PERSON-only masking leaves ORG/LOC/MISC
substrings byte-identical to the original text; PERSON+MISC masking leaves ORG/LOC substrings
byte-identical. Checkpoints: `models/experiments/narrative_selective_entity_masking_augmentation/{variant}_{author}.pth`.
Results: `reports/results/narrative_selective_entity_masking_augmentation/results.json`,
`selective_entity_masking_summary.csv`, `confusion_matrix_{variant}_{author}_test.csv`.

---

## 25. Fresh-Author Confirmatory Evaluation — Protocol / Pre-registration

**Status: COMPLETE. All 14 frozen fresh authors × 3 frozen variants trained/evaluated; results
below, exactly as pre-registered above (no protocol changes were made after seeing results).**

**Purpose.** Sections 19–24 are all exploratory: every hypothesis (Soft Topics helping
Right-wing bias, entity masking as a shortcut fix, the PER/PER+MISC selective-masking policy)
was generated and/or refined by looking at results on the SAME 3 held-out authors (`IDF`,
`MariaZakharova`, `BernieSanders`). Section 25 evaluates the single most promising policy from
Section 24 (`sbert_person_misc_masked_aug_soft_topic`) on **fresh authors never individually
used for hypothesis generation in Sections 19–24**, to obtain genuinely confirmatory (not
test-informed) evidence. Everything in this section is fixed BEFORE any training or model
evaluation happens, per explicit instruction — no masking-policy change, no hyperparameter
change, no author swap, no threshold tuning, no re-run with a different seed, and no new
metric introduced after seeing results.

**Fresh-author eligibility (pre-registered):**
- `n_examples >= 200` (comparable in order of magnitude to the original 3 authors' `n_test`).
- Excludes `IDF`, `MariaZakharova`, `BernieSanders`.
- Excludes Gemini/GPT synthetic placeholder authors.
- Excludes any author used to make a decision in Sections 19–24 (in this codebase, that is
  exactly the 3 authors above — see `narrative_fresh_author_audit.py`'s docstring for the
  disclosed operational definition of "used").

This yielded a 43-author eligible pool (all `n_examples>=200`, spanning all 7 narratives).

**Fresh confirmatory set (frozen).** 2 authors drawn uniformly at random, without
replacement, from each narrative's eligible pool, using a single fixed, documented seed
(`42`), computed by `narrative_fresh_author_freeze.py`. The eligible pool was sorted
alphabetically before sampling for reproducibility. **No author may be swapped after this
point, regardless of any later result.**

| Narrative | Author 1 | Author 2 |
|---|---|---|
| Zionist | `BringThemHomeNow` (n=200) | `abualiexpress` (n=200) |
| Resistance | `AlJazeeraEnglish` (n=200) | `PressTV` (n=400) |
| Western | `Bloomberg` (n=200) | `NATO` (n=209) |
| Russian | `KremlinRussia_E` (n=200) | `Slavyangrad` (n=200) |
| Ukrainian | `Babel` (n=200) | `United24Media` (n=200) |
| Right-wing | `TheEpochTimes` (n=200) | `ThePostMillennial` (n=200) |
| Left-wing | `@MiddleEastEye_TG` (n=200) | `ViceNews` (n=200) |

Frozen artifact (full eligible pool + seed + selected authors):
`reports/results/narrative_fresh_author_audit/fresh_author_confirmatory_set.json`.

**Frozen variants (3 only — no sweep, no tuning, no additional variants):**
1. `sbert_original` — SBERT on unmasked text, no augmentation, no topic feature.
2. `sbert_soft_topic` — SBERT + Soft Topic Distribution, no augmentation.
3. `sbert_person_misc_masked_aug_soft_topic` — Section 24's selected policy: PER+MISC-masked
   augmented copy interleaved with the original at training time + Soft Topic Distribution.

Same architecture (`AblationDetector`), hyperparameters (`EPOCHS=20, BATCH_SIZE=16,
LEARNING_RATE=0.001, patience=3, dropout=0.3, hidden_size=128`), SBERT backbone
(`all-MiniLM-L6-v2`), Soft Topic model (`models/experiments/soft_v2_baseline_seeded`),
masking implementation (`EntityAnalysisPipeline` + `mask_entities()` filtered to PER+MISC),
and seed (`42`) as Sections 18–24 — held-out-author LOAO split via `split_leave_one_author`,
one held-out author at a time, for each of the 14 frozen authors.

**Pre-registered primary metric:** true-narrative recall, paired by held-out author. Reported
per variant: mean recall across the 14 authors, median recall, std / IQR, and worst-author
recall.

**Pre-registered non-inferiority rule** (for `sbert_person_misc_masked_aug_soft_topic` vs.
`sbert_original`):
- Margin: **3 percentage points absolute recall**, fixed before seeing any result.
- Non-inferior only if BOTH: mean recall ≥ baseline mean − 3pp, AND median recall ≥ baseline
  median − 3pp.
- Robustness guardrail: no more than 20% of the 14 fresh authors (i.e. > 2 of 14) may show a
  degradation of more than 10pp recall vs. `sbert_original` — otherwise the guardrail fails
  regardless of the mean/median result.

**Pre-registered robustness endpoint** (secondary): per author, the dominant wrong-narrative
and the fraction of that author's errors going to it; then the average dominant-error
concentration is compared across the 3 variants. This tests whether selective masking + soft
topics reduces systematic shortcut-like errors without materially hurting overall recall — not
evaluated per-author in isolation.

**Secondary metrics:** Macro-F1, confusion matrix, accuracy, and per-narrative aggregation
across the 14 fresh authors.

**Pre-registered interpretation (fixed before seeing results, not to be redefined
afterward).** The selective-masking + Soft Topic policy is considered confirmatorily
supported only if ALL of the following hold simultaneously across the 14 fresh authors: (a)
average fresh-author recall is not substantially below `sbert_original` (per the 3pp
non-inferiority rule above); (b) no severe, consistent degradation across multiple fresh
authors (per the ≤20%-of-authors->10pp-degradation guardrail above); (c) at least some fresh
authors show improved robustness / lower dominant-error concentration without a large overall
recall trade-off. This is an aggregate, multi-condition judgment — not a single author's
result, and not a single metric.

**Explicitly out of scope / forbidden for this section:** changing the masking policy,
changing hyperparameters, swapping any of the 14 authors, tuning the eligibility threshold,
re-running with a different seed because a result is unfavorable, or introducing a new metric
after seeing results.

**Implementation:** `experiments/author_generalization/narrative_fresh_author_audit.py`
(Phase 1 — eligibility audit), `experiments/author_generalization/narrative_fresh_author_freeze.py`
(Phase 1b — frozen random selection, seed 42), and
`experiments/author_generalization/narrative_fresh_author_confirmatory.py` (Phase 2 — training +
evaluation for all 14 authors × 3 variants, plus `--aggregate`).

### Results

**Primary metric summary (true-narrative recall, paired by held-out author, n=14 authors):**

| Variant | Mean recall | Median recall | Std | IQR | Worst-author recall | Mean Macro-F1 | Mean dominant-error concentration |
|---|---|---|---|---|---|---|---|
| `sbert_original` (baseline) | 39.0% | 38.8% | 0.236 | 0.360 | 3.0% | 0.0810 | 44.2% |
| `sbert_soft_topic` | 38.6% | 40.0% | 0.228 | 0.342 | 4.0% | 0.0794 | 45.9% |
| `sbert_person_misc_masked_aug_soft_topic` (Section 24's candidate) | 37.1% | 32.7% | 0.235 | 0.375 | 4.0% | 0.0756 | 45.8% |

**Per-narrative mean recall (2 authors/narrative):**

| Narrative | `sbert_original` | `sbert_soft_topic` | `sbert_person_misc_masked_aug_soft_topic` |
|---|---|---|---|
| Left-wing | 10.5% | 12.5% | 12.0% |
| Resistance | 42.3% | 42.6% | 37.5% |
| Right-wing | 57.3% | 57.5% | 63.8% |
| Russian | 36.0% | 37.8% | 26.5% |
| Ukrainian | 68.0% | 62.8% | 65.0% |
| Western | 15.7% | 16.6% | 15.2% |
| Zionist | 43.0% | 40.8% | 40.0% |

**Pre-registered non-inferiority check** (`sbert_person_misc_masked_aug_soft_topic` vs.
`sbert_original`, 3pp margin):
- Mean condition (candidate mean ≥ baseline mean − 3pp): 37.1% ≥ 36.0% → **PASS**.
- Median condition (candidate median ≥ baseline median − 3pp): 32.7% ≥ 35.8% → **FAIL** (candidate
  median is 6.1pp below baseline median, more than double the 3pp margin).
- Robustness guardrail (≤20% of authors with >10pp degradation): 1/14 authors (7.1%) → **PASS**.
- **=> NON-INFERIOR overall (mean AND median AND guardrail): FALSE** — fails solely on the
  median condition.

**Robustness endpoint (secondary):** mean dominant-error concentration is *not* reduced by the
candidate (45.8%) relative to baseline (44.2%) — condition (c) from the pre-registered
interpretation ("at least some fresh authors show improved robustness / lower dominant-error
concentration without a large overall trade-off") is **not supported** either: per-narrative,
the candidate only clearly beats baseline recall on Right-wing (+6.5pp) and Left-wing (+1.5pp,
both already the worst-performing narratives in absolute terms), while losing on Resistance
(−4.8pp), Russian (−9.5pp), Ukrainian (−3.0pp), Zionist (−3.0pp), and Western (roughly flat).

**Interpretation.** Per the pre-registered rule, all of (a)/(b)/(c) must hold simultaneously for
confirmatory support; (b) passes but (a)'s median condition and (c) both fail. **Section 24's
selective-masking + Soft Topic policy does NOT replicate as confirmatory on fresh, previously
unseen authors.** The gain pattern it showed on `BernieSanders`/`MariaZakharova`/`IDF` (better
Right-wing-bias handling at roughly-tied average recall) does not generalize: on the 14 fresh
authors it trades a modest, uneven Right-wing/Left-wing improvement for larger, broader losses
on Resistance/Russian/Ukrainian/Zionist, pulling the median recall down by more than double the
pre-registered margin. This is consistent with Section 24 itself being flagged as "exploratory
evidence only" (policy chosen using the same test set it was evaluated on) — the confirmatory
test called for in Section 24 now shows that hypothesis does not hold up out-of-sample.

**Decision:** Do **not** adopt `sbert_person_misc_masked_aug_soft_topic` (or any entity-masking
augmentation variant from Sections 21–24) as a production change. The entity-masking-shortcut
line of investigation (Sections 21–25) is closed as a negative/non-generalizing result; no
further masking-policy variants should be tested against these fresh authors (doing so would
itself violate this section's own no-further-tuning pre-registration).

---

## 26. Unseen-Author Error Diagnostics — per-example interpretability study (Decision Tree)

**Status: COMPLETE. Closed as a negative/inconclusive result per the pre-registered stopping
rule below — not extended to Random Forest or further feature engineering.**

**Purpose.** Sections 18–25 established (and then confirmed, Section 25) that the model's
recall drops sharply on entirely unseen authors (LOAO), and that none of the tested
masking/feature-arm interventions reliably fix it. This section is a diagnostic/
interpretability study, NOT a model-improvement attempt: it asks, at the level of individual
test examples (not aggregated per-author metrics), WHICH properties of a text are associated
with the model getting it wrong on an unseen author — to explain, associationally and not
causally, why unseen-author performance degrades. Hypotheses tested: semantic domain shift
(the text is far from its narrative's training distribution in SBERT space), lexical/vocabulary
novelty, entity novelty (new named entities not seen for that narrative in training), topic
drift (soft-topic distribution far from the narrative's training centroid), and simple
stylistic differences.

**Data.** The 14 frozen fresh authors from Section 25 (same frozen set, same `sbert_original`
checkpoints — no new training), one row per held-out test example, **3,009 examples total**.
Author identity itself is never used as a feature. All diagnostic features are computed
strictly from each held-out author's OWN train split (the remaining 13+ authors' data for that
run) — no leakage.

**First pass (minimal, 5 already-existing/cheaply-derived features)** — a deliberately small
first iteration, per the user's explicit "start minimal" instruction:
`text_length`, `entity_count` (from the Section 24 raw-entities cache), `soft_topic_max_prob`,
`soft_topic_entropy` (both from the already-cached BERTopic soft-topic vector), and
`classifier_margin` (top1 − top2 softmax probability from the trained checkpoint's own forward
pass). A single depth-4 Decision Tree (`class_weight="balanced"`) was fit, evaluated by its own
**training-set** accuracy only (no cross-validation in this first pass).

Result: training accuracy 62.4% vs. a 59.9% majority-class baseline (+2.5pp) —
`classifier_margin` dominated feature importance (0.55), followed by `text_length` (0.31);
`entity_count`/`soft_topic_entropy` were minor (0.09/0.05) and `soft_topic_max_prob` was unused
(0.00). `classifier_margin` being dominant is close to tautological (low model confidence
correlating with being wrong is expected for any classifier) and does not explain the
*mechanism* of the LOAO failure — this motivated the second, more targeted pass below.
Artifacts: `reports/results/narrative_unseen_author_error_diagnostics/` (`diagnostic_dataset.csv`,
`feature_importance.csv`, `leaf_error_rates.csv`, `tree_rules.txt`, `tree.png`, `summary.json`).

**Second pass (domain-shift/novelty-focused, 11 features, `classifier_margin` excluded).**
`classifier_margin` was removed from the feature set entirely (reported only in the first pass
above, as a sanity check — not mixed into this pass's tree) so the tree cannot "explain" errors
via the model's own confidence. Features, all computed from the author's own train split:

- *Semantic (SBERT cosine):* `nearest_train_sbert_similarity` (max similarity to any train
  example), `mean_same_narrative_similarity` (mean similarity to same-narrative train
  examples), `distance_to_same_narrative_centroid` (1 − cosine similarity to the mean embedding
  of same-narrative train examples).
- *Entity/lexical novelty:* `entity_overlap_ratio_with_train` (fraction of the example's
  entities seen anywhere in the author's train split, any narrative), `entity_novelty_ratio`
  (1 − fraction of entities seen specifically in same-narrative train texts — narrative-specific
  novelty even if the entity is known elsewhere), `lexical_overlap_with_train` (fraction of
  content tokens, via `analyze_agendas.tokenize`, seen in same-narrative train texts).
- *Topic:* `topic_distribution_distance_to_same_narrative_train` (Euclidean distance between the
  example's soft-topic vector and the same-narrative train centroid).
- *Basic style (naive, regex-based, no new NLP model):* `avg_sentence_length`,
  `punctuation_rate`, `hashtag_count`, `mention_count`.

**Evaluation.** Per explicit instruction, not training accuracy alone: **`StratifiedGroupKFold`,
5 folds, grouped by author** (so no author's examples leak across folds — a plain random split
would overstate generalization since rows from the same author are highly correlated), at
`max_depth ∈ {3, 4, 5}`, `min_samples_leaf=25`, `class_weight="balanced"`, seed `42` throughout.
A separate full-data fit (depth=4) was used only for interpretation (feature importance / tree
rules / per-leaf stats), never for the generalization-accuracy claim.

### Results

**Baseline:** majority-class accuracy (always predict "incorrect") = **59.9%** (overall correct
rate = 40.1%, n=3,009).

**Grouped 5-fold cross-validation accuracy (the honest generalization estimate):**

| `max_depth` | CV accuracy | Std | vs. 59.9% baseline |
|---|---|---|---|
| 3 | 56.7% | ±3.9pp | below |
| 4 | 57.3% | ±4.6pp | below |
| 5 | 59.0% | ±5.7pp | below (closest) |

**No tested configuration beat the majority-class baseline.**

**Full-data fit feature importance (depth=4, for interpretation only — NOT supported by the CV
result above):**

| Feature | Importance |
|---|---|
| `distance_to_same_narrative_centroid` | ≈0.59 |
| `topic_distribution_distance_to_same_narrative_train` | ≈0.30 |
| `punctuation_rate` | ≈0.05 |
| `lexical_overlap_with_train` | ≈0.05 |
| `entity_novelty_ratio` | ≈0.01 |
| `mean_same_narrative_similarity` | ≈0.01 |
| `nearest_train_sbert_similarity`, `entity_overlap_ratio_with_train`, `avg_sentence_length`, `hashtag_count`, `mention_count` | 0.00 (unused) |

This full-data fit looks like it has a strong, clean story (semantic distance to the
same-narrative centroid + topic drift "explain" errors) — but this is **not generalized
evidence**: the grouped CV above shows none of the depths beat the trivial baseline, and the
per-leaf error rates (`reports/results/narrative_unseen_author_domain_shift_diagnostics/leaf_error_rates.csv`)
show no monotonic or otherwise stable pattern across leaves (error rates ranging 17.6%–93.5%
across leaves of only 27–56 to several-hundred examples, in no consistent order relative to the
splitting features) — consistent with the full-data fit overfitting to noise rather than
capturing a real, reproducible mechanism.

Artifacts: `reports/results/narrative_unseen_author_domain_shift_diagnostics/`
(`diagnostic_dataset.csv`, `feature_importance.csv`, `leaf_error_rates.csv`, `tree_rules.txt`,
`tree.png`, `summary.json` — the latter records the seed, config, CV results and conclusion
verbatim for reproducibility).

**Interpretation.** Under grouped cross-validation, the tested semantic, lexical, entity, topic,
and simple stylistic features did not predict unseen-author classification errors above the
majority baseline. Therefore, no stable per-example explanatory pattern was identified with the
available diagnostic features. **This is not evidence that domain shift is not the cause** —
only that it was not detectable as a stable per-example pattern with the features and the
shallow-tree method tried here; the underlying failure may be more diffuse/author-global (not
decomposable into a handful of per-example features) or may require a different
modeling/feature approach than attempted in this section.

**Decision (pre-registered stopping rule, set by the user before seeing the second pass's
results):** since the tree does not predict errors above baseline and no clear/stable pattern
emerged, this Decision-Tree diagnostics line is **closed here** — not extended to Random Forest,
permutation importance, or further feature engineering. No production change was made or
considered at any point in this section.

---

## Summary

| Experiment | Change | Main Result | Decision |
|---|---|---|---|
| 1. Soft clustering | Added `approximate_distribution()`-based multi-topic scoring (`get_topic_distribution`, `analyze_soft_topics.py`) | New capability works; requires a ctfidf-saved model | Adopted |
| 2. `save_ctfidf=True` + model versioning | Fixed `NotFittedError`; split legacy (369 topics, classifier-facing) vs. soft_v2 (310 topics, soft-scoring) models | Legacy checkpoints protected from re-fit renumbering | Adopted (both paths kept permanently) |
| 3. URL/mention/hashtag preprocessing | Added `clean_text_for_topic_model()` (+ bare-shortlink handling), unified train/inference cleaning | Removed concrete junk topics (ddgeopolitics, bringthemhomenow); outliers 35.0%→34.0%, agreement 55.0%→56.1% | Adopted permanently in `train_topics.py`/`stance.py` |
| 4. Dedup analysis + threshold=0.7 retrain | MinHash/LSH near-dup detection; dedup wired into training | ~1.7% of corpus removed; all quality deltas within run-to-run noise; maria/lying confirmed not duplicate-driven | Kept in `train_topics.py` as hygiene, not a proven quality fix |
| 5. Experiment C (representation) | Bigram vectorizer + reduce_frequent_words + MMR + multi-word labels, `update_topics()` only | Clustering unchanged (verified); most vague labels became descriptive; can't fix incoherent small clusters or merge duplicates | Adopted (labeling approach + `get_topic_label(top_n_words=3)`) |
| 6. Experiment A (`min_topic_size` 25/35) | Raised HDBSCAN granularity, seeded UMAP baseline | Fixed rulesbased duplicate + small-topic fragmentation, BUT caused severe mega-topic collapse (top-2 topics = 43.1% of corpus at mts=35) | **Rejected** — stayed at `min_topic_size=10` |
| 7. Experiment A2 (`min_topic_size=15`) | Milder granularity increase, one more sweep point | Mega-topic collapse avoided, but rulesbased duplicate NOT fixed, one control topic already lost, soft-signal coverage dropped 51.1%→42.5% | **Rejected** — stayed at `min_topic_size=10` |
| 10. Experiment D (duplicate-topic detection + rulesbased merge test) | Scored all 39,621 topic pairs (semantic+lexical similarity); tested `merge_topics()` on the one confirmed duplicate pair, on a separate model copy | Only the known rulesbased pair (score 0.461) is a genuine duplicate among top-20 candidates (others are same-domain-but-distinct); merge is clean (280/280 other topics' document membership unaffected) but shifts unrelated topics' *displayed* top-words (mean Jaccard 0.240) due to corpus-wide c-TF-IDF recompute; quality metrics improve modestly | Merge validated as safe/beneficial in isolation; **adoption on production model deferred to user** |
| 16. Experiment F (corpus-size × `min_topic_size` scaling sweep) | Stratified subsampling (4K/8K/12K/16K, 4-source × 7-narrative mix preserved), swept `min_topic_size` per size × 2 UMAP seeds (44 fitted models), scored via a pre-defined multi-metric composite + mega-topic veto | Best `min_topic_size` was **10 at every tested size** — constant fits far better than sqrt/linear/log; the old sqrt-down-scaling heuristic (section 12) is empirically refuted for smaller corpora (mts=5 always scored worst) | `recommend_min_topic_size()` rewritten: constant 10 up to the tested anchor (~16,062), small unvalidated log-based extrapolation beyond it |
| 17. Hybrid Hard/Soft topic representation (`hard` dominant→Hard else→Soft, VAL-only threshold) | Per-example routing between Hard one-hot and Soft distribution vectors fed into the same `TopicFeatureLayer`, threshold chosen on VAL Macro-F1 only | Hybrid (60.79% Acc / 0.6036 F1) ties Soft, loses to Hard-only (65.91% / 0.6522) on **both** the dominant and ambiguous subsets — no population segment benefits | **Rejected** — kept single hard `topic_id` as the production representation |
| 18. Leave-One-Author-Out (LOAO) generalization test | Held out all posts from one real account per narrative (`IDF`, `MariaZakharova`, `BernieSanders`), trained `baseline_fusion` from scratch on the remaining authors, evaluated recall on the held-out account | All 3 accounts lost 20–38pp recall vs. random-split F1 (well past the declared ≲10pp "acceptable" bar); 2 of 3 (`MariaZakharova`, `BernieSanders`) systematically misrouted 50–57.5% of posts to Right-wing specifically, not diffuse errors | Diagnostic finding, no architecture change made; sharpens the "maria/lying" open problem into a concrete reproducible symptom; author-style memorization vs. generalization remains an open problem |
| 19. Feature ablation + Soft Topics on LOAO authors | 7 "SBERT + X" variants (NER/SRL/Emotion/Hard-Topic/Soft-Topic/all-engineered/all+soft) trained on the same 3 held-out authors as #18, same splits; plus a Right-wing "shortcut" forensic analysis (entity/word/topic overlap between misclassified-as-RW rows and Right-wing's own training data) | No single feature/combo wins across all 3 authors; Soft Topics gave the best Right-wing-bias reduction (avg 20.8%→16.7%, Bernie 57.5%→46.0%) at some cost to IDF's recall; `sbert_all_engineered` gave the best avg recall (60.5%) but didn't reduce Bernie's Right-wing rate; stacking all arms together was the **worst** variant for MariaZakharova (91.5%→66.5% recall). Forensic analysis found a concrete mechanism for Bernie: NER's entity arm has no stance signal, so his heavy mentions of Trump/Congress/Republicans/Americans (also top entities in Right-wing's own training data, opposite stance) get routed toward Right-wing regardless of his actual (opposing) stance | Diagnostic only, no production change; Soft Topic Distribution flagged as the most promising future integration candidate for reducing Right-wing misrouting; NER's stance-blindness identified as a concrete target for future Domain-Adversarial Training/stance-aware entity work |
| 20. Hard vs. Soft vs. LDA, minimal SBERT-only backbone, random split + LOAO side-by-side | Same `SBERTTopicDetector` architecture (SBERT + at most one Topic arm) evaluated under BOTH random split (3 seeds × 4 modes) and the same 3 LOAO authors as #18/19 (`lda` newly trained, `none`/`hard`/`soft` reused+verified from #19) | Random split: Hard and Soft are **tied** (no evidence of an advantage either way, −0.03pp well inside seed std); Hard/LDA give small, seed-stable gains over SBERT-only (+0.48pp / +0.24pp Acc). LOAO: Soft clearly beats Hard (+7.0pp recall, Right-wing bias 16.7% vs. 20.8%) but does **not** beat SBERT-only on avg recall (59.0% vs. 59.2%) — its LOAO benefit vs. SBERT-only is specifically Right-wing-bias reduction, not recall; Hard is *worse* than SBERT-only on LOAO (−7.2pp recall); LDA is a middle ground (better than Hard on recall/bias, but its Macro-F1 0.1210 is slightly above Soft's 0.1191). Ranking reverses by evaluation regime, confirmed architecture-independent — replicates Section 15 vs. 19's contradiction with architecture held constant | Diagnostic only, no production change; Soft's evidence-backed contribution is robustness/Right-wing-bias reduction on unseen authors, not raw accuracy or recall — ~48% of rows get an all-zero `soft_dense` vector (Soft inactive there), a limitation on how large this effect can be; not claimed as a general in-distribution accuracy upgrade |
| 21. Entity Shortcut Test — mask entity identity, re-evaluate LOAO recall/Right-wing-bias | Every named entity span (PER/ORG/LOC/MISC) replaced with a generic placeholder token before SBERT encoding (`"Trump criticized Biden"` → `"[PERSON] criticized [PERSON]"`); 2 new variants (`sbert_masked`, `sbert_masked_soft_topic`) trained on the same 3 LOAO authors as #18-20, compared against 3 reused Section-19 variants (`sbert_only`/`sbert_ner`/`sbert_soft_topic`) | Effect is **author-dependent, not uniform**: masking hurts IDF and MariaZakharova (recall 63.5%→38.5% and 89.5%→76.5%, Right-wing rate *rises*) but helps BernieSanders — the one author Section 19's forensic analysis implicated (recall 24.5%→30.5%, Right-wing rate 57.5%→42.0%, further down to 30.5% when combined with Soft Topics). Averaged-across-authors numbers (recall 59.2%→48.5%) obscure this split and are not representative of any one author | Diagnostic only, no production change; directionally consistent with (but does not prove) an entity-identity-without-stance shortcut specific to Bernie/Right-wing's shared entity vocabulary; entity identity is legitimate signal, not a shortcut, for IDF/Maria — masking is not a general-purpose fix; stance-aware entity representation (Experiment 22) proposed as the next step, contingent on this finding |
| 22. Stance-Aware Entity Representation — representation-validation gate for entity-targeted stance extraction | 30-row hand-annotated pilot (3 LOAO authors) used to gate 5 stance-extraction candidates (2 ABSA context widths + SemEval target-stance + NLI zero-shot target-stance + PRO/CON debate-stance) against a pre-declared bar (≥70–75% accuracy, not author-dependent, no new systematic failure mode, balanced across pos/neg/neutral, genuinely target-sensitive) — **before** any LOAO training | Best raw accuracy (`absa_full`, 66.7%) fails on author-dependence (90% Bernie vs. 40% IDF) and introduces a new failure mode (neutral recall collapses to 0.14); `procon` degenerates to a near-constant "positive" predictor despite 33.3% surface accuracy; `semeval`/`nli` plateau at 56.7–60.0%; target-sensitivity analysis shows most candidates collapse toward generic sentence sentiment rather than true per-target conditioning | **Gate FAILED — stopped before LOAO training.** Negative finding / future work: no evidence the stance-aware-entity idea is wrong, but no evaluated method is reliable enough on this corpus to use as a training feature; would require in-domain fine-tuning or a different representation, not attempted here |
| 23. Entity-Masking Augmentation — training-time invariance vs. full masking/duplication control | Every training/validation example contributes both its original and entity-masked version under the same label (`sbert_masked_aug`), + a `sbert_masked_aug_soft_topic` combo, + a `sbert_duplicated_original_control` (2x duplicated, no masking) to isolate "more rows" from "masking"; same 3 LOAO authors/split/seed/architecture as #18-21; 3 of 6 variants reused verbatim from #21 | Augmentation captures **more** than full masking's Bernie benefit (recall 24.5%→40.5%, Right-wing rate 57.5%→38.0% with Soft Topics — the best Bernie Right-wing result in the project) while nearly eliminating Maria's cost (89.5%→90.0% with Soft Topics, vs. −13.0pp for full masking); IDF's cost is barely reduced vs. full masking (−24.5pp vs. −25.0pp). The duplicated-original control confirms Bernie's gain is attributable to masking itself, not row count (+3.5pp control vs. +16.0pp augmentation). On **average recall**, `sbert_masked_aug_soft_topic` (57.0%) is actually *below* both `sbert_original` (59.2%) and `sbert_soft_topic` (59.0%) — it is a robustness/bias trade-off, not an overall accuracy win. A root-cause audit of IDF's regressions (test-informed, exploratory) found LOC/ORG entities enriched but PER/MISC not, motivating Section 24 | Diagnostic only, no production change; NOT the best overall model — a narrow, author-dependent trade-off (Bernie/bias improves, Maria roughly preserved, IDF pays a large unresolved cost); root-cause audit of IDF's degradation proposed as immediate next step before any further training |
| 24. Selective Entity-Masking Augmentation — exploratory test of a test-informed hypothesis | 4 new variants masking only PER, or PER+MISC (policy fixed in advance per Section 23's audit), ± Soft Topics; same 3 LOAO authors/split/seed/architecture as #18-23; 3 of 7 variants reused verbatim from #23 | `sbert_person_misc_masked_aug_soft_topic` is the only variant meeting a pre-registered 5-condition success pattern: Bernie recall 24.5%→41.0% (best in project) and →Right-wing 57.5%→39.0%, Maria preserved (89.5%→88.0%), IDF's cost reduced vs. full masking (−15.5pp vs. −24.5pp) but not eliminated, and not explained by the duplicated-original control alone. Average recall is essentially tied with `sbert_original` (59.0% vs. 59.2%) | **Exploratory evidence only — not validated or confirmed** (masking policy was chosen using the same IDF test set this experiment evaluates on); no production change; required next step (not done here) is testing this policy on fresh held-out authors never used for hypothesis generation in Sections 19-24 |
| 25. Fresh-Author Confirmatory Evaluation — pre-registered test of Section 24's candidate on unseen authors | 14 fresh authors (2/narrative, seed=42, frozen before training), 3 frozen variants (`sbert_original`, `sbert_soft_topic`, `sbert_person_misc_masked_aug_soft_topic`), same architecture/hyperparameters/seed as #18-24; pre-registered 3pp non-inferiority margin (mean+median) and ≤20%-of-authors->10pp-degradation guardrail | Guardrail passes (1/14 authors degrade >10pp) and mean recall is ~tied (37.1% vs. 39.0%), but median recall fails the margin (32.7% vs. 38.8%, baseline−3pp=35.8%); dominant-error concentration is *not* reduced (45.8% vs. 44.2% baseline); per-narrative gains are limited to Right-wing/Left-wing while Resistance/Russian/Ukrainian/Zionist regress | **NON-INFERIOR = FALSE** — Section 24's policy does not replicate as confirmatory; entity-masking-augmentation line of investigation (Sections 21-25) closed as a negative/non-generalizing result, no production adoption |
| 26. Unseen-Author Error Diagnostics — per-example interpretability study (Decision Tree) | First pass: 5 generic features (`text_length`/`entity_count`/`soft_topic_max_prob`/`soft_topic_entropy`/`classifier_margin`), training accuracy only. Second pass: 11 domain-shift/novelty/style features (SBERT similarity-to-train, entity/lexical novelty, topic-distribution distance, basic style), `classifier_margin` excluded, evaluated via `StratifiedGroupKFold` (5-fold, grouped by author) at depth 3/4/5, on all 3,009 test examples from Section 25's 14 fresh authors | First pass: training accuracy 62.4% vs. 59.9% majority baseline (+2.5pp), dominated by near-tautological `classifier_margin`. Second pass: grouped CV accuracy 56.7%/57.3%/59.0% (depth 3/4/5) — **none beat the 59.9% majority baseline**; full-data-fit feature importance (`distance_to_same_narrative_centroid`≈0.59, `topic_distribution_distance`≈0.30) is not supported by the CV result, and per-leaf error rates show no stable/monotonic pattern | **Closed as negative/inconclusive per the user's pre-registered stopping rule** — not extended to Random Forest or further feature engineering; no evidence domain shift *isn't* the cause, only that no stable per-example pattern was detectable with the tried features/method |

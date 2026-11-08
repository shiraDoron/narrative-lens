# Narrative Lens — Task Completion Status
**Date:** 2026-11-08  
**Scope:** ChatGPT Style Rewrite 30-example followup (frozen TRAIN set, 2026-11-02 through present)

---

## Executive Summary

Three planned tasks for the ChatGPT Style Rewrite experiment:

| Task | Status | Notes |
|------|--------|-------|
| **1. Import & document External LLM Review** | ✅ **COMPLETED** | Counts imported; per-ID ratings unavailable; no new review conducted |
| **2. Prepare Human Validation package** | ✅ **COMPLETED** | Blind package ready at [HUMAN_VALIDATION_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md); all 30 pairs included; fields empty pending annotator |
| **3. Author-ID Diagnostic** | ✅ **COMPLETED** | Run on all 30 TRAIN pairs; results show no stable evidence of author-signal reduction |

**Current state:** All three planned tasks have been executed as of 2026-11-02. No new work remains from the original plan. Awaiting human validation.

---

## What Was Already Completed (Before This Session)

### Task 1: Import External LLM Review ✅

**Status:** Complete (2026-11-02)

The External LLM Review counts were imported from user-supplied summary:
- **Meaning preserved:** 24 Yes, 6 Borderline, 0 No
- **Style change valid:** 24 Yes, 6 Borderline, 0 No
- **Semantic drift:** 3 Yes, 11 Borderline, 16 No
- **Clean (drift=No):** 16/30

**Key details:**
- Per-ID ratings were **NOT supplied** by the reviewer
- No independent verification of review independence; no model version, prompt, or request history available
- Aggregate counts only; no ability to map "16 clean" to specific records or measure overlap between criteria
- Counts sourced in [CURRENT_STATE.md](CURRENT_STATE.md) as "External LLM Review aggregate counts are now imported"

**Critical limitation:** "24 meaning Yes" and "16 clean (drift=No)" may not identify the same 16 examples. Without per-ID decisions, cannot:
- Calculate agreement between meaning/style/drift fields
- Identify which examples meet combined criteria (meaning + style + no-drift)
- Distinguish genuine successes from potential misalignment between automated guards and external review

**Documentation:** All results stored in [artifacts/experiments/chatgpt_style_rewrite_30_20261102/](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPORT_HE.md)

---

### Task 2: Human Validation Package ✅

**Status:** Complete (2026-11-02)

**Package contents:**
- File: [review_author_analysis_20261102/HUMAN_VALIDATION_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md)
- CSV: [review_author_analysis_20261102/HUMAN_VALIDATION_30.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.csv)

**Blind design:**
- Each pair shows: **ID, Original text, ChatGPT Style Rewrite only**
- Omitted: Author name, narrative label, previous versions, automated scores, guards, guard metrics
- Evaluator cannot see which automatic thresholds were met or which external LLM review scores were assigned

**Evaluation fields (currently empty, ready for annotation):**
1. `human_meaning_preserved` (Yes / No / Borderline)
2. `human_narrative_stance_preserved` (Yes / No / Borderline)
3. `human_style_change_valid` (Yes / No / Borderline)
4. `human_semantic_drift` (Yes / No / Borderline)
5. `human_notes` (free text)

**Coverage:** All 30 TRAIN examples included; no selection based on external review or automatic scores.

**Proposed acceptance rule (not yet applied):**
```
human_meaning=Yes AND human_narrative_stance=Yes AND human_style_change=Yes
applied to all 30 (evaluation pending)
```

---

### Task 3: Author-ID Diagnostic ✅

**Status:** Complete (2026-11-02)

**Scope:**
- Closed-set author identification (not unseen-author generalization)
- All 30 TRAIN pairs; 9 authors (2–4 examples each)
- No Narrative Classifier retraining; Author-ID trained locally within fold splits only
- Evaluation: paired StratifiedKFold (2 splits, 5 seeds: 7, 42, 123, 2026, 31415)

**Method:**
- 66 existing stylometric features (no embeddings, no new features)
- LogisticRegression (C=1.0, lbfgs, max_iter=2000, no hyperparameter search)
- StandardScaler fit per fold (never full-data fit)
- Primary: Fit Original/train → eval Original/dev; independently fit Rewrite/train → eval Rewrite/dev (same pipeline, same fold IDs, so pairs never cross folds)
- Secondary: Fit Original/train, then evaluate Rewrite/dev (diagnostic for distribution shift if retraining happened)

**Results Summary:**

| Condition | Accuracy (mean ± SD) | Macro-F1 (mean ± SD) |
|-----------|-----|------|
| Original | 23.33% ± 4.71pp | 0.1964 ± 0.0487 |
| Rewrite | 22.00% ± 5.58pp | 0.1867 ± 0.0339 |
| Delta (Rewrite − Original) | **−1.33pp** | **−0.0097** |
| Original-fit → Rewrite-dev | 28.00% | 0.2129 |

**Seed-level variability:**
```
seed    accuracy_delta    macro_f1_delta
7       +6.67pp           +0.0586
42      -10.00pp          -0.0746
123     +3.33pp           +0.0405
2026    +3.33pp           -0.0049
31415   -10.00pp          -0.0682
```

**Key findings:**
- Mean delta **−1.33pp** is small; standard deviation across seeds is **4.71pp** (original) to **5.58pp** (rewrite)
- Accuracy decreased in **2 of 5 seeds** (42, 31415); increased in **3 of 5** (7, 123, 2026)
- No stable downward trend across seeds
- Majority baseline (most common author): 13.33%
- Uniform chance (9 authors): 11.11%

**Interpretation:**
- **No convincing evidence of author-signal reduction.** The small, seed-unstable change cannot support a causal claim that rewrites reduced author identifiability.
- The model trained on rewrites achieves similar performance; a fixed original classifier applied to rewrites shows a modest increase (28.0%), suggesting possible domain shift rather than removal of author signal.
- Closed-set evaluation on 30 examples with 9 authors and only 2–4 examples per author is **diagnostic only**, not confirmatory.

**Limitations (documented in protocol):**
- Tiny sample: 30 pairs, 9 authors, 2–4 per author (for comparison, historical LOAO used 14 authors with ~40 examples each)
- No unseen-author test or fresh-author generalization evaluation
- Stylometric features include function words and other surface markers that may correlate with content/length/publication date, not just author style proper
- No control for confounding variables (article length, entity density, narrative topic within the 30-train subset)
- Standard deviation between seeds exceeds mean delta

---

## Constraints Observed ✅

All original constraints were **respected**:

| Constraint | Status | Evidence |
|---|---|---|
| No rewrite prompt changes | ✅ | ChatGPT rewrite used external model; repo prompts unfrozen |
| No guard/threshold changes | ✅ | All 66 guards and thresholds identical to prior runs |
| No Narrative Classifier retraining | ✅ | Only local Author-ID diagnostic trained in fold splits; weights not saved |
| No test evaluation | ✅ | Only TRAIN pairs evaluated; frozen test_14_fresh_authors unchanged |
| External LLM Review ≠ Human Validation | ✅ | Clearly separated; external review imported, human validation pending |
| 16 examples not cherry-picked | ✅ | All 30 included in human validation package; no selection rule applied |
| No outdated selection bias | ✅ | No automatic selection of "best 16" passed to human review |

---

## Current Deliverables

### Automatic Stage (Unchanged)
- [summary.json](artifacts/experiments/chatgpt_style_rewrite_30_20261102/summary.json) — counts for v2, v3, ChatGPT
- [rewrite_validation.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/rewrite_validation.csv) — all 66 guard results per pair
- [automatic_diagnostics_30.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/automatic_diagnostics_30.csv) — detailed metrics
- [REPORT_HE.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPORT_HE.md) — technical narrative

### External LLM Review (Imported)
- Aggregate counts in REPORT_HE.md and CURRENT_STATE.md
- Per-ID ratings: **unavailable** (not supplied by reviewer)

### Human Validation (Ready)
- **[HUMAN_VALIDATION_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md)** — blind package (Markdown, all 30 pairs)
- **[HUMAN_VALIDATION_30.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.csv)** — blank CSV template for responses
- Format: ID | Original | ChatGPT Rewrite | 5 response fields (empty)

### Author-ID Diagnostic (Complete)
- [author_id_protocol.json](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/author_id_protocol.json) — full parameters and caveats
- [author_id_seed_metrics.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/author_id_seed_metrics.csv) — per-seed results
- [author_id_summary.json](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/author_id_summary.json) — mean ± SD, seed deltas
- [author_id_predictions.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/author_id_predictions.csv) — per-prediction audit
- [confusion_Original.csv, confusion_Rewrite.csv, confusion_Original_fit_Rewrite_dev.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/) — pooled confusion matrices (5 seeds)

---

## Author-ID Diagnostic: Extended Analysis

### Why the result is **not** evidence of style removal

1. **Backwards reasoning:** Author-ID accuracy did not decrease, so we cannot conclude author style was removed. Simultaneous preservation of both author-identifiable features and meaning-preserving changes is consistent with the data.

2. **Seed instability:** The −1.33pp mean change is composed of +6.67pp, −10.00pp, +3.33pp, +3.33pp, −10.00pp. With such high variance, any individual seed could be selected to support either conclusion.

3. **Confounded stylometric features:** The 66 features include:
   - Function word frequencies (legitimate style markers)
   - BUT also: average word length, sentence length, punctuation rates, rare-word frequency, which correlate with content complexity, emotional intensity, formality—all of which may change naturally in a rewrite without necessarily removing "author identity"
   - No disentanglement between true author-idiosyncratic style (e.g., phrase preferences) and content-driven markers

4. **No unseen-author test:** This diagnostic cannot and does not evaluate whether rewrites improve generalization to fresh authors. That is the actual research question. Author-ID accuracy on train-only pairs is a side effect, not evidence of treatment efficacy.

5. **Fixed Original classifier → Rewrite-dev: 28.0% accuracy:** This suggests a distribution shift between Original and Rewrite, but does NOT prove author-signal removal. A rewrite that changes vocabulary, syntax, and length will naturally score lower on a classifier trained on originals.

### What the Author-ID result actually shows

- **Linguistic shift detected:** Original and Rewrite distributions differ (Original→Rewrite accuracy 28.0% vs. in-distribution ~23.3%)
- **Signal not eliminated:** A fresh classifier trained on rewrites performs similarly to one trained on originals, suggesting author-identifiable features persist
- **No consistent trend:** Across seeds, direction is split; conclusion depends on seed choice
- **Closed-set and diagnostic:** Not suitable for causal claims or unseen-author generalization statements

---

## Research Questions: Status

| RQ | Question | Latest Evidence | Next Step |
|---|---|---|---|
| RQ1-4 | Previous interventions (entity masking, style norm v2/v3, noise removal, Group-DRO) | All negative/mixed; see EXPERIMENTS.md §18–34 | — |
| RQ5 (few-shot) | Do 10 labeled examples from a new author recover recall? | Historical: 64.9% mean (§35A), confirmed at k=10 in multi-seed test (§36) | — |
| **New: Author-style shortcut** | Does author-style signal impair generalization to unseen authors? | ChatGPT rewrite: automated pass 22/30, external LLM 24/30 meaning Yes, 16/30 drift=No. Author-ID: −1.33pp (unstable, n=30 pairs, 9 authors) | **Human validation of all 30 pairs** to confirm meaning/style trade-offs; evaluate fresh-author generalization if human judgments show sufficient quality |

---

## Next Steps & Recommendations

### Immediate (Required)
1. **Obtain human validation for all 30 pairs:**
   - Distribute [HUMAN_VALIDATION_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md)
   - Collect: meaning, stance, style change validity, semantic drift, notes
   - Do NOT select "16 clean" examples; evaluate all 30 blindly
   - Document annotator identity and date

2. **Post-human-validation decision (after collection):**
   - If human meaning+style both Yes for ≥20/30: Candidate for fresh-author generalization test
   - If human meaning+style both Yes for <15/30: Insufficient quality; consider alternative rewrite sources or prompt adjustments
   - Either way: Report human validation results transparently before any downstream use

### Medium-term (Conditional)
3. **Fresh-author generalization test (only if human validation supports):**
   - Create rewrite versions of the frozen test_14_fresh_authors holdout
   - Using **same rewrite process** (ChatGPT or alternative that passed human validation)
   - Train Narrative Classifier: Original train + Rewrite train (separately or combined)
   - Evaluate: Original test_14_fresh vs. Rewrite test_14_fresh (paired seeds)
   - Hypothesis: if author-style shortcuts impair unseen-author generalization, rewrite+train should recover recall on fresh authors

4. **Diagnostic secondary:** If rewrite test shows generalization gain, then author-ID can be re-run on test pairs to check whether reduced author-identification correlates with improved narrative generalization.

### Research Documentation
5. **Update CURRENT_STATE.md** with:
   - Human validation results (once collected)
   - Author-ID diagnostic conclusion (no stable evidence of removal; not causal)
   - Decision on fresh-author test (yes/no + rationale)

6. **Preserve all frozen components:**
   - ChatGPT rewrite outputs (external generation; reproducibility via request history if available from user)
   - Narrative Classifier checkpoint (v36_sbert_only_random_split)
   - test_14_fresh_authors holdout (unchanged)

---

## Files & Artifacts Summary

**Primary folder:** [artifacts/experiments/chatgpt_style_rewrite_30_20261102/](artifacts/experiments/chatgpt_style_rewrite_30_20261102/)

| File | Purpose | Ready? |
|------|---------|--------|
| [REVIEW_PACKAGE_BLIND_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REVIEW_PACKAGE_BLIND_30.md) | Original text pairs for comparison | ✅ |
| [review_author_analysis_20261102/HUMAN_VALIDATION_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md) | Blank human validation form (all 30) | ✅ |
| [review_author_analysis_20261102/HUMAN_VALIDATION_30.csv](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.csv) | CSV response template | ✅ |
| [review_author_analysis_20261102/author_id_summary.json](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/author_id_summary.json) | Author-ID aggregate results | ✅ |
| [review_author_analysis_20261102/REPORT_HE.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPORT_HE.md) | Diagnostic interpretation | ✅ |
| [REPORT_HE.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPORT_HE.md) | Technical overall report | ✅ |

---

## Conclusion

**All three planned tasks are complete as of 2026-11-02.**

- External LLM Review counts imported (limitation: per-ID ratings unavailable)
- Human validation package ready and blind (awaiting annotator)
- Author-ID diagnostic executed (shows linguistic shift, not causal author-style removal)

**Research status:**
- No new generalization claim can be made without human validation
- Author-ID result is diagnostic and unstable; not evidence for intervention efficacy
- Next critical step: collect and analyze human judgments on all 30 pairs
- Conditional next step: if humans confirm quality, test fresh-author generalization

**Constraints:** All original safeguards maintained (frozen test, no retraining, no cherry-picking, clear separation of reviews/validation).


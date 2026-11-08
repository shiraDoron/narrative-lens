# Review import, blank human validation and author-ID diagnostic

Run from the project root with the existing Python 3.11 environment:

```powershell
python artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/analyze.py
```

The source review is **only the aggregate counts supplied by the user in conversation**, preserved in the script's COUNTS and `external_llm_review_aggregate.json` / `external_llm_review_counts.csv`. No individual review file, ID assignments, reviewer model or prompt was supplied. No per-ID ratings or joint distributions are inferred. `clean according to External LLM Review` means exactly semantic_drift=No, not Human Validation, and not an intersection of preserved fields. Prior v2/v3 No-drift counts are read from their existing imported review summaries, not guessed from meaning ratings.

All 30 Original/Rewrite pairs and author provenance come from the frozen imported ChatGPT run. Study split membership is asserted train-only. All 30 article snapshot hashes are unique; no Original/Rewrite pair crosses a diagnostic fold. This is **closed-set within-train development**, not the research holdout and not unseen-author testing.

The existing 66 raw stylometric features are reused unchanged. There is no encoder inference, trained feature extraction, global standardization or new prompt/guard. StandardScaler is fit inside each training fold; the previous study's fitted scaling is not used. Model choice, C=1, lbfgs, max_iter=2000 and seeds [7,42,123,2026,31415] were fixed before inspecting results. Two-fold stratification is needed because some authors have only two examples. Author counts and exact dependency versions are in `author_id_protocol.json`.

Primary comparison: the **same algorithm/configuration and exact paired folds**, fit separately on Original and Rewrite training portions. Secondary comparison: the **same fitted Original pipeline** evaluated on held-out Original versus their paired Rewrite, revealing transfer/distribution effects. Neither uses the held-out row's counterpart for fitting. All rows participate in out-of-fold development predictions once per seed per representation.

Accuracy and macro-F1 are calculated on 30 out-of-fold predictions for each seed, then averaged. Seed SD describes split sensitivity, not confidence intervals from independent samples. The 150 predictions per representation are five evaluations of the same 30 rows. Pooled confusion matrices have true-author rows and predicted-author columns, total count 150 each. Majority/uniform baselines are descriptive.

No narrative classifier is trained or evaluated. Only the explicitly authorized temporary Author-ID logistic-regression probes are fit; no fitted weights are saved. No frozen test/validation examples, review-based selection, hyperparameter search, new LLM review or human judgments are used. All candidates remain included regardless of auto/review outcomes.

`HUMAN_VALIDATION_30.md` and `.csv` are blank reviewer-facing packages, not completed validation. Re-running the script recreates them blank: **do not rerun over files after humans have filled them**. Save completed human responses separately with reviewer/date provenance. The package includes only ID, Original, ChatGPT Style Rewrite and the five requested blank human fields; all diagnostic/aggregate outputs stay separate. Future acceptance rules must be applied to all 30; none is applied now.

No downloads, installation, checkpoints, weights or runtime logs are required/committed. The script imports existing feature functions and installed sklearn/numpy/scipy. Source hashes and paired-fold/review-template assertions are saved in `integrity_audit.json`. Documentation updates are separate from this reproducible analysis.

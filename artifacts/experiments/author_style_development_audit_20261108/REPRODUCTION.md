# Development corpus and author-style diagnostics — reproduction

Started 2026-11-08. This is a separate development-only experiment, not a rewrite/model-prompt revision. Every text used in fitting, feature extraction, near-duplicate scoring or topic analysis belongs to the nine frozen **train authors**. Validation/test rows are used only for frozen metadata counts/hash-collision audit; their content is never passed to a new feature/model. Prior 218-row audit findings are explicitly marked historical.

From the project root in the existing Python environment:

```powershell
python artifacts/experiments/author_style_development_audit_20261108/run.py --stage audit
python artifacts/experiments/author_style_development_audit_20261108/run.py --stage baselines
python artifacts/experiments/author_style_development_audit_20261108/style_analysis.py
python artifacts/experiments/author_style_development_audit_20261108/baseline_controls.py
python artifacts/experiments/author_style_development_audit_20261108/temporal_sensitivity.py
python artifacts/experiments/author_style_development_audit_20261108/reports.py
python artifacts/experiments/author_style_development_audit_20261108/finalize_audit.py
```

`prepare` is invoked by audit/baselines and freezes `protocol.json` and hashes before model outcomes. `baseline_runtime_audit.json` records numpy/scipy/sklearn versions and hashes of model orchestration/protocol. No packages/downloads/paid cloud/new models are needed. CPU execution uses four BLAS threads by default; inherited source feature helpers may configure local torch threads without loading checkpoint weights. No fitted pipeline or checkpoint is saved.

Data: 429 unique annotated excerpts, but only 202 from train authors are newly analyzed. The 105 eligible narrative train excerpts are a prespecified sensitivity, not the full Author-ID universe. Within-proposed-narrative analyses include 55 Left-wing and 50 Right-wing texts, five authors in each (Harrop occurs in both). Article IDs and near-duplicate connected components are grouped. Raw text and author/topic/label proposals are not sent to an LLM.

The four representations and LR C=1/lbfgs/max_iter=3000 were fixed before outcomes. Repeated StratifiedGroupKFold uses seeds [7,42,123,2026,31415] and min(5, per-author distinct groups) folds, with all methods sharing assignments. TF-IDF/scaling fit only on each fit fold. CV seed metrics aggregate out-of-fold predictions per seed; repeated seeds are not independent data. Numeric features are the existing 66, plus a fixed function-word/rate-punctuation subset (no raw length). Character n-grams and word n-grams intentionally retain lexical/content information. No method is selected using test scores.

Intervention evaluation is a **different** analysis: fit once on 172 original train sources not represented in any of the 30 paired groups, predict held-out Original and ChatGPT Rewrite with that exact fitted model. The eligible-only pool of 75 is a prespecified sensitivity. Paired resampling uses 80% of each training author pool, leaving the same 30 evaluation IDs fixed. All 30 remain included regardless of review/guard results.

Two-sided exact McNemar/binomial probabilities and Holm over the four primary full-pool methods are descriptive development inference. Dependence among texts from an author limits simple McNemar assumptions. Cluster-by-author paired accuracy bootstrap uses 2000 draws, seed 20261108, 95% quantiles; it is not multiplicity-corrected and has only nine clusters. No CV fold t-tests or seed-count significance claims are made. The fold-trained majority reference was added as an audit control after the four fixed methods ran; it does not change any model or select a favorable result.

Style analysis uses paired feature deltas, existing operational metrics and a train-fitted lexical cosine. Standardized feature changes use the 202 train Originals' SD descriptively; these scales are not used in CV pipelines. Rhetorical/uncertainty anchor sets are lexical diagnostics, not semantic adjudications or revised guards. No English parser checkpoint was available, so syntax is explicitly not claimed.

After the primary outcomes, the strong author/year metadata association motivated a separately labeled **post-hoc** temporal sensitivity: all train authors whose source dates are exclusively 2026 (139 texts, six authors; 20 existing pairs). The original protocol/results and all-30 evaluation remain unchanged. Its separate protocol freezes this metadata-only selection before its fits. It uses the same four methods, no new tuning and no confirmatory p-value claim. It cannot isolate content or compare accuracy directly with a nine-class task.

Frozen raw/30-pair/human-review files are read-only and hashed. Human answers are never filled or overwritten. New files include source hashes, author/split counts, duplicate groups, topic/year summaries, every fold and prediction, confusion matrices, model-independent metrics, paired style deltas, exactly 75 additional eligible rewrite source IDs, reports, proposed main-experiment protocol and integrity tests. No new rewrite is generated and no existing threshold, guard, label or split is changed. No Narrative Classifier is trained/evaluated and no frozen test is evaluated.

`reports.py` regenerates reports only; it does not fit models. Run all stages only inside this isolated output directory; do not reuse it for a changed corpus/protocol. If source/human files change, archive this run and create a new version. `TEST_RESULTS.md` records the actual final checks. Root documentation is updated separately after results/tests; source hashes exclude changing root status docs.

`finalize_audit.py` reconstructs the already-used 80% fit subsets from the fixed seeds/pool order, emits the optional balanced-15 and author-only-172 expansion manifests (no rewrites), counts the actual 532 author-probe fits, then executes/records the integrity suite. No models are refit by this stage. After these metadata files exist, tests can also be run alone with `python -m unittest discover -s artifacts/experiments/author_style_development_audit_20261108 -p test_integrity.py -v`.

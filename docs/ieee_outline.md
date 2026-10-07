# IEEE Conference Paper Outline

## 1. Paper skeleton and content map

| IEEE section | Content | Lives today |
|---|---|---|
| Abstract | Headline results only (see Section 3) | Nowhere yet, draft below |
| Introduction + RQs | 7 narratives, SBERT baseline, generalization gap; RQ1 LOAO gap, RQ2 entity shortcut, RQ3 style shortcut (in-distribution ranking as background, not RQ1) | README.md (overview, findings); EXPERIMENTS.md storyline rows 1-8 |
| Related work | Topic modeling, SBERT classification, authorship/style shortcuts, entity bias | docs/related_work.md (15 verified entries, 4 buckets) |
| Dataset | 7 narratives, account-level labels, gemini/gpt/twitter/telegram sources, author_source provenance | docs/narrative_definitions.md; docs/running.md; train.py load_raw_data |
| Method | Three models (sbert_only, hybrid, baseline_fusion); AblationDetector for generalization studies; frozen SBERT all-MiniLM-L6-v2, random_state=42 splits | docs/architecture.md; docs/results.md; experiments/author_generalization/ |
| Experiments | Random-split comparison; LOAO protocol (3 authors); masking variants; fresh-author confirmatory test (14 authors); author-signature trees; style normalization | EXPERIMENTS.md sections 15, 17-28; artifacts/experiments/ |
| Results | sbert_only 0.732 accuracy / 0.730 macro-F1; LOAO recall drops; confirmatory negatives | docs/results.md; Section 3 below |
| Threats to validity | Label-by-account noise, synthetic authors, seed coverage, single embedding model | Partial: docs/results.md known limitation; docs/label_quality_audit.md |
| Conclusion | Negative-result arc: shortcuts exist, tested fixes failed | EXPERIMENTS.md storyline; Section 3 |

## 2. Gaps for IEEE submission

1. Abstract and keywords: draft below, keywords not chosen.
2. Related work: no cited prior work yet, needs verified citations.
3. Threat model and limitations: label provenance caveat is documented but no formal threats section.
4. Reproducibility checklist: commands exist (docs/running.md) but no pinned data snapshot, seed table, or artifact index.
5. Author and contribution statement: no authors, roles, or contact defined.
6. Ethics statement: political-text classification risks, account-level labeling bias, and misuse limits are not addressed.
7. Figures and tables: done: artifacts/figures/ fig1-fig4 + docs/figures.md from measured artifacts.
8. Scope honesty: generalization studies from §19 onward use AblationDetector (see README disclosure added alongside); paper must state this scope explicitly.

## 3. Draft abstract (approx. 150 words, measured results only)

We study narrative classification of political text into seven narratives using frozen SBERT embeddings with alternative fusion heads. On a random split with identical partitions, sbert_only reaches 0.732 accuracy and 0.730 macro-F1, ahead of hybrid (0.722, 0.717) and baseline_fusion (0.671, 0.664). Under leave-one-author-out evaluation on three held-out accounts, recall falls 20 to 38 points relative to random-split F1, with two authors systematically misrouted to Right-wing (57.5 percent, 50.0 percent). A pre-registered confirmatory test of entity-masking augmentation on 14 fresh authors returns NON-INFERIOR as FALSE. Within-narrative decision trees still identify authors far above chance (for example Western 85.1 percent versus about 20 percent baseline). Style normalization reduces that author signal by about 15 points macro-F1 on average yet worsens fresh-author recall for 13 of 14 authors (mean minus 6.4 points, median minus 10.8 points). We report these negative results and release the full experiment log.

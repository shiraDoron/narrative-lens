# Current Research State

Updated: 2026-11-09. This is the changing status page; [README](README.md) provides the stable research overview.

## Current research question

**Can meaning-preserving author-style interventions improve political narrative classification generalization to unseen authors?** Author-style shortcut dependence is a working hypothesis, not a finding. The candidate contribution is empirical/methodological; style rewriting is the intervention instrument, not a new TST invention. [Canonical research direction](THESIS_RESEARCH_DIRECTION_HE.md).

## What is already established

Historical experiments show a large unseen-author gap, measurable author-style signals, and no generalization recovery from the earlier normalization intervention (§28). Few-shot adaptation helped in its separate historical evaluation. See the [research storyline](EXPERIMENTS.md#research-storyline-start-here).

## What is NOT established

No causal evidence yet that removing author style improves generalization. A paraphrase gain alone cannot establish that cause. No new generalization, Macro-F1 or author-identification claim follows from the latest 30-text prompt trials. Automated passes and external LLM judgments are not human gold.

## Current active experiment

**Latest status: extension intake complete75/75.** All five batches match the missing train-only ID set with no duplicates/empty outputs. [Canonical run01](artifacts/experiments/data_completion_20261109/runs/extension_v1_run01/received_rewrites_75.csv) preserves outputs unchanged; [independent human75 package](artifacts/experiments/data_completion_20261109/runs/extension_v1_run01/HUMAN_PAIR_REVIEW_NEW75.md) is populated with pairs and blank ratings. Model/date remain unknown: intake used the null-valued metadata template, with provenance_complete=false. QC dry-run and18 infrastructure tests passed; full semantic/style QC, human ratings and training remain pending. Earlier batch intake entries below are historical.

Latest intake: [Batch 4](artifacts/experiments/data_completion_20261109/received_batches/batch_04/BATCH_04_OUTPUT.csv) received: all15 expected IDs in order, no duplicate IDs or empty outputs; raw paste preserved and rewrites unchanged. Total extension intake60/75. Batch5 and generation metadata remain pending. No semantic QC, human validation, training or test evaluation was run.

Latest intake: [Batch 3](artifacts/experiments/data_completion_20261109/received_batches/batch_03/BATCH_03_OUTPUT.csv) received with all15 expected IDs in order, no duplicates or empty rewrites, and raw paste preserved. Total extension intake45/75; batches4–5 and generation metadata pending. This is structural intake only, not semantic QC or human validation.

Latest intake: [Batch 2](artifacts/experiments/data_completion_20261109/received_batches/batch_02/BATCH_02_OUTPUT.csv) also received: all15 expected IDs, ordered, nonempty and unchanged. Total extension intake30/75; batches3–5 and generation metadata pending. No semantic QC, human validation or training performed on this intake.

Partial intake: [ChatGPT extension Batch 1](artifacts/experiments/data_completion_20261109/received_batches/batch_01/BATCH_01_OUTPUT.csv) received with all15 expected IDs in order; raw paste preserved and Markdown fences removed without rewrite edits. Batches2–5 and actual generation metadata remain pending. Intake validity is not semantic preservation or human validation; no final experiment ran.

**Data completion handoff (2026-11-09):** [Bundle and exact handoff instructions](artifacts/experiments/data_completion_20261109/README_HE.md) now provide 105 proposed-label human review records, 75 missing train-only sources in five batches, a fixed extension prompt, separate human/LLM importers, immutable receipt/text binding, unchanged automatic QC wiring, and a draft 105-source A–E compiler. All 18 infrastructure tests pass. No completed attributable human30 file was found on disk; Claude judgments remain LLM-only. New75 human pair review becomes usable after generation, not before. Legacy30 and frozen source/guard hashes are unchanged. This newly authorized prompt is a distinct protocol cohort, not a reconstruction of the undocumented legacy prompt. No generation, final training, or frozen-test inference was run.

The **main A–E training experiment is prepared but blocked**, not executed. Current audit confirms 202 raw train sources / nine authors, 105 eligible Left/Right machine proposals (55/50), 30 common Original/Paraphrase/Style IDs and 75 missing Style Rewrites. Paraphrases exist for all105. Five draft arms, 25 configs and 25 deterministic schedules use a fixed update/example budget. Source labels and paired human QC are not available as attributable completed per-ID judgments; original ChatGPT prompt/model/parameters are unknown. No new text, model training or validation/test inference was performed in preparation. No process is running.

Read [main protocol](MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md), [deep review of 18 papers](RELATED_WORK_DEEP_REVIEW_HE.md), [closest-work comparison](RELATED_WORK_COMPARISON.md), [contribution candidate](RESEARCH_GAP_AND_CONTRIBUTION_HE.md), and [Evidence Matrix](EVIDENCE_MATRIX_HE.md). CATO's final published title is **Data Augmentations for Improved (Large) Language Model Generalization**; representation-based A and prompted B must be distinguished. Earlier [frozen sensitivity](STYLE_SENSITIVITY_PILOT_HE.md) remains 1/30 flips in each rewrite arm, on sources seen in training, not generalization evidence.

The central [FINAL_REPORT_HE.md](artifacts/experiments/style_intervention_v2_20261026/FINAL_REPORT_HE.md) first describes the completed 218-text V2 automatic stage, then appends the 30-train v2 prompt/review checkpoints. Its 114 matched automatic passes are a different denominator from v2's 6/30. [The new v3 report](artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_v3_30_20261102/REPORT_HE.md) is separate; no prior results were overwritten. Human Validation remains Pending.

## Current results

| Measure on the same 30 examples | Old | New v2 | New v3 |  ChatGPT Rewrite |
|---|---:|---:|---:| ---:|
| All automated preservation checks pass | 23 | 6 | 9 | 22 |
| Substantial style change, operational proxy | 10 | 24 | 26 | 22 |
| Both automated criteria | 7 | 6 | 9 | 15 |
| Exact original copies | 7 | 0 | 0 | 0 |

External LLM Review of **New v2 only**: meaning **10 Yes / 15 Borderline / 5 No**; style change **30/30 Yes**; strict preservation and style together **10/30**. Guard classifications relative to that reviewer: **TP 19 / FP 5 / TN 5 / FN 1**. All 15 Borderline ratings remain separate; all also carry explicit drift=Yes in the supplied review. These v2 ratings do not transfer to v3. The separately supplied v3 review has **5 Yes / 17 Borderline / 8 No** for meaning and **27 Yes / 3 Borderline** for style.

**Interpretation:** style intervention produces stronger stylistic changes, but semantic preservation is the bottleneck. **This does not prove:** actual removal of author identity, improved unseen-author performance, or human-verified semantic drift. No retraining followed the prompt trials. [Full report and per-example evidence](artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/REPORT_HE.md).

## Frozen components

The follow-up's author-disjoint train/validation/test assignments are recorded in [author_splits.csv](artifacts/experiments/verified_human_style_followup_20261026/author_splits.csv) and [analysis_cohort.csv](artifacts/experiments/style_intervention_v2_20261026/analysis_cohort.csv). Its validation and test rows are excluded from current 30-train development. The historical [14-author confirmatory holdout](artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json) is a separate frozen set. Do not conflate them.

Labels, human-review fields, thresholds, filtering, model/runtime and decoding remain unchanged. V3 changes only the prompt by appending targeted safeguards; it is now frozen with its outputs. Any further prompt/threshold change requires a new documented experiment. **External LLM Review ≠ Human Validation.** Automated guards, model-generated proposals, external LLM ratings and Human Validation (**Pending**) remain separate. `human_verified=False` remains false.

## External LLM Review completed — 2026-11-09

Claude independently assessed all 30 ChatGPT-rewritten text pairs on four criteria. **This is an external LLM review, not human validation.**

**Results:**
- Meaning preserved: 30/30 (100%)
- Narrative stance preserved: 30/30 (100%)
- Style change valid: 28/30 Yes, 2/30 Borderline  
- Semantic drift: 0/30 (0%)

**Reviewer-based criterion (meaning + stance + style = Yes, drift = No): 28/30 pairs (93.3%)**
**Flexible criterion (meaning + stance + style Yes or Borderline; drift = No): 30/30 pairs (100%)**

These are Claude's reported judgments, not verified preservation or an applied human acceptance rule. Two cases (creators:421853, creators:418904) have Borderline style ratings. The earlier aggregate review reports different judgments (meaning 24 Yes/6 Borderline; drift 3 Yes/11 Borderline/16 No); the two reviews must remain separate.

**Note:** creators:421951 shows weakening of "No one" → "Few people" (universal to empirical generalization), noted in review and accepted. Human expert may reconsider this edge case.

**Review location and details:** [EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md)

**Human Validation status:** PENDING — 30 text pairs prepared in blank template awaiting independent domain expert review.  
[Template: HUMAN_VALIDATION_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md)

## Next decision

Obtain the actual per-ID human judgments with notes/reviewer/date (the on-disk templates are blank), source-label gold and QC for both rewrite types. The user's reported 30/30 and 28/2 counts were preserved separately as a claim, not converted into invented human rows. Claude's complete per-ID review was imported explicitly as External LLM Review; it does not replace human gold or erase the earlier aggregate review's disagreements. Resolve quantifiers/certainty/intensity cases without overwriting original ratings. Recover original ChatGPT generation provenance before creating the 75 missing outputs, or explicitly register a new generator version rather than silently mixing methods.

Primary future contrasts are C−B and D−E (Original/Paraphrase/Style; Original+Style vs Original+Paraphrase), with common IDs/labels, matched budgets and Original unseen-author evaluation. The QC contract preserves all-attempted coverage and common accepted-only secondary analysis without model-based selection. The historical test sets are not fresh confirmatory holdouts. Sixteen preparation tests passed; [readiness command and reproduction](artifacts/experiments/main_training_preparation_20261109/REPRODUCTION.md) fail closed on missing gold/QC/provenance. No retraining, test evaluation, prompt revision or guard/threshold change was launched.

## Focused guard error analysis — 2026-11-01

הניתוח האיכותני מבחין בין פסילת רשומה לזיהוי השגיאה: חלק מה־TP נתפסו רק בדגל טכני שאינו מסביר את הסיכון הסמנטי. ציטוטים/מסגור מפורש מספקים אותות רלוונטיים; כיסוי אפיון אירוע, תפקידי משתתפים ו־certainty scope חלש. זוהו גם סיכונים במקרים שה־LLM אישר, בלי לשנות את דירוגיו או את 15 מקרי ה־Borderline. זהו ניתוח הסוכן, לא Human Validation. ההמלצות עתידיות בלבד; כל הרכיבים הקפואים נשמרו ולא בוצע אימון או test evaluation.

[Error analysis — ראיות, ספירות והמלצות](artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/ERROR_ANALYSIS_SUMMARY_HE.md)

## Two-stage v2 semantic repair — 2026-11-02

Active follow-up: **train-only intervention development**, fixed v2 → local verification → conditional patch repair → unchanged guards. No new first-stage rewriting. v3 attempted to encode more semantic-preservation constraints in a single rewrite prompt, but external review showed overall degradation relative to v2. Therefore the next experiment separates style rewriting from semantic verification and minimal repair.

Automatic results for repair: pass 6/30, substantial style 24/30, both 6/30, exact copies 0. Actual changes: 1/30; verification/patch failures retain v2 and are reported, not hidden by retries. Local verification is part of the pipeline, not independent external approval. No new external/human review, training or test evaluation. Next step: separately review the Repaired v2 blind package; no further tuning now.

[Repair report](artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REPORT_HE.md) · [Blind package](artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REVIEW_PACKAGE_BLIND_30.md) · [Reproduce](artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REPRODUCTION.md)

## Technical debug and literature checkpoint — 2026-11-02

The completed [six-TRAIN debug](artifacts/experiments/style_intervention_v2_20261026/semantic_repair_debug_subset_20261102/DEBUG_SUBSET_RESULTS.md) separates exact patch applicability from semantic correctness. No full 30-row rerun followed. The previous section's external-review next step is historical; the current decision is the design review above.

[Related Work](docs/style_transfer_related_work_he.md) now distinguishes StyleRemix's authorship obfuscation, Lai et al.'s reward-based formality training, Zhang et al.'s training-free decomposition/self-check, and our narrative-preserving intervention question. The proposed hybrid architecture is documentation only. No experimental code or data changed during this literature update; no new experiment was run.

## Existing-tool feasibility checkpoint — 2026-11-02

Read the pinned StyleRemix and Thank you BART repositories and checked official checkpoint/demo metadata. StyleRemix exposes direct text inference and 16 adapters; local hardware and hosted-service availability prevent a reasonable run here. BART's checked repo supplies style classifiers but not the transfer checkpoint needed by infer.py; no legacy environment was installed. No official Zhang et al. implementation was identified in the checked sources. [Full findings and reproduction](docs/existing_style_transfer_tools_evaluation_he.md).

The planned nine-TRAIN subset has existing v2 automatic pass/style/both/exact-copy counts **2/9, 8/9, 2/9, 0/9**; StyleRemix is **N/A, not 0/9**. This is a prepared baseline, not a completed comparative benchmark. No inference, new guard run, human/external review, classifier training or repair development followed this audit.

## ChatGPT Style Rewrite — 2026-11-02

ניסוי נפרד של generator חלופי, לבדיקת style change + semantic preservation על אותם 30 מקורות train בלבד. ה־CSV המקורי נשמר byte-for-byte; כל ID חובר למקורו והשכתובים לא נערכו. לפי דיווח המשתמש נכתבו מ־Original בלבד, ללא גרסאות/מדדים/ביקורות קודמות; פרטי generation מלאים אינם זמינים לאימות עצמאי.

| Metric | v2 | v3 | ChatGPT Rewrite |
| --- | --- | --- | --- |
| automated preservation pass | 6/30 | 9/30 | 22/30 |
| substantial style change | 24/30 | 26/30 | 22/30 |
| both preservation + style | 6/30 | 9/30 | 15/30 |
| exact copies | 0/30 | 0/30 | 0/30 |

Automated pass הוא signal בלבד; substantial style הוא proxy. אין עדיין External LLM Review עצמאי לתוצרים אלה או Human Validation, ואין להסיק הצלחת פתרון או generalization. לא שונו guards, ספים, חלוקה, תוויות, scaling או שדות אנושיים קיימים; לא בוצעו training, test evaluation או LoRA. עוצרים לפני ביקורת חיצונית חדשה.

[Report](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPORT_HE.md) · [Blind review input](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REVIEW_PACKAGE_BLIND_30.md) · [Reproduce](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPRODUCTION.md)
<!-- END_CHATGPT_REWRITE_30 -->


## ChatGPT external review and author signals — 2026-11-02

נשמרו ספירות External LLM Review שסיפק המשתמש: Meaning 24 Yes / 6 Borderline / 0 No; Style 24 Yes / 6 Borderline / 0 No; Semantic drift 3 Yes / 11 Borderline / 16 No. **16 clean according to External LLM Review**, לפי drift=No בלבד — לא Human Validation ולא כלל קבלה משולב. אין הכרעות לפי ID, ולכן אין שיוך 16 אלה לרשומות או חישוב חפיפות בין שדות. כל הספירות הנוספות והמקור המצרפי נשמרו בדוח הניתוח. לא נערך review חדש כאן.

| Method | Auto_preservation | External_LLM_meaning_Yes | External_LLM_style_Yes | Clean_no_drift |
| --- | --- | --- | --- | --- |
| v2 | 6 | 10 | 30 | 10 |
| v3 | 9 | 5 | 27 | 5 |
| ChatGPT | 22 | 24 | 24 | 16 |

חבילת Human Validation נוצרה לכל 30 הזוגות עם חמשת השדות הריקים, ללא scores, guards, מחבר, גרסאות קודמות או review. טרם הוחזרה בדיקה אנושית: **Human Validation Pending**. לא נבחר subset של 16. כלל קבלה עתידי אפשרי: human meaning=Yes וגם stance=Yes וגם style=Yes, המוחל על כל ה־30; לא הוחל כעת.

| Author-ID setting | Accuracy | Macro-F1 |
| --- | --- | --- |
| Original | 23.33% | 0.1964 |
| Rewrite | 22.00% | 0.1867 |
| Original_fit_Rewrite_dev | 28.00% | 0.2129 |

Author-ID השתמש בכל 30 זוגות ה־train, בתשעה כותבים וב־66 מאפייני style קיימים. Logistic Regression זהה מבחינת pipeline/פרמטרים, עם fit נפרד לכל representation, שתי חלוקות stratified לכל אחד מחמישה seeds ו־scaling בתוך fold בלבד. במסלול המשני אותו fitted Original classifier נבחן על paired Rewrite. זהו development closed-set, לא test או unseen-author evaluation. הירידה הממוצעת קטנה: accuracy −1.33pp ו־Macro-F1 −0.0097; accuracy יורד רק ב־2/5 seeds, ובמסווג המקור הקבוע עולה ל־28%. **אין כרגע ראיה יציבה שה־author signal ירד.** אין להציג את הממוצע הקטן כהסרת סגנון כותב מוכחת או כהשפעה על narrative generalization.

החידוש אינו בהכרח Text Style Transfer חדש. השאלה המחקרית היא האם Narrative Classifier משתמש ב־author style כ־shortcut, והאם הפחתת author-specific style תוך שמירת narrative משפרת generalization ל־unseen authors. ChatGPT rewrite הוא intervention candidate, לא contribution בפני עצמו. לא שונו prompt/guards/thresholds/split, לא אומן Narrative Classifier ולא בוצעו LoRA או test evaluation. אומנו רק probes זמניים של Author-ID, ללא שמירת weights.

[Analysis report](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPORT_HE.md) · [Human package](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md) · [Reproduce](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPRODUCTION.md)
<!-- END_CHATGPT_REVIEW_AUTHOR_20261102 -->


## Development corpus audit and expanded Author-ID — 2026-11-08/09

New development-only audit: **429 unique excerpts / 19 authors**, but only **202 originals / 9 train authors** were used in new features, topics and models. There are **105 eligible narrative-train sources**, **96 raw validation / 4 authors** and **131 raw test / 6 authors**; test/validation content was not used. All corpus narrative labels remain machine proposals (0/429 human source labels filled). No exact hash collision across frozen splits; no lexical near-duplicate among the 202 train texts at the documented audit thresholds. A fresh semantic near-duplicate scan against test was deliberately not performed.

Author-ID on held-out original sources (5-seed grouped CV, 202 train): character TF-IDF accuracy **48.42%**, Macro-F1 **0.4318**; surface-66 **29.11% / 0.2899**. This establishes predictability in this development sample, not pure style; word-content control also predicts authors and publication years are strongly author-confounded.

For the intervention question, each classifier was fit on **172 different original sources** and then predicted the same **30 held-out Original/Rewrite pairs**: surface accuracy **46.67%→33.33%**, function/punctuation **50.00%→26.67%**, character and word controls both **53.33%→53.33%**. The smallest Holm-adjusted primary p is **0.15625**; resampling and eligible-only controls are mixed. A separately labeled post-hoc 2026-only sensitivity retains lexical cues. **Some surface cues change, but robust author-signal removal and narrative generalization are not established.** No Narrative Classifier was trained or test-evaluated.

The 30 pairs and blank Human Validation package remain unchanged. ChatGPT External LLM Review is still aggregate-only; per-ID ratings/notes and generator provenance are missing. An exact manifest of **75 additional eligible train Originals** is prepared, with no new rewrites. A main-experiment design separates fixed-model sensitivity from controlled training/unseen-author evaluation; neither main experiment was run. **19 integrity tests passed.**

[Summary](artifacts/experiments/author_style_development_audit_20261108/REPORT_HE.md) · [Corpus](artifacts/experiments/author_style_development_audit_20261108/CORPUS_AUDIT_HE.md) · [Author-ID](artifacts/experiments/author_style_development_audit_20261108/AUTHOR_ID_RESULTS_HE.md) · [Style/content](artifacts/experiments/author_style_development_audit_20261108/PAIRED_STYLE_CONTENT_HE.md) · [Next experiment plan](artifacts/experiments/author_style_development_audit_20261108/MAIN_EXPERIMENT_PLAN_HE.md) · [Reproduce/tests](artifacts/experiments/author_style_development_audit_20261108/REPRODUCTION.md)
<!-- END_DEVELOPMENT_AUTHOR_AUDIT_20261108 -->

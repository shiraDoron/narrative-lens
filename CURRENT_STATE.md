# Current Research State

Updated: 2026-11-10. This is the changing status page; [README](README.md) provides the stable research overview.

## Current research question

**Can meaning-preserving author-style interventions improve political narrative classification generalization to unseen authors?** Author-style shortcut dependence is a working hypothesis, not a finding. The candidate contribution is empirical/methodological; style rewriting is the intervention instrument, not a new TST invention. [Canonical research direction](THESIS_RESEARCH_DIRECTION_HE.md).

## What is already established

Historical experiments show a large unseen-author gap, measurable author-style signals, and no generalization recovery from the earlier normalization intervention (§28). Few-shot adaptation helped in its separate historical evaluation. See the [research storyline](EXPERIMENTS.md#research-storyline-start-here).

## What is NOT established

No causal evidence yet that removing author style improves generalization. A paraphrase gain alone cannot establish that cause. No new generalization, Macro-F1 or author-identification claim follows from the latest 30-text prompt trials. Automated passes and external LLM judgments are not human gold.

## Current active experiment

**Focused quality critique — 2026-11-10:** [Summary](artifacts/experiments/research_completion_20261110/focused_quality_64_20261110/SUMMARY_HE.md), [all64 paired case analyses](artifacts/experiments/research_completion_20261110/focused_quality_64_20261110/CASE_ANALYSIS_64_HE.md), [CSV](artifacts/experiments/research_completion_20261110/focused_quality_64_20261110/FOCUSED_QUALITY_REVIEW_64.csv). Exact previous57 unresolved +7 concern records, each reread against Original/Style, stored QC and prior AI reasoning. New analytic dispositions:7 AI-identified semantic differences,23 unresolved semantic risks,17 QC signals without identified meaning change,9 limited-style cases,3 quote-fidelity-only violations,2 style-proxy disagreements,3 prior AI reservations not supported on contextual rereading. These are mutually exclusive primary categories; secondary issues remain in case notes. All105 remain human-pending. Same-assistant ChatGPT/Codex critique is neither blind/independent-model review nor Human Validation; earlier ratings and57/7 groups are unchanged. [Label ambiguity guidance](artifacts/experiments/research_completion_20261110/focused_quality_64_20261110/LABEL_AMBIGUITY_ADDENDUM_HE.md) clarifies existing classes without changing them. Scientific training still requires105 human train labels,43 human validation labels,210 human pair-QC/adjudications and signed freeze. No rewriting, guard/threshold changes, model inference, training or Test evaluation.

**A–E runtime implemented and smoke-tested — 2026-11-10:** [Trainer/reproduction and human intake](artifacts/experiments/main_training_runtime_20261110/README_HE.md), [current readiness](artifacts/experiments/main_training_runtime_20261110/TRAINER_READINESS.json). Reuses the frozen production MiniLM/head architecture, five seeds, Adam and140 updates/2240 examples per scientific arm. Same43 gold validation Originals are wired to every arm; checkpoint remains final fixed step, not best-validation selection. Human-only snapshot approval revalidates labels, paired QC, symmetric fallback, hashes and signed freeze before model loading. No test interface.

Actual technical smoke used4 train IDs/12 unique texts with synthetic targets (not machine gold), seed42 and2 updates in each A–E. Tokenization/forward/backward/checkpoint+optimizer reload passed; logits identical after reload, head initialization equal across arms and encoder unchanged/no gradients. No validation/test inputs or Accuracy/F1 in smoke. Tokenizer-only audit of315 train variants +43 validation Originals found0 truncations at frozen256-token limit (max151).

Quality reporting combines existing AI/auto signals for all105:41 pass all available AI+automatic/style checks,57 borderline/unresolved,7 AI semantic concerns. All remain human-pending; the grouping never admits data.195 distinct tests were exercised:193 passed,2 pre-existing author-audit archive failures documented in [test report](artifacts/experiments/main_training_runtime_20261110/TEST_RESULTS_HE.md). All25 new runtime tests and59 default project tests passed; lint clean. Frozen human/source files were not changed to hide archive failures. No scientific A–E training or final test evaluation was run.

**Latest AI-review audit — 2026-11-10:** [Report](artifacts/experiments/research_completion_20261110/ai_review_audit_105_20261110/AI_AUDIT_SUMMARY_HE.md). The user-supplied ChatGPT15 review was archived unchanged; a further ChatGPT/Codex pass compared all15 and continued through the remaining90 (all105, not120). Changed6 IDs /8 fields in the first15; meaning now6 Yes /8 Borderline /1 No versus4/7/4 previously. Across105, AI meaning68/30/7, narrative97/8/0, style95/8/2 (Yes/Borderline/No). These are AI assessments, not human gold or accepted training examples. Reviewer was exposed to previous review/QC; independent different-model/blind review is not established and it must not be attributed to Claude. Human forms and research inputs remain unchanged; training is still blocked.10 new artifact-integrity tests passed; no training or test evaluation.

**Development completion audit — 2026-11-10: data available; scientific training blocked.** All105 train sources have Original, Paraphrase and Style (legacy30 + extension75). [Readiness audit](artifacts/experiments/research_completion_20261110/READINESS_HE.md) verifies exact IDs/texts, disjoint9/4/6 authors,25 configs and25 deterministic schedules. Every arm/seed has140 updates and2240 processed examples; D/E have matched source/index order. Availability flags were corrected after receipt; this is not QC acceptance.

The completed75-pair automatic screen remains: Style42 preservation /71 substantial /39 both /0 exact; matched Paraphrase43 /23 /6 /12. [QC report](artifacts/experiments/data_completion_20261109/runs/extension_v1_run01/QC_REPORT_HE.md), [failure triage and limitations](artifacts/experiments/research_completion_20261110/QC_FAILURE_ANALYSIS_HE.md). NLI is complete in both directions. Quantifier surface hints were added for review only, without changing guards or acceptance. Automated passes are not narrative/meaning gold; rhetorical intensity lacks a dedicated validated guard.

[Human handoff](artifacts/experiments/research_completion_20261110/README_HE.md) now covers105 Style pairs,105 Paraphrases,105 train proposed labels and43 validation proposed labels. Independent and QC-assisted views are separate; the assisted view is explicitly not blind. All answers remain blank; Claude stays External LLM Review. No complete attributable human import is available.

For extension75, GPT-6 /2026-11-09 is user-declared provenance; exact revision/parameters/finish_reason are unknown. Legacy30 model/prompt remain unknown and are a separate protocol cohort. Human gold/QC, adjudication/common fallback and signed provenance/protocol freeze remain blockers. The new runtime bridges A–E; historical train/evaluate functions are still not drop-in replacements because checkpoint/filtering rules differ and historical evaluate includes test. Earlier completion-stage reports predate the technical smoke above.

The [thesis direction](THESIS_RESEARCH_DIRECTION_HE.md) was edited for academic Hebrew, duplicated sections and task separation while retaining reported results and limitations. The frozen [main protocol](MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md), [deep review](RELATED_WORK_DEEP_REVIEW_HE.md), [closest-work comparison](RELATED_WORK_COMPARISON.md), [contribution](RESEARCH_GAP_AND_CONTRIBUTION_HE.md) and [Evidence Matrix](EVIDENCE_MATRIX_HE.md) remain the reference documents. Earlier [frozen sensitivity](STYLE_SENSITIVITY_PILOT_HE.md) remains1/30 flips per rewrite arm on seen training sources, not unseen-author generalization evidence.

Earlier stage reports and intake statuses remain in EXPERIMENTS.md and Git history. The218-text automatic stage's114 matched passes, v2's6/30 and the new42/75 use different denominators; none is human validation.

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

1. Obtain/import attributable human labels for105 train and43 validation Originals; proposals remain non-gold and disagreements require an explicit corpus decision.
2. Complete105 Style and105 Paraphrase human pair reviews, preserving Borderline and reviewer/date metadata. Existing valid human30 answers can be imported rather than repeated; LLM reviews cannot substitute.
3. Resolve adjudication and mixed-protocol provenance, sign the unchanged-protocol freeze, then use the implemented human-only snapshot builder. Scientific training remains a separate future action; all-attempted symmetric fallback and accepted-only secondary cohorts derive from human QC, never AI groupings or model outcomes.

The historical test is not a fresh confirmatory holdout; do not use it for prompt, guard, threshold or method decisions. [Current fail-closed readiness and reproduction](artifacts/experiments/research_completion_20261110/README_HE.md).

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

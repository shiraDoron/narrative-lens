# Text Style Transfer ושמירת משמעות — Related Work

הניווט המדעי העדכני הוא [סקירה מעמיקה של 18 עבודות](../RELATED_WORK_DEEP_REVIEW_HE.md), [ביבליוגרפיה](../REFERENCES.bib) ו[ניסוי A–E](../MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md). התיאור הטכני להלן נשמר כרקע; מנגנון TST חדש אינו התרומה המוצעת.

עודכן: 2026-11-02. קריאה במאמרים הראשוניים, כולל שיטת העבודה, המדדים, האבלציות והמגבלות. ההמלצות כאן הן הצעות לעתיד; לא הוטמע מנגנון חדש בעקבות הקריאה. [Design מוצע](semantic_style_intervention_design_he.md).

**הרחבה ומיקוד מחדש, 2026-11-09:** [סקירת 12 מאמרים, פער וחידוש אפשרי](../RESEARCH_GAP_AND_NOVELTY_HE.md) מוסיפה Style Pooling, CATO, Shortcut Maze, Counterfactual Invariance, CAD, topic confusion, WILDS ו־political framing. יש תקדימים ישירים לשינוי סגנון לצורך סיווג ולהדגמת author-style shortcuts; לכן מנגנון שכתוב חדש אינו בסיס החידוש המוצע. [מטריצת הראיות](../EVIDENCE_MATRIX_HE.md) ו[הפיילוט הקפוא](../STYLE_SENSITIVITY_PILOT_HE.md) מפרידים בין המדידה לבין טענה סיבתית ושיפור הכללה. מסמך זה נשמר כרקע טכני היסטורי.

## Thank you BART! — Lai, Toral and Nissim, ACL-IJCNLP 2021

Huiyuan Lai, Antonio Toral, and Malvina Nissim. *Thank you BART! Rewarding Pre-Trained Models Improves Formality Style Transfer*. ACL-IJCNLP 2021, pp. 484–494. [מאמר ומטא־דאטה](https://aclanthology.org/2021.acl-short.62/), [PDF](https://aclanthology.org/2021.acl-short.62.pdf), DOI: 10.18653/v1/2021.acl-short.62.

| שאלה | ממצא במאמר |
|---|---|
| משימה ותשתית | העברה בין formal/informal ב־GYAFC; fine-tuning של GPT-2/BART על זוגות מקבילים. |
| Content preservation | דמיון לניסוח יעד מקביל המשמר תוכן; המדידה אינה הוכחת שקילות לוגית. |
| Content reward | משוואה 6: `λ_bleu × [BLEU(greedy_output, reference) − BLEU(sampled_output, reference)]`. ה־reference הוא יעד `y`, ולא ה־Original `x`. |
| Style reward | משוואה 4: `λ_cls × [P(target_style | output) − P(source_style | output)]`; TextCNN קפוא. ל־GPT-2 נוסף reward על צד המקור, משוואה 5. |
| מתי משולב | policy-gradient יחד עם loss האימון, לא לולאת אימות/תיקון בזמן inference. הניסויים כוללים rewards בנפרד וביחד. |
| מדדים | style-classifier accuracy; BLEU ו־BLEURT מול ארבעה human references; harmonic mean של style accuracy ו־BLEU. |
| גבול הראיות | התועלת של BLEU reward לבדו מוגבלת; ל־pretraining תרומה גדולה לתוכן. Human evaluation מוצעת כעבודה עתידית, ולא תוצאת אימות אנושי של הפלטים. |

מקור: PDF, §2.2–3, משוואות 4–7, עמ׳ 485–487; דיון ומסקנות בעמ׳ 487–488, נספח A.1. אין כאן author-style shortcut או narrative classification.

**הסקה עבורנו:** ראוי להפריד בין מטרת הסגנון לאילוצי התוכן בדיווח ובהחלטות. ללא training אפשר לשקול scoring נפרד; זו התאמה שלנו, לא שחזור reward-based training שלהם. אין לנו reference rewrite מאומת לכל מקור, ולכן אי אפשר להעתיק את BLEU reward ישירות. ממוצע גבוה גם אינו מכפר על החלפת משתתף או שינוי ציטוט.

## A Decoupled Multi-Agent Framework — Zhang et al., Findings EMNLP 2025

Lingxi Zhang, Yu-Neng Chuang, Guanchu Wang, Ruixiang Tang, Xuanting Cai, Rajesh Shenoy, and Xia Hu. *A Decoupled Multi-Agent Framework for Complex Text Style Transfer*. Findings of EMNLP 2025, pp. 21393–21403. [מאמר ומטא־דאטה](https://aclanthology.org/2025.findings-emnlp.1166/), [PDF](https://aclanthology.org/2025.findings-emnlp.1166.pdf), DOI: 10.18653/v1/2025.findings-emnlp.1166.

| רכיב/שאלה | מה מתואר במאמר |
|---|---|
| Pipeline | דוגמאות סגנון → planner → subtask/interaction plans → experts סדרתיים → self-check/refinement. |
| Planner | תוכנית של 3–5 תתי־משימות וקשרי אינטראקציה; בניסוי נבחרות 10 דוגמאות לסגנון. |
| Experts | תפקידים נוצרים מהתוכנית; דוגמאות: core-message, structure, rephrase, vocabulary. אין רשימת מומחים קבועה לכל משימה. |
| קלט למומחה | Original ופלטי הסוכנים הקודמים, עם הוראת תת־המשימה. |
| Self-check | interaction tuples מציינים אילו דרישות של סוכן אחר לבדוק; LLM מזהה קונפליקט בפלט ביניים. |
| Refinement | בקונפליקט: interaction model מעדכן תשובה ומחזירה לסוכן. מתואר עדכון פלט, ולא חוזה minimal exact-span patches. |
| עצירה | אין קונפליקט או חמש איטרציות; §4.2. בנפרד, יצירת plan חוזרת עד פורמט תקין, ללא תקרה מפורשת ב־§4.1. |
| מודלים | GPT-3.5-turbo ל־planner ולסוכנים; בדיקת האינטראקציה היא תפקיד LLM. אין הדגמת verifier בלתי־תלוי ממשפחת מודל אחרת. |
| מבנה feedback | Plan/Interaction Plan ותיאורי אינטראקציה טקסטואליים מפוענחים; לא מתואר במאמר חוזה JSON/offsets/evidence כמו שלנו. |
| Semantics | SBERT, Self-BLEU, Ref-BLEU; ממוצע מתואר. Ref-BLEU אינו זמין ב־CDS הלא־מקביל; אופן המיצוע בלעדיו אינו מובהר בקטע המדדים. |
| Style | sentiment classifier מבוסס SBERT; formality/complex style באמצעות RoBERTa-Large; ב־CDS מסווג styled מול Wikipedia. |
| כשלים ומגבלות | התנגשויות style/content, שגיאות מצטברות בתוכנית ארוכה, תלות ביכולת המודל, עלות וזמן רקורסיה. |

מקור: PDF §4–5.1, Figures 2/4/5; §5.3 ו־7. **Training-free מתייחס למנגנון ההעברה**; מסווגי evaluation כן מאומנים. §5.1 מאפשר דוגמאות CDS מ־test ללא חפיפה להערכה; זו אינה מדיניות שנאמץ במחקר שלנו.

**הסקה עבורנו:** הפרדה ותיאום עשויים לעזור, אך אינם מתקנים בעצמם כיוון patch שגוי או verifier חלש. ריבוי תפקידים אינו עצמאות שיפוטית. אי אפשר להסיק מהמדדים שלהם ששמירת attribution, certainty, quote fidelity ועמדה פוליטית הובטחה. ב־Narrative Lens שינוי sentiment/stance הוא סיכון להתערבות, גם כאשר הוא יעד לגיטימי בבנצ׳מרק TST אחר.

## StyleRemix בהקשר הנכון

Jillian Fisher, Skyler Hallinan, Ximing Lu, Mitchell L Gordon, Zaid Harchaoui, and Yejin Choi. 2024. *StyleRemix: Interpretable Authorship Obfuscation via Distillation and Perturbation of Style Elements*. EMNLP, pp. 4172–4206. [מקור](https://aclanthology.org/2024.emnlp-main.241/), [PDF](https://aclanthology.org/2024.emnlp-main.241.pdf), DOI: 10.18653/v1/2024.emnlp-main.241.

StyleRemix מכוון ל־**authorship obfuscation**: אפיון סגנון כותב ושינוי צירים מפורשים באמצעות LoRA adapters. הכנת המתאמים כוללת אימון; שימוש במתאמים שכבר אומנו אינו מחייב אימון מחדש בכל הרצה. עבורנו זו השראה לבקרת author-specific style, ולא הוכחה ששינוי כזה משפר narrative generalization או משמר framing פוליטי.

## Related Work — השוואת מטרות

| Work | Main goal | Style mechanism | Content preservation | Training required | Author-specific? | Relevance to us |
|---|---|---|---|---|---|---|
| StyleRemix | Authorship obfuscation | צירים מפורשים + LoRA | יעד לשימור תוכן, עם הערכה | אימון adapters מקדים | כן | התערבות ניתנת לפרשנות בסגנון כותב |
| Thank you BART! | Formality transfer | fine-tuning + rewards | BLEU reward, BLEU/BLEURT | כן | לא | להפריד style/content objectives |
| Decoupled Multi-Agent | Complex style transfer | planner, experts, self-check | בדיקת קונפליקטים + מדדי תוכן | העברה ללא training; evaluators מאומנים | לא כיעד המחקר | פירוק ותיאום עם refinement מוגבל |
| Narrative Lens | בדיקת shortcut ו־unseen-author generalization | intervention סגנוני מבוקר, עדיין בפיתוח | guards, external review נפרד; Human Validation עדיין pending | לא בעבודת התיעוד הנוכחית; classifier training שייך לניסוי עתידי מאושר | כן, כשאלת מחקר | Style transfer הוא כלי ניסויי; שיפור generalization טרם הוכח |

## What we can learn for Narrative Lens

המימושים והספירות שלנו נמצאים ב[דוח ה־repair](../artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REPORT_HE.md) וב[debug subset](../artifacts/experiments/style_intervention_v2_20261026/semantic_repair_debug_subset_20261102/DEBUG_SUBSET_RESULTS.md). אלה נתוני הפרויקט, לא תוצאות המאמרים.

```text
שלב קודם: Original → Rewrite → automated guards
שני שלבים: Original → fixed v2 rewrite → semantic verifier → targeted repair → guards
Zhang et al.: style examples → planner → sequential experts ↔ self-check/refinement
```

| נקודת השוואה | לקח/התאמה אפשרית שלנו |
|---|---|
| מה חסר אצלנו | תוכנית מפורשת לצירי style ולתוכן שאסור לשנות; בדיקה מחודשת לאחר כל תיקון, עם תנאי עצירה מתועדים. |
| מה דומה | הפרדת יצירה מבדיקה ושימוש במקור ובממצאים לתיקון. זו אינה המצאה שלנו כעיקרון כללי. |
| מה עשוי לטפל בכשל | הפרדת source evidence מ־rewrite target וחוזה החלה דטרמיניסטי מטפלים בכשל הטכני; self-check עשוי לעזור בבחירת תיקון, אך המאמר לא מספק את חוזה ה־patch החסר. |
| מה לא מספיק | הגדלת מספר הסוכנים או עצם מעבר schema אינם מבטיחים גילוי drift או תיקון תקין. ה־debug שלנו הראה זאת גם לאחר שיפור ההחלה. |
| מה לא נעתיק | שינוי sentiment כיעד, דוגמאות מה־test, BLEU reference reward כשאין references, או אימון LoRA/BART כעת. |
| מסקנה | **D — שילוב מצומצם:** A כתשתית ביצוע בטוחה, B כ־self-check מוגבל, C כהפרדת ציונים בזמן inference. בלי RL ובלי העתקת ארכיטקטורה מלאה. |

**הייחוד הנבחן במחקר שלנו:** התערבות המשמרת narrative, stance וייחוס כדי לבחון תלות בסגנון כותב תחת חלוקת כותבים. לא חידוש כללי ב־TST, לא טענה שהמצאנו decomposition/self-check, ולא טענה ששיפור generalization כבר הושג. הסרת author signal, שינוי style ושיפור classifier הם שלושה דברים שיש למדוד בנפרד.

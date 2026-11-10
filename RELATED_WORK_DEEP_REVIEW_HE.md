# Related Work — סקירה מעמיקה למיקוד התזה

> Current working scope (2026-11-10): text-level Left/Right is provisional, not broad narrative classification. Author-ID predictability does not establish classifier reliance on author style or improved unseen-author generalization. See [task scope, proposed human criteria and training handoff](WORKING_TASK_AND_TRAINING_HANDOFF_HE.md). Historical results below are retained unchanged.


נבדק ב־2026-11-09. זו סקירה ממוקדת במקורות ראשוניים, לא systematic review ממצה. כל הטענות מוגבלות למערכים של המאמר הנדון. “לא נבדק” אינו טענה שאין עבודה אחרת בעולם. רלוונטיות High/Medium היא להחלטת המחקר שלנו, לא דירוג איכות מאמר.

**תיקון ביבליוגרפי חשוב:** הכותרת הרשמית של עבודת Feder et al. ב־NeurIPS 2023 היא **Data Augmentations for Improved (Large) Language Model Generalization**. CATO הוא שם השיטה; “Causal-structure Driven Augmentations for Text OOD Generalization” מופיע בכותרת גרסת טיוטה/עמוד מוסדי, ואינו הכותרת בדף הפרסום הסופי. אין לערבב את CATO(A) בייצוגים עם CATO(B) המשכתב טקסט.

רשומות ביבליוגרפיות מלאות ב־[REFERENCES.bib](REFERENCES.bib). נשמר [קטלוג מקורות מובנה](artifacts/experiments/main_training_preparation_20261109/LITERATURE_CATALOG.json), עם provenance ופרטי הקריאה. אין כאן שכפול טקסטי המאמרים או המצאת מימושים רשמיים.

הסקירה מרחיבה את [המיפוי הקודם](RESEARCH_GAP_AND_NOVELTY_HE.md), ולא מחליפה תוצאות היסטוריות. תחומים: shortcut/style (1–7,18), counterfactuals (2,8,11), authorship (4,9–10), OOD/invariance (2,7,12–14), framing/narrative (15–17).

## 1. Style Pooling: Automatic Text Style Obfuscation for Improved Classification Fairness

Fatemehsadat Mireshghallah; Taylor Berg-Kirkpatrick (2021). *Style Pooling: Automatic Text Style Obfuscation for Improved Classification Fairness*. EMNLP. [מקור רשמי](https://aclanthology.org/2021.emnlp-main.152/). **Relevance: High**. BibTeX key: `stylepool`.

- **שאלת המחקר:** האם הסתרת סגנון משפרת הוגנות downstream?.
- **שיטה:** VAE עם priors של intersection/union ו־de-boosting.
- **נתונים ופרוטוקול:** Yelp עם שגיאות כתיב סינתטיות; Blogs עם גיל ועיסוק.
- **סוג התערבות:** שכתוב להסרת/ערבוב מאפייני סגנון.
- **הערכה ומיקום במאמר:** occupation accuracy, TPR gap, attribute removal, fluency ושימור תוכן; §3–4.
- **תוצאות מרכזיות:** Intersection מאפשר trade-off utility/fairness; Union לא משפר את אותה בדיקת הוגנות.
- **מגבלות:** שימור תוכן והסתרת מאפיין אינם מובטחים בכל דוגמה; לא זהות מחבר מלאה.
- **דמיון/שוני אלינו:** תקדים קרוב לשינוי style לטובת מסווג; זו אינה המצאה שלנו.
- **מה לא הודגם במאמר:** לא אותו ניסוי נרטיב פוליטי, human framing gold והכללה לכותבי דעה חדשים.

[מימוש/משאב מחברים](https://github.com/mireshghallah/style-pooling).

## 2. Data Augmentations for Improved (Large) Language Model Generalization

Amir Feder; Yoav Wald; Claudia Shi; Suchi Saria; David M. Blei (2023). *Data Augmentations for Improved (Large) Language Model Generalization*. NeurIPS 36. [מקור רשמי](https://proceedings.neurips.cc/paper_files/paper/2023/hash/df88b275bef31ac96c85f0c4013734fc-Abstract-Conference.html). **Relevance: High**. BibTeX key: `cato`.

- **שאלת המחקר:** האם augmentation מבוסס מבנה סיבתי משפר OOD תחת מתאם מאפיין–תווית?.
- **שיטה:** CATO(A): diff-in-diff על ייצוגי notes; CATO(B): prompting עם דוגמאות מותאמות במידע עזר.
- **נתונים ופרוטוקול:** MIMIC-III מול i2b2/partner data; CeBAB/CeBAB-Spurious; סימולציה.
- **סוג התערבות:** counterfactual caregiver או food-mention; A בייצוגים ובנספח prompts, B בטקסט.
- **הערכה ומיקום במאמר:** clinical F1 ממוצע חמש ריצות; OOD accuracy בביקורות; ERM, reweighting, MMD, IRM, GroupDRO ו־augmentation baselines (§4–5, Table1).
- **תוצאות מרכזיות:** שיפור OOD במערכים שנבדקו; Clinical A משתמש בעיקר ב־representations ולא רק בשכתוב טקסט חופשי.
- **מגבלות:** נדרשים no-unmeasured-confounding/positivity וב־A הנחת constant-effect; OOD בית חולים אינו author-disjoint trial שלנו.
- **דמיון/שוני אלינו:** התקדים הקרוב לרציונל caregiver style; אין להעתיק ערבויות ללא הנחות.
- **מה לא הודגם במאמר:** לא הוכחה לשימור framing פוליטי או ליתרון על בקרת פרפרזה זהה לשלנו.

לא אומת repo מימוש רשמי בקריאה זו; אין בכך הוכחה שאינו קיים. יש להשתמש במאמר, לא לייחס לו מימוש מקומי.

הכרעה מול התיאור הישן: §4.2 ו־§5.1/Algorithm1 מפרידים בין matched patient progress/discharge notes, diff-in-diff בייצוגים ו־prompting. OOD נבדק בין מקורות רפואיים, לא באותו פרוטוקול כותבים ותוויות פוליטיות. אין לתאר כל ניסויי CATO כ־free-text style rewrite.

## 3. Navigating the Shortcut Maze: A Comprehensive Analysis of Shortcut Learning in Text Classification by Language Models

Yuqing Zhou; Ruixiang Tang; Ziyu Yao; Ziwei Zhu (2024). *Navigating the Shortcut Maze: A Comprehensive Analysis of Shortcut Learning in Text Classification by Language Models*. Findings of EMNLP. [מקור רשמי](https://aclanthology.org/2024.findings-emnlp.146/). **Relevance: High**. BibTeX key: `shortcutmaze`.

- **שאלת המחקר:** האם LMs רגישים ל־occurrence/style/concept shortcuts מורכבים?.
- **שיטה:** Llama2-70B יוצר formal/casual ו־Shakespeare/Hemingway; הזרקת מתאם label–style ובדיקת anti-test.
- **נתונים ופרוטוקול:** Yelp, GoEmotions מותאם, Beer palate.
- **סוג התערבות:** שינוי register/סגנון מחבר, עוצמת מתאם מבוקרת.
- **הערכה ומיקום במאמר:** BERT בחמש ריצות ו־LLMs; accuracy/Macro-F1 ב־normal/anti-test (§2–3).
- **תוצאות מרכזיות:** ירידות תחת anti-test גם ב־author writing style; LLMs אינם חסינים.
- **מגבלות:** מתאם וסגנונות מלאכותיים; איכות label-preservation אינה זהה ל־gold framing פוליטי.
- **דמיון/שוני אלינו:** עצם הוכחת author-style shortcut בטקסט כבר נעשתה.
- **מה לא הודגם במאמר:** לא ברור אם אותה תלות מתקיימת במתאמים טבעיים בין כותבי דעה ונרטיב.

[מימוש/משאב מחברים](https://github.com/yuqing-zhou/shortcut-learning-in-text-classification).

## 4. StyleRemix: Interpretable Authorship Obfuscation via Distillation and Perturbation of Style Elements

Jillian Fisher; Skyler Hallinan; Ximing Lu; Mitchell L. Gordon; Zaid Harchaoui; Yejin Choi (2024). *StyleRemix: Interpretable Authorship Obfuscation via Distillation and Perturbation of Style Elements*. EMNLP. [מקור רשמי](https://aclanthology.org/2024.emnlp-main.241/). **Relevance: High**. BibTeX key: `styleremix`.

- **שאלת המחקר:** כיצד לשנות מאפייני מחבר בצורה נשלטת?.
- **שיטה:** פרופיל מחבר ו־LoRA adapters לצירי style.
- **נתונים ופרוטוקול:** AuthorMix: כ־30K טקסטים, 14 כותבים/4 domains; DiSC: שבעה צירים/16 כיוונים.
- **סוג התערבות:** שינוי צירים הרחק מחתימת מחבר, בנפרד או בהרכבה.
- **הערכה ומיקום במאמר:** authorship obfuscation, איכות אוטומטית והערכה אנושית.
- **תוצאות מרכזיות:** יתרון על baselines ו־LLMs גדולים במערכי המאמר.
- **מגבלות:** טקסטים ארוכים; הצלחת attack אינה תועלת למשימת narrative.
- **דמיון/שוני אלינו:** generator אפשרי; אינו contribution של התזה שלנו.
- **מה לא הודגם במאמר:** לא unseen-author political narrative benefit עם אותם ציטוטים/stance כ־gold.

[מימוש/משאב מחברים](https://github.com/jfisher52/StyleRemix).

## 5. Thank you BART! Rewarding Pre-Trained Models Improves Formality Style Transfer

Huiyuan Lai; Antonio Toral; Malvina Nissim (2021). *Thank you BART! Rewarding Pre-Trained Models Improves Formality Style Transfer*. ACL-IJCNLP Short Papers. [מקור רשמי](https://aclanthology.org/2021.acl-short.62/). **Relevance: Medium**. BibTeX key: `bart`.

- **שאלת המחקר:** האם pretraining ו־rewards עוזרים לשינוי formality ושימור תוכן?.
- **שיטה:** fine-tuning של GPT-2/BART עם style-classifier reward ו־BLEU reward.
- **נתונים ופרוטוקול:** GYAFC: Entertainment/Music ו־Family/Relationships; זוגות מקבילים וארבעה references ב־valid/test.
- **סוג התערבות:** informal↔formal; גם ablations לפי כמות נתוני אימון.
- **הערכה ומיקום במאמר:** classifier style accuracy, BLEU, BLEURT ו־harmonic mean (§2–3).
- **תוצאות מרכזיות:** pretraining משפר תוכן, ושילוב rewards משיג שיפור; גם 10% parallel data מועילים.
- **מגבלות:** BLEU reward משווה ל־target reference y, לא למקור x; אין תוצאת Human Validation של הפלטים.
- **דמיון/שוני אלינו:** מלמד להפריד style/content; לא מנגנון תיקון מקומי או author obfuscation.
- **מה לא הודגם במאמר:** לא downstream narrative generalization ולא fidelity לכל certainty/quote.

[מימוש/משאב מחברים](https://github.com/laihuiyuan/pre-trained-formality-transfer).

## 6. A Decoupled Multi-Agent Framework for Complex Text Style Transfer

Lingxi Zhang; Yu-Neng Chuang; Guanchu Wang; Ruixiang Tang; Xuanting Cai; Rajesh Shenoy; Xia Hu (2025). *A Decoupled Multi-Agent Framework for Complex Text Style Transfer*. Findings of EMNLP. [מקור רשמי](https://aclanthology.org/2025.findings-emnlp.1166/). **Relevance: Medium**. BibTeX key: `multiagent`.

- **שאלת המחקר:** האם פירוק מורכבות style/content ושיתוף מומחים עוזרים ל־TST?.
- **שיטה:** planner, expert agents ו־self-check/refinement; GPT-3.5-turbo; עד חמש איטרציות (§4–5).
- **נתונים ופרוטוקול:** Yelp, GYAFC, Shakespeare ו־CDS.
- **סוג התערבות:** training-free style transfer עם תוכנית ואינטראקציות.
- **הערכה ומיקום במאמר:** style classifiers; SBERT/Self-BLEU/Ref-BLEU לפי זמינות; ablations.
- **תוצאות מרכזיות:** המאמר מדווח CDS style +2.8% ו־content +4.4% ביחס לבסיס המושווה שם.
- **מגבלות:** self-check אינו סוקר בלתי תלוי; dependencies/עלות; דוגמאות CDS עשויות להגיע מ־test ללא חפיפת evaluation.
- **דמיון/שוני אלינו:** השראה ארכיטקטונית קיימת, לא חידוש ולא פרוטוקול QC שלנו.
- **מה לא הודגם במאמר:** לא הבטחת framing/attribution/quotes פוליטיים או downstream unseen authors.

לא אומת repo מימוש רשמי בקריאה זו; אין בכך הוכחה שאינו קיים. יש להשתמש במאמר, לא לייחס לו מימוש מקומי.

## 7. Counterfactual Invariance to Spurious Correlations in Text Classification

Victor Veitch; Alexander D'Amour; Steve Yadlowsky; Jacob Eisenstein (2021). *Counterfactual Invariance to Spurious Correlations in Text Classification*. NeurIPS 34. [מקור רשמי](https://papers.neurips.cc/paper_files/paper/2021/hash/8710ef761bbb29a6f9d12e4ef8e4379c-Abstract.html). **Relevance: High**. BibTeX key: `veitch`.

- **שאלת המחקר:** מתי stress-test invariance מקנה robustness?.
- **שיטה:** פורמליזציה סיבתית, מבנים causal/anti-causal ו־regularization שונה עבורם.
- **נתונים ופרוטוקול:** ניתוח פורמלי וניסויי text classification.
- **סוג התערבות:** התערבות במאפיין לא רלוונטי/אילוצי invariance.
- **הערכה ומיקום במאמר:** ערבויות מותנות מבנה ו־stress testing; מאמר §2–4.
- **תוצאות מרכזיות:** הקשר בין invariance להכללה תלוי במבנה הסיבתי.
- **מגבלות:** label-invariance אינה מובנת מאליה כשמשנים framing.
- **דמיון/שוני אלינו:** מצדיק הפרדה בין flip לבין causal style effect.
- **מה לא הודגם במאמר:** לא מזהה את המנגנון במודל המקומי ללא הנחות והתערבות תקפה.

לא אומת repo מימוש רשמי בקריאה זו; אין בכך הוכחה שאינו קיים. יש להשתמש במאמר, לא לייחס לו מימוש מקומי.

## 8. Learning the Difference that Makes a Difference with Counterfactually-Augmented Data

Divyansh Kaushik; Eduard Hovy; Zachary C. Lipton (2020). *Learning the Difference that Makes a Difference with Counterfactually-Augmented Data*. ICLR. [מקור רשמי](https://openreview.net/forum?id=Sklgs0NFvr). **Relevance: High**. BibTeX key: `cad`.

- **שאלת המחקר:** האם עריכות נגד־עובדתיות מפחיתות דפוסים לא רצויים?.
- **שיטה:** אדם עורך מינימלית לשינוי תווית; אימון מקור/ערוך/משולב.
- **נתונים ופרוטוקול:** IMDb sentiment ו־SNLI.
- **סוג התערבות:** label-changing edits, לא label-preserving author style.
- **הערכה ומיקום במאמר:** בדיקה על Original ו־counterfactuals והשפעת feature shortcuts.
- **תוצאות מרכזיות:** שילוב משפר העברה בין התנאים ומפחית אותות לא רלוונטיים.
- **מגבלות:** עלות annotation; עריכה עשויה להכניס artifacts.
- **דמיון/שוני אלינו:** augmentation סיבתי כבר קיים; אצלנו נשמרת התווית.
- **מה לא הודגם במאמר:** לא אותה הערכת framing והכללה למחברים.

[מימוש/משאב מחברים](https://github.com/dkaushik96/counterfactually-augmented-data).

## 9. The Topic Confusion Task: A Novel Evaluation Scenario for Authorship Attribution

Malik H. Altakrori; Jackie Chi Kit Cheung; Benjamin C. M. Fung (2021). *The Topic Confusion Task: A Novel Evaluation Scenario for Authorship Attribution*. Findings of EMNLP. [מקור רשמי](https://aclanthology.org/2021.findings-emnlp.359/). **Relevance: High**. BibTeX key: `topicconfusion`.

- **שאלת המחקר:** איך להבדיל זיהוי נושא מזיהוי כותב?.
- **שיטה:** החלפת author–topic mapping בין train/test והשוואת features.
- **נתונים ופרוטוקול:** Guardian מנוקה ומאוזן עם כמה נושאים למחבר.
- **סוג התערבות:** topic assignment shift, לא שכתוב.
- **הערכה ומיקום במאמר:** attribution accuracy וסיווג טעויות topic/style; stylometry/POS/ngrams/BERT.
- **תוצאות מרכזיות:** stylometry/POS פחות רגישים לנושא; שילובים עוזרים.
- **מגבלות:** closed-set AA אינה generalization נרטיב לכותבים חדשים.
- **דמיון/שוני אלינו:** מחייב בקרות topic/time בפירוש ה־Author-ID שלנו.
- **מה לא הודגם במאמר:** לא שיפור narrative לאחר intervention.

לא אומת repo מימוש רשמי בקריאה זו; אין בכך הוכחה שאינו קיים. יש להשתמש במאמר, לא לייחס לו מימוש מקומי.

## 10. Authorship Attribution Using Text Distortion

Efstathios Stamatatos (2017). *Authorship Attribution Using Text Distortion*. EACL. [מקור רשמי](https://aclanthology.org/E17-1107/). **Relevance: Medium**. BibTeX key: `distortion`.

- **שאלת המחקר:** איך למדוד סגנון בלי topic-specific words?.
- **שיטה:** distortion/masking לפני חילוץ char-level stylometry.
- **נתונים ופרוטוקול:** CCAT-10 ו־Guardian ל־closed-set AA; עשרה PAN14/PAN15 verification corpora.
- **סוג התערבות:** הסתרת מידע תוכני במקום הסתרת מחבר.
- **הערכה ומיקום במאמר:** attribution/verification metrics והשוואת preprocessing (§3–5).
- **תוצאות מרכזיות:** שיפור attribution במיוחד ב־cross-topic.
- **מגבלות:** אי אפשר להשתמש בטקסט המעוות כתחליף meaning-preserving political rewrite.
- **דמיון/שוני אלינו:** בקרת תוכן חשובה; המטרה הפוכה משלנו.
- **מה לא הודגם במאמר:** לא תועלת downstream לסיווג נרטיב.

לא אומת repo מימוש רשמי בקריאה זו; אין בכך הוכחה שאינו קיים. יש להשתמש במאמר, לא לייחס לו מימוש מקומי.

## 11. Adversarial Example Generation with Syntactically Controlled Paraphrase Networks

Mohit Iyyer; John Wieting; Kevin Gimpel; Luke Zettlemoyer (2018). *Adversarial Example Generation with Syntactically Controlled Paraphrase Networks*. NAACL-HLT. [מקור רשמי](https://aclanthology.org/N18-1170/). **Relevance: High**. BibTeX key: `scpn`.

- **שאלת המחקר:** האם פרפרזה מבוקרת תחביר מייצרת adversarial examples ומשפרת robustness?.
- **שיטה:** backtranslation רחב, parse templates ו־encoder-decoder מותנה תחביר.
- **נתונים ופרוטוקול:** ParaNMT-50M לאימון פרפרזה; SST sentiment ו־SICK entailment downstream.
- **סוג התערבות:** controlled syntax מול uncontrolled paraphrases.
- **הערכה ומיקום במאמר:** אוטומטי ואנושי; syntax adherence, paraphrase quality, fooling ו־augmentation (§3–5).
- **תוצאות מרכזיות:** פרפרזות מבוקרות שומרות איכות, מטעות מודלים ומסייעות robustness לשינוי תחבירי.
- **מגבלות:** paraphrase quality אינה ערבות לכל טענה; לא סגנון כותב אמיתי.
- **דמיון/שוני אלינו:** תקדים להשוואת controlled linguistic intervention מול פרפרזה כללית.
- **מה לא הודגם במאמר:** לא author-disjoint political narrative generalization.

[מימוש/משאב מחברים](https://github.com/miyyer/scpn).

## 12. WILDS: A Benchmark of in-the-Wild Distribution Shifts

Pang Wei Koh; Shiori Sagawa; Henrik Marklund; Sang Michael Xie; Marvin Zhang; Akshay Balsubramani; Weihua Hu; Michihiro Yasunaga; Richard Lanas Phillips; Irena Gao; Tony Lee; Etienne David; Ian Stavness; Wei Guo; Berton A. Earnshaw; Imran S. Haque; Sara M. Beery; Jure Leskovec; Anshul Kundaje; Emma Pierson; Sergey Levine; Chelsea Finn; Percy Liang (2021). *WILDS: A Benchmark of in-the-Wild Distribution Shifts*. ICML, PMLR 139. [מקור רשמי](https://proceedings.mlr.press/v139/koh21a.html). **Relevance: High**. BibTeX key: `wilds`.

- **שאלת המחקר:** איך להעריך shift מציאותי?.
- **שיטה:** benchmarks ופרוטוקולי domain/group evaluation.
- **נתונים ופרוטוקול:** עשרה datasets; Amazon reviews עם user-disjoint train/test.
- **סוג התערבות:** אין שכתוב סגנוני מובנה.
- **הערכה ומיקום במאמר:** ID/OOD וקבוצות; Amazon מדווח 10th-percentile user accuracy.
- **תוצאות מרכזיות:** פערי OOD גם בשיטות robustness; author-disjoint אינו רעיון חדש.
- **מגבלות:** תחומים ותוויות שונים; שונות קושי בין users עשויה להסביר חלק מהפער.
- **דמיון/שוני אלינו:** מודל לפרוטוקול כותבים נפרדים ומדדי per-author.
- **מה לא הודגם במאמר:** לא אותו narrative-preserving augmentation.

[מימוש/משאב מחברים](https://github.com/p-lambda/wilds).

## 13. Invariant Risk Minimization

Martin Arjovsky; Leon Bottou; Ishaan Gulrajani; David Lopez-Paz (2019). *Invariant Risk Minimization*. arXiv preprint; v3 March 2020. [מקור רשמי](https://arxiv.org/abs/1907.02893). **Relevance: Medium**. BibTeX key: `irm`.

- **שאלת המחקר:** איך ללמוד predictor יציב בין environments?.
- **שיטה:** representation עם אותו classifier אופטימלי בכל environment; IRMv1 surrogate.
- **נתונים ופרוטוקול:** ניתוח פורמלי, ניסויים סינתטיים ו־Colored MNIST.
- **סוג התערבות:** regularization בין סביבות, לא rewrite.
- **הערכה ומיקום במאמר:** סיכון בסביבות משתנות והנחות זיהוי.
- **תוצאות מרכזיות:** הדגמת תועלת בתנאי המאמר; אין guarantee לכל shift.
- **מגבלות:** איכות environments והנחות; לא תוצאת political NLP בפני עצמה.
- **דמיון/שוני אלינו:** author groups הם environment מועמד, לא מספיקים לזיהוי סיבתיות.
- **מה לא הודגם במאמר:** לא הוכחה ל־meaning-preserving author augmentation.

[מימוש/משאב מחברים](https://github.com/facebookresearch/InvariantRiskMinimization).

## 14. Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization

Shiori Sagawa; Pang Wei Koh; Tatsunori B. Hashimoto; Percy Liang (2020). *Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization*. ICLR. [מקור רשמי](https://openreview.net/forum?id=ryxGuJrFvS). **Relevance: Medium**. BibTeX key: `groupdro`.

- **שאלת המחקר:** מתי minimax group training משפר קבוצות חלשות?.
- **שיטה:** Group-DRO עם regularization/early stopping.
- **נתונים ופרוטוקול:** MultiNLI, Waterbirds ו־CelebA.
- **סוג התערבות:** משקלי קבוצות loss, לא שכתוב.
- **הערכה ומיקום במאמר:** worst-group לצד average accuracy.
- **תוצאות מרכזיות:** regularization חיוני; שיפורים ב־worst-group בתנאי המאמר.
- **מגבלות:** דורש קבוצות נאותות; אימון minimax לבדו אינו מבטיח generalization.
- **דמיון/שוני אלינו:** הכישלון המקומי אינו סתירה למאמר או הוכחה נגד כל robustness.
- **מה לא הודגם במאמר:** לא מחליף ניסוי התערבות ושימור נרטיב.

[מימוש/משאב מחברים](https://github.com/kohpangwei/group_DRO).

## 15. The Media Frames Corpus: Annotations of Frames Across Issues

Dallas Card; Amber E. Boydstun; Justin H. Gross; Philip Resnik; Noah A. Smith (2015). *The Media Frames Corpus: Annotations of Frames Across Issues*. ACL-IJCNLP. [מקור רשמי](https://aclanthology.org/P15-2072/). **Relevance: High**. BibTeX key: `frames`.

- **שאלת המחקר:** כיצד לתייג frames מעבר לנושא אחד?.
- **שיטה:** 15 framing dimensions, spans ו־primary frames; כמה שלבי annotation.
- **נתונים ופרוטוקול:** כתבות הגירה/עישון/נישואים חד־מיניים.
- **סוג התערבות:** אין rewrite intervention.
- **הערכה ומיקום במאמר:** annotation coverage והסכמה בין מסמנים.
- **תוצאות מרכזיות:** משאב והדגמת operationalization של framing.
- **מגבלות:** לא כל הערכות מסכימות; קטגוריות אינן זהות Left/Right.
- **דמיון/שוני אלינו:** נדרש text-level codebook, לא account labels בלבד.
- **מה לא הודגם במאמר:** לא אותה בדיקת style invariance.

[מימוש/משאב מחברים](https://github.com/dallascard/media_frames_corpus).

## 16. Media Framing: A Typology and Survey of Computational Approaches Across Disciplines

Yulia Otmakhova; Shima Khanehzar; Lea Frermann (2024). *Media Framing: A Typology and Survey of Computational Approaches Across Disciplines*. ACL. [מקור רשמי](https://aclanthology.org/2024.acl-long.822/). **Relevance: High**. BibTeX key: `framingreview`.

- **שאלת המחקר:** מה כוללת framing analysis מעבר לנושא?.
- **שיטה:** סקירה בין־תחומית והבחנה semantics/cognition/communication.
- **נתונים ופרוטוקול:** מאגר מחקרים ו־frame definitions.
- **סוג התערבות:** סקירה, ללא augmentation experiment.
- **הערכה ומיקום במאמר:** מיפוי הגדרות ומתודולוגיות, לא ציון מודל אחד.
- **תוצאות מרכזיות:** typology והצבעה על ערבוב topic/framing במחקר.
- **מגבלות:** אין benchmark אחד או הוכחה למנגנון מסוים.
- **דמיון/שוני אלינו:** certainty/intensity יכולים להיות חלק מהתווית ולא nuisance.
- **מה לא הודגם במאמר:** לא מאמת את ה־labels המקומיים.

[מימוש/משאב מחברים](https://github.com/julia-nixie/awesome-media-framing).

## 17. SemEval 2025 Task 10: Multilingual Characterization and Extraction of Narratives from Online News

Jakub Piskorski; Tarek Mahmoud; Nikolaos Nikolaidis; Ricardo Campos; Alipio Mario Jorge; Dimitar Dimitrov; Purificacao Silvano; Roman Yangarber; Shivam Sharma; Tanmoy Chakraborty; Nuno Guimaraes; Elisa Sartori; Nicolas Stefanovitch; Zhuohan Xie; Preslav Nakov; Giovanni Da San Martino (2025). *SemEval 2025 Task 10: Multilingual Characterization and Extraction of Narratives from Online News*. SemEval. [מקור רשמי](https://aclanthology.org/2025.semeval-1.331/). **Relevance: High**. BibTeX key: `semeval`.

- **שאלת המחקר:** כיצד לאפיין narratives ו־entity roles בחדשות?.
- **שיטה:** שלוש משימות: framing, classification ו־extraction.
- **נתונים ופרוטוקול:** אקלים ומלחמת רוסיה–אוקראינה, חמש שפות, טקסונומיה היררכית.
- **סוג התערבות:** מערכות משתתפים; אין style intervention יחיד של מארגני המשימה.
- **הערכה ומיקום במאמר:** train/dev/test רשמיים ומדדים לפי subtask/language.
- **תוצאות מרכזיות:** 66 צוותים הגישו תוצאות בכלל המשימות; classification פוליטי אינו חדש.
- **מגבלות:** הטקסונומיה אינה 7 תוויות הפרויקט ואינה Left/Right בלבד.
- **דמיון/שוני אלינו:** רקע להגדרת יעד עשיר ולהפרדת roles מ־stance.
- **מה לא הודגם במאמר:** לא ניסוי זהה של author-disjoint A–E.

לא אומת repo מימוש רשמי בקריאה זו; אין בכך הוכחה שאינו קיים. יש להשתמש במאמר, לא לייחס לו מימוש מקומי.

## 18. Shortcut learning in deep neural networks

Robert Geirhos; Jorn-Henrik Jacobsen; Claudio Michaelis; Richard Zemel; Wieland Brendel; Matthias Bethge; Felix A. Wichmann (2020). *Shortcut learning in deep neural networks*. Nature Machine Intelligence 2:665–673. [מקור רשמי](https://doi.org/10.1038/s42256-020-00257-z). **Relevance: Medium**. BibTeX key: `geirhos`.

- **שאלת המחקר:** מדוע הצלחת IID אינה מספיקה?.
- **שיטה:** Perspective המאחד כשלים כ־decision-rule shortcuts.
- **נתונים ופרוטוקול:** סינתזה ודוגמאות/ניסוי צעצוע.
- **סוג התערבות:** stress-test והמלצות benchmarking.
- **הערכה ומיקום במאמר:** ניתוח מושגי, לא dataset פוליטי חדש.
- **תוצאות מרכזיות:** מסגרת להבנת failures תחת shift.
- **מגבלות:** לא מזהה איזה shortcut פועל בכל מערכת.
- **דמיון/שוני אלינו:** מניע למחקר, לא ראיה מקומית לסגנון.
- **מה לא הודגם במאמר:** לא intervention outcome בנרטיב פוליטי.

[מימוש/משאב מחברים](https://github.com/rgeirhos/shortcut-perspective).

## סינתזה והשלכות לניסוי שלנו

התקדימים הקרובים הם CATO, Style Pooling ו־Shortcut Maze: כבר קיימים רציונל התערבות במאפייני מחבר, downstream improvement בתנאים מסוימים ו־style shortcuts מלאכותיים. SCPN כבר משווה controlled paraphrase לפרפרזה לא מבוקרת. WILDS כבר משתמש בכותבים נפרדים. החידוש המועמד הוא הערכה מקומית טבעית של התערבות **המשמרת מסגור פוליטי**, עם ניתוח shared-ID A–E והבחנה בין שיפור ביצועים להסבר המנגנון.

לא אותר בקריאה זו צירוף זהה של כל אלה עם כותבי דעה טבעיים, אך אין לטעון ראשוניות לפני citation chaining רחב יותר. מעבר תחום הוא וריאציה אמפירית, ונהלי QC הם תרומה מתודולוגית אפשרית אם הושלמו והוערכו, לא מעצם כתיבתם.

[מטריצת השוואה](RELATED_WORK_COMPARISON.md) · [תרומה מדורגת](RESEARCH_GAP_AND_CONTRIBUTION_HE.md) · [פרוטוקול A–E](MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md)

# Related Work

Scope: verifiable literature relevant to this repo's measured findings in
`EXPERIMENTS.md` §18-§28 (the unseen-author generalization arc) and the
topic-representation comparisons in §15/§17/§20. Every entry below was
verified by lookup (authors, venue, year checkable via the ACL Anthology,
JMLR, or arXiv record cited). Anything not so verified would carry a
`[VERIFY]` tag; no entry here needs one.

## 1. Narrative and framing classification

1. Card, Boydstun, Gross, Resnik, and Smith (2015), "The Media Frames Corpus:
   Annotations of Frames Across Issues", ACL-IJCNLP 2015.
   Relevance: the standard frame-annotated news corpus this repo's 7-way
   narrative labels parallel at a coarser, outlet-provenance level; its
   cross-issue framing setup anticipates our §18 LOAO finding that a
   classifier trained on one set of authors fails on a held-out one.
2. Piskorski et al. (2023), "SemEval-2023 Task 3: Detecting the Category, the
   Framing, and the Persuasion Techniques in Online News in a Multilingual
   Setup", SemEval-2023 (ACL 2023 workshop).
   Relevance: the current benchmark for multilingual news framing detection;
   its genre-vs-framing split mirrors our `docs/narrative_definitions.md`
   distinction between institutional voice (Western) and partisan argument
   (Right-wing/Left-wing), which §26-§27 show classifiers blur.
3. Mendelsohn, Budak, and Jurgens (2021), "Modeling Framing in Immigration
   Discourse on Social Media", NAACL 2021.
   Relevance: supervised frame detection on tweets with asymmetric
   performance across ideological groups, the same asymmetry our §18 LOAO
   test finds (2 of 3 held-out authors systematically misrouted to
   `Right-wing`).
4. Demszky, Garg, Voigt, et al. (2019), "Analyzing Polarization in Social
   Media: Method and Application to Tweets on 21 Mass Shootings", NAACL 2019.
   Relevance: shows partisans frame the same events with different topics and
   lexical choices, which is the mechanism behind our §27 result that author
   identity is recoverable even within one fixed narrative.

Connection to repo: §15/§17 compare hard topic id vs. soft distribution as
features for narrative classification; the framing literature above treats
topic choice itself as part of the frame, which explains why our topic arm
helps in-distribution yet hurts or stalls on unseen authors (§19, §20 LOAO:
hard topic recall 52.0% vs. SBERT-only 59.2%).

## 2. Cross-author and domain generalization in text classification

5. Ganin et al. (2016), "Domain-Adversarial Training of Neural Networks",
   Journal of Machine Learning Research, vol. 17 (arXiv 2015).
   Relevance: the canonical method for learning domain-invariant
   representations; directly applicable to our §18-§28 arc, where author
   identity acts as the unobserved domain and no tested intervention
   (§23-§25 masking, §28 style normalization) learned invariance.
6. Sap, Card, Gabriel, Choi, and Smith (2019), "The Risk of Racial Bias in
   Hate Speech Detection", ACL 2019.
   Relevance: demonstrates that dialect-correlated training signal produces
   systematic misrouting of unseen varieties, the closest published analogue
   of our §18 finding (held-out authors misrouted to `Right-wing`) and of
   the §20 LOAO Right-wing bias gap (hard 20.8% vs. soft 16.7%).
7. Hovy, Johannsen and Sogaard (2015), "User Review Sites as a Resource for
   Large-Scale Sociolinguistic Studies", WWW 2015.
   Relevance: early evidence that NLP performance varies with author
   demographics even when the task is ostensibly author-independent; the
   precedent for our §27 author-signature diagnostics (e.g. `Western` 85.1%
   author-identification accuracy vs. ~20% baseline within one narrative).

Connection to repo: ��27 confirms the author-as-domain problem exists in our
corpus (all 7 narratives beat author baselines with narrative held constant);
§28 shows our attempted fix (style normalization) reduced the measurable
signature (about -15pp macro-F1) without improving LOAO recall (worse for
13/14 fresh authors), a negative result consistent with this literature's
lesson that surface-feature removal rarely yields domain invariance on its
own. Diverge note: unlike Ganin-style adversarial training, we never trained
an explicitly domain-invariant representation, so §28 does not test that
family of methods.

## 3. Entity and style shortcuts, de-biasing

8. McCoy, Pavlick, and Linzen (2019), "Right for the Wrong Reasons:
   Diagnosing Syntactic Heuristics in Natural Language Inference", ACL 2019
   (HANS dataset).
   Relevance: the template for our §21 entity-shortcut test: high
   in-distribution accuracy that collapses under a targeted evaluation
   probing reliance on a spurious heuristic rather than the intended signal.
9. Gururangan et al. (2018), "Annotation Artifacts in Natural Language
   Inference Data", NAACL 2018.
   Relevance: shows hypothesis-only baselines beat chance because of
   annotator artifacts; parallels our §27 finding that shallow style/entity
   features recover author identity, meaning our narrative labels partly
   encode provenance (who wrote it) rather than pure content.
10. Clark, Yatskar, and Zettlemoyer (2019), "Don't Take the Easy Way Out:
    Ensemble Based Methods for Avoiding Known Dataset Biases", EMNLP-IJCNLP
    2019.
    Relevance: bias-product ensembles that down-weight examples solvable by a
    bias-only model; a concrete untested alternative to our §23-§24 masking
    augmentations, which helped one author (Bernie) but hurt two others and
    failed confirmation in §25 (`NON-INFERIOR = FALSE`).
11. Elazar and Goldberg (2018), "Adversarial Removal of Demographic Attributes
    from Text Data", EMNLP 2018.
    Relevance: shows demographic/author attributes persist in hidden
    representations even after adversarial removal is applied; predicts our
    §28 outcome, where normalizing observable style features left the
    generalization gap intact (fresh-author recall mean -6.4pp).

Connection to repo: §21-§22 diagnose the entity shortcut (masking entity
identity changes predictions, inconsistently across authors); §23-§25 test
masking as an intervention and it does not generalize. This bucket explains
why: shortcuts are typically overdetermined (entities plus style plus topic),
so removing one leg, as we did, is expected to give mixed author-dependent
results rather than a clean fix.

## 4. Topic modeling for ideology: BERTopic vs. LDA

12. Grootendorst (2022), "BERTopic: Neural Topic Modeling with a Class-based
    TF-IDF Procedure", arXiv 2022 (arXiv:2203.05794).
    Relevance: the method behind our `saved_topic_model_soft_v2` pipeline;
    our §9/§20 measurements (about 42-49% of docs get an all-zero soft
    distribution; mean 1.39 nonzero entries where signal exists) document a
    concrete sparsity property of `approximate_distribution()` that conditions
    every downstream result.
13. Blei, Ng, and Jordan (2003), "Latent Dirichlet Allocation", Journal of
    Machine Learning Research, vol. 3.
    Relevance: the dense-distribution baseline (K=50, every doc sums to 1.0,
    no outlier concept) against which our §15/§20 LDA arm is built; its
    density is exactly why LDA narrows but does not close the LOAO gap in
    §20 (recall 57.8% vs. soft 59.0% vs. hard 52.0%).
14. Egger and Yu (2022), "A Topic Modeling Comparison Between LDA, NMF,
    Top2Vec, and BERTopic to Demystify Twitter Posts", Frontiers in Sociology
    2022.
    Relevance: head-to-head evidence that BERTopic outperforms LDA-family
    models on short social media text; consistent with our §15 random-split
    ranking (Hard > Soft > LDA > None) while our §20 LOAO reversal (soft/LDA
    beating hard on unseen authors) adds the generalization dimension their
    comparison does not evaluate.
15. Angelov (2020), "Top2Vec: Distributed Representations of Topics", arXiv
    2020 (arXiv:2008.09470).
    Relevance: the embedding-plus-clustering alternative in the same family
    as BERTopic; listed because any future work replacing our BERTopic arm
    should benchmark Top2Vec alongside LDA rather than treating LDA as the
    only classical baseline.

Connection and divergence vs. repo: §15 finds hard topic id beats soft/LDA
in the full fusion architecture on a random split; §17 finds the hybrid
representation inconclusive; §20, on a minimal SBERT backbone, finds hard
and soft tied in-distribution (73.46% vs. 73.44% accuracy) while soft and LDA
both beat hard on LOAO authors. The literature (Egger and Yu) predicts the
in-distribution ordering but not the LOAO reversal, which is this repo's
distinctive empirical contribution: topic-distribution features act less as
accuracy boosters and more as bias reducers under author shift.

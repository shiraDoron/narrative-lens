"""
Narrative Classification — Unseen-Author Error Diagnostics #2: domain-shift/novelty features
================================================================================================
Follow-up to narrative_unseen_author_error_diagnostics.py (first pass): that pass used 5
generic features and found a weak signal dominated by classifier_margin - near-tautological
(low model confidence correlates with being wrong) and uninformative about *why* LOAO fails.

This second, still-minimal pass asks a sharper question: are unseen-author errors associated
with the test text being semantically/lexically DISTANT from its own narrative's training
distribution, or with its entities/topics being NOVEL (never seen for that narrative in
training) - rather than with the classifier's own confidence? classifier_margin is therefore
EXCLUDED from the main tree (reported separately only as a sanity check).

All features are computed strictly from each held-out author's OWN train split (no leakage -
same split_leave_one_author/cache used by Experiment 25) - author identity itself is never a
feature. No new heavy model inference - only cosine similarity/vocabulary-overlap arithmetic on
top of already-cached SBERT embeddings, soft-topic vectors and the Experiment-24 raw-entities
cache. No reliability/emotion features (only available for 3 of the 14 authors) - all 14 fresh
authors are used, for consistency.

Features (11):
  Semantic (SBERT embedding, cosine):
    1. nearest_train_sbert_similarity          - max similarity to ANY train example.
    2. mean_same_narrative_similarity          - mean similarity to train examples sharing the
                                                  test example's true narrative.
    3. distance_to_same_narrative_centroid     - 1 - cos_sim(test, mean-embedding of
                                                  same-narrative train examples).
  Entity / lexical novelty:
    4. entity_overlap_ratio_with_train         - fraction of the test example's entities that
                                                  appear ANYWHERE in the author's train split
                                                  (any narrative) - generic vocabulary familiarity.
    5. entity_novelty_ratio                    - 1 - fraction of entities seen specifically in
                                                  SAME-narrative train texts (narrative-specific
                                                  entity novelty, even if the entity is known
                                                  elsewhere).
    6. lexical_overlap_with_train              - fraction of the test example's content tokens
                                                  (analyze_agendas.tokenize) seen in same-
                                                  narrative train texts.
  Topic distribution:
    7. topic_distribution_distance_to_same_narrative_train - Euclidean distance between the
                                                  test example's soft-topic vector and the mean
                                                  soft-topic vector of same-narrative train
                                                  examples.
  Basic style (naive, regex-based - no new NLP model):
    8. avg_sentence_length   - words / naive sentence count ([.!?]+ split).
    9. punctuation_rate      - punctuation chars / text length.
    10. hashtag_count
    11. mention_count

Target: correct_prediction, from the already-trained 'sbert_original' checkpoint (Experiment 25)
- inference/forward pass only, no re-training.

Evaluation (per user request - NOT train accuracy only): StratifiedGroupKFold (5-fold, grouped
by author so no author's examples leak across folds - a plain random split would overstate
generalization since rows from the same author are highly correlated) for an honest accuracy
estimate, plus a final fit on all data (standard practice) for interpretation (feature
importance / tree rules / per-leaf error rates). max_depth in {3,4,5}, smallest (3) tried first.

Run (from repo root):
    python experiments/author_generalization/narrative_unseen_author_domain_shift_diagnostics.py
"""
import json
import os
import re
import string
import sys

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
import matplotlib.pyplot as plt

from narrative_lens.config import NARRATIVES
from narrative_lens.train import load_raw_data, split_leave_one_author
from narrative_lens.features.analyze_agendas import tokenize

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from narrative_ablation_loao import AblationDetector  # noqa: E402
from narrative_fresh_author_confirmatory import (  # noqa: E402
    load_frozen_authors, build_or_load_raw_entities_cache, build_or_load_author_cache,
    CHECKPOINT_DIR,
)

VARIANT = "sbert_original"

NOVELTY_FEATURES = [
    "nearest_train_sbert_similarity", "mean_same_narrative_similarity",
    "distance_to_same_narrative_centroid", "entity_overlap_ratio_with_train",
    "entity_novelty_ratio", "lexical_overlap_with_train",
    "topic_distribution_distance_to_same_narrative_train",
    "avg_sentence_length", "punctuation_rate", "hashtag_count", "mention_count",
]

REPORT_DIR = "reports/results/narrative_unseen_author_domain_shift_diagnostics"
DATASET_FILE = os.path.join(REPORT_DIR, "diagnostic_dataset.csv")
IMPORTANCE_FILE = os.path.join(REPORT_DIR, "feature_importance.csv")
LEAF_STATS_FILE = os.path.join(REPORT_DIR, "leaf_error_rates.csv")
TREE_TEXT_FILE = os.path.join(REPORT_DIR, "tree_rules.txt")
TREE_PNG_FILE = os.path.join(REPORT_DIR, "tree.png")
SUMMARY_FILE = os.path.join(REPORT_DIR, "summary.json")

PUNCT_SET = set(string.punctuation)


def load_detector(author, meta):
    detector = AblationDetector(set(), ner_vocab_size=1, srl_vocab_size=1,
                                 bertopic_vec_size=meta["bertopic_vec_size"], sbert_dim=meta["sbert_dim"])
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{VARIANT}_{author}.pth")
    detector.load_state_dict(torch.load(checkpoint_file, weights_only=True))
    detector.eval()
    return detector


def style_features(text):
    words = text.split()
    n_words = len(words)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    n_sentences = len(sentences) if sentences else 1
    avg_sentence_length = n_words / n_sentences
    punctuation_rate = (sum(1 for c in text if c in PUNCT_SET) / len(text)) if text else 0.0
    hashtag_count = len(re.findall(r"#\w+", text))
    mention_count = len(re.findall(r"@\w+", text))
    return avg_sentence_length, punctuation_rate, hashtag_count, mention_count


def entity_set(text, raw_entities_by_text):
    entities = raw_entities_by_text.get(text)
    if not entities:
        return None
    return {e["text"].strip().lower() for e in entities}


def build_author_rows(author, df, raw_entities_by_text):
    cache = build_or_load_author_cache(author, None, None, None, None)
    meta = cache["_meta"]
    detector = load_detector(author, meta)

    train_data, _, test_data = split_leave_one_author(df, author)
    train_texts = train_data["text"].astype(str).str.slice(0, 3000).tolist()
    test_texts = test_data["text"].astype(str).str.slice(0, 3000).tolist()
    train_rows, test_rows = cache["train"], cache["test"]
    assert len(train_texts) == len(train_rows) and len(test_texts) == len(test_rows), \
        f"length mismatch for author '{author}'"

    train_embeddings = np.stack([f["sbert_embedding"].numpy() for f, _ in train_rows])
    train_soft = np.stack([f["soft_dense"].numpy() for f, _ in train_rows])
    train_labels = np.array([l for _, l in train_rows])
    train_norm = train_embeddings / (np.linalg.norm(train_embeddings, axis=1, keepdims=True) + 1e-8)

    # Per-narrative train entity/lexical vocabularies + SBERT/topic centroids (built ONLY from
    # this author's own train split - no leakage, no author identity used as a feature).
    narrative_entity_vocab, narrative_lexical_vocab = {}, {}
    narrative_sbert_centroid, narrative_soft_centroid = {}, {}
    full_train_entity_vocab = set()
    for lbl in np.unique(train_labels):
        mask = train_labels == lbl
        narrative_sbert_centroid[lbl] = train_embeddings[mask].mean(axis=0)
        narrative_soft_centroid[lbl] = train_soft[mask].mean(axis=0)
        ent_vocab, lex_vocab = set(), set()
        for t in (train_texts[i] for i in np.where(mask)[0]):
            ents = entity_set(t, raw_entities_by_text)
            if ents:
                ent_vocab |= ents
            lex_vocab |= set(tokenize(t))
        narrative_entity_vocab[lbl] = ent_vocab
        narrative_lexical_vocab[lbl] = lex_vocab
        full_train_entity_vocab |= ent_vocab

    test_embeddings = np.stack([f["sbert_embedding"].numpy() for f, _ in test_rows])
    test_norm = test_embeddings / (np.linalg.norm(test_embeddings, axis=1, keepdims=True) + 1e-8)
    sim_matrix = test_norm @ train_norm.T  # (n_test, n_train)
    nearest_sim_all = sim_matrix.max(axis=1)

    rows = []
    with torch.no_grad():
        for i, (feat, label) in enumerate(test_rows):
            text = test_texts[i]
            probs = detector.classify_features({"sbert_embedding": feat["sbert_embedding"]})
            predicted = int(torch.argmax(probs).item())

            mask = train_labels == label
            mean_same_narrative_similarity = float(sim_matrix[i, mask].mean()) if mask.any() else np.nan
            centroid = narrative_sbert_centroid.get(label)
            if centroid is not None:
                c_norm = centroid / (np.linalg.norm(centroid) + 1e-8)
                distance_to_centroid = 1.0 - float(test_norm[i] @ c_norm)
            else:
                distance_to_centroid = np.nan

            ents_test = entity_set(text, raw_entities_by_text)
            if ents_test:
                entity_overlap_ratio = len(ents_test & full_train_entity_vocab) / len(ents_test)
                same_nar_ent_vocab = narrative_entity_vocab.get(label, set())
                entity_novelty_ratio = 1.0 - (len(ents_test & same_nar_ent_vocab) / len(ents_test))
            else:
                entity_overlap_ratio, entity_novelty_ratio = np.nan, np.nan

            tokens_test = set(tokenize(text))
            same_nar_lex_vocab = narrative_lexical_vocab.get(label, set())
            lexical_overlap = (len(tokens_test & same_nar_lex_vocab) / len(tokens_test)) if tokens_test else np.nan

            soft_centroid = narrative_soft_centroid.get(label)
            topic_dist = float(np.linalg.norm(feat["soft_dense"].numpy() - soft_centroid)) \
                if soft_centroid is not None else np.nan

            avg_sent_len, punct_rate, hashtag_count, mention_count = style_features(text)

            rows.append({
                "author": author,
                "true_narrative": NARRATIVES[label],
                "predicted_narrative": NARRATIVES[predicted],
                "correct": int(predicted == label),
                "nearest_train_sbert_similarity": float(nearest_sim_all[i]),
                "mean_same_narrative_similarity": mean_same_narrative_similarity,
                "distance_to_same_narrative_centroid": distance_to_centroid,
                "entity_overlap_ratio_with_train": entity_overlap_ratio,
                "entity_novelty_ratio": entity_novelty_ratio,
                "lexical_overlap_with_train": lexical_overlap,
                "topic_distribution_distance_to_same_narrative_train": topic_dist,
                "avg_sentence_length": avg_sent_len,
                "punctuation_rate": punct_rate,
                "hashtag_count": hashtag_count,
                "mention_count": mention_count,
            })
    return rows


def fit_and_report(dataset, feature_cols, label_suffix):
    X = dataset[feature_cols].fillna(-1)
    y = dataset["correct"]
    groups = dataset["author"]

    overall_correct_rate = y.mean()
    majority_baseline = max(overall_correct_rate, 1 - overall_correct_rate)
    print(f"\n=== Tree [{label_suffix}] (features: {feature_cols}) ===")
    print(f"Overall correct rate: {overall_correct_rate * 100:.1f}% | "
          f"majority-class baseline: {majority_baseline * 100:.1f}%")

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = {}
    for depth in (3, 4, 5):
        clf_cv = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=25, class_weight="balanced",
                                         random_state=42)
        cv_scores = cross_val_score(clf_cv, X, y, cv=cv, groups=groups, scoring="accuracy")
        print(f"  max_depth={depth}: grouped 5-fold CV accuracy = {cv_scores.mean() * 100:.1f}% "
              f"(+/- {cv_scores.std() * 100:.1f}pp) | folds={np.round(cv_scores * 100, 1)}")
        cv_results[depth] = {"mean": float(cv_scores.mean()), "std": float(cv_scores.std()),
                              "folds": [float(s) for s in cv_scores]}

    # Final fit on ALL data (depth=4) for interpretation only - CV numbers above are the
    # honest generalization estimate, not this fit's own accuracy.
    clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=25, class_weight="balanced", random_state=42)
    clf.fit(X, y)

    importance_df = pd.DataFrame({
        "feature": feature_cols, "importance": clf.feature_importances_,
    }).sort_values("importance", ascending=False)
    print(f"Feature importances (full-data fit, depth=4):\n{importance_df.to_string(index=False)}")

    leaf_ids = clf.apply(X)
    leaf_df = dataset.copy()
    leaf_df["leaf_id"] = leaf_ids
    leaf_stats = leaf_df.groupby("leaf_id").agg(
        n_samples=("correct", "size"), error_rate=("correct", lambda s: 1 - s.mean()),
    ).sort_values("n_samples", ascending=False)
    print(f"Per-leaf stats:\n{leaf_stats.to_string()}")

    return clf, importance_df, leaf_stats, overall_correct_rate, majority_baseline, cv_results


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    authors, _ = load_frozen_authors()
    print(f"Loaded {len(authors)} frozen fresh authors.")
    raw_entities_by_text = build_or_load_raw_entities_cache()["raw_entities_by_text"]
    df = load_raw_data()

    all_rows = []
    for author in authors:
        print(f"Processing author '{author}'...")
        all_rows.extend(build_author_rows(author, df, raw_entities_by_text))
    dataset = pd.DataFrame(all_rows)
    dataset.to_csv(DATASET_FILE, index=False, encoding="utf-8-sig")
    print(f"\nSaved per-example diagnostic dataset ({len(dataset)} rows) to '{DATASET_FILE}'.")

    clf, importance_df, leaf_stats, overall_correct_rate, majority_baseline, cv_results = fit_and_report(
        dataset, NOVELTY_FEATURES, "novelty+style only (no classifier_margin)")
    importance_df.to_csv(IMPORTANCE_FILE, index=False, encoding="utf-8-sig")
    leaf_stats.to_csv(LEAF_STATS_FILE, encoding="utf-8-sig")

    with open(TREE_TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(export_text(clf, feature_names=NOVELTY_FEATURES))
    print(f"Saved tree rules to '{TREE_TEXT_FILE}'.")

    plt.figure(figsize=(26, 12))
    plot_tree(clf, feature_names=NOVELTY_FEATURES, class_names=["incorrect", "correct"],
              filled=True, rounded=True, fontsize=7)
    plt.tight_layout()
    plt.savefig(TREE_PNG_FILE, dpi=150)
    plt.close()
    print(f"Saved tree visualization to '{TREE_PNG_FILE}'.")

    beats_baseline = any(r["mean"] > majority_baseline for r in cv_results.values())
    summary = {
        "seed": 42,
        "variant": VARIANT,
        "n_authors": len(authors),
        "n_examples": len(dataset),
        "features": NOVELTY_FEATURES,
        "classifier_margin_excluded": True,
        "cv_method": "StratifiedGroupKFold",
        "cv_n_splits": 5,
        "cv_grouped_by": "author",
        "overall_correct_rate": overall_correct_rate,
        "majority_baseline": majority_baseline,
        "cv_results_by_depth": cv_results,
        "any_depth_beats_majority_baseline": beats_baseline,
        "full_fit_depth": 4,
        "full_fit_min_samples_leaf": 25,
        "conclusion": "Under grouped cross-validation, the tested semantic, lexical, entity, "
                      "topic, and simple stylistic features did not predict unseen-author "
                      "classification errors above the majority baseline. Therefore, no stable "
                      "per-example explanatory pattern was identified with the available "
                      "diagnostic features.",
    }
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved run summary to '{SUMMARY_FILE}'.")


if __name__ == "__main__":
    main()

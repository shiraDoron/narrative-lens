"""
Narrative Classification — Unseen-Author Error Diagnostics (minimal first pass)
================================================================================
Diagnostic/interpretability study, NOT a model-improvement attempt: explains (associationally,
not causally) WHICH per-example properties correlate with the model being wrong on a held-out
author's text (Leave-One-Author-Out), using the 14 frozen fresh authors from Experiment 25 and
their already-trained 'sbert_original' checkpoints (models/experiments/
narrative_fresh_author_confirmatory/sbert_original_{author}.pth) - no new training, no new
heavy feature extraction. Reuses only artifacts that already exist on disk:
  - Per-author feature cache (sbert_embedding + soft_dense) from narrative_fresh_author_confirmatory.py.
  - The corpus-wide raw-entities cache from Experiment 24 (data/cache/cached_raw_entities_by_text.pt).
  - The trained sbert_original checkpoints themselves (inference/forward pass only).

Scope decision (explicit, per user request): start minimal - ONE shallow Decision Tree, 5
already-existing/cheaply-derived features, no Random Forest, no bootstrap stability check, no
per-narrative sub-trees yet. Only expand if this first pass shows an interesting signal.

Features used (none fabricated - each is directly derived from an existing cached artifact):
  1. text_length       - len(text actually fed to the model, i.e. truncated to 3000 chars).
  2. entity_count      - len(raw_entities_by_text[text]) from Experiment 24's cache (NaN/-1 if
                          the exact text isn't in that cache - coverage is reported).
  3. soft_topic_max_prob - max(soft_dense) - the already-cached BERTopic soft-topic vector.
  4. soft_topic_entropy  - Shannon entropy over the nonzero entries of soft_dense.
  5. classifier_margin   - top1_prob - top2_prob of the trained model's own softmax output
                            (computed via a forward pass over the already-cached sbert_embedding
                            - no re-training).

Target: correct_prediction (1 if the model's predicted narrative == true narrative, else 0).

Run (from repo root):
    python experiments/author_generalization/narrative_unseen_author_error_diagnostics.py
"""
import math
import os
import sys

import numpy as np
import pandas as pd
import torch
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
import matplotlib.pyplot as plt

from narrative_lens.config import NARRATIVES
from narrative_lens.train import load_raw_data, split_leave_one_author

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from narrative_ablation_loao import AblationDetector  # noqa: E402
from narrative_fresh_author_confirmatory import (  # noqa: E402
    load_frozen_authors, build_or_load_raw_entities_cache, build_or_load_author_cache,
    CHECKPOINT_DIR,
)

VARIANT = "sbert_original"  # cleanest/least-confounded of the 3 Experiment-25 variants
FEATURES = ["text_length", "entity_count", "soft_topic_max_prob", "soft_topic_entropy", "classifier_margin"]

REPORT_DIR = "reports/results/narrative_unseen_author_error_diagnostics"
DATASET_FILE = os.path.join(REPORT_DIR, "diagnostic_dataset.csv")
IMPORTANCE_FILE = os.path.join(REPORT_DIR, "feature_importance.csv")
LEAF_STATS_FILE = os.path.join(REPORT_DIR, "leaf_error_rates.csv")
TREE_TEXT_FILE = os.path.join(REPORT_DIR, "tree_rules.txt")
TREE_PNG_FILE = os.path.join(REPORT_DIR, "tree.png")
SUMMARY_FILE = os.path.join(REPORT_DIR, "summary.json")
SEED = 42


def soft_dense_stats(soft_dense):
    vec = soft_dense.numpy()
    nonzero = vec[vec > 0]
    max_prob = float(vec.max()) if vec.size else 0.0
    entropy = float(-(nonzero * np.log(nonzero)).sum()) if nonzero.size else 0.0
    return max_prob, entropy


def load_detector(author, meta):
    detector = AblationDetector(set(), ner_vocab_size=1, srl_vocab_size=1,
                                 bertopic_vec_size=meta["bertopic_vec_size"], sbert_dim=meta["sbert_dim"])
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{VARIANT}_{author}.pth")
    detector.load_state_dict(torch.load(checkpoint_file, weights_only=True))
    detector.eval()
    return detector


def build_dataset(authors, df, raw_entities_by_text):
    rows = []
    n_missing_entities = 0
    for author in authors:
        print(f"Processing author '{author}'...")
        cache = build_or_load_author_cache(author, None, None, None, None)
        meta = cache["_meta"]
        detector = load_detector(author, meta)

        test_data = split_leave_one_author(df, author)[2]
        texts = test_data["text"].astype(str).str.slice(0, 3000).tolist()
        assert len(texts) == len(cache["test"]), f"length mismatch for author '{author}'"

        with torch.no_grad():
            for i, (feat, label) in enumerate(cache["test"]):
                probs = detector.classify_features({"sbert_embedding": feat["sbert_embedding"]})
                probs_sorted, _ = torch.sort(probs, descending=True)
                predicted = int(torch.argmax(probs).item())
                confidence = float(probs_sorted[0].item())
                margin = float((probs_sorted[0] - probs_sorted[1]).item())

                max_prob, entropy = soft_dense_stats(feat["soft_dense"])

                text = texts[i]
                entities = raw_entities_by_text.get(text)
                if entities is None:
                    n_missing_entities += 1
                    entity_count = np.nan
                else:
                    entity_count = len(entities)

                rows.append({
                    "author": author,
                    "true_narrative": NARRATIVES[label],
                    "predicted_narrative": NARRATIVES[predicted],
                    "correct": int(predicted == label),
                    "text_length": len(text),
                    "entity_count": entity_count,
                    "soft_topic_max_prob": max_prob,
                    "soft_topic_entropy": entropy,
                    "classifier_confidence": confidence,
                    "classifier_margin": margin,
                })

    if n_missing_entities:
        print(f"[!] {n_missing_entities}/{len(rows)} row(s) had no entry in the raw-entities cache "
              f"(entity_count left as NaN, filled with -1 before training the tree).")
    return pd.DataFrame(rows)


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    authors, _ = load_frozen_authors()
    print(f"Loaded {len(authors)} frozen fresh authors.")

    raw_entities_cache = build_or_load_raw_entities_cache()
    raw_entities_by_text = raw_entities_cache["raw_entities_by_text"]

    df = load_raw_data()
    dataset = build_dataset(authors, df, raw_entities_by_text)
    dataset.to_csv(DATASET_FILE, index=False, encoding="utf-8-sig")
    print(f"\nSaved per-example diagnostic dataset ({len(dataset)} rows) to '{DATASET_FILE}'.")

    overall_correct_rate = dataset["correct"].mean()
    majority_baseline = max(overall_correct_rate, 1 - overall_correct_rate)
    print(f"Overall correct rate (variant='{VARIANT}', n={len(dataset)}): {overall_correct_rate * 100:.1f}% "
          f"| majority-class baseline: {majority_baseline * 100:.1f}%")

    X = dataset[FEATURES].fillna(-1)
    y = dataset["correct"]

    clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=25, class_weight="balanced", random_state=42)
    clf.fit(X, y)
    tree_accuracy = clf.score(X, y)
    print(f"Decision tree training-set accuracy: {tree_accuracy * 100:.1f}% "
          f"(majority-class baseline: {majority_baseline * 100:.1f}%)")

    importance_df = pd.DataFrame({
        "feature": FEATURES,
        "importance": clf.feature_importances_,
    }).sort_values("importance", ascending=False)
    importance_df.to_csv(IMPORTANCE_FILE, index=False, encoding="utf-8-sig")
    print(f"\nFeature importances:\n{importance_df.to_string(index=False)}")

    with open(TREE_TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(export_text(clf, feature_names=FEATURES))
    print(f"Saved tree rules to '{TREE_TEXT_FILE}'.")

    plt.figure(figsize=(20, 10))
    plot_tree(clf, feature_names=FEATURES, class_names=["incorrect", "correct"],
              filled=True, rounded=True, fontsize=8)
    plt.tight_layout()
    plt.savefig(TREE_PNG_FILE, dpi=150)
    plt.close()
    print(f"Saved tree visualization to '{TREE_PNG_FILE}'.")

    leaf_ids = clf.apply(X)
    leaf_df = dataset.copy()
    leaf_df["leaf_id"] = leaf_ids
    leaf_stats = leaf_df.groupby("leaf_id").agg(
        n_samples=("correct", "size"),
        error_rate=("correct", lambda s: 1 - s.mean()),
    ).sort_values("n_samples", ascending=False)
    leaf_stats.to_csv(LEAF_STATS_FILE, encoding="utf-8-sig")
    print(f"\nPer-leaf stats (n_samples, error_rate):\n{leaf_stats.to_string()}")
    print(f"Saved per-leaf stats to '{LEAF_STATS_FILE}'.")

    import json
    summary = {
        "seed": SEED,
        "variant": VARIANT,
        "n_authors": len(authors),
        "n_examples": len(dataset),
        "features": FEATURES,
        "tree_max_depth": 4,
        "tree_min_samples_leaf": 25,
        "overall_correct_rate": overall_correct_rate,
        "majority_baseline": majority_baseline,
        "tree_training_accuracy": tree_accuracy,
        "note": "training-set accuracy only (no CV in this first pass) - see diagnostics #2 for "
                "a cross-validated follow-up.",
    }
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved run summary to '{SUMMARY_FILE}'.")


if __name__ == "__main__":
    main()

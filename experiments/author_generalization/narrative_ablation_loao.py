"""
Narrative Classification — Feature Ablation on Unseen Authors (Leave-One-Author-Out)
======================================================================================
Follow-up to EXPERIMENTS.md section 18 (LOAO generalization test): baseline_fusion showed
severe generalization gaps on 3 held-out real authors/accounts (IDF, MariaZakharova,
BernieSanders never seen during training) - recall on the held-out author's own narrative
dropped 20-38 percentage points vs. the random-split baseline, and 2 of 3 authors were
majority-misrouted to "Right-wing". This script asks WHICH feature group helps or hurts
generalization to an unseen author, via a controlled ablation on the SAME 3 accounts and
the SAME split logic (train.split_leave_one_author, unmodified, imported directly - same
random_state=42, so row membership is byte-identical to section 18's runs).

Variants compared (all "SBERT + X", same MLP architecture/hyperparameters, only the
concatenated feature arms differ - see AblationDetector):
  1. sbert_only                      - SBERT embedding alone (no engineered feature at all).
  2. sbert_ner                       - SBERT + NER only.
  3. sbert_stance_hard_topic         - SBERT + Stance (hard BERTopic topic_id). NOTE: in this
                                        codebase "Stance" (TopicStanceLayer/features["stance"])
                                        IS the hard topic_id - there is no separate stance
                                        signal - so this variant also stands in for the
                                        user-requested optional "SBERT+Hard Topic" variant;
                                        they are the SAME model/result here, not duplicated.
  4. sbert_srl                       - SBERT + SRL only.
  5. sbert_all_engineered            - SBERT + NER + SRL + Emotion + Stance/Hard-Topic +
                                        Reliability (mirrors fusion.HybridNarrativeDetector's
                                        engineered-feature set, minus agenda_ideology which
                                        isn't part of the ablation the user asked for).
  6. sbert_soft_topic                - SBERT + Soft Topic Distribution (top-5,
                                        approximate_distribution(), re-normalized) instead of
                                        a hard topic id.
  7. sbert_all_engineered_plus_soft  - variant 5's arms + Soft Topic Distribution added on top
                                        (both hard and soft topic signals present together).

Design decision (stated explicitly, not silently assumed): hard AND soft topic features are
BOTH computed from the SAME single BERTopic model
(models/experiments/soft_v2_baseline_seeded, the same model used by
narrative_topic_compare.py) - not from the production legacy model
(models/saved_topic_model). This isolates "single id vs. distribution" as the one true
independent variable between variants 3 and 6, exactly like narrative_topic_compare.py's
Hard-vs-Soft comparison methodology. The Topics arm reuses narrative_topic_compare.py's
TopicFeatureLayer (imported unmodified) for both hard_topic and soft_topic.

Efficiency design (avoids repeating ~5-23h/author heavy inference 7x per author): NER, SRL,
Emotion and Reliability features are REUSED BY POSITION from the already-computed
data/cache/cached_features_baseline_fusion_loao_{author}.pt (section 18's own cache),
verified via a by-position label-alignment check (same safety pattern as
narrative_topic_compare.py's build_full_feature_cache) before trusting the reuse. Only SBERT
embeddings (batched encode) and hard+soft BERTopic features (batched transform +
approximate_distribution) are computed fresh - both comparatively cheap. This full raw-feature
set is extracted ONCE per held-out author and cached to
data/cache/cached_features_ablation_loao_{author}.pt; all 7 lightweight MLP variants for that
author are then trained cheaply from this single shared cache.

Strict constraints honored throughout: identical train/val/test split per author across all 7
variants (see above); held-out author fully excluded from training in every variant (same
split_leave_one_author guarantee); the held-out author's test rows are NEVER used for
checkpoint selection - checkpoints are chosen purely by validation Macro-F1 (reusing train.py's
own `evaluate`/`compute_metrics`, unmodified); one single fixed seed (42) applied identically to
every variant/author for a fair comparison (per user's explicit request - not a multi-seed
variance study, just consistency).

Nothing under models/best_*.pth, data/cache/cached_features_baseline_fusion_loao_*.pt,
data/cache/cached_features_hybrid*.pt, reports/tables/model_comparison_results.json, or any of
narrative_topic_compare.py's/narrative_topic_hybrid.py's own files is ever touched or
overwritten by this script - all outputs go to clearly separate, dedicated paths (see the
*_DIR / *_FILE constants below).

Run (from repo root), one author at a time (each may take a while: SBERT/BERTopic extraction
pass + 7 lightweight MLP trainings):
    python experiments/author_generalization/narrative_ablation_loao.py --author IDF
    python experiments/author_generalization/narrative_ablation_loao.py --author MariaZakharova
    python experiments/author_generalization/narrative_ablation_loao.py --author BernieSanders
Then, after all 3 authors have been run:
    python experiments/author_generalization/narrative_ablation_loao.py --aggregate
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# narrative_topic_compare.py is a sibling experiment script (not part of the installable
# narrative_lens package) living in experiments/feature_ablation/ - add just that folder to
# sys.path. Everything else below is imported from the installed `narrative_lens` package
# (pip install -e ., see pyproject.toml) instead of a sys.path hack.
import sys

_SIBLING_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "feature_ablation"))
if _SIBLING_DIR not in sys.path:
    sys.path.insert(0, _SIBLING_DIR)

from narrative_lens.config import NARRATIVES, NUM_NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from narrative_lens.train import load_raw_data, split_leave_one_author, evaluate, compute_metrics, save_confusion_matrix_csv
from narrative_lens.topic_modeling.topic_preprocessing import clean_text_for_topic_model
from narrative_topic_compare import TopicFeatureLayer, BERTOPIC_MODEL_PATH, BERTOPIC_EMBEDDING_MODEL_NAME, SOFT_TOP_N

from narrative_lens.features.ner import NarrativeEntityLayer
from narrative_lens.features.srl import SRLNarrativeLayer
from narrative_lens.features.emotion import EmotionAgencyLayer
from narrative_lens.features.reliability import ReliabilityLayer

# =========================================================================================
# Paths - all new/dedicated, none overlap with any existing cache/checkpoint/results file.
# =========================================================================================
AUTHORS = ("IDF", "MariaZakharova", "BernieSanders")
SEED = 42  # single fixed seed for every variant/author, for a fair, simple comparison

CACHE_DIR = "data/cache"
CHECKPOINT_DIR = "models/experiments/narrative_ablation_loao"
REPORT_DIR = "reports/results/narrative_ablation_loao"
RESULTS_FILE = f"{REPORT_DIR}/results.json"

EXISTING_LOAO_CACHE_TEMPLATE = "data/cache/cached_features_baseline_fusion_loao_{author}.pt"

VARIANTS = {
    "sbert_only": set(),
    "sbert_ner": {"ner"},
    "sbert_stance_hard_topic": {"hard_topic"},
    "sbert_srl": {"srl"},
    "sbert_all_engineered": {"ner", "srl", "emotion", "hard_topic", "reliability"},
    "sbert_soft_topic": {"soft_topic"},
    "sbert_all_engineered_plus_soft": {"ner", "srl", "emotion", "hard_topic", "reliability", "soft_topic"},
}

RIGHT_WING_IDX = NARRATIVES.index("Right-wing")


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


# =========================================================================================
# Feature cache: reuse NER/SRL/Emotion/Reliability from the existing LOAO cache (by
# position, verified), compute SBERT + hard/soft BERTopic features fresh.
# =========================================================================================
def build_hard_soft_dense_vectors(texts, bertopic_model, num_bertopic_topics):
    """Batched BERTopic hard+soft computation (subset of narrative_topic_compare.py's
    build_topic_dense_vectors - LDA omitted, not needed here)."""
    oov_idx = num_bertopic_topics
    vec_size = num_bertopic_topics + 1

    cleaned_texts = [clean_text_for_topic_model(t) for t in texts]
    safe_texts = [t if t.strip() else "empty" for t in cleaned_texts]

    print(f"  Running BERTopic .transform() on {len(safe_texts)} texts (hard topic ids)...")
    hard_topics, _ = bertopic_model.transform(safe_texts)

    print(f"  Running BERTopic .approximate_distribution() on {len(safe_texts)} texts (soft distribution)...")
    soft_dists, _ = bertopic_model.approximate_distribution(safe_texts)

    hard_dense_list, soft_dense_list = [], []
    for i in range(len(texts)):
        hard_vec = np.zeros(vec_size, dtype=np.float32)
        tid = int(hard_topics[i])
        idx = oov_idx if (tid < 0 or tid >= num_bertopic_topics) else tid
        hard_vec[idx] = 1.0
        hard_dense_list.append(hard_vec)

        scores = soft_dists[i]
        nonzero_idx = [j for j, s in enumerate(scores) if s > 0]
        soft_vec = np.zeros(vec_size, dtype=np.float32)
        if nonzero_idx:
            nonzero_idx.sort(key=lambda j: scores[j], reverse=True)
            top_idx = nonzero_idx[:SOFT_TOP_N]
            total = float(sum(scores[j] for j in top_idx))
            if total > 0:
                for j in top_idx:
                    idx2 = oov_idx if (j < 0 or j >= num_bertopic_topics) else j
                    soft_vec[idx2] += float(scores[j]) / total
        soft_dense_list.append(soft_vec)

    return hard_dense_list, soft_dense_list


def build_or_load_cache(author):
    cache_file = os.path.join(CACHE_DIR, f"cached_features_ablation_loao_{author}.pt")
    if os.path.exists(cache_file):
        print(f"Found existing ablation feature cache '{cache_file}'. Loading...")
        return torch.load(cache_file, weights_only=False)

    print(f"\n=== Building fresh ablation feature cache for held-out author '{author}' ===")
    df = load_raw_data()
    train_data, val_data, test_data = split_leave_one_author(df, author)
    for split_df in (train_data, val_data, test_data):
        split_df["text"] = split_df["text"].astype(str).str.slice(0, 3000)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    existing_cache_path = EXISTING_LOAO_CACHE_TEMPLATE.format(author=author)
    print(f"Loading existing LOAO cache '{existing_cache_path}' to reuse its NER/SRL/Emotion/"
          f"Reliability features (read-only, by-position, verified by label alignment)...")
    existing_cache = torch.load(existing_cache_path, weights_only=False)

    for name, split_df in splits.items():
        cached_labels = [label for _, label in existing_cache[name]]
        fresh_labels = split_df["label"].astype(int).tolist()
        if cached_labels != fresh_labels or len(cached_labels) != len(split_df):
            raise RuntimeError(
                f"Alignment check FAILED for split '{name}' (author='{author}'): the existing "
                f"'{existing_cache_path}' no longer matches a fresh load_raw_data()+"
                f"split_leave_one_author() reconstruction. Refusing to silently reuse "
                f"misaligned features."
            )
    print("Alignment verified for train/val/test: safe to reuse NER/SRL/Emotion/Reliability by position.")

    print(f"Loading BERTopic model from '{BERTOPIC_MODEL_PATH}' (shared hard+soft source, "
          f"same model narrative_topic_compare.py uses, for a fair hard-vs-soft comparison)...")
    bertopic_model = BERTopic.load(BERTOPIC_MODEL_PATH, embedding_model=BERTOPIC_EMBEDDING_MODEL_NAME)
    num_bertopic_topics = len([t for t in bertopic_model.get_topics().keys() if t != -1])
    print(f"  -> {num_bertopic_topics} real topics (+1 reserved OOV/outlier slot).")

    print(f"Loading SBERT model '{BERTOPIC_EMBEDDING_MODEL_NAME}' (frozen, encode-only)...")
    sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)

    result = {}
    max_ner_idx, max_srl_idx, sbert_dim = -1, -1, None
    for name, split_df in splits.items():
        print(f"\n--- Split '{name}' ({len(split_df)} rows) ---")
        texts = split_df["text"].tolist()
        labels = split_df["label"].astype(int).tolist()

        print("  Computing SBERT embeddings...")
        sbert_embeddings = sbert_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        sbert_dim = int(sbert_embeddings.shape[1])

        print("  Computing hard+soft BERTopic features (batched)...")
        hard_dense, soft_dense = build_hard_soft_dense_vectors(texts, bertopic_model, num_bertopic_topics)

        rows = []
        for i in range(len(texts)):
            base_feat, base_label = existing_cache[name][i]
            assert base_label == labels[i], f"label mismatch at split={name} idx={i}"
            ner_idx, srl_idx = base_feat["ner"], base_feat["srl"]
            if ner_idx.numel() > 0:
                max_ner_idx = max(max_ner_idx, int(ner_idx.max().item()))
            if srl_idx.numel() > 0:
                max_srl_idx = max(max_srl_idx, int(srl_idx.max().item()))
            feat = {
                "sbert_embedding": torch.tensor(sbert_embeddings[i], dtype=torch.float32),
                "ner": ner_idx,
                "srl": srl_idx,
                "emotion": base_feat["emotion"],
                "reliability": base_feat["reliability"],
                "hard_dense": torch.from_numpy(hard_dense[i]),
                "soft_dense": torch.from_numpy(soft_dense[i]),
            }
            rows.append((feat, labels[i]))
        result[name] = rows

    result["_meta"] = {
        "bertopic_vec_size": num_bertopic_topics + 1,
        "num_bertopic_topics": num_bertopic_topics,
        "ner_vocab_size": max_ner_idx + 1,
        "srl_vocab_size": max_srl_idx + 1,
        "sbert_dim": sbert_dim,
        "reused_ner_srl_emotion_reliability_from": existing_cache_path,
        "bertopic_model_path": BERTOPIC_MODEL_PATH,
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    torch.save(result, cache_file)
    print(f"\nSaved new ablation feature cache to '{cache_file}'.")
    return result


# =========================================================================================
# Model: SBERT + configurable subset of engineered-feature "arms", concatenated -> MLP.
# =========================================================================================
class AblationDetector(nn.Module):
    """Same MLP template as fusion.HybridNarrativeDetector/SBERTOnlyDetector (Linear->ReLU->
    Dropout(0.3)->Linear->Softmax) - only the set of concatenated arms varies, so any
    difference in test performance between variants is attributable to the feature(s)
    included/excluded, not to an architecture change."""

    def __init__(self, arms, ner_vocab_size, srl_vocab_size, bertopic_vec_size, sbert_dim,
                 hidden_size=128, dropout=0.3):
        super().__init__()
        self.arms = set(arms)

        if "ner" in self.arms:
            self.ner_layer = NarrativeEntityLayer(list(range(ner_vocab_size)))
        if "srl" in self.arms:
            self.srl_layer = SRLNarrativeLayer(list(range(srl_vocab_size)))
        if "emotion" in self.arms:
            self.emotion_layer = EmotionAgencyLayer()
        if "reliability" in self.arms:
            self.reliability_layer = ReliabilityLayer()
        if "hard_topic" in self.arms:
            self.hard_topic_layer = TopicFeatureLayer("hard", vec_size=bertopic_vec_size)
        if "soft_topic" in self.arms:
            self.soft_topic_layer = TopicFeatureLayer("soft", vec_size=bertopic_vec_size)

        combined_dim = sbert_dim
        combined_dim += NUM_NARRATIVES if "ner" in self.arms else 0
        combined_dim += NUM_NARRATIVES if "srl" in self.arms else 0
        combined_dim += NUM_NARRATIVES if "emotion" in self.arms else 0
        combined_dim += 1 if "reliability" in self.arms else 0
        combined_dim += NUM_NARRATIVES if "hard_topic" in self.arms else 0
        combined_dim += NUM_NARRATIVES if "soft_topic" in self.arms else 0

        self.mlp = nn.Sequential(
            nn.Linear(combined_dim, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, NUM_NARRATIVES),
        )
        self.softmax = nn.Softmax(dim=-1)

    def classify_features(self, features):
        parts = [features["sbert_embedding"]]
        if "ner" in self.arms:
            parts.append(self.ner_layer(features["ner"]).squeeze())
        if "srl" in self.arms:
            parts.append(self.srl_layer(features["srl"]).squeeze())
        if "emotion" in self.arms:
            emotion_idx, agency_flag = features["emotion"]
            parts.append(self.emotion_layer(emotion_idx, agency_flag).squeeze())
        if "reliability" in self.arms:
            parts.append(self.reliability_layer(features["reliability"]))
        if "hard_topic" in self.arms:
            parts.append(self.hard_topic_layer(features["hard_dense"]).squeeze())
        if "soft_topic" in self.arms:
            parts.append(self.soft_topic_layer(features["soft_dense"]).squeeze())

        combined = torch.cat(parts, dim=-1)
        logits = self.mlp(combined)
        return self.softmax(logits)


# =========================================================================================
# Training loop (identical hyperparameters/early-stopping/checkpoint-selection convention as
# train.py's train() - reusing its evaluate()/compute_metrics()/save_confusion_matrix_csv()
# unmodified) - only lightweight (no feature re-extraction), since train/val/test features
# are already fully precomputed in the cache.
# =========================================================================================
def train_variant(variant_name, arms, author, train_features, val_features, test_features,
                   ner_vocab_size, srl_vocab_size, bertopic_vec_size, sbert_dim,
                   epochs=EPOCHS, batch_size=BATCH_SIZE, patience=3, lr=LEARNING_RATE, seed=SEED):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{variant_name}_{author}.pth")

    set_seed(seed)
    detector = AblationDetector(arms, ner_vocab_size, srl_vocab_size, bertopic_vec_size, sbert_dim)

    if os.path.exists(checkpoint_file):
        print(f"[{variant_name}/{author}] Found existing checkpoint - loading for eval only "
              f"(delete '{checkpoint_file}' manually to force a genuine re-run).")
        detector.load_state_dict(torch.load(checkpoint_file))
    else:
        optimizer = optim.Adam(detector.parameters(), lr=lr)
        loss_fn = nn.NLLLoss()
        best_val_macro_f1 = -1.0
        epochs_no_improve = 0

        for epoch in range(epochs):
            detector.train()
            total_train_loss, train_correct = 0.0, 0
            optimizer.zero_grad()

            for i, (features, label_idx) in enumerate(train_features):
                label = torch.tensor([label_idx], dtype=torch.long)
                probs = detector.classify_features(features)
                if probs.dim() == 1:
                    probs = probs.unsqueeze(0)

                predicted = torch.argmax(probs, dim=-1)
                if predicted.item() == label.item():
                    train_correct += 1

                loss = loss_fn(torch.log(probs + 1e-8), label)
                loss = loss / batch_size
                loss.backward()

                if (i + 1) % batch_size == 0 or (i + 1) == len(train_features):
                    optimizer.step()
                    optimizer.zero_grad()

                total_train_loss += loss.item() * batch_size

            # Checkpoint selection by VALIDATION Macro-F1 only - test features/labels for this
            # author are never touched here.
            val_metrics, avg_val_loss, _, _ = evaluate(detector, val_features, loss_fn)
            print(f"[{variant_name}/{author}] Epoch {epoch + 1}: "
                  f"Train Acc {100 * train_correct / len(train_features):.2f}% | "
                  f"Val Loss {avg_val_loss:.4f} | Val Acc {val_metrics['accuracy'] * 100:.2f}% | "
                  f"Val Macro-F1 {val_metrics['macro_f1']:.4f}")

            if val_metrics['macro_f1'] > best_val_macro_f1:
                best_val_macro_f1 = val_metrics['macro_f1']
                epochs_no_improve = 0
                torch.save(detector.state_dict(), checkpoint_file)
                print(f">>> New best model saved (Val Macro-F1: {best_val_macro_f1:.4f}) -> '{checkpoint_file}'")
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"[{variant_name}/{author}] Early stopping at epoch {epoch + 1}.")
                    break

        detector.load_state_dict(torch.load(checkpoint_file))

    # Final test evaluation - held-out author's test rows, used only here, never for tuning.
    test_metrics, _, test_true, test_pred = evaluate(detector, test_features)
    return test_metrics, test_true, test_pred


# =========================================================================================
# Orchestration
# =========================================================================================
def run_author(author):
    cache = build_or_load_cache(author)
    train_features, val_features, test_features = cache["train"], cache["val"], cache["test"]
    meta = cache["_meta"]
    bertopic_vec_size = meta["bertopic_vec_size"]
    ner_vocab_size = meta["ner_vocab_size"]
    srl_vocab_size = meta["srl_vocab_size"]
    sbert_dim = meta["sbert_dim"]

    os.makedirs(REPORT_DIR, exist_ok=True)
    author_results = {}
    for variant_name, arms in VARIANTS.items():
        print(f"\n{'=' * 70}\n=== Variant '{variant_name}' (arms={sorted(arms) or ['(none)']}) "
              f"- author '{author}' ===\n{'=' * 70}")
        test_metrics, test_true, test_pred = train_variant(
            variant_name, arms, author, train_features, val_features, test_features,
            ner_vocab_size, srl_vocab_size, bertopic_vec_size, sbert_dim,
        )

        n = len(test_true)
        correct = sum(1 for t, p in zip(test_true, test_pred) if t == p)
        recall_true_narrative = correct / n if n else 0.0
        pct_right_wing = sum(1 for p in test_pred if p == RIGHT_WING_IDX) / n if n else 0.0

        cm_path = os.path.join(REPORT_DIR, f"confusion_matrix_{variant_name}_{author}_test.csv")
        save_confusion_matrix_csv(test_metrics, cm_path)

        author_results[variant_name] = {
            "accuracy": test_metrics["accuracy"],
            "macro_precision": test_metrics["macro_precision"],
            "macro_recall": test_metrics["macro_recall"],
            "macro_f1": test_metrics["macro_f1"],
            "recall_true_narrative": recall_true_narrative,
            "pct_misclassified_right_wing": pct_right_wing,
            "n_test": n,
            "confusion_matrix_csv": cm_path,
        }
        print(f"[{variant_name}/{author}] TEST: accuracy={test_metrics['accuracy'] * 100:.1f}% | "
              f"recall(true narrative)={recall_true_narrative * 100:.1f}% | "
              f"%->Right-wing={pct_right_wing * 100:.1f}% | macro_f1={test_metrics['macro_f1']:.4f}")

    all_results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    all_results[author] = author_results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved results for author '{author}' to '{RESULTS_FILE}'.")
    return author_results


def aggregate():
    """Prints (and saves) a variant x author table plus a 3-author average per variant -
    run after all 3 --author runs have completed."""
    if not os.path.exists(RESULTS_FILE):
        raise FileNotFoundError(f"'{RESULTS_FILE}' not found - run --author for all 3 authors first.")
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    missing = [a for a in AUTHORS if a not in all_results]
    if missing:
        print(f"[!] WARNING: results missing for author(s) {missing} - averages below are "
              f"partial/incomplete until all 3 authors have been run.")

    rows = []
    for variant_name in VARIANTS:
        per_author = {}
        for author in AUTHORS:
            if author in all_results and variant_name in all_results[author]:
                per_author[author] = all_results[author][variant_name]
        if not per_author:
            continue
        avg_recall = float(np.mean([v["recall_true_narrative"] for v in per_author.values()]))
        avg_rw_pct = float(np.mean([v["pct_misclassified_right_wing"] for v in per_author.values()]))
        avg_macro_f1 = float(np.mean([v["macro_f1"] for v in per_author.values()]))
        row = {"variant": variant_name, "avg_recall_true_narrative": avg_recall,
               "avg_pct_right_wing": avg_rw_pct, "avg_macro_f1": avg_macro_f1}
        for author in AUTHORS:
            if author in per_author:
                row[f"{author}_recall"] = per_author[author]["recall_true_narrative"]
                row[f"{author}_pct_right_wing"] = per_author[author]["pct_misclassified_right_wing"]
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("avg_recall_true_narrative", ascending=False)
    print("\n" + "=" * 100)
    print("ABLATION SUMMARY (sorted by avg recall of the true/held-out-author narrative, "
          "descending):")
    print("=" * 100)
    print(df.to_string(index=False))

    summary_path = os.path.join(REPORT_DIR, "ablation_summary.csv")
    df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved summary table to '{summary_path}'.")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Feature ablation for Narrative Classification on unseen (LOAO) authors."
    )
    parser.add_argument("--author", choices=AUTHORS, default=None,
                         help="Run extraction (if needed) + train/evaluate all 7 variants "
                              "for this held-out author.")
    parser.add_argument("--aggregate", action="store_true",
                         help="Aggregate results across all 3 authors into a summary table "
                              "(run after all 3 --author runs have completed).")
    args = parser.parse_args()

    if args.aggregate:
        aggregate()
    elif args.author:
        run_author(args.author)
    else:
        parser.error("Specify --author <IDF|MariaZakharova|BernieSanders> or --aggregate.")

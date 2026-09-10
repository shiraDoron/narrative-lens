"""
Narrative Classification — Topic Feature Representation Comparison
====================================================================

Central question: does using a *distribution* over several Topics improve Narrative
classification compared to a single hard Topic id? A fully separate, controlled 4-way
comparison, independent of the existing baseline_fusion/sbert_only/hybrid comparison in
train.py/fusion.py - nothing in those files, their checkpoints, or their cache files is
touched or overwritten by this script.

The 4 configurations compared (identical data/splits/seed/training loop - only the "Topics"
arm differs):
  1. "none" - Baseline, NO topic feature at all (the Topics arm of the fusion network always
              receives a zero vector, i.e. contributes nothing - the cleanest way to represent
              "no topic feature" while keeping the exact same architecture/parameter shapes
              as the other 3 configs, so the comparison isn't confounded by an architecture
              change).
  2. "hard"  - BERTopic Hard: a single hard topic_id (`.transform()`), exactly the same
              mechanism as production's TopicStanceLayer (stance.py) - a one-hot vector fed
              through a learned embedding-style table.
  3. "soft"  - BERTopic Soft: the top-5 topics from `.approximate_distribution()`
              (BERTopic's existing soft/multi-topic scoring, already implemented but UNUSED in
              production - see stance.py's `get_topic_distribution`), re-normalized to sum to
              1.0, fed as a score-weighted sum over the SAME kind of learned table (i.e. Soft
              is the natural generalization of Hard: instead of picking exactly one row of the
              table, take a weighted combination of up to 5 rows).
  4. "lda"   - LDA document-topic distribution: the FULL K=50 distribution from the already-
              fitted Experiment E baseline (`models/experiments/lda_baseline/lda_k50_seed42`),
              fed the same way (score-weighted sum over the K=50 rows of its own table).

Why a single embedding-table-weighted-sum design for Hard/Soft/LDA (design decision, requested
by the user before writing code): it keeps the "Topics arm" architecture (and therefore its
parameter count / expressive power *per active topic*) identical in kind across all 3 non-
baseline configs - literally the same class (`TopicFeatureLayer`), same uniform(0,1) init
convention as production's `TopicStanceLayer`, same `NUM_NARRATIVES`-sized output. Hard is
mathematically the special case of Soft/LDA with a single weight of 1.0. This isolates
"single id vs. distribution" as the one true independent variable, rather than comparing
architecturally different mechanisms.

Fairness / controlled-comparison methodology:
  - Same data: `train.load_raw_data()` (unmodified, imported), the SAME 4 concatenated
    datasets, same `random_state=42` shuffle.
  - Same split: `train.split_random()` (unmodified, imported) - identical train/val/test row
    membership across all 4 configs x all seeds (verified once via cached-label alignment
    check in `build_full_feature_cache()`).
  - Same NER/SRL/Emotion/Reliability features: reused BY POSITION from the existing
    `data/cache/cached_features_hybrid.pt` (baseline_fusion's own cache) - verified to align
    perfectly (see `build_full_feature_cache()`), which means the NER/SRL/Emotion/Reliability
    processing pipeline is not just "the same code", it is *the exact same already-computed
    values*, with zero re-extraction randomness/drift possible. This cache is READ-ONLY here
    and is never modified.
  - Same fusion architecture: `fusion.NarrativeFusionNetwork` imported unmodified (linear
    weighted-sum of 4 modules + reliability multiplier).
  - Same training loop/hyperparameters: identical to train.py's `train()` (Adam, NLLLoss,
    gradient-accumulation over `BATCH_SIZE`, early stopping on Val Macro-F1 with patience=3,
    `EPOCHS`/`LEARNING_RATE` from config.py).
  - Only the Topics arm (representation + its own small table) varies between configs.
  - `torch.manual_seed(seed)` fixes model-init/dropout randomness (the split is already fixed
    independently of `seed` via `random_state=42` inside load_raw_data/split_random - `seed`
    here ONLY controls training randomness, so multi-seed runs are a pure training-variance
    check, not a data-leakage risk).
  - Every (config, seed) gets its own checkpoint
    (`models/experiments/narrative_topic_compare/{mode}_seed{seed}.pth`) and result entry;
    nothing under `models/best_*.pth` or `reports/tables/model_comparison_results.json` is ever
    touched. Re-running an existing (mode, seed) is refused (existing checkpoints are never
    silently overwritten) - delete the specific file manually first if a genuine re-run is
    wanted.

Known, inherited limitation (not introduced by this experiment): both the BERTopic model
(`soft_v2_baseline_seeded`) and the LDA model (`lda_k50_seed42`) were originally fit on a
corpus that overlaps with this experiment's "random"-split train/val/test rows (the same
accepted limitation already documented in train.py for split_mode="random" - only
leave_one_topic mode actively avoids this). This experiment does not re-fit either topic
model - it only *reuses* them as fixed, frozen feature extractors, exactly like production's
TopicAnalysisPipeline already does.

Run (from repo root): python experiments/feature_ablation/narrative_topic_compare.py
"""
import json
import os

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from tqdm import tqdm

from bertopic import BERTopic
from gensim.corpora import Dictionary
from gensim.models import LdaModel

# Moved out of src/ into experiments/ - add src/ and sibling experiment folders to sys.path so
# same-style flat imports (e.g. `from train import ...`) keep working unmodified.
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _rel_dir in ("src", "experiments/topic_modeling", "experiments/feature_ablation", "experiments/author_generalization"):
    _abs_dir = os.path.join(_REPO_ROOT, _rel_dir)
    if _abs_dir not in sys.path:
        sys.path.insert(0, _abs_dir)

from config import NARRATIVES, NUM_NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from train import load_raw_data, split_random
from topic_preprocessing import clean_text_for_topic_model
from experiment_e_lda_baseline import tokenize as lda_tokenize

from ner import NarrativeEntityLayer
from srl import SRLNarrativeLayer
from emotion import EmotionAgencyLayer
from reliability import ReliabilityLayer
from fusion import NarrativeFusionNetwork

# ---------------------------------------------------------------------------------------
# Paths - all new, none overlap with any existing cache/checkpoint/results file.
# ---------------------------------------------------------------------------------------
EXISTING_HYBRID_CACHE = "data/cache/cached_features_hybrid.pt"   # read-only reuse
SHARED_VOCAB_FILE = "data/cache/shared_vocab.json"               # read-only reuse

NEW_CACHE_FILE = "data/cache/cached_features_narrative_topic_compare.pt"
CHECKPOINT_DIR = "models/experiments/narrative_topic_compare"
REPORT_DIR = "reports/results/narrative_topic_compare"
RESULTS_FILE = f"{REPORT_DIR}/results.json"

BERTOPIC_MODEL_PATH = "models/experiments/soft_v2_baseline_seeded"
BERTOPIC_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LDA_MODEL_PATH = "models/experiments/lda_baseline/lda_k50_seed42"
LDA_DICT_PATH = "models/experiments/lda_baseline/dictionary.gensim"

TOPIC_MODES = ("none", "hard", "soft", "lda")
SOFT_TOP_N = 5
SEEDS = (42, 7, 123)

INDEX_TO_LABEL = {i: n for i, n in enumerate(NARRATIVES)}


# =========================================================================================
# Feature cache: reuse existing NER/SRL/Emotion/Reliability + compute fresh topic features
# =========================================================================================
def build_topic_dense_vectors(texts, bertopic_model, lda_model, lda_dictionary, num_bertopic_topics):
    """Batched BERTopic hard+soft computation, looped (cheap) LDA computation, per text."""
    oov_idx = num_bertopic_topics
    vec_size_bt = num_bertopic_topics + 1

    cleaned_texts = [clean_text_for_topic_model(t) for t in texts]
    # BERTopic can choke on a fully-empty string after cleaning (e.g. a tweet that was only
    # @mentions/URLs) - substitute a harmless placeholder so the batched call doesn't crash;
    # such rows naturally end up in the outlier/-1 bucket (correctly reflected as OOV below).
    safe_texts = [t if t.strip() else "empty" for t in cleaned_texts]

    print(f"  Running BERTopic .transform() on {len(safe_texts)} texts (hard topic ids)...")
    hard_topics, _ = bertopic_model.transform(safe_texts)

    print(f"  Running BERTopic .approximate_distribution() on {len(safe_texts)} texts (soft distribution)...")
    soft_dists, _ = bertopic_model.approximate_distribution(safe_texts)

    hard_dense_list = []
    soft_dense_list = []
    for i in range(len(texts)):
        hard_vec = np.zeros(vec_size_bt, dtype=np.float32)
        tid = int(hard_topics[i])
        idx = oov_idx if (tid < 0 or tid >= num_bertopic_topics) else tid
        hard_vec[idx] = 1.0
        hard_dense_list.append(hard_vec)

        scores = soft_dists[i]
        nonzero_idx = [j for j, s in enumerate(scores) if s > 0]
        soft_vec = np.zeros(vec_size_bt, dtype=np.float32)
        if nonzero_idx:
            nonzero_idx.sort(key=lambda j: scores[j], reverse=True)
            top_idx = nonzero_idx[:SOFT_TOP_N]
            total = float(sum(scores[j] for j in top_idx))
            if total > 0:
                for j in top_idx:
                    idx = oov_idx if (j < 0 or j >= num_bertopic_topics) else j
                    soft_vec[idx] += float(scores[j]) / total
        soft_dense_list.append(soft_vec)

    print(f"  Computing LDA document-topic distributions for {len(texts)} texts...")
    num_lda_topics = lda_model.num_topics
    lda_dense_list = []
    for t in tqdm(cleaned_texts, desc="  LDA distribution"):
        bow = lda_dictionary.doc2bow(lda_tokenize(t))
        dist = lda_model.get_document_topics(bow, minimum_probability=0.0)
        vec = np.zeros(num_lda_topics, dtype=np.float32)
        for tid, prob in dist:
            vec[tid] = prob
        lda_dense_list.append(vec)

    return hard_dense_list, soft_dense_list, lda_dense_list


def build_full_feature_cache():
    """Builds (or loads, if already built) a single combined feature cache shared by all 4
    configs: NER/SRL/Emotion/Reliability reused BY POSITION from the existing baseline_fusion
    cache (verified aligned via labels), + freshly-computed hard/soft/lda topic dense vectors.
    """
    if os.path.exists(NEW_CACHE_FILE):
        print(f"Found existing combined feature cache at '{NEW_CACHE_FILE}'. Loading...")
        return torch.load(NEW_CACHE_FILE, weights_only=False)

    print("Reconstructing the SAME train/val/test split as train.py "
          "(train.load_raw_data() + train.split_random(), unmodified, imported directly)...")
    df = load_raw_data()
    train_data, val_data, test_data = split_random(df)
    for split_df in (train_data, val_data, test_data):
        split_df["text"] = split_df["text"].astype(str).str.slice(0, 3000)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    print(f"Loading existing baseline_fusion cache '{EXISTING_HYBRID_CACHE}' to reuse its "
          f"NER/SRL/Emotion/Reliability features (read-only)...")
    existing_cache = torch.load(EXISTING_HYBRID_CACHE, weights_only=False)

    print("Verifying positional alignment (by label sequence) before trusting reuse...")
    for name, split_df in splits.items():
        cached_labels = [label for _, label in existing_cache[name]]
        fresh_labels = split_df["label"].astype(int).tolist()
        if cached_labels != fresh_labels:
            raise RuntimeError(
                f"Alignment check FAILED for split '{name}': the existing "
                f"'{EXISTING_HYBRID_CACHE}' no longer matches a fresh "
                f"load_raw_data()+split_random() reconstruction (raw CSVs must have changed "
                f"since that cache was built). Refusing to silently reuse misaligned features."
            )
        if len(cached_labels) != len(split_df):
            raise RuntimeError(f"Alignment check FAILED for split '{name}': length mismatch.")
    print("Alignment verified for train/val/test: safe to reuse NER/SRL/Emotion/Reliability by position.")

    print(f"Loading BERTopic model from '{BERTOPIC_MODEL_PATH}'...")
    bertopic_model = BERTopic.load(BERTOPIC_MODEL_PATH, embedding_model=BERTOPIC_EMBEDDING_MODEL_NAME)
    num_bertopic_topics = len([t for t in bertopic_model.get_topics().keys() if t != -1])
    print(f"  -> {num_bertopic_topics} real topics (+1 reserved OOV/outlier slot).")

    print(f"Loading LDA model from '{LDA_MODEL_PATH}'...")
    lda_model = LdaModel.load(LDA_MODEL_PATH)
    lda_dictionary = Dictionary.load(LDA_DICT_PATH)
    print(f"  -> K={lda_model.num_topics} LDA topics.")

    result = {}
    for name, split_df in splits.items():
        print(f"\n=== Building topic features for split '{name}' ({len(split_df)} rows) ===")
        texts = split_df["text"].tolist()
        labels = split_df["label"].astype(int).tolist()
        hard_dense, soft_dense, lda_dense = build_topic_dense_vectors(
            texts, bertopic_model, lda_model, lda_dictionary, num_bertopic_topics
        )
        rows = []
        for i in range(len(texts)):
            base_features, _ = existing_cache[name][i]
            combined = {
                "ner": base_features["ner"],
                "srl": base_features["srl"],
                "emotion": base_features["emotion"],
                "reliability": base_features["reliability"],
                "hard_dense": torch.from_numpy(hard_dense[i]),
                "soft_dense": torch.from_numpy(soft_dense[i]),
                "lda_dense": torch.from_numpy(lda_dense[i]),
            }
            rows.append((combined, labels[i]))
        result[name] = rows

    result["_meta"] = {
        "num_bertopic_topics": num_bertopic_topics,
        "bertopic_vec_size": num_bertopic_topics + 1,
        "num_lda_topics": lda_model.num_topics,
        "soft_top_n": SOFT_TOP_N,
        "bertopic_model_path": BERTOPIC_MODEL_PATH,
        "lda_model_path": LDA_MODEL_PATH,
    }

    os.makedirs(os.path.dirname(NEW_CACHE_FILE), exist_ok=True)
    torch.save(result, NEW_CACHE_FILE)
    print(f"\nSaved new combined feature cache to '{NEW_CACHE_FILE}'.")
    return result


# =========================================================================================
# Model: same architecture as fusion.py's NarrativeDetector, generalized Topics arm
# =========================================================================================
class TopicFeatureLayer(nn.Module):
    """See module docstring for the design rationale. mode="none" carries zero learnable
    parameters (a true "no topic feature" baseline); mode in {"hard","soft","lda"} is a
    uniform(0,1)-initialized [vec_size, NUM_NARRATIVES] table (same init convention as
    production's TopicStanceLayer), consumed via `dense_vec @ table` (a score-weighted sum
    over the table's rows - Hard is the one-hot special case of this)."""

    def __init__(self, mode, vec_size=None):
        super().__init__()
        assert mode in TOPIC_MODES
        self.mode = mode
        if mode == "none":
            self.table = None
        else:
            assert vec_size is not None
            self.table = nn.Embedding(vec_size, NUM_NARRATIVES)
            nn.init.uniform_(self.table.weight, 0, 1)

    def forward(self, dense_vec):
        if self.mode == "none":
            return torch.zeros(1, NUM_NARRATIVES)
        return dense_vec.unsqueeze(0) @ self.table.weight


class TopicAblationDetector(nn.Module):
    """Same architecture/weights-elsewhere as fusion.NarrativeDetector (linear weighted
    fusion of NER/Topics/SRL/Emotion + reliability multiplier, via the unmodified
    `fusion.NarrativeFusionNetwork`) - only the Topics arm's representation differs by mode."""

    DENSE_KEY = {"hard": "hard_dense", "soft": "soft_dense", "lda": "lda_dense"}

    def __init__(self, mode, ner_vocab, srl_vocab, bertopic_vec_size, lda_vec_size):
        super().__init__()
        self.mode = mode
        self.ner_layer = NarrativeEntityLayer(ner_vocab)
        self.srl_layer = SRLNarrativeLayer(srl_vocab)
        self.emotion_layer = EmotionAgencyLayer()
        self.reliability_layer = ReliabilityLayer()
        self.fusion_network = NarrativeFusionNetwork()

        if mode in ("hard", "soft"):
            self.topic_layer = TopicFeatureLayer(mode, vec_size=bertopic_vec_size)
        elif mode == "lda":
            self.topic_layer = TopicFeatureLayer(mode, vec_size=lda_vec_size)
        else:
            self.topic_layer = TopicFeatureLayer("none")

    def classify_features(self, features):
        vec_ner = self.ner_layer(features["ner"])
        vec_srl = self.srl_layer(features["srl"])
        emotion_idx, agency_flag = features["emotion"]
        vec_emotion = self.emotion_layer(emotion_idx, agency_flag)

        if self.mode == "none":
            vec_topics = self.topic_layer(None)
        else:
            vec_topics = self.topic_layer(features[self.DENSE_KEY[self.mode]])

        weight_factor = self.reliability_layer(features["reliability"])
        return self.fusion_network(vec_ner, vec_topics, vec_srl, vec_emotion, weight_factor)


# =========================================================================================
# Metrics / evaluation (same methodology as train.py, extended with weighted P/R/F1)
# =========================================================================================
def compute_metrics(true_labels, predicted_labels):
    accuracy = accuracy_score(true_labels, predicted_labels)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        true_labels, predicted_labels, average="macro", zero_division=0
    )
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        true_labels, predicted_labels, average="weighted", zero_division=0
    )

    labels_present = sorted(set(true_labels) | set(predicted_labels))
    per_p, per_r, per_f1, per_support = precision_recall_fscore_support(
        true_labels, predicted_labels, labels=labels_present, zero_division=0
    )
    per_class = {
        INDEX_TO_LABEL[l]: {
            "precision": float(per_p[i]), "recall": float(per_r[i]),
            "f1": float(per_f1[i]), "support": int(per_support[i]),
        }
        for i, l in enumerate(labels_present)
    }
    cm = confusion_matrix(true_labels, predicted_labels, labels=labels_present).tolist()
    cm_labels = [INDEX_TO_LABEL[l] for l in labels_present]

    return {
        "accuracy": float(accuracy),
        "macro_precision": float(macro_p), "macro_recall": float(macro_r), "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_p), "weighted_recall": float(weighted_r),
        "weighted_f1": float(weighted_f1),
        "per_class": per_class,
        "confusion_matrix": cm, "confusion_matrix_labels": cm_labels,
    }


def evaluate(detector, features_labels, loss_fn=None):
    detector.eval()
    true_labels, predicted_labels = [], []
    total_loss = 0.0
    with torch.no_grad():
        for features, label_idx in features_labels:
            label = torch.tensor([label_idx], dtype=torch.long)
            probs = detector.classify_features(features)
            if probs.dim() == 1:
                probs = probs.unsqueeze(0)
            predicted = torch.argmax(probs, dim=-1)
            true_labels.append(label_idx)
            predicted_labels.append(predicted.item())
            if loss_fn is not None:
                total_loss += loss_fn(torch.log(probs + 1e-8), label).item()
    metrics = compute_metrics(true_labels, predicted_labels)
    avg_loss = (total_loss / len(features_labels)) if loss_fn is not None else None
    return metrics, avg_loss, true_labels, predicted_labels


def save_confusion_matrix_csv(metrics, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    labels = metrics["confusion_matrix_labels"]
    cm_df = pd.DataFrame(metrics["confusion_matrix"], index=labels, columns=labels)
    cm_df.to_csv(path, encoding="utf-8-sig")


# =========================================================================================
# Training (same loop/hyperparameters as train.py's train())
# =========================================================================================
def train_one_config(mode, seed, train_features, val_features, test_features, ner_vocab, srl_vocab,
                      bertopic_vec_size, lda_vec_size, epochs=EPOCHS, batch_size=BATCH_SIZE,
                      patience=3, lr=LEARNING_RATE):
    print(f"\n{'=' * 70}\nTraining config='{mode}' seed={seed}\n{'=' * 70}")
    torch.manual_seed(seed)

    detector = TopicAblationDetector(mode, ner_vocab, srl_vocab, bertopic_vec_size, lda_vec_size)
    optimizer = optim.Adam(detector.parameters(), lr=lr)
    loss_fn = nn.NLLLoss()

    checkpoint_file = f"{CHECKPOINT_DIR}/{mode}_seed{seed}.pth"
    os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
    if os.path.exists(checkpoint_file):
        raise RuntimeError(
            f"Refusing to overwrite existing checkpoint '{checkpoint_file}'. Delete it "
            f"manually first if a genuine re-run of this exact (mode, seed) is intended."
        )

    best_val_macro_f1 = -1.0
    epochs_no_improve = 0
    best_val_metrics = None

    for epoch in range(epochs):
        detector.train()
        total_train_loss = 0.0
        train_correct = 0
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

        val_metrics, avg_val_loss, _, _ = evaluate(detector, val_features, loss_fn)
        print(f"[{mode}/seed{seed}] Epoch {epoch + 1}: Train Acc: {100 * train_correct / len(train_features):.2f}% | "
              f"Val Loss: {avg_val_loss:.4f} | Val Acc: {val_metrics['accuracy'] * 100:.2f}% | "
              f"Val Macro-F1: {val_metrics['macro_f1']:.4f}")

        if val_metrics["macro_f1"] > best_val_macro_f1:
            best_val_macro_f1 = val_metrics["macro_f1"]
            best_val_metrics = val_metrics
            epochs_no_improve = 0
            torch.save(detector.state_dict(), checkpoint_file)
            print(f">>> New best model saved (Val Macro-F1: {best_val_macro_f1:.4f}) -> '{checkpoint_file}'")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"[!] Early stopping at epoch {epoch + 1}.")
                break

    detector.load_state_dict(torch.load(checkpoint_file))
    test_metrics, _, test_true, test_pred = evaluate(detector, test_features)

    print(f"[{mode}/seed{seed}] FINAL TEST: Acc={test_metrics['accuracy'] * 100:.2f}% "
          f"MacroF1={test_metrics['macro_f1']:.4f} WeightedF1={test_metrics['weighted_f1']:.4f}")

    save_confusion_matrix_csv(test_metrics, f"{REPORT_DIR}/confusion_matrix_{mode}_seed{seed}_test.csv")

    return {
        "val_metrics": best_val_metrics,
        "test_metrics": test_metrics,
        "test_true": test_true,
        "test_pred": test_pred,
    }


# =========================================================================================
# Aggregation across seeds + additional requested analyses
# =========================================================================================
def mean_std(values):
    arr = np.array(values, dtype=np.float64)
    return float(arr.mean()), (float(arr.std(ddof=0)) if len(arr) > 1 else 0.0)


def aggregate_across_seeds(mode_results):
    """mode_results: {seed: {"val_metrics":..., "test_metrics":...}} -> mean/std summary."""
    keys = ["accuracy", "macro_precision", "macro_recall", "macro_f1",
            "weighted_precision", "weighted_recall", "weighted_f1"]
    summary = {}
    for k in keys:
        values = [r["test_metrics"][k] for r in mode_results.values()]
        m, s = mean_std(values)
        summary[k] = {"mean": m, "std": s, "values": values}
    return summary


def multi_topic_benefit_analysis(test_df, soft_dense_list, hard_true_pred, soft_true_pred,
                                  num_bertopic_topics, dominance_threshold=0.7):
    """Does Soft help disproportionately on texts spread across multiple topics?
    "multi-topic" := the top-1 soft score's share of the (already renormalized top-5) soft
    distribution is BELOW dominance_threshold (i.e. no single topic dominates)."""
    is_multi_topic = []
    for vec in soft_dense_list:
        nz = vec[vec > 0]
        if len(nz) == 0:
            is_multi_topic.append(False)
            continue
        dominance = float(nz.max())
        is_multi_topic.append(dominance < dominance_threshold)
    is_multi_topic = np.array(is_multi_topic)

    hard_true, hard_pred = hard_true_pred
    soft_true, soft_pred = soft_true_pred
    hard_correct = np.array([int(t == p) for t, p in zip(hard_true, hard_pred)])
    soft_correct = np.array([int(t == p) for t, p in zip(soft_true, soft_pred)])

    def acc_on(mask, correct):
        return float(correct[mask].mean()) if mask.sum() > 0 else None

    return {
        "dominance_threshold": dominance_threshold,
        "n_multi_topic": int(is_multi_topic.sum()),
        "n_single_dominant": int((~is_multi_topic).sum()),
        "hard_acc_multi_topic": acc_on(is_multi_topic, hard_correct),
        "soft_acc_multi_topic": acc_on(is_multi_topic, soft_correct),
        "hard_acc_single_dominant": acc_on(~is_multi_topic, hard_correct),
        "soft_acc_single_dominant": acc_on(~is_multi_topic, soft_correct),
    }


def per_narrative_deltas(hard_metrics, soft_metrics, lda_metrics):
    deltas = {}
    for narrative in NARRATIVES:
        hard_f1 = hard_metrics["per_class"].get(narrative, {}).get("f1", 0.0)
        soft_f1 = soft_metrics["per_class"].get(narrative, {}).get("f1", 0.0)
        lda_f1 = lda_metrics["per_class"].get(narrative, {}).get("f1", 0.0)
        deltas[narrative] = {
            "hard_f1": hard_f1, "soft_f1": soft_f1, "lda_f1": lda_f1,
            "soft_minus_hard": soft_f1 - hard_f1,
            "lda_minus_soft": lda_f1 - soft_f1,
        }
    return deltas


# =========================================================================================
# Main
# =========================================================================================
def main():
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    with open(SHARED_VOCAB_FILE, "r", encoding="utf-8") as f:
        shared_vocab = json.load(f)

    cache = build_full_feature_cache()
    meta = cache["_meta"]
    bertopic_vec_size = meta["bertopic_vec_size"]
    lda_vec_size = meta["num_lda_topics"]

    all_results = {}
    predictions_store = {}

    for mode in TOPIC_MODES:
        all_results[mode] = {}
        for seed in SEEDS:
            checkpoint_file = f"{CHECKPOINT_DIR}/{mode}_seed{seed}.pth"
            if os.path.exists(checkpoint_file):
                print(f"[skip] checkpoint already exists for {mode}/seed{seed}: "
                      f"'{checkpoint_file}' - delete it manually first to re-run.")
                continue
            run = train_one_config(
                mode, seed, cache["train"], cache["val"], cache["test"],
                shared_vocab, shared_vocab, bertopic_vec_size, lda_vec_size,
            )
            all_results[mode][seed] = {
                "val_metrics": run["val_metrics"],
                "test_metrics": run["test_metrics"],
            }
            predictions_store[(mode, seed)] = (run["test_true"], run["test_pred"])

    # --- aggregate mean/std across seeds per config ---
    aggregated = {}
    for mode in TOPIC_MODES:
        if all_results[mode]:
            aggregated[mode] = aggregate_across_seeds(all_results[mode])

    # --- additional analyses (using seed=42's predictions as the reference run) ---
    extra_analysis = {}
    ref_seed = SEEDS[0]
    if all(((mode, ref_seed) in predictions_store) for mode in ("hard", "soft")):
        soft_dense_list = [features["soft_dense"].numpy() for features, _ in cache["test"]]
        extra_analysis["multi_topic_benefit"] = multi_topic_benefit_analysis(
            None, soft_dense_list,
            predictions_store[("hard", ref_seed)], predictions_store[("soft", ref_seed)],
            meta["num_bertopic_topics"],
        )
    if all(ref_seed in all_results.get(mode, {}) for mode in ("hard", "soft", "lda")):
        extra_analysis["per_narrative_deltas"] = per_narrative_deltas(
            all_results["hard"][ref_seed]["test_metrics"],
            all_results["soft"][ref_seed]["test_metrics"],
            all_results["lda"][ref_seed]["test_metrics"],
        )

    output = {
        "seeds": list(SEEDS),
        "meta": {k: v for k, v in meta.items()},
        "per_seed_results": all_results,
        "aggregated_mean_std": aggregated,
        "extra_analysis": extra_analysis,
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved full results to '{RESULTS_FILE}'.")

    print("\n" + "=" * 70)
    print("SUMMARY (test set, mean +/- std across seeds)")
    print("=" * 70)
    for mode in TOPIC_MODES:
        if mode not in aggregated:
            continue
        a = aggregated[mode]
        print(f"[{mode:5s}] Acc={a['accuracy']['mean']*100:.2f}+/-{a['accuracy']['std']*100:.2f}%  "
              f"MacroF1={a['macro_f1']['mean']:.4f}+/-{a['macro_f1']['std']:.4f}  "
              f"WeightedF1={a['weighted_f1']['mean']:.4f}+/-{a['weighted_f1']['std']:.4f}")


if __name__ == "__main__":
    main()

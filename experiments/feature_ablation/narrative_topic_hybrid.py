"""
Narrative Classification — Hybrid Hard/Soft Topic Representation
====================================================================

Follow-up to `narrative_topic_compare.py` (see EXPERIMENTS.md section 15). That experiment's
headline finding was:
  - Hard Topic (single BERTopic id) gave the BEST overall Narrative-classification performance.
  - Soft Topic (top-5 BERTopic distribution) was WORSE overall, BUT beat Hard specifically on
    the minority (~9% of test rows) of texts whose soft distribution has no single dominant
    topic (the "multi-topic benefit analysis" in that experiment).

This experiment tests the natural follow-up idea: **use Hard when a text has one clearly
dominant Topic, and fall back to Soft only when the text is genuinely multi-topic/ambiguous.**
A rule-based routing decision (NOT a learned gate — no extra trainable parameters), so the
rest of the architecture stays byte-for-byte identical to the Hard/Soft configs already
validated.

--------------------------------------------------------------------------------------------
1) How Hard/Soft are represented in the previous experiment's code (verified before writing
   any of this script, per the user's request):
--------------------------------------------------------------------------------------------
- `narrative_topic_compare.TopicFeatureLayer` is a single `nn.Embedding(vec_size, NUM_NARRATIVES)`
  table (uniform(0,1) init, same convention as production's `TopicStanceLayer`). Its `forward`
  takes ANY dense vector of size `vec_size` and returns `dense_vec @ table.weight` — a
  score-weighted sum over the table's rows.
- Hard's dense vector (`hard_dense`, cached) is a ONE-HOT vector over `bertopic_vec_size =
  num_bertopic_topics + 1` (last index reserved for -1/OOV), built from `BERTopic.transform()`.
- Soft's dense vector (`soft_dense`, cached) lives in the EXACT SAME `bertopic_vec_size`-dim
  space — it is the top-5 `BERTopic.approximate_distribution()` scores, re-normalized to sum to
  1.0, scattered into their corresponding topic indices (all other entries 0).
- Because Hard and Soft already share one common vector space and one common table class, no
  new "mode" is architecturally required for a hybrid: a hybrid representation is simply "pick
  `hard_dense` OR `soft_dense`, per example, by a rule", fed into the SAME `TopicFeatureLayer`
  class used for Hard/Soft (see below — reused directly via `TOPIC_MODES` being extended
  in-process, the original `narrative_topic_compare.py` file is never edited on disk).

--------------------------------------------------------------------------------------------
2) Proposed Hybrid representation (fair — rest of the architecture unchanged):
--------------------------------------------------------------------------------------------
For each example, compute the soft distribution's own "dominance" (either its top-1 score, or
the margin between its top-1 and top-2 scores — both tried, see below). If dominance >=
threshold: feed `hard_dense` (the text has one clear Topic — use the representation that won
overall). Otherwise: feed `soft_dense` (the text is genuinely multi-topic — use the
representation that won on that subset). This is precomputed ONCE per example (deterministic,
label-free — it only looks at the topic distribution, never at the Narrative label) and cached
as a new field `hybrid_dense` (+ a `route_is_hard` bool for analysis). The Topics arm's table
(`TopicFeatureLayer`, `vec_size = bertopic_vec_size`) is otherwise IDENTICAL in class, shape,
and init convention to the Hard/Soft configs. Everything else (NER/SRL/Emotion/Reliability
layers, `fusion.NarrativeFusionNetwork`, training loop/hyperparameters, data/splits/seeds) is
reused completely unmodified from `narrative_topic_compare.py` / `train.py` / `fusion.py`.

--------------------------------------------------------------------------------------------
3) Threshold selection methodology — VALIDATION SET ONLY, no test-set leakage:
--------------------------------------------------------------------------------------------
The threshold is NOT chosen by trying candidate hybrid models and peeking at test accuracy.
Instead:
  a. The already-trained, already-validated reference `hard_seed42.pth` / `soft_seed42.pth`
     checkpoints (from the previous experiment) are loaded read-only and evaluated ONLY on the
     VALIDATION split, producing per-example Hard/Soft predictions (no new training needed for
     this step — cheap, a single forward pass over ~2,476 val rows per model).
  b. For a grid of candidate (criterion, threshold) pairs — criterion in {"top1_score",
     "margin"} (top1 = the soft distribution's own top score; margin = top1 − top2) — a
     SIMULATED hybrid prediction is built on VAL: `hard_pred[i]` if dominant-enough, else
     `soft_pred[i]`. Val Macro-F1 of this simulated prediction is computed for every candidate.
  c. The (criterion, threshold) that maximizes VAL Macro-F1 is selected and frozen. The full
     candidate table + the chosen pick are saved to
     `reports/results/narrative_topic_hybrid/threshold_selection.json` for transparency.
  d. This chosen, FIXED rule is then applied identically (and blindly — it needs no labels at
     application time, only the already-computed `soft_dense`) to the train/val/test splits to
     build `hybrid_dense`. The test set is never touched, in any way, during threshold
     selection — only used afterward, exactly once, for final reporting. This directly
     satisfies "no data leakage in threshold selection".

--------------------------------------------------------------------------------------------
Fairness / controlled comparison (mirrors narrative_topic_compare.py's methodology exactly):
--------------------------------------------------------------------------------------------
  - Same data/split: reuses `data/cache/cached_features_narrative_topic_compare.pt` (built by
    the previous experiment via `train.load_raw_data()` + `train.split_random()`) read-only —
    same NER/SRL/Emotion/Reliability values, same hard_dense/soft_dense per row.
  - Same fusion architecture, same training loop/hyperparameters (Adam, NLLLoss, gradient
    accumulation over BATCH_SIZE, early stopping patience=3 on Val Macro-F1, EPOCHS/LEARNING_RATE
    from config.py), same 3 seeds (42, 7, 123).
  - New, fully separate artifacts: `data/cache/cached_features_narrative_topic_hybrid.pt` (new
    cache — extends the old one with `hybrid_dense`/`route_is_hard`, old cache untouched),
    `models/experiments/narrative_topic_hybrid/hybrid_seed{seed}.pth` (new checkpoints, refuses
    to overwrite if already present), `reports/results/narrative_topic_hybrid/` (new report dir).
    Nothing under `models/experiments/narrative_topic_compare/`,
    `data/cache/cached_features_narrative_topic_compare.pt`, or
    `reports/results/narrative_topic_compare/results.json` is ever written to — read-only reuse only.

Run (from repo root): python experiments/feature_ablation/narrative_topic_hybrid.py
"""
import json
import os

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Moved out of src/ into experiments/ - add src/ and sibling experiment folders to sys.path so
# same-style flat imports (e.g. `from config import ...`) keep working unmodified.
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _rel_dir in ("src", "experiments/topic_modeling", "experiments/feature_ablation", "experiments/author_generalization"):
    _abs_dir = os.path.join(_REPO_ROOT, _rel_dir)
    if _abs_dir not in sys.path:
        sys.path.insert(0, _abs_dir)

from config import EPOCHS, BATCH_SIZE, LEARNING_RATE

from ner import NarrativeEntityLayer
from srl import SRLNarrativeLayer
from emotion import EmotionAgencyLayer
from reliability import ReliabilityLayer
from fusion import NarrativeFusionNetwork

import narrative_topic_compare as ntc

# Extend (in-process only — the original narrative_topic_compare.py file on disk is never
# edited) the set of modes TopicFeatureLayer's assertion accepts, so we can directly reuse that
# exact class (same table shape/init/consumption) for the Hybrid representation too.
ntc.TOPIC_MODES = ntc.TOPIC_MODES + ("hybrid",)

# ---------------------------------------------------------------------------------------
# Paths: OLD_* are read-only reuse of the previous experiment's artifacts. Everything this
# script WRITES lives under new, separate paths.
# ---------------------------------------------------------------------------------------
OLD_CACHE_FILE = ntc.NEW_CACHE_FILE                       # cached_features_narrative_topic_compare.pt (read-only)
OLD_CHECKPOINT_DIR = ntc.CHECKPOINT_DIR                   # models/experiments/narrative_topic_compare (read-only)
OLD_RESULTS_FILE = ntc.RESULTS_FILE                       # reports/results/narrative_topic_compare/results.json (read-only)
SHARED_VOCAB_FILE = ntc.SHARED_VOCAB_FILE                 # data/cache/shared_vocab.json (read-only)

NEW_CACHE_FILE = "data/cache/cached_features_narrative_topic_hybrid.pt"
CHECKPOINT_DIR = "models/experiments/narrative_topic_hybrid"
REPORT_DIR = "reports/results/narrative_topic_hybrid"
RESULTS_FILE = f"{REPORT_DIR}/results.json"
THRESHOLD_FILE = f"{REPORT_DIR}/threshold_selection.json"

REF_SEED = 42          # matches the reference seed convention used by narrative_topic_compare.py
SEEDS = ntc.SEEDS       # (42, 7, 123) — identical seeds for a fair cross-experiment comparison

TOP1_THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
MARGIN_THRESHOLDS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]


# =========================================================================================
# Dominance / margin metrics (derived purely from the soft distribution itself, label-free)
# =========================================================================================
def compute_dominance_and_margin(dense_vecs):
    """top1 = the soft distribution's own highest score; margin = top1 - top2 (0 if there is
    no second nonzero topic). Both are computed straight from `soft_dense`, never from labels
    or from any trained classifier's confidence — this is what makes the resulting routing
    rule label-free/leakage-free once chosen."""
    top1_scores = np.zeros(len(dense_vecs), dtype=np.float64)
    margins = np.zeros(len(dense_vecs), dtype=np.float64)
    for i, vec in enumerate(dense_vecs):
        sorted_desc = np.sort(np.asarray(vec, dtype=np.float64))[::-1]
        top1_scores[i] = sorted_desc[0]
        margins[i] = sorted_desc[0] - (sorted_desc[1] if len(sorted_desc) > 1 else 0.0)
    return top1_scores, margins


def sweep_thresholds(val_true, val_hard_pred, val_soft_pred, val_top1, val_margin):
    """Simulates a hybrid prediction on VAL ONLY for every candidate (criterion, threshold),
    by swapping in the already-trained reference Hard/Soft models' own VAL predictions per the
    routing rule (no new model is trained for this search — cheap and leakage-free: only val
    labels + val predictions of models already frozen/validated are used)."""
    candidates = []
    for criterion, thresholds, metric_values in (
        ("top1_score", TOP1_THRESHOLDS, val_top1),
        ("margin", MARGIN_THRESHOLDS, val_margin),
    ):
        for tau in thresholds:
            route_is_hard = metric_values >= tau
            sim_pred = [
                val_hard_pred[i] if route_is_hard[i] else val_soft_pred[i]
                for i in range(len(val_true))
            ]
            m = ntc.compute_metrics(val_true, sim_pred)
            candidates.append({
                "criterion": criterion,
                "threshold": tau,
                "val_accuracy": m["accuracy"],
                "val_macro_f1": m["macro_f1"],
                "val_weighted_f1": m["weighted_f1"],
                "pct_routed_hard": float(route_is_hard.mean() * 100),
            })
    best = max(candidates, key=lambda c: c["val_macro_f1"])
    return candidates, best


def load_reference_detector(mode, ner_vocab, srl_vocab, bertopic_vec_size, lda_vec_size, seed=REF_SEED):
    """Loads one of the previous experiment's already-trained checkpoints, read-only, purely
    for generating predictions (never re-trained/modified here)."""
    detector = ntc.TopicAblationDetector(mode, ner_vocab, srl_vocab, bertopic_vec_size, lda_vec_size)
    ckpt_path = f"{OLD_CHECKPOINT_DIR}/{mode}_seed{seed}.pth"
    detector.load_state_dict(torch.load(ckpt_path))
    detector.eval()
    return detector


# =========================================================================================
# Hybrid-extended feature cache (new file — extends, never overwrites, the old cache)
# =========================================================================================
def build_hybrid_cache(base_cache, criterion, threshold):
    if os.path.exists(NEW_CACHE_FILE):
        print(f"Found existing hybrid feature cache at '{NEW_CACHE_FILE}'. Loading...")
        return torch.load(NEW_CACHE_FILE, weights_only=False)

    print(f"Building hybrid_dense using criterion='{criterion}' threshold={threshold} "
          f"(chosen from VAL only, applied blindly/identically to train/val/test)...")
    result = {}
    for split_name in ("train", "val", "test"):
        rows = []
        for features, label in base_cache[split_name]:
            soft_vec = features["soft_dense"].numpy()
            hard_vec = features["hard_dense"].numpy()
            sorted_desc = np.sort(soft_vec.astype(np.float64))[::-1]
            top1 = float(sorted_desc[0])
            margin = float(top1 - (sorted_desc[1] if len(sorted_desc) > 1 else 0.0))
            metric_value = top1 if criterion == "top1_score" else margin
            route_is_hard = bool(metric_value >= threshold)
            hybrid_vec = hard_vec if route_is_hard else soft_vec
            combined = dict(features)
            combined["hybrid_dense"] = torch.from_numpy(hybrid_vec.copy())
            combined["route_is_hard"] = route_is_hard
            rows.append((combined, label))
        result[split_name] = rows

    result["_meta"] = dict(base_cache["_meta"])
    result["_meta"]["hybrid_threshold_criterion"] = criterion
    result["_meta"]["hybrid_threshold_value"] = threshold

    os.makedirs(os.path.dirname(NEW_CACHE_FILE), exist_ok=True)
    torch.save(result, NEW_CACHE_FILE)
    print(f"Saved hybrid-extended feature cache to '{NEW_CACHE_FILE}'.")
    return result


# =========================================================================================
# Model: identical architecture to narrative_topic_compare's Hard/Soft configs; the Topics
# arm's table is `TopicFeatureLayer(mode="hybrid", vec_size=bertopic_vec_size)` — same class,
# same shape, same uniform(0,1) init as Hard/Soft. Only the fed-in dense vector differs
# per-example (the precomputed, routed `hybrid_dense`).
# =========================================================================================
class HybridNarrativeTopicDetector(nn.Module):
    def __init__(self, ner_vocab, srl_vocab, bertopic_vec_size):
        super().__init__()
        self.ner_layer = NarrativeEntityLayer(ner_vocab)
        self.srl_layer = SRLNarrativeLayer(srl_vocab)
        self.emotion_layer = EmotionAgencyLayer()
        self.reliability_layer = ReliabilityLayer()
        self.fusion_network = NarrativeFusionNetwork()
        self.topic_layer = ntc.TopicFeatureLayer("hybrid", vec_size=bertopic_vec_size)

    def classify_features(self, features):
        vec_ner = self.ner_layer(features["ner"])
        vec_srl = self.srl_layer(features["srl"])
        emotion_idx, agency_flag = features["emotion"]
        vec_emotion = self.emotion_layer(emotion_idx, agency_flag)
        vec_topics = self.topic_layer(features["hybrid_dense"])
        weight_factor = self.reliability_layer(features["reliability"])
        return self.fusion_network(vec_ner, vec_topics, vec_srl, vec_emotion, weight_factor)


# =========================================================================================
# Training (identical loop/hyperparameters to narrative_topic_compare.train_one_config)
# =========================================================================================
def train_one_hybrid_config(seed, train_features, val_features, test_features, ner_vocab, srl_vocab,
                             bertopic_vec_size, epochs=EPOCHS, batch_size=BATCH_SIZE,
                             patience=3, lr=LEARNING_RATE):
    print(f"\n{'=' * 70}\nTraining config='hybrid' seed={seed}\n{'=' * 70}")
    torch.manual_seed(seed)

    detector = HybridNarrativeTopicDetector(ner_vocab, srl_vocab, bertopic_vec_size)
    optimizer = optim.Adam(detector.parameters(), lr=lr)
    loss_fn = nn.NLLLoss()

    checkpoint_file = f"{CHECKPOINT_DIR}/hybrid_seed{seed}.pth"
    os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
    if os.path.exists(checkpoint_file):
        raise RuntimeError(
            f"Refusing to overwrite existing checkpoint '{checkpoint_file}'. Delete it "
            f"manually first if a genuine re-run of this exact seed is intended."
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

        val_metrics, avg_val_loss, _, _ = ntc.evaluate(detector, val_features, loss_fn)
        print(f"[hybrid/seed{seed}] Epoch {epoch + 1}: Train Acc: {100 * train_correct / len(train_features):.2f}% | "
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
    test_metrics, _, test_true, test_pred = ntc.evaluate(detector, test_features)

    print(f"[hybrid/seed{seed}] FINAL TEST: Acc={test_metrics['accuracy'] * 100:.2f}% "
          f"MacroF1={test_metrics['macro_f1']:.4f} WeightedF1={test_metrics['weighted_f1']:.4f}")

    ntc.save_confusion_matrix_csv(test_metrics, f"{REPORT_DIR}/confusion_matrix_hybrid_seed{seed}_test.csv")

    return {"val_metrics": best_val_metrics, "test_metrics": test_metrics,
            "test_true": test_true, "test_pred": test_pred}


# =========================================================================================
# Main
# =========================================================================================
def main():
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    with open(SHARED_VOCAB_FILE, "r", encoding="utf-8") as f:
        shared_vocab = json.load(f)

    print(f"Loading existing combined feature cache '{OLD_CACHE_FILE}' (read-only reuse)...")
    base_cache = torch.load(OLD_CACHE_FILE, weights_only=False)
    meta = base_cache["_meta"]
    bertopic_vec_size = meta["bertopic_vec_size"]
    lda_vec_size = meta["num_lda_topics"]

    print(f"Loading reference Hard/Soft models (seed={REF_SEED}) — read-only, for threshold "
          f"selection and subset analysis (never re-trained here)...")
    hard_detector = load_reference_detector("hard", shared_vocab, shared_vocab, bertopic_vec_size, lda_vec_size)
    soft_detector = load_reference_detector("soft", shared_vocab, shared_vocab, bertopic_vec_size, lda_vec_size)

    # ---- Step 1: threshold selection, VAL SET ONLY ----
    if os.path.exists(THRESHOLD_FILE):
        print(f"Found existing threshold selection at '{THRESHOLD_FILE}'. Loading...")
        with open(THRESHOLD_FILE, "r", encoding="utf-8") as f:
            threshold_output = json.load(f)
        best = threshold_output["chosen"]
    else:
        print("Evaluating reference Hard/Soft models on VAL set (threshold selection)...")
        _, _, val_true, val_hard_pred = ntc.evaluate(hard_detector, base_cache["val"])
        _, _, val_true2, val_soft_pred = ntc.evaluate(soft_detector, base_cache["val"])
        assert val_true == val_true2, "VAL label order mismatch between reference model evaluations"

        val_soft_dense = [f["soft_dense"].numpy() for f, _ in base_cache["val"]]
        val_top1, val_margin = compute_dominance_and_margin(val_soft_dense)

        candidates, best = sweep_thresholds(val_true, val_hard_pred, val_soft_pred, val_top1, val_margin)
        threshold_output = {
            "note": "Threshold chosen using ONLY the validation set: val labels + VAL-set "
                    "predictions of the already-trained reference hard_seed42/soft_seed42 "
                    "models. The test set is never accessed during this selection step.",
            "reference_seed": REF_SEED,
            "candidates": candidates,
            "chosen": best,
        }
        with open(THRESHOLD_FILE, "w", encoding="utf-8") as f:
            json.dump(threshold_output, f, ensure_ascii=False, indent=2)
        print(f"Chosen threshold: criterion={best['criterion']} threshold={best['threshold']} "
              f"(val macro-F1={best['val_macro_f1']:.4f}, {best['pct_routed_hard']:.1f}% "
              f"routed to Hard on VAL)")

    chosen_criterion = best["criterion"]
    chosen_threshold = best["threshold"]

    # ---- Step 2: build the hybrid-extended cache using the CHOSEN threshold ----
    cache = build_hybrid_cache(base_cache, chosen_criterion, chosen_threshold)

    # ---- Step 3: reference Hard/Soft predictions on TEST (for the subset analysis only —
    #      these models are NOT retrained; this is purely inference for comparison) ----
    print("Evaluating reference Hard/Soft models on TEST set (subset analysis only)...")
    _, _, test_true_ref, test_hard_pred_ref = ntc.evaluate(hard_detector, base_cache["test"])
    _, _, test_true_ref2, test_soft_pred_ref = ntc.evaluate(soft_detector, base_cache["test"])
    assert test_true_ref == test_true_ref2, "TEST label order mismatch between reference model evaluations"

    # ---- Step 4: train the Hybrid model across the same 3 seeds ----
    all_results = {}
    predictions_store = {}
    for seed in SEEDS:
        checkpoint_file = f"{CHECKPOINT_DIR}/hybrid_seed{seed}.pth"
        if os.path.exists(checkpoint_file):
            print(f"[reload] checkpoint already exists for hybrid/seed{seed}: '{checkpoint_file}' "
              f"— loading it for evaluation instead of retraining.")
            detector = HybridNarrativeTopicDetector(shared_vocab, shared_vocab, bertopic_vec_size)
            detector.load_state_dict(torch.load(checkpoint_file))
            test_metrics, _, test_true, test_pred = ntc.evaluate(detector, cache["test"])
            all_results[seed] = {"val_metrics": None, "test_metrics": test_metrics}
            predictions_store[seed] = (test_true, test_pred)
            continue
        run = train_one_hybrid_config(
            seed, cache["train"], cache["val"], cache["test"], shared_vocab, shared_vocab, bertopic_vec_size
        )
        all_results[seed] = {"val_metrics": run["val_metrics"], "test_metrics": run["test_metrics"]}
        predictions_store[seed] = (run["test_true"], run["test_pred"])

    aggregated_hybrid = ntc.aggregate_across_seeds(all_results)

    # ---- Step 5: subset analysis (single-topic vs. ambiguous), reference seed ----
    route_is_hard_test = np.array([bool(features["route_is_hard"]) for features, _ in cache["test"]])
    hybrid_true, hybrid_pred = predictions_store[REF_SEED]

    def acc_on(mask, true_list, pred_list):
        if mask.sum() == 0:
            return None
        true_arr = np.array(true_list)[mask]
        pred_arr = np.array(pred_list)[mask]
        return float((true_arr == pred_arr).mean())

    subset_analysis = {
        "pct_test_routed_to_soft": float((~route_is_hard_test).mean() * 100),
        "n_single_topic": int(route_is_hard_test.sum()),
        "n_ambiguous": int((~route_is_hard_test).sum()),
        "single_topic_subset": {
            "hard_only_acc": acc_on(route_is_hard_test, test_true_ref, test_hard_pred_ref),
            "soft_only_acc": acc_on(route_is_hard_test, test_true_ref, test_soft_pred_ref),
            "hybrid_acc": acc_on(route_is_hard_test, hybrid_true, hybrid_pred),
        },
        "ambiguous_subset": {
            "hard_only_acc": acc_on(~route_is_hard_test, test_true_ref, test_hard_pred_ref),
            "soft_only_acc": acc_on(~route_is_hard_test, test_true_ref, test_soft_pred_ref),
            "hybrid_acc": acc_on(~route_is_hard_test, hybrid_true, hybrid_pred),
        },
        "overall": {
            "hard_only_acc": float((np.array(test_true_ref) == np.array(test_hard_pred_ref)).mean()),
            "soft_only_acc": float((np.array(test_true_ref) == np.array(test_soft_pred_ref)).mean()),
            "hybrid_acc": float((np.array(hybrid_true) == np.array(hybrid_pred)).mean()),
        },
    }

    # ---- Step 6: pull in none/hard/soft/lda aggregated stats from the previous experiment ----
    with open(OLD_RESULTS_FILE, "r", encoding="utf-8") as f:
        old_results = json.load(f)
    old_aggregated = old_results["aggregated_mean_std"]

    comparison_table = dict(old_aggregated)
    comparison_table["hybrid"] = aggregated_hybrid

    # ---- Step 7: per-narrative comparison (reference seed, consistent with the previous
    #      experiment's per_narrative_deltas convention) ----
    per_narrative_comparison = {}
    for narrative in ntc.NARRATIVES:
        row = {}
        for mode in ("none", "hard", "soft", "lda"):
            pc = old_results["per_seed_results"][mode][str(REF_SEED)]["test_metrics"]["per_class"].get(narrative, {})
            row[mode] = {"precision": pc.get("precision"), "recall": pc.get("recall"), "f1": pc.get("f1")}
        pc_hybrid = all_results[REF_SEED]["test_metrics"]["per_class"].get(narrative, {})
        row["hybrid"] = {"precision": pc_hybrid.get("precision"), "recall": pc_hybrid.get("recall"),
                          "f1": pc_hybrid.get("f1")}
        row["hybrid_minus_hard_f1"] = row["hybrid"]["f1"] - row["hard"]["f1"]
        per_narrative_comparison[narrative] = row

    # ---- Step 8: final verdict vs. the Hard-only baseline ----
    hard_agg = old_aggregated["hard"]
    verdict = {
        "hard_only_accuracy_mean": hard_agg["accuracy"]["mean"],
        "hard_only_macro_f1_mean": hard_agg["macro_f1"]["mean"],
        "hybrid_accuracy_mean": aggregated_hybrid["accuracy"]["mean"],
        "hybrid_macro_f1_mean": aggregated_hybrid["macro_f1"]["mean"],
        "hybrid_beats_hard_accuracy": aggregated_hybrid["accuracy"]["mean"] > hard_agg["accuracy"]["mean"],
        "hybrid_beats_hard_macro_f1": aggregated_hybrid["macro_f1"]["mean"] > hard_agg["macro_f1"]["mean"],
        "accuracy_delta_pp": (aggregated_hybrid["accuracy"]["mean"] - hard_agg["accuracy"]["mean"]) * 100,
        "macro_f1_delta": aggregated_hybrid["macro_f1"]["mean"] - hard_agg["macro_f1"]["mean"],
    }

    output = {
        "seeds": list(SEEDS),
        "reference_seed": REF_SEED,
        "chosen_threshold": {"criterion": chosen_criterion, "threshold": chosen_threshold},
        "per_seed_results": {str(seed): all_results[seed] for seed in SEEDS},
        "aggregated_mean_std_hybrid": aggregated_hybrid,
        "comparison_table_mean_std": comparison_table,
        "per_narrative_comparison": per_narrative_comparison,
        "subset_analysis": subset_analysis,
        "final_verdict": verdict,
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved full results to '{RESULTS_FILE}'.")

    print("\n" + "=" * 70)
    print("SUMMARY (test set, mean +/- std across seeds)")
    print("=" * 70)
    for mode in ("none", "hard", "soft", "lda", "hybrid"):
        a = comparison_table[mode]
        print(f"[{mode:6s}] Acc={a['accuracy']['mean']*100:.2f}+/-{a['accuracy']['std']*100:.2f}%  "
              f"MacroF1={a['macro_f1']['mean']:.4f}+/-{a['macro_f1']['std']:.4f}  "
              f"WeightedF1={a['weighted_f1']['mean']:.4f}+/-{a['weighted_f1']['std']:.4f}")

    print("\nSubset analysis (test set, reference seed={}):".format(REF_SEED))
    print(f"  {subset_analysis['n_ambiguous']} / {subset_analysis['n_ambiguous']+subset_analysis['n_single_topic']} "
          f"({subset_analysis['pct_test_routed_to_soft']:.1f}%) routed to Soft (ambiguous)")
    print(f"  Ambiguous subset  -> Hard={subset_analysis['ambiguous_subset']['hard_only_acc']}  "
          f"Soft={subset_analysis['ambiguous_subset']['soft_only_acc']}  "
          f"Hybrid={subset_analysis['ambiguous_subset']['hybrid_acc']}")
    print(f"  Single-topic subset -> Hard={subset_analysis['single_topic_subset']['hard_only_acc']}  "
          f"Soft={subset_analysis['single_topic_subset']['soft_only_acc']}  "
          f"Hybrid={subset_analysis['single_topic_subset']['hybrid_acc']}")

    print(f"\nFINAL VERDICT: Hybrid vs. Hard-only baseline (Acc={verdict['hard_only_accuracy_mean']*100:.2f}%, "
          f"MacroF1={verdict['hard_only_macro_f1_mean']:.4f}):")
    print(f"  Hybrid: Acc={verdict['hybrid_accuracy_mean']*100:.2f}%, MacroF1={verdict['hybrid_macro_f1_mean']:.4f}")
    print(f"  Beats Hard on Accuracy: {verdict['hybrid_beats_hard_accuracy']} "
          f"(delta={verdict['accuracy_delta_pp']:+.2f}pp)")
    print(f"  Beats Hard on Macro-F1: {verdict['hybrid_beats_hard_macro_f1']} "
          f"(delta={verdict['macro_f1_delta']:+.4f})")


if __name__ == "__main__":
    main()

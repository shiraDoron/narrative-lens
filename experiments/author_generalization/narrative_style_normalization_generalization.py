"""
Narrative Classification — Style-Normalization Intervention, Part B: Narrative Generalization
================================================================================================
EXPERIMENTS.md Section 28, Part B — does reducing author-specific stylistic/formatting cues
(via `narrative_lens.features.style_normalization.normalize_style()`) improve the narrative
classifier's generalization to UNSEEN authors, without hurting in-distribution (random-split)
performance?

Design (ONE predefined intervention, no sweep, no further tuning after seeing results):
  - Architecture: `AblationDetector(arms=set())` (narrative_ablation_loao.py) = frozen SBERT
    embedding -> MLP only, NO engineered-feature arms. This is EXACTLY the "sbert_original"
    variant already used throughout Sections 19-25, and architecturally identical (by
    construction - same combined_dim formula, same TopicFeatureLayer-free MLP template) to
    `SBERTTopicDetector(mode="none")` used in Section 20's random-split comparison - so results
    trained with either class are directly comparable.
  - "Original" baseline: REUSED AS-IS from two already-completed experiments (zero retraining):
      * random split  -> Section 20's `narrative_topic_sbert_backbone.py` "none" mode results
                         (3 seeds: 42/7/123) - artifacts/experiments/narrative_topic_sbert_backbone/
                         results_random.json.
      * fresh authors -> Section 25's `narrative_fresh_author_confirmatory.py` "sbert_original"
                         variant results, on the SAME 14 frozen fresh authors (2 per narrative,
                         seed=42) - artifacts/experiments/narrative_fresh_author_confirmatory/
                         results.json.
  - "Style-normalized" variant: trained FRESH here, on the SAME splits/seeds (`split_random()`/
    `split_leave_one_author()`, both imported unmodified from train.py - same random_state=42
    baked into those functions - and the SAME 14 frozen authors loaded from the SAME frozen-set
    file), with `normalize_style()` applied to every text (train/val/test alike) before SBERT
    encoding. Same architecture, same EPOCHS/BATCH_SIZE/LEARNING_RATE/patience=3 early-stopping
    convention, same seed(s) as the reused baselines - text representation is the ONLY variable.

Pre-specified interpretation rules (fixed BEFORE running, applied mechanically to whatever the
numbers turn out to be - see `classify_outcome()` below and EXPERIMENTS.md Section 28):
  1. STRONG EVIDENCE of a real author-identity shortcut: Part A's decisive within-narrative test
     shows author-signal materially reduced after normalization (macro-F1 drop >= 10pp absolute
     in a majority of narratives, or stops beating both baselines in a majority of narratives)
     AND Part B's fresh-author mean AND median true-narrative recall improve by >= 3pp versus the
     reused sbert_original baseline, AND random-split macro-F1 does not degrade by more than 3pp
     (non-inferior in-distribution - normalization isn't just making the model worse everywhere).
  2. WEAK / INCONCLUSIVE EVIDENCE: Part A shows only a partial reduction in author-signal, and/or
     Part B's fresh-author recall improvement is small or mixed (within +/-3pp of baseline, or
     improves on some narratives/authors but not others) - a real effect cannot be confidently
     claimed either way.
  3. INSUFFICIENT INTERVENTION (manipulation check failed): Part A shows author-signal
     essentially UNCHANGED after normalization (macro-F1 drop < 5pp, still beats both baselines
     in most/all narratives) - in this case Part B's numbers are NOT diagnostic of the causal
     question at all (the intervention never achieved style-invariance), and the honest
     conclusion is that THIS normalization was insufficient to remove the author signal, not that
     "narrative generalization doesn't benefit from style-invariance" in general.

Run (from repo root):
    python experiments/author_generalization/narrative_style_normalization_generalization.py --random
    python experiments/author_generalization/narrative_style_normalization_generalization.py --author abualiexpress
    python experiments/author_generalization/narrative_style_normalization_generalization.py --all-authors
    python experiments/author_generalization/narrative_style_normalization_generalization.py --aggregate
"""
import argparse
import json
import os
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer

from narrative_lens.config import NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from narrative_lens.train import (
    load_raw_data, split_random, split_leave_one_author, evaluate, save_confusion_matrix_csv,
)
from narrative_lens.features.style_normalization import normalize_style

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from narrative_ablation_loao import AblationDetector  # noqa: E402

SEED = 42
RANDOM_SPLIT_SEEDS = (42, 7, 123)  # matches Section 20's SEEDS convention exactly
BERTOPIC_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

FROZEN_SET_FILE = "artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json"

# Existing, READ-ONLY reuse sources (never modified by this script) - the "original" baseline.
ORIGINAL_RANDOM_RESULTS_FILE = "artifacts/experiments/narrative_topic_sbert_backbone/results_random.json"
ORIGINAL_FRESH_AUTHOR_RESULTS_FILE = "artifacts/experiments/narrative_fresh_author_confirmatory/results.json"
PART_A_COMPARISON_FILE = "artifacts/experiments/narrative_style_normalization_author_signature/original_vs_normalized_summary.json"
# Per-row original caches (same rows/labels as the reused results above) - used ONLY for the
# sanity checks below (row-count + label-sequence equality against our own normalized caches),
# never loaded for training/features.
ORIGINAL_RANDOM_CACHE_FILE = "data/cache/cached_features_sbert_only.pt"
ORIGINAL_LOAO_CACHE_TEMPLATE = "data/cache/cached_features_fresh_author_confirmatory_{author}.pt"

CACHE_DIR = "data/cache"
RANDOM_CACHE_FILE = os.path.join(CACHE_DIR, "cached_features_style_normalization_random.pt")
LOAO_CACHE_TEMPLATE = os.path.join(CACHE_DIR, "cached_features_style_normalization_loao_{author}.pt")
CHECKPOINT_DIR = "models/experiments/narrative_style_normalization_generalization"
REPORT_DIR = "artifacts/experiments/narrative_style_normalization_generalization"
RESULTS_FILE = os.path.join(REPORT_DIR, "results.json")
RANDOM_SPLIT_COMPARISON_FILE = os.path.join(REPORT_DIR, "random_split_comparison.csv")
FRESH_AUTHOR_COMPARISON_FILE = os.path.join(REPORT_DIR, "fresh_author_comparison.csv")
PER_NARRATIVE_FILE = os.path.join(REPORT_DIR, "per_narrative_aggregation.csv")
FINAL_DECISION_FILE = os.path.join(REPORT_DIR, "final_decision.json")
SANITY_CHECKS_FILE = os.path.join(REPORT_DIR, "sanity_checks.json")

# Pre-specified thresholds (see module docstring) - fixed before any result was seen.
FRESH_AUTHOR_IMPROVEMENT_MARGIN = 0.03   # 3pp
RANDOM_SPLIT_NON_INFERIORITY_MARGIN = 0.03  # 3pp
PART_A_STRONG_DROP_MARGIN = 0.10  # 10pp macro-F1 drop (Experiment B, per-narrative)
PART_A_INSUFFICIENT_DROP_MARGIN = 0.05  # 5pp


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


def safe_torch_save(obj, path, retries=5, delay=1.0):
    """Retries torch.save on transient Windows WinError 32 sharing violations - see
    narrative_fresh_author_confirmatory.py for the same pattern."""
    last_err = None
    for attempt in range(retries):
        try:
            torch.save(obj, path)
            return
        except RuntimeError as e:
            last_err = e
            print(f"[!] torch.save to '{path}' failed (attempt {attempt + 1}/{retries}): {e}. Retrying...")
            time.sleep(delay)
    raise last_err


def load_frozen_authors():
    with open(FROZEN_SET_FILE, "r", encoding="utf-8") as f:
        frozen = json.load(f)
    authors = [a["author_source"] for a in frozen["selected_authors"]]
    return authors, frozen


# =========================================================================================
# Caches: SBERT embeddings of STYLE-NORMALIZED text only (the "original" side is reused
# as-is from existing results/caches - never recomputed here).
# =========================================================================================
def build_or_load_random_cache(sbert_model):
    if os.path.exists(RANDOM_CACHE_FILE):
        print(f"Found existing normalized random-split cache '{RANDOM_CACHE_FILE}'. Loading...")
        return torch.load(RANDOM_CACHE_FILE, weights_only=False)

    print("Building fresh normalized random-split cache (split_random(), same random_state=42 "
          "as train.py/Section 20 - identical rows, only the text representation differs)...")
    df = load_raw_data()
    train_data, val_data, test_data = split_random(df)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    result = {}
    sbert_dim = None
    for name, split_df in splits.items():
        texts = split_df["text"].astype(str).str.slice(0, 3000).tolist()
        normalized_texts = [normalize_style(t) for t in texts]
        labels = split_df["label"].astype(int).tolist()
        print(f"  Split '{name}' ({len(texts)} rows): encoding normalized text with SBERT...")
        embeddings = sbert_model.encode(normalized_texts, convert_to_numpy=True, show_progress_bar=True)
        sbert_dim = int(embeddings.shape[1])
        rows = [({"sbert_embedding": torch.tensor(embeddings[i], dtype=torch.float32)}, labels[i])
                for i in range(len(texts))]
        result[name] = rows

    result["_meta"] = {"sbert_dim": sbert_dim}
    os.makedirs(CACHE_DIR, exist_ok=True)
    torch.save(result, RANDOM_CACHE_FILE)
    print(f"Saved normalized random-split cache to '{RANDOM_CACHE_FILE}'.")
    return result


def build_or_load_loao_cache(author, sbert_model):
    cache_file = LOAO_CACHE_TEMPLATE.format(author=author)
    if os.path.exists(cache_file):
        print(f"Found existing normalized LOAO cache '{cache_file}'. Loading...")
        return torch.load(cache_file, weights_only=False)

    print(f"Building fresh normalized LOAO cache for held-out author '{author}' "
          f"(split_leave_one_author(), same split as Section 25 - identical rows, only the "
          f"text representation differs)...")
    df = load_raw_data()
    train_data, val_data, test_data = split_leave_one_author(df, author)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    result = {}
    sbert_dim = None
    for name, split_df in splits.items():
        texts = split_df["text"].astype(str).str.slice(0, 3000).tolist()
        normalized_texts = [normalize_style(t) for t in texts]
        labels = split_df["label"].astype(int).tolist()
        print(f"  Split '{name}' ({len(texts)} rows): encoding normalized text with SBERT...")
        embeddings = sbert_model.encode(normalized_texts, convert_to_numpy=True, show_progress_bar=True)
        sbert_dim = int(embeddings.shape[1])
        rows = [({"sbert_embedding": torch.tensor(embeddings[i], dtype=torch.float32)}, labels[i])
                for i in range(len(texts))]
        result[name] = rows

    result["_meta"] = {"sbert_dim": sbert_dim}
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_torch_save(result, cache_file)
    print(f"Saved normalized LOAO cache to '{cache_file}'.")
    return result


# =========================================================================================
# Training loop - identical hyperparameters/early-stopping/checkpoint convention as
# Sections 18-25/20's train_variant()/train_one().
# =========================================================================================
def train_one(run_tag, sbert_dim, train_features, val_features, test_features,
              seed, epochs=EPOCHS, batch_size=BATCH_SIZE, patience=3, lr=LEARNING_RATE):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{run_tag}.pth")

    set_seed(seed)
    detector = AblationDetector(set(), ner_vocab_size=1, srl_vocab_size=1,
                                 bertopic_vec_size=1, sbert_dim=sbert_dim)

    if os.path.exists(checkpoint_file):
        print(f"[{run_tag}] Found existing checkpoint - loading for eval only "
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

            val_metrics, avg_val_loss, _, _ = evaluate(detector, val_features, loss_fn)
            print(f"[{run_tag}] Epoch {epoch + 1}: "
                  f"Train Acc {100 * train_correct / len(train_features):.2f}% | "
                  f"Val Loss {avg_val_loss:.4f} | Val Acc {val_metrics['accuracy'] * 100:.2f}% | "
                  f"Val Macro-F1 {val_metrics['macro_f1']:.4f}")

            if val_metrics["macro_f1"] > best_val_macro_f1:
                best_val_macro_f1 = val_metrics["macro_f1"]
                epochs_no_improve = 0
                safe_torch_save(detector.state_dict(), checkpoint_file)
                print(f">>> New best model saved (Val Macro-F1: {best_val_macro_f1:.4f}) -> '{checkpoint_file}'")
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"[{run_tag}] Early stopping at epoch {epoch + 1}.")
                    break

        detector.load_state_dict(torch.load(checkpoint_file))

    test_metrics, _, test_true, test_pred = evaluate(detector, test_features)
    return test_metrics, test_true, test_pred, checkpoint_file


# =========================================================================================
# Orchestration: random split (normalized variant, 3 seeds)
# =========================================================================================
def run_random():
    os.makedirs(REPORT_DIR, exist_ok=True)
    print(f"Loading SBERT model '{BERTOPIC_EMBEDDING_MODEL_NAME}'...")
    sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)
    cache = build_or_load_random_cache(sbert_model)
    sbert_dim = cache["_meta"]["sbert_dim"]

    results = {}
    for seed in RANDOM_SPLIT_SEEDS:
        run_tag = f"random_normalized_seed{seed}"
        print(f"\n{'=' * 70}\n=== style-normalized random split, seed={seed} ===\n{'=' * 70}")
        test_metrics, test_true, test_pred, checkpoint_file = train_one(
            run_tag, sbert_dim, cache["train"], cache["val"], cache["test"], seed=seed,
        )
        cm_path = os.path.join(REPORT_DIR, f"confusion_matrix_random_normalized_seed{seed}_test.csv")
        save_confusion_matrix_csv(test_metrics, cm_path)
        results[str(seed)] = {"test_metrics": test_metrics, "checkpoint": checkpoint_file,
                               "confusion_matrix_csv": cm_path}
        print(f"[seed{seed}] TEST: accuracy={test_metrics['accuracy'] * 100:.2f}% "
              f"macro_f1={test_metrics['macro_f1']:.4f}")

    all_results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    all_results["random_split_normalized"] = {"seeds": list(RANDOM_SPLIT_SEEDS), "results": results}
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved random-split (style-normalized) results to '{RESULTS_FILE}'.")


# =========================================================================================
# Orchestration: fresh-author LOAO (normalized variant, seed=42, one author at a time)
# =========================================================================================
def run_author(author):
    os.makedirs(REPORT_DIR, exist_ok=True)
    print(f"Loading SBERT model '{BERTOPIC_EMBEDDING_MODEL_NAME}'...")
    sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)
    cache = build_or_load_loao_cache(author, sbert_model)
    sbert_dim = cache["_meta"]["sbert_dim"]
    true_narrative_name = NARRATIVES[cache["test"][0][1]]

    run_tag = f"loao_normalized_{author}"
    print(f"\n{'=' * 70}\n=== style-normalized LOAO, author='{author}' "
          f"(true narrative: {true_narrative_name}) ===\n{'=' * 70}")
    test_metrics, test_true, test_pred, checkpoint_file = train_one(
        run_tag, sbert_dim, cache["train"], cache["val"], cache["test"], seed=SEED,
    )

    n = len(test_true)
    correct = sum(1 for t, p in zip(test_true, test_pred) if t == p)
    recall_true_narrative = correct / n if n else 0.0
    wrong_preds = [p for t, p in zip(test_true, test_pred) if p != t]
    dominant_wrong_narrative, dominant_wrong_error_share = None, 0.0
    if wrong_preds:
        dominant_idx, dominant_count = Counter(wrong_preds).most_common(1)[0]
        dominant_wrong_narrative = NARRATIVES[dominant_idx]
        dominant_wrong_error_share = dominant_count / len(wrong_preds)

    cm_path = os.path.join(REPORT_DIR, f"confusion_matrix_loao_normalized_{author}_test.csv")
    save_confusion_matrix_csv(test_metrics, cm_path)

    author_result = {
        "narrative": true_narrative_name,
        "accuracy": test_metrics["accuracy"],
        "macro_precision": test_metrics["macro_precision"],
        "macro_recall": test_metrics["macro_recall"],
        "macro_f1": test_metrics["macro_f1"],
        "recall_true_narrative": recall_true_narrative,
        "dominant_wrong_narrative": dominant_wrong_narrative,
        "dominant_wrong_narrative_error_share": dominant_wrong_error_share,
        "n_test": n,
        "checkpoint": checkpoint_file,
        "confusion_matrix_csv": cm_path,
    }

    all_results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    all_results.setdefault("fresh_author_normalized", {})[author] = author_result
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"[{author}] TEST: recall(true narrative)={recall_true_narrative * 100:.1f}% | "
          f"macro_f1={test_metrics['macro_f1']:.4f}")
    print(f"Saved result for author '{author}' to '{RESULTS_FILE}'.")
    return author_result


def run_all_authors():
    authors, _ = load_frozen_authors()
    for i, author in enumerate(authors):
        print(f"\n\n######## Author {i + 1}/{len(authors)}: '{author}' ########")
        run_author(author)


# =========================================================================================
# Aggregation: Original (reused) vs. Style-normalized (fresh), both halves + final decision.
# =========================================================================================
def classify_outcome(part_a_comparison, fresh_author_mean_delta, fresh_author_median_delta,
                      random_split_macro_f1_delta):
    """Applies the 3 pre-specified interpretation rules (see module docstring) mechanically to
    the actual Part A + Part B numbers. Returns (pattern_name, explanation)."""
    b_narratives = part_a_comparison["experiment_b_by_narrative"]
    n_narratives = len(b_narratives)
    n_strong_drop = sum(1 for r in b_narratives if r["macro_f1_delta"] <= -PART_A_STRONG_DROP_MARGIN)
    n_flips_to_not_beating_baseline = sum(
        1 for r in b_narratives if r["original_beats_baselines"] and not r["normalized_beats_baselines"]
    )
    n_small_drop = sum(1 for r in b_narratives if r["macro_f1_delta"] > -PART_A_INSUFFICIENT_DROP_MARGIN)

    majority = (n_narratives / 2) if n_narratives else 0
    part_a_materially_reduced = (n_strong_drop > majority) or (n_flips_to_not_beating_baseline > majority)
    part_a_essentially_unchanged = n_small_drop >= majority if n_narratives else True

    random_split_non_inferior = random_split_macro_f1_delta >= -RANDOM_SPLIT_NON_INFERIORITY_MARGIN
    fresh_author_improved = (fresh_author_mean_delta >= FRESH_AUTHOR_IMPROVEMENT_MARGIN and
                              fresh_author_median_delta >= FRESH_AUTHOR_IMPROVEMENT_MARGIN)

    if part_a_essentially_unchanged:
        return ("INSUFFICIENT_INTERVENTION",
                "Part A's within-narrative author-signature test shows author-signal "
                "essentially UNCHANGED after style normalization (manipulation check failed) - "
                "Part B's fresh-author numbers are NOT diagnostic of the causal question. This "
                "specific normalization was insufficient to remove the author signal; it does "
                "NOT mean narrative generalization doesn't benefit from style-invariance in "
                "general.")
    if part_a_materially_reduced and fresh_author_improved and random_split_non_inferior:
        return ("STRONG_EVIDENCE",
                "Part A shows author-signal materially reduced in a majority of narratives AND "
                "Part B shows fresh-author recall improved (mean+median >= 3pp) without "
                "degrading random-split performance (>= -3pp macro-F1) - consistent with a real "
                "author-identity shortcut that style normalization partially closes.")
    return ("WEAK_INCONCLUSIVE",
            "Part A shows some reduction in author-signal, but Part B's fresh-author recall "
            "improvement is small/mixed or random-split performance degraded beyond the "
            "non-inferiority margin - a real generalization benefit cannot be confidently "
            "claimed either way.")


def _cache_label_sequence(cache, split_name):
    return [int(label) for _, label in cache[split_name]]


def run_sanity_checks():
    """Pre-conclusion sanity checks (required before trusting any comparison below):
      1. Random split: our own normalized cache has the EXACT same per-split row counts AND
         label sequence as the original 'sbert_only' cache Section 20 reused (same
         split_random(), random_state=42 baked into train.py - verifies no accidental dropped/
         reordered rows and identical labels).
      2. Each of the 14 frozen fresh authors: our own normalized LOAO cache has the EXACT same
         per-split row counts AND label sequence as Section 25's own per-author cache (same
         split_leave_one_author() - verifies identical train/val/test membership, no leakage
         change, no dropped rows).
      3. The 14 authors used here are EXACTLY the frozen set (no substitution/addition/removal),
         and each cached test split's true narrative matches the frozen set's declared
         narrative for that author.
    Raises RuntimeError on any failure (never silently continues to a conclusion on
    unverified data). Saves a full pass/fail record to SANITY_CHECKS_FILE.
    """
    checks = {"random_split": {}, "fresh_authors": {}, "failures": []}

    # --- 1. Random split ---
    if os.path.exists(RANDOM_CACHE_FILE) and os.path.exists(ORIGINAL_RANDOM_CACHE_FILE):
        own_cache = torch.load(RANDOM_CACHE_FILE, weights_only=False)
        orig_cache = torch.load(ORIGINAL_RANDOM_CACHE_FILE, weights_only=False)
        for split_name in ("train", "val", "test"):
            own_labels = _cache_label_sequence(own_cache, split_name)
            orig_labels = _cache_label_sequence(orig_cache, split_name)
            same_count = len(own_labels) == len(orig_labels)
            same_labels = same_count and own_labels == orig_labels
            checks["random_split"][split_name] = {
                "own_n": len(own_labels), "original_n": len(orig_labels),
                "same_row_count": same_count, "same_label_sequence": same_labels,
            }
            if not same_labels:
                checks["failures"].append(
                    f"random_split/{split_name}: label sequence mismatch vs. "
                    f"'{ORIGINAL_RANDOM_CACHE_FILE}' (own_n={len(own_labels)}, "
                    f"original_n={len(orig_labels)})"
                )
    else:
        checks["failures"].append(
            "random_split: skipped (own or original cache not found yet - run --random first)"
        )

    # --- 2 & 3. Frozen fresh authors ---
    authors, frozen = load_frozen_authors()
    frozen_narrative_by_author = {a["author_source"]: a["narrative"] for a in frozen["selected_authors"]}
    expected_authors = set(frozen_narrative_by_author.keys())
    checks["fresh_authors"]["frozen_set_matches_14_authors"] = (
        len(authors) == 14 and set(authors) == expected_authors
    )
    if not checks["fresh_authors"]["frozen_set_matches_14_authors"]:
        checks["failures"].append(
            f"fresh_authors: author set does not match the frozen 14-author set exactly "
            f"(got {sorted(authors)})"
        )

    per_author = {}
    for author in authors:
        own_path = LOAO_CACHE_TEMPLATE.format(author=author)
        orig_path = ORIGINAL_LOAO_CACHE_TEMPLATE.format(author=author)
        if not (os.path.exists(own_path) and os.path.exists(orig_path)):
            checks["failures"].append(f"fresh_authors/{author}: skipped (own or original cache not found yet)")
            continue
        own_cache = torch.load(own_path, weights_only=False)
        orig_cache = torch.load(orig_path, weights_only=False)
        author_record = {}
        for split_name in ("train", "val", "test"):
            own_labels = _cache_label_sequence(own_cache, split_name)
            orig_labels = _cache_label_sequence(orig_cache, split_name)
            same_count = len(own_labels) == len(orig_labels)
            same_labels = same_count and own_labels == orig_labels
            author_record[split_name] = {
                "own_n": len(own_labels), "original_n": len(orig_labels),
                "same_row_count": same_count, "same_label_sequence": same_labels,
            }
            if not same_labels:
                checks["failures"].append(
                    f"fresh_authors/{author}/{split_name}: label sequence mismatch vs. "
                    f"'{orig_path}' (own_n={len(own_labels)}, original_n={len(orig_labels)})"
                )
        test_labels = _cache_label_sequence(own_cache, "test")
        cached_narrative = NARRATIVES[test_labels[0]] if test_labels else None
        expected_narrative = frozen_narrative_by_author.get(author)
        narrative_ok = cached_narrative == expected_narrative
        author_record["test_narrative_matches_frozen_set"] = narrative_ok
        if not narrative_ok:
            checks["failures"].append(
                f"fresh_authors/{author}: test narrative '{cached_narrative}' != frozen set's "
                f"declared narrative '{expected_narrative}'"
            )
        per_author[author] = author_record
    checks["fresh_authors"]["per_author"] = per_author

    checks["all_passed"] = len(checks["failures"]) == 0
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(SANITY_CHECKS_FILE, "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2)

    print(f"\n{'=' * 100}\nSANITY CHECKS (original vs. normalized: identical rows/labels/splits/authors, "
          f"no leakage, no dropped rows)\n{'=' * 100}")
    if checks["all_passed"]:
        print("ALL SANITY CHECKS PASSED - original and normalized variants are built from "
              "identical examples/labels/splits/authors; safe to compare.")
    else:
        print("SANITY CHECKS FAILED:")
        for failure in checks["failures"]:
            print(f"  - {failure}")
    print(f"Saved full sanity-check record to '{SANITY_CHECKS_FILE}'.")

    hard_failures = [f for f in checks["failures"] if "skipped" not in f]
    if hard_failures:
        raise RuntimeError(
            f"Sanity checks FAILED ({len(hard_failures)} issue(s)) - refusing to aggregate/"
            f"conclude on unverified data. See '{SANITY_CHECKS_FILE}' for details."
        )
    return checks


def aggregate():
    os.makedirs(REPORT_DIR, exist_ok=True)
    run_sanity_checks()

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        own_results = json.load(f)
    with open(ORIGINAL_RANDOM_RESULTS_FILE, "r", encoding="utf-8") as f:
        original_random = json.load(f)
    with open(ORIGINAL_FRESH_AUTHOR_RESULTS_FILE, "r", encoding="utf-8") as f:
        original_fresh_author = json.load(f)

    # ---- Random split: original ("none" mode, reused) vs. normalized (fresh) ----
    random_rows = []
    for seed in RANDOM_SPLIT_SEEDS:
        orig_m = original_random["results"]["none"][str(seed)]["test_metrics"]
        norm_m = own_results["random_split_normalized"]["results"][str(seed)]["test_metrics"]
        random_rows.append({"seed": seed, "variant": "original", "accuracy": orig_m["accuracy"],
                             "macro_f1": orig_m["macro_f1"]})
        random_rows.append({"seed": seed, "variant": "normalized", "accuracy": norm_m["accuracy"],
                             "macro_f1": norm_m["macro_f1"]})
    random_df = pd.DataFrame(random_rows)
    random_df.to_csv(RANDOM_SPLIT_COMPARISON_FILE, index=False, encoding="utf-8-sig")
    print("\nRandom-split comparison (original 'none' mode, reused, vs. style-normalized, fresh):")
    print(random_df.to_string(index=False))
    random_summary = random_df.groupby("variant")[["accuracy", "macro_f1"]].agg(["mean", "std"])
    print(random_summary)
    random_split_macro_f1_delta = (random_df[random_df.variant == "normalized"]["macro_f1"].mean() -
                                    random_df[random_df.variant == "original"]["macro_f1"].mean())

    # ---- Fresh authors: original (sbert_original, reused) vs. normalized (fresh) ----
    authors, _ = load_frozen_authors()
    fresh_rows = []
    for author in authors:
        orig = original_fresh_author.get(author, {}).get("sbert_original")
        norm = own_results.get("fresh_author_normalized", {}).get(author)
        if not orig or not norm:
            print(f"[!] WARNING: missing result for author '{author}' (orig={bool(orig)}, "
                  f"normalized={bool(norm)}) - skipped from aggregation.")
            continue
        fresh_rows.append({"author": author, "narrative": orig["narrative"], "variant": "original",
                            "recall_true_narrative": orig["recall_true_narrative"], "macro_f1": orig["macro_f1"]})
        fresh_rows.append({"author": author, "narrative": norm["narrative"], "variant": "normalized",
                            "recall_true_narrative": norm["recall_true_narrative"], "macro_f1": norm["macro_f1"]})
    fresh_df = pd.DataFrame(fresh_rows)
    fresh_df.to_csv(FRESH_AUTHOR_COMPARISON_FILE, index=False, encoding="utf-8-sig")
    print("\nFresh-author comparison (original 'sbert_original', reused, vs. style-normalized, fresh):")
    print(fresh_df.to_string(index=False))

    per_narrative = fresh_df.groupby(["narrative", "variant"])["recall_true_narrative"].mean().reset_index()
    per_narrative_pivot = per_narrative.pivot(index="narrative", columns="variant", values="recall_true_narrative")
    per_narrative_pivot.to_csv(PER_NARRATIVE_FILE, encoding="utf-8-sig")
    print("\nPer-narrative aggregation (mean recall across the 2 authors per narrative):")
    print(per_narrative_pivot.to_string())

    orig_recall = fresh_df[fresh_df.variant == "original"]["recall_true_narrative"]
    norm_recall = fresh_df[fresh_df.variant == "normalized"]["recall_true_narrative"]
    summary = {
        "original": {"mean": float(orig_recall.mean()), "median": float(orig_recall.median()),
                     "std": float(orig_recall.std()), "worst": float(orig_recall.min())},
        "normalized": {"mean": float(norm_recall.mean()), "median": float(norm_recall.median()),
                       "std": float(norm_recall.std()), "worst": float(norm_recall.min())},
    }
    print(f"\nFresh-author recall summary: {json.dumps(summary, indent=2)}")
    fresh_author_mean_delta = summary["normalized"]["mean"] - summary["original"]["mean"]
    fresh_author_median_delta = summary["normalized"]["median"] - summary["original"]["median"]

    # ---- Final decision (requires Part A's comparison file) ----
    if not os.path.exists(PART_A_COMPARISON_FILE):
        print(f"\n[!] '{PART_A_COMPARISON_FILE}' not found - run "
              f"narrative_style_normalization_author_signature.py first to get the final "
              f"decision (Part A + Part B combined).")
        return
    with open(PART_A_COMPARISON_FILE, "r", encoding="utf-8") as f:
        part_a_comparison = json.load(f)

    pattern, explanation = classify_outcome(
        part_a_comparison, fresh_author_mean_delta, fresh_author_median_delta,
        random_split_macro_f1_delta,
    )
    decision = {
        "fresh_author_mean_delta": fresh_author_mean_delta,
        "fresh_author_median_delta": fresh_author_median_delta,
        "random_split_macro_f1_delta": random_split_macro_f1_delta,
        "fresh_author_summary": summary,
        "outcome_pattern": pattern,
        "explanation": explanation,
    }
    with open(FINAL_DECISION_FILE, "w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2)
    print(f"\n{'=' * 100}\nFINAL DECISION: {pattern}\n{explanation}\n{'=' * 100}")
    print(f"Saved final decision to '{FINAL_DECISION_FILE}'.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--random", action="store_true", help="Train the style-normalized variant on the random split (3 seeds).")
    parser.add_argument("--author", type=str, default=None, help="Train the style-normalized variant LOAO for a single frozen fresh author.")
    parser.add_argument("--all-authors", action="store_true", help="Train the style-normalized variant LOAO for all 14 frozen fresh authors.")
    parser.add_argument("--aggregate", action="store_true", help="Aggregate original (reused) vs. normalized (fresh) results and apply the pre-specified decision rules.")
    args = parser.parse_args()

    if args.random:
        run_random()
    if args.author:
        run_author(args.author)
    if args.all_authors:
        run_all_authors()
    if args.aggregate:
        aggregate()
    if not (args.random or args.author or args.all_authors or args.aggregate):
        parser.print_help()


if __name__ == "__main__":
    main()

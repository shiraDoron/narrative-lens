"""
Narrative Classification — Fresh-Author Confirmatory Evaluation (Experiment 25, Phase 2)
===========================================================================================
CONFIRMATORY, per the pre-registered protocol in EXPERIMENTS.md Section 25 (written and
frozen BEFORE this script was run). Evaluates exactly 3 frozen variants on the 14 fresh
authors frozen by narrative_fresh_author_freeze.py (2 per narrative, seed=42) — authors never
individually used for hypothesis generation in Sections 19-24.

Frozen variants (exactly 3, no sweep, no tuning, no additions):
  1. sbert_original                          - SBERT on unmasked text, no augmentation.
  2. sbert_soft_topic                        - SBERT + Soft Topic Distribution.
  3. sbert_person_misc_masked_aug_soft_topic - Section 24's selected policy: PER+MISC-masked
                                                augmented copy interleaved with the original
                                                + Soft Topic Distribution.

Same architecture (AblationDetector), hyperparameters, SBERT backbone, Soft Topic model, and
seed (42) as Sections 18-24. PER+MISC masking reuses the corpus-wide raw-entities cache built
in Section 24 (data/cache/cached_raw_entities_by_text.pt) — no new NER inference is run here.

No masking-policy change, no hyperparameter change, no author swap, no threshold tuning, no
seed change, and no new metric introduced after seeing results — see EXPERIMENTS.md Section 25
for the full pre-registered protocol.

Run (from repo root):
    python experiments/author_generalization/narrative_fresh_author_confirmatory.py --author <name>
    python experiments/author_generalization/narrative_fresh_author_confirmatory.py --all
    python experiments/author_generalization/narrative_fresh_author_confirmatory.py --aggregate
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
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

from narrative_lens.config import NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from narrative_lens.train import load_raw_data, split_leave_one_author, evaluate, save_confusion_matrix_csv

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from narrative_ablation_loao import AblationDetector, build_hard_soft_dense_vectors  # noqa: E402
from narrative_selective_entity_masking_augmentation import (  # noqa: E402
    masked_text_for_policy, MASK_POLICIES,
)

SEED = 42  # same fixed seed as Sections 18-24

BERTOPIC_MODEL_PATH = "models/experiments/soft_v2_baseline_seeded"
BERTOPIC_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

FROZEN_SET_FILE = "reports/results/narrative_fresh_author_audit/fresh_author_confirmatory_set.json"
RAW_ENTITIES_CACHE_FILE = "data/cache/cached_raw_entities_by_text.pt"

CACHE_DIR = "data/cache"
FEATURE_CACHE_TEMPLATE = os.path.join(CACHE_DIR, "cached_features_fresh_author_confirmatory_{author}.pt")
CHECKPOINT_DIR = "models/experiments/narrative_fresh_author_confirmatory"
REPORT_DIR = "reports/results/narrative_fresh_author_confirmatory"
RESULTS_FILE = os.path.join(REPORT_DIR, "results.json")
SUMMARY_FILE = os.path.join(REPORT_DIR, "fresh_author_confirmatory_summary.csv")
PER_NARRATIVE_FILE = os.path.join(REPORT_DIR, "per_narrative_aggregation.csv")

VARIANTS = ("sbert_original", "sbert_soft_topic", "sbert_person_misc_masked_aug_soft_topic")
MASK_TYPES = MASK_POLICIES["person_misc"]  # {"PER", "MISC"} - fixed, reused verbatim from Section 24

# Pre-registered (EXPERIMENTS.md Section 25) — fixed before any result was seen.
NON_INFERIORITY_MARGIN = 0.03  # 3 percentage points absolute recall
DEGRADATION_GUARDRAIL_MARGIN = 0.10  # 10pp
DEGRADATION_GUARDRAIL_MAX_FRACTION = 0.20  # no more than 20% of authors may exceed the margin


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


def safe_torch_save(obj, path, retries=5, delay=1.0):
    """Windows occasionally raises a transient sharing-violation (WinError 32) when
    overwriting a just-written checkpoint file (antivirus/indexer holding a brief lock) -
    retry with backoff instead of aborting a long multi-author run over it."""
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


def build_or_load_raw_entities_cache():
    if not os.path.exists(RAW_ENTITIES_CACHE_FILE):
        raise FileNotFoundError(
            f"'{RAW_ENTITIES_CACHE_FILE}' not found - expected it to already exist from "
            f"Experiment 24 (corpus-wide, author-independent raw-entities cache)."
        )
    print(f"Loading existing raw-entities cache '{RAW_ENTITIES_CACHE_FILE}'...")
    return torch.load(RAW_ENTITIES_CACHE_FILE, weights_only=False)


# =========================================================================================
# Step 1: per-author feature cache - sbert_embedding (original), sbert_embedding_masked
# (PER+MISC-masked, train/val only - test is never masked, same convention as Section 24),
# soft_dense (BERTopic Soft Topic Distribution) for train/val/test.
# =========================================================================================
def build_or_load_author_cache(author, sbert_model, bertopic_model, num_bertopic_topics,
                                raw_entities_by_text):
    cache_file = FEATURE_CACHE_TEMPLATE.format(author=author)
    if os.path.exists(cache_file):
        print(f"Found existing feature cache '{cache_file}'. Loading...")
        return torch.load(cache_file, weights_only=False)

    print(f"\n=== Building fresh feature cache for held-out author '{author}' ===")
    df = load_raw_data()
    train_data, val_data, test_data = split_leave_one_author(df, author)
    for split_df in (train_data, val_data, test_data):
        split_df["text"] = split_df["text"].astype(str).str.slice(0, 3000)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    result = {}
    sbert_dim = None
    n_missing_entities_entry = 0
    for name, split_df in splits.items():
        print(f"--- Split '{name}' ({len(split_df)} rows) ---")
        texts = split_df["text"].tolist()
        labels = split_df["label"].astype(int).tolist()

        print("  Computing SBERT embeddings (original text)...")
        sbert_embeddings = sbert_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        sbert_dim = int(sbert_embeddings.shape[1])

        print("  Computing Soft Topic Distribution (BERTopic)...")
        _, soft_dense = build_hard_soft_dense_vectors(texts, bertopic_model, num_bertopic_topics)

        sbert_embeddings_masked = None
        if name in ("train", "val"):
            masked_texts = []
            for t in texts:
                if t in raw_entities_by_text:
                    masked_texts.append(masked_text_for_policy(t, raw_entities_by_text[t], MASK_TYPES))
                else:
                    n_missing_entities_entry += 1
                    masked_texts.append(t)
            print("  Computing SBERT embeddings (PERSON+MISC-masked text)...")
            sbert_embeddings_masked = sbert_model.encode(
                masked_texts, convert_to_numpy=True, show_progress_bar=True)

        rows = []
        for i in range(len(texts)):
            feat = {
                "sbert_embedding": torch.tensor(sbert_embeddings[i], dtype=torch.float32),
                "soft_dense": torch.from_numpy(soft_dense[i]),
            }
            if sbert_embeddings_masked is not None:
                feat["sbert_embedding_masked"] = torch.tensor(sbert_embeddings_masked[i], dtype=torch.float32)
            rows.append((feat, labels[i]))
        result[name] = rows

    if n_missing_entities_entry:
        print(f"[!] WARNING: {n_missing_entities_entry} row(s) had no entry in the raw-entities "
              f"cache (fell back to unmasked text).")

    result["_meta"] = {
        "bertopic_vec_size": num_bertopic_topics + 1,
        "sbert_dim": sbert_dim,
        "n_missing_entities_entry": n_missing_entities_entry,
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_torch_save(result, cache_file)
    print(f"Saved feature cache to '{cache_file}'.")
    return result


def _interleave(rows_a, rows_b):
    """[a0, b0, a1, b1, ...] - same interleaving convention as Section 24."""
    assert len(rows_a) == len(rows_b)
    out = []
    for a, b in zip(rows_a, rows_b):
        out.append(a)
        out.append(b)
    return out


def build_variant_features(variant_name, cache):
    def plain(rows, use_soft):
        out = []
        for f, l in rows:
            feat = {"sbert_embedding": f["sbert_embedding"]}
            if use_soft:
                feat["soft_dense"] = f["soft_dense"]
            out.append((feat, l))
        return out

    def masked(rows, use_soft):
        out = []
        for f, l in rows:
            feat = {"sbert_embedding": f["sbert_embedding_masked"]}
            if use_soft:
                feat["soft_dense"] = f["soft_dense"]
            out.append((feat, l))
        return out

    if variant_name == "sbert_original":
        arms = set()
        return (arms, plain(cache["train"], False), plain(cache["val"], False),
                plain(cache["test"], False))
    if variant_name == "sbert_soft_topic":
        arms = {"soft_topic"}
        return (arms, plain(cache["train"], True), plain(cache["val"], True),
                plain(cache["test"], True))
    if variant_name == "sbert_person_misc_masked_aug_soft_topic":
        arms = {"soft_topic"}
        train_features = _interleave(plain(cache["train"], True), masked(cache["train"], True))
        val_features = _interleave(plain(cache["val"], True), masked(cache["val"], True))
        test_features = plain(cache["test"], True)  # test is never masked
        return arms, train_features, val_features, test_features
    raise ValueError(f"Unknown variant '{variant_name}'")


# =========================================================================================
# Training loop - identical hyperparameters/early-stopping/checkpoint convention as
# Sections 18-24's train_variant().
# =========================================================================================
def train_variant(variant_name, arms, author, train_features, val_features, test_features,
                   bertopic_vec_size, sbert_dim, epochs=EPOCHS, batch_size=BATCH_SIZE,
                   patience=3, lr=LEARNING_RATE, seed=SEED):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{variant_name}_{author}.pth")

    set_seed(seed)
    detector = AblationDetector(arms, ner_vocab_size=1, srl_vocab_size=1,
                                 bertopic_vec_size=bertopic_vec_size, sbert_dim=sbert_dim)

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

            val_metrics, avg_val_loss, _, _ = evaluate(detector, val_features, loss_fn)
            print(f"[{variant_name}/{author}] Epoch {epoch + 1}: "
                  f"Train Acc {100 * train_correct / len(train_features):.2f}% | "
                  f"Val Loss {avg_val_loss:.4f} | Val Acc {val_metrics['accuracy'] * 100:.2f}% | "
                  f"Val Macro-F1 {val_metrics['macro_f1']:.4f}")

            if val_metrics['macro_f1'] > best_val_macro_f1:
                best_val_macro_f1 = val_metrics['macro_f1']
                epochs_no_improve = 0
                safe_torch_save(detector.state_dict(), checkpoint_file)
                print(f">>> New best model saved (Val Macro-F1: {best_val_macro_f1:.4f}) -> '{checkpoint_file}'")
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"[{variant_name}/{author}] Early stopping at epoch {epoch + 1}.")
                    break

        detector.load_state_dict(torch.load(checkpoint_file))

    test_metrics, _, test_true, test_pred = evaluate(detector, test_features)
    return test_metrics, test_true, test_pred


# =========================================================================================
# Orchestration
# =========================================================================================
def run_author(author, sbert_model, bertopic_model, num_bertopic_topics, raw_entities_by_text):
    cache = build_or_load_author_cache(author, sbert_model, bertopic_model, num_bertopic_topics,
                                        raw_entities_by_text)
    meta = cache["_meta"]
    bertopic_vec_size = meta["bertopic_vec_size"]
    sbert_dim = meta["sbert_dim"]
    true_narrative_name = NARRATIVES[cache["test"][0][1]]

    os.makedirs(REPORT_DIR, exist_ok=True)
    author_results = {}

    for variant_name in VARIANTS:
        print(f"\n{'=' * 70}\n=== Variant '{variant_name}' - author '{author}' "
              f"(true narrative: {true_narrative_name}) ===\n{'=' * 70}")
        arms, train_features, val_features, test_features = build_variant_features(variant_name, cache)
        print(f"  n_train_effective={len(train_features)} | n_val_effective={len(val_features)} | "
              f"n_test={len(test_features)}")

        test_metrics, test_true, test_pred = train_variant(
            variant_name, arms, author, train_features, val_features, test_features,
            bertopic_vec_size, sbert_dim,
        )

        n = len(test_true)
        correct = sum(1 for t, p in zip(test_true, test_pred) if t == p)
        recall_true_narrative = correct / n if n else 0.0

        wrong_preds = [p for t, p in zip(test_true, test_pred) if p != t]
        dominant_wrong_narrative = None
        dominant_wrong_error_share = 0.0
        if wrong_preds:
            dominant_idx, dominant_count = Counter(wrong_preds).most_common(1)[0]
            dominant_wrong_narrative = NARRATIVES[dominant_idx]
            dominant_wrong_error_share = dominant_count / len(wrong_preds)

        cm_path = os.path.join(REPORT_DIR, f"confusion_matrix_{variant_name}_{author}_test.csv")
        save_confusion_matrix_csv(test_metrics, cm_path)

        author_results[variant_name] = {
            "narrative": true_narrative_name,
            "accuracy": test_metrics["accuracy"],
            "macro_precision": test_metrics["macro_precision"],
            "macro_recall": test_metrics["macro_recall"],
            "macro_f1": test_metrics["macro_f1"],
            "recall_true_narrative": recall_true_narrative,
            "dominant_wrong_narrative": dominant_wrong_narrative,
            "dominant_wrong_narrative_error_share": dominant_wrong_error_share,
            "n_test": n,
            "n_errors": len(wrong_preds),
            "n_train_effective": len(train_features),
            "n_val_effective": len(val_features),
            "confusion_matrix_csv": cm_path,
        }
        print(f"[{variant_name}/{author}] TEST: recall(true narrative)={recall_true_narrative * 100:.1f}% | "
              f"dominant wrong narrative={dominant_wrong_narrative} "
              f"({dominant_wrong_error_share * 100:.1f}% of errors) | macro_f1={test_metrics['macro_f1']:.4f}")

    all_results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    all_results[author] = author_results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved results for author '{author}' to '{RESULTS_FILE}'.")
    return author_results


def run_all(authors):
    print(f"Loading SBERT model '{BERTOPIC_EMBEDDING_MODEL_NAME}' (frozen, encode-only, shared "
          f"across all {len(authors)} authors)...")
    sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)

    print(f"Loading BERTopic model from '{BERTOPIC_MODEL_PATH}' (shared across all authors)...")
    bertopic_model = BERTopic.load(BERTOPIC_MODEL_PATH, embedding_model=BERTOPIC_EMBEDDING_MODEL_NAME)
    num_bertopic_topics = len([t for t in bertopic_model.get_topics().keys() if t != -1])
    print(f"  -> {num_bertopic_topics} real topics (+1 reserved OOV/outlier slot).")

    raw_entities_cache = build_or_load_raw_entities_cache()
    raw_entities_by_text = raw_entities_cache["raw_entities_by_text"]

    for i, author in enumerate(authors):
        print(f"\n\n######## Author {i + 1}/{len(authors)}: '{author}' ########")
        run_author(author, sbert_model, bertopic_model, num_bertopic_topics, raw_entities_by_text)


# =========================================================================================
# Aggregation + pre-registered non-inferiority / robustness-guardrail check.
# =========================================================================================
def aggregate():
    if not os.path.exists(RESULTS_FILE):
        raise FileNotFoundError(f"'{RESULTS_FILE}' not found - run --all (or --author per author) first.")
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    authors, _ = load_frozen_authors()
    missing = [a for a in authors if a not in all_results]
    if missing:
        print(f"[!] WARNING: results missing for author(s) {missing} - aggregation is "
              f"partial/incomplete until all 14 authors have been run.")
    present_authors = [a for a in authors if a in all_results]

    rows = []
    for author in present_authors:
        for variant_name in VARIANTS:
            r = all_results[author].get(variant_name)
            if not r:
                continue
            rows.append({
                "author": author,
                "narrative": r["narrative"],
                "variant": variant_name,
                "recall_true_narrative": r["recall_true_narrative"],
                "macro_f1": r["macro_f1"],
                "accuracy": r["accuracy"],
                "dominant_wrong_narrative": r["dominant_wrong_narrative"],
                "dominant_wrong_narrative_error_share": r["dominant_wrong_narrative_error_share"],
            })
    df = pd.DataFrame(rows)

    print("\n" + "=" * 100)
    print("FRESH-AUTHOR CONFIRMATORY EVALUATION (Experiment 25) - per-author results")
    print("=" * 100)
    print(df.to_string(index=False))

    print("\n" + "=" * 100)
    print("PRIMARY METRIC SUMMARY (true-narrative recall, paired by held-out author)")
    print("=" * 100)
    summary_rows = []
    for variant_name in VARIANTS:
        sub = df[df["variant"] == variant_name]["recall_true_narrative"]
        summary_rows.append({
            "variant": variant_name,
            "n_authors": len(sub),
            "mean_recall": float(sub.mean()) if len(sub) else None,
            "median_recall": float(sub.median()) if len(sub) else None,
            "std_recall": float(sub.std()) if len(sub) else None,
            "iqr_recall": float(sub.quantile(0.75) - sub.quantile(0.25)) if len(sub) else None,
            "worst_author_recall": float(sub.min()) if len(sub) else None,
            "mean_macro_f1": float(df[df["variant"] == variant_name]["macro_f1"].mean()) if len(sub) else None,
            "mean_dominant_error_concentration": float(
                df[df["variant"] == variant_name]["dominant_wrong_narrative_error_share"].mean()
            ) if len(sub) else None,
        })
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))

    os.makedirs(REPORT_DIR, exist_ok=True)
    df.to_csv(SUMMARY_FILE, index=False, encoding="utf-8-sig")
    summary_df.to_csv(SUMMARY_FILE.replace(".csv", "_by_variant.csv"), index=False, encoding="utf-8-sig")

    per_narrative = df.groupby(["narrative", "variant"])["recall_true_narrative"].mean().reset_index()
    per_narrative_pivot = per_narrative.pivot(index="narrative", columns="variant", values="recall_true_narrative")
    print("\nPer-narrative aggregation (mean recall across the 2 authors per narrative):")
    print(per_narrative_pivot.to_string())
    per_narrative_pivot.to_csv(PER_NARRATIVE_FILE, encoding="utf-8-sig")

    # -------------------------------------------------------------------------------
    # Pre-registered non-inferiority rule + robustness guardrail (EXPERIMENTS.md Section 25)
    # -------------------------------------------------------------------------------
    if len(present_authors) == len(authors):
        print("\n" + "=" * 100)
        print("PRE-REGISTERED NON-INFERIORITY CHECK: sbert_person_misc_masked_aug_soft_topic "
              "vs. sbert_original")
        print("=" * 100)
        baseline = df[df["variant"] == "sbert_original"].set_index("author")["recall_true_narrative"]
        candidate = df[df["variant"] == "sbert_person_misc_masked_aug_soft_topic"].set_index("author")["recall_true_narrative"]

        mean_ok = candidate.mean() >= baseline.mean() - NON_INFERIORITY_MARGIN
        median_ok = candidate.median() >= baseline.median() - NON_INFERIORITY_MARGIN
        print(f"  Baseline mean={baseline.mean() * 100:.1f}% | Candidate mean={candidate.mean() * 100:.1f}% | "
              f"mean condition (candidate >= baseline - 3pp)? {mean_ok}")
        print(f"  Baseline median={baseline.median() * 100:.1f}% | Candidate median={candidate.median() * 100:.1f}% | "
              f"median condition (candidate >= baseline - 3pp)? {median_ok}")

        degradation = baseline - candidate
        n_severe = int((degradation > DEGRADATION_GUARDRAIL_MARGIN).sum())
        frac_severe = n_severe / len(authors)
        guardrail_ok = frac_severe <= DEGRADATION_GUARDRAIL_MAX_FRACTION
        print(f"  Authors with >10pp degradation vs. baseline: {n_severe}/{len(authors)} "
              f"({frac_severe * 100:.1f}%) | guardrail (<=20%)? {guardrail_ok}")

        non_inferior = mean_ok and median_ok and guardrail_ok
        print(f"\n  => NON-INFERIOR (mean AND median AND guardrail)? {non_inferior}")
        print("\n  Reminder: per EXPERIMENTS.md Section 25, confirmatory support additionally "
              "requires evidence that some fresh authors show improved robustness / lower "
              "dominant-error concentration without a large overall trade-off - see the "
              "mean_dominant_error_concentration row above, compared across variants.")
    else:
        print("\n[!] Non-inferiority check skipped - not all 14 authors have results yet.")

    return df, summary_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fresh-Author Confirmatory Evaluation (Experiment 25) for Narrative "
                     "Classification - 3 frozen variants on 14 frozen fresh authors."
    )
    parser.add_argument("--author", default=None, help="Run all 3 variants for a single author.")
    parser.add_argument("--all", action="store_true", help="Run all 3 variants for all 14 frozen authors.")
    parser.add_argument("--aggregate", action="store_true", help="Print + save the cross-author summary.")
    args = parser.parse_args()

    frozen_authors, _frozen = load_frozen_authors()

    if args.author:
        if args.author not in frozen_authors:
            raise ValueError(f"'{args.author}' is not in the frozen 14-author set: {frozen_authors}")
        print(f"Loading SBERT model '{BERTOPIC_EMBEDDING_MODEL_NAME}'...")
        _sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)
        print(f"Loading BERTopic model from '{BERTOPIC_MODEL_PATH}'...")
        _bertopic_model = BERTopic.load(BERTOPIC_MODEL_PATH, embedding_model=BERTOPIC_EMBEDDING_MODEL_NAME)
        _num_topics = len([t for t in _bertopic_model.get_topics().keys() if t != -1])
        _raw_entities = build_or_load_raw_entities_cache()["raw_entities_by_text"]
        run_author(args.author, _sbert_model, _bertopic_model, _num_topics, _raw_entities)
    elif args.all:
        run_all(frozen_authors)
    elif args.aggregate:
        aggregate()
    else:
        parser.print_help()

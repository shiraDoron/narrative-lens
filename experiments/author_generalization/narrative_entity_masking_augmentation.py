"""
Narrative Classification — Entity-Masking Augmentation Test (Experiment 23)
=============================================================================
Follow-up to EXPERIMENTS.md section 21 (Entity Shortcut Test) and section 22 (stance-aware
entity representation, closed as a negative finding). Section 21 found that FULL entity
masking is not a universal fix: it helps BernieSanders (reduces the Right-wing-misrouting
shortcut) but HURTS IDF and MariaZakharova (removes legitimate identity signal). This
experiment asks whether TRAINING-TIME masking augmentation - showing the model both the
original and the entity-masked version of every training example, both under the same
narrative label - can get some of Bernie's benefit without paying IDF/Maria's full cost,
by teaching the model that the label should be invariant to entity identity being
present/absent, rather than removing identity information from the model entirely.

Research question: does entity-masking AUGMENTATION improve unseen-author generalization
without losing the useful entity signal seen for IDF/MariaZakharova?

Variants compared (same 3 LOAO authors, same split_leave_one_author logic/seed=42 as
sections 18-21, same SBERT backbone, same AblationDetector architecture/hyperparameters -
see "Audit" below for exactly what is reused vs. newly trained):
  1. sbert_original                     - REUSED verbatim (section 21's "sbert_only", itself
                                           reused from section 19). SBERT on ORIGINAL,
                                           unmasked text. Baseline.
  2. sbert_masked_only                  - REUSED verbatim (section 21's "sbert_masked").
                                           SBERT on entity-MASKED text only, no original text
                                           ever seen. The "full masking" comparison point.
  3. sbert_soft_topic                   - REUSED verbatim (section 21's "sbert_soft_topic",
                                           itself reused from section 19). SBERT (unmasked)
                                           + Soft Topic Distribution arm. Existing robustness
                                           baseline.
  4. sbert_duplicated_original_control  - NEW. Every training/validation example duplicated
                                           TWICE, both copies ORIGINAL (unmasked), no masking
                                           at all. Isolates "more training rows" from
                                           "masking augmentation" - see Fairness section.
  5. sbert_masked_aug                   - NEW. Every training/validation example contributes
                                           BOTH its original and its entity-masked version,
                                           both under the SAME label. Test stays original-only.
  6. sbert_masked_aug_soft_topic        - NEW. Same augmentation as (5), + Soft Topic
                                           Distribution arm on top.

Audit performed before writing any new code (per explicit instruction - documented here,
not just asserted):
  - Section 21's results.json (reports/results/narrative_entity_shortcut/results.json)
    already contains "sbert_only", "sbert_masked", and "sbert_soft_topic" for all 3 LOAO
    authors, computed under the EXACT split/seed/architecture this experiment needs -> all
    3 reused verbatim (verify_reuse_validity() checks this programmatically before allowing
    reuse; no retraining).
  - narrative_lens/features/ner.py's mask_entities()/EntityAnalysisPipeline/
    reconstruct_fragmented_entities() (section 21's masking pipeline) do NOT need to run
    again: BOTH the per-author ORIGINAL feature cache
    (data/cache/cached_features_ablation_loao_{author}.pt, from section 19/20 - has
    "sbert_embedding" on unmasked text + "soft_dense") and the per-author MASKED feature
    cache (data/cache/cached_features_entity_shortcut_{author}.pt, from section 21 - has
    "sbert_embedding" on masked text + the SAME "soft_dense" reused by position) already
    exist on disk for all 3 authors, and were independently verified (at their own
    construction time, in their own scripts) to be position-aligned to the SAME
    split_leave_one_author(df, author) train/val/test split. A direct label-by-position
    comparison between the two caches (done once, ad hoc, before writing this script)
    confirmed exact alignment (train/val/test label lists identical) for all 3 authors.
    Consequence: this experiment needs ZERO new NER/SBERT/BERTopic inference - the 3 new
    variants are built purely by INTERLEAVING rows already sitting in these two existing
    caches, and training is 3 new lightweight MLPs x 3 authors = 9 trainings total, no
    heavier than section 19-21's own "new variant" trainings.
  - AblationDetector (narrative_ablation_loao.py) is reused UNMODIFIED - no architecture
    change. Every new variant here only varies which rows are concatenated into
    train_features/val_features (arms are always set() or {"soft_topic"}, both paths
    AblationDetector already supports).

Fairness / leakage constraints honored (see build_variant_features()):
  - Masked (or duplicated) copies are created ONLY from rows already inside the TRAIN or
    VAL split of the per-author cache. Since both source caches are themselves scoped to
    split_leave_one_author's train/val/test partition (verified at their own construction),
    it is not possible for a held-out author's row to be duplicated/masked into training -
    the held-out author's data was never in either source cache's "train"/"val" list to
    begin with.
  - TEST is always the untouched, single-copy, ORIGINAL (unmasked) test split
    (orig_cache["test"]) for every variant, including the new ones - no augmentation, no
    masking, ever applied at test time. This matches the reused variants' own test sets
    exactly (same n_test=200/author), so all 6 variants are compared on identical test data.
  - "sbert_duplicated_original_control" isolates "twice as many training ROWS" (with zero
    new information - literal duplicates) from "twice as many training rows because one
    copy is masked" (sbert_masked_aug). If duplicated-original alone recovers a similar
    amount of the effect, the improvement is not attributable to masking specifically.
  - Effective training/validation size is recorded explicitly per variant
    (n_train_original/n_train_effective/n_val_original/n_val_effective) in results.json -
    always exactly 2x the original split for the 3 new variants.
  - Original and masked (or duplicated) rows are INTERLEAVED as [row0_a, row0_b, row1_a,
    row1_b, ...], not concatenated as [all_a..., all_b...] - train.py's training convention
    (reused via AblationDetector's train loop, see train_variant() below) does NOT shuffle
    between epochs, so concatenation would put ~13k original-only gradient steps before any
    masked/duplicated ones each epoch. Interleaving is applied IDENTICALLY to both
    sbert_masked_aug and sbert_duplicated_original_control, so the two variants differ ONLY
    in whether the second copy of each example is masked or an exact duplicate - not in
    batch composition/order.

Not touched: no stance features (section 22 closed as a negative finding), no new
architecture, no hyperparameter tuning after seeing results (same EPOCHS/BATCH_SIZE/
LEARNING_RATE/hidden_size/dropout/patience/seed as sections 19-21 throughout).

Run (from repo root):
    python experiments/author_generalization/narrative_entity_masking_augmentation.py --author IDF
    python experiments/author_generalization/narrative_entity_masking_augmentation.py --author MariaZakharova
    python experiments/author_generalization/narrative_entity_masking_augmentation.py --author BernieSanders
Then:
    python experiments/author_generalization/narrative_entity_masking_augmentation.py --aggregate
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

from narrative_lens.config import NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from narrative_lens.train import evaluate, save_confusion_matrix_csv

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from narrative_ablation_loao import AblationDetector  # noqa: E402 - sibling script, unmodified

AUTHORS = ("IDF", "MariaZakharova", "BernieSanders")
SEED = 42  # same fixed seed as sections 18-21, no variance study

CACHE_DIR = "data/cache"
ORIGINAL_CACHE_TEMPLATE = os.path.join(CACHE_DIR, "cached_features_ablation_loao_{author}.pt")
MASKED_CACHE_TEMPLATE = os.path.join(CACHE_DIR, "cached_features_entity_shortcut_{author}.pt")

CHECKPOINT_DIR = "models/experiments/narrative_entity_masking_augmentation"
REPORT_DIR = "reports/results/narrative_entity_masking_augmentation"
RESULTS_FILE = os.path.join(REPORT_DIR, "results.json")
SUMMARY_FILE = os.path.join(REPORT_DIR, "entity_masking_augmentation_summary.csv")

EXISTING_SHORTCUT_RESULTS_FILE = "reports/results/narrative_entity_shortcut/results.json"
# new_variant_name -> the variant name it is reused verbatim from in section 21's results.json
REUSED_VARIANT_MAP = {
    "sbert_original": "sbert_only",
    "sbert_masked_only": "sbert_masked",
    "sbert_soft_topic": "sbert_soft_topic",
}

NEW_VARIANTS = {
    "sbert_duplicated_original_control": set(),
    "sbert_masked_aug": set(),
    "sbert_masked_aug_soft_topic": {"soft_topic"},
}

ALL_VARIANTS_ORDER = (
    "sbert_original", "sbert_duplicated_original_control", "sbert_masked_only",
    "sbert_masked_aug", "sbert_soft_topic", "sbert_masked_aug_soft_topic",
)

RIGHT_WING_IDX = NARRATIVES.index("Right-wing")


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


# =========================================================================================
# Reuse section 21's sbert_only/sbert_masked/sbert_soft_topic verbatim (no retraining).
# =========================================================================================
def verify_reuse_validity():
    if not os.path.exists(EXISTING_SHORTCUT_RESULTS_FILE):
        raise FileNotFoundError(
            f"'{EXISTING_SHORTCUT_RESULTS_FILE}' not found - run section 21's "
            f"narrative_entity_shortcut.py for all 3 authors first."
        )
    with open(EXISTING_SHORTCUT_RESULTS_FILE, "r", encoding="utf-8") as f:
        existing_results = json.load(f)
    for author in AUTHORS:
        if author not in existing_results:
            raise RuntimeError(f"Author '{author}' missing from '{EXISTING_SHORTCUT_RESULTS_FILE}'.")
        for source_variant in REUSED_VARIANT_MAP.values():
            if source_variant not in existing_results[author]:
                raise RuntimeError(
                    f"Variant '{source_variant}' missing for author '{author}' in "
                    f"'{EXISTING_SHORTCUT_RESULTS_FILE}' - cannot reuse."
                )
    return existing_results


def reused_variant_result(existing_results, author, new_name, source_name):
    entry = dict(existing_results[author][source_name])
    entry["reused_from"] = EXISTING_SHORTCUT_RESULTS_FILE
    entry["reused_from_variant"] = source_name
    return entry


# =========================================================================================
# Load the 2 existing per-author caches (original + masked), verify they are position-
# aligned to each other on every split before building any augmented feature list.
# =========================================================================================
def load_author_caches(author):
    orig_path = ORIGINAL_CACHE_TEMPLATE.format(author=author)
    masked_path = MASKED_CACHE_TEMPLATE.format(author=author)
    for path in (orig_path, masked_path):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"'{path}' not found - run sections 19-21's scripts for author '{author}' first."
            )
    orig_cache = torch.load(orig_path, weights_only=False)
    masked_cache = torch.load(masked_path, weights_only=False)

    for split in ("train", "val", "test"):
        orig_labels = [label for _, label in orig_cache[split]]
        masked_labels = [label for _, label in masked_cache[split]]
        if orig_labels != masked_labels or len(orig_labels) != len(masked_labels):
            raise RuntimeError(
                f"Alignment check FAILED for split '{split}' (author='{author}'): "
                f"'{orig_path}' and '{masked_path}' do not agree row-for-row. Refusing to "
                f"silently build a mismatched augmented dataset."
            )
    return orig_cache, masked_cache


def _interleave(rows_a, rows_b):
    """[a0, b0, a1, b1, ...] - see module docstring's Fairness section for why interleaving
    (not concatenation) is used, and why it's applied identically to both the masked-
    augmentation and duplicated-original-control variants."""
    assert len(rows_a) == len(rows_b)
    out = []
    for a, b in zip(rows_a, rows_b):
        out.append(a)
        out.append(b)
    return out


def build_variant_features(variant_name, orig_cache, masked_cache):
    """Returns (train_features, val_features, test_features). test_features is ALWAYS the
    untouched, single-copy, original test split - never augmented, matching the reused
    variants' own test sets exactly."""
    test_features = orig_cache["test"]

    if variant_name == "sbert_duplicated_original_control":
        train_features = _interleave(orig_cache["train"], orig_cache["train"])
        val_features = _interleave(orig_cache["val"], orig_cache["val"])
    elif variant_name in ("sbert_masked_aug", "sbert_masked_aug_soft_topic"):
        train_features = _interleave(orig_cache["train"], masked_cache["train"])
        val_features = _interleave(orig_cache["val"], masked_cache["val"])
    else:
        raise ValueError(f"Unknown new variant '{variant_name}'.")
    return train_features, val_features, test_features


# =========================================================================================
# Training loop - identical convention to sections 19-21's train_variant() (same
# AblationDetector, same hyperparameters/early-stopping/checkpoint-selection rule), only
# operating on the (possibly 2x-length) train_features/val_features built above.
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
                torch.save(detector.state_dict(), checkpoint_file)
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
def run_author(author):
    existing_results = verify_reuse_validity()
    orig_cache, masked_cache = load_author_caches(author)
    meta = orig_cache["_meta"]
    bertopic_vec_size = meta["bertopic_vec_size"]
    sbert_dim = meta["sbert_dim"]

    os.makedirs(REPORT_DIR, exist_ok=True)
    author_results = {}

    for new_name, source_name in REUSED_VARIANT_MAP.items():
        author_results[new_name] = reused_variant_result(existing_results, author, new_name, source_name)
        r = author_results[new_name]
        print(f"[{new_name}/{author}] REUSED from section 21 ('{source_name}'): "
              f"recall(true narrative)={r['recall_true_narrative'] * 100:.1f}% | "
              f"%->Right-wing={r['pct_misclassified_right_wing'] * 100:.1f}% | "
              f"macro_f1={r['macro_f1']:.4f}")

    n_train_original = len(orig_cache["train"])
    n_val_original = len(orig_cache["val"])

    for variant_name, arms in NEW_VARIANTS.items():
        print(f"\n{'=' * 70}\n=== Variant '{variant_name}' (arms={sorted(arms) or ['(none)']}) "
              f"- author '{author}' ===\n{'=' * 70}")
        train_features, val_features, test_features = build_variant_features(
            variant_name, orig_cache, masked_cache)
        print(f"  n_train: {n_train_original} original rows -> {len(train_features)} effective "
              f"training rows | n_val: {n_val_original} original rows -> {len(val_features)} "
              f"effective validation rows | n_test: {len(test_features)} (untouched, original-only)")

        test_metrics, test_true, test_pred = train_variant(
            variant_name, arms, author, train_features, val_features, test_features,
            bertopic_vec_size, sbert_dim,
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
            "n_train_original": n_train_original,
            "n_train_effective": len(train_features),
            "n_val_original": n_val_original,
            "n_val_effective": len(val_features),
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
    if not os.path.exists(RESULTS_FILE):
        raise FileNotFoundError(f"'{RESULTS_FILE}' not found - run --author for all 3 authors first.")
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    missing = [a for a in AUTHORS if a not in all_results]
    if missing:
        print(f"[!] WARNING: results missing for author(s) {missing} - table below is "
              f"partial/incomplete until all 3 authors have been run.")

    rows = []
    for variant_name in ALL_VARIANTS_ORDER:
        per_author = {}
        for author in AUTHORS:
            if author in all_results and variant_name in all_results[author]:
                per_author[author] = all_results[author][variant_name]
        if not per_author:
            continue
        avg_recall = float(np.mean([v["recall_true_narrative"] for v in per_author.values()]))
        avg_rw_pct = float(np.mean([v["pct_misclassified_right_wing"] for v in per_author.values()]))
        avg_macro_f1 = float(np.mean([v["macro_f1"] for v in per_author.values()]))
        row = {
            "variant": variant_name,
            "IDF_recall": per_author.get("IDF", {}).get("recall_true_narrative"),
            "Maria_recall": per_author.get("MariaZakharova", {}).get("recall_true_narrative"),
            "Bernie_recall": per_author.get("BernieSanders", {}).get("recall_true_narrative"),
            "avg_recall": avg_recall,
            "Bernie_to_RW": per_author.get("BernieSanders", {}).get("pct_misclassified_right_wing"),
            "avg_pct_right_wing": avg_rw_pct,
            "avg_macro_f1": avg_macro_f1,
        }
        for author in AUTHORS:
            if author in per_author:
                row[f"{author}_accuracy"] = per_author[author]["accuracy"]
                row[f"{author}_macro_f1"] = per_author[author]["macro_f1"]
                row[f"{author}_pct_right_wing"] = per_author[author]["pct_misclassified_right_wing"]
        rows.append(row)

    df = pd.DataFrame(rows)
    print("\n" + "=" * 100)
    print("ENTITY-MASKING AUGMENTATION TEST SUMMARY (primary metrics):")
    print("=" * 100)
    display_cols = ["variant", "IDF_recall", "Maria_recall", "Bernie_recall", "avg_recall", "Bernie_to_RW"]
    print(df[display_cols].to_string(index=False))

    os.makedirs(REPORT_DIR, exist_ok=True)
    df.to_csv(SUMMARY_FILE, index=False, encoding="utf-8-sig")
    print(f"\nSaved summary table to '{SUMMARY_FILE}'.")

    _print_analysis(all_results)
    return df


def _get(all_results, author, variant, field):
    return all_results.get(author, {}).get(variant, {}).get(field)


def _print_analysis(all_results):
    print("\n" + "=" * 100)
    print("ANALYSIS")
    print("=" * 100)

    print("\n1) Does Bernie's Right-wing bias drop for masked_aug vs. original?")
    for variant in ("sbert_original", "sbert_masked_only", "sbert_masked_aug", "sbert_masked_aug_soft_topic"):
        v = _get(all_results, "BernieSanders", variant, "pct_misclassified_right_wing")
        r = _get(all_results, "BernieSanders", variant, "recall_true_narrative")
        if v is not None:
            print(f"   {variant:32s} Bernie->RW={v * 100:5.1f}%   Bernie recall={r * 100:5.1f}%")

    print("\n2) Is IDF/Maria degradation SMALLER for masked_aug than for masked_only (vs. original)?")
    for author in ("IDF", "MariaZakharova"):
        orig_r = _get(all_results, author, "sbert_original", "recall_true_narrative")
        masked_r = _get(all_results, author, "sbert_masked_only", "recall_true_narrative")
        aug_r = _get(all_results, author, "sbert_masked_aug", "recall_true_narrative")
        if None not in (orig_r, masked_r, aug_r):
            print(f"   {author}: original={orig_r * 100:.1f}% | masked_only={masked_r * 100:.1f}% "
                  f"(delta {100 * (masked_r - orig_r):+.1f}pp) | masked_aug={aug_r * 100:.1f}% "
                  f"(delta {100 * (aug_r - orig_r):+.1f}pp)")

    print("\n3) Does the duplicated-original CONTROL (no masking) give a similar improvement to "
          "masked_aug? If so, the effect is not (only) about masking.")
    for author in AUTHORS:
        orig_r = _get(all_results, author, "sbert_original", "recall_true_narrative")
        dup_r = _get(all_results, author, "sbert_duplicated_original_control", "recall_true_narrative")
        aug_r = _get(all_results, author, "sbert_masked_aug", "recall_true_narrative")
        if None not in (orig_r, dup_r, aug_r):
            print(f"   {author}: original={orig_r * 100:.1f}% | duplicated_control={dup_r * 100:.1f}% "
                  f"(delta {100 * (dup_r - orig_r):+.1f}pp) | masked_aug={aug_r * 100:.1f}% "
                  f"(delta {100 * (aug_r - orig_r):+.1f}pp)")
    for author in ("BernieSanders",):
        orig_rw = _get(all_results, author, "sbert_original", "pct_misclassified_right_wing")
        dup_rw = _get(all_results, author, "sbert_duplicated_original_control", "pct_misclassified_right_wing")
        aug_rw = _get(all_results, author, "sbert_masked_aug", "pct_misclassified_right_wing")
        if None not in (orig_rw, dup_rw, aug_rw):
            print(f"   {author} ->Right-wing: original={orig_rw * 100:.1f}% | "
                  f"duplicated_control={dup_rw * 100:.1f}% (delta {100 * (dup_rw - orig_rw):+.1f}pp) | "
                  f"masked_aug={aug_rw * 100:.1f}% (delta {100 * (aug_rw - orig_rw):+.1f}pp)")

    print("\n4) Author-dependence check - does augmentation affect the 3 authors differently?")
    for author in AUTHORS:
        orig_r = _get(all_results, author, "sbert_original", "recall_true_narrative")
        aug_r = _get(all_results, author, "sbert_masked_aug", "recall_true_narrative")
        if None not in (orig_r, aug_r):
            print(f"   {author}: masked_aug vs. original recall delta = {100 * (aug_r - orig_r):+.1f}pp")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entity-Masking Augmentation Test (Experiment 23) for Narrative "
                     "Classification on unseen (LOAO) authors."
    )
    parser.add_argument("--author", choices=AUTHORS, default=None,
                         help="Build augmented/control feature sets + train/evaluate the 3 "
                              "new variants (and reuse the 3 existing section-21 variants) "
                              "for this held-out author.")
    parser.add_argument("--aggregate", action="store_true",
                         help="Print + save the cross-author summary table and analysis "
                              "after all 3 authors have been run.")
    args = parser.parse_args()

    if args.author:
        run_author(args.author)
    elif args.aggregate:
        aggregate()
    else:
        parser.print_help()

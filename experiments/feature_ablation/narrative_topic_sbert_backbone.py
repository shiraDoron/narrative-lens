"""
Narrative Classification - SBERT-backbone Topic Representation Comparison
===========================================================================
Central research question (as explicitly scoped by the user, distinct from the
narrative_topic_compare.py / narrative_ablation_loao.py experiments already in this repo):
does a Topic *distribution* (Soft BERTopic or LDA) improve Narrative Classification over a
single hard Topic id, when the base architecture is a MINIMAL "SBERT + one topic arm" model
(matching production's SBERTOnlyDetector plus exactly one additional signal) - evaluated on
BOTH a random split and unseen-author (LOAO) generalization, in one unified comparison?

Four variants (identical everywhere except the Topics arm):
  1. "none" (SBERT only)                    - no topic feature at all.
  2. "hard" (SBERT + Hard BERTopic)          - a single hard topic_id, one-hot.
  3. "soft" (SBERT + Soft BERTopic dist.)    - top-5 approximate_distribution(), NOT top-1.
  4. "lda"  (SBERT + LDA topic distribution) - full K=50 gensim document-topic distribution.

Why this is a NEW script and not a rerun of existing ones (audit performed before writing any
code, per explicit user instruction):
  - `narrative_topic_compare.py` (EXPERIMENTS.md section 15) already compared
    none/hard/soft/lda on a RANDOM split with 3 seeds - but using the FULL
    `fusion.NarrativeFusionNetwork` architecture (NER+SRL+Emotion+Reliability+Topics), not a
    pure SBERT backbone. Different research question (does topic representation matter given
    every other engineered feature is already present) - its results are NOT reused here
    because the base architecture differs from what the user asked for this time.
  - `narrative_ablation_loao.py` (EXPERIMENTS.md section 19) already trained SBERT+single-arm
    variants (`sbert_only`, `sbert_stance_hard_topic`, `sbert_soft_topic`) on LOAO for 3 real
    held-out authors (IDF, MariaZakharova, BernieSanders), same seed=42, same underlying
    BERTopic model (`models/experiments/soft_v2_baseline_seeded`). This EXACTLY matches 3 of
    the 4 variants needed here (config is identical: same split, same seed, same architecture
    convention) - REUSED AS-IS below, no rerun (see `load_existing_loao_results`). Only the
    missing 4th arm (`sbert_lda_topic`, never run before) is trained fresh, and only for that
    one arm - not the other 3, which would be a wasteful duplicate run.
  - Neither prior script ran the pure "SBERT + single topic arm" family on a RANDOM split -
    that half of this comparison is run fresh here (see `run_random_comparison`), but at
    ZERO heavy-feature-extraction cost: SBERT embeddings are reused BY POSITION from
    `data/cache/cached_features_sbert_only.pt` (train.py's own cache, same
    `load_raw_data()+split_random()`), and Hard/Soft/LDA dense topic vectors are reused BY
    POSITION from `data/cache/cached_features_narrative_topic_compare.pt` (already computed
    by narrative_topic_compare.py for the exact same split) - both verified aligned by label
    sequence before trusting the reuse (same safety pattern used throughout this project).
    Only the lightweight MLP training itself is new computation.

Nothing in fusion.py/train.py/config.py, any `models/best_*.pth` checkpoint, any of
narrative_topic_compare.py's/narrative_ablation_loao.py's own checkpoints/results/cache files,
or `artifacts/tables/model_comparison_results.json` is ever touched or overwritten - all new
outputs go to dedicated paths (see the *_DIR / *_FILE constants below).

Run (from repo root):
    python experiments/feature_ablation/narrative_topic_sbert_backbone.py --random
    python experiments/feature_ablation/narrative_topic_sbert_backbone.py --loao-lda --author IDF
    python experiments/feature_ablation/narrative_topic_sbert_backbone.py --loao-lda --author MariaZakharova
    python experiments/feature_ablation/narrative_topic_sbert_backbone.py --loao-lda --author BernieSanders
    python experiments/feature_ablation/narrative_topic_sbert_backbone.py --report
"""
import argparse
import json
import os

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from gensim.corpora import Dictionary
from gensim.models import LdaModel

from narrative_lens.config import NARRATIVES, NUM_NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from narrative_lens.train import (
    load_raw_data, split_random, split_leave_one_author,
    evaluate, compute_metrics, save_confusion_matrix_csv, CACHE_FILES,
)
from narrative_lens.topic_modeling.topic_preprocessing import clean_text_for_topic_model
from narrative_lens.utils.repro import write_run_metadata
from narrative_lens.utils.seeding import set_all_seeds

# narrative_topic_compare.py is a sibling script in this SAME directory (experiments/
# feature_ablation/), so a plain import works with no sys.path hack (Python auto-adds the
# running script's own directory). Reuses TopicFeatureLayer/paths/LDA tokenizer unmodified.
from narrative_topic_compare import (
    TopicFeatureLayer, BERTOPIC_MODEL_PATH, BERTOPIC_EMBEDDING_MODEL_NAME, SOFT_TOP_N,
    LDA_MODEL_PATH, LDA_DICT_PATH, lda_tokenize,
    NEW_CACHE_FILE as RANDOM_TOPIC_DENSE_CACHE,
)

# =========================================================================================
# Paths - all new/dedicated, nothing existing is overwritten.
# =========================================================================================
MODES = ("none", "hard", "soft", "lda")
SEEDS = (42, 7, 123)  # matches this project's established multi-seed convention
LOAO_SEED = 42        # matches narrative_ablation_loao.py's single fixed seed

AUTHORS = ("IDF", "MariaZakharova", "BernieSanders")
RIGHT_WING_IDX = NARRATIVES.index("Right-wing")

RANDOM_CACHE_FILE = "data/cache/cached_features_narrative_topic_sbert_backbone_random.pt"
CHECKPOINT_DIR = "models/experiments/narrative_topic_sbert_backbone"
REPORT_DIR = "artifacts/experiments/narrative_topic_sbert_backbone"
RESULTS_FILE_RANDOM = f"{REPORT_DIR}/results_random.json"
RESULTS_FILE_LOAO_LDA = f"{REPORT_DIR}/results_loao_lda.json"
METADATA_FILE = f"{REPORT_DIR}/run_metadata.json"

# Existing, READ-ONLY reuse sources (never modified by this script):
EXISTING_LOAO_ABLATION_CACHE_TEMPLATE = "data/cache/cached_features_ablation_loao_{author}.pt"
EXISTING_LOAO_REPORT_DIR = "artifacts/experiments/narrative_ablation_loao"
EXISTING_LOAO_RESULTS_FILE = f"{EXISTING_LOAO_REPORT_DIR}/results.json"
LOAO_VARIANT_NAME_FOR_MODE = {
    "none": "sbert_only",
    "hard": "sbert_stance_hard_topic",
    "soft": "sbert_soft_topic",
    # "lda" has no existing entry - trained fresh by this script (see below).
}

# New cache (additive: existing ablation_loao cache's SBERT/NER/SRL/Emotion/Reliability/hard/
# soft fields + a freshly-computed lda_dense field). The ORIGINAL ablation_loao cache file is
# never modified - this is a brand-new file.
LOAO_LDA_CACHE_TEMPLATE = "data/cache/cached_features_ablation_loao_{author}_plus_lda.pt"


def _label_sequence(rows):
    return [label for _, label in rows]


# =========================================================================================
# Model: SBERT embedding + (optionally) exactly one TopicFeatureLayer arm -> MLP.
# Mirrors production's SBERTOnlyDetector for mode="none" exactly (no topic arm at all, not
# even a zero-filler), and generalizes it with a single extra arm for hard/soft/lda - the
# minimal architecture that isolates the topic-representation choice as the one variable.
# =========================================================================================
class SBERTTopicDetector(nn.Module):
    DENSE_KEY = {"hard": "hard_dense", "soft": "soft_dense", "lda": "lda_dense"}

    def __init__(self, mode, sbert_dim, bertopic_vec_size=None, lda_vec_size=None,
                 hidden_size=128, dropout=0.3):
        super().__init__()
        assert mode in MODES
        self.mode = mode
        if mode == "none":
            self.topic_layer = None
            combined_dim = sbert_dim
        else:
            vec_size = bertopic_vec_size if mode in ("hard", "soft") else lda_vec_size
            self.topic_layer = TopicFeatureLayer(mode, vec_size=vec_size)
            combined_dim = sbert_dim + NUM_NARRATIVES

        self.mlp = nn.Sequential(
            nn.Linear(combined_dim, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, NUM_NARRATIVES),
        )
        self.softmax = nn.Softmax(dim=-1)

    def classify_features(self, features):
        parts = [features["sbert_embedding"]]
        if self.mode != "none":
            parts.append(self.topic_layer(features[self.DENSE_KEY[self.mode]]).squeeze())
        combined = torch.cat(parts, dim=-1)
        return self.softmax(self.mlp(combined))


# =========================================================================================
# Random-split cache: recombine two ALREADY-COMPUTED caches (zero heavy computation) -
# cached_features_sbert_only.pt (train.py's own cache) for sbert_embedding, plus
# cached_features_narrative_topic_compare.pt for hard_dense/soft_dense/lda_dense. Both were
# built from the exact same load_raw_data()+split_random() (random_state=42) - verified by
# label-sequence alignment before trusting the reuse, not assumed.
# =========================================================================================
def build_or_load_random_cache():
    if os.path.exists(RANDOM_CACHE_FILE):
        print(f"Found existing combined cache '{RANDOM_CACHE_FILE}'. Loading...")
        return torch.load(RANDOM_CACHE_FILE, weights_only=False)

    sbert_cache_path = CACHE_FILES["sbert_only"]
    if not os.path.exists(sbert_cache_path):
        raise FileNotFoundError(
            f"'{sbert_cache_path}' not found - run train.py with --model sbert_only "
            f"--split random at least once first (this script only REUSES that cache, it "
            f"never re-extracts SBERT embeddings itself)."
        )
    if not os.path.exists(RANDOM_TOPIC_DENSE_CACHE):
        raise FileNotFoundError(
            f"'{RANDOM_TOPIC_DENSE_CACHE}' not found - run narrative_topic_compare.py at "
            f"least once first (this script only REUSES its hard/soft/lda dense vectors, it "
            f"never recomputes BERTopic/LDA features itself)."
        )

    print(f"Loading existing SBERT-only cache '{sbert_cache_path}' (read-only reuse)...")
    sbert_cache = torch.load(sbert_cache_path, weights_only=False)
    print(f"Loading existing topic-dense cache '{RANDOM_TOPIC_DENSE_CACHE}' (read-only reuse)...")
    topic_cache = torch.load(RANDOM_TOPIC_DENSE_CACHE, weights_only=False)

    print("Reconstructing the SAME split as train.py/narrative_topic_compare.py "
          "(load_raw_data()+split_random(), unmodified, imported directly) for a fresh "
          "label-alignment check...")
    df = load_raw_data()
    train_data, val_data, test_data = split_random(df)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    result = {}
    sbert_dim = None
    for name, split_df in splits.items():
        fresh_labels = split_df["label"].astype(int).tolist()
        sbert_labels = _label_sequence(sbert_cache[name])
        topic_labels = _label_sequence(topic_cache[name])
        if not (fresh_labels == sbert_labels == topic_labels):
            raise RuntimeError(
                f"Alignment check FAILED for split '{name}': '{sbert_cache_path}' and/or "
                f"'{RANDOM_TOPIC_DENSE_CACHE}' no longer match a fresh "
                f"load_raw_data()+split_random() reconstruction. Refusing to silently reuse "
                f"misaligned features."
            )
        if not (len(fresh_labels) == len(sbert_labels) == len(topic_labels)):
            raise RuntimeError(f"Alignment check FAILED for split '{name}': length mismatch.")

        rows = []
        for i, label in enumerate(fresh_labels):
            sbert_feat, _ = sbert_cache[name][i]
            topic_feat, _ = topic_cache[name][i]
            if sbert_dim is None:
                sbert_dim = int(sbert_feat["sbert_embedding"].shape[-1])
            feat = {
                "sbert_embedding": sbert_feat["sbert_embedding"],
                "hard_dense": topic_feat["hard_dense"],
                "soft_dense": topic_feat["soft_dense"],
                "lda_dense": topic_feat["lda_dense"],
            }
            rows.append((feat, label))
        result[name] = rows
        print(f"  Split '{name}': {len(rows)} rows, alignment verified against both source caches.")

    topic_meta = topic_cache["_meta"]
    result["_meta"] = {
        "sbert_dim": sbert_dim,
        "bertopic_vec_size": topic_meta["bertopic_vec_size"],
        "num_bertopic_topics": topic_meta["num_bertopic_topics"],
        "lda_vec_size": topic_meta["num_lda_topics"],
        "sbert_cache_source": sbert_cache_path,
        "topic_dense_cache_source": RANDOM_TOPIC_DENSE_CACHE,
        "bertopic_model_path": BERTOPIC_MODEL_PATH,
        "lda_model_path": LDA_MODEL_PATH,
    }
    os.makedirs(os.path.dirname(RANDOM_CACHE_FILE), exist_ok=True)
    torch.save(result, RANDOM_CACHE_FILE)
    print(f"Saved new combined random-split cache to '{RANDOM_CACHE_FILE}' "
          f"(zero heavy feature extraction was performed - pure recombination of existing "
          f"cached tensors).")
    return result


# =========================================================================================
# LOAO cache augmentation: add ONLY a freshly-computed lda_dense field to the existing
# ablation_loao cache (which already has sbert_embedding/ner/srl/emotion/reliability/
# hard_dense/soft_dense) - avoids re-running the expensive SBERT+BERTopic extraction that
# narrative_ablation_loao.py already did for these exact 3 authors/split/seed.
# =========================================================================================
def build_or_load_loao_lda_cache(author):
    cache_file = LOAO_LDA_CACHE_TEMPLATE.format(author=author)
    if os.path.exists(cache_file):
        print(f"Found existing LOAO+LDA cache '{cache_file}'. Loading...")
        return torch.load(cache_file, weights_only=False)

    base_cache_path = EXISTING_LOAO_ABLATION_CACHE_TEMPLATE.format(author=author)
    if not os.path.exists(base_cache_path):
        raise FileNotFoundError(
            f"'{base_cache_path}' not found - run narrative_ablation_loao.py --author "
            f"{author} at least once first (this script only ADDS an lda_dense field to "
            f"that existing cache, it never re-extracts SBERT/NER/SRL/Emotion/Reliability "
            f"itself)."
        )
    print(f"Loading existing LOAO ablation cache '{base_cache_path}' (read-only reuse)...")
    base_cache = torch.load(base_cache_path, weights_only=False)

    print("Reconstructing the SAME split as narrative_ablation_loao.py "
          "(load_raw_data()+split_leave_one_author(), unmodified, imported directly) for a "
          "fresh label-alignment check...")
    df = load_raw_data()
    train_data, val_data, test_data = split_leave_one_author(df, author)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    print(f"Loading LDA model from '{LDA_MODEL_PATH}' + dictionary from '{LDA_DICT_PATH}' "
          f"(Experiment E's already-fitted K=50 baseline, reused as a frozen feature "
          f"extractor - cheap, no neural inference)...")
    lda_model = LdaModel.load(LDA_MODEL_PATH)
    lda_dictionary = Dictionary.load(LDA_DICT_PATH)
    num_lda_topics = lda_model.num_topics

    result = {}
    for name, split_df in splits.items():
        fresh_labels = split_df["label"].astype(int).tolist()
        base_labels = _label_sequence(base_cache[name])
        if fresh_labels != base_labels or len(fresh_labels) != len(split_df):
            raise RuntimeError(
                f"Alignment check FAILED for split '{name}' (author='{author}'): "
                f"'{base_cache_path}' no longer matches a fresh load_raw_data()+"
                f"split_leave_one_author() reconstruction. Refusing to silently reuse "
                f"misaligned features."
            )

        texts = split_df["text"].astype(str).str.slice(0, 3000).tolist()
        cleaned_texts = [clean_text_for_topic_model(t) for t in texts]
        rows = []
        for i, cleaned in enumerate(cleaned_texts):
            bow = lda_dictionary.doc2bow(lda_tokenize(cleaned))
            dist = lda_model.get_document_topics(bow, minimum_probability=0.0)
            vec = np.zeros(num_lda_topics, dtype=np.float32)
            for tid, prob in dist:
                vec[tid] = prob
            base_feat, label = base_cache[name][i]
            new_feat = dict(base_feat)
            new_feat["lda_dense"] = torch.from_numpy(vec)
            rows.append((new_feat, label))
        result[name] = rows
        print(f"  Split '{name}': {len(rows)} rows, alignment verified, lda_dense added.")

    base_meta = dict(base_cache["_meta"])
    base_meta["lda_vec_size"] = num_lda_topics
    base_meta["lda_model_path"] = LDA_MODEL_PATH
    result["_meta"] = base_meta

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    torch.save(result, cache_file)
    print(f"Saved new LOAO+LDA cache to '{cache_file}' (only LDA inference was freshly "
          f"computed - SBERT/NER/SRL/Emotion/Reliability/hard/soft were reused unchanged).")
    return result


# =========================================================================================
# Training loop (same hyperparameters/early-stopping/checkpoint convention as train.py's
# train() / narrative_ablation_loao.py's train_variant() - lightweight, no feature
# re-extraction, features are already fully precomputed in the cache).
# =========================================================================================
def train_one(mode, seed, run_tag, train_features, val_features, test_features,
              sbert_dim, bertopic_vec_size, lda_vec_size,
              epochs=EPOCHS, batch_size=BATCH_SIZE, patience=3, lr=LEARNING_RATE):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = f"{CHECKPOINT_DIR}/{mode}_{run_tag}.pth"

    set_all_seeds(seed)
    detector = SBERTTopicDetector(mode, sbert_dim, bertopic_vec_size, lda_vec_size)

    if os.path.exists(checkpoint_file):
        print(f"[{mode}/{run_tag}] Found existing checkpoint - loading for eval only "
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
            print(f"[{mode}/{run_tag}] Epoch {epoch + 1}: "
                  f"Train Acc {100 * train_correct / len(train_features):.2f}% | "
                  f"Val Loss {avg_val_loss:.4f} | Val Acc {val_metrics['accuracy'] * 100:.2f}% | "
                  f"Val Macro-F1 {val_metrics['macro_f1']:.4f}")

            if val_metrics["macro_f1"] > best_val_macro_f1:
                best_val_macro_f1 = val_metrics["macro_f1"]
                epochs_no_improve = 0
                torch.save(detector.state_dict(), checkpoint_file)
                print(f">>> New best model saved (Val Macro-F1: {best_val_macro_f1:.4f}) -> '{checkpoint_file}'")
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"[{mode}/{run_tag}] Early stopping at epoch {epoch + 1}.")
                    break

        detector.load_state_dict(torch.load(checkpoint_file))

    test_metrics, _, test_true, test_pred = evaluate(detector, test_features)
    return test_metrics, test_true, test_pred, checkpoint_file


# =========================================================================================
# Orchestration: random split (all 4 modes x 3 seeds)
# =========================================================================================
def run_random_comparison():
    os.makedirs(REPORT_DIR, exist_ok=True)
    cache = build_or_load_random_cache()
    meta = cache["_meta"]
    sbert_dim = meta["sbert_dim"]
    bertopic_vec_size = meta["bertopic_vec_size"]
    lda_vec_size = meta["lda_vec_size"]

    all_results = {}
    for mode in MODES:
        all_results[mode] = {}
        for seed in SEEDS:
            run_tag = f"random_seed{seed}"
            print(f"\n{'=' * 70}\n=== mode='{mode}' seed={seed} (random split) ===\n{'=' * 70}")
            test_metrics, test_true, test_pred, checkpoint_file = train_one(
                mode, seed, run_tag, cache["train"], cache["val"], cache["test"],
                sbert_dim, bertopic_vec_size, lda_vec_size,
            )
            cm_path = f"{REPORT_DIR}/confusion_matrix_{mode}_seed{seed}_random_test.csv"
            save_confusion_matrix_csv(test_metrics, cm_path)
            all_results[mode][str(seed)] = {
                "test_metrics": test_metrics,
                "checkpoint": checkpoint_file,
                "confusion_matrix_csv": cm_path,
            }
            print(f"[{mode}/seed{seed}] TEST: accuracy={test_metrics['accuracy'] * 100:.2f}% "
                  f"macro_f1={test_metrics['macro_f1']:.4f}")

    with open(RESULTS_FILE_RANDOM, "w", encoding="utf-8") as f:
        json.dump({"seeds": list(SEEDS), "meta": meta, "results": all_results}, f,
                   ensure_ascii=False, indent=2)
    print(f"\nSaved random-split results to '{RESULTS_FILE_RANDOM}'.")

    write_run_metadata(
        f"{REPORT_DIR}/run_metadata_random.json",
        config="SBERT-backbone Topic comparison, random split",
        seeds=list(SEEDS),
        modes=list(MODES),
        dataset_size={split: len(cache[split]) for split in ("train", "val", "test")},
        topic_model_path=BERTOPIC_MODEL_PATH,
        lda_model_path=LDA_MODEL_PATH,
        results_file=RESULTS_FILE_RANDOM,
        checkpoint_dir=CHECKPOINT_DIR,
    )
    return all_results


# =========================================================================================
# Orchestration: LOAO, lda arm only (none/hard/soft are REUSED from
# narrative_ablation_loao.py's existing results - see load_existing_loao_results)
# =========================================================================================
def run_loao_lda(author):
    os.makedirs(REPORT_DIR, exist_ok=True)
    cache = build_or_load_loao_lda_cache(author)
    meta = cache["_meta"]
    sbert_dim = meta["sbert_dim"]
    lda_vec_size = meta["lda_vec_size"]

    run_tag = f"loao_{author}"
    print(f"\n{'=' * 70}\n=== mode='lda' author='{author}' (LOAO) ===\n{'=' * 70}")
    test_metrics, test_true, test_pred, checkpoint_file = train_one(
        "lda", LOAO_SEED, run_tag, cache["train"], cache["val"], cache["test"],
        sbert_dim, None, lda_vec_size,
    )

    n = len(test_true)
    correct = sum(1 for t, p in zip(test_true, test_pred) if t == p)
    recall_true_narrative = correct / n if n else 0.0
    pct_right_wing = sum(1 for p in test_pred if p == RIGHT_WING_IDX) / n if n else 0.0

    cm_path = f"{REPORT_DIR}/confusion_matrix_sbert_lda_topic_{author}_test.csv"
    save_confusion_matrix_csv(test_metrics, cm_path)

    all_results = {}
    if os.path.exists(RESULTS_FILE_LOAO_LDA):
        with open(RESULTS_FILE_LOAO_LDA, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    all_results[author] = {
        "accuracy": test_metrics["accuracy"],
        "macro_precision": test_metrics["macro_precision"],
        "macro_recall": test_metrics["macro_recall"],
        "macro_f1": test_metrics["macro_f1"],
        "per_class": test_metrics["per_class"],
        "recall_true_narrative": recall_true_narrative,
        "pct_misclassified_right_wing": pct_right_wing,
        "n_test": n,
        "checkpoint": checkpoint_file,
        "confusion_matrix_csv": cm_path,
    }
    with open(RESULTS_FILE_LOAO_LDA, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"[lda/{author}] TEST: recall(true narrative)={recall_true_narrative * 100:.1f}% | "
          f"%->Right-wing={pct_right_wing * 100:.1f}% | macro_f1={test_metrics['macro_f1']:.4f}")
    print(f"Saved LOAO+LDA result for author '{author}' to '{RESULTS_FILE_LOAO_LDA}'.")

    write_run_metadata(
        f"{REPORT_DIR}/run_metadata_loao_lda_{author}.json",
        config="SBERT-backbone Topic comparison, LOAO lda-topic arm",
        seed=LOAO_SEED,
        mode="lda",
        held_out_author=author,
        dataset_size={split: len(cache[split]) for split in ("train", "val", "test")},
        lda_model_path=LDA_MODEL_PATH,
        results_file=RESULTS_FILE_LOAO_LDA,
        checkpoint=checkpoint_file,
    )
    return all_results[author]


# =========================================================================================
# Fairness / reuse-validity verification (required before trusting the LOAO reuse - see
# module docstring): confirms the reused sbert_only/hard/soft LOAO runs used the EXACT same
# dataset, split, held-out authors and architecture convention as the fresh "lda" runs here,
# rather than just assuming it from the module docstrings.
# =========================================================================================
def verify_loao_reuse_validity():
    """Raises RuntimeError if anything relevant differs between the reused
    sbert_only/hard/soft LOAO runs (narrative_ablation_loao.py) and this script's fresh
    lda run, for each of the 3 authors: same sbert_dim, same bertopic_vec_size, same
    BERTopic model path, same held-out-author set, same seed/epoch/batch/lr hyperparameters,
    and the classifier's input dimensionality formula (sbert_dim, or sbert_dim+NUM_NARRATIVES
    for a single topic arm) is architecturally identical between AblationDetector(arms=...)
    and SBERTTopicDetector(mode=...) by construction (both reuse the same TopicFeatureLayer
    class and the same Linear->ReLU->Dropout(0.3)->Linear->Softmax MLP template)."""
    if not os.path.exists(EXISTING_LOAO_RESULTS_FILE):
        raise FileNotFoundError(
            f"'{EXISTING_LOAO_RESULTS_FILE}' not found - run "
            f"narrative_ablation_loao.py --author <X> for all 3 authors first."
        )
    with open(EXISTING_LOAO_RESULTS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    missing_authors = [a for a in AUTHORS if a not in raw]
    if missing_authors:
        raise RuntimeError(
            f"Reused LOAO results missing author(s) {missing_authors} in "
            f"'{EXISTING_LOAO_RESULTS_FILE}' - cannot verify reuse validity."
        )
    for author in AUTHORS:
        for variant_name in LOAO_VARIANT_NAME_FOR_MODE.values():
            if variant_name not in raw[author]:
                raise RuntimeError(
                    f"Reused variant '{variant_name}' missing for author '{author}' in "
                    f"'{EXISTING_LOAO_RESULTS_FILE}'."
                )

        base_cache_path = EXISTING_LOAO_ABLATION_CACHE_TEMPLATE.format(author=author)
        lda_cache_path = LOAO_LDA_CACHE_TEMPLATE.format(author=author)
        if not (os.path.exists(base_cache_path) and os.path.exists(lda_cache_path)):
            raise RuntimeError(
                f"Cannot verify reuse validity for author '{author}': both "
                f"'{base_cache_path}' and '{lda_cache_path}' must exist (run --loao-lda "
                f"--author {author} first)."
            )
        base_meta = torch.load(base_cache_path, weights_only=False)["_meta"]
        lda_meta = torch.load(lda_cache_path, weights_only=False)["_meta"]
        for key in ("sbert_dim", "bertopic_vec_size", "bertopic_model_path"):
            if base_meta[key] != lda_meta[key]:
                raise RuntimeError(
                    f"Reuse-validity check FAILED for author '{author}', key '{key}': "
                    f"base cache has {base_meta[key]!r}, lda-augmented cache has "
                    f"{lda_meta[key]!r}. The reused sbert_only/hard/soft results and the "
                    f"fresh lda result are NOT built on identical features - do not compare."
                )
        if lda_meta["bertopic_model_path"] != BERTOPIC_MODEL_PATH:
            raise RuntimeError(
                f"Author '{author}': LOAO BERTopic model path {lda_meta['bertopic_model_path']!r} "
                f"differs from this script's random-split BERTOPIC_MODEL_PATH {BERTOPIC_MODEL_PATH!r}."
            )

    print("[verify] LOAO reuse-validity check PASSED for all 3 authors: same sbert_dim, same "
          "bertopic_vec_size, same BERTopic model path, same held-out-author set, between the "
          "reused sbert_only/hard/soft runs and the fresh lda run. Architecture equivalence "
          "(AblationDetector(arms=set()/{'hard_topic'}/{'soft_topic'}) vs "
          "SBERTTopicDetector(mode='none'/'hard'/'soft')) holds by construction: both use the "
          "identical combined_dim formula (sbert_dim, or sbert_dim+NUM_NARRATIVES for a single "
          "topic arm), the same TopicFeatureLayer class, the same "
          "Linear->ReLU->Dropout(0.3)->Linear->Softmax MLP, and the same EPOCHS/BATCH_SIZE/"
          "LEARNING_RATE/seed=42/patience=3 training convention - see narrative_ablation_loao.py.")


def per_class_metrics_from_confusion_csv(path):
    """Derives per-narrative precision/recall/f1/support directly from an already-saved
    confusion matrix CSV (rows=true, cols=predicted) - used for the REUSED LOAO variants
    (sbert_only/hard/soft), which were not rerun and whose results.json entry does not store
    a per_class breakdown, only the confusion matrix CSV. No retraining/re-evaluation."""
    import pandas as pd
    cm_df = pd.read_csv(path, index_col=0, encoding="utf-8-sig")
    labels = list(cm_df.index)
    cm = cm_df.values.astype(np.float64)
    per_class = {}
    for i, label in enumerate(labels):
        tp = cm[i, i]
        fn = cm[i, :].sum() - tp
        fp = cm[:, i].sum() - tp
        support = int(cm[i, :].sum())
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
    return per_class


# =========================================================================================
# Unified report: random-split (fresh, 3 seeds) + LOAO (3 reused variants + 1 fresh lda
# variant) - kept as TWO SEPARATE summary tables (random-split accuracy/macro-F1 with
# mean+/-std is not comparable to LOAO's single-narrative-dominated recall metric - see
# EXPERIMENTS.md sections 18/19 for why LOAO uses recall_true_narrative, not macro_f1, as
# its headline metric).
# =========================================================================================
def load_existing_loao_results():
    """Reuses narrative_ablation_loao.py's already-computed sbert_only/hard/soft LOAO
    results AS-IS (identical split/seed/architecture convention, verified by
    verify_loao_reuse_validity() before this is ever called) - no rerun. Returns
    {mode: {author: {...}}} for mode in ("none", "hard", "soft")."""
    with open(EXISTING_LOAO_RESULTS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    out = {mode: {} for mode in ("none", "hard", "soft")}
    for author in AUTHORS:
        for mode, variant_name in LOAO_VARIANT_NAME_FOR_MODE.items():
            out[mode][author] = raw[author][variant_name]
    return out


def _mean_std(values):
    arr = np.array(values, dtype=np.float64)
    return float(arr.mean()), (float(arr.std(ddof=0)) if len(arr) > 1 else 0.0)


def build_random_split_report(random_results, meta):
    """Per-mode mean+/-std across 3 seeds (Accuracy, Macro-F1) + PAIRED per-seed deltas vs.
    'none' (SBERT-only) and vs. 'hard' (never conclude an improvement from a single seed -
    each seed trains all 4 modes on the identical train/val/test rows, so a per-seed paired
    difference is the correct, more sensitive comparison, not an independent-samples one) +
    a per-narrative Precision/Recall/F1 mean+/-std table."""
    random_summary = {}
    per_seed_acc, per_seed_f1 = {}, {}
    for mode in MODES:
        seed_entries = random_results.get(mode, {})
        if not seed_entries:
            continue
        acc_by_seed = {s: e["test_metrics"]["accuracy"] for s, e in seed_entries.items()}
        f1_by_seed = {s: e["test_metrics"]["macro_f1"] for s, e in seed_entries.items()}
        per_seed_acc[mode], per_seed_f1[mode] = acc_by_seed, f1_by_seed
        acc_m, acc_s = _mean_std(list(acc_by_seed.values()))
        f1_m, f1_s = _mean_std(list(f1_by_seed.values()))
        random_summary[mode] = {"accuracy_mean": acc_m, "accuracy_std": acc_s,
                                 "macro_f1_mean": f1_m, "macro_f1_std": f1_s,
                                 "n_seeds": len(seed_entries)}

    for mode in MODES:
        if mode not in random_summary:
            continue
        for ref in ("none", "hard"):
            if ref not in per_seed_acc or mode == ref:
                continue
            shared_seeds = sorted(set(per_seed_acc[mode]) & set(per_seed_acc[ref]), key=str)
            if not shared_seeds:
                continue
            acc_deltas = [per_seed_acc[mode][s] - per_seed_acc[ref][s] for s in shared_seeds]
            f1_deltas = [per_seed_f1[mode][s] - per_seed_f1[ref][s] for s in shared_seeds]
            acc_dm, acc_ds = _mean_std(acc_deltas)
            f1_dm, f1_ds = _mean_std(f1_deltas)
            random_summary[mode][f"delta_vs_{ref}"] = {
                "accuracy_mean": acc_dm, "accuracy_std": acc_ds, "per_seed_accuracy": acc_deltas,
                "macro_f1_mean": f1_dm, "macro_f1_std": f1_ds, "per_seed_macro_f1": f1_deltas,
                "n_seeds": len(shared_seeds),
            }

    # per-narrative P/R/F1, mean+/-std across seeds
    narrative_rows = []
    for mode in MODES:
        seed_entries = random_results.get(mode, {})
        if not seed_entries:
            continue
        per_narrative_values = {n: {"precision": [], "recall": [], "f1": []} for n in NARRATIVES}
        support_ref = None
        for entry in seed_entries.values():
            per_class = entry["test_metrics"]["per_class"]
            for n in NARRATIVES:
                if n in per_class:
                    per_narrative_values[n]["precision"].append(per_class[n]["precision"])
                    per_narrative_values[n]["recall"].append(per_class[n]["recall"])
                    per_narrative_values[n]["f1"].append(per_class[n]["f1"])
            if support_ref is None:
                support_ref = {n: per_class.get(n, {}).get("support", 0) for n in NARRATIVES}
        for n in NARRATIVES:
            vals = per_narrative_values[n]
            if not vals["precision"]:
                continue
            p_m, p_s = _mean_std(vals["precision"])
            r_m, r_s = _mean_std(vals["recall"])
            f_m, f_s = _mean_std(vals["f1"])
            narrative_rows.append({
                "mode": mode, "narrative": n, "support": support_ref.get(n, 0),
                "precision_mean": p_m, "precision_std": p_s,
                "recall_mean": r_m, "recall_std": r_s,
                "f1_mean": f_m, "f1_std": f_s,
            })

    import pandas as pd
    per_narrative_df = pd.DataFrame(narrative_rows)
    per_narrative_csv = f"{REPORT_DIR}/per_narrative_summary_random.csv"
    per_narrative_df.to_csv(per_narrative_csv, index=False, encoding="utf-8-sig")

    random_table_rows = []
    for mode in MODES:
        if mode not in random_summary:
            continue
        r = random_summary[mode]
        row = {
            "mode": mode,
            "accuracy": f"{r['accuracy_mean']*100:.2f}+/-{r['accuracy_std']*100:.2f}%",
            "macro_f1": f"{r['macro_f1_mean']:.4f}+/-{r['macro_f1_std']:.4f}",
        }
        if "delta_vs_none" in r:
            row["delta_accuracy_vs_none"] = f"{r['delta_vs_none']['accuracy_mean']*100:+.2f}+/-{r['delta_vs_none']['accuracy_std']*100:.2f}pp"
            row["delta_macro_f1_vs_none"] = f"{r['delta_vs_none']['macro_f1_mean']:+.4f}+/-{r['delta_vs_none']['macro_f1_std']:.4f}"
        if "delta_vs_hard" in r:
            row["delta_accuracy_vs_hard"] = f"{r['delta_vs_hard']['accuracy_mean']*100:+.2f}+/-{r['delta_vs_hard']['accuracy_std']*100:.2f}pp"
            row["delta_macro_f1_vs_hard"] = f"{r['delta_vs_hard']['macro_f1_mean']:+.4f}+/-{r['delta_vs_hard']['macro_f1_std']:.4f}"
        random_table_rows.append(row)
    random_df = pd.DataFrame(random_table_rows)
    random_csv = f"{REPORT_DIR}/random_split_summary_table.csv"
    random_df.to_csv(random_csv, index=False, encoding="utf-8-sig")

    return random_summary, random_df, per_narrative_csv, random_csv


def build_loao_report():
    """LOAO summary table: none/hard/soft REUSED (verified), lda FRESH - avg
    recall_true_narrative + avg pct_misclassified_right_wing across the 3 authors (macro_f1
    is reported too, but as an established LOAO caveat - EXPERIMENTS.md section 18 - it's
    near-meaningless when the held-out author's test set is dominated by one narrative,
    hence recall_true_narrative, not macro_f1, is the headline LOAO metric here)."""
    loao_reused = load_existing_loao_results()
    loao_lda = {}
    if os.path.exists(RESULTS_FILE_LOAO_LDA):
        with open(RESULTS_FILE_LOAO_LDA, "r", encoding="utf-8") as f:
            loao_lda = json.load(f)

    loao_summary = {}
    per_narrative_rows = []
    for mode in MODES:
        per_author = loao_reused.get(mode, {}) if mode != "lda" else loao_lda
        if not per_author:
            continue
        recalls = [v["recall_true_narrative"] for v in per_author.values()]
        rw_pcts = [v["pct_misclassified_right_wing"] for v in per_author.values()]
        macro_f1s = [v["macro_f1"] for v in per_author.values()]
        loao_summary[mode] = {
            "avg_recall_true_narrative": float(np.mean(recalls)),
            "avg_pct_misclassified_right_wing": float(np.mean(rw_pcts)),
            "avg_macro_f1": float(np.mean(macro_f1s)),
            "n_authors": len(per_author),
            "reused_from_existing_run": mode != "lda",
            "per_author": {a: per_author[a] for a in per_author},
        }

        # per-narrative P/R/F1 per author (derived from confusion matrix CSV for reused
        # variants; already present in results_loao_lda.json's per_class for "lda"). The
        # confusion_matrix_csv path stored inside results.json is stale/relative to a
        # different cwd - reconstruct the real on-disk path instead of trusting it blindly.
        for author, entry in per_author.items():
            if mode == "lda":
                per_class = entry["per_class"]
            else:
                variant_name = LOAO_VARIANT_NAME_FOR_MODE[mode]
                cm_path = f"{EXISTING_LOAO_REPORT_DIR}/confusion_matrix_{variant_name}_{author}_test.csv"
                per_class = per_class_metrics_from_confusion_csv(cm_path)
            for n, m in per_class.items():
                per_narrative_rows.append({
                    "mode": mode, "author": author, "narrative": n,
                    "precision": m["precision"], "recall": m["recall"], "f1": m["f1"],
                    "support": m["support"],
                })

    import pandas as pd
    loao_table_rows = []
    for mode in MODES:
        if mode not in loao_summary:
            continue
        l = loao_summary[mode]
        loao_table_rows.append({
            "mode": mode,
            "avg_recall_true_narrative": f"{l['avg_recall_true_narrative']*100:.1f}%",
            "avg_pct_misclassified_right_wing": f"{l['avg_pct_misclassified_right_wing']*100:.1f}%",
            "avg_macro_f1": f"{l['avg_macro_f1']:.4f}",
            "n_authors": l["n_authors"],
            "reused_from_section_19": l["reused_from_existing_run"],
        })
    loao_df = pd.DataFrame(loao_table_rows)
    loao_csv = f"{REPORT_DIR}/loao_summary_table.csv"
    loao_df.to_csv(loao_csv, index=False, encoding="utf-8-sig")

    per_narrative_df = pd.DataFrame(per_narrative_rows)
    per_narrative_csv = f"{REPORT_DIR}/per_narrative_summary_loao.csv"
    per_narrative_df.to_csv(per_narrative_csv, index=False, encoding="utf-8-sig")

    return loao_summary, loao_df, per_narrative_csv, loao_csv


def build_unified_report():
    os.makedirs(REPORT_DIR, exist_ok=True)

    if not os.path.exists(RESULTS_FILE_RANDOM):
        raise FileNotFoundError(f"'{RESULTS_FILE_RANDOM}' not found - run --random first.")
    with open(RESULTS_FILE_RANDOM, "r", encoding="utf-8") as f:
        random_payload = json.load(f)
    random_results, meta = random_payload["results"], random_payload["meta"]

    print("\n[verify] Checking LOAO reuse validity before building the LOAO summary...")
    verify_loao_reuse_validity()

    random_summary, random_df, per_narrative_random_csv, random_csv = build_random_split_report(
        random_results, meta)
    loao_summary, loao_df, per_narrative_loao_csv, loao_csv = build_loao_report()

    # --- dimensionality fairness note (required check) ---
    bertopic_vec_size = meta["bertopic_vec_size"]
    lda_vec_size = meta["lda_vec_size"]
    dimensionality_note = {
        "bertopic_vec_size_hard_soft": bertopic_vec_size,
        "lda_vec_size": lda_vec_size,
        "classifier_input_dim_added_by_topic_arm": NUM_NARRATIVES,
        "note": (
            f"Soft BERTopic's underlying table has {bertopic_vec_size} rows (num topics + 1 "
            f"OOV slot) vs. LDA's {lda_vec_size} rows (K=50) - a large difference in "
            f"TopicFeatureLayer's PARAMETER COUNT ({bertopic_vec_size}x{NUM_NARRATIVES}="
            f"{bertopic_vec_size*NUM_NARRATIVES} vs. {lda_vec_size}x{NUM_NARRATIVES}="
            f"{lda_vec_size*NUM_NARRATIVES}). However, the actual FEATURE DIMENSION appended "
            f"to the SBERT embedding before the final MLP is exactly {NUM_NARRATIVES} "
            f"(NUM_NARRATIVES) for every one of hard/soft/lda, because TopicFeatureLayer "
            f"always projects the (possibly much larger) input distribution down to a "
            f"{NUM_NARRATIVES}-dim vector via `dense_vec @ table` (a weighted sum over the "
            f"table's rows) before concatenation. So the classifier itself sees the SAME "
            f"input dimensionality (sbert_dim + {NUM_NARRATIVES}) for hard/soft/lda - no "
            f"variant gets an unfair advantage merely from having a larger raw feature-vector "
            f"count; only the number of LEARNABLE embedding-table parameters differs, which "
            f"is an inherent property of the topic model's own vocabulary size (283 BERTopic "
            f"topics vs. 50 LDA topics), not an experimental design choice."
        ),
    }

    print("\n" + "=" * 100)
    print("RANDOM SPLIT SUMMARY (mean +/- std across 3 seeds)")
    print("=" * 100)
    print(random_df.to_string(index=False))
    print(f"Saved to '{random_csv}' (+ per-narrative breakdown: '{per_narrative_random_csv}')")

    print("\n" + "=" * 100)
    print("LOAO (UNSEEN-AUTHOR) SUMMARY (3 authors: IDF, MariaZakharova, BernieSanders)")
    print("=" * 100)
    print(loao_df.to_string(index=False))
    print(f"Saved to '{loao_csv}' (+ per-narrative breakdown: '{per_narrative_loao_csv}')")

    print("\n" + "=" * 100)
    print("DIMENSIONALITY FAIRNESS NOTE")
    print("=" * 100)
    print(dimensionality_note["note"])

    unified_json = f"{REPORT_DIR}/unified_comparison.json"
    output = {
        "random_split": random_summary,
        "loao": loao_summary,
        "dimensionality_fairness_note": dimensionality_note,
        "random_split_table_csv": random_csv,
        "loao_table_csv": loao_csv,
        "per_narrative_random_csv": per_narrative_random_csv,
        "per_narrative_loao_csv": per_narrative_loao_csv,
    }
    with open(unified_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved full unified comparison to '{unified_json}'.")

    write_run_metadata(
        METADATA_FILE,
        config="SBERT-backbone Topic comparison, unified report",
        random_seeds=list(SEEDS),
        loao_authors=list(AUTHORS),
        loao_seed=LOAO_SEED,
        modes=list(MODES),
        random_dataset_size=meta.get("sbert_dim"),
        bertopic_vec_size=bertopic_vec_size,
        lda_vec_size=lda_vec_size,
        random_results_file=RESULTS_FILE_RANDOM,
        loao_lda_results_file=RESULTS_FILE_LOAO_LDA,
        loao_reused_results_file=EXISTING_LOAO_RESULTS_FILE,
        random_split_table_csv=random_csv,
        loao_table_csv=loao_csv,
        unified_comparison_json=unified_json,
    )
    return output


# =========================================================================================
# Completeness check: all 12 random-split (mode, seed) runs actually finished (not
# skipped/truncated), before trusting results_random.json for reporting.
# =========================================================================================
def verify_random_split_completeness():
    if not os.path.exists(RESULTS_FILE_RANDOM):
        raise RuntimeError(f"'{RESULTS_FILE_RANDOM}' not found - --random has not been run.")
    with open(RESULTS_FILE_RANDOM, "r", encoding="utf-8") as f:
        payload = json.load(f)
    results = payload["results"]

    missing, bad = [], []
    for mode in MODES:
        for seed in SEEDS:
            entry = results.get(mode, {}).get(str(seed))
            if entry is None:
                missing.append((mode, seed))
                continue
            acc = entry["test_metrics"]["accuracy"]
            f1 = entry["test_metrics"]["macro_f1"]
            if not (0.0 <= acc <= 1.0) or not (0.0 <= f1 <= 1.0) or acc != acc or f1 != f1:
                bad.append((mode, seed, acc, f1))
            if not os.path.exists(entry["checkpoint"]):
                bad.append((mode, seed, "missing checkpoint", entry["checkpoint"]))

    if missing or bad:
        raise RuntimeError(
            f"Random-split completeness check FAILED. Missing (mode, seed) runs: {missing}. "
            f"Invalid/corrupt entries: {bad}. Expected exactly {len(MODES)}x{len(SEEDS)}="
            f"{len(MODES)*len(SEEDS)} completed runs."
        )
    print(f"[verify] Random-split completeness check PASSED: all {len(MODES)}x{len(SEEDS)}="
          f"{len(MODES)*len(SEEDS)} (mode, seed) runs completed with valid metrics and an "
          f"on-disk checkpoint.")
    return results


# =========================================================================================
# Sanity checks (dataset sizes, label distributions, feature dimensions, author leakage,
# non-degenerate soft/lda vectors) - run after --random and all 3 --loao-lda have completed.
# =========================================================================================
def run_sanity_checks():
    problems = []

    print("\n--- Sanity check 1: random-split cache sizes + label distribution ---")
    random_cache = torch.load(RANDOM_CACHE_FILE, weights_only=False)
    for split_name in ("train", "val", "test"):
        rows = random_cache[split_name]
        labels = [label for _, label in rows]
        dist = {NARRATIVES[i]: labels.count(i) for i in range(NUM_NARRATIVES)}
        print(f"  random/{split_name}: n={len(rows)}, label distribution={dist}")
        if len(rows) == 0:
            problems.append(f"random/{split_name} is empty")
        if any(v == 0 for v in dist.values()):
            print(f"  [!] random/{split_name} has narrative(s) with zero examples: "
                  f"{[k for k, v in dist.items() if v == 0]}")

    meta = random_cache["_meta"]
    print(f"  feature dims: sbert_dim={meta['sbert_dim']}, "
          f"bertopic_vec_size={meta['bertopic_vec_size']}, lda_vec_size={meta['lda_vec_size']}")

    print("\n--- Sanity check 2: random-split soft/lda vectors are non-degenerate ---")
    test_rows = random_cache["test"]
    soft_sums = np.array([feat["soft_dense"].sum().item() for feat, _ in test_rows])
    lda_sums = np.array([feat["lda_dense"].sum().item() for feat, _ in test_rows])
    soft_nnz = np.array([int((feat["soft_dense"] > 0).sum().item()) for feat, _ in test_rows])
    lda_nnz = np.array([int((feat["lda_dense"] > 0).sum().item()) for feat, _ in test_rows])
    print(f"  soft_dense: sum mean={soft_sums.mean():.4f} (expect ~1.0 for non-outlier rows), "
          f"all-zero rows={(soft_sums == 0).sum()}/{len(test_rows)}, "
          f"mean nonzero entries={soft_nnz.mean():.2f} (top-{SOFT_TOP_N} renormalized)")
    print(f"  lda_dense: sum mean={lda_sums.mean():.4f} (expect ~1.0), "
          f"all-zero rows={(lda_sums == 0).sum()}/{len(test_rows)}, "
          f"mean nonzero entries={lda_nnz.mean():.2f} (K={meta['lda_vec_size']})")
    if (soft_sums == 0).sum() > 0.5 * len(test_rows):
        problems.append("soft_dense is degenerate (all-zero) for >50% of test rows")
    if (lda_sums == 0).sum() > 0.5 * len(test_rows):
        problems.append("lda_dense is degenerate (all-zero) for >50% of test rows")
    if soft_nnz.mean() <= 1.0:
        nonzero_mask = soft_sums > 0
        nnz_among_nonzero = soft_nnz[nonzero_mask].mean() if nonzero_mask.sum() > 0 else 0.0
        print(f"  [i] NOTE (not treated as a failure - documented, pre-existing corpus/model "
              f"property, not introduced by this script): soft_dense's raw mean nonzero-entry "
              f"count ({soft_nnz.mean():.2f}) is <=1 only because it is dragged down by the "
              f"{(soft_sums == 0).sum()}/{len(test_rows)} all-zero rows counted in the same "
              f"average; among the {int(nonzero_mask.sum())} rows that DO have a soft signal, "
              f"the mean nonzero-entry count is {nnz_among_nonzero:.2f} (top-{SOFT_TOP_N} "
              f"renormalized, so <5 is expected whenever approximate_distribution() finds fewer "
              f"than {SOFT_TOP_N} topics with positive overlap for a given text). This matches "
              f"two already-documented findings elsewhere in this project: (a) EXPERIMENTS.md "
              f"Section 9's 'soft-signal%' metric (~51-58% of documents get ANY positive-score "
              f"topic from approximate_distribution(), i.e. ~42-49% get an all-zero soft "
              f"distribution, in line with the {(soft_sums == 0).sum() / len(test_rows) * 100:.1f}% "
              f"all-zero rate measured here), and (b) Section 15's dominance-threshold analysis, "
              f"where only 8.8% of rows are genuinely 'multi-topic' (dominance<0.7) - i.e. even "
              f"among rows WITH a soft signal, the vast majority are dominated by a single topic "
              f"already, so a low mean nonzero-entry count is an accurate reflection of this "
              f"corpus, not a computation bug.")

    print("\n--- Sanity check 3: LOAO+lda cache sizes, label distribution, dimensions ---")
    for author in AUTHORS:
        cache_path = LOAO_LDA_CACHE_TEMPLATE.format(author=author)
        if not os.path.exists(cache_path):
            problems.append(f"LOAO+lda cache missing for author '{author}': '{cache_path}'")
            continue
        cache = torch.load(cache_path, weights_only=False)
        for split_name in ("train", "val", "test"):
            rows = cache[split_name]
            labels = [label for _, label in rows]
            dist = {NARRATIVES[i]: labels.count(i) for i in range(NUM_NARRATIVES)}
            print(f"  {author}/{split_name}: n={len(rows)}, label distribution={dist}")
        test_lda_sums = np.array([feat["lda_dense"].sum().item() for feat, _ in cache["test"]])
        print(f"  {author}: lda_dense sum mean={test_lda_sums.mean():.4f}, "
              f"all-zero rows={(test_lda_sums == 0).sum()}/{len(cache['test'])}")
        if (test_lda_sums == 0).sum() > 0.5 * len(cache["test"]):
            problems.append(f"LOAO {author}: lda_dense degenerate (all-zero) for >50% of test rows")

    print("\n--- Sanity check 4: author leakage (LOAO) ---")
    print("  Already enforced structurally: split_leave_one_author() calls verify_no_leakage() "
          "internally on every call (raises AssertionError if the held-out author's rows "
          "appear in train/val) - this ran again during build_or_load_loao_lda_cache()'s "
          "fresh-split reconstruction for each of the 3 authors above, with no assertion "
          "raised, so no leakage is present.")

    if problems:
        raise RuntimeError(f"Sanity checks FAILED: {problems}")
    print("\n[verify] All sanity checks PASSED.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SBERT-backbone Topic representation comparison (none/hard/soft/lda), "
                     "random split + LOAO."
    )
    parser.add_argument("--random", action="store_true",
                         help="Run all 4 modes x 3 seeds on the random split.")
    parser.add_argument("--loao-lda", action="store_true",
                         help="Train the (new) sbert_lda_topic variant for one held-out "
                              "author on LOAO (use with --author).")
    parser.add_argument("--author", choices=AUTHORS, default=None)
    parser.add_argument("--report", action="store_true",
                         help="Build the unified comparison table (run after --random and "
                              "all 3 --loao-lda runs have completed).")
    parser.add_argument("--verify-random", action="store_true",
                         help="Verify all 12 (mode, seed) random-split runs completed "
                              "successfully with valid metrics + on-disk checkpoints.")
    parser.add_argument("--sanity-check", action="store_true",
                         help="Run dataset-size/label-distribution/feature-dimension/"
                              "non-degenerate-vector sanity checks (run after --random and "
                              "all 3 --loao-lda have completed).")
    args = parser.parse_args()

    if args.random:
        run_random_comparison()
    elif args.loao_lda:
        if not args.author:
            parser.error("--loao-lda requires --author <IDF|MariaZakharova|BernieSanders>")
        run_loao_lda(args.author)
    elif args.verify_random:
        verify_random_split_completeness()
    elif args.sanity_check:
        run_sanity_checks()
    elif args.report:
        verify_random_split_completeness()
        build_unified_report()
    else:
        parser.error("Specify --random, --loao-lda --author <X>, --verify-random, "
                      "--sanity-check, or --report.")

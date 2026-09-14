"""
Narrative Classification — Entity Shortcut Test (Experiment 21)
=================================================================
Follow-up to EXPERIMENTS.md section 19 (LOAO feature ablation) and its Right-wing-shortcut
forensic analysis (narrative_ablation_rw_shortcut.py): that analysis found BernieSanders'
Right-wing-misclassified rows share the SAME top entities (trump, americans, congress,
america, republicans) with the Right-wing narrative's own training corpus - Bernie and
Right-wing discuss the same entities with OPPOSITE stance, and NER-based features encode
entity IDENTITY only (no stance), a plausible mechanism for the LOAO Right-wing shortcut.

This experiment asks directly: does entity IDENTITY (who is mentioned) - as opposed to WHAT
is said about that entity - drive a shortcut that harms generalization to an unseen author?
Method: entity MASKING. Every named entity mention (PER/ORG/LOC/MISC, per
dslim/bert-base-NER) is replaced by a generic placeholder token
("Trump criticized Biden" -> "[PERSON] criticized [PERSON]") before computing the SBERT
embedding - removing entity-identity information from the model's input while keeping
sentence structure, sentiment/stance language, and every other cue intact. If masking
identity out reduces the Right-wing-misclassification bias and/or improves recall of the
true/held-out narrative (relative to unmasked SBERT), that is evidence consistent with the
model partly relying on WHO is mentioned rather than what is said about them - not
conclusive proof of the mechanism, since other differences between masked and unmasked text
(e.g. slightly different sentence length/structure around the placeholder) are not ruled out.

Variants compared (same 3 LOAO authors, same split_leave_one_author logic, seed=42, as
section 19/20):
  1. sbert_only                     - REUSED verbatim from section 19's results.json (no
                                       entity information at all beyond whatever is
                                       implicit in the raw SBERT embedding of the
                                       ORIGINAL, unmasked text).
  2. sbert_ner                      - REUSED verbatim from section 19's results.json
                                       (SBERT on unmasked text + an explicit NER-identity
                                       arm on top - entity identity maximally present,
                                       both implicitly via the unmasked SBERT embedding
                                       and explicitly via the NER arm).
  3. sbert_masked (NEW)             - SBERT embedding computed on entity-MASKED text, no
                                       other arm. This is the PRIMARY comparison of this
                                       experiment: sbert_only (identity present,
                                       implicit) vs. sbert_masked (identity removed)
                                       isolates the effect of removing entity identity
                                       from the input text.
  4. sbert_soft_topic               - REUSED verbatim from section 19's results.json
                                       (SBERT on unmasked text + Soft Topic Distribution
                                       arm).
  5. sbert_masked_soft_topic (NEW)  - SBERT on entity-MASKED text + Soft Topic
                                       Distribution arm (tests whether Soft Topics can
                                       restore some narrative-relevant signal once entity
                                       identity is removed).

Why variants 1/2/4 are REUSED rather than retrained: they are architecturally IDENTICAL
(same AblationDetector class, same arms, same hyperparameters, same train/val/test split,
same seed=42) to section 19's own sbert_only/sbert_ner/sbert_soft_topic runs - retraining
would just reproduce the same numbers with sampling noise, not a genuinely new result.
Reused after verifying (see verify_reuse_validity()) that section 19's results.json
actually contains exactly these 3 variants for all 3 authors.

Masking mechanics: entity spans come from EntityAnalysisPipeline.extract_raw_entities()
(narrative_lens/features/ner.py, unmodified, already used elsewhere for the Narrative
Fingerprint profiler), passed through reconstruct_fragmented_entities() first (so a single
fragmented name is not masked as several separate placeholder tokens), then replaced via
mask_entities() (narrative_lens/features/ner.py). Entity boundaries come from the SAME
underlying dslim/bert-base-NER model already used by the production NER arm - so
"sbert_ner" (variant 2) and "sbert_masked" (variant 3) draw entity boundaries from the same
model; only what happens to those boundaries differs (fed to a separate identity-embedding
arm vs. erased from the SBERT input text). Masking runs ONCE over the full corpus's unique
texts (a text -> masked_text cache, data/cache/cached_raw_entities_masked_text.pt) since all
3 authors' train sets are large, overlapping subsets of the same underlying corpus - this
avoids repeating ~16.5k NER-pipeline calls per author.

Known limitation (documented up front, not discovered after the fact): dslim/bert-base-NER
only tags proper-noun-like PER/ORG/LOC/MISC spans - collective/abstract nouns that also
carry entity-like identity in this domain (e.g. "the West", "NATO forces", "the regime")
are not guaranteed to be tagged and may survive masking. Masking coverage stats (% of texts
with >=1 entity masked, per entity_group counts) are saved and reported so results can be
read against how much text was actually affected.

Run (from repo root):
    python experiments/author_generalization/narrative_entity_shortcut.py --author IDF
    python experiments/author_generalization/narrative_entity_shortcut.py --author MariaZakharova
    python experiments/author_generalization/narrative_entity_shortcut.py --author BernieSanders
Then:
    python experiments/author_generalization/narrative_entity_shortcut.py --aggregate

Sanity check (prints a handful of before/after masking examples, no training):
    python experiments/author_generalization/narrative_entity_shortcut.py --sanity-check
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer

from narrative_lens.config import NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from narrative_lens.train import load_raw_data, split_leave_one_author, evaluate, save_confusion_matrix_csv
from narrative_lens.features.ner import EntityAnalysisPipeline, reconstruct_fragmented_entities, mask_entities

# narrative_ablation_loao.py is a sibling script in this SAME folder (Python auto-adds a
# running script's own directory to sys.path) - reuse its AblationDetector unmodified, so
# the 2 new variants below share the EXACT same architecture as section 19's variants.
from narrative_ablation_loao import AblationDetector

AUTHORS = ("IDF", "MariaZakharova", "BernieSanders")
SEED = 42  # single fixed seed, matching section 19/20's convention (not a variance study)

CACHE_DIR = "data/cache"
MASKED_TEXT_CACHE_FILE = os.path.join(CACHE_DIR, "cached_raw_entities_masked_text.pt")
EXISTING_ABLATION_CACHE_TEMPLATE = os.path.join(CACHE_DIR, "cached_features_ablation_loao_{author}.pt")

CHECKPOINT_DIR = "models/experiments/narrative_entity_shortcut"
REPORT_DIR = "reports/results/narrative_entity_shortcut"
RESULTS_FILE = os.path.join(REPORT_DIR, "results.json")

EXISTING_LOAO_RESULTS_FILE = "reports/results/narrative_ablation_loao/results.json"
EXISTING_LOAO_REPORT_DIR = "reports/results/narrative_ablation_loao"
REUSED_VARIANTS = ("sbert_only", "sbert_ner", "sbert_soft_topic")

NEW_VARIANTS = {
    "sbert_masked": set(),
    "sbert_masked_soft_topic": {"soft_topic"},
}

ALL_VARIANTS_ORDER = ("sbert_only", "sbert_ner", "sbert_masked", "sbert_soft_topic", "sbert_masked_soft_topic")

BERTOPIC_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # same SBERT used throughout the project

RIGHT_WING_IDX = NARRATIVES.index("Right-wing")


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


# =========================================================================================
# Step 1: build (once) or load a text -> entity-masked-text map over the FULL corpus.
# =========================================================================================
def build_or_load_masked_text_cache():
    if os.path.exists(MASKED_TEXT_CACHE_FILE):
        print(f"Found existing masked-text cache '{MASKED_TEXT_CACHE_FILE}'. Loading...")
        return torch.load(MASKED_TEXT_CACHE_FILE, weights_only=False)

    print("\n=== Building fresh entity-masked-text cache over the FULL corpus (one-time, "
          "reused by all 3 authors) ===")
    df = load_raw_data()
    texts = df["text"].astype(str).str.slice(0, 3000)
    unique_texts = texts.unique().tolist()
    print(f"  {len(unique_texts)} unique texts (of {len(texts)} total rows) to run NER on...")

    print("Loading BERT-NER model (dslim/bert-base-NER) for entity-span extraction...")
    ner_analyzer = EntityAnalysisPipeline()

    masked_by_text = {}
    n_with_entity = 0
    entity_group_counts = {}
    for i, text in enumerate(unique_texts):
        raw_entities = ner_analyzer.extract_raw_entities(text)
        raw_entities = reconstruct_fragmented_entities(raw_entities, text)
        masked_by_text[text] = mask_entities(text, raw_entities)
        if raw_entities:
            n_with_entity += 1
        for ent in raw_entities:
            entity_group_counts[ent["entity_group"]] = entity_group_counts.get(ent["entity_group"], 0) + 1
        if (i + 1) % 1000 == 0:
            print(f"    ...{i + 1}/{len(unique_texts)} texts processed")

    stats = {
        "n_unique_texts": len(unique_texts),
        "n_texts_with_at_least_one_entity": n_with_entity,
        "pct_texts_with_at_least_one_entity": (n_with_entity / len(unique_texts)) if unique_texts else 0.0,
        "entity_group_counts": entity_group_counts,
    }
    print(f"  Masking coverage: {stats['pct_texts_with_at_least_one_entity'] * 100:.1f}% of "
          f"unique texts had >=1 entity masked. Entity group counts: {entity_group_counts}")

    result = {"masked_by_text": masked_by_text, "stats": stats}
    os.makedirs(CACHE_DIR, exist_ok=True)
    torch.save(result, MASKED_TEXT_CACHE_FILE)
    print(f"Saved masked-text cache to '{MASKED_TEXT_CACHE_FILE}'.")
    return result


# =========================================================================================
# Step 2: per-author feature cache: masked-SBERT embeddings (fresh) + soft_dense (reused by
# position from section 19's own cache, verified) + label.
# =========================================================================================
def build_or_load_author_cache(author, masked_text_cache):
    cache_file = os.path.join(CACHE_DIR, f"cached_features_entity_shortcut_{author}.pt")
    if os.path.exists(cache_file):
        print(f"Found existing entity-shortcut feature cache '{cache_file}'. Loading...")
        return torch.load(cache_file, weights_only=False)

    print(f"\n=== Building fresh entity-shortcut feature cache for held-out author '{author}' ===")
    df = load_raw_data()
    train_data, val_data, test_data = split_leave_one_author(df, author)
    for split_df in (train_data, val_data, test_data):
        split_df["text"] = split_df["text"].astype(str).str.slice(0, 3000)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    existing_cache_path = EXISTING_ABLATION_CACHE_TEMPLATE.format(author=author)
    print(f"Loading existing ablation cache '{existing_cache_path}' to reuse its soft_dense "
          f"feature (read-only, by-position, verified by label alignment)...")
    existing_cache = torch.load(existing_cache_path, weights_only=False)

    masked_by_text = masked_text_cache["masked_by_text"]

    print(f"Loading SBERT model '{BERTOPIC_EMBEDDING_MODEL_NAME}' (frozen, encode-only)...")
    sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)

    result = {}
    sbert_dim = None
    n_missing_mask = 0
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

        print(f"\n--- Split '{name}' ({len(split_df)} rows) ---")
        texts = split_df["text"].tolist()
        labels = split_df["label"].astype(int).tolist()

        masked_texts = []
        for t in texts:
            if t in masked_by_text:
                masked_texts.append(masked_by_text[t])
            else:
                n_missing_mask += 1
                masked_texts.append(t)  # fall back to the original (unmasked) text

        print("  Computing SBERT embeddings on entity-MASKED text...")
        sbert_embeddings = sbert_model.encode(masked_texts, convert_to_numpy=True, show_progress_bar=True)
        sbert_dim = int(sbert_embeddings.shape[1])

        rows = []
        for i in range(len(texts)):
            base_feat, base_label = existing_cache[name][i]
            assert base_label == labels[i], f"label mismatch at split={name} idx={i}"
            feat = {
                "sbert_embedding": torch.tensor(sbert_embeddings[i], dtype=torch.float32),
                "soft_dense": base_feat["soft_dense"],
            }
            rows.append((feat, labels[i]))
        result[name] = rows

    if n_missing_mask:
        print(f"[!] WARNING: {n_missing_mask} row(s) had no entry in the masked-text cache "
              f"(fell back to unmasked text) - unexpected unless texts differ from those the "
              f"cache was built from.")

    result["_meta"] = {
        "bertopic_vec_size": existing_cache["_meta"]["bertopic_vec_size"],
        "sbert_dim": sbert_dim,
        "reused_soft_dense_from": existing_cache_path,
        "n_missing_mask": n_missing_mask,
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    torch.save(result, cache_file)
    print(f"\nSaved new entity-shortcut feature cache to '{cache_file}'.")
    return result


# =========================================================================================
# Step 3: train the 2 new variants (sbert_masked, sbert_masked_soft_topic) - same MLP
# architecture/hyperparameters/checkpoint-selection convention as section 19/20's
# train_variant(), reusing AblationDetector unmodified. Kept as a separate copy (rather than
# importing narrative_ablation_loao.train_variant directly) only so checkpoints land in this
# experiment's OWN dedicated CHECKPOINT_DIR, not mixed into section 19's folder.
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
# Reuse section 19's sbert_only / sbert_ner / sbert_soft_topic results verbatim (no
# retraining - see module docstring for why this is valid).
# =========================================================================================
def verify_reuse_validity():
    if not os.path.exists(EXISTING_LOAO_RESULTS_FILE):
        raise FileNotFoundError(
            f"'{EXISTING_LOAO_RESULTS_FILE}' not found - run section 19's "
            f"narrative_ablation_loao.py for all 3 authors first (needed to reuse its "
            f"sbert_only/sbert_ner/sbert_soft_topic results)."
        )
    with open(EXISTING_LOAO_RESULTS_FILE, "r", encoding="utf-8") as f:
        existing_results = json.load(f)
    for author in AUTHORS:
        if author not in existing_results:
            raise RuntimeError(f"Author '{author}' missing from '{EXISTING_LOAO_RESULTS_FILE}'.")
        for variant in REUSED_VARIANTS:
            if variant not in existing_results[author]:
                raise RuntimeError(
                    f"Variant '{variant}' missing for author '{author}' in "
                    f"'{EXISTING_LOAO_RESULTS_FILE}' - cannot reuse."
                )
    return existing_results


def reused_variant_result(existing_results, author, variant_name):
    entry = dict(existing_results[author][variant_name])
    entry["confusion_matrix_csv"] = os.path.join(
        EXISTING_LOAO_REPORT_DIR, f"confusion_matrix_{variant_name}_{author}_test.csv"
    )
    entry["reused_from"] = EXISTING_LOAO_RESULTS_FILE
    return entry


# =========================================================================================
# Orchestration
# =========================================================================================
def run_author(author):
    existing_results = verify_reuse_validity()
    masked_text_cache = build_or_load_masked_text_cache()
    cache = build_or_load_author_cache(author, masked_text_cache)
    train_features, val_features, test_features = cache["train"], cache["val"], cache["test"]
    meta = cache["_meta"]
    bertopic_vec_size = meta["bertopic_vec_size"]
    sbert_dim = meta["sbert_dim"]

    os.makedirs(REPORT_DIR, exist_ok=True)
    author_results = {}

    for variant_name in REUSED_VARIANTS:
        author_results[variant_name] = reused_variant_result(existing_results, author, variant_name)
        r = author_results[variant_name]
        print(f"[{variant_name}/{author}] REUSED from section 19: "
              f"recall(true narrative)={r['recall_true_narrative'] * 100:.1f}% | "
              f"%->Right-wing={r['pct_misclassified_right_wing'] * 100:.1f}% | "
              f"macro_f1={r['macro_f1']:.4f}")

    for variant_name, arms in NEW_VARIANTS.items():
        print(f"\n{'=' * 70}\n=== Variant '{variant_name}' (arms={sorted(arms) or ['(none)']}) "
              f"- author '{author}' ===\n{'=' * 70}")
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
        print(f"[!] WARNING: results missing for author(s) {missing} - averages below are "
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
        row = {"variant": variant_name, "avg_recall_true_narrative": avg_recall,
               "avg_pct_right_wing": avg_rw_pct, "avg_macro_f1": avg_macro_f1}
        for author in AUTHORS:
            if author in per_author:
                row[f"{author}_recall"] = per_author[author]["recall_true_narrative"]
                row[f"{author}_pct_right_wing"] = per_author[author]["pct_misclassified_right_wing"]
        rows.append(row)

    df = pd.DataFrame(rows)
    print("\n" + "=" * 100)
    print("ENTITY SHORTCUT TEST SUMMARY (variant order = conceptual grouping, not sorted "
          "by performance):")
    print("=" * 100)
    print(df.to_string(index=False))

    summary_path = os.path.join(REPORT_DIR, "entity_shortcut_summary.csv")
    df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved summary table to '{summary_path}'.")

    if os.path.exists(MASKED_TEXT_CACHE_FILE):
        stats = torch.load(MASKED_TEXT_CACHE_FILE, weights_only=False)["stats"]
        print(f"\nMasking coverage over the full corpus: "
              f"{stats['pct_texts_with_at_least_one_entity'] * 100:.1f}% of unique texts had "
              f">=1 entity masked. Entity group counts: {stats['entity_group_counts']}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entity Shortcut Test (Experiment 21) for Narrative Classification on unseen (LOAO) authors."
    )
    parser.add_argument("--author", choices=AUTHORS, default=None,
                         help="Run masking (if needed) + train/evaluate the 2 new variants "
                              "(and reuse the 3 existing section-19 variants) for this "
                              "held-out author.")
    parser.add_argument("--aggregate", action="store_true",
                         help="Aggregate results across all 3 authors into a summary table "
                              "(run after all 3 --author runs have completed).")
    parser.add_argument("--sanity-check", action="store_true",
                         help="Print a handful of before/after masking examples and exit "
                              "(no training, no per-author cache built).")
    args = parser.parse_args()

    if args.sanity_check:
        text_cache = build_or_load_masked_text_cache()
        masked_by_text = text_cache["masked_by_text"]

        def _safe_print(line):
            # the console codepage (e.g. cp1255) can't encode every character (emoji etc.)
            # that shows up in scraped social-media text - never let a print() crash the run.
            print(line.encode("ascii", errors="replace").decode("ascii"))

        shown = 0
        for original, masked in masked_by_text.items():
            if original != masked:
                _safe_print(f"\nORIGINAL: {original[:200]}")
                _safe_print(f"MASKED:   {masked[:200]}")
                shown += 1
            if shown >= 10:
                break
        if shown == 0:
            print("No masked examples found (unexpected - check EntityAnalysisPipeline output).")
    elif args.aggregate:
        aggregate()
    elif args.author:
        run_author(args.author)
    else:
        parser.error("Specify --author <IDF|MariaZakharova|BernieSanders>, --aggregate, or --sanity-check.")

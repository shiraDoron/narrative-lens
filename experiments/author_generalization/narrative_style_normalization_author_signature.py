"""
Narrative Classification — Style-Normalization Intervention, Part A: Author Signature
=======================================================================================
EXPERIMENTS.md Section 28 — direct causal follow-up to Section 27 (which showed author identity
is strongly recoverable from style/formatting features, even WITHIN a single fixed narrative).
This script re-runs Section 27's EXACT Decision Tree methodology (same authors, same features,
same StratifiedKFold(5, shuffle=True, random_state=42) + cross_val_predict CV, same depths, same
evaluation rules) TWICE: once on the ORIGINAL text (reusing Section 27's already-computed
`diagnostic_dataset.csv` as-is, zero recompute), and once on the SAME rows after applying
`narrative_lens.features.style_normalization.normalize_style()` (a deterministic, author-blind
URL/@mention/hashtag/punctuation/whitespace/elongation normalization - see that module's
docstring for exactly what it does and does not touch).

Research question: does author recoverability (Experiment A - global pooled, and especially
Experiment B - within-narrative, the decisive test) actually DROP after normalizing away
stylistic/formatting signal, while leaving semantic content (named entities, wording) untouched?

Everything (dataset build, feature functions, CV methodology, depths, baselines, artifacts) is
reused UNMODIFIED from `narrative_author_signature_diagnostics.py` (sibling script, same
directory - plain import, no sys.path hack needed when run directly) - only the TEXT fed into
the style/semantic/topic feature functions differs between the two variants. Entity counts are
looked up by the ORIGINAL text in both variants (named entities are never altered by
normalization - see style_normalization.py's docstring), but entity_density uses each variant's
own (possibly different) word_count.

One predefined intervention, no further tuning: if normalization doesn't move the needle, that is
reported as-is (see EXPERIMENTS.md Section 28 for the pre-specified interpretation rules).

Run (from repo root):
    python experiments/author_generalization/narrative_style_normalization_author_signature.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import torch
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

from narrative_lens.train import load_raw_data, is_synthetic_author
from narrative_lens.features.style_normalization import normalize_style

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from narrative_author_signature_diagnostics import (  # noqa: E402
    ALL_FEATURES, BERTOPIC_EMBEDDING_MODEL_NAME, BERTOPIC_MODEL_PATH,
    DATASET_FILE as ORIGINAL_DATASET_FILE, MIN_EXAMPLES_PER_AUTHOR,
    N_PCA_COMPONENTS, SEED, build_or_load_raw_entities_cache, entity_count_features,
    run_cv_experiment, soft_topic_summary_features, style_lexical_features,
)

REPORT_DIR = "artifacts/experiments/narrative_style_normalization_author_signature"
NORMALIZED_DATASET_FILE = os.path.join(REPORT_DIR, "diagnostic_dataset_normalized.csv")
COMPARISON_FILE = os.path.join(REPORT_DIR, "original_vs_normalized_summary.json")


def _rebuild_filtered_df():
    """Reproduces Section 27's exact filtering (same code, same deterministic
    load_raw_data() shuffle) so we have the raw ORIGINAL texts to normalize - needed because
    `diagnostic_dataset.csv` only stores already-computed features, not the raw text."""
    df = load_raw_data()
    df = df[~df["author_source"].apply(is_synthetic_author)].copy()
    df["text"] = df["text"].astype(str).str.slice(0, 3000)
    counts = df["author_source"].value_counts()
    eligible_authors = counts[counts >= MIN_EXAMPLES_PER_AUTHOR].index.tolist()
    df = df[df["author_source"].isin(eligible_authors)].reset_index(drop=True)
    return df


def load_original_dataset():
    if not os.path.exists(ORIGINAL_DATASET_FILE):
        raise FileNotFoundError(
            f"'{ORIGINAL_DATASET_FILE}' not found - run "
            f"narrative_author_signature_diagnostics.py at least once first (Section 27); "
            f"this script REUSES its output as-is, it never recomputes the original variant."
        )
    return pd.read_csv(ORIGINAL_DATASET_FILE)


def build_normalized_dataset(original_dataset):
    if os.path.exists(NORMALIZED_DATASET_FILE):
        print(f"Found existing normalized dataset '{NORMALIZED_DATASET_FILE}'. Loading "
              f"(skipping feature extraction)...")
        return pd.read_csv(NORMALIZED_DATASET_FILE)

    df = _rebuild_filtered_df()
    print(f"Verifying row-alignment between the rebuilt raw-text dataframe ({len(df)} rows) "
          f"and the existing diagnostic_dataset.csv ({len(original_dataset)} rows)...")
    if (len(df) != len(original_dataset)
            or df["author_source"].tolist() != original_dataset["author"].astype(str).tolist()
            or df["narrative_name"].tolist() != original_dataset["narrative_name"].astype(str).tolist()):
        raise RuntimeError(
            "Alignment check FAILED: rebuilding Section 27's filtering no longer reproduces "
            "the same row order/authors as the existing diagnostic_dataset.csv. Refusing to "
            "build a normalized variant that would not be directly comparable row-for-row."
        )
    print("Alignment check passed: rebuilt rows match diagnostic_dataset.csv exactly.")

    original_texts = df["text"].tolist()
    normalized_texts = [normalize_style(t) for t in original_texts]

    print("Computing style/lexical features on NORMALIZED text...")
    style_rows = [style_lexical_features(t) for t in normalized_texts]

    print("Loading raw-entities cache + computing entity-count features (entities looked up "
          "by ORIGINAL text - normalization never alters named entities - using each "
          "variant's own normalized word_count for entity_density)...")
    raw_entities_by_text = build_or_load_raw_entities_cache()
    entity_rows = [entity_count_features(orig_t, raw_entities_by_text, s["word_count"])
                   for orig_t, s in zip(original_texts, style_rows)]

    print("Loading SBERT model + encoding NORMALIZED texts (fresh PCA fit, same methodology "
          "as Section 27, now on the normalized embedding space)...")
    sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)
    embeddings = sbert_model.encode(normalized_texts, show_progress_bar=True, batch_size=64)
    pca = PCA(n_components=N_PCA_COMPONENTS, random_state=SEED)
    pca_components = pca.fit_transform(embeddings)
    print(f"  PCA explained variance ratio (top {N_PCA_COMPONENTS}): "
          f"{np.round(pca.explained_variance_ratio_, 3)}")

    print("Loading BERTopic model + computing soft-topic summary features on NORMALIZED text...")
    bertopic_model = BERTopic.load(BERTOPIC_MODEL_PATH, embedding_model=BERTOPIC_EMBEDDING_MODEL_NAME)
    num_bertopic_topics = len([t for t in bertopic_model.get_topics().keys() if t != -1])
    max_probs, entropies = soft_topic_summary_features(normalized_texts, bertopic_model, num_bertopic_topics)

    dataset = pd.DataFrame(style_rows)
    entity_df = pd.DataFrame(entity_rows)
    dataset = pd.concat([dataset, entity_df], axis=1)
    dataset["soft_topic_max_prob"] = max_probs
    dataset["soft_topic_entropy"] = entropies
    for i in range(N_PCA_COMPONENTS):
        dataset[f"sbert_pca_{i + 1}"] = pca_components[:, i]
    dataset["author"] = df["author_source"].values
    dataset["narrative_name"] = df["narrative_name"].values

    os.makedirs(REPORT_DIR, exist_ok=True)
    dataset.to_csv(NORMALIZED_DATASET_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved normalized diagnostic dataset ({len(dataset)} rows) to "
          f"'{NORMALIZED_DATASET_FILE}'.")
    return dataset


def run_both_experiments(dataset, variant_label, prefix):
    result_a = run_cv_experiment(
        dataset, ALL_FEATURES, depths=(5, 10, 15, None),
        report_prefix=os.path.join(REPORT_DIR, f"{prefix}_experiment_a_global"),
        scope_label=f"Experiment A [{variant_label}] - global author prediction (all narratives pooled)",
    )
    results_b = []
    for narrative in sorted(dataset["narrative_name"].unique()):
        subset = dataset[dataset["narrative_name"] == narrative].reset_index(drop=True)
        if subset["author"].nunique() < 2:
            print(f"\n[skip] narrative '{narrative}' has < 2 eligible authors, skipping Experiment B.")
            continue
        result = run_cv_experiment(
            subset, ALL_FEATURES, depths=(3, 4, 5),
            report_prefix=os.path.join(REPORT_DIR, f"{prefix}_experiment_b_{narrative}"),
            scope_label=f"Experiment B [{variant_label}] - within-narrative author prediction ({narrative})",
        )
        results_b.append(result)
    return result_a, results_b


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    print("=" * 70)
    print("VARIANT: original text (reusing Section 27's diagnostic_dataset.csv as-is)")
    print("=" * 70)
    original_dataset = load_original_dataset()
    original_a, original_b = run_both_experiments(original_dataset, "original", "original")

    print("\n" + "=" * 70)
    print("VARIANT: style-normalized text")
    print("=" * 70)
    normalized_dataset = build_normalized_dataset(original_dataset)
    normalized_a, normalized_b = run_both_experiments(normalized_dataset, "normalized", "normalized")

    # ---- Side-by-side comparison ----
    def delta(orig, norm):
        return float(norm - orig)

    comparison_a = {
        "original": {"accuracy": original_a["depth_results"][str(original_a["best_depth"])]["accuracy"],
                     "macro_f1": original_a["depth_results"][str(original_a["best_depth"])]["macro_f1"],
                     "top_features": original_a["top_features"]},
        "normalized": {"accuracy": normalized_a["depth_results"][str(normalized_a["best_depth"])]["accuracy"],
                       "macro_f1": normalized_a["depth_results"][str(normalized_a["best_depth"])]["macro_f1"],
                       "top_features": normalized_a["top_features"]},
    }
    comparison_a["accuracy_delta"] = delta(comparison_a["original"]["accuracy"], comparison_a["normalized"]["accuracy"])
    comparison_a["macro_f1_delta"] = delta(comparison_a["original"]["macro_f1"], comparison_a["normalized"]["macro_f1"])

    comparison_b = []
    orig_b_by_narrative = {r["scope"].split("(")[-1].rstrip(")"): r for r in original_b}
    norm_b_by_narrative = {r["scope"].split("(")[-1].rstrip(")"): r for r in normalized_b}
    for narrative in sorted(set(orig_b_by_narrative) & set(norm_b_by_narrative)):
        o = orig_b_by_narrative[narrative]
        n = norm_b_by_narrative[narrative]
        o_best = o["depth_results"][str(o["best_depth"])]
        n_best = n["depth_results"][str(n["best_depth"])]
        comparison_b.append({
            "narrative": narrative,
            "original_accuracy": o_best["accuracy"], "normalized_accuracy": n_best["accuracy"],
            "accuracy_delta": delta(o_best["accuracy"], n_best["accuracy"]),
            "original_macro_f1": o_best["macro_f1"], "normalized_macro_f1": n_best["macro_f1"],
            "macro_f1_delta": delta(o_best["macro_f1"], n_best["macro_f1"]),
            "original_beats_baselines": o["best_depth_beats_both_baselines"],
            "normalized_beats_baselines": n["best_depth_beats_both_baselines"],
        })

    comparison = {
        "seed": SEED,
        "experiment_a": comparison_a,
        "experiment_b_by_narrative": comparison_b,
        "experiment_a_still_beats_baselines_after_normalization": normalized_a["best_depth_beats_both_baselines"],
        "any_experiment_b_narrative_still_beats_baselines_after_normalization":
            any(r["normalized_beats_baselines"] for r in comparison_b),
    }
    with open(COMPARISON_FILE, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)
    print(f"\nSaved original-vs-normalized comparison to '{COMPARISON_FILE}'.")


if __name__ == "__main__":
    main()

"""Stratified corpus-size subsampling utility for the min_topic_size-vs-corpus-size validation
experiment (`experiment_f_corpus_scaling.py`).

Loads the same 4 raw natural datasets used by `train_topics.load_deduplicated_training_texts()`
(same cleaning via `topic_preprocessing.clean_text_for_topic_model()` + `has_enough_content()`,
same near-duplicate removal via `text_dedup.deduplicate_texts()`), but - unlike that function,
which only returns a bare list of cleaned strings - KEEPS `narrative_name` and `dataset_source`
aligned to every surviving row. This alignment is required to draw smaller, reproducible corpus
subsamples that preserve (as closely as integer rounding allows) the SAME joint distribution over
the 4 data sources (gemini/gpt/twitter/telegram) and the 7 narratives as the full corpus, so a
min_topic_size comparison across different corpus sizes is not confounded by an accidental shift
in what KIND of data got smaller/bigger.

Does not touch fusion.py/train.py/any checkpoint/any existing saved BERTopic model - purely a new
read-only data-preparation utility.
"""
import os
import sys

import numpy as np
import pandas as pd

from narrative_lens.data.text_dedup import NEAR_DUP_THRESHOLD, deduplicate_texts
from narrative_lens.topic_modeling.topic_preprocessing import clean_text_for_topic_model, has_enough_content

RAW_DATASETS = {
    "gemini": "data/raw/gemini_natural_dataset.csv",
    "gpt": "data/raw/gpt_natural_dataset.csv",
    "twitter": "data/raw/twitter_natural_dataset.csv",
    "telegram": "data/raw/telegram_natural_dataset.csv",
}

# Joint stratification key: preserving the distribution over BOTH of these together
# automatically preserves each one's own marginal distribution too.
STRATA_COLS = ("dataset_source", "narrative_name")


def load_cleaned_labeled_corpus(verbose=True):
    """Returns a DataFrame [text, narrative_name, dataset_source] - one row per surviving
    (cleaned, non-near-duplicate) document, in the same relative order as the raw concatenated
    data. `text` is already cleaned (`clean_text_for_topic_model`), ready to feed directly into
    BERTopic.fit()/embeddings - identical preprocessing to
    `train_topics.load_deduplicated_training_texts()`, just with source/narrative columns kept."""
    if verbose:
        print("Loading raw datasets (tagging dataset_source)...")
    frames = []
    for source, path in RAW_DATASETS.items():
        df = pd.read_csv(path)[["text", "narrative_name"]].dropna()
        df = df.copy()
        df["dataset_source"] = source
        frames.append(df)
    full = pd.concat(frames, ignore_index=True)
    full["text"] = full["text"].astype(str)
    n_raw = len(full)
    if verbose:
        print(f"Loaded {n_raw} raw rows across {len(RAW_DATASETS)} datasets.")

    cleaned_texts = []
    keep_mask = []
    for raw in full["text"]:
        cleaned = clean_text_for_topic_model(raw)
        keep = has_enough_content(cleaned)
        keep_mask.append(keep)
        if keep:
            cleaned_texts.append(cleaned)
    full = full[keep_mask].copy()
    full["text"] = cleaned_texts
    full = full.reset_index(drop=True)
    if verbose:
        print(f"After cleaning: {n_raw} -> {len(full)} rows "
              f"({n_raw - len(full)} dropped as empty/near-empty after cleaning).")

    if verbose:
        print(f"Running near-duplicate dedup (threshold={NEAR_DUP_THRESHOLD})...")
    n_before_dedup = len(full)
    kept_indices, cluster_summaries = deduplicate_texts(
        full["text"].tolist(), threshold=NEAR_DUP_THRESHOLD
    )
    full = full.iloc[kept_indices].reset_index(drop=True)
    if verbose:
        print(f"After dedup: {n_before_dedup} -> {len(full)} rows "
              f"({n_before_dedup - len(full)} removed as near-duplicates, "
              f"{len(cluster_summaries)} clusters).")
    return full


def compute_marginal_proportions(df, col):
    return (df[col].value_counts(normalize=True) * 100).round(2).sort_index()


def stratified_subsample(df, target_size, seed=42, strata_cols=STRATA_COLS):
    """Draws a stratified subsample of (as close as possible to) `target_size` rows from `df`,
    preserving the joint distribution over `strata_cols` (default: dataset_source x
    narrative_name) via proportional allocation + the largest-remainder method (avoids the
    systematic under/over-count naive per-stratum rounding would cause when summed over ~28
    strata). If `target_size >= len(df)`, returns the full df unchanged (just reset_index/
    shuffled) since there is nothing to subsample.

    Sampling within each stratum uses `random_state=seed` (no replacement) - this seed controls
    ONLY which rows are selected into the subsample (the "which data" question), fully
    independent of any later UMAP/HDBSCAN random_state used to fit BERTopic on the result (the
    "how it's clustered" question) - keeping these two sources of randomness decoupled is
    important so that seed-stability checks on the SAME corpus subsample aren't confounded by
    also silently resampling different data each time.
    """
    n_total = len(df)
    if target_size >= n_total:
        return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    groups = list(df.groupby(list(strata_cols)))
    sizes = np.array([len(g) for _, g in groups])
    raw_alloc = sizes * (target_size / n_total)
    base_alloc = np.floor(raw_alloc).astype(int)
    remainder = raw_alloc - base_alloc
    n_remaining = int(target_size - base_alloc.sum())
    order = np.argsort(-remainder)
    alloc = base_alloc.copy()
    for idx in order[:n_remaining]:
        alloc[idx] += 1
    alloc = np.minimum(alloc, sizes)  # safety clip, should not bind in practice

    sampled_frames = [
        g.sample(n=int(n), random_state=seed) for (_, g), n in zip(groups, alloc) if n > 0
    ]
    result = pd.concat(sampled_frames, ignore_index=True)
    # shuffle so rows aren't grouped by stratum (avoids any accidental input-order sensitivity)
    result = result.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return result


def stratification_report(df_full, df_sub):
    """Compares marginal proportions (dataset_source, narrative_name) between the full cleaned
    corpus and a subsample - used to verify/report the fairness of stratified sampling."""
    report = {}
    for col in ("dataset_source", "narrative_name"):
        full_props = compute_marginal_proportions(df_full, col)
        sub_props = compute_marginal_proportions(df_sub, col)
        aligned = pd.DataFrame({"full_pct": full_props, "subsample_pct": sub_props}).fillna(0.0)
        report[col] = {
            "full_pct": full_props.to_dict(),
            "subsample_pct": sub_props.to_dict(),
            "max_abs_diff_pct": float((aligned["full_pct"] - aligned["subsample_pct"]).abs().max()),
        }
    return report

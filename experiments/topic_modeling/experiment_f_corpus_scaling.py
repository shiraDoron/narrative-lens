"""Experiment F: empirical validation of `recommend_min_topic_size(corpus_size)` via a
corpus-size subsampling sweep.

Full methodology, results, scoring rule, scaling-law fit and limitations are documented in
EXPERIMENTS.md (section "Experiment F"). Short summary:

- Builds the same cleaned+deduplicated corpus as `train_topics.load_deduplicated_training_texts()`
  (via `corpus_subsampling.load_cleaned_labeled_corpus()`), but keeps `narrative_name`/
  `dataset_source` aligned per row.
- Draws 4 corpus-size subsamples (4K/8K/12K/full~16K), each stratified jointly by
  (dataset_source, narrative_name) so the 4-source and 7-narrative mix stays constant across
  sizes (`corpus_subsampling.stratified_subsample`).
- For each corpus size, sweeps a `min_topic_size` grid (see MTS_GRID below), each fit with 2 UMAP
  seeds (42, 7) for a real seed-stability check - everything else held fixed: embedding model
  (all-MiniLM-L6-v2), preprocessing, dedup, representation (Experiment C's CountVectorizer(
  stop_words="english", ngram_range=(1,2)) + ClassTfidfTransformer(reduce_frequent_words=True,
  bm25_weighting=True) + MaximalMarginalRelevance(diversity=0.3)).
- Per config, computes: topic count, outlier %, micro-topic counts, avg/median topic size,
  largest-topics + mega-topic (top-2-combined %) check, u_mass Topic Coherence + Topic Diversity
  (same method as `experiment_e_lda_baseline.py`), hard/soft agreement + soft-signal coverage on
  the SAME fixed n=280/seed=42 stratified eval sample used by every prior experiment in this
  project (reusing `analyze_soft_topic_quality.run_batch_analysis`/`compute_summary_stats`
  directly, in-memory - no BERTopic.load(), no per-config model saved to disk, avoiding both the
  documented BERTopic.load() embedding-resolution flakiness and 40+ redundant saved model dirs).
- Embeddings are computed ONCE per corpus size (not per min_topic_size/seed config) and passed
  into BERTopic via `fit_transform(texts, embeddings=...)` - this is the single biggest runtime
  optimization (SBERT encoding, not UMAP/HDBSCAN, is the dominant per-config cost otherwise) and
  is functionally identical to BERTopic re-embedding every time (same model, same texts).
- After the full sweep, selects the best `min_topic_size` per corpus size via an explicit,
  documented multi-metric scoring rule (see `score_all_configs()`), then fits several candidate
  scaling laws (constant / linear / sqrt / log / general power law) against the 4 resulting
  (corpus_size, best_min_topic_size) points and reports which fits best.

Does NOT touch fusion.py, train.py, any .pth checkpoint, models/saved_topic_model, or
models/saved_topic_model_soft_v2 - every model fit in this sweep lives only in-memory (or, for
resumability, cached embeddings/subsample CSVs under data/cache/), never saved as a BERTopic
model directory.

Run (from repo root): python experiments/topic_modeling/experiment_f_corpus_scaling.py
Resumable: re-running skips any (corpus_size, min_topic_size, seed) config already present in
reports/results/profiler_prototype/expF_corpus_scaling_results.json.
"""
import argparse
import json
import os
import time

import numpy as np
from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from bertopic.vectorizers import ClassTfidfTransformer
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP

from narrative_lens.evaluation.analyze_soft_topic_quality import compute_summary_stats, load_stratified_sample, run_batch_analysis
from corpus_subsampling import load_cleaned_labeled_corpus, stratification_report, stratified_subsample
from experiment_e_lda_baseline import build_dictionary_and_corpus, compute_coherence, tokenize, topic_diversity
from narrative_lens.topic_modeling.topic_preprocessing import build_multiword_label

REPORT_DIR = "reports/results/profiler_prototype"
CACHE_DIR = "data/cache"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Randomness used ONLY to pick which subset of documents ends up in each corpus-size subsample -
# fixed so that seed=42/seed=7 UMAP runs below are compared on the EXACT SAME data, isolating
# clustering-seed variance from data-sampling variance.
SUBSAMPLE_SEED = 42

# UMAP random_state values swept per (corpus_size, min_topic_size) config - a real, if modest
# (2, not 3), seed-stability check, chosen for CPU runtime reasons (see EXPERIMENTS.md
# limitations - full 3-seed stability, as done for the single embedding-model comparison in
# Experiment B, was judged too expensive to repeat across 22 min_topic_size x corpus_size cells).
UMAP_SEEDS = [42, 7]

# corpus size "full" is resolved to the actual cleaned+deduplicated corpus size (~16,062) at
# runtime - kept symbolic here since that exact number depends on the current raw data.
SIZE_KEYS = [4000, 8000, 12000, "full"]
SIZE_LABELS = {4000: "4K", 8000: "8K", 12000: "12K", "full": "16K (full)"}

# Grid as proposed by the user: not purely linear, wide enough to find a real optimum instead of
# assuming one. Reused verbatim (no change proposed - it already spans below/above the current
# corpus's own validated optimum of 10 at every size, and grows with corpus size as intended).
MTS_GRID = {
    4000: [5, 10, 15, 20],
    8000: [5, 10, 15, 20, 25],
    12000: [5, 10, 15, 20, 25, 30],
    "full": [5, 10, 15, 20, 25, 30, 35],
}

MICRO_TOPIC_ABS_THRESHOLD = 15
# top-2-combined-% above which a config is VETOED as a mega-topic/over-merging failure, per
# Experiment A's finding (baseline ~4.4%, mts=25 -> 17.2%, mts=35 -> 43.1%; mts=25 was already
# judged unacceptable) - set well below the mts=25 value, comfortably above normal variance.
MEGA_TOPIC_VETO_PCT = 12.0

RESULTS_JSON = os.path.join(REPORT_DIR, "expF_corpus_scaling_results.json")
SELECTION_JSON = os.path.join(REPORT_DIR, "expF_selection_and_scaling_law.json")


def config_key(sizekey, mts, seed):
    return f"{sizekey}__mts{mts}__seed{seed}"


class _InMemoryLabelPipeline:
    """Minimal adapter so `analyze_soft_topic_quality.run_batch_analysis()`/
    `compute_summary_stats()` (already validated, used by every prior BERTopic experiment in this
    project) can be reused directly on an in-memory (never saved to disk) BERTopic model."""

    def __init__(self, topic_model):
        self.topic_model = topic_model

    def get_topic_label(self, topic_id, top_n_words=3):
        if topic_id == -1:
            return "outlier"
        info = self.topic_model.get_topic(topic_id)
        if not info:
            return "outlier"
        return build_multiword_label(info, top_n_words=top_n_words) or "outlier"


def get_or_build_subsample_and_embeddings(sizekey, df_full, encoder):
    os.makedirs(CACHE_DIR, exist_ok=True)
    csv_path = os.path.join(CACHE_DIR, f"expF_subsample_{sizekey}.csv")
    npy_path = os.path.join(CACHE_DIR, f"expF_embeddings_{sizekey}.npy")

    if os.path.exists(csv_path):
        import pandas as pd
        sub = pd.read_csv(csv_path)
    else:
        target_size = len(df_full) if sizekey == "full" else sizekey
        sub = stratified_subsample(df_full, target_size, seed=SUBSAMPLE_SEED)
        sub.to_csv(csv_path, index=False, encoding="utf-8-sig")

    if os.path.exists(npy_path):
        embeddings = np.load(npy_path)
        if len(embeddings) != len(sub):
            print(f"  WARNING: cached embeddings size mismatch for {sizekey}, recomputing.")
            embeddings = None
    else:
        embeddings = None

    if embeddings is None:
        print(f"  Encoding {len(sub)} texts for corpus size {sizekey} "
              f"({EMBEDDING_MODEL_NAME})...")
        embeddings = encoder.encode(sub["text"].tolist(), show_progress_bar=True)
        np.save(npy_path, embeddings)

    return sub, embeddings


def apply_representation(topic_model, texts_list):
    """Same representation-quality settings validated in Experiment C, held fixed across every
    config in this sweep (fresh transformer instances per call - they hold fit state)."""
    topic_model.update_topics(
        texts_list,
        vectorizer_model=CountVectorizer(stop_words="english", ngram_range=(1, 2)),
        ctfidf_model=ClassTfidfTransformer(reduce_frequent_words=True, bm25_weighting=True),
        representation_model=MaximalMarginalRelevance(diversity=0.3),
    )


def compute_cluster_stats(topic_model, min_topic_size):
    info_df = topic_model.get_topic_info()
    non_outlier = info_df[info_df["Topic"] != -1]
    outlier_row = info_df[info_df["Topic"] == -1]
    n_docs_total = int(info_df["Count"].sum())
    n_outliers = int(outlier_row["Count"].iloc[0]) if len(outlier_row) else 0
    return {
        "n_topics": int(len(non_outlier)),
        "n_docs_total": n_docs_total,
        "n_outliers": n_outliers,
        "outlier_pct": round(100 * n_outliers / n_docs_total, 2) if n_docs_total else None,
        "topic_size_mean": round(float(non_outlier["Count"].mean()), 1) if len(non_outlier) else None,
        "topic_size_median": float(non_outlier["Count"].median()) if len(non_outlier) else None,
        "n_micro_topics_abs15": int((non_outlier["Count"] <= MICRO_TOPIC_ABS_THRESHOLD).sum()),
        "n_micro_topics_floor_rel": int((non_outlier["Count"] <= min_topic_size + 10).sum()),
        "micro_topic_floor_rel_frac": (
            round(float((non_outlier["Count"] <= min_topic_size + 10).sum()) / len(non_outlier), 3)
            if len(non_outlier) else None
        ),
    }


def compute_largest_topics(topic_model, n_shown=5):
    info_df = topic_model.get_topic_info()
    non_outlier = info_df[info_df["Topic"] != -1]
    n_clustered = int(non_outlier["Count"].sum())
    largest = non_outlier.sort_values("Count", ascending=False).head(n_shown)
    largest_topics = [
        {
            "topic_id": int(row.Topic), "count": int(row.Count),
            "pct_of_clustered": round(100 * int(row.Count) / n_clustered, 2) if n_clustered else None,
            "label": build_multiword_label(topic_model.get_topic(int(row.Topic)), top_n_words=3),
        }
        for row in largest.itertuples()
    ]
    top2_count = int(non_outlier.sort_values("Count", ascending=False).head(2)["Count"].sum())
    top2_pct = round(100 * top2_count / n_clustered, 2) if n_clustered else None
    return {"largest_topics": largest_topics, "top2_combined_pct": top2_pct}


def compute_topic_words_for_coherence(topic_model, dictionary, top_n=10):
    """Decomposes BERTopic's (possibly multi-word/bigram, post-MMR) top phrases into single
    tokens present in the shared gensim Dictionary, same approach as experiment_e_lda_baseline,
    so u_mass coherence can be computed against the SAME dictionary/corpus used for that corpus
    size. Returns (topics_words, n_dropped_oov)."""
    topics_words = []
    n_dropped = 0
    for tid in topic_model.get_topics().keys():
        if tid == -1:
            continue
        phrases = [w for w, _ in topic_model.get_topic(tid)][:top_n]
        words, seen = [], set()
        for phrase in phrases:
            for tok in phrase.split():
                tok = tok.lower()
                if tok in seen:
                    continue
                if tok in dictionary.token2id:
                    words.append(tok)
                    seen.add(tok)
                else:
                    n_dropped += 1
        if words:
            topics_words.append(words)
    return topics_words, n_dropped


def hard_soft_quality(topic_model, eval_df):
    pipeline = _InMemoryLabelPipeline(topic_model)
    result_df = run_batch_analysis(pipeline, eval_df, top_n=3)
    return compute_summary_stats(result_df)


def run_one_config(sizekey, mts, seed, texts_list, embeddings, dictionary, corpus_bow,
                    tokenized_docs, eval_df):
    t0 = time.time()
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine",
                       random_state=seed)
    topic_model = BERTopic(embedding_model=EMBEDDING_MODEL_NAME, umap_model=umap_model,
                            min_topic_size=mts)
    topic_model.fit_transform(texts_list, embeddings=embeddings)
    apply_representation(topic_model, texts_list)
    fit_seconds = time.time() - t0

    cluster_stats = compute_cluster_stats(topic_model, mts)
    largest_stats = compute_largest_topics(topic_model)

    topics_words, n_dropped_oov = compute_topic_words_for_coherence(topic_model, dictionary)
    coherence, _ = compute_coherence(topics_words, tokenized_docs, dictionary, corpus_bow)
    diversity = topic_diversity(topics_words)

    quality_summary = hard_soft_quality(topic_model, eval_df)
    agree_counts = quality_summary["hard_soft_agreement_counts"]
    n_true = agree_counts.get("True", 0)
    n_false = agree_counts.get("False", 0)
    agreement_rate_with_signal = (
        round(100 * n_true / (n_true + n_false), 1) if (n_true + n_false) > 0 else None
    )
    soft_signal_pct = round(100 - quality_summary["case_pct"].get("no_soft_signal", 0), 1)

    result = {
        "sizekey": str(sizekey), "min_topic_size": mts, "umap_seed": seed,
        "fit_seconds": round(fit_seconds, 1),
        "cluster_stats": cluster_stats,
        "largest_topics_stats": largest_stats,
        "u_mass_coherence": coherence,
        "topic_diversity": diversity,
        "n_dropped_oov_coherence_words": n_dropped_oov,
        "quality_summary": quality_summary,
        "agreement_rate_with_signal_pct": agreement_rate_with_signal,
        "soft_signal_coverage_pct": soft_signal_pct,
    }
    return result


def load_results():
    if os.path.exists(RESULTS_JSON):
        with open(RESULTS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_results(all_results):
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)


def run_sweep(size_keys=None, seeds=None):
    size_keys = size_keys or SIZE_KEYS
    seeds = seeds or UMAP_SEEDS

    print("Loading full cleaned+deduplicated corpus...")
    df_full = load_cleaned_labeled_corpus()

    print(f"Loading eval sample (n=280, seed=42, same sample as every prior experiment)...")
    eval_df = load_stratified_sample(n_per_narrative=40, seed=42)

    print(f"Loading SentenceTransformer encoder ({EMBEDDING_MODEL_NAME})...")
    encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)

    all_results = load_results()
    strat_reports = {}

    for sizekey in size_keys:
        print(f"\n{'=' * 70}\nCorpus size {SIZE_LABELS[sizekey]} ({sizekey})\n{'=' * 70}")
        sub, embeddings = get_or_build_subsample_and_embeddings(sizekey, df_full, encoder)
        texts_list = sub["text"].tolist()
        strat_reports[str(sizekey)] = stratification_report(df_full, sub)

        print("Building shared gensim Dictionary/corpus for coherence (this corpus size only)...")
        tokenized_docs = [tokenize(t) for t in texts_list]
        dictionary, corpus_bow = build_dictionary_and_corpus(tokenized_docs)

        for mts in MTS_GRID[sizekey]:
            for seed in seeds:
                key = config_key(sizekey, mts, seed)
                if key in all_results:
                    print(f"  [skip, already done] {key}")
                    continue
                print(f"  Fitting {key} ...")
                t0 = time.time()
                result = run_one_config(
                    sizekey, mts, seed, texts_list, embeddings, dictionary, corpus_bow,
                    tokenized_docs, eval_df,
                )
                print(f"  {key}: n_topics={result['cluster_stats']['n_topics']} "
                      f"outlier%={result['cluster_stats']['outlier_pct']} "
                      f"coherence={result['u_mass_coherence']:.3f} "
                      f"diversity={result['topic_diversity']:.3f} "
                      f"top2%={result['largest_topics_stats']['top2_combined_pct']} "
                      f"(total {time.time()-t0:.1f}s)")
                all_results[key] = result
                save_results(all_results)  # checkpoint after every config

    strat_path = os.path.join(REPORT_DIR, "expF_stratification_report.json")
    with open(strat_path, "w", encoding="utf-8") as f:
        json.dump(strat_reports, f, ensure_ascii=False, indent=2)
    print(f"\nSaved stratification fidelity report to {strat_path}")
    print(f"All sweep results saved to {RESULTS_JSON}")
    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=str, default=None,
                        help="Comma-separated subset of corpus sizes to run, e.g. 4000,8000. "
                             "Use 'full' for the full-corpus size. Default: all.")
    parser.add_argument("--seeds", type=str, default=None,
                        help="Comma-separated UMAP seeds to run, e.g. 42,7. Default: 42,7.")
    args = parser.parse_args()

    sizes = None
    if args.sizes:
        sizes = [int(s) if s != "full" else "full" for s in args.sizes.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")] if args.seeds else None

    run_sweep(size_keys=sizes, seeds=seeds)

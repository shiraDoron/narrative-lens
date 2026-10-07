"""
Duplicate / near-duplicate analysis for the BERTopic training corpus.

ANALYSIS ONLY - does NOT delete any data and does NOT retrain BERTopic. This is meant to inform a
future decision about whether/how to deduplicate before the next BERTopic fit.

Methodology
-----------
1. EXACT duplicates: group raw texts by an exact match on a lightly normalized string (collapse
   whitespace, lowercase). Cheap and unambiguous.

2. NEAR duplicates: word-level 3-gram shingling + MinHash (k=64 hash functions via vectorized
   universal hashing) + LSH banding (b=16 bands x r=4 rows) to find CANDIDATE similar pairs
   cheaply (avoids an O(n^2) pairwise comparison over the whole corpus), then each candidate pair
   is VERIFIED with an exact Jaccard similarity over the full shingle sets (removes MinHash/LSH
   false positives). Verified pairs are merged via Union-Find into connected-component clusters.
   Threshold is configurable (--threshold, default 0.7); the script also reports cluster counts at
   several thresholds (0.5/0.6/0.7/0.8) to show sensitivity.

3. Clusters are split into "pure exact" (every member has identical normalized text) vs.
   "true near-duplicate" (paraphrase-like - similar but not byte-identical) for reporting.

4. A dedicated search for texts mentioning @MariaVladimirovnaZakharova (case-insensitive) checks
   whether they fall into one or several near-duplicate clusters, to root-cause the "maria"/"lying"
   BERTopic topic identified in the Phase C quality report.

Outputs (written to artifacts/experiments/profiler_prototype/):
  - duplicate_clusters.csv: one row per cluster (>=2 members) with size, type, sample texts.
  - duplicate_analysis_summary.json: corpus-level stats + threshold sensitivity + recommendation.

Run: `python -m narrative_lens.evaluation.analyze_text_duplicates [--threshold 0.7]` from repo root.
"""

import argparse
import json
import re
from collections import defaultdict
import os

import pandas as pd

# Shared MinHash/LSH/Jaccard near-duplicate detection - see text_dedup.py docstring. This is the
# SAME method train_topics.py uses to deduplicate the soft_v2 training texts, so results here stay
# comparable to what actually gets applied before a BERTopic fit.
from narrative_lens.data.text_dedup import (
    cluster_at_threshold,
    build_minhash_signatures,
    lsh_candidate_pairs,
    get_shingles,
    normalize_for_exact,
)

RAW_FILES = [
    "data/raw/gemini_natural_dataset.csv",
    "data/raw/gpt_natural_dataset.csv",
    "data/raw/twitter_natural_dataset.csv",
    "data/raw/telegram_natural_dataset.csv",
]

MARIA_PATTERN = re.compile(r"mariavladimirovnazakharova", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_corpus():
    frames = []
    for path in RAW_FILES:
        df = pd.read_csv(path)
        frames.append(df[["text"]].dropna())
    full = pd.concat(frames, ignore_index=True)
    texts = full["text"].astype(str).tolist()
    return texts


# ---------------------------------------------------------------------------
# Exact duplicates
# ---------------------------------------------------------------------------

def find_exact_duplicate_groups(texts):
    groups = defaultdict(list)
    for idx, text in enumerate(texts):
        groups[normalize_for_exact(text)].append(idx)
    dup_groups = {k: v for k, v in groups.items() if len(v) >= 2}
    return dup_groups


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--top-groups", type=int, default=15)
    args = parser.parse_args()

    print("Loading corpus...")
    texts = load_corpus()
    n_docs = len(texts)
    print(f"Total texts: {n_docs}")

    print("\n=== Exact duplicates ===")
    exact_groups = find_exact_duplicate_groups(texts)
    n_exact_dup_texts = sum(len(v) for v in exact_groups.values())
    n_exact_removed_if_dedup = sum(len(v) - 1 for v in exact_groups.values())
    print(f"Exact-duplicate groups (size>=2): {len(exact_groups)}")
    print(f"Texts involved in exact duplication: {n_exact_dup_texts} "
          f"({100 * n_exact_dup_texts / n_docs:.2f}% of corpus)")
    print(f"Texts that would be removed keeping 1/group: {n_exact_removed_if_dedup} "
          f"({100 * n_exact_removed_if_dedup / n_docs:.2f}% of corpus)")

    largest_exact = sorted(exact_groups.items(), key=lambda kv: -len(kv[1]))[:args.top_groups]
    print(f"\nTop {len(largest_exact)} largest exact-duplicate groups:")
    for norm_text, idxs in largest_exact:
        print(f"  size={len(idxs)}: {norm_text[:120]!r}")

    print("\nBuilding shingles + MinHash signatures for near-duplicate detection...")
    shingle_sets = [get_shingles(t) for t in texts]
    signatures = build_minhash_signatures(shingle_sets)
    candidate_pairs = lsh_candidate_pairs(signatures)
    print(f"LSH candidate pairs found: {len(candidate_pairs)}")

    print("\n=== Near-duplicate threshold sensitivity ===")
    sensitivity = {}
    for t in [0.5, 0.6, 0.7, 0.8]:
        clusters, verified_pairs = cluster_at_threshold(candidate_pairs, shingle_sets, n_docs, t)
        n_members = sum(len(v) for v in clusters.values())
        n_removed = sum(len(v) - 1 for v in clusters.values())
        sensitivity[t] = {
            "n_clusters": len(clusters),
            "n_members": n_members,
            "n_removed_if_dedup": n_removed,
            "pct_of_corpus_removed": round(100 * n_removed / n_docs, 3),
        }
        print(f"threshold={t}: clusters={len(clusters)}, members={n_members}, "
              f"would_remove={n_removed} ({100 * n_removed / n_docs:.2f}%)")

    chosen_threshold = args.threshold
    clusters, verified_pairs = cluster_at_threshold(
        candidate_pairs, shingle_sets, n_docs, chosen_threshold
    )
    print(f"\n=== Near-duplicate clusters at chosen threshold={chosen_threshold} ===")
    print(f"Clusters: {len(clusters)}, verified similar pairs: {verified_pairs}")

    # Classify clusters as pure-exact vs true-near-duplicate
    cluster_rows = []
    n_pure_exact_clusters = 0
    n_true_near_dup_clusters = 0
    for root, members in clusters.items():
        normalized_texts = {normalize_for_exact(texts[i]) for i in members}
        is_pure_exact = len(normalized_texts) == 1
        if is_pure_exact:
            n_pure_exact_clusters += 1
        else:
            n_true_near_dup_clusters += 1
        sample = [texts[i][:200] for i in members[:3]]
        cluster_rows.append({
            "cluster_id": root,
            "size": len(members),
            "type": "pure_exact" if is_pure_exact else "near_duplicate",
            "n_distinct_normalized_texts": len(normalized_texts),
            "sample_texts": " ||| ".join(sample),
        })
    cluster_rows.sort(key=lambda r: -r["size"])

    os.makedirs("artifacts/experiments/profiler_prototype", exist_ok=True)
    clusters_csv_path = "artifacts/experiments/profiler_prototype/duplicate_clusters.csv"
    pd.DataFrame(cluster_rows).to_csv(clusters_csv_path, index=False, encoding="utf-8-sig")
    print(f"\nWrote cluster details to {clusters_csv_path}")

    print(f"\nTop {args.top_groups} largest clusters at threshold={chosen_threshold}:")
    for row in cluster_rows[:args.top_groups]:
        print(f"  size={row['size']} type={row['type']}: {row['sample_texts'][:200]!r}")

    # --- Maria/lying specific investigation ---
    print("\n=== @MariaVladimirovnaZakharova specific investigation ===")
    maria_idxs = [i for i, t in enumerate(texts) if MARIA_PATTERN.search(t)]
    print(f"Texts mentioning @MariaVladimirovnaZakharova: {len(maria_idxs)}")
    maria_idx_set = set(maria_idxs)
    doc_to_cluster = {}
    for row in cluster_rows:
        pass
    doc_to_root = {}
    for root, members in clusters.items():
        for m in members:
            doc_to_root[m] = root
    maria_clusters = defaultdict(list)
    maria_singletons = []
    for i in maria_idxs:
        if i in doc_to_root:
            maria_clusters[doc_to_root[i]].append(i)
        else:
            maria_singletons.append(i)
    print(f"Maria-texts grouped into {len(maria_clusters)} near-duplicate cluster(s) "
          f"(covering {sum(len(v) for v in maria_clusters.values())} texts); "
          f"{len(maria_singletons)} maria-texts had no near-duplicate match at threshold="
          f"{chosen_threshold}.")
    for root, members in sorted(maria_clusters.items(), key=lambda kv: -len(kv[1])):
        print(f"  cluster size={len(members)} (of which maria-related: {len(members)})")
        for i in members[:5]:
            print(f"    - {texts[i][:150]!r}")

    # --- Summary / recommendation ---
    n_near_dup_members = sum(len(v) for v in clusters.values())
    n_near_dup_removed = sum(len(v) - 1 for v in clusters.values())

    summary = {
        "n_docs": n_docs,
        "exact_duplicates": {
            "n_groups": len(exact_groups),
            "n_texts_involved": n_exact_dup_texts,
            "pct_of_corpus": round(100 * n_exact_dup_texts / n_docs, 3),
            "n_removed_if_dedup": n_exact_removed_if_dedup,
        },
        "near_duplicates_at_chosen_threshold": {
            "threshold": chosen_threshold,
            "n_clusters": len(clusters),
            "n_pure_exact_clusters": n_pure_exact_clusters,
            "n_true_near_duplicate_clusters": n_true_near_dup_clusters,
            "n_texts_involved": n_near_dup_members,
            "pct_of_corpus": round(100 * n_near_dup_members / n_docs, 3),
            "n_removed_if_dedup": n_near_dup_removed,
            "pct_removed_if_dedup": round(100 * n_near_dup_removed / n_docs, 3),
        },
        "threshold_sensitivity": sensitivity,
        "maria_investigation": {
            "n_maria_texts": len(maria_idxs),
            "n_clusters_containing_maria_texts": len(maria_clusters),
            "n_maria_texts_in_clusters": sum(len(v) for v in maria_clusters.values()),
            "n_maria_texts_without_near_dup_match": len(maria_singletons),
        },
    }
    summary_path = "artifacts/experiments/profiler_prototype/duplicate_analysis_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nWrote summary to {summary_path}")

    print("\n=== FINAL SUMMARY ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

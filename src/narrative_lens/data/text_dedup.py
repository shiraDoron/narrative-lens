"""
Shared near-duplicate text detection (MinHash + LSH + Jaccard verification + Union-Find).

Single source of truth for the near-duplicate detection method validated in
`analyze_text_duplicates.py` (word-level 3-gram shingling + MinHash(k=64) via vectorized
universal hashing + LSH banding to find candidate pairs cheaply, each candidate verified via
exact Jaccard similarity over the full shingle sets before merging into clusters). Threshold
0.7 was chosen after inspecting cluster examples at 0.5/0.6/0.7/0.8 (see
`artifacts/experiments/profiler_prototype/duplicate_analysis_summary.json`) - genuine paraphrase-level
near-duplicates at 0.7, fewer false positives than looser thresholds.

Used by:
  - `analyze_text_duplicates.py` (read-only corpus-wide investigation, no dedup applied).
  - `train_topics.py` (applies `deduplicate_texts()` to the SOFT_v2 training texts only, keeps
    exactly one representative per near-duplicate cluster before `BERTopic().fit()`).
"""

import hashlib
import re
from collections import defaultdict

import numpy as np

SHINGLE_K = 3          # word-level 3-grams
MINHASH_K = 64          # number of hash functions
LSH_BANDS = 16
LSH_ROWS = 4            # LSH_BANDS * LSH_ROWS must equal MINHASH_K
MERSENNE_PRIME = (1 << 61) - 1

# Recommended default operating threshold - see module docstring / duplicate_analysis_summary.json.
NEAR_DUP_THRESHOLD = 0.7

TOKEN_RE = re.compile(r"\w+")
WHITESPACE_RE = re.compile(r"\s+")


def normalize_for_exact(text):
    return WHITESPACE_RE.sub(" ", text.strip().lower())


def get_shingles(text, k=SHINGLE_K):
    tokens = TOKEN_RE.findall(text.lower())
    if len(tokens) < k:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i + k]) for i in range(len(tokens) - k + 1)}


def shingle_to_hash(shingle):
    digest = hashlib.md5(" ".join(shingle).encode("utf-8")).hexdigest()
    return int(digest[:16], 16)  # 64-bit int


def build_minhash_signatures(shingle_sets, k=MINHASH_K, seed=1337):
    rng = np.random.RandomState(seed)
    a = rng.randint(1, MERSENNE_PRIME - 1, size=k, dtype=np.int64)
    b = rng.randint(0, MERSENNE_PRIME - 1, size=k, dtype=np.int64)

    signatures = np.full((len(shingle_sets), k), np.iinfo(np.int64).max, dtype=np.int64)
    for doc_idx, shingles in enumerate(shingle_sets):
        if not shingles:
            continue
        hashes = np.array([shingle_to_hash(s) % MERSENNE_PRIME for s in shingles], dtype=np.int64)
        # (a * h + b) % p for every (hash, hash-function) pair, then min over shingles.
        combined = (np.outer(hashes, a) + b) % MERSENNE_PRIME
        signatures[doc_idx] = combined.min(axis=0)
    return signatures


def lsh_candidate_pairs(signatures, bands=LSH_BANDS, rows=LSH_ROWS):
    assert bands * rows == signatures.shape[1]
    candidates = set()
    for band_idx in range(bands):
        buckets = defaultdict(list)
        band_cols = signatures[:, band_idx * rows:(band_idx + 1) * rows]
        for doc_idx in range(signatures.shape[0]):
            key = (band_idx, tuple(band_cols[doc_idx].tolist()))
            buckets[key].append(doc_idx)
        for members in buckets.values():
            if len(members) < 2:
                continue
            if len(members) > 500:
                # Extremely large bucket (likely a mass-duplicate group) - still verify all
                # pairs would be too expensive; cap verification by pairing everyone against the
                # first member (still correctly clusters via union-find transitivity for true
                # near-duplicates, at some risk of missing rare within-bucket sub-splits).
                anchor = members[0]
                for m in members[1:]:
                    candidates.add((anchor, m))
            else:
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        candidates.add((members[i], members[j]))
    return candidates


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[rx] = ry


def cluster_at_threshold(candidate_pairs, shingle_sets, n_docs, threshold):
    uf = UnionFind(n_docs)
    verified_pairs = 0
    for i, j in candidate_pairs:
        sim = jaccard(shingle_sets[i], shingle_sets[j])
        if sim >= threshold:
            uf.union(i, j)
            verified_pairs += 1
    groups = defaultdict(list)
    for idx in range(n_docs):
        groups[uf.find(idx)].append(idx)
    clusters = {root: members for root, members in groups.items() if len(members) >= 2}
    return clusters, verified_pairs


def find_near_duplicate_clusters(texts, threshold=NEAR_DUP_THRESHOLD):
    """Full pipeline: texts -> shingles -> MinHash signatures -> LSH candidates -> verified
    (Jaccard >= threshold) clusters. Returns (clusters, verified_pairs) where clusters is a
    dict of root_index -> sorted list of member indices (only clusters with size >= 2)."""
    n_docs = len(texts)
    shingle_sets = [get_shingles(t) for t in texts]
    signatures = build_minhash_signatures(shingle_sets)
    candidate_pairs = lsh_candidate_pairs(signatures)
    clusters, verified_pairs = cluster_at_threshold(candidate_pairs, shingle_sets, n_docs, threshold)
    clusters = {root: sorted(members) for root, members in clusters.items()}
    return clusters, verified_pairs


def deduplicate_texts(texts, threshold=NEAR_DUP_THRESHOLD):
    """Keeps exactly ONE representative (the lowest original index) per near-duplicate
    cluster (Jaccard >= threshold on word-3-gram shingles); all other texts are dropped.
    Texts with no near-duplicate match are kept unchanged. Does NOT mutate `texts` or touch
    any file - purely returns which indices to keep, for the caller to filter in-memory.

    Returns:
        kept_indices: sorted list of indices into `texts` to keep.
        cluster_summaries: list of {"kept_index", "dropped_indices", "size"} dicts, one per
            near-duplicate cluster that had >=2 members (for reporting/auditing).
    """
    clusters, _ = find_near_duplicate_clusters(texts, threshold=threshold)
    to_drop = set()
    cluster_summaries = []
    for members in clusters.values():
        keep = members[0]
        drop = members[1:]
        to_drop.update(drop)
        cluster_summaries.append({
            "kept_index": keep,
            "dropped_indices": drop,
            "size": len(members),
        })
    kept_indices = [i for i in range(len(texts)) if i not in to_drop]
    return kept_indices, cluster_summaries

"""Few-shot author adaptation with NO training, frozen SBERT embeddings only.

For each of the 14 frozen confirmatory authors (EXPERIMENTS.md S25, set file at
artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json):
  - build 7 narrative centroids from TRAIN-author embeddings (train split rows of
    the S25 LOAO split via split_leave_one_author, author-disjoint from test author),
  - adapt the true-narrative centroid toward the test author using k labeled support
    rows from the test author (k in {0,1,5,10,20}, seed 42, strictly disjoint from
    the query rows evaluated),
  - classify queries by nearest adapted centroid (cosine).

Adaptation rule (weight a): adapted_t = normalize((1-a) * C_t + a * S), where C_t
is the L2-normalized global centroid of the author's true narrative t and S is the
L2-normalized mean of the k support embeddings. Other centroids unchanged.
Weight grid tried: {0.25, 0.5, 1.0}; primary a=0.5 fixed before seeing results.

Run (CPU only) from repo root: .venv/bin/python artifacts/experiments/few_shot_adaptation/run_fewshot.py
Writes fewshot_results.json next to this script.
"""

import json
import os
import sys

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from narrative_lens.config import NARRATIVES  # noqa: E402
from narrative_lens.train import load_raw_data, split_leave_one_author  # noqa: E402

SEED = 42
SBERT_NAME = "sentence-transformers/all-MiniLM-L6-v2"
KS = (0, 1, 5, 10, 20)
WEIGHTS = (0.25, 0.5, 1.0)
PRIMARY_WEIGHT = 0.5
BASELINE_MEAN = 0.39
BASELINE_MEDIAN = 0.388
POSITIVE_MARGIN = 0.03

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(OUT_DIR, "fewshot_results.json")
FROZEN_SET_FILE = os.path.join(
    REPO_ROOT, "artifacts", "experiments", "narrative_fresh_author_audit",
    "fresh_author_confirmatory_set.json",
)


def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)


def l2norm(v, eps=1e-12):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, eps)


def main():
    set_seed(SEED)
    with open(FROZEN_SET_FILE, "r", encoding="utf-8") as f:
        frozen = json.load(f)
    authors = [(a["author_source"], a["narrative"]) for a in frozen["selected_authors"]]
    assert len(authors) == 14, f"expected 14 authors, got {len(authors)}"
    true_idx = {a: NARRATIVES.index(n) for a, n in authors}

    os.chdir(REPO_ROOT)
    df = load_raw_data()
    df = df.copy()
    df["_rowid"] = np.arange(len(df))
    df["text"] = df["text"].astype(str).str.slice(0, 3000)
    label_of = df["label"].astype(int).to_numpy()

    from sentence_transformers import SentenceTransformer
    print(f"Loading frozen SBERT '{SBERT_NAME}' (encode-only, CPU)...", flush=True)
    model = SentenceTransformer(SBERT_NAME, device="cpu")
    texts = df["text"].tolist()
    print(f"Encoding {len(texts)} texts...", flush=True)
    emb = model.encode(texts, convert_to_numpy=True, show_progress_bar=False, batch_size=64)
    emb = emb.astype(np.float64)
    print(f"Embeddings shape: {emb.shape}", flush=True)

    per_author = {}
    disjointness = {}
    for author, narrative in authors:
        train_data, _val_data, test_data = split_leave_one_author(df, author)
        train_idx = train_data["_rowid"].to_numpy()
        test_idx = test_data["_rowid"].to_numpy()
        t = true_idx[author]
        centroids = np.zeros((len(NARRATIVES), emb.shape[1]), dtype=np.float64)
        for c in range(len(NARRATIVES)):
            rows = train_idx[label_of[train_idx] == c]
            assert len(rows) > 0, f"no train rows for narrative {c} (author {author})"
            centroids[c] = l2norm(emb[rows].mean(axis=0))

        rng = np.random.RandomState(SEED)
        perm = rng.permutation(len(test_idx))
        test_labels = label_of[test_idx]
        assert set(test_labels.tolist()) == {t}, f"{author} not single-narrative: {set(test_labels.tolist())}"

        k_res = {}
        disj = {"n_test": int(len(test_idx)), "per_k": {}}
        for k in KS:
            sup_pos = perm[:k]
            qry_pos = perm[k:]
            sup_idx = test_idx[sup_pos]
            qry_idx = test_idx[qry_pos]
            assert len(set(sup_idx.tolist()) & set(qry_idx.tolist())) == 0
            assert len(sup_idx) + len(qry_idx) == len(test_idx)
            disj["per_k"][str(k)] = {
                "n_support": int(len(sup_idx)),
                "n_query": int(len(qry_idx)),
                "overlap": 0,
            }
            q_emb = l2norm(emb[qry_idx])
            if k > 0:
                s_mean = l2norm(emb[sup_idx].mean(axis=0))
            else:
                s_mean = None
            recalls = {}
            for a in WEIGHTS:
                if k == 0:
                    adapted = l2norm(centroids)
                else:
                    adapted = l2norm(centroids).copy()
                    adapted[t] = l2norm((1.0 - a) * l2norm(centroids)[t] + a * s_mean)
                    adapted = l2norm(adapted)
                sims = q_emb @ adapted.T
                pred = sims.argmax(axis=1)
                recalls[str(a)] = float((pred == t).mean())
            k_res[str(k)] = recalls
        per_author[author] = {"true_narrative": narrative, "true_index": int(t), "recall": k_res}
        disjointness[author] = disj

    summary = {}
    for k in KS:
        for a in WEIGHTS:
            vals = np.array([per_author[au]["recall"][str(k)][str(a)] for au, _ in authors])
            summary[f"k={k}/a={a}"] = {
                "mean": float(vals.mean()),
                "median": float(np.median(vals)),
                "std": float(vals.std()),
                "min": float(vals.min()),
                "max": float(vals.max()),
            }
    k0 = summary[f"k=0/a={PRIMARY_WEIGHT}"]["mean"]

    per_k_primary = {}
    for k in KS:
        s = summary[f"k={k}/a={PRIMARY_WEIGHT}"]
        per_k_primary[str(k)] = s

    best_k_le10 = max([1, 5, 10], key=lambda k: per_k_primary[str(k)]["mean"])
    best_mean = per_k_primary[str(best_k_le10)]["mean"]
    gain_vs_s25 = best_mean - BASELINE_MEAN
    passed = bool(best_mean > BASELINE_MEAN + POSITIVE_MARGIN)

    results = {
        "seed": SEED,
        "sbert_model": SBERT_NAME,
        "frozen_set": "artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json",
        "split": "split_leave_one_author per author (S25 convention); centroids from TRAIN split only (author-disjoint)",
        "adaptation_rule": "adapted_t = normalize((1-a)*C_t + a*S); others unchanged; cosine nearest centroid",
        "weights_tried": list(WEIGHTS),
        "primary_weight": PRIMARY_WEIGHT,
        "ks": list(KS),
        "baseline_s25_sbert_original": {"mean": BASELINE_MEAN, "median": BASELINE_MEDIAN},
        "k0_centroid_baseline_primary_weight": {"mean": k0, "median": per_k_primary["0"]["median"]},
        "per_k_primary_weight": per_k_primary,
        "full_grid_summary": summary,
        "per_author": per_author,
        "disjointness": disjointness,
        "disjointness_verified": bool(all(
            d["per_k"][str(k)]["overlap"] == 0
            and d["per_k"][str(k)]["n_support"] + d["per_k"][str(k)]["n_query"] == d["n_test"]
            for d in disjointness.values() for k in KS
        )),
        "positive_bar": "mean recall at some k<=10 beats S25 baseline mean (0.39) by more than 3pp (i.e. > 0.42)",
        "best_k_le10": int(best_k_le10),
        "best_mean_le10": float(best_mean),
        "gain_vs_s25_mean_pp": float(gain_vs_s25 * 100.0),
        "pass": passed,
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {RESULTS_FILE}", flush=True)
    print(f"k=0 mean={k0:.4f} | best k<=10: k={best_k_le10} mean={best_mean:.4f} "
          f"(gain {gain_vs_s25*100:+.2f}pp) -> {'PASS' if passed else 'FAIL'}", flush=True)


if __name__ == "__main__":
    main()

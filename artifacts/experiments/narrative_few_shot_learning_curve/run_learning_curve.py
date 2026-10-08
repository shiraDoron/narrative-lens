"""Few-shot author-adaptation LEARNING CURVE, with multi-seed sampling robustness.

Extends EXPERIMENTS.md Section 35A (artifacts/experiments/few_shot_adaptation/run_fewshot.py),
which drew a SINGLE fixed sample of k support rows per author (data seed=42, support sets for
different k were NESTED PREFIXES of one permutation, not independent draws). That is exactly
the methodological gap this script closes: for k in {1, 5, 10, 20} it draws SAMPLING_SEEDS
independent random samples of k support rows per author, so no reported number depends on which
particular k examples happened to be chosen.

Reused EXACTLY from Section 35A / Section 25, never swapped or re-derived:
  - the 14 frozen fresh authors, same file, same order:
    artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json
  - the frozen SBERT all-MiniLM-L6-v2 encoder (no fine-tuning)
  - narrative_lens.train.load_raw_data() + split_leave_one_author() (identical per-author
    train/test split, author-disjoint train, same data-load seed 42, same 3000-char truncation)
  - the centroid-adaptation rule and PRIMARY weight a=0.5 from Section 35A:
      adapted_t = normalize((1-a)*C_t + a*S)
    only the target narrative's centroid is moved; prediction = cosine-nearest centroid.
    Weight is NOT re-tuned here (that was already explored in Section 35A; re-tuning now would
    be post-hoc fishing).
  - the deployed zero-shot baseline (k=0) = Section 25's trained `sbert_original` per-author
    recall_true_narrative values, loaded directly from
    artifacts/experiments/narrative_fresh_author_confirmatory/results.json. This is the exact
    "vs 39.0% zero-shot" baseline quoted in Section 35A's conclusion.

  IMPORTANT DISAMBIGUATION (see docs/EXPERIMENTS.md Section 36 for the full discussion):
  Section 35A's own k=0 (mean 0.326) is a DIFFERENT number: it is the *centroid method's own*
  unadapted nearest-centroid baseline (no training, no support rows), not the trained
  classifier's zero-shot recall (0.390/0.388). Both are computed and reported separately here
  under distinct keys so the two are never conflated:
    - "deployed_zero_shot_baseline"   -> trained sbert_original classifier (Section 25), used
                                         as the k=0 anchor on the main learning-curve figure and
                                         for the "vs zero-shot" improved/degraded counts, exactly
                                         as Section 35A's conclusion used it.
    - "centroid_zero_shot_reference"  -> this script's own unadapted (k=0) centroid-method
                                         baseline, used only as a same-method internal
                                         consistency / replication check against Section 35A's
                                         published 0.326.

New in this script: k in {1, 5, 10, 20}, each evaluated under SAMPLING_SEEDS = [1, 2, 3, 4, 5]
independent support draws per author. Seeds and k values are fixed below, in advance, before
running or seeing any result; they are not changed after the fact. If k=20 is not achievable for
some author (fewer than 21 test rows) this is reported honestly in sanity_checks.json, not
silently patched by swapping or dropping an author.

Pre-registered interpretation thresholds (fixed before running; see INTERPRETATION_RULES below
and the "interpretation" block of aggregated_table.json):
  - efficiency "A" (most of the gap closes by k=5)   if gain(k=5)  >= 0.70 * gain(k=20)
  - efficiency "B" (needs k=10-20)                    otherwise
  - stability "heterogeneous"                         if CV(k=10) > 0.35 OR >30% of authors
                                                        degrade vs the deployed zero-shot baseline
                                                        at k=10
  - replication "does_not_replicate_cleanly"           if |mean_recall(k=10) - 0.649| > 0.05
                                                        (5pp) vs Section 35A's published number,
                                                        OR the curve is non-monotonic by more than
                                                        2pp at any step
  gain(k) := mean_recall(k) - deployed_zero_shot_baseline_mean

Run (CPU only) from repo root:
  python artifacts/experiments/narrative_few_shot_learning_curve/run_learning_curve.py
Writes all artifacts into this script's own directory.
"""

import json
import os
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from narrative_lens.config import NARRATIVES  # noqa: E402
from narrative_lens.train import load_raw_data, split_leave_one_author  # noqa: E402

# ---------------------------------------------------------------------------
# Fixed configuration (pre-registered; do not change after seeing results)
# ---------------------------------------------------------------------------
DATA_SEED = 42
SAMPLING_SEEDS = [1, 2, 3, 4, 5]
KS_FEWSHOT = (1, 5, 10, 20)
ALL_KS = (0,) + KS_FEWSHOT
PRIMARY_WEIGHT = 0.5
SBERT_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TEXT_TRUNC_CHARS = 3000
N_BOOTSTRAP = 10000
BOOT_SEED = 123

MODE_A_FRACTION = 0.70
HETEROGENEITY_CV_THRESHOLD = 0.35
HETEROGENEITY_DEGRADE_FRACTION = 0.30
REPLICATION_TOLERANCE = 0.05
MONOTONIC_TOLERANCE = 0.02
SECTION_35A_PUBLISHED_K10_MEAN = 0.649

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FROZEN_SET_FILE = os.path.join(
    REPO_ROOT, "artifacts", "experiments", "narrative_fresh_author_audit",
    "fresh_author_confirmatory_set.json",
)
BASELINE_RESULTS_FILE = os.path.join(
    REPO_ROOT, "artifacts", "experiments", "narrative_fresh_author_confirmatory", "results.json",
)


def l2norm(v, eps=1e-12):
    v = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, eps)


def bootstrap_ci(values, n_boot=N_BOOTSTRAP, seed=BOOT_SEED, alpha=0.05):
    """Percentile bootstrap CI for the mean of `values` (resampling over authors)."""
    values = np.asarray(values, dtype=np.float64)
    if len(values) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.RandomState(seed)
    n = len(values)
    boot_means = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        idx = rng.randint(0, n, size=n)
        boot_means[i] = values[idx].mean()
    lo = float(np.percentile(boot_means, 100 * alpha / 2))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return (lo, hi)


def main():
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    # --- Load frozen 14-author cohort (verbatim reuse, not swapped/re-derived) ---
    with open(FROZEN_SET_FILE, "r", encoding="utf-8") as f:
        frozen = json.load(f)
    authors = [(a["author_source"], a["narrative"]) for a in frozen["selected_authors"]]
    assert len(authors) == 14, f"expected 14 frozen authors, got {len(authors)}"
    author_order = [a for a, _ in authors]
    narrative_of_author = {a: n for a, n in authors}
    true_idx = {a: NARRATIVES.index(n) for a, n in authors}
    log(f"Loaded {len(authors)} frozen authors from {FROZEN_SET_FILE}")

    # --- Load Section 25's trained sbert_original per-author recall (the deployed zero-shot
    #     baseline quoted as "39.0% zero-shot" in Section 35A's conclusion) ---
    with open(BASELINE_RESULTS_FILE, "r", encoding="utf-8") as f:
        baseline_raw = json.load(f)
    missing_authors = [a for a in author_order if a not in baseline_raw]
    assert not missing_authors, f"authors missing from {BASELINE_RESULTS_FILE}: {missing_authors}"
    deployed_zero_shot = {}
    deployed_n_test = {}
    for a in author_order:
        block = baseline_raw[a]["sbert_original"]
        assert block["narrative"] == narrative_of_author[a], (
            f"narrative mismatch for {a}: {block['narrative']} vs {narrative_of_author[a]}"
        )
        deployed_zero_shot[a] = float(block["recall_true_narrative"])
        deployed_n_test[a] = int(block["n_test"])
    log(f"Loaded deployed zero-shot (Section 25 sbert_original) baseline for all 14 authors "
        f"from {BASELINE_RESULTS_FILE}")

    # --- Load raw data + embed with the frozen SBERT encoder (identical to Section 35A) ---
    os.chdir(REPO_ROOT)
    df = load_raw_data()
    df = df.copy()
    df["_rowid"] = np.arange(len(df))
    df["text"] = df["text"].astype(str).str.slice(0, TEXT_TRUNC_CHARS)
    label_of = df["label"].astype(int).to_numpy()
    dataset_total_rows = int(len(df))

    from sentence_transformers import SentenceTransformer
    log(f"Loading frozen SBERT '{SBERT_NAME}' (encode-only, CPU)...")
    model = SentenceTransformer(SBERT_NAME, device="cpu")
    texts = df["text"].tolist()
    log(f"Encoding {len(texts)} texts...")
    emb = model.encode(texts, convert_to_numpy=True, show_progress_bar=False, batch_size=64)
    emb = emb.astype(np.float64)
    log(f"Embeddings shape: {emb.shape}")

    # --- Per-author: build train-only centroids, check split sizes, run k=0 (centroid
    #     reference) and k in {1,5,10,20} under SAMPLING_SEEDS independent draws ---
    per_author_centroid_k0 = {}
    per_author_k = {k: {} for k in KS_FEWSHOT}  # per_author_k[k][author] = {seed: recall}
    disjointness_log = {}
    n_test_check = {}
    k20_feasibility = {}

    pooled_true_by_k = {0: []}
    pooled_pred_by_k = {0: []}
    for k in KS_FEWSHOT:
        pooled_true_by_k[k] = {s: [] for s in SAMPLING_SEEDS}
        pooled_pred_by_k[k] = {s: [] for s in SAMPLING_SEEDS}

    for author in author_order:
        narrative = narrative_of_author[author]
        t = true_idx[author]
        train_data, _val_data, test_data = split_leave_one_author(df, author)
        train_idx = train_data["_rowid"].to_numpy()
        test_idx = test_data["_rowid"].to_numpy()
        n_test = int(len(test_idx))
        n_test_check[author] = {
            "n_test_from_split": n_test,
            "n_test_from_section25_results": deployed_n_test[author],
            "match": n_test == deployed_n_test[author],
        }

        test_labels = label_of[test_idx]
        assert set(test_labels.tolist()) == {t}, (
            f"{author} test set is not single-narrative: {set(test_labels.tolist())}"
        )

        centroids = np.zeros((len(NARRATIVES), emb.shape[1]), dtype=np.float64)
        for c in range(len(NARRATIVES)):
            rows = train_idx[label_of[train_idx] == c]
            assert len(rows) > 0, f"no train rows for narrative {c} (author {author})"
            centroids[c] = l2norm(emb[rows].mean(axis=0))
        centroids = l2norm(centroids)

        # k=0 centroid-method internal reference (no support rows, no adaptation at all)
        q_emb_all = l2norm(emb[test_idx])
        sims0 = q_emb_all @ centroids.T
        pred0 = sims0.argmax(axis=1)
        per_author_centroid_k0[author] = float((pred0 == t).mean())
        pooled_true_by_k[0].extend([t] * n_test)
        pooled_pred_by_k[0].extend(pred0.tolist())

        k20_feasibility[author] = bool(n_test >= 21)  # need >=1 query row left after 20 support

        for k in KS_FEWSHOT:
            per_author_k[k][author] = {}
            disjointness_log.setdefault(author, {})[str(k)] = {}
            if n_test <= k:
                # Would leave zero query rows - not achievable; report honestly, do not swap author.
                for seed in SAMPLING_SEEDS:
                    per_author_k[k][author][str(seed)] = None
                disjointness_log[author][str(k)] = {"feasible": False, "n_test": n_test}
                continue
            author_position = author_order.index(author)
            for seed in SAMPLING_SEEDS:
                # Deterministic, reproducible per (seed, author): do NOT use Python's hash()
                # (randomized per-process via PYTHONHASHSEED), use the fixed author position
                # in the frozen cohort list instead.
                rng = np.random.RandomState(seed * 1000 + author_position)
                perm = rng.permutation(n_test)
                sup_pos = perm[:k]
                qry_pos = perm[k:]
                sup_idx = test_idx[sup_pos]
                qry_idx = test_idx[qry_pos]
                overlap = len(set(sup_idx.tolist()) & set(qry_idx.tolist()))
                assert overlap == 0
                assert len(sup_idx) + len(qry_idx) == n_test
                disjointness_log[author][str(k)].setdefault("per_seed", {})[str(seed)] = {
                    "n_support": int(len(sup_idx)), "n_query": int(len(qry_idx)), "overlap": int(overlap),
                }
                disjointness_log[author][str(k)]["feasible"] = True
                disjointness_log[author][str(k)]["n_test"] = n_test

                q_emb = l2norm(emb[qry_idx])
                s_mean = l2norm(emb[sup_idx].mean(axis=0))
                adapted = centroids.copy()
                adapted[t] = l2norm((1.0 - PRIMARY_WEIGHT) * centroids[t] + PRIMARY_WEIGHT * s_mean)
                adapted = l2norm(adapted)
                sims = q_emb @ adapted.T
                pred = sims.argmax(axis=1)
                recall = float((pred == t).mean())
                per_author_k[k][author][str(seed)] = recall
                pooled_true_by_k[k][seed].extend([t] * len(qry_idx))
                pooled_pred_by_k[k][seed].extend(pred.tolist())

        log(f"[{author}] narrative={narrative} n_test={n_test} k0_centroid_recall="
            f"{per_author_centroid_k0[author]:.4f} deployed_zero_shot="
            f"{deployed_zero_shot[author]:.4f}")

    # --- Pooled accuracy / macro-F1 (centroid method, self-consistent across k=0..20) ---
    from sklearn.metrics import accuracy_score, f1_score

    all_label_ids = list(range(len(NARRATIVES)))
    pooled_metrics = {}
    acc0 = accuracy_score(pooled_true_by_k[0], pooled_pred_by_k[0])
    f10 = f1_score(pooled_true_by_k[0], pooled_pred_by_k[0], labels=all_label_ids, average="macro")
    pooled_metrics[0] = {"accuracy": float(acc0), "macro_f1": float(f10), "n_seeds": 1}
    for k in KS_FEWSHOT:
        accs, f1s = [], []
        for seed in SAMPLING_SEEDS:
            yt, yp = pooled_true_by_k[k][seed], pooled_pred_by_k[k][seed]
            accs.append(accuracy_score(yt, yp))
            f1s.append(f1_score(yt, yp, labels=all_label_ids, average="macro"))
        pooled_metrics[k] = {
            "accuracy_mean": float(np.mean(accs)), "accuracy_std": float(np.std(accs)),
            "macro_f1_mean": float(np.mean(f1s)), "macro_f1_std": float(np.std(f1s)),
            "n_seeds": len(SAMPLING_SEEDS),
        }

    # --- Per-author aggregation across seeds, per k ---
    per_author_summary = {}
    for author in author_order:
        per_author_summary[author] = {
            "narrative": narrative_of_author[author],
            "deployed_zero_shot_baseline": deployed_zero_shot[author],
            "centroid_zero_shot_reference": per_author_centroid_k0[author],
            "by_k": {},
        }
        per_author_summary[author]["by_k"]["0"] = {
            "mean": deployed_zero_shot[author], "std": 0.0, "n_seeds": 1,
            "seed_values": None, "source": "section25_sbert_original_trained_classifier",
        }
        for k in KS_FEWSHOT:
            vals = per_author_k[k][author]
            seed_values = {s: v for s, v in vals.items()}
            feasible_vals = [v for v in seed_values.values() if v is not None]
            if feasible_vals:
                per_author_summary[author]["by_k"][str(k)] = {
                    "mean": float(np.mean(feasible_vals)),
                    "std": float(np.std(feasible_vals)),
                    "n_seeds": len(feasible_vals),
                    "seed_values": seed_values,
                    "feasible": True,
                }
            else:
                per_author_summary[author]["by_k"][str(k)] = {
                    "mean": None, "std": None, "n_seeds": 0,
                    "seed_values": seed_values, "feasible": False,
                }

    # --- Per-k aggregation across authors ---
    deployed_baseline_values = np.array([deployed_zero_shot[a] for a in author_order])
    centroid_k0_values = np.array([per_author_centroid_k0[a] for a in author_order])

    per_k_table = {}
    per_k_table["0"] = {
        "k": 0,
        "deployed_zero_shot_mean": float(deployed_baseline_values.mean()),
        "deployed_zero_shot_median": float(np.median(deployed_baseline_values)),
        "deployed_zero_shot_std": float(deployed_baseline_values.std()),
        "deployed_zero_shot_ci95": list(bootstrap_ci(deployed_baseline_values)),
        "centroid_reference_mean": float(centroid_k0_values.mean()),
        "centroid_reference_median": float(np.median(centroid_k0_values)),
        "centroid_reference_std": float(centroid_k0_values.std()),
        "centroid_reference_ci95": list(bootstrap_ci(centroid_k0_values)),
        "pooled_accuracy": pooled_metrics[0]["accuracy"],
        "pooled_macro_f1": pooled_metrics[0]["macro_f1"],
    }

    improved_degraded = {}
    for k in KS_FEWSHOT:
        author_means = np.array([per_author_summary[a]["by_k"][str(k)]["mean"] for a in author_order], dtype=np.float64)
        feasible_mask = np.array([per_author_summary[a]["by_k"][str(k)]["feasible"] for a in author_order])
        vals_for_agg = author_means[feasible_mask]
        n_infeasible = int((~feasible_mask).sum())

        seed_stds = [per_author_summary[a]["by_k"][str(k)]["std"] for a in author_order
                     if per_author_summary[a]["by_k"][str(k)]["feasible"]]

        deltas_vs_deployed = {}
        for a in author_order:
            entry = per_author_summary[a]["by_k"][str(k)]
            if entry["feasible"]:
                deltas_vs_deployed[a] = float(entry["mean"] - deployed_zero_shot[a])
        n_improved = sum(1 for d in deltas_vs_deployed.values() if d > 0)
        n_degraded = sum(1 for d in deltas_vs_deployed.values() if d < 0)
        n_unchanged = sum(1 for d in deltas_vs_deployed.values() if d == 0)
        biggest_gain_author = max(deltas_vs_deployed, key=lambda a: deltas_vs_deployed[a])
        biggest_degradation_author = min(deltas_vs_deployed, key=lambda a: deltas_vs_deployed[a])

        improved_degraded[str(k)] = {
            "n_improved": n_improved, "n_degraded": n_degraded, "n_unchanged": n_unchanged,
            "biggest_gain_author": biggest_gain_author,
            "biggest_gain_delta": deltas_vs_deployed[biggest_gain_author],
            "biggest_degradation_author": biggest_degradation_author,
            "biggest_degradation_delta": deltas_vs_deployed[biggest_degradation_author],
            "per_author_delta_vs_deployed_zero_shot": deltas_vs_deployed,
        }

        cv = float(vals_for_agg.std() / vals_for_agg.mean()) if vals_for_agg.mean() > 0 else float("nan")
        per_k_table[str(k)] = {
            "k": k,
            "n_authors_feasible": int(feasible_mask.sum()),
            "n_authors_infeasible": n_infeasible,
            "mean_recall": float(vals_for_agg.mean()),
            "median_recall": float(np.median(vals_for_agg)),
            "std_across_authors": float(vals_for_agg.std()),
            "ci95_across_authors": list(bootstrap_ci(vals_for_agg)),
            "mean_std_across_seeds_per_author": float(np.mean(seed_stds)) if seed_stds else None,
            "coefficient_of_variation_across_authors": cv,
            "pooled_accuracy_mean": pooled_metrics[k]["accuracy_mean"],
            "pooled_accuracy_std": pooled_metrics[k]["accuracy_std"],
            "pooled_macro_f1_mean": pooled_metrics[k]["macro_f1_mean"],
            "pooled_macro_f1_std": pooled_metrics[k]["macro_f1_std"],
        }

    # --- Per-narrative recall (mean across the authors of that narrative, mean-across-seeds) ---
    per_narrative = {}
    narratives_present = sorted(set(narrative_of_author.values()))
    for narrative in narratives_present:
        narrative_authors = [a for a in author_order if narrative_of_author[a] == narrative]
        per_narrative[narrative] = {"authors": narrative_authors, "by_k": {}}
        per_narrative[narrative]["by_k"]["0"] = float(
            np.mean([deployed_zero_shot[a] for a in narrative_authors]))
        for k in KS_FEWSHOT:
            vals = [per_author_summary[a]["by_k"][str(k)]["mean"] for a in narrative_authors
                    if per_author_summary[a]["by_k"][str(k)]["feasible"]]
            per_narrative[narrative]["by_k"][str(k)] = float(np.mean(vals)) if vals else None

    # --- Pre-registered interpretation rules, applied mechanically (no post-hoc tuning) ---
    base_mean = per_k_table["0"]["deployed_zero_shot_mean"]
    gain5 = per_k_table["5"]["mean_recall"] - base_mean
    gain10 = per_k_table["10"]["mean_recall"] - base_mean
    gain20 = per_k_table["20"]["mean_recall"] - base_mean
    frac5_of_20 = (gain5 / gain20) if gain20 > 0 else float("nan")

    efficiency_mode = "A" if (not np.isnan(frac5_of_20) and frac5_of_20 >= MODE_A_FRACTION) else "B"

    cv10 = per_k_table["10"]["coefficient_of_variation_across_authors"]
    frac_degraded_10 = improved_degraded["10"]["n_degraded"] / max(1, (
        improved_degraded["10"]["n_improved"] + improved_degraded["10"]["n_degraded"] + improved_degraded["10"]["n_unchanged"]))
    stability_mode = "heterogeneous" if (
        (not np.isnan(cv10) and cv10 > HETEROGENEITY_CV_THRESHOLD)
        or frac_degraded_10 > HETEROGENEITY_DEGRADE_FRACTION
    ) else "stable"

    k10_mean = per_k_table["10"]["mean_recall"]
    replicates_k10 = abs(k10_mean - SECTION_35A_PUBLISHED_K10_MEAN) <= REPLICATION_TOLERANCE
    curve_means = [per_k_table[str(k)]["mean_recall"] if k != 0 else base_mean for k in ALL_KS]
    monotonic = all(
        (curve_means[i + 1] - curve_means[i]) >= -MONOTONIC_TOLERANCE for i in range(len(curve_means) - 1)
    )
    replication_mode = "replicates_cleanly" if (replicates_k10 and monotonic) else "does_not_replicate_cleanly"

    interpretation = {
        "efficiency_mode": efficiency_mode,
        "efficiency_rule": f"A if gain(k=5)/gain(k=20) >= {MODE_A_FRACTION} else B",
        "frac5_of_gain20": frac5_of_20,
        "stability_mode": stability_mode,
        "stability_rule": (
            f"heterogeneous if CV(k=10) > {HETEROGENEITY_CV_THRESHOLD} or "
            f"degraded-author-fraction(k=10) > {HETEROGENEITY_DEGRADE_FRACTION}"
        ),
        "cv_at_k10": cv10,
        "fraction_degraded_at_k10": frac_degraded_10,
        "replication_mode": replication_mode,
        "replication_rule": (
            f"does_not_replicate_cleanly if |mean(k=10) - {SECTION_35A_PUBLISHED_K10_MEAN}| > "
            f"{REPLICATION_TOLERANCE} or curve non-monotonic by more than {MONOTONIC_TOLERANCE}"
        ),
        "mean_k10_this_run": k10_mean,
        "mean_k10_section35a_published": SECTION_35A_PUBLISHED_K10_MEAN,
        "curve_is_monotonic": monotonic,
        "curve_means_k_0_1_5_10_20": dict(zip([str(k) for k in ALL_KS], curve_means)),
    }

    # --- Sanity checks ---
    frozen_authors_section25 = sorted(baseline_raw.keys())
    sanity = {
        "n_frozen_authors": len(author_order),
        "frozen_authors_match_section25_results_file": sorted(author_order) == frozen_authors_section25,
        "zero_shot_baseline": {
            "mean_this_run": float(deployed_baseline_values.mean()),
            "section35a_published_mean": 0.390,
            "matches_within_1pp": abs(float(deployed_baseline_values.mean()) - 0.390) <= 0.01,
        },
        "test_set_sizes_match_split_function": n_test_check,
        "all_test_sizes_match": all(v["match"] for v in n_test_check.values()),
        "k20_feasible_for_all_authors": all(k20_feasibility.values()),
        "k20_infeasible_authors": [a for a, ok in k20_feasibility.items() if not ok],
        "support_query_disjoint_verified": all(
            disjointness_log[a][str(k)].get("feasible", False)
            and all(v["overlap"] == 0 for v in disjointness_log[a][str(k)].get("per_seed", {}).values())
            for a in author_order for k in KS_FEWSHOT
            if disjointness_log[a][str(k)].get("feasible", False)
        ),
        "labels_unchanged": all(narrative_of_author[a] == baseline_raw[a]["sbert_original"]["narrative"] for a in author_order),
        "same_dataset_version": {"dataset_total_rows": dataset_total_rows, "data_load_seed": DATA_SEED},
        "preprocessing": {"text_truncation_chars": TEXT_TRUNC_CHARS, "sbert_model": SBERT_NAME},
        "same_checkpoint_model_family": SBERT_NAME,
        "sampling_seeds_documented": SAMPLING_SEEDS,
        "primary_weight_reused_unchanged": PRIMARY_WEIGHT,
        "centroid_k0_vs_section35a_published": {
            "mean_this_run": float(centroid_k0_values.mean()),
            "section35a_published": 0.326,
            "difference_pp": float((centroid_k0_values.mean() - 0.326) * 100),
        },
    }
    all_sanity_passed = (
        sanity["frozen_authors_match_section25_results_file"]
        and sanity["zero_shot_baseline"]["matches_within_1pp"]
        and sanity["all_test_sizes_match"]
        and sanity["k20_feasible_for_all_authors"]
        and sanity["support_query_disjoint_verified"]
        and sanity["labels_unchanged"]
    )
    sanity["all_passed"] = all_sanity_passed

    with open(os.path.join(OUT_DIR, "sanity_checks.json"), "w", encoding="utf-8") as f:
        json.dump(sanity, f, indent=2)
    log(f"Wrote sanity_checks.json (all_passed={all_sanity_passed})")

    configuration = {
        "data_seed": DATA_SEED,
        "sampling_seeds": SAMPLING_SEEDS,
        "ks_fewshot": list(KS_FEWSHOT),
        "primary_weight": PRIMARY_WEIGHT,
        "sbert_model": SBERT_NAME,
        "text_truncation_chars": TEXT_TRUNC_CHARS,
        "n_bootstrap": N_BOOTSTRAP,
        "frozen_set_file": os.path.relpath(FROZEN_SET_FILE, REPO_ROOT),
        "baseline_results_file": os.path.relpath(BASELINE_RESULTS_FILE, REPO_ROOT),
        "interpretation_thresholds": {
            "mode_a_fraction": MODE_A_FRACTION,
            "heterogeneity_cv_threshold": HETEROGENEITY_CV_THRESHOLD,
            "heterogeneity_degrade_fraction": HETEROGENEITY_DEGRADE_FRACTION,
            "replication_tolerance": REPLICATION_TOLERANCE,
            "monotonic_tolerance": MONOTONIC_TOLERANCE,
            "section_35a_published_k10_mean": SECTION_35A_PUBLISHED_K10_MEAN,
        },
    }
    with open(os.path.join(OUT_DIR, "configuration.json"), "w", encoding="utf-8") as f:
        json.dump(configuration, f, indent=2)

    raw_results = {
        "configuration": configuration,
        "per_author_summary": per_author_summary,
        "per_k_table": per_k_table,
        "per_narrative": per_narrative,
        "improved_degraded_vs_deployed_zero_shot": improved_degraded,
        "interpretation": interpretation,
        "disjointness": disjointness_log,
    }
    with open(os.path.join(OUT_DIR, "raw_results.json"), "w", encoding="utf-8") as f:
        json.dump(raw_results, f, indent=2)
    log("Wrote raw_results.json")

    # --- CSV exports ---
    import csv as csv_module

    with open(os.path.join(OUT_DIR, "per_seed_results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv_module.writer(f)
        w.writerow(["author", "narrative", "k", "seed", "recall"])
        for a in author_order:
            w.writerow([a, narrative_of_author[a], 0, "NA", deployed_zero_shot[a]])
            for k in KS_FEWSHOT:
                for seed, val in per_author_k[k][a].items():
                    w.writerow([a, narrative_of_author[a], k, seed, "" if val is None else val])

    with open(os.path.join(OUT_DIR, "per_author_results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv_module.writer(f)
        w.writerow(["author", "narrative", "k", "mean_recall", "std_recall", "n_seeds", "feasible"])
        for a in author_order:
            w.writerow([a, narrative_of_author[a], 0, deployed_zero_shot[a], 0.0, 1, True])
            for k in KS_FEWSHOT:
                e = per_author_summary[a]["by_k"][str(k)]
                w.writerow([a, narrative_of_author[a], k, e["mean"], e["std"], e["n_seeds"], e["feasible"]])

    with open(os.path.join(OUT_DIR, "aggregated_table.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv_module.writer(f)
        w.writerow(["k", "mean_recall", "median_recall", "std_across_authors", "ci95_low", "ci95_high",
                    "n_improved", "n_degraded", "n_unchanged", "biggest_gain_author", "biggest_gain_delta",
                    "biggest_degradation_author", "biggest_degradation_delta",
                    "pooled_accuracy_mean", "pooled_macro_f1_mean"])
        w.writerow([0, per_k_table["0"]["deployed_zero_shot_mean"], per_k_table["0"]["deployed_zero_shot_median"],
                    per_k_table["0"]["deployed_zero_shot_std"], per_k_table["0"]["deployed_zero_shot_ci95"][0],
                    per_k_table["0"]["deployed_zero_shot_ci95"][1], "", "", "", "", "", "", "",
                    per_k_table["0"]["pooled_accuracy"], per_k_table["0"]["pooled_macro_f1"]])
        for k in KS_FEWSHOT:
            t = per_k_table[str(k)]
            d = improved_degraded[str(k)]
            w.writerow([k, t["mean_recall"], t["median_recall"], t["std_across_authors"],
                        t["ci95_across_authors"][0], t["ci95_across_authors"][1],
                        d["n_improved"], d["n_degraded"], d["n_unchanged"],
                        d["biggest_gain_author"], d["biggest_gain_delta"],
                        d["biggest_degradation_author"], d["biggest_degradation_delta"],
                        t["pooled_accuracy_mean"], t["pooled_macro_f1_mean"]])
    log("Wrote per_seed_results.csv, per_author_results.csv, aggregated_table.csv")

    # --- Figures ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x_pos = list(range(len(ALL_KS)))
    x_labels = [str(k) for k in ALL_KS]
    means = [per_k_table["0"]["deployed_zero_shot_mean"]] + [per_k_table[str(k)]["mean_recall"] for k in KS_FEWSHOT]
    ci_lo = [per_k_table["0"]["deployed_zero_shot_ci95"][0]] + [per_k_table[str(k)]["ci95_across_authors"][0] for k in KS_FEWSHOT]
    ci_hi = [per_k_table["0"]["deployed_zero_shot_ci95"][1]] + [per_k_table[str(k)]["ci95_across_authors"][1] for k in KS_FEWSHOT]
    err_lo = [m - lo for m, lo in zip(means, ci_lo)]
    err_hi = [hi - m for m, hi in zip(means, ci_hi)]

    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    ax.errorbar(x_pos, means, yerr=[err_lo, err_hi], marker="o", capsize=5, color="#1f77b4",
                linewidth=2, label="Mean fresh-author recall (95% bootstrap CI across authors)")
    ax.scatter([x_pos[0]], [means[0]], color="#d62728", zorder=5, s=90,
               label="Zero-shot (k=0, Section 25 trained classifier)")
    for xi, yi in zip(x_pos, means):
        ax.annotate(f"{yi:.3f}", (xi, yi), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Number of labeled examples from unseen author (k)")
    ax.set_ylabel("Mean fresh-author recall")
    ax.set_title("Few-shot adaptation learning curve (14 frozen fresh authors, 5 sampling seeds per k)")
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "learning_curve.png"), dpi=150)
    plt.close(fig)
    log("Wrote learning_curve.png")

    fig2, ax2 = plt.subplots(figsize=(8.0, 5.5))
    cmap = plt.get_cmap("tab20")
    for i, a in enumerate(author_order):
        ys = [deployed_zero_shot[a]] + [
            per_author_summary[a]["by_k"][str(k)]["mean"] if per_author_summary[a]["by_k"][str(k)]["feasible"] else np.nan
            for k in KS_FEWSHOT
        ]
        ax2.plot(x_pos, ys, marker="o", markersize=3, linewidth=1, alpha=0.7, color=cmap(i % 20),
                 label=f"{a} ({narrative_of_author[a]})")
    ax2.plot(x_pos, means, marker="o", linewidth=3, color="black", label="Mean (all authors)")
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(x_labels)
    ax2.set_xlabel("Number of labeled examples from unseen author (k)")
    ax2.set_ylabel("Recall")
    ax2.set_title("Per-author learning-curve trajectories (14 frozen fresh authors)")
    ax2.set_ylim(0, 1.05)
    ax2.grid(axis="y", alpha=0.3)
    ax2.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=6, ncol=1)
    fig2.tight_layout()
    fig2.savefig(os.path.join(OUT_DIR, "learning_curve_per_author.png"), dpi=150)
    plt.close(fig2)
    log("Wrote learning_curve_per_author.png")

    with open(os.path.join(OUT_DIR, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    log("=" * 70)
    log(f"Zero-shot (k=0, deployed): mean={base_mean:.4f}")
    for k in KS_FEWSHOT:
        t = per_k_table[str(k)]
        log(f"k={k}: mean={t['mean_recall']:.4f} median={t['median_recall']:.4f} "
            f"std_across_authors={t['std_across_authors']:.4f} "
            f"mean_std_across_seeds={t['mean_std_across_seeds_per_author']:.4f} "
            f"n_improved={improved_degraded[str(k)]['n_improved']} "
            f"n_degraded={improved_degraded[str(k)]['n_degraded']}")
    log(f"Interpretation: efficiency={efficiency_mode} stability={stability_mode} "
        f"replication={replication_mode}")
    log("=" * 70)


if __name__ == "__main__":
    main()

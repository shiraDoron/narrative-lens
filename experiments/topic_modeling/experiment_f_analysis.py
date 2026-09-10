"""Experiment F, phase 2: score/select the best `min_topic_size` per corpus size from the sweep
results produced by `experiment_f_corpus_scaling.py`, then fit candidate scaling laws to the
resulting (corpus_size, best_min_topic_size) points.

Reads reports/results/profiler_prototype/expF_corpus_scaling_results.json (44 configs: 4 corpus sizes x
its own min_topic_size grid x 2 UMAP seeds). Writes
reports/results/profiler_prototype/expF_selection_and_scaling_law.json with the full per-candidate
scoring breakdown, the winning min_topic_size per corpus size, and the scaling-law comparison.

SCORING RULE (documented here and in EXPERIMENTS.md - decided BEFORE looking at which law "wins",
to avoid post-hoc metric shopping):
Per (corpus_size, min_topic_size) candidate, seed-averaged metrics are combined into one composite
score in [0, 1], each metric min-max normalized WITHIN that corpus size's own candidate set (so
different corpus sizes, which have structurally different topic counts/coherence baselines, are
each judged relative to their own peers, not against each other):
    +0.20 * u_mass coherence (higher better)
    +0.10 * topic diversity (higher better)
    +0.15 * (1 - outlier_pct)               (lower outliers better)
    +0.15 * (1 - micro_topic_floor_rel_frac) (fewer fragile "at their own floor" topics better)
    +0.10 * (1 - top2_combined_pct)          (less mega-topic dominance better)
    +0.10 * agreement_rate_with_signal_pct   (hard/soft agreement, higher better)
    +0.10 * soft_signal_coverage_pct         (higher better)
    +0.10 * (1 - seed_instability)           (lower cross-seed variance better)
Weights sum to 1.00.

HARD VETOES (candidate excluded from selection entirely, regardless of score):
  - top2_combined_pct (mega-topic risk) > MEGA_TOPIC_VETO_PCT (12.0) for either seed
  - n_topics < MIN_VIABLE_TOPICS (3) for either seed (degenerate collapse)
Vetoed candidates are still shown in the report (flagged), just never selected as "best".
"""
import json
import os

import numpy as np

REPORT_DIR = "reports/results/profiler_prototype"
RESULTS_JSON = os.path.join(REPORT_DIR, "expF_corpus_scaling_results.json")
SELECTION_JSON = os.path.join(REPORT_DIR, "expF_selection_and_scaling_law.json")

MEGA_TOPIC_VETO_PCT = 12.0
MIN_VIABLE_TOPICS = 3

WEIGHTS = {
    "coherence": 0.20,
    "diversity": 0.10,
    "outlier_pct": 0.15,       # inverted
    "micro_topic_frac": 0.15,  # inverted
    "top2_combined_pct": 0.10, # inverted
    "agreement_rate": 0.10,
    "soft_signal_pct": 0.10,
    "instability": 0.10,       # inverted
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

SIZE_LABELS = {"4000": "4K", "8000": "8K", "12000": "12K", "full": "16K (full)"}
SIZE_NUMERIC = {"4000": 4000, "8000": 8000, "12000": 12000, "full": 16062}


def load_and_group(results):
    """Groups the 44 raw per-(sizekey,mts,seed) results into per-(sizekey,mts) candidates with
    seed-averaged metrics + cross-seed instability + veto flags."""
    grouped = {}
    for key, r in results.items():
        sizekey = r["sizekey"]
        mts = r["min_topic_size"]
        grouped.setdefault((sizekey, mts), []).append(r)

    candidates = []
    for (sizekey, mts), runs in grouped.items():
        n_topics_list = [r["cluster_stats"]["n_topics"] for r in runs]
        outlier_pct_list = [r["cluster_stats"]["outlier_pct"] for r in runs]
        top2_list = [r["largest_topics_stats"]["top2_combined_pct"] for r in runs]
        micro_frac_list = [r["cluster_stats"]["micro_topic_floor_rel_frac"] for r in runs]
        coherence_list = [r["u_mass_coherence"] for r in runs]
        diversity_list = [r["topic_diversity"] for r in runs]
        agree_list = [r["agreement_rate_with_signal_pct"] for r in runs
                      if r["agreement_rate_with_signal_pct"] is not None]
        soft_signal_list = [r["soft_signal_coverage_pct"] for r in runs]

        veto_reasons = []
        if any(t < MIN_VIABLE_TOPICS for t in n_topics_list):
            veto_reasons.append(f"degenerate topic count (<{MIN_VIABLE_TOPICS}) in >=1 seed")
        if any(t > MEGA_TOPIC_VETO_PCT for t in top2_list):
            veto_reasons.append(f"mega-topic: top2_combined_pct > {MEGA_TOPIC_VETO_PCT} in >=1 seed")

        # cross-seed instability: normalized spread (range / (mean+eps)) averaged over the 3
        # tracked quantities - a simple, explicit, documented stability signal (only 2 seeds, so
        # "range" and "std" carry the same information; range is simpler to reason about).
        def rel_range(vals):
            vals = [v for v in vals if v is not None]
            if len(vals) < 2 or np.mean(vals) == 0:
                return 0.0
            return (max(vals) - min(vals)) / abs(np.mean(vals))

        instability = np.mean([
            rel_range(n_topics_list), rel_range(outlier_pct_list), rel_range(top2_list),
        ])

        candidates.append({
            "sizekey": sizekey,
            "min_topic_size": mts,
            "n_seeds": len(runs),
            "n_topics_mean": round(float(np.mean(n_topics_list)), 1),
            "n_topics_per_seed": n_topics_list,
            "outlier_pct_mean": round(float(np.mean(outlier_pct_list)), 2),
            "topic_size_mean": round(float(np.mean([r["cluster_stats"]["topic_size_mean"] for r in runs])), 1),
            "topic_size_median_mean": round(float(np.mean([r["cluster_stats"]["topic_size_median"] for r in runs])), 1),
            "micro_topic_frac_mean": round(float(np.mean(micro_frac_list)), 3),
            "top2_combined_pct_mean": round(float(np.mean(top2_list)), 2),
            "top2_combined_pct_per_seed": top2_list,
            "coherence_mean": round(float(np.mean(coherence_list)), 3),
            "diversity_mean": round(float(np.mean(diversity_list)), 3),
            "agreement_rate_mean": round(float(np.mean(agree_list)), 1) if agree_list else None,
            "soft_signal_pct_mean": round(float(np.mean(soft_signal_list)), 1),
            "instability": round(float(instability), 3),
            "vetoed": len(veto_reasons) > 0,
            "veto_reasons": veto_reasons,
        })
    return candidates


def minmax_norm(values):
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [0.5 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def score_candidates(candidates):
    """Adds a `score` field to each candidate (min-max normalized WITHIN its own corpus-size
    group), and marks the best non-vetoed candidate per corpus size as `is_selected`."""
    by_size = {}
    for c in candidates:
        by_size.setdefault(c["sizekey"], []).append(c)

    for sizekey, group in by_size.items():
        coherence_n = minmax_norm([c["coherence_mean"] for c in group])
        diversity_n = minmax_norm([c["diversity_mean"] for c in group])
        outlier_n = minmax_norm([c["outlier_pct_mean"] for c in group])
        micro_n = minmax_norm([c["micro_topic_frac_mean"] for c in group])
        top2_n = minmax_norm([c["top2_combined_pct_mean"] for c in group])
        agree_vals = [c["agreement_rate_mean"] if c["agreement_rate_mean"] is not None else 0.0 for c in group]
        agree_n = minmax_norm(agree_vals)
        soft_n = minmax_norm([c["soft_signal_pct_mean"] for c in group])
        instab_n = minmax_norm([c["instability"] for c in group])

        for i, c in enumerate(group):
            score = (
                WEIGHTS["coherence"] * coherence_n[i]
                + WEIGHTS["diversity"] * diversity_n[i]
                + WEIGHTS["outlier_pct"] * (1 - outlier_n[i])
                + WEIGHTS["micro_topic_frac"] * (1 - micro_n[i])
                + WEIGHTS["top2_combined_pct"] * (1 - top2_n[i])
                + WEIGHTS["agreement_rate"] * agree_n[i]
                + WEIGHTS["soft_signal_pct"] * soft_n[i]
                + WEIGHTS["instability"] * (1 - instab_n[i])
            )
            c["score"] = round(float(score), 4)

        viable = [c for c in group if not c["vetoed"]]
        if viable:
            best = max(viable, key=lambda c: c["score"])
            best["is_selected"] = True
            for c in group:
                if c is not best:
                    c["is_selected"] = False
        else:
            for c in group:
                c["is_selected"] = False

    return candidates


def fit_scaling_laws(points):
    """points: list of (corpus_size, best_mts). Fits several simple candidate scaling laws and
    reports R^2 for each, to empirically decide which functional form best explains the data -
    does NOT assume any form (including the current sqrt heuristic) is correct in advance."""
    sizes = np.array([p[0] for p in points], dtype=float)
    mts = np.array([p[1] for p in points], dtype=float)

    def r_squared(y, y_pred):
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    laws = {}

    # constant: mts = c (c = mean)
    c = float(np.mean(mts))
    laws["constant"] = {"formula": f"mts = {c:.2f}", "r_squared": r_squared(mts, np.full_like(mts, c))}

    # linear/proportional through origin: mts = a * size
    a_lin = float(np.sum(sizes * mts) / np.sum(sizes ** 2))
    pred_lin = a_lin * sizes
    laws["linear_proportional"] = {
        "formula": f"mts = {a_lin:.6f} * corpus_size",
        "r_squared": r_squared(mts, pred_lin),
    }

    # sqrt: mts = a * sqrt(size)
    sqrt_sizes = np.sqrt(sizes)
    a_sqrt = float(np.sum(sqrt_sizes * mts) / np.sum(sqrt_sizes ** 2))
    pred_sqrt = a_sqrt * sqrt_sizes
    laws["sqrt"] = {"formula": f"mts = {a_sqrt:.4f} * sqrt(corpus_size)", "r_squared": r_squared(mts, pred_sqrt)}

    # log: mts = a * log(size) + b  (OLS)
    log_sizes = np.log(sizes)
    A = np.vstack([log_sizes, np.ones_like(log_sizes)]).T
    (a_log, b_log), _, _, _ = np.linalg.lstsq(A, mts, rcond=None)
    pred_log = a_log * log_sizes + b_log
    laws["log"] = {
        "formula": f"mts = {a_log:.3f} * ln(corpus_size) + {b_log:.3f}",
        "r_squared": r_squared(mts, pred_log),
    }

    # general power law: mts = a * size^b  (fit via log-log OLS)
    log_mts = np.log(mts)
    A2 = np.vstack([log_sizes, np.ones_like(log_sizes)]).T
    (b_pow, log_a), _, _, _ = np.linalg.lstsq(A2, log_mts, rcond=None)
    a_pow = float(np.exp(log_a))
    pred_pow = a_pow * sizes ** b_pow
    laws["power"] = {
        "formula": f"mts = {a_pow:.4f} * corpus_size^{b_pow:.4f}",
        "r_squared": r_squared(mts, pred_pow),
        "exponent_b": round(float(b_pow), 4),
    }

    best_law_name = max(laws.keys(), key=lambda k: laws[k]["r_squared"])
    return laws, best_law_name


def main():
    with open(RESULTS_JSON, "r", encoding="utf-8") as f:
        results = json.load(f)

    candidates = load_and_group(results)
    candidates = score_candidates(candidates)

    print(f"\n{'=' * 100}")
    print(f"{'size':<10}{'mts':>5}{'n_top':>8}{'outl%':>8}{'top2%':>8}{'coh':>9}{'div':>7}"
          f"{'agree%':>8}{'soft%':>7}{'instab':>8}{'score':>8}  flags")
    print("=" * 100)
    for sizekey in ["4000", "8000", "12000", "full"]:
        group = sorted([c for c in candidates if c["sizekey"] == sizekey], key=lambda c: c["min_topic_size"])
        for c in group:
            flags = []
            if c["vetoed"]:
                flags.append("VETOED:" + ";".join(c["veto_reasons"]))
            if c.get("is_selected"):
                flags.append("<-- SELECTED")
            print(f"{SIZE_LABELS[sizekey]:<10}{c['min_topic_size']:>5}{c['n_topics_mean']:>8.1f}"
                  f"{c['outlier_pct_mean']:>8.1f}{c['top2_combined_pct_mean']:>8.1f}"
                  f"{c['coherence_mean']:>9.3f}{c['diversity_mean']:>7.3f}"
                  f"{(c['agreement_rate_mean'] if c['agreement_rate_mean'] is not None else float('nan')):>8.1f}"
                  f"{c['soft_signal_pct_mean']:>7.1f}{c['instability']:>8.3f}{c['score']:>8.3f}  "
                  f"{' '.join(flags)}")
        print("-" * 100)

    best_per_size = {}
    for sizekey in ["4000", "8000", "12000", "full"]:
        group = [c for c in candidates if c["sizekey"] == sizekey]
        selected = [c for c in group if c.get("is_selected")]
        if selected:
            best_per_size[sizekey] = selected[0]

    print("\nFINAL TABLE: corpus_size | best_min_topic_size | ratio_to_corpus | main_metrics")
    print(f"{'corpus_size':<14}{'best_mts':>10}{'ratio':>10}{'n_topics':>10}{'outlier%':>10}"
          f"{'coherence':>11}{'diversity':>11}")
    points = []
    for sizekey, c in best_per_size.items():
        n = SIZE_NUMERIC[sizekey]
        ratio = c["min_topic_size"] / n
        points.append((n, c["min_topic_size"]))
        print(f"{SIZE_LABELS[sizekey]:<14}{c['min_topic_size']:>10}{ratio:>10.5f}"
              f"{c['n_topics_mean']:>10.1f}{c['outlier_pct_mean']:>10.1f}"
              f"{c['coherence_mean']:>11.3f}{c['diversity_mean']:>11.3f}")

    points.sort(key=lambda p: p[0])
    print(f"\nData points for scaling-law fit: {points}")
    laws, best_law_name = fit_scaling_laws(points)
    print(f"\n{'law':<22}{'R^2':>10}  formula")
    for name, law in sorted(laws.items(), key=lambda kv: -kv[1]["r_squared"]):
        marker = " <-- BEST FIT" if name == best_law_name else ""
        print(f"{name:<22}{law['r_squared']:>10.4f}  {law['formula']}{marker}")

    output = {
        "candidates": candidates,
        "best_per_size": {k: v["min_topic_size"] for k, v in best_per_size.items()},
        "final_table_points_corpus_size_best_mts": points,
        "scaling_laws": laws,
        "best_law": best_law_name,
        "scoring_weights": WEIGHTS,
        "mega_topic_veto_pct": MEGA_TOPIC_VETO_PCT,
        "min_viable_topics": MIN_VIABLE_TOPICS,
    }
    with open(SELECTION_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nSaved full selection + scaling-law report to {SELECTION_JSON}")


if __name__ == "__main__":
    main()

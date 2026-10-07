"""
Quality analysis of the soft (multi-topic) BERTopic scoring produced by
`models/saved_topic_model_soft_v2` (see stance.py's `get_topic_distribution` /
`process_text_with_distribution`, and the smaller demo `analyze_soft_topics.py`).

READ-ONLY analysis tool. Does NOT modify any saved model, does NOT touch fusion.py /
train.py / any checkpoint. Only loads `config.TOPIC_MODEL_PATH_SOFT` and inspects its
output on a sample of real texts.

What this computes, over a stratified sample of texts (n_per_narrative per narrative,
across all 4 natural datasets):
  1. Per-text: hard topic_id (.transform(), same as fusion.py/train.py use), top-3 soft
     topics with normalized scores + labels (approximate_distribution(), same as
     stance.py's get_topic_distribution), and whether the hard topic agrees with the
     soft top-1 topic.
  2. Dominance classification per text: "dominant_single_topic" (top-1 soft topic holds
     >= DOMINANCE_THRESHOLD of the total assigned soft mass) vs "spread_multi_topic"
     (more evenly spread) vs "no_soft_signal" (approximate_distribution found nothing,
     e.g. very short/out-of-vocabulary text).
  3. Distribution (mean/median/std/quartiles) of the raw (non-renormalized) top-1/top-2/
     top-3 soft scores across the whole sample.
  4. Topic co-occurrence: which topic-id pairs appear together most often in the same
     text's top-3 soft topics.
  5. A curated set of illustrative example rows (clean agreement, hard=-1 "noise" texts
     where soft still finds signal, hard/soft disagreements, most spread-out texts) for
     manual eyeballing of quality.

Outputs (all under artifacts/experiments/profiler_prototype/):
  - soft_topic_quality_full.csv        - one row per sampled text, all computed fields
  - soft_topic_quality_summary.json    - the aggregate statistics from point 2/3 above
  - soft_topic_cooccurrence.csv        - top topic-pairs from point 4
  - soft_topic_quality_examples.csv    - curated rows from point 5, with a `case_type` column

Run (from repo root): `python -m narrative_lens.evaluation.analyze_soft_topic_quality --n-per-narrative 40`
"""
import argparse
import itertools
import json
import os
from collections import Counter

import numpy as np
import pandas as pd

from narrative_lens.config import TOPIC_MODEL_PATH_SOFT
from narrative_lens.topic_modeling.stance import TopicAnalysisPipeline

RAW_DATASETS = [
    "data/raw/twitter_natural_dataset.csv",
    "data/raw/telegram_natural_dataset.csv",
    "data/raw/gemini_natural_dataset.csv",
    "data/raw/gpt_natural_dataset.csv",
]

REPORT_DIR = "artifacts/experiments/profiler_prototype"

# A text is classified "dominant_single_topic" if its single strongest soft topic holds
# at least this fraction of the TOTAL soft mass assigned across all topics for that text
# (not just relative to the other top-3) - a simple, explicit, documented heuristic.
DOMINANCE_THRESHOLD = 0.5


def load_stratified_sample(n_per_narrative=40, seed=42):
    """Loads all 4 natural datasets and samples up to n_per_narrative texts PER
    narrative_name (stratified, so every narrative is represented in the stats/
    co-occurrence analysis, not just whichever dataset happens to be biggest)."""
    frames = []
    for path in RAW_DATASETS:
        if os.path.exists(path):
            df = pd.read_csv(path)
            frames.append(df[["text", "narrative_name"]])
        else:
            print(f"WARNING: dataset not found, skipping: {path}")

    full = pd.concat(frames, ignore_index=True).dropna(subset=["text", "narrative_name"])
    full = full.drop_duplicates(subset=["text"])

    sampled = (
        full.groupby("narrative_name", group_keys=False)
        .apply(lambda g: g.sample(n=min(n_per_narrative, len(g)), random_state=seed))
        .reset_index(drop=True)
    )
    return sampled


def run_batch_analysis(pipeline, df, top_n=3):
    """Runs hard .transform() + soft approximate_distribution() ONCE each, batched over
    all texts (much faster than the single-text loop in analyze_soft_topics.py's demo),
    then builds one result row per text."""
    texts = df["text"].tolist()

    print(f"Running .transform() (hard topic_id) on {len(texts)} texts...")
    hard_topics, _ = pipeline.topic_model.transform(texts)

    print(f"Running approximate_distribution() (soft scores) on {len(texts)} texts...")
    topic_distr, _ = pipeline.topic_model.approximate_distribution(texts)

    rows = []
    for i, text in enumerate(texts):
        narrative = df.iloc[i]["narrative_name"]
        hard_id = int(hard_topics[i])
        scores = topic_distr[i]
        row_sum = float(scores.sum())

        nonzero_idx = [j for j, s in enumerate(scores) if s > 0]
        nonzero_idx.sort(key=lambda j: scores[j], reverse=True)
        top_idx = nonzero_idx[:top_n]

        if not top_idx or row_sum <= 0:
            rows.append({
                "narrative_name": narrative,
                "text": text,
                "hard_topic_id": hard_id,
                "hard_topic_label": pipeline.get_topic_label(hard_id),
                "soft_top1_id": None, "soft_top1_label": None, "soft_top1_score_norm": None,
                "soft_top2_id": None, "soft_top2_label": None, "soft_top2_score_norm": None,
                "soft_top3_id": None, "soft_top3_label": None, "soft_top3_score_norm": None,
                "raw_top1_score": 0.0, "raw_top2_score": 0.0, "raw_top3_score": 0.0,
                "row_sum": row_sum,
                "dominance_ratio": None,
                "case": "no_soft_signal",
                "hard_soft_agree": None,
            })
            continue

        norm_total = sum(scores[j] for j in top_idx)
        top_entries = [
            {"topic_id": int(j), "label": pipeline.get_topic_label(int(j)),
             "raw_score": float(scores[j]),
             "norm_score": float(scores[j] / norm_total) if norm_total > 0 else 0.0}
            for j in top_idx
        ]
        # pad to length top_n with Nones so all rows have the same columns
        while len(top_entries) < top_n:
            top_entries.append({"topic_id": None, "label": None, "raw_score": 0.0, "norm_score": None})

        dominance_ratio = top_entries[0]["raw_score"] / row_sum if row_sum > 0 else None
        if dominance_ratio is None:
            case = "no_soft_signal"
        elif dominance_ratio >= DOMINANCE_THRESHOLD:
            case = "dominant_single_topic"
        else:
            case = "spread_multi_topic"

        if hard_id == -1:
            agree = "hard_is_outlier"
        else:
            agree = bool(hard_id == top_entries[0]["topic_id"])

        row = {
            "narrative_name": narrative,
            "text": text,
            "hard_topic_id": hard_id,
            "hard_topic_label": pipeline.get_topic_label(hard_id),
            "soft_top1_id": top_entries[0]["topic_id"], "soft_top1_label": top_entries[0]["label"],
            "soft_top1_score_norm": top_entries[0]["norm_score"],
            "soft_top2_id": top_entries[1]["topic_id"], "soft_top2_label": top_entries[1]["label"],
            "soft_top2_score_norm": top_entries[1]["norm_score"],
            "soft_top3_id": top_entries[2]["topic_id"], "soft_top3_label": top_entries[2]["label"],
            "soft_top3_score_norm": top_entries[2]["norm_score"],
            "raw_top1_score": top_entries[0]["raw_score"],
            "raw_top2_score": top_entries[1]["raw_score"],
            "raw_top3_score": top_entries[2]["raw_score"],
            "row_sum": row_sum,
            "dominance_ratio": dominance_ratio,
            "case": case,
            "hard_soft_agree": agree,
        }
        rows.append(row)

    return pd.DataFrame(rows)


def compute_summary_stats(result_df):
    n_total = len(result_df)
    case_counts = result_df["case"].value_counts().to_dict()

    agree_counts = result_df["hard_soft_agree"].value_counts(dropna=False).to_dict()
    agree_counts = {str(k): int(v) for k, v in agree_counts.items()}

    def describe(col):
        s = result_df[col].dropna()
        if len(s) == 0:
            return {}
        return {
            "mean": float(s.mean()), "median": float(s.median()), "std": float(s.std()),
            "min": float(s.min()), "max": float(s.max()),
            "p25": float(s.quantile(0.25)), "p75": float(s.quantile(0.75)),
        }

    summary = {
        "n_texts_analyzed": n_total,
        "dominance_threshold_used": DOMINANCE_THRESHOLD,
        "case_counts": {str(k): int(v) for k, v in case_counts.items()},
        "case_pct": {str(k): round(100 * v / n_total, 1) for k, v in case_counts.items()},
        "hard_soft_agreement_counts": agree_counts,
        "hard_is_outlier_pct": round(100 * agree_counts.get("hard_is_outlier", 0) / n_total, 1),
        "raw_top1_score_stats": describe("raw_top1_score"),
        "raw_top2_score_stats": describe("raw_top2_score"),
        "raw_top3_score_stats": describe("raw_top3_score"),
        "dominance_ratio_stats": describe("dominance_ratio"),
        # among texts where hard topic_id == -1 (BERTopic outlier/noise), how many still
        # got a real soft signal - i.e. cases where soft clustering "rescues" information
        # that the hard assignment discarded.
        "outlier_rescue": None,
    }

    outliers = result_df[result_df["hard_topic_id"] == -1]
    if len(outliers) > 0:
        rescued = outliers[outliers["case"] != "no_soft_signal"]
        summary["outlier_rescue"] = {
            "n_hard_outliers": int(len(outliers)),
            "n_rescued_by_soft": int(len(rescued)),
            "pct_rescued": round(100 * len(rescued) / len(outliers), 1),
        }

    return summary


def compute_cooccurrence(result_df, top_k=20):
    """Counts how often each unordered pair of topic ids appears together in the same
    text's top-3 soft topics, across the whole sample."""
    pair_counter = Counter()
    label_lookup = {}
    for _, row in result_df.iterrows():
        ids = [row[c] for c in ("soft_top1_id", "soft_top2_id", "soft_top3_id") if pd.notna(row[c])]
        labels = [row[c] for c in ("soft_top1_label", "soft_top2_label", "soft_top3_label") if pd.notna(row[c])]
        for tid, lbl in zip(ids, labels):
            label_lookup[int(tid)] = lbl
        for a, b in itertools.combinations(sorted(int(x) for x in ids), 2):
            pair_counter[(a, b)] += 1

    rows = [
        {"topic_a": a, "topic_a_label": label_lookup.get(a, ""),
         "topic_b": b, "topic_b_label": label_lookup.get(b, ""),
         "co_occurrence_count": count}
        for (a, b), count in pair_counter.most_common(top_k)
    ]
    return pd.DataFrame(rows)


def select_examples(result_df, n_per_case=5, seed=42):
    """Curates a handful of rows per interesting case, for manual quality eyeballing."""
    examples = []

    clean = result_df[(result_df["case"] == "dominant_single_topic") & (result_df["hard_soft_agree"] == True)]
    clean = clean.sort_values("dominance_ratio", ascending=False).head(n_per_case).copy()
    clean["example_type"] = "clean_agreement_dominant"
    examples.append(clean)

    rescued = result_df[(result_df["hard_topic_id"] == -1) & (result_df["case"] != "no_soft_signal")]
    rescued = rescued.sort_values("raw_top1_score", ascending=False).head(n_per_case).copy()
    rescued["example_type"] = "hard_outlier_soft_rescued"
    examples.append(rescued)

    disagree = result_df[(result_df["hard_topic_id"] != -1) & (result_df["hard_soft_agree"] == False)]
    disagree = disagree.sample(n=min(n_per_case, len(disagree)), random_state=seed).copy()
    disagree["example_type"] = "hard_soft_disagreement"
    examples.append(disagree)

    spread = result_df[result_df["case"] == "spread_multi_topic"]
    spread = spread.sort_values("dominance_ratio", ascending=True).head(n_per_case).copy()
    spread["example_type"] = "most_spread_out"
    examples.append(spread)

    no_signal = result_df[result_df["case"] == "no_soft_signal"]
    no_signal = no_signal.sample(n=min(n_per_case, len(no_signal)), random_state=seed).copy()
    no_signal["example_type"] = "no_soft_signal"
    examples.append(no_signal)

    return pd.concat(examples, ignore_index=True) if examples else pd.DataFrame()


def analyze(n_per_narrative=40, top_n=3, model_path=TOPIC_MODEL_PATH_SOFT):
    os.makedirs(REPORT_DIR, exist_ok=True)

    sample_df = load_stratified_sample(n_per_narrative=n_per_narrative)
    print(f"Loaded stratified sample: {len(sample_df)} texts across "
          f"{sample_df['narrative_name'].nunique()} narratives.")

    pipeline = TopicAnalysisPipeline(model_path=model_path)

    result_df = run_batch_analysis(pipeline, sample_df, top_n=top_n)
    full_csv = os.path.join(REPORT_DIR, "soft_topic_quality_full.csv")
    result_df.to_csv(full_csv, index=False, encoding="utf-8-sig")
    print(f"Saved full per-text results ({len(result_df)} rows) to {full_csv}")

    summary = compute_summary_stats(result_df)
    summary_json = os.path.join(REPORT_DIR, "soft_topic_quality_summary.json")
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Saved summary stats to {summary_json}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    cooc_df = compute_cooccurrence(result_df, top_k=30)
    cooc_csv = os.path.join(REPORT_DIR, "soft_topic_cooccurrence.csv")
    cooc_df.to_csv(cooc_csv, index=False, encoding="utf-8-sig")
    print(f"Saved top {len(cooc_df)} co-occurring topic pairs to {cooc_csv}")

    examples_df = select_examples(result_df)
    examples_csv = os.path.join(REPORT_DIR, "soft_topic_quality_examples.csv")
    examples_df.to_csv(examples_csv, index=False, encoding="utf-8-sig")
    print(f"Saved {len(examples_df)} curated example rows to {examples_csv}")

    return result_df, summary, cooc_df, examples_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-per-narrative", type=int, default=40,
                        help="Max texts sampled per narrative (default 40, stratified).")
    parser.add_argument("--top-n", type=int, default=3,
                        help="Number of top soft topics to keep per text (default 3).")
    parser.add_argument("--model-path", type=str, default=TOPIC_MODEL_PATH_SOFT,
                        help=f"Path to a saved BERTopic model (default: {TOPIC_MODEL_PATH_SOFT}).")
    args = parser.parse_args()

    analyze(n_per_narrative=args.n_per_narrative, top_n=args.top_n, model_path=args.model_path)

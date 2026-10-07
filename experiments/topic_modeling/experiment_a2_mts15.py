"""Experiment A2: one additional min_topic_size sweep point (15), requested after Experiment A
found that min_topic_size=25 and =35 were too aggressive (severe over-merging of large topics -
at mts=35 the top-2 topics alone absorbed ~43% of all clustered documents).

Compares ONLY min_topic_size=10 (the existing seeded baseline from Experiment A, reused as-is -
NOT refit) against min_topic_size=15 (new, freshly fit with the same UMAP random_state=42), on
exactly the 8 dimensions requested:
  1. number of topics
  2. outlier %
  3. hard/soft agreement
  4. % of texts with any soft signal (not no_soft_signal)
  5. average/median topic size
  6. number of small topics
  7. size of the largest topics (incl. the top-2-combined "mega-topic" % metric from Experiment A)
  8. whether the 'rulesbased' duplicate-topic problem is still present
plus whether previously-good control topics (gaza/ukraine/iran/telephone/home/maria) stay
distinct rather than being absorbed into giant catch-all topics.

Uses a substring match (not exact top-K-word equality) over the top-10 c-TF-IDF words to find
control topics - Experiment A's exact-match search was found to under-report matches for
bigram/MMR-diversified phrases (e.g. "ukraine glory" != exact "ukraine").

Reuses Experiment A's helpers (compute_cluster_stats, apply_experiment_c_representation,
run_analysis_with_retry, CONTROL_THEMES, WATCH_WORDS) rather than duplicating them.

Does NOT touch fusion.py, train.py, any .pth checkpoint, models/saved_topic_model,
models/saved_topic_model_soft_v2, or any existing experiment folder (soft_v2_baseline_seeded,
soft_v2_expA_mts25, soft_v2_expA_mts35, soft_v2_expC_representation) - the new mts=15 model is
saved to its own separate path, models/experiments/soft_v2_expA_mts15.

Run (from repo root): python experiments/topic_modeling/experiment_a2_mts15.py
"""
import json
import os
import shutil

from bertopic import BERTopic

from experiment_a_min_topic_size import (
    CONTROL_THEMES,
    N_SMALLEST_SHOWN,
    WATCH_WORDS,
    apply_experiment_c_representation,
    compute_cluster_stats,
    run_analysis_with_retry,
)
from experiment_c_representation import _topic_snapshot
from narrative_lens.topic_modeling.topic_preprocessing import build_multiword_label
from narrative_lens.train_topics import build_bertopic_model, load_deduplicated_training_texts

REPORT_DIR = "artifacts/experiments/profiler_prototype"

# (display name, min_topic_size, save path) - baseline reused unchanged, mts15 is new
CONFIGS = [
    ("baseline_mts10", 10, "models/experiments/soft_v2_baseline_seeded"),
    ("expA2_mts15", 15, "models/experiments/soft_v2_expA_mts15"),
]

# "iran" added on top of Experiment A's original 5 control themes, per explicit user request to
# also check Iran-related topics stay distinct
ALL_CONTROL_THEMES = dict(CONTROL_THEMES, iran_related="iran")

N_LARGEST_SHOWN = 5


def find_control_topic_substring(topic_model, keyword, top_n_search=10):
    """Substring match over the top-N c-TF-IDF words (not exact top-K equality) - avoids
    Experiment A's documented false-negative issue with bigram/MMR-diversified phrases. Returns
    the largest matching topic, or None."""
    info_df = topic_model.get_topic_info()
    matches = []
    for tid in topic_model.get_topics().keys():
        if tid == -1:
            continue
        words = [w.lower() for w in _topic_snapshot(topic_model, tid, top_n=top_n_search)]
        if any(keyword.lower() in w for w in words):
            matches.append(tid)
    if not matches:
        return None
    sizes = {tid: int(info_df.loc[info_df["Topic"] == tid, "Count"].iloc[0]) for tid in matches}
    best_tid = max(sizes, key=sizes.get)
    return {
        "topic_id": best_tid,
        "count": sizes[best_tid],
        "label": build_multiword_label(topic_model.get_topic(best_tid), top_n_words=3),
        "top_words": _topic_snapshot(topic_model, best_tid, top_n=6),
    }


def compute_largest_topics(topic_model):
    info_df = topic_model.get_topic_info()
    non_outlier = info_df[info_df["Topic"] != -1]
    n_clustered = int(non_outlier["Count"].sum())
    largest = non_outlier.sort_values("Count", ascending=False).head(N_LARGEST_SHOWN)
    largest_topics = [
        {
            "topic_id": int(row.Topic),
            "count": int(row.Count),
            "pct_of_clustered": round(100 * int(row.Count) / n_clustered, 1) if n_clustered else None,
            "label": build_multiword_label(topic_model.get_topic(int(row.Topic)), top_n_words=3),
            "top_words": _topic_snapshot(topic_model, int(row.Topic), top_n=6),
        }
        for row in largest.itertuples()
    ]
    top2_combined_count = int(non_outlier.sort_values("Count", ascending=False).head(2)["Count"].sum())
    top2_combined_pct = round(100 * top2_combined_count / n_clustered, 1) if n_clustered else None
    return {
        "largest_topics": largest_topics,
        "top2_combined_count": top2_combined_count,
        "top2_combined_pct_of_clustered": top2_combined_pct,
    }


def pct_with_soft_signal(summary):
    """% of analyzed texts with ANY soft signal (dominant_single_topic + spread_multi_topic),
    i.e. 100 - no_soft_signal% - the 'soft signal coverage' metric requested explicitly."""
    return round(100 - summary.get("case_pct", {}).get("no_soft_signal", 0), 1)


def analyze_one(name, min_topic_size, save_path, texts_list):
    already_saved = os.path.exists(os.path.join(save_path, "topics.json"))
    if already_saved:
        print(f"\n{'=' * 70}\n'{name}': מודל כבר קיים ב-{save_path} - טוען מודל קיים (לא בונה "
              f"מחדש, לא נדרס).\n{'=' * 70}")
        topic_model = BERTopic.load(save_path)
    else:
        print(f"\n{'=' * 70}\nבונה מודל '{name}' (min_topic_size={min_topic_size}, "
              f"UMAP random_state=42)...\n{'=' * 70}")
        topic_model = build_bertopic_model(min_topic_size=min_topic_size, random_state=42)
        topic_model.fit(texts_list)
        print(f"'{name}': fit הושלם.")

        apply_experiment_c_representation(topic_model, texts_list)
        print(f"'{name}': update_topics() (representation Experiment C) הושלם.")

        os.makedirs(save_path, exist_ok=True)
        topic_model.save(save_path, serialization="safetensors", save_ctfidf=True)
        print(f"'{name}': נשמר בנפרד ל-{save_path} (לא נדרס אף מודל קיים)")

    cluster_stats = compute_cluster_stats(topic_model, min_topic_size)
    largest_stats = compute_largest_topics(topic_model)

    # explicit rulesbased-merge check: which topic id(s) have 'rulesbased'/'call'/'hard'/'era' as
    # a substring of any of their top-10 words/phrases? (wider substring match than Experiment A's
    # original exact top-3-word equality, so a bigram phrase like "rulesbased case" still counts)
    watch_word_hits = {
        word: [
            tid for tid in topic_model.get_topics().keys()
            if tid != -1
            and any(word.lower() in w.lower() for w in _topic_snapshot(topic_model, tid, top_n=10))
        ]
        for word in WATCH_WORDS
    }

    info_df = topic_model.get_topic_info()
    non_outlier = info_df[info_df["Topic"] != -1]
    smallest_ids = (
        non_outlier.sort_values("Count", ascending=True).head(N_SMALLEST_SHOWN)["Topic"].tolist()
    )
    smallest_topics = [
        {
            "topic_id": int(tid),
            "count": int(non_outlier.loc[non_outlier["Topic"] == tid, "Count"].iloc[0]),
            "label": build_multiword_label(topic_model.get_topic(tid), top_n_words=3),
            "top_words": _topic_snapshot(topic_model, tid, top_n=6),
        }
        for tid in smallest_ids
    ]

    control_topics = {
        theme: find_control_topic_substring(topic_model, keyword)
        for theme, keyword in ALL_CONTROL_THEMES.items()
    }

    print(f"'{name}': מריץ ניתוח hard/soft agreement (analyze_soft_topic_quality, n=280, seed=42)...")
    _, summary, _, _ = run_analysis_with_retry(save_path)
    for fname in ("soft_topic_quality_full.csv", "soft_topic_quality_summary.json",
                  "soft_topic_cooccurrence.csv", "soft_topic_quality_examples.csv"):
        src_path = os.path.join(REPORT_DIR, fname)
        if os.path.exists(src_path):
            base, ext = os.path.splitext(fname)
            shutil.copy(src_path, os.path.join(REPORT_DIR, f"{base}.{name}{ext}"))

    return {
        "min_topic_size": min_topic_size,
        "save_path": save_path,
        "cluster_stats": cluster_stats,
        "largest_topics_stats": largest_stats,
        "watch_word_topic_ids": watch_word_hits,
        "smallest_topics": smallest_topics,
        "control_topics": control_topics,
        "soft_quality_summary": summary,
        "pct_texts_with_soft_signal": pct_with_soft_signal(summary),
    }


def run():
    print("טוען את טקסטי האימון (ניקוי + deduplication, כולל תיקון ניקוי bit.ly)...")
    texts_list = load_deduplicated_training_texts(verbose=True)

    all_results = {}
    for name, min_topic_size, save_path in CONFIGS:
        all_results[name] = analyze_one(name, min_topic_size, save_path, texts_list)

    print("\n\n" + "=" * 70)
    print("=== Experiment A2: baseline (mts=10, seeded) מול mts=15 ===")
    print("=" * 70)
    for name, res in all_results.items():
        cs = res["cluster_stats"]
        ls = res["largest_topics_stats"]
        sq = res["soft_quality_summary"]
        print(f"\n--- {name} (min_topic_size={res['min_topic_size']}) ---")
        print(f"  1. מספר Topics (ללא -1): {cs['n_topics']}")
        print(f"  2. אחוז outliers: {cs['outlier_pct']}% ({cs['n_outliers']}/{cs['n_docs_total']})")
        print(f"  3. Hard/Soft agreement counts: {sq['hard_soft_agreement_counts']}")
        print(f"  4. אחוז טקסטים עם soft signal כלשהו: {res['pct_texts_with_soft_signal']}%")
        print(f"  5. גודל Topic ממוצע/חציוני: {cs['topic_size_mean']} / {cs['topic_size_median']}")
        print(f"  6. מספר Topics קטנים (<=15 מסמכים, מוחלט): {cs['n_small_topics_leq15']} | "
              f"צמודים לרצפה שלהם (<=mts+10): {cs['n_topics_at_own_floor']}")
        print(f"  7. Topics הגדולים ביותר (top {N_LARGEST_SHOWN}):")
        for t in ls["largest_topics"]:
            print(f"       Topic {t['topic_id']} (n={t['count']}, {t['pct_of_clustered']}% "
                  f"מהמקובצים): label='{t['label']}'")
        print(f"     2 ה-Topics הגדולים ביותר יחד: {ls['top2_combined_count']} מסמכים = "
              f"{ls['top2_combined_pct_of_clustered']}% מהמקובצים (מדד ה-mega-topic מ-Experiment A)")
        print("  8. מילות-מעקב rulesbased/call/hard/era -> topic ids (בדיקת המיזוג):")
        for word, tids in res["watch_word_topic_ids"].items():
            print(f"       '{word}': {tids}")
        print("  Topics 'שליטה' (gaza/ukraine/iran/telephone/home/maria) - נשארו נפרדים?")
        for theme, ct in res["control_topics"].items():
            if ct is None:
                print(f"       {theme}: לא נמצא topic מתאים (!)")
            else:
                print(f"       {theme}: Topic {ct['topic_id']} (n={ct['count']}), label='{ct['label']}'")

    comparison_json_path = os.path.join(REPORT_DIR, "expA2_mts15_vs_mts10_comparison.json")
    with open(comparison_json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nנשמרה השוואה מובנית מלאה ל-{comparison_json_path}")


if __name__ == "__main__":
    run()

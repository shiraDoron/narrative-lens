"""Experiment B: embedding model swap (all-MiniLM-L6-v2 -> all-mpnet-base-v2), everything else
held fixed, following Experiment A/A2's final decision to keep min_topic_size=10.

Per explicit user request (2026-08-31): keep every other setting constant (min_topic_size=10,
seeded UMAP random_state=42, same preprocessing/dedup pipeline, same Experiment C representation
improvement) and test ONLY whether swapping the sentence-embedding model from
"sentence-transformers/all-MiniLM-L6-v2" (384-dim, BERTopic's default, used by the seeded baseline)
to "sentence-transformers/all-mpnet-base-v2" (768-dim, generally stronger semantic embeddings at
the cost of being ~2-3x slower) improves topic quality.

Compares on the same dimensions used throughout Experiment A/A2, for direct comparability:
  1. number of topics
  2. outlier %
  3. hard/soft agreement
  4. % of texts with any soft signal
  5. average/median topic size
  6. number of small topics
  7. size of the largest topics (incl. the top-2-combined "mega-topic" % metric)
  8. whether the 'rulesbased' duplicate-topic problem is fixed
plus whether previously-good control topics (gaza/ukraine/iran/telephone/home/maria) stay distinct.

Reuses Experiment A/A2's helpers (compute_cluster_stats, compute_largest_topics,
find_control_topic_substring, apply_experiment_c_representation, run_analysis_with_retry,
WATCH_WORDS, ALL_CONTROL_THEMES) rather than duplicating them.

Does NOT touch fusion.py, train.py, any .pth checkpoint, models/saved_topic_model,
models/saved_topic_model_soft_v2, or any existing experiment folder (soft_v2_baseline_seeded,
soft_v2_expA_mts25, soft_v2_expA_mts35, soft_v2_expC_representation) - the new mpnet model is
saved to its own separate path, models/experiments/soft_v2_expB_mpnet.

Run (from repo root): python experiments/topic_modeling/experiment_b_embedding_model.py
"""
import json
import os
import shutil

from bertopic import BERTopic

# Moved out of src/ into experiments/ - add src/ and sibling experiment folders to sys.path so
# same-style flat imports (e.g. `from train_topics import ...`) keep working unmodified.
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _rel_dir in ("src", "experiments/topic_modeling", "experiments/feature_ablation", "experiments/author_generalization"):
    _abs_dir = os.path.join(_REPO_ROOT, _rel_dir)
    if _abs_dir not in sys.path:
        sys.path.insert(0, _abs_dir)

from experiment_a_min_topic_size import (
    N_SMALLEST_SHOWN,
    WATCH_WORDS,
    apply_experiment_c_representation,
    compute_cluster_stats,
    run_analysis_with_retry,
)
from experiment_a2_mts15 import (
    ALL_CONTROL_THEMES,
    N_LARGEST_SHOWN,
    compute_largest_topics,
    find_control_topic_substring,
    pct_with_soft_signal,
)
from experiment_c_representation import _topic_snapshot
from topic_preprocessing import build_multiword_label
from train_topics import build_bertopic_model, load_deduplicated_training_texts

REPORT_DIR = "reports/results/profiler_prototype"

# fixed for both configs, per Experiment A/A2's final decision
MIN_TOPIC_SIZE = 10

# (display name, embedding model, save path) - baseline reused unchanged, mpnet is new
CONFIGS = [
    ("baseline_mts10", "sentence-transformers/all-MiniLM-L6-v2",
     "models/experiments/soft_v2_baseline_seeded"),
    ("expB_mpnet", "sentence-transformers/all-mpnet-base-v2",
     "models/experiments/soft_v2_expB_mpnet"),
]


def analyze_one(name, embedding_model, save_path, texts_list):
    already_saved = os.path.exists(os.path.join(save_path, "topics.json"))
    if already_saved:
        print(f"\n{'=' * 70}\n'{name}': מודל כבר קיים ב-{save_path} - טוען מודל קיים (לא בונה "
              f"מחדש, לא נדרס).\n{'=' * 70}")
        topic_model = BERTopic.load(save_path)
    else:
        print(f"\n{'=' * 70}\nבונה מודל '{name}' (embedding_model={embedding_model}, "
              f"min_topic_size={MIN_TOPIC_SIZE}, UMAP random_state=42)...\n{'=' * 70}")
        topic_model = build_bertopic_model(
            min_topic_size=MIN_TOPIC_SIZE, random_state=42, embedding_model=embedding_model,
        )
        topic_model.fit(texts_list)
        print(f"'{name}': fit הושלם.")

        apply_experiment_c_representation(topic_model, texts_list)
        print(f"'{name}': update_topics() (representation Experiment C) הושלם.")

        os.makedirs(save_path, exist_ok=True)
        topic_model.save(save_path, serialization="safetensors", save_ctfidf=True)
        print(f"'{name}': נשמר בנפרד ל-{save_path} (לא נדרס אף מודל קיים)")

    cluster_stats = compute_cluster_stats(topic_model, MIN_TOPIC_SIZE)
    largest_stats = compute_largest_topics(topic_model)

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
        "embedding_model": embedding_model,
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
    for name, embedding_model, save_path in CONFIGS:
        all_results[name] = analyze_one(name, embedding_model, save_path, texts_list)

    print("\n\n" + "=" * 70)
    print("=== Experiment B: baseline (MiniLM-L6-v2) מול mpnet-base-v2 ===")
    print("=" * 70)
    for name, res in all_results.items():
        cs = res["cluster_stats"]
        ls = res["largest_topics_stats"]
        sq = res["soft_quality_summary"]
        print(f"\n--- {name} (embedding_model={res['embedding_model']}) ---")
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
              f"{ls['top2_combined_pct_of_clustered']}% מהמקובצים (מדד ה-mega-topic)")
        print("  8. מילות-מעקב rulesbased/call/hard/era -> topic ids (בדיקת המיזוג):")
        for word, tids in res["watch_word_topic_ids"].items():
            print(f"       '{word}': {tids}")
        print("  Topics 'שליטה' (gaza/ukraine/iran/telephone/home/maria) - נשארו נפרדים?")
        for theme, ct in res["control_topics"].items():
            if ct is None:
                print(f"       {theme}: לא נמצא topic מתאים (!)")
            else:
                print(f"       {theme}: Topic {ct['topic_id']} (n={ct['count']}), label='{ct['label']}'")

    comparison_json_path = os.path.join(REPORT_DIR, "expB_mpnet_vs_minilm_comparison.json")
    with open(comparison_json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nנשמרה השוואה מובנית מלאה ל-{comparison_json_path}")


if __name__ == "__main__":
    run()

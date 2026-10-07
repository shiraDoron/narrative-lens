"""Experiment B seed-stability check: is the Experiment B result (mpnet beats MiniLM on outlier %,
hard/soft agreement, soft-signal coverage, AND fixes the 'rulesbased' duplicate-topic pair without
mega-topic collapse) consistent across multiple UMAP random seeds, or was it a lucky roll on
random_state=42?

Per explicit user request (2026-08-31): re-run Experiment B's exact comparison (min_topic_size=10,
same preprocessing/dedup/Experiment C representation, same 16,062-text corpus) at two ADDITIONAL
UMAP random_state values (7, 123), for BOTH embedding models (all-MiniLM-L6-v2, all-mpnet-base-v2).
Combined with the existing random_state=42 results (soft_v2_baseline_seeded /
soft_v2_expB_mpnet, reused as-is, NOT refit), this gives 3 seeds x 2 embedding models = 6 data
points total (4 newly fit here, 2 reused).

Compares, per (embedding, seed) pair: topic count, outlier %, hard/soft agreement, soft-signal
coverage, small-topic counts, largest-topic/mega-topic metric, whether the 'rulesbased' topic
stays merged into ONE topic (mpnet) or stays as a duplicate pair (MiniLM), and prints the top
words of the gaza/ukraine/iran/maria/home control topics for manual coherence inspection (per the
established gotcha: automated "not found"/count-based signals must be manually eyeballed, since
tokenization of the same underlying topic can differ across embedding models/seeds - e.g.
'rulesbased' vs. 'rules based').

Ends with a 3-seed x 2-embedding comparison table AND a per-embedding-model average across all 3
seeds for every numeric metric, to answer ONE question: does mpnet consistently beat MiniLM across
seeds, or was seed=42 a lucky draw?

Does NOT touch fusion.py, train.py, any .pth checkpoint, models/saved_topic_model,
models/saved_topic_model_soft_v2, or any existing experiment folder - each new model is saved to
its own separate path under models/experiments/soft_v2_seedstab_<embedding>_seed<N>.

Run (from repo root): python experiments/topic_modeling/experiment_b_seed_stability.py
"""
import json
import os
import shutil

from bertopic import BERTopic

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
from narrative_lens.topic_modeling.topic_preprocessing import build_multiword_label
from narrative_lens.train_topics import build_bertopic_model, load_deduplicated_training_texts

REPORT_DIR = "artifacts/experiments/profiler_prototype"
MIN_TOPIC_SIZE = 10

EMBEDDINGS = [
    ("minilm", "sentence-transformers/all-MiniLM-L6-v2"),
    ("mpnet", "sentence-transformers/all-mpnet-base-v2"),
]

# (embedding_key, seed, save_path) - seed=42 entries reuse Experiment B's existing models
CONFIGS = [
    ("minilm", 42, "models/experiments/soft_v2_baseline_seeded"),
    ("minilm", 7, "models/experiments/soft_v2_seedstab_minilm_seed7"),
    ("minilm", 123, "models/experiments/soft_v2_seedstab_minilm_seed123"),
    ("mpnet", 42, "models/experiments/soft_v2_expB_mpnet"),
    ("mpnet", 7, "models/experiments/soft_v2_seedstab_mpnet_seed7"),
    ("mpnet", 123, "models/experiments/soft_v2_seedstab_mpnet_seed123"),
]

EMBEDDING_MODEL_BY_KEY = dict(EMBEDDINGS)

# themes the user explicitly asked to check for coherence (subset of ALL_CONTROL_THEMES)
COHERENCE_THEMES = ["gaza_ceasefire", "ukraine_glory", "iran_related", "maria_lying", "home_bring"]


def find_rulesbased_topics(topic_model):
    """Robust to both tokenizations seen so far: MiniLM's concatenated 'rulesbased' single token,
    and mpnet's bigram 'rules based'. Requires BOTH 'rule' and 'based' substrings to co-occur
    among a topic's top-10 words (as one word or across two), to avoid false positives like a
    'rule law' (judicial fairness) topic which has 'rule' but not 'based'."""
    matches = []
    for tid in topic_model.get_topics().keys():
        if tid == -1:
            continue
        words = [w.lower() for w in _topic_snapshot(topic_model, tid, top_n=10)]
        joined = " ".join(words)
        if "rulesbased" in joined.replace(" ", "") or ("rule" in joined and "based" in joined):
            matches.append(tid)
    return matches


def analyze_one(embedding_key, seed, save_path, texts_list):
    embedding_model = EMBEDDING_MODEL_BY_KEY[embedding_key]
    name = f"{embedding_key}_seed{seed}"
    already_saved = os.path.exists(os.path.join(save_path, "topics.json"))
    if already_saved:
        print(f"\n{'=' * 70}\n'{name}': מודל כבר קיים ב-{save_path} - טוען מודל קיים (לא בונה "
              f"מחדש, לא נדרס).\n{'=' * 70}")
        topic_model = BERTopic.load(save_path)
    else:
        print(f"\n{'=' * 70}\nבונה מודל '{name}' (embedding_model={embedding_model}, "
              f"min_topic_size={MIN_TOPIC_SIZE}, UMAP random_state={seed})...\n{'=' * 70}")
        topic_model = build_bertopic_model(
            min_topic_size=MIN_TOPIC_SIZE, random_state=seed, embedding_model=embedding_model,
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
    rulesbased_topic_ids = find_rulesbased_topics(topic_model)

    info_df = topic_model.get_topic_info()
    rulesbased_topics = [
        {
            "topic_id": int(tid),
            "count": int(info_df.loc[info_df["Topic"] == tid, "Count"].iloc[0]),
            "top_words": _topic_snapshot(topic_model, tid, top_n=6),
        }
        for tid in rulesbased_topic_ids
    ]

    coherence_topics = {
        theme: find_control_topic_substring(topic_model, ALL_CONTROL_THEMES[theme])
        for theme in COHERENCE_THEMES
    }

    print(f"'{name}': מריץ ניתוח hard/soft agreement (analyze_soft_topic_quality, n=280, seed=42)...")
    _, summary, _, _ = run_analysis_with_retry(save_path)
    for fname in ("soft_topic_quality_full.csv", "soft_topic_quality_summary.json",
                  "soft_topic_cooccurrence.csv", "soft_topic_quality_examples.csv"):
        src_path = os.path.join(REPORT_DIR, fname)
        if os.path.exists(src_path):
            base, ext = os.path.splitext(fname)
            shutil.copy(src_path, os.path.join(REPORT_DIR, f"{base}.{name}{ext}"))

    agreement = summary.get("hard_soft_agreement_counts", {})
    return {
        "embedding_key": embedding_key,
        "embedding_model": embedding_model,
        "seed": seed,
        "save_path": save_path,
        "n_topics": cluster_stats["n_topics"],
        "outlier_pct": cluster_stats["outlier_pct"],
        "topic_size_mean": cluster_stats["topic_size_mean"],
        "topic_size_median": cluster_stats["topic_size_median"],
        "n_small_topics_leq15": cluster_stats["n_small_topics_leq15"],
        "n_topics_at_own_floor": cluster_stats["n_topics_at_own_floor"],
        "agreement_true": agreement.get("True", 0),
        "agreement_false": agreement.get("False", 0),
        "agreement_none": agreement.get("None", 0),
        "pct_texts_with_soft_signal": pct_with_soft_signal(summary),
        "top1_topic_size": largest_stats["largest_topics"][0]["count"] if largest_stats["largest_topics"] else None,
        "top2_combined_pct": largest_stats["top2_combined_pct_of_clustered"],
        "largest_topics": largest_stats["largest_topics"],
        "n_rulesbased_topics": len(rulesbased_topic_ids),
        "rulesbased_topics": rulesbased_topics,
        "coherence_topics": coherence_topics,
    }


def avg(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 2) if values else None


def run():
    print("טוען את טקסטי האימון (ניקוי + deduplication, כולל תיקון ניקוי bit.ly)...")
    texts_list = load_deduplicated_training_texts(verbose=True)

    all_results = {}
    for embedding_key, seed, save_path in CONFIGS:
        name = f"{embedding_key}_seed{seed}"
        all_results[name] = analyze_one(embedding_key, seed, save_path, texts_list)

    print("\n\n" + "=" * 70)
    print("=== יציבות בין seeds: MiniLM מול mpnet, seeds 42/7/123 ===")
    print("=" * 70)
    for name, res in all_results.items():
        print(f"\n--- {name} ---")
        print(f"  מספר Topics: {res['n_topics']} | אחוז outliers: {res['outlier_pct']}%")
        print(f"  Hard/Soft agreement (True/False/None): "
              f"{res['agreement_true']}/{res['agreement_false']}/{res['agreement_none']}")
        print(f"  אחוז עם soft signal: {res['pct_texts_with_soft_signal']}%")
        print(f"  גודל ממוצע/חציוני: {res['topic_size_mean']}/{res['topic_size_median']} | "
              f"Topics קטנים (<=15/<=floor+10): {res['n_small_topics_leq15']}/{res['n_topics_at_own_floor']}")
        print(f"  Topic הגדול ביותר: {res['top1_topic_size']} | 2 הגדולים ביחד: "
              f"{res['top2_combined_pct']}% (mega-topic check)")
        print(f"  'rulesbased': {res['n_rulesbased_topics']} topic(s) נמצאו: "
              f"{[(t['topic_id'], t['count'], t['top_words'][:3]) for t in res['rulesbased_topics']]}")
        print("  Coherence themes (gaza/ukraine/iran/maria/home):")
        for theme, ct in res["coherence_topics"].items():
            if ct is None:
                print(f"    {theme}: לא נמצא (!)")
            else:
                print(f"    {theme}: Topic {ct['topic_id']} (n={ct['count']}) top_words={ct['top_words']}")

    print("\n\n" + "=" * 70)
    print("=== טבלת השוואה: 3 seeds x 2 embeddings + ממוצעים ===")
    print("=" * 70)
    header = f"{'seed':<8}{'embedding':<10}{'topics':<8}{'outlier%':<10}{'T/F/None':<14}{'soft%':<8}{'small<=15':<11}{'top1':<7}{'top2%':<8}{'rulesb#':<9}"
    print(header)
    for embedding_key, _ in EMBEDDINGS:
        for seed in (42, 7, 123):
            r = all_results[f"{embedding_key}_seed{seed}"]
            agreement_str = f"{r['agreement_true']}/{r['agreement_false']}/{r['agreement_none']}"
            print(f"{seed:<8}{embedding_key:<10}{r['n_topics']:<8}{r['outlier_pct']:<10}"
                  f"{agreement_str:<14}"
                  f"{r['pct_texts_with_soft_signal']:<8}{r['n_small_topics_leq15']:<11}"
                  f"{r['top1_topic_size']:<7}{r['top2_combined_pct']:<8}{r['n_rulesbased_topics']:<9}")

    averages = {}
    for embedding_key, _ in EMBEDDINGS:
        rows = [all_results[f"{embedding_key}_seed{s}"] for s in (42, 7, 123)]
        averages[embedding_key] = {
            "avg_n_topics": avg([r["n_topics"] for r in rows]),
            "avg_outlier_pct": avg([r["outlier_pct"] for r in rows]),
            "avg_agreement_true": avg([r["agreement_true"] for r in rows]),
            "avg_agreement_false": avg([r["agreement_false"] for r in rows]),
            "avg_agreement_none": avg([r["agreement_none"] for r in rows]),
            "avg_pct_soft_signal": avg([r["pct_texts_with_soft_signal"] for r in rows]),
            "avg_n_small_topics_leq15": avg([r["n_small_topics_leq15"] for r in rows]),
            "avg_n_topics_at_own_floor": avg([r["n_topics_at_own_floor"] for r in rows]),
            "avg_top1_topic_size": avg([r["top1_topic_size"] for r in rows]),
            "avg_top2_combined_pct": avg([r["top2_combined_pct"] for r in rows]),
            "n_rulesbased_topics_per_seed": [r["n_rulesbased_topics"] for r in rows],
        }
    print("\n--- ממוצעים על פני 3 ה-seeds ---")
    for embedding_key, a in averages.items():
        print(f"\n{embedding_key}: {json.dumps(a, ensure_ascii=False, indent=2)}")

    out = {"per_config": all_results, "averages": averages}
    comparison_json_path = os.path.join(REPORT_DIR, "expB_seed_stability_comparison.json")
    with open(comparison_json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nנשמרה השוואה מובנית מלאה ל-{comparison_json_path}")


if __name__ == "__main__":
    run()

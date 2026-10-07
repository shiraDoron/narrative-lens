"""Experiment A: BERTopic clustering-granularity (min_topic_size) sweep, on a NEW reproducible
seeded baseline.

Per explicit user request (2026-08-31): before touching clustering granularity, pin UMAP's
random_state=42 (see train_topics.py's build_bertopic_model()) so re-fits are reproducible, then
build a fresh "baseline" re-fit (min_topic_size=10, otherwise identical config/data/preprocessing/
dedup to saved_topic_model_soft_v2) as the true apples-to-apples reference point - NOT reusing the
existing (non-seeded) saved_topic_model_soft_v2 for this comparison, since its randomness makes
before/after deltas unattributable to min_topic_size alone.

Fits 3 SEPARATE models (real embedding+UMAP+HDBSCAN re-run each time - unlike Experiment C's
update_topics(), this is a genuine re-cluster):
  - baseline (min_topic_size=10, seeded)  -> models/experiments/soft_v2_baseline_seeded
  - Experiment A, min_topic_size=25       -> models/experiments/soft_v2_expA_mts25
  - Experiment A, min_topic_size=35       -> models/experiments/soft_v2_expA_mts35

Each model gets Experiment C's already-validated representation improvement applied
(update_topics() with the same CountVectorizer/ClassTfidfTransformer/MaximalMarginalRelevance
settings) before saving, so all label comparisons across the 3 models use the SAME improved,
human-readable representation - apples-to-apples label quality, not just clustering quality.

Compares, per model: topic count, outlier %, avg/median topic size, count of small topics (both an
absolute <=15-doc threshold and a floor-relative threshold), whether the known 'rulesbased'
duplicate-topic pair merged, hard/soft agreement (reusing analyze_soft_topic_quality's identical
n=280/seed=42 stratified sample for direct comparability), manual label quality on the 15 smallest
topics, and whether previously-good large topics (gaza/ukraine/telephone/home/maria themes,
identified by CONTENT since topic ids are not stable across separate fits) regressed.

Does NOT touch saved_topic_model_soft_v2, models/saved_topic_model (legacy), fusion.py, train.py,
or any .pth checkpoint - each new model is saved to its own separate path under
models/experiments/.

Run (from repo root): python experiments/topic_modeling/experiment_a_min_topic_size.py
"""
import json
import os
import shutil
import time

from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

from narrative_lens.evaluation.analyze_soft_topic_quality import analyze as run_soft_quality_analysis
from experiment_c_representation import _find_topics_by_top_word, _topic_snapshot
from narrative_lens.topic_modeling.topic_preprocessing import build_multiword_label
from narrative_lens.train_topics import build_bertopic_model, load_deduplicated_training_texts

REPORT_DIR = "artifacts/experiments/profiler_prototype"

# (display name, min_topic_size, save path)
CONFIGS = [
    ("baseline_mts10", 10, "models/experiments/soft_v2_baseline_seeded"),
    ("expA_mts25", 25, "models/experiments/soft_v2_expA_mts25"),
    ("expA_mts35", 35, "models/experiments/soft_v2_expA_mts35"),
]

# Same 4 watch-words flagged by the user in Experiment C - lets us check whether the two
# 'rulesbased' topics (over-segmented duplicates at mts=10) actually merge into one at mts=25/35.
WATCH_WORDS = ["rulesbased", "call", "hard", "era"]

# Themes of the 5 largest ("control") topics identified in Experiment C's soft_v2 run (sizes at
# mts=10, post-dedup: gaza=150, ukraine=156, telephone=254, home=214, maria=193) - used to find the
# corresponding topic (by CONTENT/keyword, since topic ids are NOT stable across separate fits) in
# each new model and check it wasn't degraded by the min_topic_size change.
CONTROL_THEMES = {
    "gaza_ceasefire": "gaza",
    "ukraine_glory": "ukraine",
    "telephone_conversation": "telephone",
    "home_bring": "home",
    "maria_lying": "maria",
}
N_SMALLEST_SHOWN = 15


def apply_experiment_c_representation(topic_model, texts_list):
    """Applies the SAME representation improvement validated in Experiment C, so all 3 models in
    this sweep are compared using identical, already-validated label-quality settings (fresh
    transformer instances each call - these hold fit state, can't be reused across models)."""
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
        "outlier_pct": round(100 * n_outliers / n_docs_total, 1) if n_docs_total else None,
        "topic_size_mean": round(float(non_outlier["Count"].mean()), 1) if len(non_outlier) else None,
        "topic_size_median": float(non_outlier["Count"].median()) if len(non_outlier) else None,
        # absolute smallness (comparable across all 3 configs - will correctly be 0 for
        # mts=25/35 since HDBSCAN can't produce a topic smaller than min_topic_size at all)
        "n_small_topics_leq15": int((non_outlier["Count"] <= 15).sum()),
        # floor-relative smallness (is over-segmentation still happening right at the NEW floor,
        # just shifted up?)
        "n_topics_at_own_floor": int((non_outlier["Count"] <= min_topic_size + 10).sum()),
    }


def find_control_topic(topic_model, keyword, top_k_search=8):
    """Finds the topic best matching `keyword` in its top-N words (content-based match, since
    topic ids differ across separate fits). If multiple topics match, returns the largest one."""
    matches = _find_topics_by_top_word(topic_model, keyword, top_k_search=top_k_search)
    if not matches:
        return None
    info_df = topic_model.get_topic_info()
    sizes = {tid: int(info_df.loc[info_df["Topic"] == tid, "Count"].iloc[0]) for tid in matches}
    best_tid = max(sizes, key=sizes.get)
    return {
        "topic_id": best_tid,
        "count": sizes[best_tid],
        "label": build_multiword_label(topic_model.get_topic(best_tid), top_n_words=3),
        "top_words": _topic_snapshot(topic_model, best_tid, top_n=6),
    }


def run_analysis_with_retry(save_path, attempts=3):
    """analyze_soft_topic_quality reloads the saved BERTopic model via BERTopic.load(path), which
    re-resolves the embedding model by name (e.g. from the HF Hub / local cache) rather than
    bundling its weights in the safetensors save. This has been observed to occasionally fail
    transiently (BERTopic silently falls back to embedding_model=None and later raises 'No
    embedding model was found' inside .transform()) - retry a few times before giving up."""
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            return run_soft_quality_analysis(n_per_narrative=40, model_path=save_path)
        except ValueError as e:
            last_err = e
            print(f"  (ניסיון {attempt}/{attempts} נכשל: {e} - מנסה שוב...)")
            time.sleep(2)
    raise last_err


def run():
    print("טוען את טקסטי האימון (ניקוי + deduplication, כולל תיקון ניקוי bit.ly החדש)...")
    texts_list = load_deduplicated_training_texts(verbose=True)

    all_results = {}
    for name, min_topic_size, save_path in CONFIGS:
        already_saved = os.path.exists(os.path.join(save_path, "topics.json"))
        if already_saved:
            print(f"\n{'=' * 70}\n'{name}': מודל כבר קיים ב-{save_path} - מדלג על fit, טוען מחדש "
                  f"לצורך ניתוח בלבד.\n{'=' * 70}")
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
            print(f"'{name}': נשמר בנפרד ל-{save_path}")

        cluster_stats = compute_cluster_stats(topic_model, min_topic_size)

        watch_word_topics = {
            word: _find_topics_by_top_word(topic_model, word, top_k_search=3)
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
            theme: find_control_topic(topic_model, keyword)
            for theme, keyword in CONTROL_THEMES.items()
        }

        print(f"'{name}': מריץ ניתוח hard/soft agreement (analyze_soft_topic_quality, n=280, seed=42)...")
        _, summary, _, _ = run_analysis_with_retry(save_path)
        # analyze() writes to shared fixed filenames - copy them aside per-config so each run's
        # output survives the next config's overwrite (mirrors the existing .BEFORE_X convention)
        for fname in ("soft_topic_quality_full.csv", "soft_topic_quality_summary.json",
                      "soft_topic_cooccurrence.csv", "soft_topic_quality_examples.csv"):
            src_path = os.path.join(REPORT_DIR, fname)
            if os.path.exists(src_path):
                base, ext = os.path.splitext(fname)
                shutil.copy(src_path, os.path.join(REPORT_DIR, f"{base}.{name}{ext}"))

        all_results[name] = {
            "min_topic_size": min_topic_size,
            "save_path": save_path,
            "cluster_stats": cluster_stats,
            "watch_word_topics": watch_word_topics,
            "smallest_topics": smallest_topics,
            "control_topics": control_topics,
            "soft_quality_summary": summary,
        }

    print("\n\n" + "=" * 70)
    print("=== השוואת baseline (mts=10, seeded) מול Experiment A (mts=25) ו-(mts=35) ===")
    print("=" * 70)
    for name, res in all_results.items():
        cs = res["cluster_stats"]
        sq = res["soft_quality_summary"]
        print(f"\n--- {name} (min_topic_size={res['min_topic_size']}) ---")
        print(f"  מספר Topics (ללא -1): {cs['n_topics']}")
        print(f"  אחוז outliers: {cs['outlier_pct']}% ({cs['n_outliers']}/{cs['n_docs_total']})")
        print(f"  גודל Topic ממוצע/חציוני: {cs['topic_size_mean']} / {cs['topic_size_median']}")
        print(f"  מספר Topics קטנים (<=15 מסמכים, מוחלט): {cs['n_small_topics_leq15']}")
        print(f"  מספר Topics צמודים לרצפה שלהם (<=min_topic_size+10): {cs['n_topics_at_own_floor']}")
        print(f"  Hard/Soft agreement counts: {sq['hard_soft_agreement_counts']}")
        print(f"  hard_is_outlier_pct (מדגם n=280): {sq['hard_is_outlier_pct']}%")
        print(f"  case_pct (dominant/spread/no_signal): {sq['case_pct']}")
        print("  מילות-מעקב (rulesbased/call/hard/era) -> topics:")
        for word, tids in res["watch_word_topics"].items():
            print(f"    '{word}': {tids}")
        print("  15 ה-Topics הקטנים ביותר:")
        for t in res["smallest_topics"]:
            print(f"    Topic {t['topic_id']} (n={t['count']}): label='{t['label']}' | "
                  f"top6={' | '.join(t['top_words'])}")
        print("  Topics 'שליטה' (היו גדולים/טובים ב-Experiment C):")
        for theme, ct in res["control_topics"].items():
            if ct is None:
                print(f"    {theme}: לא נמצא topic מתאים (!)")
            else:
                print(f"    {theme}: Topic {ct['topic_id']} (n={ct['count']}), label='{ct['label']}'")

    comparison_json_path = os.path.join(REPORT_DIR, "expA_min_topic_size_comparison.json")
    with open(comparison_json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nנשמרה השוואה מובנית מלאה ל-{comparison_json_path}")


if __name__ == "__main__":
    run()

"""Experiment C: improve saved_topic_model_soft_v2's topic REPRESENTATION (labels) only.

Does NOT touch embedding_model / UMAP / HDBSCAN / min_topic_size - clustering itself is left
100% untouched. Uses BERTopic.update_topics() on the ALREADY-FITTED model, which only recomputes
the vectorizer/c-TF-IDF/representation layer from the existing topic assignments (self.topics_) -
no re-embedding, no UMAP, no HDBSCAN re-run.

Changes tested (all local, no Gemini/external API):
  - vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 2))
  - ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True, bm25_weighting=True)
  - representation_model = MaximalMarginalRelevance(diversity=0.3)

Saves the updated model to a SEPARATE experiment path (models/experiments/soft_v2_expC_representation)
- does NOT overwrite models/saved_topic_model_soft_v2. The legacy model (models/saved_topic_model),
fusion.py, train.py and all .pth checkpoints are not touched by this script at all.

Run (from repo root): python experiments/topic_modeling/experiment_c_representation.py
"""
import os

import pandas as pd
from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# Moved out of src/ into experiments/ - add src/ and sibling experiment folders to sys.path so
# same-style flat imports (e.g. `from train_topics import ...`) keep working unmodified.
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _rel_dir in ("src", "experiments/topic_modeling", "experiments/feature_ablation", "experiments/author_generalization"):
    _abs_dir = os.path.join(_REPO_ROOT, _rel_dir)
    if _abs_dir not in sys.path:
        sys.path.insert(0, _abs_dir)

from config import TOPIC_MODEL_PATH_SOFT
from topic_preprocessing import build_multiword_label
from train_topics import load_deduplicated_training_texts

EXPERIMENT_MODEL_PATH = "models/experiments/soft_v2_expC_representation"
REPORT_PATH = "reports/results/profiler_prototype/expC_label_comparison.csv"

# Topics explicitly flagged by the user as generic/problematic in the earlier analysis
WATCH_WORDS = ["rulesbased", "call", "hard", "era"]
N_SMALLEST = 15
N_LARGEST_CONTROL = 5


def _topic_snapshot(topic_model, topic_id, top_n=6):
    info = topic_model.get_topic(topic_id)
    words = [w for w, _ in info[:top_n]] if info else []
    return words


def _find_topics_by_top_word(topic_model, word, top_k_search=3):
    """Returns topic ids where `word` appears among the top-`top_k_search` c-TF-IDF words."""
    matches = []
    for tid in topic_model.get_topics().keys():
        if tid == -1:
            continue
        info = topic_model.get_topic(tid)
        top_words = [w.lower() for w, _ in info[:top_k_search]] if info else []
        if word.lower() in top_words:
            matches.append(tid)
    return matches


def run():
    print("טוען את טקסטי האימון (ניקוי + deduplication, זהה למה שהמודל אומן עליו)...")
    texts_list = load_deduplicated_training_texts(verbose=False)

    print(f"טוען את המודל הקיים מ-'{TOPIC_MODEL_PATH_SOFT}'...")
    topic_model = BERTopic.load(TOPIC_MODEL_PATH_SOFT)

    # Sanity check - update_topics() requires docs to align 1:1 with the model's existing
    # per-document topic assignments (self.topics_). A mismatch here would silently corrupt
    # the topic representations, so we fail loudly instead.
    n_fitted = len(topic_model.topics_)
    assert len(texts_list) == n_fitted, (
        f"Text count mismatch: reproduced {len(texts_list)} training texts but the loaded "
        f"model was fitted on {n_fitted}. Raw CSVs may have changed since the last train run - "
        f"aborting to avoid silently corrupting topic representations."
    )
    print(f"אימות: {len(texts_list)} טקסטים תואמים בדיוק למספר המסמכים שהמודל אומן עליהם.")

    # --- Select topics to compare before/after ---
    watch_topic_ids = []
    for word in WATCH_WORDS:
        found = _find_topics_by_top_word(topic_model, word)
        print(f"  מילת-מעקב '{word}' -> topics: {found}")
        watch_topic_ids.extend(found)

    info_df = topic_model.get_topic_info()
    info_df = info_df[info_df["Topic"] != -1]
    smallest_ids = info_df.sort_values("Count", ascending=True).head(N_SMALLEST)["Topic"].tolist()
    largest_ids = info_df.sort_values("Count", ascending=False).head(N_LARGEST_CONTROL)["Topic"].tolist()

    # De-duplicated, order-preserving union: watch-word topics, then smallest, then largest (control)
    selected_ids = []
    for tid in watch_topic_ids + smallest_ids + largest_ids:
        if tid not in selected_ids:
            selected_ids.append(tid)
    print(f"\nנבחרו {len(selected_ids)} topics להשוואה before/after: {selected_ids}")

    # --- Capture BEFORE snapshot ---
    before_snapshot = {}
    for tid in selected_ids:
        count = int(info_df.loc[info_df["Topic"] == tid, "Count"].iloc[0])
        before_snapshot[tid] = {
            "count": count,
            "top_words": _topic_snapshot(topic_model, tid, top_n=6),
        }

    # --- Apply Experiment C representation update ---
    print("\nמריץ update_topics() עם vectorizer/c-TF-IDF/representation חדשים "
          "(ה-clustering עצמו לא משתנה)...")
    vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 2))
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True, bm25_weighting=True)
    representation_model = MaximalMarginalRelevance(diversity=0.3)
    topic_model.update_topics(
        texts_list,
        vectorizer_model=vectorizer_model,
        ctfidf_model=ctfidf_model,
        representation_model=representation_model,
    )
    print("update_topics() הושלם.")

    # --- Capture AFTER snapshot ---
    after_info_df = topic_model.get_topic_info()
    after_info_df = after_info_df[after_info_df["Topic"] != -1]
    rows = []
    for tid in selected_ids:
        after_count = int(after_info_df.loc[after_info_df["Topic"] == tid, "Count"].iloc[0])
        after_words = _topic_snapshot(topic_model, tid, top_n=6)
        after_raw_topic = topic_model.get_topic(tid)
        before = before_snapshot[tid]
        rows.append({
            "topic_id": tid,
            "count_before": before["count"],
            "count_after": after_count,
            "label_before_1word": before["top_words"][0] if before["top_words"] else "",
            "top_words_before": " | ".join(before["top_words"]),
            "label_after_3word_deduped": build_multiword_label(after_raw_topic, top_n_words=3),
            "top_words_after": " | ".join(after_words),
        })

    comparison_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    comparison_df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
    print(f"\nנשמרה טבלת השוואה ל-{REPORT_PATH}")

    print("\n=== השוואת before/after ===")
    for _, row in comparison_df.iterrows():
        print(f"\nTopic {row['topic_id']} (count: {row['count_before']} -> {row['count_after']})")
        print(f"  לפני : label='{row['label_before_1word']}' | top6={row['top_words_before']}")
        print(f"  אחרי : label='{row['label_after_3word_deduped']}' | top6={row['top_words_after']}")

    # --- Sanity check: confirm clustering itself (topic count + per-topic doc counts) unchanged ---
    n_topics_before = len(before_snapshot)  # not the full count, just informational
    full_before_info = info_df[["Topic", "Count"]].set_index("Topic")["Count"]
    full_after_info = after_info_df[["Topic", "Count"]].set_index("Topic")["Count"]
    counts_identical = full_before_info.equals(full_after_info)
    print(f"\n=== אימות שה-clustering לא השתנה ===")
    print(f"מספר topics (ללא -1): לפני={len(full_before_info)}, אחרי={len(full_after_info)}")
    print(f"גדלי כל ה-topics זהים לחלוטין לפני/אחרי: {counts_identical}")

    # --- Save to a SEPARATE experiment path, do NOT overwrite saved_topic_model_soft_v2 ---
    os.makedirs(EXPERIMENT_MODEL_PATH, exist_ok=True)
    topic_model.save(EXPERIMENT_MODEL_PATH, serialization="safetensors", save_ctfidf=True)
    print(f"\nהמודל של הניסוי נשמר בנפרד ל-'{EXPERIMENT_MODEL_PATH}' "
          f"(saved_topic_model_soft_v2 לא נדרס).")


if __name__ == "__main__":
    run()

import os

import numpy as np
import pandas as pd
from bertopic import BERTopic
from umap import UMAP

from config import TOPIC_MODEL_PATH_SOFT
from llm_topic_refiner import refine_topics_with_llm
# Shared (train + inference) preprocessing - see topic_preprocessing.py docstring for why this
# MUST be the same function used by stance.py's TopicAnalysisPipeline at inference time.
from topic_preprocessing import clean_text_for_topic_model, has_enough_content
# Shared near-duplicate detection (MinHash+LSH+Jaccard, see text_dedup.py docstring) - same
# method/threshold validated in analyze_text_duplicates.py. Applied ONLY to the soft_v2 training
# texts below (in-memory only - raw CSVs are never modified).
from text_dedup import deduplicate_texts, NEAR_DUP_THRESHOLD


def load_deduplicated_training_texts(verbose=True):
    """טוען+מנקה+מבצע deduplication על נתוני האימון של saved_topic_model_soft_v2, בדיוק
    לפי אותו pipeline ש-build_and_save_topics() משתמש בו לפני BERTopic().fit(). מופרד
    לפונקציה עצמאית (ולא רק inline בתוך build_and_save_topics()) כדי שגם סקריפטי ניסוי
    שקוראים ל-BERTopic.update_topics() על המודל הקיים (למשל experiment_c_representation.py)
    יוכלו לשחזר בדיוק את אותה רשימת טקסטים/סדר שהמודל הנוכחי אומן עליה - update_topics()
    דורש doc-list שתואם אחד-לאחד למספר/סדר ה-topics_ הפנימיים שכבר שמורים במודל."""
    if verbose:
        print("טוען את קבצי הנתונים...")
    df_llm = pd.read_csv("data/raw/gemini_natural_dataset.csv")
    df_little = pd.read_csv("data/raw/gpt_natural_dataset.csv")
    df_twitter = pd.read_csv("data/raw/twitter_natural_dataset.csv")
    df_telegram = pd.read_csv("data/raw/telegram_natural_dataset.csv")

    # איחוד הקבצים
    full_data = pd.concat([df_llm, df_little, df_twitter, df_telegram], ignore_index=True)
    raw_texts_list = full_data['text'].dropna().astype(str).tolist()

    # ניקוי @mentions/#hashtags/URLs + הסרת טקסטים ריקים/כמעט-ריקים אחרי הניקוי (ראו
    # topic_preprocessing.py - זו אותה פונקציה בדיוק שמשמשת את stance.py ב-inference,
    # כדי להבטיח עקביות מלאה בין אימון להסקה. נמצא אמפירית ב-analyze_soft_topic_quality.py
    # שללא זה נוצרים topics מזוהמים כמו "ddgeopolitics").
    texts_list = []
    n_dropped_empty = 0
    for raw in raw_texts_list:
        cleaned = clean_text_for_topic_model(raw)
        if not has_enough_content(cleaned):
            n_dropped_empty += 1
            continue
        texts_list.append(cleaned)
    if verbose:
        print(f"ניקוי הושלם: {len(raw_texts_list)} משפטים -> {len(texts_list)} נשארו "
              f"({n_dropped_empty} הוסרו כי היו ריקים/כמעט-ריקים אחרי הניקוי).")

    # Deduplication (near-duplicate removal) - applied ONLY to the soft_v2 training texts,
    # in-memory only (raw CSV files are never modified). Uses the SAME MinHash+LSH+Jaccard
    # method/threshold (0.7) validated in analyze_text_duplicates.py: word-3-gram shingles,
    # Jaccard similarity >= NEAR_DUP_THRESHOLD -> keep exactly ONE representative (lowest
    # original index) per near-duplicate cluster. Deliberately does NOT special-case the
    # "maria"/"lying" texts - the prior investigation showed those are NOT near-duplicates of
    # each other (185/187 had no near-dup match), so they are left untouched here too.
    if verbose:
        print(f"מריץ deduplication (near-duplicate, threshold={NEAR_DUP_THRESHOLD})...")
    n_before_dedup = len(texts_list)
    kept_indices, cluster_summaries = deduplicate_texts(texts_list, threshold=NEAR_DUP_THRESHOLD)
    texts_list = [texts_list[i] for i in kept_indices]
    n_removed_dedup = n_before_dedup - len(texts_list)
    if verbose:
        print(f"Deduplication הושלמה: {n_before_dedup} -> {len(texts_list)} "
              f"({n_removed_dedup} הוסרו כ-near-duplicates, {len(cluster_summaries)} קבוצות "
              f"near-duplicate נמצאו, threshold={NEAR_DUP_THRESHOLD}).")
    return texts_list


def build_bertopic_model(min_topic_size=10, random_state=42, embedding_model=None):
    """Constructs a BERTopic instance with a REPRODUCIBLE UMAP (fixed random_state), used by
    experiment scripts (e.g. experiment_a_min_topic_size.py) that need to fit multiple comparable
    models (a seeded baseline + min_topic_size variants) side by side. Every other component
    (embedding_model, hdbscan_model, vectorizer_model, ctfidf_model, representation_model) is left
    at BERTopic's own defaults, matching exactly what `build_and_save_topics()` below uses for the
    real `saved_topic_model_soft_v2` (confirmed via direct inspection: default UMAP is
    n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine' - reproduced here explicitly,
    plus random_state, which BERTopic's default UMAP does NOT set - that omission is the reason
    soft_v2 itself is non-deterministic across re-fits, see repo memory).

    `embedding_model`: optional override (e.g. "sentence-transformers/all-mpnet-base-v2" for
    Experiment B). Left as None by default, in which case BERTopic falls back to its own default
    ("sentence-transformers/all-MiniLM-L6-v2") - i.e. passing nothing is 100% behavior-identical
    to before this parameter existed.

    Deliberately NOT used by `build_and_save_topics()` itself - the real `saved_topic_model_soft_v2`
    build path is left completely untouched (still non-seeded) so this function's introduction
    carries zero risk to the existing pinned artifact; only NEW experiment scripts opt into it."""
    umap_model = UMAP(
        n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=random_state,
    )
    kwargs = {"umap_model": umap_model, "min_topic_size": min_topic_size}
    if embedding_model is not None:
        kwargs["embedding_model"] = embedding_model
    return BERTopic(**kwargs)


# Anchor point: min_topic_size=10 is the EMPIRICAL choice validated for the current corpus
# (~16,062 texts post-clean/dedup) across Experiments A/A2 (see EXPERIMENTS.md) - every other
# min_topic_size tried at that single size (15/25/35) was rejected. Experiment F then directly
# tested whether smaller/larger corpora need a DIFFERENT min_topic_size, by re-running the same
# kind of sweep at 4 stratified subsample sizes (4K/8K/12K/16K, same 4-source x 7-narrative mix
# preserved at each size) - the empirical result was that min_topic_size=10 ALSO scored best at
# EVERY one of those smaller sizes (4K, 8K, 12K), not just at the original 16K anchor. This
# directly REFUTES the previously-assumed sqrt-down-scaling for smaller corpora (which would have
# recommended ~5/7/9 at 4K/8K/12K) - empirically, going below 10 was never better: it consistently
# scored worse on coherence, diversity, hard/soft agreement AND soft-signal coverage at every
# tested size, because a smaller min_topic_size mainly just produces many more low-value
# micro-topics rather than better topics. See EXPERIMENTS.md, Experiment F, for the full sweep,
# scoring rule, and scaling-law comparison (constant fit the tested 4K-16K range essentially
# perfectly; sqrt/linear/log all fit visibly worse since the empirical optimum simply never moved).
_ANCHOR_CORPUS_SIZE = 16_062
_ANCHOR_MIN_TOPIC_SIZE = 10
# Reasonable bounds regardless of corpus size: never go below the anchor (smaller than 10 was
# never validated and risks the micro-topic fragmentation seen at mts=10 already being close to
# BERTopic's own practical floor), and never exceed 100 (Experiment A found min_topic_size=25
# already causes real mega-topic over-merging and 35 causes severe collapse - 100 is a hard
# safety ceiling for even very large future corpora, to be re-validated empirically if ever hit).
MIN_TOPIC_SIZE_FLOOR = 10
MIN_TOPIC_SIZE_CEILING = 100
# Beyond the largest size Experiment F actually tested (_ANCHOR_CORPUS_SIZE, ~16K), the constant
# recommendation is UNVALIDATED extrapolation, not an empirical finding - Experiment F did find
# that HDBSCAN could tolerate a somewhat higher min_topic_size (up to ~20) without mega-topic
# collapse at 16K vs. only ~10-14 at 4K-8K, a mild hint that much larger corpora MIGHT benefit
# from (and safely tolerate) a bigger min_topic_size, but there is no direct evidence for corpora
# beyond ~16K texts. `_EXTRAPOLATION_LOG_COEFF` applies a small, deliberately gentle log-scaled
# increase ONLY above the validated anchor, as a cautious placeholder - much slower growth than
# the old (now-refuted-for-downscaling) sqrt formula would have given, e.g. at 1,000,000 texts
# this gives ~31 vs. the old formula's ~79. Re-validate with a real large-corpus sweep (same
# methodology as Experiment F) before trusting this beyond-anchor portion.
_EXTRAPOLATION_LOG_COEFF = 5


def recommend_min_topic_size(corpus_size):
    """Recommends a `min_topic_size` for BERTopic/HDBSCAN as a function of corpus size.

    EMPIRICAL BASIS (Experiment F, see EXPERIMENTS.md): a corpus-size subsampling sweep (4K/8K/
    12K/16K, min_topic_size in {5,10,...,35} depending on size, 2 UMAP seeds per config, scored
    on topic coherence/diversity, outlier %, micro-topic fraction, mega-topic/over-merging risk,
    hard/soft agreement, soft-signal coverage, and cross-seed stability - full scoring rule and
    per-config results documented in EXPERIMENTS.md) found that min_topic_size=10 scored best at
    EVERY tested corpus size from 4K to 16K. In other words, across a 4x range of corpus sizes,
    the empirically optimal min_topic_size did NOT need to change at all - a CONSTANT function
    fits the tested data (essentially perfectly) far better than the sqrt/linear/log scaling laws
    that were also fit and compared (see EXPERIMENTS.md for the comparison table). This directly
    overturns the earlier (untested) assumption that smaller corpora need a proportionally
    smaller min_topic_size.

    Formula:
      - For corpus_size <= _ANCHOR_CORPUS_SIZE (~16,062, the largest size actually tested):
        returns the constant _ANCHOR_MIN_TOPIC_SIZE (10) - this is the empirically validated
        portion of the function.
      - For corpus_size > _ANCHOR_CORPUS_SIZE (beyond what Experiment F tested): applies a small
        log-scaled increase, `10 + _EXTRAPOLATION_LOG_COEFF * ln(corpus_size / _ANCHOR_CORPUS_SIZE)`
        - continuous with the constant portion at the anchor, but explicitly UNVALIDATED
        extrapolation (a cautious hedge, not an empirical finding - see the comment above
        `_EXTRAPOLATION_LOG_COEFF`).
      Result is clamped to [MIN_TOPIC_SIZE_FLOOR, MIN_TOPIC_SIZE_CEILING].

    IMPORTANT: this remains a STARTING POINT/recommendation, not a guaranteed optimum, especially
    for corpus sizes far outside the validated 4K-16K range. Users applying this to a
    substantially different corpus (in size, domain, or language mix) should still re-validate
    with the same kind of sweep Experiment F used (a seeded subsampling sweep + the documented
    scoring rule, watching especially for mega-topic collapse per Experiment A/F's method) before
    trusting it blindly.

    Example outputs (validated portion is flat at 10; beyond ~16K is extrapolated, see above):
        recommend_min_topic_size(1_000)     -> 10   (validated: constant within tested range)
        recommend_min_topic_size(16_000)    -> 10   (validated: matches Experiment F's 16K point)
        recommend_min_topic_size(100_000)   -> 19   (EXTRAPOLATED, not empirically tested)
        recommend_min_topic_size(1_000_000) -> 31   (EXTRAPOLATED, not empirically tested)
    """
    if corpus_size <= 0:
        raise ValueError(f"corpus_size must be positive, got {corpus_size}")
    if corpus_size <= _ANCHOR_CORPUS_SIZE:
        raw = _ANCHOR_MIN_TOPIC_SIZE
    else:
        raw = _ANCHOR_MIN_TOPIC_SIZE + _EXTRAPOLATION_LOG_COEFF * np.log(corpus_size / _ANCHOR_CORPUS_SIZE)
    return int(max(MIN_TOPIC_SIZE_FLOOR, min(MIN_TOPIC_SIZE_CEILING, round(raw))))


def build_and_save_topics():
    texts_list = load_deduplicated_training_texts()

    print(f"בונה אשכולות נושאים מתוך {len(texts_list)} משפטים (התהליך עשוי לקחת מספר דקות)...")
    topic_model = BERTopic()
    topic_model.fit(texts_list)

    print("שומר את המודל לתיקייה מקומית...")
    # שימוש בפורמט safetensors המומלץ והמאובטח לשמירת מודלים.
    # save_ctfidf=True: בנוסף למשקלי ה-embedding, שומר גם את ה-vectorizer_model המאומן
    # (CountVectorizer) ואת c_tf_idf_ - נדרש כדי ש-approximate_distribution() (חלוקת
    # נושאים "רכה"/multi-topic, ראו stance.py) יעבוד אחרי טעינה מחדש. וודא (נבדק ידנית):
    # ללא save_ctfidf=True, vectorizer_model.vocabulary_ אינו מאותחל אחרי load() -
    # approximate_distribution() נכשל עם NotFittedError.
    #
    # שומר לנתיב "soft_v2" (config.TOPIC_MODEL_PATH_SOFT) ולא לנתיב הישן/הקפוא
    # models/saved_topic_model - אותו נתיב ישן משמש כרגע כ"פינים" (pinned) של המודל
    # שעליו אומנו הצ'קפוינטים הקיימים (best_narrative_model_hybrid.pth,
    # best_model_hybrid_architecture.pth) דרך TopicStanceLayer, שמניחה מספור topic_id
    # יציב. הרצה חוזרת של סקריפט זה משנה את מספור ה-topic_id (BERTopic לא מבטיח יציבות
    # בין fit-ים) ותשבור את ההתאמה בין topic_id ל-narrative שנלמדה בצ'קפוינטים הישנים -
    # ולכן היא לא נשמרת עוד לנתיב הישן. ראו config.py להסבר המלא על שתי הגרסאות.
    topic_model.save(TOPIC_MODEL_PATH_SOFT, serialization="safetensors", save_ctfidf=True)

    # שמירת משקלי המודל ישירות ל-Google Drive (אותה גרסת soft_v2)
    drive_save_path = "/content/drive/MyDrive/saved_topic_model_soft_v2"
    topic_model.save(drive_save_path, serialization="safetensors", save_ctfidf=True)
    print(f">>> Best Hybrid MLP Model Saved to Drive at: {drive_save_path}")
    print("השמירה הושלמה בהצלחה!")

    # שיפור פרשנות הנושאים בעזרת LLM (גרסה קלה בהשראת LLM-ITL, ראו llm_topic_refiner.py).
    # דורש משתנה סביבה GEMINI_API_KEY; מדלג בשקט אם הוא לא מוגדר כדי לא לשבור
    # את זרימת האימון הרגילה.
    if os.environ.get("GEMINI_API_KEY"):
        print("משכלל תוויות נושאים בעזרת Gemini...")
        refine_topics_with_llm(topic_model, out_path=os.path.join(TOPIC_MODEL_PATH_SOFT, "topics_llm_refined.json"))
    else:
        print("[i] GEMINI_API_KEY לא מוגדר - מדלג על שכלול תוויות הנושאים ב-LLM.")

if __name__ == "__main__":
    build_and_save_topics()
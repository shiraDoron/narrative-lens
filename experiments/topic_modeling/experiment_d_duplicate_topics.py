"""Experiment D: targeted duplicate-topic detection + a merge test on ONLY the confirmed
'rulesbased' pair, run on the SELECTED final baseline (`models/experiments/soft_v2_baseline_seeded`
= all-MiniLM-L6-v2, min_topic_size=10, UMAP random_state=42, dedup, Experiment C representation -
the config Experiments A/A2/B all closed on).

Per explicit user request (before starting a separate future outlier-rate experiment): check
whether the corpus has OTHER genuinely duplicate/near-duplicate topic pairs beyond "rulesbased",
using more than just topic_id / a single label word, then specifically test
`BERTopic.merge_topics()` on the "rulesbased" pair alone, on a SEPARATE experimental model copy,
and compare quality metrics before/after.

Two independent stages:

STAGE 1 - detection (read-only, does not modify or re-save any model):
    For every topic pair (excluding -1), compute THREE similarity signals:
      - semantic_sim:  cosine similarity between BERTopic's own `topic_embeddings_` rows (SBERT
        embedding-space topic centroids) - the same signal `visualize_heatmap(use_ctfidf=False)`
        uses. This is the real "semantic similarity between topics" signal (as opposed to mere
        word overlap), directly addressing the requirement to not rely on labels/top-words alone.
      - lexical_sim:   cosine similarity between `c_tf_idf_` rows (word-overlap-weighted space) -
        `visualize_heatmap(use_ctfidf=True)` equivalent.
      - top10_jaccard: plain set-overlap of each topic's top-10 c-TF-IDF words (cheap, easy to
        eyeball "same vocabulary" signal, reported alongside but NOT part of the ranking score).
    combined_score = mean(semantic_sim, lexical_sim) is used to rank pairs, since relying on only
    one of the two can mislead (word overlap alone can be high for topics that share generic
    vocabulary but are semantically distinct, or low for topics that use different words for the
    same underlying concept).
    For the top-ranked candidates, also pulls a few real example documents per topic straight from
    the training corpus (matched via `topic_model.topics_`), since `get_representative_docs()`
    returns None on this model (BERTopic doesn't persist `representative_docs_` through this
    version's update_topics()+save()+load() round trip) - manual inspection of real documents is
    required per the user's request, not just word lists.
    Saves the ranked candidate list + score-distribution percentiles (to help pick a sensible
    threshold) to `reports/results/profiler_prototype/expD_duplicate_topic_candidates.json`.

STAGE 2 - merge test (writes ONE new model, `models/experiments/soft_v2_expD_merge_rulesbased`;
never touches `soft_v2_baseline_seeded`, `saved_topic_model_soft_v2`, or any other existing path):
    Loads a FRESH `BERTopic.load()` copy of the baseline (a separate Python object from Stage 1,
    so Stage 1's in-memory model is never mutated either), locates the confirmed 'rulesbased' pair
    (reusing `find_rulesbased_topics()` from `experiment_b_seed_stability.py`), calls
    `merge_topics()` on just that pair, saves the result to the new experiment path, then:
      - reports topic count before/after (expect exactly -1),
      - reports outlier count/pct before/after (expect unchanged - merge_topics only reassigns
        docs between two non-outlier topics),
      - reports the merged topic's new top words + size (expect count_a + count_b),
      - content-matches (not id-matches, since merge_topics renumbers all topic ids by frequency)
        every OTHER topic before vs. after to confirm none of them were altered by the merge,
      - re-runs `analyze_soft_topic_quality.analyze()` on the merged model and compares its
        summary against the baseline's ALREADY-SAVED quality snapshot
        (`reports/results/profiler_prototype/soft_topic_quality_summary.minilm_seed42.json`, produced by
        Experiment B's seed-stability check on this exact same baseline model - re-running the
        baseline analysis again would be redundant).

Does NOT touch `fusion.py`, `train.py`, any `.pth` checkpoint, `models/saved_topic_model` (legacy),
`models/saved_topic_model_soft_v2`, or `models/experiments/soft_v2_baseline_seeded`.

Run (from repo root): python experiments/topic_modeling/experiment_d_duplicate_topics.py
"""
import json
import os
import sys

import numpy as np
from bertopic import BERTopic
from sklearn.metrics.pairwise import cosine_similarity

# Some scraped source texts contain characters outside the Windows console's default codepage
# (e.g. curly quotes) which crash a plain print() - reconfigure stdout to UTF-8 with a safe
# fallback, matching the existing pattern in analyze_agendas.py.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from experiment_a_min_topic_size import run_analysis_with_retry
from experiment_b_seed_stability import find_rulesbased_topics
from experiment_c_representation import _topic_snapshot
from narrative_lens.train_topics import load_deduplicated_training_texts

BASELINE_PATH = "models/experiments/soft_v2_baseline_seeded"
MERGE_EXPERIMENT_PATH = "models/experiments/soft_v2_expD_merge_rulesbased"
# Must match models/experiments/soft_v2_baseline_seeded/config.json's "embedding_model" value
# exactly. BERTopic.load() WITHOUT this explicit argument silently drops the embedding-model
# reference (self.embedding_model ends up None, with only a warning printed) - harmless for
# Stage 1 (read-only, no re-embedding needed) but fatal for Stage 2: merge_topics() + .save()
# on such a load produces a config.json with NO "embedding_model" key at all, which then makes
# any later .transform() call (as used by analyze_soft_topic_quality.py) fail with "No embedding
# model was found" - not transient, 100% reproducible, root-caused during this experiment.
BASELINE_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
REPORT_DIR = "reports/results/profiler_prototype"
BASELINE_QUALITY_SNAPSHOT = os.path.join(REPORT_DIR, "soft_topic_quality_summary.minilm_seed42.json")
TOP_N_CANDIDATES = 20
N_EXAMPLE_DOCS = 3
# Proposed (NOT auto-applied) similarity threshold above which a pair is worth a human look.
# Based on the observed score distribution: p99=0.332, p99.5=0.365, p99.9=0.417, max=0.512.
# The confirmed genuine duplicate (rulesbased, topics 96/209) scores 0.461 - above p99.9 but NOT
# the highest-scoring pair overall (several same-domain-but-distinct pairs score higher, up to
# 0.512). This means combined_score has limited discriminative power: a threshold around p99.9
# (~0.42) is a reasonable "flag for manual review" cutoff, but pairs above it are NOT reliably
# duplicates - manual inspection of the top-20 in this run found the rulesbased pair to be the
# ONLY genuine duplicate; the rest were same-domain/related-but-distinct topics. Treat any
# threshold here as a recall-oriented filter for human review, never as an auto-merge trigger.
PROPOSED_COMBINED_SCORE_THRESHOLD = 0.42



def compute_similarity_matrices(topic_model):
    """Row i of the sliced matrices corresponds to topic id i. BERTopic's `topic_embeddings_` and
    `c_tf_idf_` both have topic -1 as their first row (there are `topic_model._outliers`, normally
    1, such leading rows) followed by topics 0..N-1 in order - the same alignment
    `visualize_heatmap()` relies on internally."""
    n_outliers = topic_model._outliers
    semantic_sim = cosine_similarity(topic_model.topic_embeddings_[n_outliers:])
    lexical_sim = cosine_similarity(topic_model.c_tf_idf_[n_outliers:])
    return semantic_sim, lexical_sim


def top_n_words_set(topic_model, tid, n=10):
    return set(w.lower() for w in _topic_snapshot(topic_model, tid, top_n=n))


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def get_example_docs(topic_model, tid, texts_list, n=N_EXAMPLE_DOCS):
    idx = [i for i, t in enumerate(topic_model.topics_) if t == tid]
    return [texts_list[i][:220] for i in idx[:n]]


def find_candidate_pairs(topic_model, texts_list, top_n=TOP_N_CANDIDATES):
    semantic_sim, lexical_sim = compute_similarity_matrices(topic_model)
    info_df = topic_model.get_topic_info()
    info_df = info_df[info_df["Topic"] != -1].set_index("Topic")
    topic_ids = sorted(info_df.index.tolist())
    n = len(topic_ids)
    assert topic_ids == list(range(n)), (
        f"Expected contiguous topic ids 0..{n - 1} for the topic_embeddings_/c_tf_idf_ row "
        f"alignment used above - got a non-contiguous set, aborting to avoid silently comparing "
        f"the wrong rows."
    )

    top10_words = {tid: top_n_words_set(topic_model, tid, n=10) for tid in topic_ids}

    candidates = []
    for i in range(n):
        for j in range(i + 1, n):
            sem = float(semantic_sim[i, j])
            lex = float(lexical_sim[i, j])
            jac = jaccard(top10_words[i], top10_words[j])
            candidates.append({
                "topic_a": i,
                "topic_b": j,
                "semantic_sim": round(sem, 3),
                "lexical_sim": round(lex, 3),
                "top10_jaccard": round(jac, 3),
                "combined_score": round((sem + lex) / 2, 3),
                "count_a": int(info_df.loc[i, "Count"]),
                "count_b": int(info_df.loc[j, "Count"]),
                "words_a": _topic_snapshot(topic_model, i, top_n=10),
                "words_b": _topic_snapshot(topic_model, j, top_n=10),
            })
    candidates.sort(key=lambda c: c["combined_score"], reverse=True)
    top_candidates = candidates[:top_n]
    for c in top_candidates:
        c["examples_a"] = get_example_docs(topic_model, c["topic_a"], texts_list)
        c["examples_b"] = get_example_docs(topic_model, c["topic_b"], texts_list)
    return top_candidates, candidates


def run_detection():
    print("=" * 70)
    print("שלב 1: זיהוי זוגות topics כפולים/דומים מאוד (baseline, ללא שינוי במודל)")
    print("=" * 70)
    print(f"טוען את הבייסליין הנבחר מ-'{BASELINE_PATH}'...")
    topic_model = BERTopic.load(BASELINE_PATH, embedding_model=BASELINE_EMBEDDING_MODEL_NAME)
    print("טוען את טקסטי האימון (לצורך representative documents)...")
    texts_list = load_deduplicated_training_texts(verbose=False)
    assert len(texts_list) == len(topic_model.topics_), (
        f"Text/topic count mismatch: {len(texts_list)} texts vs. "
        f"{len(topic_model.topics_)} fitted topics - aborting."
    )

    n_topics = len(topic_model.get_topic_info()) - 1
    print(f"מחשב similarity על {n_topics} topics ({n_topics * (n_topics - 1) // 2} זוגות)...")
    top_candidates, all_candidates = find_candidate_pairs(topic_model, texts_list)

    all_scores = np.array([c["combined_score"] for c in all_candidates])
    print(f"\nהתפלגות combined_score (ממוצע semantic_sim + lexical_sim) על פני "
          f"{len(all_candidates)} זוגות:")
    percentiles = {}
    for pct in (50, 90, 95, 99, 99.5, 99.9):
        val = float(np.percentile(all_scores, pct))
        percentiles[str(pct)] = val
        print(f"  percentile {pct}: {val:.3f}")
    print(f"  max: {all_scores.max():.3f}")

    print(f"\nTop {len(top_candidates)} זוגות מועמדים (ממוין לפי combined_score):")
    for c in top_candidates:
        print(f"\n  Topic {c['topic_a']} (n={c['count_a']}) <-> Topic {c['topic_b']} (n={c['count_b']})")
        print(f"    semantic={c['semantic_sim']}  lexical={c['lexical_sim']}  "
              f"jaccard={c['top10_jaccard']}  combined={c['combined_score']}")
        print(f"    words_a: {c['words_a']}")
        print(f"    words_b: {c['words_b']}")
        print(f"    examples_a: {c['examples_a']}")
        print(f"    examples_b: {c['examples_b']}")

    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = os.path.join(REPORT_DIR, "expD_duplicate_topic_candidates.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "n_topics": n_topics,
                "n_pairs": len(all_candidates),
                "score_percentiles": percentiles,
                "proposed_combined_score_threshold": PROPOSED_COMBINED_SCORE_THRESHOLD,
                "top_candidates": top_candidates,
            },
            f, ensure_ascii=False, indent=2, default=str,
        )
    print(f"\nנשמרו {len(top_candidates)} המועמדים המובילים + התפלגות ה-scores ל-{out_path}")
    return texts_list


def snapshot_all_topics(topic_model):
    """Content-based snapshot (count + top-10 words) per topic id - used to verify, by CONTENT
    rather than numeric id, that non-merged topics survive a merge_topics() call unaffected (ids
    get renumbered by frequency after any merge)."""
    info_df = topic_model.get_topic_info()
    info_df = info_df[info_df["Topic"] != -1]
    snapshot = {}
    for tid in info_df["Topic"].tolist():
        count = int(info_df.loc[info_df["Topic"] == tid, "Count"].iloc[0])
        snapshot[int(tid)] = {
            "count": count,
            "top_words": tuple(_topic_snapshot(topic_model, tid, top_n=10)),
        }
    return snapshot


def run_merge_test(texts_list):
    print("\n\n" + "=" * 70)
    print("שלב 2: מיזוג ממוקד של זוג 'rulesbased' (עותק ניסויי נפרד - לא נוגע ב-baseline)")
    print("=" * 70)
    print(f"טוען עותק טרי (אובייקט נפרד) של הבייסליין מ-'{BASELINE_PATH}'...")
    topic_model = BERTopic.load(BASELINE_PATH, embedding_model=BASELINE_EMBEDDING_MODEL_NAME)
    assert len(texts_list) == len(topic_model.topics_), "Text/topic count mismatch"

    before_snapshot = snapshot_all_topics(topic_model)
    before_info = topic_model.get_topic_info()
    before_outlier_count = int(before_info.loc[before_info["Topic"] == -1, "Count"].iloc[0])
    before_n_topics = len(before_snapshot)
    before_doc_topics = list(topic_model.topics_)  # snapshot per-document topic assignment

    rulesbased_ids = find_rulesbased_topics(topic_model)
    print(f"\nזוג 'rulesbased' שזוהה: topics {rulesbased_ids}")
    assert len(rulesbased_ids) == 2, (
        f"Expected exactly 2 'rulesbased' topics on this baseline, found {rulesbased_ids} - "
        f"aborting merge test (unexpected corpus/model state)."
    )
    for tid in rulesbased_ids:
        print(f"  Topic {tid}: n={before_snapshot[tid]['count']}  words={before_snapshot[tid]['top_words']}")

    print("\nמריץ merge_topics() (in-place, על העותק הנוכחי בלבד)...")
    topic_model.merge_topics(texts_list, topics_to_merge=rulesbased_ids)
    print("merge_topics() הושלם.")

    after_snapshot = snapshot_all_topics(topic_model)
    after_info = topic_model.get_topic_info()
    after_outlier_count = int(after_info.loc[after_info["Topic"] == -1, "Count"].iloc[0])
    after_n_topics = len(after_snapshot)

    print(f"\nמספר Topics: {before_n_topics} -> {after_n_topics} (מצופה: בדיוק -1)")
    print(f"Outliers: {before_outlier_count} -> {after_outlier_count} "
          f"(מצופה: זהה - המיזוג לא נוגע ב-topic -1)")

    # Identify the merged topic by CONTENT (find_rulesbased_topics on the post-merge model),
    # NOT by matching the expected combined count - two unrelated topics can coincidentally share
    # the same document count, which would silently pick the wrong topic.
    merged_candidates = find_rulesbased_topics(topic_model)
    assert len(merged_candidates) == 1, (
        f"Expected exactly 1 'rulesbased' topic after merging, found {merged_candidates} - "
        f"merge_topics() may not have behaved as expected."
    )
    merged_tid = merged_candidates[0]
    expected_merged_count = before_snapshot[rulesbased_ids[0]]["count"] + before_snapshot[rulesbased_ids[1]]["count"]
    print(f"\nTopic הממוזג (id חדש אחרי renumbering: {merged_tid}): "
          f"n={after_snapshot[merged_tid]['count']} (מצופה {expected_merged_count}) "
          f"words={after_snapshot[merged_tid]['top_words']}")
    assert after_snapshot[merged_tid]["count"] == expected_merged_count, (
        f"Merged topic count {after_snapshot[merged_tid]['count']} != expected {expected_merged_count}"
    )

    # Compare every OTHER (non-merged) topic before vs. after, matched by ACTUAL DOCUMENT
    # MEMBERSHIP (the exact set of document indices assigned to it) - not by count or top-words,
    # which can collide or (as discovered while building this script) drift. Document membership
    # is the ground truth: merge_topics() only remaps documents between the merged topic ids, so
    # every non-merged topic's member-document set is mathematically guaranteed to be identical
    # before/after - this lets us prove that with certainty, then separately measure how much the
    # DISPLAYED representation (top-10 words) drifted for those provably-unchanged topics.
    after_doc_topics = list(topic_model.topics_)
    before_docs_by_topic = {}
    for i, tid in enumerate(before_doc_topics):
        if tid not in rulesbased_ids and tid != -1:
            before_docs_by_topic.setdefault(tid, set()).add(i)
    after_docs_by_topic = {}
    for i, tid in enumerate(after_doc_topics):
        if tid != merged_tid and tid != -1:
            after_docs_by_topic.setdefault(tid, set()).add(i)

    after_by_docset = {frozenset(docs): tid for tid, docs in after_docs_by_topic.items()}
    membership_preserved = 0
    word_drift_jaccards = []
    biggest_drift = []
    for tid, docs in before_docs_by_topic.items():
        after_tid = after_by_docset.get(frozenset(docs))
        if after_tid is None:
            continue  # should not happen - would mean a real (unexpected) membership change
        membership_preserved += 1
        before_words = set(before_snapshot[tid]["top_words"])
        after_words = set(after_snapshot[after_tid]["top_words"])
        j = jaccard(before_words, after_words)
        word_drift_jaccards.append(j)
        biggest_drift.append((j, tid, after_tid, before_snapshot[tid]["top_words"], after_snapshot[after_tid]["top_words"]))

    print(f"\nבדיקת שאר ה-{len(before_docs_by_topic)} Topics (לא-ממוזגים), לפי document membership בפועל:")
    print(f"  Topics עם document membership זהה לחלוטין לפני/אחרי: "
          f"{membership_preserved}/{len(before_docs_by_topic)} "
          f"(מוכיח שהמיזוג לא נגע באף topic אחר ברמת המסמכים)")
    if word_drift_jaccards:
        arr = np.array(word_drift_jaccards)
        exact_word_match = int((arr == 1.0).sum())
        print(f"  מתוכם, עם top-10 words זהה לחלוטין (אין 'drift' בייצוג): "
              f"{exact_word_match}/{len(arr)}")
        print(f"  Jaccard(top-10 words, לפני/אחרי) על אותם topics: "
              f"mean={arr.mean():.3f} median={np.median(arr):.3f} min={arr.min():.3f}")
        print(f"  (הסבר: אף מסמך לא זז, אבל ClassTfidfTransformer/MMR מחשבים מחדש את הדירוג "
              f"על כל הקורפוס אחרי כל merge - אז גם topics לא-קשורים עשויים לקבל top-words "
              f"מעט/הרבה שונות, למרות שאוכלוסיית המסמכים שלהם לא השתנתה כלל.)")
        biggest_drift.sort(key=lambda x: x[0])
        print(f"  3 ה-topics עם ה-drift הגדול ביותר בייצוג (document membership זהה, מילים שונות):")
        for j, tid, after_tid, before_w, after_w in biggest_drift[:3]:
            print(f"    topic {tid}->{after_tid} (jaccard={j:.3f}):")
            print(f"      לפני:  {before_w}")
            print(f"      אחרי:  {after_w}")

    os.makedirs(MERGE_EXPERIMENT_PATH, exist_ok=True)
    topic_model.save(MERGE_EXPERIMENT_PATH, serialization="safetensors", save_ctfidf=True)
    print(f"\nהמודל הממוזג נשמר בנפרד ל-'{MERGE_EXPERIMENT_PATH}' "
          f"(לא נדרס baseline_seeded ולא saved_topic_model_soft_v2).")

    print("\nמריץ ניתוח hard/soft agreement (analyze_soft_topic_quality, n=280, seed=42) על המודל הממוזג...")
    _, after_quality_summary, _, _ = run_analysis_with_retry(MERGE_EXPERIMENT_PATH)
    for fname in ("soft_topic_quality_full.csv", "soft_topic_quality_summary.json",
                  "soft_topic_cooccurrence.csv", "soft_topic_quality_examples.csv"):
        src_path = os.path.join(REPORT_DIR, fname)
        if os.path.exists(src_path):
            import shutil
            base, ext = os.path.splitext(fname)
            shutil.copy(src_path, os.path.join(REPORT_DIR, f"{base}.expD_merge_rulesbased{ext}"))

    with open(BASELINE_QUALITY_SNAPSHOT, "r", encoding="utf-8") as f:
        before_quality_summary = json.load(f)

    print("\nהשוואת hard/soft agreement, baseline (minilm_seed42) לעומת אחרי המיזוג:")
    before_agr = before_quality_summary.get("hard_soft_agreement_counts", {})
    after_agr = after_quality_summary.get("hard_soft_agreement_counts", {})
    print(f"  hard_soft_agreement_counts  before={before_agr}  after={after_agr}")
    print(f"  hard_is_outlier_pct         before={before_quality_summary.get('hard_is_outlier_pct')}  "
          f"after={after_quality_summary.get('hard_is_outlier_pct')}")
    before_case_pct = before_quality_summary.get("case_pct", {})
    after_case_pct = after_quality_summary.get("case_pct", {})
    print(f"  case_pct                    before={before_case_pct}  after={after_case_pct}")

    comparison = {
        "rulesbased_ids_before": rulesbased_ids,
        "merged_topic_id_after": merged_tid,
        "n_topics_before": before_n_topics,
        "n_topics_after": after_n_topics,
        "outlier_count_before": before_outlier_count,
        "outlier_count_after": after_outlier_count,
        "merged_topic_words_after": list(after_snapshot[merged_tid]["top_words"]),
        "merged_topic_count_after": after_snapshot[merged_tid]["count"],
        "other_topics_total": len(before_docs_by_topic),
        "other_topics_document_membership_preserved_count": membership_preserved,
        "other_topics_word_drift_jaccard_mean": float(np.mean(word_drift_jaccards)) if word_drift_jaccards else None,
        "other_topics_word_drift_jaccard_median": float(np.median(word_drift_jaccards)) if word_drift_jaccards else None,
        "other_topics_exact_word_match_count": int((np.array(word_drift_jaccards) == 1.0).sum()) if word_drift_jaccards else None,
        "quality_before_minilm_seed42": before_quality_summary,
        "quality_after_merge": after_quality_summary,
    }
    comparison_path = os.path.join(REPORT_DIR, "expD_merge_rulesbased_comparison.json")
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nהשוואה מלאה נשמרה ל-{comparison_path}")


def run():
    texts_list = run_detection()
    run_merge_test(texts_list)
    print("\n\nExperiment D הושלם. לא נגעו ב-fusion.py / train.py / checkpoints / "
          "soft_v2_baseline_seeded / saved_topic_model_soft_v2.")


if __name__ == "__main__":
    run()

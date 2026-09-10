"""Experiment D2: final check of whether the "rulesbased" merge (Experiment D, Stage 2) is safe
for the SOFT (multi-topic) distribution, not just for the hard cluster / topic-count / outlier
metrics already checked. Compares `models/experiments/soft_v2_baseline_seeded` (before) against
`models/experiments/soft_v2_expD_merge_rulesbased` (after) on the SAME n=280 quality sample
(`analyze_soft_topic_quality.py`, seed=42) used throughout Experiments A/A2/B/D.

Neither `soft_v2_baseline_seeded` nor `saved_topic_model_soft_v2` (production) is modified by this
script - read-only comparison of 2 already-saved models.

Question asked (verbatim from user): for texts that do NOT belong to either of the 2 merged
"rulesbased" topics, does merging them elsewhere in the topic space leave their OWN soft
distribution effectively unchanged, or does it perturb it in a way that would make the merge risky
to apply to a live soft-distribution classification feature?

Methodology:
1. Build a topic-id map baseline_id -> merged_id using the FULL TRAINING CORPUS's `.topics_`
   per-document assignment (document-membership-based, per the lesson learned in Experiment D:
   never match renumbered topic ids by count or label, only by the exact set of member documents).
   This also lets the merged pair fall out PROGRAMMATICALLY (the 2 baseline ids whose docsets don't
   individually match any single after-topic docset, because their union was merged into one new
   topic) - not hardcoded, so this script is not tied to already knowing which ids were merged.
2. Run `analyze_soft_topic_quality.analyze()` against BOTH models on the identical (same seed)
   n=280 stratified quality sample - gives hard_topic_id + top-3 soft topics/scores per text, per
   model.
3. Exclude any sampled text whose BASELINE hard topic id OR any of its baseline top-3 soft topic
   ids is one of the 2 merged "rulesbased" ids (these texts legitimately WILL change - that's the
   point of the merge, not a stability failure).
4. For the remaining ("unaffected-by-design") texts, using the id map from step 1 to translate
   baseline topic ids into their merged-model equivalents, compute:
     - top-1 soft topic same after mapping? (%)
     - top-3 soft topic SET overlap (Jaccard) after mapping
     - how much the top-1 raw/normalized score changed (delta)
     - how many texts have an UNCHANGED hard cluster (mapped baseline hard id == merged hard id)
       but a MEANINGFULLY CHANGED soft distribution anyway (top-3 set changed OR score delta above
       a threshold) - directly answers the "does the hard cluster staying the same guarantee a
       stable soft distribution" question.
   Saves curated "stable" and "changed" example rows (with real text) for manual inspection.

Run (from repo root): `python experiments/topic_modeling/experiment_d2_soft_stability_check.py`
"""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
from bertopic import BERTopic

# Moved out of src/ into experiments/ - add src/ and sibling experiment folders to sys.path so
# same-style flat imports (e.g. `from train_topics import ...`) keep working unmodified.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _rel_dir in ("src", "experiments/topic_modeling", "experiments/feature_ablation", "experiments/author_generalization"):
    _abs_dir = os.path.join(_REPO_ROOT, _rel_dir)
    if _abs_dir not in sys.path:
        sys.path.insert(0, _abs_dir)

from analyze_soft_topic_quality import analyze as run_soft_quality_analysis
from train_topics import load_deduplicated_training_texts

BASELINE_PATH = "models/experiments/soft_v2_baseline_seeded"
MERGE_PATH = "models/experiments/soft_v2_expD_merge_rulesbased"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
REPORT_DIR = "reports/results/profiler_prototype"
N_PER_NARRATIVE = 40  # matches all prior experiments' n=280 quality sample (7 narratives x 40)
# A soft-distribution change on an "unaffected" text is considered "meaningful" if the top-3 topic
# id SET changed after mapping, OR the top-1 normalized score moved by more than this amount.
SCORE_DELTA_THRESHOLD = 0.15


def build_topic_id_map(texts_list):
    """Loads both models fresh and maps every baseline topic id to its merged-model equivalent by
    matching EXACT document-membership sets (not count, not label - see module docstring). Also
    identifies the merged pair and the resulting merged id purely from this membership evidence
    (no hardcoded topic ids)."""
    baseline = BERTopic.load(BASELINE_PATH, embedding_model=EMBEDDING_MODEL_NAME)
    merged = BERTopic.load(MERGE_PATH, embedding_model=EMBEDDING_MODEL_NAME)

    before_topics = list(baseline.topics_)
    after_topics = list(merged.topics_)
    assert len(before_topics) == len(texts_list), (
        f"before_topics length {len(before_topics)} != texts_list length {len(texts_list)} - "
        "wrong corpus/order, cannot trust document-membership matching."
    )
    assert len(after_topics) == len(texts_list), (
        f"after_topics length {len(after_topics)} != texts_list length {len(texts_list)}"
    )

    before_docs = {}
    for i, tid in enumerate(before_topics):
        before_docs.setdefault(tid, set()).add(i)
    after_docs = {}
    for i, tid in enumerate(after_topics):
        after_docs.setdefault(tid, set()).add(i)

    after_by_docset = {frozenset(docs): tid for tid, docs in after_docs.items()}

    id_map = {}
    unmapped_before_ids = []
    for tid, docs in before_docs.items():
        after_tid = after_by_docset.get(frozenset(docs))
        if after_tid is not None:
            id_map[tid] = after_tid
        else:
            unmapped_before_ids.append(tid)

    merged_tid = None
    if len(unmapped_before_ids) == 2:
        union_docs = before_docs[unmapped_before_ids[0]] | before_docs[unmapped_before_ids[1]]
        merged_tid = after_by_docset.get(frozenset(union_docs))

    return id_map, unmapped_before_ids, merged_tid


def load_sample_and_compare():
    print("שלב 1: בונים מיפוי topic_id (baseline -> merged) לפי document membership בפועל "
          "(על קורפוס האימון המלא, 16062 טקסטים)...")
    texts_list = load_deduplicated_training_texts(verbose=False)
    id_map, unmapped_ids, merged_tid = build_topic_id_map(texts_list)
    print(f"  Topics לא ממופים ישירות (צפוי: 2, אלה שמוזגו): {unmapped_ids}")
    print(f"  ה-id של ה-topic הממוזג אחרי renumbering: {merged_tid}")
    print(f"  סה\"כ topics אחרים שמופו בהצלחה: {len(id_map)}")

    print("\nשלב 2: מריצים ניתוח soft quality (n=280, seed=42) על ה-baseline...")
    baseline_df, _, _, _ = run_soft_quality_analysis(n_per_narrative=N_PER_NARRATIVE, model_path=BASELINE_PATH)
    print("\nמריצים ניתוח soft quality (n=280, seed=42) זהה על המודל הממוזג...")
    merged_df, _, _, _ = run_soft_quality_analysis(n_per_narrative=N_PER_NARRATIVE, model_path=MERGE_PATH)

    # Both calls use the identical deterministic (seed=42) load_stratified_sample() - merge on
    # (narrative_name, text) to be robust rather than relying on row order.
    merged_cols = {c: f"after_{c}" for c in merged_df.columns if c not in ("narrative_name", "text")}
    merged_df = merged_df.rename(columns=merged_cols)
    combined = baseline_df.merge(merged_df, on=["narrative_name", "text"], how="inner")
    assert len(combined) == len(baseline_df) == 280, (
        f"expected 280/280/280 matched rows, got baseline={len(baseline_df)} "
        f"merged={len(merged_df)} combined={len(combined)}"
    )

    return combined, id_map, unmapped_ids, merged_tid


def _mapped(id_map, tid):
    if tid is None or (isinstance(tid, float) and np.isnan(tid)):
        return None
    return id_map.get(int(tid))


def run():
    combined, id_map, rulesbased_ids, merged_tid = load_sample_and_compare()

    def touches_rulesbased(row):
        ids = [row["hard_topic_id"], row["soft_top1_id"], row["soft_top2_id"], row["soft_top3_id"]]
        return any((pd.notna(i) and int(i) in rulesbased_ids) for i in ids)

    combined["baseline_touches_rulesbased"] = combined.apply(touches_rulesbased, axis=1)
    affected = combined[combined["baseline_touches_rulesbased"]]
    unaffected = combined[~combined["baseline_touches_rulesbased"]].copy()

    print(f"\nמתוך 280 הטקסטים במדגם: {len(affected)} שייכים (hard או soft top-3) לאחד "
          f"מ-2 ה-Topics שמוזגו (rulesbased ids {rulesbased_ids}) - אלה צפויים להשתנות, "
          f"לא נבדקים ליציבות. נותרו {len(unaffected)} טקסטים 'לא-אמורים-להיות-מושפעים'.")

    # Map baseline ids -> expected merged-model ids for the unaffected rows.
    for col in ("hard_topic_id", "soft_top1_id", "soft_top2_id", "soft_top3_id"):
        unaffected[f"expected_after_{col}"] = unaffected[col].apply(lambda t: _mapped(id_map, t))

    def top3_set(row, prefix=""):
        ids = [row[f"{prefix}soft_top1_id"], row[f"{prefix}soft_top2_id"], row[f"{prefix}soft_top3_id"]]
        return frozenset(int(i) for i in ids if pd.notna(i))

    top1_matches = 0
    jaccards = []
    top1_score_deltas = []
    hard_unchanged_but_soft_changed = 0
    n_hard_unchanged = 0
    stable_rows = []
    changed_rows = []

    for _, row in unaffected.iterrows():
        expected_top1 = row["expected_after_soft_top1_id"]
        actual_top1 = row["after_soft_top1_id"]
        top1_match = (
            pd.notna(expected_top1) and pd.notna(actual_top1)
            and int(expected_top1) == int(actual_top1)
        ) or (pd.isna(expected_top1) and pd.isna(actual_top1))
        if top1_match:
            top1_matches += 1

        expected_top3 = frozenset(
            int(id_map[int(t)]) for t in
            [row["soft_top1_id"], row["soft_top2_id"], row["soft_top3_id"]]
            if pd.notna(t) and int(t) in id_map
        )
        actual_top3 = top3_set(row, prefix="after_")
        union = expected_top3 | actual_top3
        jaccard = len(expected_top3 & actual_top3) / len(union) if union else 1.0
        jaccards.append(jaccard)

        score_before = row["soft_top1_score_norm"]
        score_after = row["after_soft_top1_score_norm"]
        if pd.notna(score_before) and pd.notna(score_after):
            delta = abs(float(score_before) - float(score_after))
            top1_score_deltas.append(delta)
        else:
            delta = None

        expected_hard = row["expected_after_hard_topic_id"]
        actual_hard = row["after_hard_topic_id"]
        hard_unchanged = (
            pd.notna(expected_hard) and pd.notna(actual_hard)
            and int(expected_hard) == int(actual_hard)
        ) or (pd.isna(expected_hard) and pd.isna(actual_hard))
        if hard_unchanged:
            n_hard_unchanged += 1
            soft_changed = (jaccard < 1.0) or (delta is not None and delta > SCORE_DELTA_THRESHOLD)
            if soft_changed:
                hard_unchanged_but_soft_changed += 1

        record = {
            "narrative_name": row["narrative_name"],
            "text": row["text"][:200],
            "baseline_hard_id": row["hard_topic_id"], "baseline_hard_label": row["hard_topic_label"],
            "expected_after_hard_id": expected_hard, "actual_after_hard_id": actual_hard,
            "baseline_top1_label": row["soft_top1_label"], "after_top1_label": row["after_soft_top1_label"],
            "top3_jaccard": round(jaccard, 3),
            "top1_score_before": score_before, "top1_score_after": score_after,
            "top1_score_delta": None if delta is None else round(delta, 3),
        }
        if jaccard == 1.0 and (delta is None or delta <= SCORE_DELTA_THRESHOLD):
            stable_rows.append(record)
        else:
            changed_rows.append(record)

    n = len(unaffected)
    jacc_arr = np.array(jaccards)
    delta_arr = np.array(top1_score_deltas) if top1_score_deltas else np.array([])

    print(f"\n=== יציבות ה-Soft Distribution עבור {n} הטקסטים הלא-אמורים-להיות-מושפעים ===")
    print(f"Top-1 soft topic נשאר זהה (אחרי מיפוי ה-id): {top1_matches}/{n} "
          f"({100*top1_matches/n:.1f}%)")
    print(f"Jaccard(top-3 soft topics, אחרי מיפוי) : mean={jacc_arr.mean():.3f} "
          f"median={np.median(jacc_arr):.3f} min={jacc_arr.min():.3f} "
          f"(1.0 = identical top-3 set): "
          f"{int((jacc_arr == 1.0).sum())}/{n} טקסטים עם top-3 זהה לחלוטין")
    if len(delta_arr):
        print(f"שינוי ב-top-1 normalized score: mean={delta_arr.mean():.3f} "
              f"median={np.median(delta_arr):.3f} max={delta_arr.max():.3f} "
              f"({int((delta_arr <= SCORE_DELTA_THRESHOLD).sum())}/{len(delta_arr)} "
              f"מתחת לסף {SCORE_DELTA_THRESHOLD})")
    print(f"\nHard cluster נשאר זהה (אחרי מיפוי) עבור {n_hard_unchanged}/{n} טקסטים.")
    print(f"מתוכם, כאלה שבכל זאת קיבלו שינוי משמעותי ב-Soft Distribution "
          f"(top-3 set שונה, או |Δscore|>{SCORE_DELTA_THRESHOLD}): "
          f"{hard_unchanged_but_soft_changed}/{n_hard_unchanged} "
          f"({100*hard_unchanged_but_soft_changed/n_hard_unchanged:.1f}%)" if n_hard_unchanged else "")

    print(f"\nסה\"כ: {len(stable_rows)}/{n} טקסטים יציבים לחלוטין "
          f"(top-3 זהה + Δscore<={SCORE_DELTA_THRESHOLD}), {len(changed_rows)}/{n} עם שינוי כלשהו.")

    print("\n--- 3 דוגמאות יציבות ---")
    for r in stable_rows[:3]:
        print(f"  [{r['narrative_name']}] before={r['baseline_top1_label']!r} "
              f"after={r['after_top1_label']!r} Δscore={r['top1_score_delta']}")
        print(f"    text: {r['text']}")

    print("\n--- 3 דוגמאות עם השינוי הגדול ביותר ---")
    changed_rows.sort(key=lambda r: (r["top1_score_delta"] or 0) + (1 - r["top3_jaccard"]), reverse=True)
    for r in changed_rows[:3]:
        print(f"  [{r['narrative_name']}] before={r['baseline_top1_label']!r} "
              f"after={r['after_top1_label']!r} jaccard={r['top3_jaccard']} "
              f"Δscore={r['top1_score_delta']}")
        print(f"    text: {r['text']}")

    os.makedirs(REPORT_DIR, exist_ok=True)
    out = {
        "n_sample_total": 280,
        "n_affected_by_merge": int(len(affected)),
        "n_unaffected_checked": int(n),
        "rulesbased_ids_baseline": [int(x) for x in rulesbased_ids],
        "merged_topic_id_after": int(merged_tid) if merged_tid is not None else None,
        "top1_soft_topic_identical_count": int(top1_matches),
        "top1_soft_topic_identical_pct": round(100 * top1_matches / n, 1) if n else None,
        "top3_jaccard_mean": float(jacc_arr.mean()) if len(jacc_arr) else None,
        "top3_jaccard_median": float(np.median(jacc_arr)) if len(jacc_arr) else None,
        "top3_identical_count": int((jacc_arr == 1.0).sum()) if len(jacc_arr) else None,
        "top1_score_delta_mean": float(delta_arr.mean()) if len(delta_arr) else None,
        "top1_score_delta_median": float(np.median(delta_arr)) if len(delta_arr) else None,
        "top1_score_delta_max": float(delta_arr.max()) if len(delta_arr) else None,
        "score_delta_threshold_used": SCORE_DELTA_THRESHOLD,
        "n_hard_cluster_unchanged": int(n_hard_unchanged),
        "n_hard_unchanged_but_soft_changed": int(hard_unchanged_but_soft_changed),
        "n_fully_stable": int(len(stable_rows)),
        "n_changed": int(len(changed_rows)),
        "stable_examples": stable_rows[:5],
        "changed_examples": changed_rows[:5],
    }
    out_path = os.path.join(REPORT_DIR, "expD2_soft_stability_check.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nתוצאות מלאות נשמרו ל-{out_path}")
    print("\nExperiment D2 הושלם. לא נגעו ב-fusion.py / train.py / checkpoints / "
          "saved_topic_model_soft_v2. soft_v2_baseline_seeded ו-soft_v2_expD_merge_rulesbased "
          "נטענו read-only בלבד.")


if __name__ == "__main__":
    run()

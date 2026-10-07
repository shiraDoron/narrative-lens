"""
Root-Cause Audit: why does entity-masking augmentation hurt IDF so strongly?
=============================================================================
Follow-up to EXPERIMENTS.md section 23. Section 23 found `sbert_masked_aug`/
`sbert_masked_aug_soft_topic` trade IDF's recall for Bernie's (63.5%->39.0%/42.0% vs.
24.5%->40.5%/39.0%) - a real, unresolved cost, not a minor side effect (average recall for
`sbert_masked_aug_soft_topic` is actually BELOW both `sbert_original` and `sbert_soft_topic`;
see the corrected section 23 conclusion). This is a read-only AUDIT (no new training) that asks:
which IDF test examples get newly wrong under `sbert_masked_aug` that `sbert_original` AND
`sbert_soft_topic` both got right, and what do those regressions have in common (entity type,
entity count, which entities were masked, where the prediction goes)?

This determines whether Experiment 24 ("Selective Entity-Masking Augmentation" - masking only
specific entity types instead of all of them) is worth running at all: if IDF's regressions are
concentrated in a small number of entity types, selective masking of the OTHER types is a
plausible fix; if regressions are diffuse across all entity types (or unrelated to entities
altogether), selective masking by type is unlikely to help and the entity-intervention line
should stop here instead of continuing into an unsupported tuning exercise.

Method:
  - All 4 models are evaluated on the SAME 200 IDF test rows (`orig_cache["test"]`, the
    untouched, original-only test split reused throughout section 23) - a fair, single-source
    comparison, no re-training, no re-encoding.
  - `sbert_original`/`sbert_soft_topic` checkpoints are loaded (eval-only) from Section 19's own
    directory (`models/experiments/narrative_ablation_loao/`, unmodified).
  - `sbert_masked_aug`/`sbert_masked_aug_soft_topic` checkpoints are loaded (eval-only) from
    Section 23's directory (`models/experiments/narrative_entity_masking_augmentation/`,
    unmodified).
  - Regression set := {row : sbert_original correct AND sbert_soft_topic correct AND
    sbert_masked_aug WRONG}. Both "masked_aug" and "masked_aug_soft_topic" predictions are
    recorded for every regression row for completeness, but membership in the regression set
    is defined by `sbert_masked_aug` alone (matches the user's stage-1 request exactly - "masked
    augmentation" errs while original/soft succeed).
  - Entities for each regression row are extracted FRESH from the original text via the same
    pipeline used to build the masking cache in section 21
    (`EntityAnalysisPipeline.extract_raw_entities()` + `reconstruct_fragmented_entities()`,
    both unmodified) - not re-approximated from the masked-text cache, so entity
    type/count/boundary is exact for this analysis.
  - As a baseline for comparison, the SAME entity extraction is run over all 200 IDF test rows
    (not just the regression set), so entity-type prevalence in the regression set can be
    compared against the corpus-wide baseline rather than read in isolation.

Run (from repo root):
    python experiments/author_generalization/narrative_idf_masking_regression_audit.py
"""
import json
import os
import sys

import pandas as pd
import torch

from narrative_lens.config import NARRATIVES
from narrative_lens.train import load_raw_data, split_leave_one_author
from narrative_lens.features.ner import EntityAnalysisPipeline, reconstruct_fragmented_entities

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from narrative_ablation_loao import AblationDetector  # noqa: E402

AUTHOR = "IDF"
ORIGINAL_CACHE_FILE = f"data/cache/cached_features_ablation_loao_{AUTHOR}.pt"

MODELS = {
    "sbert_original": {
        "checkpoint": f"models/experiments/narrative_ablation_loao/sbert_only_{AUTHOR}.pth",
        "arms": set(),
    },
    "sbert_soft_topic": {
        "checkpoint": f"models/experiments/narrative_ablation_loao/sbert_soft_topic_{AUTHOR}.pth",
        "arms": {"soft_topic"},
    },
    "sbert_masked_aug": {
        "checkpoint": f"models/experiments/narrative_entity_masking_augmentation/sbert_masked_aug_{AUTHOR}.pth",
        "arms": set(),
    },
    "sbert_masked_aug_soft_topic": {
        "checkpoint": f"models/experiments/narrative_entity_masking_augmentation/sbert_masked_aug_soft_topic_{AUTHOR}.pth",
        "arms": {"soft_topic"},
    },
}

REPORT_DIR = "artifacts/experiments/narrative_idf_masking_regression_audit"
SAMPLE_SIZE = 30

IDF_TRUE_NARRATIVE_IDX = NARRATIVES.index("Zionist")


def load_model(checkpoint_path, arms, bertopic_vec_size, sbert_dim):
    detector = AblationDetector(arms, ner_vocab_size=1, srl_vocab_size=1,
                                 bertopic_vec_size=bertopic_vec_size, sbert_dim=sbert_dim)
    detector.load_state_dict(torch.load(checkpoint_path))
    detector.eval()
    return detector


def predict_all(detector, test_features):
    preds = []
    with torch.no_grad():
        for features, _ in test_features:
            probs = detector.classify_features(features)
            if probs.dim() == 1:
                probs = probs.unsqueeze(0)
            preds.append(int(torch.argmax(probs, dim=-1).item()))
    return preds


def main():
    print(f"Loading original per-author cache for '{AUTHOR}' (test split, original/unmasked text)...")
    orig_cache = torch.load(ORIGINAL_CACHE_FILE, weights_only=False)
    test_features = orig_cache["test"]
    true_labels = [label for _, label in test_features]
    meta = orig_cache["_meta"]
    bertopic_vec_size, sbert_dim = meta["bertopic_vec_size"], meta["sbert_dim"]

    print(f"Rebuilding fresh IDF test split (for raw text) via split_leave_one_author()...")
    df = load_raw_data()
    _, _, test_data = split_leave_one_author(df, AUTHOR)
    test_data = test_data.reset_index(drop=True)
    test_data["text"] = test_data["text"].astype(str).str.slice(0, 3000)
    fresh_labels = test_data["label"].astype(int).tolist()
    if fresh_labels != true_labels or len(fresh_labels) != len(true_labels):
        raise RuntimeError(
            "Alignment check FAILED: fresh split_leave_one_author() test labels don't match "
            f"'{ORIGINAL_CACHE_FILE}' test labels row-for-row. Refusing to proceed."
        )
    print(f"Alignment verified: {len(test_data)} test rows, labels match row-for-row.")

    preds = {}
    for name, cfg in MODELS.items():
        print(f"Loading checkpoint for '{name}' from '{cfg['checkpoint']}' (eval-only)...")
        detector = load_model(cfg["checkpoint"], cfg["arms"], bertopic_vec_size, sbert_dim)
        preds[name] = predict_all(detector, test_features)

    n = len(true_labels)
    for name, p in preds.items():
        acc = sum(1 for t, x in zip(true_labels, p) if t == x) / n
        print(f"  Sanity check - '{name}' test accuracy: {acc * 100:.1f}% (should match section 23's numbers)")

    print("\nLoading BERT-NER model (dslim/bert-base-NER) for fresh entity extraction on IDF test rows...")
    ner_analyzer = EntityAnalysisPipeline()

    def extract_entities(text):
        raw = ner_analyzer.extract_raw_entities(text)
        return reconstruct_fragmented_entities(raw, text)

    print(f"Extracting entities for all {n} IDF test rows (baseline set)...")
    all_entities = [extract_entities(t) for t in test_data["text"].tolist()]

    baseline_type_counts = {}
    baseline_rows_with_type = {}
    for ents in all_entities:
        types_in_row = set()
        for e in ents:
            baseline_type_counts[e["entity_group"]] = baseline_type_counts.get(e["entity_group"], 0) + 1
            types_in_row.add(e["entity_group"])
        for t in types_in_row:
            baseline_rows_with_type[t] = baseline_rows_with_type.get(t, 0) + 1

    regression_idx = [
        i for i in range(n)
        if preds["sbert_original"][i] == true_labels[i]
        and preds["sbert_soft_topic"][i] == true_labels[i]
        and preds["sbert_masked_aug"][i] != true_labels[i]
    ]
    print(f"\nRegression set (original correct AND soft_topic correct AND masked_aug WRONG): "
          f"{len(regression_idx)} / {n} IDF test rows.")

    also_wrong_with_soft = sum(
        1 for i in regression_idx if preds["sbert_masked_aug_soft_topic"][i] != true_labels[i]
    )
    print(f"  Of these, {also_wrong_with_soft}/{len(regression_idx)} are ALSO wrong under "
          f"masked_aug_soft_topic (i.e. adding Soft Topics does not recover them); "
          f"{len(regression_idx) - also_wrong_with_soft}/{len(regression_idx)} are recovered by "
          f"adding the Soft Topic arm.")

    reg_type_counts = {}
    reg_rows_with_type = {}
    reg_entity_count_hist = {}
    reg_pred_narrative_counts = {}
    rows = []
    for i in regression_idx:
        ents = all_entities[i]
        types_in_row = set()
        for e in ents:
            reg_type_counts[e["entity_group"]] = reg_type_counts.get(e["entity_group"], 0) + 1
            types_in_row.add(e["entity_group"])
        for t in types_in_row:
            reg_rows_with_type[t] = reg_rows_with_type.get(t, 0) + 1
        reg_entity_count_hist[len(ents)] = reg_entity_count_hist.get(len(ents), 0) + 1

        pred_narrative = NARRATIVES[preds["sbert_masked_aug"][i]]
        reg_pred_narrative_counts[pred_narrative] = reg_pred_narrative_counts.get(pred_narrative, 0) + 1

        rows.append({
            "row_idx": i,
            "text": test_data["text"].iloc[i],
            "n_entities": len(ents),
            "entities": "; ".join(f"{e['entity_group']}:{e['text']}" for e in ents) or "(none)",
            "entity_types_present": ",".join(sorted(types_in_row)) or "(none)",
            "true_narrative": NARRATIVES[true_labels[i]],
            "pred_sbert_original": NARRATIVES[preds["sbert_original"][i]],
            "pred_sbert_soft_topic": NARRATIVES[preds["sbert_soft_topic"][i]],
            "pred_sbert_masked_aug": NARRATIVES[preds["sbert_masked_aug"][i]],
            "pred_sbert_masked_aug_soft_topic": NARRATIVES[preds["sbert_masked_aug_soft_topic"][i]],
        })

    reg_df = pd.DataFrame(rows)
    os.makedirs(REPORT_DIR, exist_ok=True)
    full_path = os.path.join(REPORT_DIR, "idf_masked_aug_regressions_full.csv")
    reg_df.to_csv(full_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved full regression set ({len(reg_df)} rows) to '{full_path}'.")

    sample_df = reg_df.head(SAMPLE_SIZE)
    sample_path = os.path.join(REPORT_DIR, "idf_masked_aug_regressions_sample.csv")
    sample_df.to_csv(sample_path, index=False, encoding="utf-8-sig")
    print(f"Saved qualitative sample ({len(sample_df)} rows) to '{sample_path}'.")

    print("\n" + "=" * 100)
    print("ENTITY-TYPE SUMMARY (regression set vs. full IDF test-set baseline)")
    print("=" * 100)
    all_types = sorted(set(baseline_type_counts) | set(reg_type_counts))
    summary_rows = []
    for t in all_types:
        summary_rows.append({
            "entity_type": t,
            "regression_rows_containing_type": reg_rows_with_type.get(t, 0),
            "regression_pct_of_regressions": (
                100 * reg_rows_with_type.get(t, 0) / len(regression_idx) if regression_idx else 0.0
            ),
            "regression_total_entity_mentions": reg_type_counts.get(t, 0),
            "baseline_rows_containing_type": baseline_rows_with_type.get(t, 0),
            "baseline_pct_of_all_200": 100 * baseline_rows_with_type.get(t, 0) / n,
            "baseline_total_entity_mentions": baseline_type_counts.get(t, 0),
        })
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    summary_path = os.path.join(REPORT_DIR, "entity_type_summary.csv")
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved entity-type summary to '{summary_path}'.")

    print("\nEntity-count histogram in regression set (n_entities -> n_rows):")
    for k in sorted(reg_entity_count_hist):
        print(f"  {k} entities: {reg_entity_count_hist[k]} rows")

    print("\nWhere masked_aug's predictions go for the regression set (true label is always Zionist):")
    for narrative, count in sorted(reg_pred_narrative_counts.items(), key=lambda kv: -kv[1]):
        print(f"  -> {narrative}: {count} ({100 * count / len(regression_idx):.1f}%)")

    audit_summary = {
        "author": AUTHOR,
        "n_test": n,
        "n_regressions": len(regression_idx),
        "pct_regressions_of_test": len(regression_idx) / n,
        "n_regressions_also_wrong_with_soft_topic": also_wrong_with_soft,
        "n_regressions_recovered_by_soft_topic": len(regression_idx) - also_wrong_with_soft,
        "entity_type_summary": summary_rows,
        "entity_count_histogram": reg_entity_count_hist,
        "masked_aug_prediction_targets": reg_pred_narrative_counts,
    }
    audit_json_path = os.path.join(REPORT_DIR, "audit_summary.json")
    with open(audit_json_path, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved audit summary JSON to '{audit_json_path}'.")


if __name__ == "__main__":
    main()

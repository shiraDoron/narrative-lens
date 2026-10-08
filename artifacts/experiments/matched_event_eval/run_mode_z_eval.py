"""Matched-event Mode Z eval runner (reconstructed).

Inputs:
  - Suite pairs: artifacts/experiments/matched_event_eval/pairs_<event>.csv
    (columns include pair_id, train_author, train_narrative, test_author,
    test_narrative, n_test) and suite_<event>.csv rows per suite_spec.json.
  - Frozen confirmatory checkpoints for the 14 fresh authors in
    models/experiments/narrative_fresh_author_confirmatory/
    (variants Z_sbert_original, Z_sbert_soft_topic,
    Z_sbert_person_misc_masked_aug_soft_topic).
  - SBERT backbone sentence-transformers/all-MiniLM-L6-v2 + soft topic table
    from models/experiments/soft_v2_baseline_seeded.

Outputs:
  - artifacts/experiments/matched_event_eval/matched_eval_results.json
    (per-pair modes, suite summaries, overall_matched, mismatched_loao_reference).

Seed: 42.

Method: frozen-checkpoint batched classify_features-equivalent eval over suite
pairs. Mode Z trains nothing: for each pair, the test author's frozen
checkpoint scores the test author's suite rows; uncovered pairs (test author
has no frozen checkpoint, e.g. all of event_russia_ukraine_2026-02) carry
empty modes by definition. Metric: true-narrative recall + predicted-label
histogram per pair, then mean recall / mean gap vs random-split baseline.

Dim note (from results notes): the spec text calls det.mlp on a raw
sbert+soft concat, which mismatches checkpoint dims (391 vs 667); this runner
uses the architecture-faithful classify_features-equivalent path instead
(batched [sbert|soft@table] -> mlp, verified equal to per-row
classify_features on 10 PressTV rows: MATCH). gensim is absent from the venv
and uninstallable (no wheel build); an import-only stub in /tmp was used and
is never touched by the soft-topic path.

Reconstruction source: matched_eval_results.json (summaries + notes),
suite_spec.json (pairing_instructions), narrative_fresh_author_confirmatory.py
build_variant_features/train_variant.
"""
from __future__ import annotations

import argparse
import json

SEED = 42
SUITE_DIR = "artifacts/experiments/matched_event_eval"
CHECKPOINT_DIR = "models/experiments/narrative_fresh_author_confirmatory"
RESULTS_FILE = "artifacts/experiments/matched_event_eval/matched_eval_results.json"
VARIANTS = (
    "Z_sbert_original",
    "Z_sbert_soft_topic",
    "Z_sbert_person_misc_masked_aug_soft_topic",
)


def run_mode_z_eval(seed=SEED, dry_run=False):
    # TODO(unverifiable): exact random-split baseline recall values used for
    # gap_vs_random_split_pp per pair are not restated in the results file;
    # they come from the confirmatory/fusion baselines.
    # TODO(unverifiable): eval batch size for the 12.8-minute Mode Z pass is
    # not logged; behavior is batch-size invariant (batched == per-row).
    _ = (seed, VARIANTS, CHECKPOINT_DIR, SUITE_DIR)
    if dry_run:
        return {"seed": seed, "variants": list(VARIANTS)}
    raise NotImplementedError(
        "Reconstructed spec only; wire frozen-checkpoint batched "
        "classify_features-equivalent scoring over suite pairs here."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out = run_mode_z_eval(args.seed, args.dry_run)
    if args.dry_run:
        print(f"dry-run ok: {json.dumps(out)}")


if __name__ == "__main__":
    main()

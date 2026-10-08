"""Matched-event Mode T sampled eval runner (reconstructed).

Inputs:
  - Suite pairs: artifacts/experiments/matched_event_eval/pairs_<event>.csv
    (columns include pair_id, train_author, train_narrative, test_author,
    test_narrative, train_n/test_n) and suite_<event>.csv rows per
    suite_spec.json.
  - Mode Z reference: artifacts/experiments/matched_event_eval/
    matched_eval_results.json (variant Z_sbert_soft_topic, 196 covered
    pairs, matched mean gap -36.3pp) for the on-sample comparison.

Outputs:
  - artifacts/experiments/matched_event_eval/mode_t_sampled/
    mode_t_results.json (per-pair mode_T_recall, gaps, pred_hist;
    summary, sampling, hyperparams, mode_Z_reference, verdict).

Seed: 42.

Method: per sampled pair, fresh-train sbert_only on the train author's
suite rows only (85/15 train/val split, seed 42), then score the test
author's suite rows for true-narrative recall + predicted-label
histogram. Sampling: 40 undirected author pairs, min-1 per suite plus
largest-remainder proportional to covered-pair counts (seed 42 choice
without replacement per suite); direction per undirected pair prefers
the Mode-Z-covered test author for direct comparability, else random
(seed 42); all cells >=30 texts verified from pairs CSV train_n/test_n.

Reconstruction source: mode_t_results.json (summary + sampling +
hyperparams + mode_Z_reference + per-pair fields).
"""
from __future__ import annotations

import argparse
import json

SEED = 42
SUITE_DIR = "artifacts/experiments/matched_event_eval"
RESULTS_FILE = (
    "artifacts/experiments/matched_event_eval/mode_t_sampled/mode_t_results.json"
)
VARIANT = "sbert_only"
EPOCHS = 20
BATCH = 16
LR = 0.001
PATIENCE = 3
HIDDEN = 128
DROPOUT = 0.3
BACKBONE = "sentence-transformers/all-MiniLM-L6-v2"
N_PAIRS = 40


def run_mode_t_sampled(seed=SEED, dry_run=False):
    # TODO(unverifiable): exact per-pair train/val row lists (85/15 split of
    # the train-author suite rows) are not logged in the results file; only
    # the split rule (seed 42) and n_train per pair are recorded.
    # TODO(unverifiable): the sampled pair_id list per suite (seed 42 choice
    # without replacement) is recorded only as outputs in mode_t_results.json
    # pairs, not as the RNG draw sequence; resampling needs the pairs CSV row
    # order plus the exact RNG call order, which are not logged.
    # TODO(unverifiable): per-pair sbert_only random-baseline recall values
    # used for mode_T_gap_vs_sbert_only_random_pp are stored per pair but
    # their source run (which random-split checkpoint/seed) is not stated.
    # TODO(unverifiable): training harness details (optimizer, train_variant
    # entry point, eval batch size, device) are not logged beyond
    # EPOCHS/BATCH/lr/patience/hidden/dropout/backbone.
    _ = (seed, VARIANT, EPOCHS, BATCH, LR, PATIENCE, HIDDEN, DROPOUT,
         BACKBONE, SUITE_DIR, N_PAIRS)
    if dry_run:
        return {"seed": seed, "variant": VARIANT, "n_pairs": N_PAIRS}
    raise NotImplementedError(
        "Reconstructed spec only; wire per-pair fresh sbert_only training "
        "on train-author suite rows + test-author recall scoring here."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out = run_mode_t_sampled(args.seed, args.dry_run)
    if args.dry_run:
        print(f"dry-run ok: {json.dumps(out)}")


if __name__ == "__main__":
    main()

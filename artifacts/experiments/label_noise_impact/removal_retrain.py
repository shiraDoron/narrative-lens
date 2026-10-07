"""Removal-retrain runner (reconstructed).

Inputs:
  - Raw corpus via narrative_lens.train.load_raw_data (four CSVs + author_source).
  - Spec: artifacts/experiments/label_noise_impact/retrain_protocol.json
    (protocol_version 1.0-frozen; EXCLUDED_ACCOUNTS = OpenSourceIntel,
    ResistanceNewsNetwork; 202/16510 rows removed; test splits unchanged).
  - Baseline arm: experiments/author_generalization/narrative_ablation_loao.py
    sbert_only-equivalent (SBERT-only, no engineered arms).

Outputs:
  - artifacts/experiments/label_noise_impact/removal_retrain_results.json
  - artifacts/experiments/label_noise_impact/confusion_matrix_sbert_only_*_removal_test.csv

Seed: 42. Hyperparams: EPOCHS=20, BATCH_SIZE=16, LR=0.001, patience=3,
dropout=0.3, hidden=128, backbone sentence-transformers/all-MiniLM-L6-v2.

Method: monkeypatch-style exclusion filter (or equivalent code hook in
load_raw_data per protocol: df = df[~df["author_source"].isin(EXCLUDED)]),
then 3 LOAO sbert_only runs for held-out authors IDF, MariaZakharova,
BernieSanders. Held-out authors are disjoint from the exclusion set so test
rows are byte-identical before/after (verified multiset + order).

Reconstruction source: retrain_protocol.json (spec) + removal_retrain_results.json
commands + narrative_ablation_loao.py train_variant.
"""
from __future__ import annotations

import argparse
import json

SEED = 42
EXCLUDED_ACCOUNTS = ["OpenSourceIntel", "ResistanceNewsNetwork"]
HELD_OUT_AUTHORS = ("IDF", "MariaZakharova", "BernieSanders")
VARIANT = "sbert_only"
EPOCHS = 20
BATCH_SIZE = 16
LR = 0.001
PATIENCE = 3
PROTOCOL_FILE = "artifacts/experiments/label_noise_impact/retrain_protocol.json"
RESULTS_FILE = "artifacts/experiments/label_noise_impact/removal_retrain_results.json"


def apply_exclusion_filter(df, excluded=EXCLUDED_ACCOUNTS):
    """Drop every corpus row whose author_source is in the exclusion set."""
    return df[~df["author_source"].isin(excluded)].reset_index(drop=True)


def run_removal_retrain(seed=SEED, dry_run=False):
    # TODO(unverifiable): whether the original /tmp runner used a true
    # monkeypatch of load_raw_data at runtime or the in-file edit described in
    # protocol code_hook is not logged; both are equivalent given identical
    # predicate and both are accepted by the spec.
    # TODO(unverifiable): exact per-author train/val row counts beyond the
    # results JSON and the val split call path (split_data seed 42) details
    # rely on narrative_lens.train internals, not re-stated here.
    from narrative_lens.train import load_raw_data, split_leave_one_author  # noqa: F401

    commands = [
        f"removal-retrain: split_leave_one_author(author={a}) on corpus minus "
        f"{EXCLUDED_ACCOUNTS}; train_variant('{VARIANT}', set(), seed={seed}, "
        f"EPOCHS={EPOCHS}, BATCH={BATCH_SIZE}, lr={LR}, patience={PATIENCE})"
        for a in HELD_OUT_AUTHORS
    ]
    if dry_run:
        return {"seed": seed, "commands": commands}
    raise NotImplementedError(
        "Reconstructed spec only; wire load_raw_data + exclusion filter + "
        "3x sbert_only train_variant runs here."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out = run_removal_retrain(args.seed, args.dry_run)
    if args.dry_run:
        print(f"dry-run ok: {json.dumps(out)}")


if __name__ == "__main__":
    main()

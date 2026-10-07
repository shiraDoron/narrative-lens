"""Entity attribution runner (reconstructed).

Inputs:
  - Frozen sbert_original checkpoints in
    models/experiments/narrative_fresh_author_confirmatory/
    (one per author).
  - Test rows + cached NER spans:
    artifacts/experiments/entity_attribution/test_entities.json
    (fields per row: author, narrative, label, text, entities).
  - narrative_lens.features.ner: extract_raw_entities,
    reconstruct_fragmented_entities, swap_entities.

Outputs:
  - artifacts/experiments/entity_attribution/attribution_results.json
  - artifacts/experiments/entity_attribution/per_author_attribution.csv
  - Protocol fields in attribution_results.json are the spec.

Seed: 42. CPU only.

Method (from results protocol):
  - NER with dslim/bert-base-NER via extract_raw_entities +
    reconstruct_fragmented_entities (ner_extract.log wall time ~22.5 min).
  - All same-type spans replaced per row via swap_entities; donor resampled
    up to 8 tries to differ from original.
  - Cross donors: opposing narrative, same entity_group
    (Zionist<->Resistance, Russian<->Ukrainian, Western->Russian,
    Right-wing<->Left-wing; fallback any-other-narrative same group).
  - Placebo donors: same narrative, same entity_group.
  - flip = predicted narrative on swapped text differs from prediction on
    original text. ACE = flip_rate_cross - flip_rate_placebo on paired rows.
  - LOAO gap = 1 - sbert_original recall_true_narrative; report Pearson r and
    Spearman rho of per-author ACE vs gap.

Reconstruction source: attribution_results.json protocol block, ner_extract.log,
attribution_run.log, src/narrative_lens/features/ner.py.
"""
from __future__ import annotations

import argparse
import json
import random

SEED = 42
CPU_ONLY = True
CHECKPOINT_DIR = "models/experiments/narrative_fresh_author_confirmatory"
ENTITIES_FILE = "artifacts/experiments/entity_attribution/test_entities.json"
RESULTS_FILE = "artifacts/experiments/entity_attribution/attribution_results.json"

CROSS_DONORS = {
    "Zionist": "Resistance",
    "Resistance": "Zionist",
    "Russian": "Ukrainian",
    "Ukrainian": "Russian",
    "Western": "Russian",
    "Right-wing": "Left-wing",
    "Left-wing": "Right-wing",
}

MAX_DONOR_TRIES = 8


def load_rows(path=ENTITIES_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pick_donor(entity_group, pool, rng, exclude_text=None):
    """Sample a same-group donor string differing from the original span."""
    candidates = [e["text"] for e in pool if e.get("entity_group") == entity_group]
    # TODO(unverifiable): exact donor-pool iteration order and tie-breaking
    # across qualifying rows was in /tmp and is not logged.
    rng.shuffle(candidates)
    for cand in candidates[:MAX_DONOR_TRIES]:
        if cand != exclude_text:
            return cand
    return None


def run_attribution(checkpoint_dir=CHECKPOINT_DIR, seed=SEED, dry_run=False):
    # TODO(unverifiable): exact checkpoint filename template and SBERT backbone
    # load call lived in the lost /tmp runner; expected pattern is
    # sbert_original_<author>.pth with AblationDetector(arms=set()).
    # TODO(unverifiable): SBERT encode / inference batch sizes for the 2912x3
    # swap pass are not in the logs.
    from narrative_lens.features.ner import (  # noqa: F401
        reconstruct_fragmented_entities,
        swap_entities,
    )

    rng = random.Random(seed)
    rows = load_rows()
    if dry_run:
        return {"n_rows": len(rows), "seed": seed, "checkpoint_dir": checkpoint_dir}
    _ = rng
    raise NotImplementedError(
        "Reconstructed spec only; wire frozen-checkpoint load + "
        "cross/placebo swap_entities loop here."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint-dir", default=CHECKPOINT_DIR)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out = run_attribution(args.checkpoint_dir, args.seed, args.dry_run)
    if args.dry_run:
        print(f"dry-run ok: {json.dumps(out)}")


if __name__ == "__main__":
    main()

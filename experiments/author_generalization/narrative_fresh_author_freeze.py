"""
Narrative Classification — Fresh-Author Confirmatory Set Freeze (Experiment 25, Phase 1b)
============================================================================================
PHASE 1b ONLY: deterministically freezes the 14-author confirmatory evaluation set for
Experiment 25, from the eligible pool already computed by narrative_fresh_author_audit.py.
No training, no model loading, no performance-based selection anywhere in this script.

Eligibility (pre-registered, decided before this script ever looks at any author's identity
beyond the audit table already produced in Phase 1):
  1. n_examples >= 200.
  2. Not IDF / MariaZakharova / BernieSanders (already-used LOAO test authors, Experiments
     18-24).
  3. Not a Gemini/GPT synthetic placeholder author.
  4. Not any author that was used to make a decision in Experiments 19-24 (in this codebase,
     that set is exactly {IDF, MariaZakharova, BernieSanders} - see
     narrative_fresh_author_audit.py's docstring for the disclosed operational definition of
     "used").

Selection: within each of the 7 narratives, 2 authors are drawn UNIFORMLY AT RANDOM (no
replacement) from that narrative's eligible pool, using a single fixed, documented seed
(42). The eligible pool is sorted alphabetically by author_source before sampling so the
result is reproducible independent of any incidental DataFrame row order. No author is ever
swapped after being drawn, regardless of any later result.

Output (frozen, do not edit by hand after this script is run):
    artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json
      - eligible_pool: every author in the >=200 / non-excluded / non-synthetic pool, with
        narrative + n_examples (i.e. the full pre-selection candidate set, for auditability).
      - random_seed: 42
      - selected_authors: the frozen 14, each with narrative + n_examples.

Run (from repo root):
    python experiments/author_generalization/narrative_fresh_author_freeze.py
"""
import json
import os
import random

import pandas as pd

from narrative_lens.train import load_raw_data, is_synthetic_author

REPORT_DIR = "artifacts/experiments/narrative_fresh_author_audit"
FROZEN_SET_FILE = os.path.join(REPORT_DIR, "fresh_author_confirmatory_set.json")

EXCLUDED_AUTHORS = {"IDF", "MariaZakharova", "BernieSanders"}
MIN_EXAMPLES = 200
N_PER_NARRATIVE = 2
SEED = 42

NARRATIVES_ORDER = (
    "Zionist", "Resistance", "Western", "Russian", "Ukrainian", "Right-wing", "Left-wing",
)


def build_eligible_pool(df):
    rows = []
    grouped = df.groupby("author_source", dropna=False)
    for author_source, g in grouped:
        if is_synthetic_author(author_source):
            continue
        if author_source in EXCLUDED_AUTHORS:
            continue
        narratives = g["narrative_name"].unique().tolist()
        if len(narratives) != 1:
            # Every author in this corpus maps to exactly one narrative; guard against a
            # silent multi-narrative author being fed into per-narrative sampling.
            continue
        n_examples = len(g)
        if n_examples < MIN_EXAMPLES:
            continue
        rows.append({
            "author_source": author_source,
            "narrative": narratives[0],
            "n_examples": n_examples,
        })
    rows.sort(key=lambda r: r["author_source"])  # deterministic order before seeded sampling
    return rows


def select_frozen_authors(eligible_pool, seed=SEED, n_per_narrative=N_PER_NARRATIVE):
    rng = random.Random(seed)
    selected = []
    for narrative in NARRATIVES_ORDER:
        candidates = [r for r in eligible_pool if r["narrative"] == narrative]
        if len(candidates) < n_per_narrative:
            raise RuntimeError(
                f"Only {len(candidates)} eligible author(s) for narrative '{narrative}' - "
                f"need at least {n_per_narrative}."
            )
        chosen = rng.sample(candidates, n_per_narrative)
        selected.extend(chosen)
    return selected


def main():
    df = load_raw_data()
    eligible_pool = build_eligible_pool(df)

    print("\n" + "=" * 100)
    print(f"FRESH-AUTHOR CONFIRMATORY SET FREEZE (Experiment 25) - n_examples >= {MIN_EXAMPLES}, "
          f"seed={SEED}")
    print("=" * 100)
    pool_df = pd.DataFrame(eligible_pool).sort_values(["narrative", "author_source"])
    print(f"\nEligible pool ({len(eligible_pool)} authors):")
    print(pool_df.to_string(index=False))

    selected = select_frozen_authors(eligible_pool)
    selected_df = pd.DataFrame(selected).sort_values(["narrative", "author_source"])
    print(f"\nFROZEN 14-author confirmatory set (2 per narrative, seed={SEED}):")
    print(selected_df.to_string(index=False))

    frozen = {
        "min_examples_threshold": MIN_EXAMPLES,
        "excluded_authors": sorted(EXCLUDED_AUTHORS),
        "random_seed": SEED,
        "n_per_narrative": N_PER_NARRATIVE,
        "eligible_pool": eligible_pool,
        "selected_authors": selected,
    }
    os.makedirs(REPORT_DIR, exist_ok=True)
    if os.path.exists(FROZEN_SET_FILE):
        raise RuntimeError(
            f"'{FROZEN_SET_FILE}' already exists - refusing to overwrite an already-frozen "
            f"author set. Delete it manually first if a genuine re-freeze is intended."
        )
    with open(FROZEN_SET_FILE, "w", encoding="utf-8") as f:
        json.dump(frozen, f, ensure_ascii=False, indent=2)
    print(f"\nSaved frozen confirmatory set to '{FROZEN_SET_FILE}'.")
    print("\nThis list is now FROZEN. Do not swap any author after seeing any model result.")


if __name__ == "__main__":
    main()

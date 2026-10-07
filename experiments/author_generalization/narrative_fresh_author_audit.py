"""
Narrative Classification — Fresh-Author Audit (Experiment 25, Phase 1)
=======================================================================
PHASE 1 ONLY: read-only audit of every author in the corpus - no training, no model
loading, no peeking at any model's performance. This script's sole purpose is to freeze a
"fresh held-out author" evaluation set for Experiment 25 (confirmatory evaluation of the
exploratory `sbert_person_misc_masked_aug_soft_topic` policy from Experiment 24) BEFORE any
training happens, so eligibility cannot be chosen (even implicitly) by looking at results.

Experiments 19-24 = exploratory / hypothesis-generating (used IDF, MariaZakharova,
BernieSanders as the ONLY held-out/test authors, and used their results to select masking
policies, arms, etc.). Experiment 25 = confirmatory evaluation on authors that were NEVER
held out / never individually analyzed for hypothesis generation in 19-24.

IMPORTANT DISCLOSED LIMITATION (not hidden): because Experiments 19-24 always trained on
"all real authors except the one held out", every real author's rows WERE present in the
training pool for at least 2 of the 3 runs in each of those experiments (this is unavoidable
given the shared corpus - there is no way to have a multi-author training set that excludes
every author individually). "Fresh" here specifically means: never the held-out/test author,
never the specific subject of any hypothesis/decision in Experiments 19-24 - NOT "rows never
seen in any training pool anywhere". This distinction is the operational definition of
"used in Experiments 19-24" applied below.

Eligibility criteria (declared here, BEFORE any training, and not to be changed after seeing
results):
  1. Real author only (a genuine Twitter account or Telegram channel with its own rows) -
     excludes gemini_synthetic/gpt_synthetic placeholders (is_synthetic_author()).
  2. Not IDF / MariaZakharova / BernieSanders (the 3 authors already used as held-out test
     sets throughout Experiments 18-24).
  3. Preference for >=100 examples (gives a test set at least comparable in order of
     magnitude to IDF's n_test=200 from Experiments 18-24); if too few authors clear 100,
     the full distribution is shown and a threshold is proposed - never chosen by looking at
     any model's performance on that author.
  4. Preference for narrative diversity across the chosen set (not all fresh authors from the
     same single narrative).

Run (from repo root):
    python experiments/author_generalization/narrative_fresh_author_audit.py
"""
import json
import os

import pandas as pd

from narrative_lens.train import load_raw_data, is_synthetic_author

REPORT_DIR = "artifacts/experiments/narrative_fresh_author_audit"
AUDIT_CSV = os.path.join(REPORT_DIR, "author_audit.csv")
AUDIT_JSON = os.path.join(REPORT_DIR, "author_audit_summary.json")

EXCLUDED_AUTHORS = {"IDF", "MariaZakharova", "BernieSanders"}  # held-out/test authors in Sections 18-24


def build_author_audit(df):
    rows = []
    grouped = df.groupby("author_source", dropna=False)
    for author_source, g in grouped:
        synthetic = is_synthetic_author(author_source)
        narratives = sorted(g["narrative_name"].unique().tolist())
        dataset_sources = sorted(g["dataset_source"].unique().tolist())
        used_in_19_24 = (author_source in EXCLUDED_AUTHORS)
        rows.append({
            "author_source": author_source,
            "narrative(s)": ", ".join(narratives),
            "n_examples": len(g),
            "dataset_source": ", ".join(dataset_sources),
            "is_synthetic": synthetic,
            "used_in_experiments_19_24": used_in_19_24,
            "eligible_for_fresh_evaluation": (not synthetic) and (not used_in_19_24),
        })
    audit_df = pd.DataFrame(rows).sort_values("n_examples", ascending=False).reset_index(drop=True)
    return audit_df


def main():
    df = load_raw_data()
    audit_df = build_author_audit(df)

    os.makedirs(REPORT_DIR, exist_ok=True)
    audit_df.to_csv(AUDIT_CSV, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 100)
    print("FRESH-AUTHOR AUDIT (Experiment 25, Phase 1) - read-only, no training, no model results used")
    print("=" * 100)
    print(audit_df.to_string(index=False))

    eligible = audit_df[audit_df["eligible_for_fresh_evaluation"]].reset_index(drop=True)
    print(f"\n{len(eligible)} author(s) eligible (real, not synthetic, not used as held-out "
          f"test author in Experiments 19-24):")
    print(eligible[["author_source", "narrative(s)", "n_examples"]].to_string(index=False))

    thresholds = [200, 150, 100, 75, 50, 30]
    print("\nEligible-author count at candidate minimum-example thresholds (for reference only "
          "- NOT chosen by looking at any model's performance):")
    threshold_counts = {}
    for t in thresholds:
        n = int((eligible["n_examples"] >= t).sum())
        threshold_counts[t] = n
        print(f"   >= {t:4d} examples: {n} author(s)")

    summary = {
        "n_total_authors": int(len(audit_df)),
        "n_synthetic_authors": int(audit_df["is_synthetic"].sum()),
        "n_excluded_prior_experiments": int(audit_df["used_in_experiments_19_24"].sum()),
        "n_eligible_total": int(len(eligible)),
        "eligible_authors_by_threshold": threshold_counts,
        "excluded_authors_list": sorted(EXCLUDED_AUTHORS),
    }
    with open(AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nSaved full audit table to '{AUDIT_CSV}'.")
    print(f"Saved summary to '{AUDIT_JSON}'.")
    print("\nNo author list has been frozen yet - this is Phase 1 (audit only). Do not train "
          "anything until the fresh-author list is explicitly reviewed and frozen.")


if __name__ == "__main__":
    main()

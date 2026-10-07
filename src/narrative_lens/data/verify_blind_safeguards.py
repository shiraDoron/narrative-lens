"""Verifies the 4 blindness safeguards on the human-validation package before
annotation starts. Read-only - does not modify any file.

Checks:
  1. The blind file(s) expose no author/source/platform/current_narrative columns.
  2. No obvious identifying handles/URLs remain in the blind `text` column.
  3. The 300-row blind file and the 100-row second-annotator subset have exactly the
     same annotation_ids as the key file expects (no drift from redaction/regeneration).
  4. The key file has one raw_text + full metadata row per annotation_id, enabling a
     complete merge after annotation.

Usage: python -m narrative_lens.data.verify_blind_safeguards
"""
import re
import sys
from pathlib import Path

import pandas as pd

ANNOT_DIR = Path("data/annotation")
BLIND_PATH = ANNOT_DIR / "human_validation_pilot_300_blind.csv"
SUBSET_PATH = ANNOT_DIR / "human_validation_pilot_300_blind_second_annotator_subset.csv"
KEY_PATH = ANNOT_DIR / "human_validation_pilot_300_key.csv"

FORBIDDEN_COLUMNS = {"author", "source", "platform", "current_narrative"}
LEAK_RE = re.compile(r"@\w+|https?://\S+|www\.\S+|t\.me/\S+", re.IGNORECASE)


def check_no_forbidden_columns(df: pd.DataFrame, name: str) -> list:
    problems = []
    hit = FORBIDDEN_COLUMNS & set(df.columns)
    if hit:
        problems.append(f"{name}: forbidden columns present: {sorted(hit)}")
    return problems


def check_no_leaks(df: pd.DataFrame, name: str) -> list:
    problems = []
    leaking = df["text"].astype(str).apply(lambda t: bool(LEAK_RE.search(t)))
    n = int(leaking.sum())
    if n:
        examples = df.loc[leaking, "annotation_id"].head(5).tolist()
        problems.append(f"{name}: {n} rows still contain handle/URL-shaped text, e.g. {examples}")
    return problems


def check_ids(blind: pd.DataFrame, subset: pd.DataFrame, key: pd.DataFrame) -> list:
    problems = []
    blind_ids = set(blind["annotation_id"])
    subset_ids = set(subset["annotation_id"])
    key_ids = set(key["annotation_id"])

    if len(blind) != 300 or len(blind_ids) != 300:
        problems.append(f"blind file: expected 300 unique annotation_ids, got {len(blind)} rows / {len(blind_ids)} unique")
    if len(subset) != 100 or len(subset_ids) != 100:
        problems.append(f"subset file: expected 100 unique annotation_ids, got {len(subset)} rows / {len(subset_ids)} unique")
    if not subset_ids.issubset(blind_ids):
        problems.append(f"subset file has {len(subset_ids - blind_ids)} annotation_ids not present in the blind file")
    if blind_ids != key_ids:
        problems.append(f"blind/key annotation_id mismatch: {len(blind_ids ^ key_ids)} ids differ")
    expected_subset_ids = set(key.loc[key["second_annotator_subset"], "annotation_id"])
    if expected_subset_ids != subset_ids:
        problems.append("key.second_annotator_subset flag does not match the subset file's annotation_ids")
    return problems


def check_key_completeness(key: pd.DataFrame) -> list:
    problems = []
    required = {"annotation_id", "raw_text", "current_narrative", "author", "platform", "timestamp"}
    missing_cols = required - set(key.columns)
    if missing_cols:
        problems.append(f"key file missing columns: {sorted(missing_cols)}")
    if key["annotation_id"].duplicated().any():
        problems.append("key file has duplicate annotation_ids")
    if key["raw_text"].isna().any() or (key["raw_text"].astype(str).str.strip() == "").any():
        problems.append("key file has rows with empty raw_text")
    return problems


def main():
    blind = pd.read_csv(BLIND_PATH)
    subset = pd.read_csv(SUBSET_PATH)
    key = pd.read_csv(KEY_PATH)

    problems = []
    problems += check_no_forbidden_columns(blind, "blind file")
    problems += check_no_forbidden_columns(subset, "subset file")
    problems += check_no_leaks(blind, "blind file")
    problems += check_no_leaks(subset, "subset file")
    problems += check_ids(blind, subset, key)
    problems += check_key_completeness(key)

    if problems:
        print("BLINDNESS SAFEGUARD CHECK: FAILED\n")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    print("BLINDNESS SAFEGUARD CHECK: PASSED")
    print(f"  1. No author/source/platform/current_narrative columns in blind/subset files.")
    print(f"  2. No @handle/URL-shaped text remains in blind/subset text columns.")
    print(f"  3. Blind file has 300 unique annotation_ids; subset has 100, all a subset of blind's;"
          f" key's second_annotator_subset flag matches exactly.")
    print(f"  4. Key file has complete raw_text + metadata for all {len(key)} annotation_ids - full merge possible.")


if __name__ == "__main__":
    main()

"""Builds the BLIND human-validation package from the already-sampled 300-row pilot
(`data/annotation/human_validation_pilot_300.csv` - built by
`build_human_validation_sample.py`, unchanged here).

Purpose: the reviewer must judge each text's narrative from the text ALONE - not
confirm/reject an existing label. So the file reviewers actually see must not expose
`current_narrative`, `author`, `platform`, or any heuristic prediction. Metadata is
kept in a separate "key" file and only merged back in after annotation is complete
(by `analyze_human_validation.py`, via `annotation_id`).

In this dataset "author" and "source/account" refer to the same field (the
Twitter/Telegram handle); "platform" is twitter vs. telegram. All three are withheld
from the blind file; only `annotation_id` + `text` are shown.

Outputs (all under data/annotation/):
  - human_validation_pilot_300_blind.csv                        <- give to annotator 1 (all 300)
  - human_validation_pilot_300_blind_second_annotator_subset.csv <- give to annotator 2 (100, stratified)
  - human_validation_pilot_300_key.csv                          <- private; current_narrative/author/
                                                                    platform/timestamp/event_id/
                                                                    second_annotator_subset flag

Row order is deterministically shuffled (RANDOM_SEED) so that no two consecutive rows
share the same author, narrative, or platform (best-effort greedy pass - falls back to
relaxing the constraint only if no clean candidate remains).

Last-mile blindness safeguard: the `text` shown to annotators has technical metadata
that could reveal the source redacted (@handles -> [USER], URLs/t.me links -> [URL]).
The untouched raw text is never modified in `data/raw/*.csv` and is kept privately in
`human_validation_pilot_300_key.csv` (`raw_text` column) for merging back after
annotation. Named entities that are part of the actual content (Trump, Israel, NATO,
Hezbollah, etc.) are never touched - only handle/URL-shaped tokens are replaced.

Usage: python -m narrative_lens.data.build_blind_validation_sample
"""
import re
from pathlib import Path

import pandas as pd

IN_PATH = Path("data/annotation/human_validation_pilot_300.csv")
OUT_DIR = Path("data/annotation")
RANDOM_SEED = 42

# Technical-metadata patterns only - never touches plain-text named entities.
_URL_RE = re.compile(r"https?://\S+|www\.\S+|t\.me/\S+", re.IGNORECASE)
_BARE_DOMAIN_RE = re.compile(
    r"\b[a-zA-Z0-9][-a-zA-Z0-9]{1,62}\.(?:com|org|net|io|gov|edu|tv|co|uk|ru|ir)(?:/\S*)?\b",
    re.IGNORECASE,
)
_HANDLE_RE = re.compile(r"@\w+")


def redact_technical_metadata(text: str) -> str:
    """Replace handle/URL-shaped technical metadata with neutral placeholders so
    annotators can't identify the source account/platform from the text itself."""
    text = _URL_RE.sub("[URL]", text)
    text = _BARE_DOMAIN_RE.sub("[URL]", text)
    text = _HANDLE_RE.sub("[USER]", text)
    return text

NARRATIVES = ["Zionist", "Resistance", "Western", "Russian", "Ukrainian", "Right-wing", "Left-wing"]
# 14 per narrative (7*14=98) + 1 extra each to these 2 narratives -> exactly 100.
SECOND_ANNOTATOR_BASE = 14
SECOND_ANNOTATOR_BOOST = {"Zionist", "Resistance"}


def anti_cluster_shuffle(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Deterministically reorder rows so consecutive rows never share narrative,
    author, or platform. Falls back to the next available row (relaxing the
    constraint) only if every remaining row would clash."""
    pool = df.sample(frac=1.0, random_state=seed).to_dict("records")
    ordered = []
    last = None
    while pool:
        chosen_i = None
        for i, cand in enumerate(pool):
            if last is None or (
                cand["current_narrative"] != last["current_narrative"]
                and cand["author"] != last["author"]
                and cand["source"] != last["source"]
            ):
                chosen_i = i
                break
        if chosen_i is None:
            chosen_i = 0  # no clash-free candidate left; relax constraint
        last = pool.pop(chosen_i)
        ordered.append(last)
    return pd.DataFrame(ordered)


def count_adjacent_clashes(df: pd.DataFrame) -> dict:
    clashes = {"narrative": 0, "author": 0, "platform": 0}
    for col, key in [("current_narrative", "narrative"), ("author", "author"), ("source", "platform")]:
        clashes[key] = int((df[col].values[1:] == df[col].values[:-1]).sum())
    return clashes


def pick_second_annotator_ids(df: pd.DataFrame, seed: int) -> set:
    parts = []
    for narrative in NARRATIVES:
        sub = df[df["current_narrative"] == narrative]
        target = SECOND_ANNOTATOR_BASE + (1 if narrative in SECOND_ANNOTATOR_BOOST else 0)
        target = min(target, len(sub))
        parts.append(sub.sample(n=target, random_state=seed))
    return set(pd.concat(parts)["annotation_id"])


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN_PATH)
    df = df.drop(columns=["reviewer_narrative", "confidence", "ambiguous_flag",
                           "neutral_or_no_clear_narrative", "notes"])

    df = anti_cluster_shuffle(df, RANDOM_SEED).reset_index(drop=True)
    df["annotation_id"] = [f"HV{i + 1:03d}" for i in range(len(df))]

    clashes = count_adjacent_clashes(df)
    second_ids = pick_second_annotator_ids(df, RANDOM_SEED)

    redacted_text = df["text"].apply(redact_technical_metadata)

    blind = pd.DataFrame({
        "annotation_id": df["annotation_id"],
        "text": redacted_text,
        "reviewer_label": "",
        "confidence": "",
        "neutral_or_no_clear_narrative": "",
        "ambiguous_flag": "",
        "secondary_narrative": "",
        "notes": "",
    })
    blind.to_csv(OUT_DIR / "human_validation_pilot_300_blind.csv", index=False)

    key = pd.DataFrame({
        "annotation_id": df["annotation_id"],
        "raw_text": df["text"],
        "current_narrative": df["current_narrative"],
        "author": df["author"],
        "platform": df["source"],
        "timestamp": df["timestamp"],
        "event_id": df["event_id"],
        "second_annotator_subset": df["annotation_id"].isin(second_ids),
    })
    key.to_csv(OUT_DIR / "human_validation_pilot_300_key.csv", index=False)

    n_redacted = int((redacted_text != df["text"]).sum())
    print(f"Redacted technical metadata (handles/URLs) in {n_redacted} / {len(df)} texts")

    subset_blind = blind[blind["annotation_id"].isin(second_ids)].reset_index(drop=True)
    subset_blind.to_csv(OUT_DIR / "human_validation_pilot_300_blind_second_annotator_subset.csv", index=False)

    print(f"Wrote {len(blind)} rows to human_validation_pilot_300_blind.csv (no narrative/author/platform columns)")
    print(f"Wrote {len(key)} rows to human_validation_pilot_300_key.csv (private, merge later via annotation_id)")
    print(f"Wrote {len(subset_blind)} rows to human_validation_pilot_300_blind_second_annotator_subset.csv")
    print(f"\nAdjacent-row clashes remaining after anti-cluster shuffle (0 = fully clean): {clashes}")
    print("\nSecond-annotator subset per narrative:")
    print(key[key["second_annotator_subset"]]["current_narrative"].value_counts())


if __name__ == "__main__":
    main()

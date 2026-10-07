"""Builds a 300-row stratified Human-Validation sample from EXISTING human-authored
data only (Twitter + Telegram - gemini/gpt synthetic rows are excluded, since the
point is to validate real labels on real human text, not synthetic statements).

Stratifies as evenly as possible across:
  - narrative (7 groups, ~43/42 rows each)
  - author (round-robin across accounts within each narrative, so no single account
    dominates the sample)
  - source/platform (falls out naturally since accounts are platform-specific)
  - event/topic (rows matching a systematic matched-event candidate - see
    audit_matched_events.py - are prioritized first within each account, so the
    sample also lets us spot-check matched-event rows; not all rows will have one)

Does NOT fill in any reviewer_narrative/confidence/ambiguous_flag/
neutral_or_no_clear_narrative/notes values - those columns are left blank and unused.

NOTE: this file is an intermediate artifact only. Actual annotation happens on the BLIND
version built from this output by `build_blind_validation_sample.py`
(`data/annotation/human_validation_pilot_300_blind.csv`, which withholds
narrative/author/platform) - see docs/NARRATIVE_ANNOTATION_GUIDE.md.

Usage: python -m narrative_lens.data.build_human_validation_sample
"""
import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/annotation")
TOTAL_TARGET = 300
RANDOM_SEED = 42
NARRATIVES = ["Zionist", "Resistance", "Western", "Russian", "Ukrainian", "Right-wing", "Left-wing"]
# Western has the fewest human-authored rows of the 7 - give it one fewer slot so the
# other 6 (43 each) + Western (42) sum to exactly 300.
NARRATIVE_TARGETS = {n: 43 for n in NARRATIVES}
NARRATIVE_TARGETS["Western"] = 42

# Same topic keyword groups as audit_matched_events.py, used only to tag event_id for
# rows that fall in an actual candidate-event (topic, month) cell with narrative_count>=2.
TOPICS = {
    "israel_hezbollah_gaza": r"\b(?:israel|gaza|hezbollah|hamas|lebanon|beirut|idf|palestin|west bank|houthi)\w*\b",
    "russia_ukraine": r"\b(?:russia|ukrain|kyiv|kiev|moscow|kursk|zelensky|putin|donbas|crimea|zaporizh)\w*\b",
    "us_politics_trump": r"\b(?:trump|congress|republican|democrat|election|president|shutdown|impeach|senate|whitehouse|ice\b|dhs\b)\w*\b",
    "iran": r"\b(?:iran|tehran|irgc|khamenei|hormuz|nuclear|pezeshkian)\w*\b",
    "ceasefire_hostage_peace": r"\b(?:ceasefire|hostage|peace talks|negotiation|truce|prisoner exchange|cease-fire)\w*\b",
}
CANDIDATE_SUMMARY_PATH = Path("artifacts/experiments/narrative_audit/matched_event_candidates_summary.csv")


def load_human_authored() -> pd.DataFrame:
    frames = []
    for fname, source in [
        ("twitter_natural_dataset.csv", "twitter"),
        ("telegram_natural_dataset.csv", "telegram"),
    ]:
        df = pd.read_csv(RAW_DIR / fname)
        df["source"] = source
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    combined["text"] = combined["text"].astype(str)
    combined["date_parsed"] = pd.to_datetime(combined["date"], errors="coerce", utc=True)
    combined["month"] = combined["date_parsed"].dt.to_period("M").astype(str)
    return combined


def tag_event_ids(df: pd.DataFrame) -> pd.Series:
    """Tag rows with an event_id (topic_month) only if that (topic, month) is an
    actual candidate event (narrative_count >= 2) per audit_matched_events.py."""
    valid_cells = set()
    if CANDIDATE_SUMMARY_PATH.is_file():
        summary = pd.read_csv(CANDIDATE_SUMMARY_PATH)
        valid_cells = set(zip(summary["topic"], summary["month"]))

    event_ids = pd.Series([None] * len(df), index=df.index, dtype=object)
    for topic, pattern in TOPICS.items():
        regex = re.compile(pattern, re.IGNORECASE)
        matches = df["text"].str.contains(regex, na=False)
        for month in df.loc[matches, "month"].unique():
            if (topic, month) in valid_cells:
                cell_mask = matches & (df["month"] == month) & event_ids.isna()
                event_ids.loc[cell_mask] = f"{topic}_{month}"
    return event_ids


def sample_narrative(sub: pd.DataFrame, target_n: int, seed: int) -> pd.DataFrame:
    """Round-robin across accounts, preferring event-tagged rows first within
    each account, so no single account dominates and event rows get surfaced."""
    sub = sub.sample(frac=1.0, random_state=seed)  # shuffle within-account order
    sub = sub.sort_values("has_event", ascending=False, kind="stable")  # event rows first per account
    by_account = {acc: list(g.index) for acc, g in sub.groupby("account")}
    accounts = sorted(by_account.keys())

    picked = []
    while len(picked) < target_n and any(by_account[a] for a in accounts):
        for acc in accounts:
            if len(picked) >= target_n:
                break
            if by_account[acc]:
                picked.append(by_account[acc].pop(0))
    return sub.loc[picked]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_human_authored()
    df["event_id"] = tag_event_ids(df)
    df["has_event"] = df["event_id"].notna()

    sampled_parts = []
    for narrative in NARRATIVES:
        sub = df[df["narrative_name"] == narrative]
        target_n = NARRATIVE_TARGETS[narrative]
        if len(sub) < target_n:
            print(f"WARNING: {narrative} only has {len(sub)} human-authored rows (<{target_n})")
            target_n = len(sub)
        picked = sample_narrative(sub, target_n, RANDOM_SEED)
        sampled_parts.append(picked)

    result = pd.concat(sampled_parts, ignore_index=True)
    result = result.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)  # shuffle final order

    annotation = pd.DataFrame({
        "text": result["text"],
        "current_narrative": result["narrative_name"],
        "author": result["account"],
        "source": result["source"],
        "timestamp": result["date"],
        "event_id": result["event_id"],
        "reviewer_narrative": "",
        "confidence": "",
        "ambiguous_flag": "",
        "neutral_or_no_clear_narrative": "",
        "notes": "",
    })
    annotation.to_csv(OUT_DIR / "human_validation_pilot_300.csv", index=False)

    print(f"Wrote {len(annotation)} rows to {OUT_DIR / 'human_validation_pilot_300.csv'}")
    print("\nPer-narrative counts:")
    print(annotation["current_narrative"].value_counts())
    print("\nPer-source counts:")
    print(annotation["source"].value_counts())
    print(f"\nRows with an event_id tag: {annotation['event_id'].notna().sum()} / {len(annotation)}")
    print("\nDistinct authors per narrative:")
    print(annotation.groupby("current_narrative")["author"].nunique())


if __name__ == "__main__":
    main()

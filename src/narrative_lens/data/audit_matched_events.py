"""Systematic (not cherry-picked) Matched-Event candidate mining across the existing
human-authored corpus (Twitter + Telegram only - gemini/gpt synthetic rows have no
real timestamps/authors and are excluded from event matching).

For each topic keyword-group and each calendar month present in the data, counts how
many narratives have coverage and with how many distinct authors. Does NOT force a
match - a (topic, month) cell only counts as a candidate event if narratives actually
have data there. Read-only, writes a candidate table for review; changes nothing else.

Usage: python -m narrative_lens.data.audit_matched_events
"""
import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("artifacts/experiments/narrative_audit")
MIN_TEXTS_FOR_NARRATIVE_PRESENCE = 3  # a narrative "has coverage" in a cell if >= this many texts

# Topic keyword groups (regex, case-insensitive). A text can match more than one topic.
TOPICS = {
    "israel_hezbollah_gaza": r"\b(?:israel|gaza|hezbollah|hamas|lebanon|beirut|idf|palestin|west bank|houthi)\w*\b",
    "russia_ukraine": r"\b(?:russia|ukrain|kyiv|kiev|moscow|kursk|zelensky|putin|donbas|crimea|zaporizh)\w*\b",
    "us_politics_trump": r"\b(?:trump|congress|republican|democrat|election|president|shutdown|impeach|senate|whitehouse|ice\b|dhs\b)\w*\b",
    "iran": r"\b(?:iran|tehran|irgc|khamenei|hormuz|nuclear|pezeshkian)\w*\b",
    "ceasefire_hostage_peace": r"\b(?:ceasefire|hostage|peace talks|negotiation|truce|prisoner exchange|cease-fire)\w*\b",
}


def load_human_authored() -> pd.DataFrame:
    frames = []
    for fname, source in [
        ("twitter_natural_dataset.csv", "twitter"),
        ("telegram_natural_dataset.csv", "telegram"),
    ]:
        path = RAW_DIR / fname
        if not path.is_file():
            continue
        df = pd.read_csv(path)
        df["dataset_source"] = source
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    combined["text"] = combined["text"].astype(str)
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce", utc=True)
    combined = combined.dropna(subset=["date"])
    combined["month"] = combined["date"].dt.to_period("M").astype(str)
    return combined


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_human_authored()

    rows = []
    for topic, pattern in TOPICS.items():
        regex = re.compile(pattern, re.IGNORECASE)
        matched = df[df["text"].str.contains(regex, na=False)]
        if matched.empty:
            continue
        grouped = matched.groupby(["month", "narrative_name"]).agg(
            text_count=("text", "count"), author_count=("account", "nunique")
        ).reset_index()
        grouped["topic"] = topic
        rows.append(grouped)

    candidate_cells = pd.concat(rows, ignore_index=True)
    candidate_cells = candidate_cells[
        ["topic", "month", "narrative_name", "text_count", "author_count"]
    ].sort_values(["topic", "month", "narrative_name"])
    candidate_cells.to_csv(OUT_DIR / "matched_event_candidates_full.csv", index=False)

    # Summarize per (topic, month): how many narratives have >= MIN_TEXTS_FOR_NARRATIVE_PRESENCE
    present = candidate_cells[candidate_cells["text_count"] >= MIN_TEXTS_FOR_NARRATIVE_PRESENCE]
    summary_rows = []
    for (topic, month), group in present.groupby(["topic", "month"]):
        narratives_present = sorted(group["narrative_name"].tolist())
        summary_rows.append({
            "topic": topic,
            "month": month,
            "narrative_count": len(narratives_present),
            "narratives_present": ",".join(narratives_present),
            "min_text_count": int(group["text_count"].min()),
            "min_author_count": int(group["author_count"].min()),
            "total_texts": int(group["text_count"].sum()),
        })
    summary = pd.DataFrame(summary_rows).sort_values(
        ["narrative_count", "min_author_count"], ascending=[False, False]
    )
    summary.to_csv(OUT_DIR / "matched_event_candidates_summary.csv", index=False)

    n2 = (summary["narrative_count"] >= 2).sum()
    n3 = (summary["narrative_count"] >= 3).sum()
    n4 = (summary["narrative_count"] >= 4).sum()
    print(f"Total (topic, month) cells with any narrative present: {len(summary)}")
    print(f"Cells with >=2 narratives: {n2}")
    print(f"Cells with >=3 narratives: {n3}")
    print(f"Cells with >=4 narratives: {n4}")
    print("\nTop candidates (>=3 narratives), by min_author_count:")
    top = summary[summary["narrative_count"] >= 3].sort_values(
        ["narrative_count", "min_author_count"], ascending=[False, False]
    ).head(15)
    print(top.to_string(index=False))


if __name__ == "__main__":
    main()

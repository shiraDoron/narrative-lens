"""
Matched-Event Benchmark pilot exporter (Phase 1, offline / credential-free).

Mines the ALREADY-EXISTING raw corpus (data/raw/twitter_natural_dataset.csv +
data/raw/telegram_natural_dataset.csv) for two candidate matched events, using simple
keyword + date-window filtering. Does NOT scrape anything new and does NOT touch the
existing dataset files - only reads them and writes a new pilot export.

Output: data/candidates/v2_pilot/matched_event_pilot.csv
Schema: event_id, event_description, date_window, narrative, author, source, text

This is real (non-fabricated) data already present in the corpus, re-packaged under the
new V2 pilot schema so it can be reviewed as a Matched-Event Benchmark candidate.
"""

import re
import pandas as pd

MAX_PER_NARRATIVE = 20

EVENTS = {
    "event_us_politics_2026_03": {
        "description": (
            "US politics, March 2026: Trump administration military strikes on Iran, "
            "domestic ICE/DHS security policy announcements, and related partisan reaction "
            "(incl. Left-wing framing of Trump-era foreign policy via the Cuba/Havana convoy "
            "coverage)."
        ),
        "narratives": ["Left-wing", "Right-wing", "Western"],
        "keywords": ["trump", "congress", "republican", "democrat", "election", "president", "shutdown", "impeach"],
        "month": "2026-03",
    },
    "event_israel_hezbollah_lebanon_2026_03": {
        "description": (
            "Israel-Hezbollah-Lebanon escalation, March 2026: cross-border strikes framed by "
            "Zionist accounts as Iran-backed Hezbollah aggression, by Resistance accounts as "
            "legitimate defense/solidarity with Gaza and Yemen, and by Western accounts as a "
            "humanitarian/diplomatic aid issue (EU emergency aid to Lebanon)."
        ),
        "narratives": ["Zionist", "Resistance", "Western"],
        "keywords": ["hezbollah", "lebanon", "gaza", "ceasefire", "hostage", "beirut", "idf"],
        "month": "2026-03",
    },
}


def main():
    tw = pd.read_csv("data/raw/twitter_natural_dataset.csv")
    tg = pd.read_csv("data/raw/telegram_natural_dataset.csv")
    tw["source"] = "twitter"
    tg["source"] = "telegram"
    df = pd.concat([tw, tg], ignore_index=True)
    df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["text_lower"] = df["text"].astype(str).str.lower()

    rows = []
    for event_id, spec in EVENTS.items():
        pattern = re.compile(r"\b(" + "|".join(spec["keywords"]) + r")\b")
        sub = df[df["narrative_name"].isin(spec["narratives"])].copy()
        sub = sub[sub["text_lower"].str.contains(pattern, regex=True)]
        sub = sub.dropna(subset=["date_parsed"])
        sub = sub[sub["date_parsed"].dt.to_period("M").astype(str) == spec["month"]]

        print(f"\n{event_id}: {len(sub)} raw matches in {spec['month']}")
        for narrative in spec["narratives"]:
            narr_sub = sub[sub["narrative_name"] == narrative]
            n_authors = narr_sub["account"].nunique()
            print(f"  {narrative}: {len(narr_sub)} texts, {n_authors} authors")
            # Cap per narrative, but spread across authors rather than taking one author's texts only.
            capped = (
                narr_sub.groupby("account", group_keys=False)
                .apply(lambda g: g.head(max(1, MAX_PER_NARRATIVE // max(n_authors, 1) + 3)))
                .head(MAX_PER_NARRATIVE)
            )
            for _, r in capped.iterrows():
                rows.append({
                    "event_id": event_id,
                    "event_description": spec["description"],
                    "date_window": spec["month"],
                    "narrative": narrative,
                    "author": r["account"],
                    "source": r["source"],
                    "text": r["text"],
                })

    out = pd.DataFrame(rows, columns=[
        "event_id", "event_description", "date_window", "narrative", "author", "source", "text",
    ])
    out_path = "data/candidates/v2_pilot/matched_event_pilot.csv"
    out.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nWrote {len(out)} rows to {out_path}")
    print(out.groupby(["event_id", "narrative"])["author"].agg(["count", "nunique"]))


if __name__ == "__main__":
    main()

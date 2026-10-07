"""Source-derived label-quality audit (flagging only - does NOT change any labels).

Heuristic, keyword-based proxy for whether a text's narrative label is actually
supported by framing markers IN THE TEXT, or whether it looks like it was labeled
purely by account/source provenance. This is a coarse triage tool, not ground truth -
its purpose is to surface candidates for the human-validation pilot and for manual
account-level review, per docs/narrative_definitions.md.

Scope: human-authored data only (Twitter + Telegram). Synthetic gemini/gpt rows are
deliberately narrative-representative by construction and are out of scope for this
"does the account's real-world text match its label" question.

For each text, counts framing-marker keyword hits per narrative (see FRAMING_MARKERS)
and classifies it as:
  - strongly_aligned: has >=1 hit for its OWN narrative's markers, and that count is
    >= any other narrative's hit count.
  - potentially_neutral: zero hits for every narrative's markers (looks like plain
    factual/neutral content).
  - potentially_mismatched: some OTHER narrative's marker count exceeds its own.

Also flags accounts whose fraction of non-strongly_aligned texts is high (>=0.5,
with >=5 texts), as "label likely unstable at text-level - needs manual review".

Usage: python -m narrative_lens.data.audit_label_quality
"""
import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("reports/results/narrative_audit")
MIN_TEXTS_FOR_ACCOUNT_FLAG = 5
UNSTABLE_ACCOUNT_THRESHOLD = 0.5  # fraction of non-strongly_aligned texts

# Framing/opinion markers per narrative - deliberately NOT plain topic nouns (e.g. "Israel",
# "Iran", "Russia") since those appear in neutral wire reporting too and wouldn't distinguish
# framing from topic. These were derived from real examples in
# reports/results/narrative_audit/narrative_audit.txt and docs/narrative_definitions.md.
FRAMING_MARKERS = {
    "Zionist": [
        r"terrorist", r"terror regime", r"hostages?", r"eliminated", r"self-defen",
        r"antisemit", r"delegitimi", r"iranian regime", r"jewish state", r"israel's right",
        r"idf strike", r"targeted strike", r"butcher", r"massacre",
    ],
    "Resistance": [
        r"occupation forces", r"zionist regime", r"zionist entity", r"resistance",
        r"martyr", r"aggression", r"occupied palestin", r"settler", r"genocide",
        r"war crime", r"colonial", r"liberation", r"axis of resistance",
    ],
    "Western": [
        r"\balliance\b", r"sanctions?", r"\bcondemn", r"our government", r"shared values",
        r"committed to", r"we stand with", r"rules-based", r"our ally", r"solidarity with",
        r"we urge",
    ],
    "Russian": [
        r"hypocrisy", r"russophob", r"special military operation", r"\bnazis?\b",
        r"nazi regime", r"western double standard", r"denazif",
    ],
    "Ukrainian": [
        r"russian aggression", r"russian invasion", r"sovereignty", r"war crime",
        r"occupier", r"defend our", r"russia's war", r"invading forces",
    ],
    "Right-wing": [
        r"\bwoke\b", r"radical left", r"illegal immig", r"deep state", r"liberal media",
        r"cancel cultur", r"big government", r"socialis", r"biological male",
        r"indoctrinat",
    ],
    "Left-wing": [
        r"billionaire", r"inequality", r"fight back", r"solidarity", r"\bworkers?\b",
        r"unioniz", r"corporate greed", r"healthcare is a right", r"asylum seekers?",
        r"settler violence", r"occupied west bank", r"climate justice",
    ],
}
COMPILED_MARKERS = {
    narrative: [re.compile(p, re.IGNORECASE) for p in patterns]
    for narrative, patterns in FRAMING_MARKERS.items()
}


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
    return combined


def score_row(text: str) -> dict:
    return {
        narrative: sum(1 for pat in patterns if pat.search(text))
        for narrative, patterns in COMPILED_MARKERS.items()
    }


def classify(own_narrative: str, scores: dict) -> str:
    own_score = scores[own_narrative]
    other_scores = {n: s for n, s in scores.items() if n != own_narrative}
    max_other = max(other_scores.values()) if other_scores else 0

    if own_score == 0 and max_other == 0:
        return "potentially_neutral"
    if max_other > own_score:
        return "potentially_mismatched"
    return "strongly_aligned"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_human_authored()

    scores = df["text"].apply(score_row)
    df["category"] = [classify(n, s) for n, s in zip(df["narrative_name"], scores)]

    per_text_cols = ["text", "narrative_name", "account", "source", "category"]
    df[per_text_cols].to_csv(OUT_DIR / "label_quality_per_text.csv", index=False)

    # Per-narrative summary.
    summary = df.groupby(["narrative_name", "category"]).size().unstack(fill_value=0)
    for col in ["strongly_aligned", "potentially_neutral", "potentially_mismatched"]:
        if col not in summary.columns:
            summary[col] = 0
    summary = summary[["strongly_aligned", "potentially_neutral", "potentially_mismatched"]]
    summary["total"] = summary.sum(axis=1)
    summary["pct_aligned"] = (summary["strongly_aligned"] / summary["total"] * 100).round(1)
    summary.to_csv(OUT_DIR / "label_quality_narrative_summary.csv")

    # Per-account instability flagging.
    account_stats = df.groupby(["narrative_name", "account"]).agg(
        total_texts=("category", "size"),
        strongly_aligned=("category", lambda s: (s == "strongly_aligned").sum()),
        potentially_neutral=("category", lambda s: (s == "potentially_neutral").sum()),
        potentially_mismatched=("category", lambda s: (s == "potentially_mismatched").sum()),
    ).reset_index()
    account_stats["non_aligned_fraction"] = (
        (account_stats["total_texts"] - account_stats["strongly_aligned"]) / account_stats["total_texts"]
    ).round(3)
    account_stats["flagged_unstable"] = (
        (account_stats["total_texts"] >= MIN_TEXTS_FOR_ACCOUNT_FLAG)
        & (account_stats["non_aligned_fraction"] >= UNSTABLE_ACCOUNT_THRESHOLD)
    )
    account_stats = account_stats.sort_values(
        ["flagged_unstable", "non_aligned_fraction"], ascending=[False, False]
    )
    account_stats.to_csv(OUT_DIR / "label_quality_account_flags.csv", index=False)

    print("=== Per-narrative label-quality summary (heuristic, flagging only) ===")
    print(summary.to_string())
    print(f"\n=== Accounts flagged as likely unstable (>= {MIN_TEXTS_FOR_ACCOUNT_FLAG} texts, "
          f">= {UNSTABLE_ACCOUNT_THRESHOLD:.0%} non-aligned) ===")
    flagged = account_stats[account_stats["flagged_unstable"]]
    print(flagged.to_string(index=False))
    print(f"\nTotal flagged accounts: {len(flagged)} / {len(account_stats)}")


if __name__ == "__main__":
    main()

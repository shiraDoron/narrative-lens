"""Read-only audit of the 7 narrative labels across all raw data sources.

Does NOT modify any labels or existing data. Produces a report (counts, authors,
source breakdown, sample texts per narrative) used to ground the narrative
definitions written in docs/narrative_definitions.md.

Usage: python -m narrative_lens.data.audit_narratives
"""
import json
import random
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("artifacts/experiments/narrative_audit")
NARRATIVES = ["Zionist", "Resistance", "Western", "Russian", "Ukrainian", "Right-wing", "Left-wing"]
SAMPLES_PER_AUTHOR = 2
RANDOM_SEED = 42


def load_all() -> pd.DataFrame:
    frames = []
    for fname, source in [
        ("twitter_natural_dataset.csv", "twitter"),
        ("telegram_natural_dataset.csv", "telegram"),
        ("gemini_natural_dataset.csv", "gemini"),
        ("gpt_natural_dataset.csv", "gpt"),
    ]:
        path = RAW_DIR / fname
        if not path.is_file():
            continue
        df = pd.read_csv(path)
        df["dataset_source"] = source
        if "account" not in df.columns:
            df["account"] = f"{source}_synthetic"
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    combined["text"] = combined["text"].astype(str)
    return combined


def main():
    random.seed(RANDOM_SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_all()

    report = {}
    lines = []
    for narrative in NARRATIVES:
        sub = df[df["narrative_name"] == narrative]
        authors = sub.groupby("account").size().sort_values(ascending=False)
        by_source = sub.groupby("dataset_source").size().to_dict()
        avg_len = sub["text"].str.len().mean()

        # Sample a spread of texts: a couple per author, capped, shuffled.
        samples = []
        for account, group in sub.groupby("account"):
            picked = group["text"].sample(
                n=min(SAMPLES_PER_AUTHOR, len(group)), random_state=RANDOM_SEED
            ).tolist()
            for text in picked:
                samples.append({"account": account, "text": text[:400]})
        random.shuffle(samples)
        samples = samples[:25]

        report[narrative] = {
            "total_rows": int(len(sub)),
            "distinct_authors": int(authors.shape[0]),
            "top_authors": authors.head(10).to_dict(),
            "by_dataset_source": by_source,
            "avg_text_len": round(float(avg_len), 1) if pd.notna(avg_len) else None,
            "samples": samples,
        }

        lines.append(f"=== {narrative} ===")
        lines.append(
            f"total={len(sub)} distinct_authors={authors.shape[0]} "
            f"by_source={by_source} avg_len={report[narrative]['avg_text_len']}"
        )
        lines.append(f"top_authors={authors.head(10).to_dict()}")
        for s in samples:
            lines.append(f"  [{s['account']}] {s['text']}")
        lines.append("")

    (OUT_DIR / "narrative_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "narrative_audit.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote audit report to {OUT_DIR}")


if __name__ == "__main__":
    main()

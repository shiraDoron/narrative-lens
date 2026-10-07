"""Post-annotation analysis report for the blind human-validation pilot.

Run this AFTER annotators have filled in `human_validation_pilot_300_blind.csv`
(annotator 1, all 300 rows) and, ideally, `human_validation_pilot_300_blind_
second_annotator_subset.csv` (annotator 2, ~100 rows). Merges each blind file back
with the private `human_validation_pilot_300_key.csv` via `annotation_id` - this is
the FIRST point at which reviewer judgments are compared to the original
source-derived labels. Does not change any label anywhere; read-only analysis.

Outputs a printed report plus `artifacts/experiments/narrative_audit/human_validation_report.md`
covering:
  - Overall: % agreement with original labels, % disagreement, % neutral/no-clear,
    % ambiguous, confidence distribution.
  - Per narrative: label validity (of texts originally labeled X, how many the human
    also called X), common relabel destinations, neutral rate, ambiguous rate.
  - Per author: disagreement rate, neutral rate - candidates for keep/remove/
    downsample/manual-review decisions.
  - Inter-annotator agreement (only if the second-annotator file has been filled in):
    raw agreement, Cohen's kappa, confusion matrix, agreement per narrative, agreement
    by confidence level.

Usage: python -m narrative_lens.data.analyze_human_validation
"""
from pathlib import Path

import pandas as pd

ANNOT_DIR = Path("data/annotation")
BLIND_PATH = ANNOT_DIR / "human_validation_pilot_300_blind.csv"
KEY_PATH = ANNOT_DIR / "human_validation_pilot_300_key.csv"
SECOND_PATH = ANNOT_DIR / "human_validation_pilot_300_blind_second_annotator_subset.csv"
OUT_DIR = Path("artifacts/experiments/narrative_audit")
OUT_PATH = OUT_DIR / "human_validation_report.md"

NARRATIVES = ["Zionist", "Resistance", "Western", "Russian", "Ukrainian", "Right-wing", "Left-wing"]
MIN_TEXTS_FOR_ACCOUNT_FLAG = 3
SUSPICIOUS_RATE_THRESHOLD = 0.5


def _is_true(val) -> bool:
    return str(val).strip().lower() in {"true", "yes", "1", "y"}


def load_merged() -> pd.DataFrame:
    blind = pd.read_csv(BLIND_PATH, dtype={"confidence": "string"})
    key = pd.read_csv(KEY_PATH)
    merged = blind.merge(key, on="annotation_id", how="left")
    merged["is_neutral"] = merged["neutral_or_no_clear_narrative"].apply(_is_true)
    merged["is_ambiguous"] = merged["ambiguous_flag"].apply(_is_true)
    merged["reviewer_label"] = merged["reviewer_label"].fillna("").astype(str).str.strip()
    merged["agrees"] = (~merged["is_neutral"]) & (merged["reviewer_label"] == merged["current_narrative"])
    return merged


def overall_section(df: pd.DataFrame) -> str:
    n = len(df)
    annotated = df[df["reviewer_label"].ne("") | df["is_neutral"]]
    if annotated.empty:
        return "## Overall\n\nNo annotations filled in yet - nothing to report.\n"
    n_ann = len(annotated)
    agree = annotated["agrees"].sum()
    neutral = annotated["is_neutral"].sum()
    ambiguous = annotated["is_ambiguous"].sum()
    disagree = n_ann - agree - neutral
    conf_dist = annotated["confidence"].value_counts(dropna=False).to_dict()
    return (
        "## Overall\n\n"
        f"- Annotated: {n_ann} / {n}\n"
        f"- Agreement with original label: {agree} ({agree / n_ann:.1%})\n"
        f"- Disagreement (different narrative than original): {disagree} ({disagree / n_ann:.1%})\n"
        f"- Neutral / no clear narrative: {neutral} ({neutral / n_ann:.1%})\n"
        f"- Ambiguous: {ambiguous} ({ambiguous / n_ann:.1%})\n"
        f"- Confidence distribution: {conf_dist}\n"
    )


def per_narrative_section(df: pd.DataFrame) -> str:
    annotated = df[df["reviewer_label"].ne("") | df["is_neutral"]]
    if annotated.empty:
        return "## Per narrative\n\nNo annotations filled in yet.\n"
    lines = ["## Per narrative\n"]
    lines.append("| Narrative | n | validity (% still X) | neutral rate | ambiguous rate | top relabel destinations |")
    lines.append("|---|---|---|---|---|---|")
    for narrative in NARRATIVES:
        sub = annotated[annotated["current_narrative"] == narrative]
        if sub.empty:
            continue
        n = len(sub)
        validity = sub["agrees"].sum() / n
        neutral_rate = sub["is_neutral"].sum() / n
        ambiguous_rate = sub["is_ambiguous"].sum() / n
        relabels = sub[(~sub["is_neutral"]) & (sub["reviewer_label"] != narrative) & (sub["reviewer_label"] != "")]
        top_relabels = relabels["reviewer_label"].value_counts().head(3).to_dict()
        lines.append(f"| {narrative} | {n} | {validity:.1%} | {neutral_rate:.1%} | {ambiguous_rate:.1%} | {top_relabels} |")
    return "\n".join(lines) + "\n"


def per_author_section(df: pd.DataFrame) -> str:
    annotated = df[df["reviewer_label"].ne("") | df["is_neutral"]]
    if annotated.empty:
        return "## Per author - suspicious accounts\n\nNo annotations filled in yet.\n"
    rows = []
    for author, sub in annotated.groupby("author"):
        n = len(sub)
        if n < MIN_TEXTS_FOR_ACCOUNT_FLAG:
            continue
        disagree_rate = 1 - (sub["agrees"].sum() / n)
        neutral_rate = sub["is_neutral"].sum() / n
        rows.append((author, n, disagree_rate, neutral_rate))
    rows.sort(key=lambda r: -(r[2] + r[3]))
    lines = ["## Per author - suspicious accounts\n"]
    lines.append(f"(>= {MIN_TEXTS_FOR_ACCOUNT_FLAG} annotated texts, sorted by disagreement + neutral rate)\n")
    lines.append("| Author | n | disagreement rate | neutral rate | flag |")
    lines.append("|---|---|---|---|---|")
    for author, n, disagree_rate, neutral_rate in rows:
        flag = "SUSPICIOUS" if (disagree_rate + neutral_rate) >= SUSPICIOUS_RATE_THRESHOLD else ""
        lines.append(f"| {author} | {n} | {disagree_rate:.1%} | {neutral_rate:.1%} | {flag} |")
    return "\n".join(lines) + "\n"


def inter_annotator_section() -> str:
    if not SECOND_PATH.is_file():
        return "## Inter-annotator agreement\n\nSecond-annotator file not found.\n"
    second = pd.read_csv(SECOND_PATH, dtype={"confidence": "string"})
    second = second[second["reviewer_label"].fillna("").astype(str).str.strip().ne("")
                     | second["neutral_or_no_clear_narrative"].apply(_is_true)]
    if second.empty:
        return "## Inter-annotator agreement\n\nSecond-annotator file not filled in yet.\n"

    primary = pd.read_csv(BLIND_PATH, dtype={"confidence": "string"})
    key = pd.read_csv(KEY_PATH)

    def normalize(sub_df: pd.DataFrame, suffix: str) -> pd.DataFrame:
        out = sub_df[["annotation_id", "reviewer_label", "confidence"]].copy()
        out["reviewer_label"] = out["reviewer_label"].fillna("").astype(str).str.strip()
        is_neutral = sub_df["neutral_or_no_clear_narrative"].apply(_is_true)
        out.loc[is_neutral, "reviewer_label"] = "Neutral"
        return out.add_suffix(suffix).rename(columns={f"annotation_id{suffix}": "annotation_id"})

    p1 = normalize(primary, "_1")
    p2 = normalize(second, "_2")
    merged = p1.merge(p2, on="annotation_id", how="inner").merge(key, on="annotation_id", how="left")
    merged = merged[merged["reviewer_label_1"].ne("") & merged["reviewer_label_2"].ne("")]
    if merged.empty:
        return "## Inter-annotator agreement\n\nNo overlapping annotated rows yet.\n"

    n = len(merged)
    raw_agreement = (merged["reviewer_label_1"] == merged["reviewer_label_2"]).mean()

    try:
        from sklearn.metrics import cohen_kappa_score
        kappa = cohen_kappa_score(merged["reviewer_label_1"], merged["reviewer_label_2"])
        kappa_str = f"{kappa:.3f}"
    except ImportError:
        kappa_str = "scikit-learn not available"

    confusion = pd.crosstab(merged["reviewer_label_1"], merged["reviewer_label_2"])

    lines = ["## Inter-annotator agreement\n"]
    lines.append(f"- Overlap size: {n} rows")
    lines.append(f"- Raw agreement: {raw_agreement:.1%}")
    lines.append(f"- Cohen's kappa: {kappa_str}\n")

    lines.append("### Agreement per narrative (based on original label)\n")
    lines.append("| Narrative | n | raw agreement |")
    lines.append("|---|---|---|")
    for narrative, sub in merged.groupby("current_narrative"):
        agree = (sub["reviewer_label_1"] == sub["reviewer_label_2"]).mean()
        lines.append(f"| {narrative} | {len(sub)} | {agree:.1%} |")

    lines.append("\n### Agreement by annotator-1 confidence\n")
    lines.append("| Confidence | n | raw agreement |")
    lines.append("|---|---|---|")
    for conf, sub in merged.groupby("confidence_1"):
        agree = (sub["reviewer_label_1"] == sub["reviewer_label_2"]).mean()
        lines.append(f"| {conf} | {len(sub)} | {agree:.1%} |")

    lines.append("\n### Confusion matrix (annotator 1 rows x annotator 2 columns)\n")
    lines.append(_dataframe_to_markdown(confusion))

    return "\n".join(lines) + "\n"


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Manual markdown table rendering (avoids a hard dependency on the optional
    `tabulate` package that pandas' own `.to_markdown()` requires)."""
    header = "| | " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|---|" + "|".join(["---"] * len(df.columns)) + "|"
    rows = [f"| {idx} | " + " | ".join(str(v) for v in row) + " |" for idx, row in zip(df.index, df.values)]
    return "\n".join([header, sep, *rows])


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_merged()

    sections = [
        "# Human Validation Report (blind pilot, 300 rows)\n",
        overall_section(df),
        per_narrative_section(df),
        per_author_section(df),
        inter_annotator_section(),
    ]
    report = "\n".join(sections)
    OUT_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWrote report to {OUT_PATH}")


if __name__ == "__main__":
    main()

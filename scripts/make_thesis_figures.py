"""Thesis figures generated ONLY from measured repo artifacts.

Reads (no other inputs):
  - artifacts/tables/comparison_random_test.csv        (random-split source;
    used in place of artifacts/tables/model_comparison_results.json)
  - artifacts/experiments/narrative_ablation_loao/results.json
  - artifacts/experiments/narrative_fresh_author_confirmatory/fresh_author_confirmatory_summary.csv
  - artifacts/experiments/narrative_style_normalization_generalization/fresh_author_comparison.csv

Emits to artifacts/figures/:
  - fig1_random_split_bars.png
  - fig2_random_vs_loao_recall.png
  - fig3_fresh_author_masking_delta.png
  - fig4_style_normalization_delta.png

Rendering: stdlib + Pillow only (matplotlib is not installed in this
environment and installs are out of scope). Bar charts are drawn with
PIL.ImageDraw; every value plotted comes from the files above.
"""
import csv
import json
import os
import statistics

from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(REPO, "artifacts", "figures")

CSV_RANDOM = os.path.join(REPO, "artifacts", "tables", "comparison_random_test.csv")
JSON_LOAO = os.path.join(REPO, "artifacts", "experiments", "narrative_ablation_loao", "results.json")
CSV_FRESH = os.path.join(
    REPO, "artifacts", "experiments", "narrative_fresh_author_confirmatory",
    "fresh_author_confirmatory_summary.csv")
CSV_NORM = os.path.join(
    REPO, "artifacts", "experiments", "narrative_style_normalization_generalization",
    "fresh_author_comparison.csv")

W, H = 900, 600
MARGIN = {"l": 70, "r": 30, "t": 90, "b": 120}
BLUE = (31, 119, 180)
ORANGE = (255, 127, 14)
GREEN = (44, 160, 44)
RED = (214, 39, 40)
GRAY = (150, 150, 150)
BLACK = (20, 20, 20)


def load_random_models():
    with open(CSV_RANDOM, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def draw_grouped_bars(path, title, caption, groups, series, colors, ylabel="score"):
    """groups: [labels]; series: [(name, [values])]."""
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((MARGIN["l"], 12), title, fill=BLACK)
    d.text((MARGIN["l"], 32), caption, fill=(90, 90, 90))
    lo, hi = 0.0, 1.0
    plot_w = W - MARGIN["l"] - MARGIN["r"]
    plot_h = H - MARGIN["t"] - MARGIN["b"]
    ox, oy = MARGIN["l"], MARGIN["t"]
    for i in range(5):
        y = oy + plot_h * i / 4
        d.line([(ox, y), (ox + plot_w, y)], fill=(225, 225, 225))
        d.text((8, y - 7), f"{hi - (hi - lo) * i / 4:.2f}", fill=BLACK)
    d.text((8, oy + plot_h - 7), ylabel, fill=(90, 90, 90))
    n, m = len(groups), len(series)
    slot = plot_w / n
    bw = min(60, slot / (m + 1))
    for gi, g in enumerate(groups):
        cx = ox + slot * (gi + 0.5)
        for si, (name, vals) in enumerate(series):
            v = vals[gi]
            x0 = cx + (si - (m - 1) / 2) * bw
            y1 = oy + plot_h
            y0 = y1 - plot_h * max(0.0, min(1.0, v))
            d.rectangle([x0 - bw / 2 + 2, y0, x0 + bw / 2 - 2, y1], fill=colors[si % len(colors)])
            d.text((x0 - 20, y0 - 16), f"{v:.3f}" if v < 1 else f"{v:.2f}", fill=BLACK)
        d.text((cx - 40, oy + plot_h + 8), str(g)[:16], fill=BLACK)
    for si, (name, _) in enumerate(series):
        lx = ox + si * 220
        d.rectangle([lx, H - 34, lx + 18, H - 20], fill=colors[si % len(colors)])
        d.text((lx + 24, H - 34), name, fill=BLACK)
    img.save(path)


def draw_delta_bars(path, title, caption, labels, deltas, mean, median):
    img = Image.new("RGB", (2 * W - 200, H + 40), "white")
    d = ImageDraw.Draw(img)
    IW = 2 * W - 200
    d.text((MARGIN["l"], 12), title, fill=BLACK)
    d.text((MARGIN["l"], 32), caption, fill=(90, 90, 90))
    lo = min(min(deltas), mean, median, 0.0)
    hi = max(max(deltas), mean, median, 0.0)
    pad = 0.02
    lo -= pad
    hi += pad
    plot_w = IW - MARGIN["l"] - MARGIN["r"]
    plot_h = (H + 40) - MARGIN["t"] - MARGIN["b"]
    ox, oy = MARGIN["l"], MARGIN["t"]
    y0 = oy + plot_h * (hi - 0) / (hi - lo)
    d.line([(ox, y0), (ox + plot_w, y0)], fill=BLACK)
    n = len(labels)
    slot = plot_w / n
    bw = min(70, slot * 0.6)
    for i, (lab, dv) in enumerate(zip(labels, deltas)):
        cx = ox + slot * (i + 0.5)
        yv = oy + plot_h * (hi - dv) / (hi - lo)
        top, bot = (yv, y0) if dv >= 0 else (y0, yv)
        d.rectangle([cx - bw / 2, top, cx + bw / 2, bot],
                    fill=GREEN if dv >= 0 else RED)
        d.text((cx - 25, (top - 16) if dv >= 0 else (bot + 2)), f"{dv:+.1%}", fill=BLACK)
        d.text((cx - 45, oy + plot_h + 6), lab[:18], fill=BLACK)
    for val, name in ((mean, f"mean {mean:+.1%}"), (median, f"median {median:+.1%}")):
        yv = oy + plot_h * (hi - val) / (hi - lo)
        d.line([(ox, yv), (ox + plot_w, yv)], fill=GRAY)
        d.text((ox + plot_w - 150, yv - 16), name, fill=(90, 90, 90))
    img.save(path)


def fig1():
    rows = load_random_models()
    models = [r["model_type"] for r in rows]
    acc = [float(r["accuracy"]) for r in rows]
    f1 = [float(r["macro_f1"]) for r in rows]
    draw_grouped_bars(
        os.path.join(FIGDIR, "fig1_random_split_bars.png"),
        "Fig 1: Random-split accuracy and Macro-F1 by model (3 models)",
        "Source: artifacts/tables/comparison_random_test.csv (random-split test; EXPERIMENTS.md sections 15-20)",
        models, [("accuracy", acc), ("macro_f1", f1)], [BLUE, ORANGE])


def fig2():
    rows = {r["model_type"]: r for r in load_random_models()}
    rand_recall = float(rows["sbert_only"]["macro_recall"])
    with open(JSON_LOAO, encoding="utf-8") as f:
        loao = json.load(f)
    authors = sorted(loao.keys())
    loao_recalls = [float(loao[a]["sbert_only"]["recall_true_narrative"]) for a in authors]
    draw_grouped_bars(
        os.path.join(FIGDIR, "fig2_random_vs_loao_recall.png"),
        "Fig 2: sbert_only random macro-recall vs LOAO true-narrative recall (3 held-out authors)",
        "Sources: comparison_random_test.csv (random) + narrative_ablation_loao/results.json (LOAO; EXPERIMENTS.md sections 18-19)",
        ["random"] + authors,
        [("recall", [rand_recall] + loao_recalls)], [BLUE])
    return rand_recall, list(zip(authors, loao_recalls))


def pivot(csv_path, variant_col, value_col, variants):
    per = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r[variant_col] in variants:
                per.setdefault(r["author"], {})[r[variant_col]] = float(r[value_col])
    return per


def fig3():
    per = pivot(CSV_FRESH, "variant", "recall_true_narrative",
                ("sbert_original", "sbert_person_misc_masked_aug_soft_topic"))
    authors = sorted(per.keys())
    deltas = [per[a]["sbert_person_misc_masked_aug_soft_topic"] - per[a]["sbert_original"]
              for a in authors]
    order = sorted(range(len(authors)), key=lambda i: deltas[i], reverse=True)
    labels = [authors[i] for i in order]
    vals = [deltas[i] for i in order]
    draw_delta_bars(
        os.path.join(FIGDIR, "fig3_fresh_author_masking_delta.png"),
        "Fig 3: Per-author recall delta, masking candidate minus baseline (14 fresh authors)",
        "Source: narrative_fresh_author_confirmatory/fresh_author_confirmatory_summary.csv (EXPERIMENTS.md section 25)",
        labels, vals, statistics.mean(vals), statistics.median(vals))
    return list(zip(labels, vals))


def fig4():
    per = pivot(CSV_NORM, "variant", "recall_true_narrative", ("original", "normalized"))
    authors = sorted(per.keys())
    deltas = [per[a]["normalized"] - per[a]["original"] for a in authors]
    order = sorted(range(len(authors)), key=lambda i: deltas[i], reverse=True)
    labels = [authors[i] for i in order]
    vals = [deltas[i] for i in order]
    draw_delta_bars(
        os.path.join(FIGDIR, "fig4_style_normalization_delta.png"),
        "Fig 4: Per-author recall delta, style-normalized minus original (14 fresh authors)",
        "Source: narrative_style_normalization_generalization/fresh_author_comparison.csv (EXPERIMENTS.md section 28)",
        labels, vals, statistics.mean(vals), statistics.median(vals))
    return list(zip(labels, vals))


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    fig1()
    r = fig2()
    m = fig3()
    s = fig4()
    print("fig2 random recall:", round(r[0], 4), "loao:", [(a, round(v, 4)) for a, v in r[1]])
    print("fig3 mean/median:", round(statistics.mean(v for _, v in m), 4),
          round(statistics.median(v for _, v in m), 4))
    print("fig4 mean/median:", round(statistics.mean(v for _, v in s), 4),
          round(statistics.median(v for _, v in s), 4))


if __name__ == "__main__":
    main()

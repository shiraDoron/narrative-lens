"""Selective prediction under author shift (frozen Section 25 checkpoints).

For each of the 14 confirmatory held-out authors, loads the frozen
``sbert_original_<author>.pth`` MLP checkpoint and scores that author's test
rows (the author's own rows, text truncated to 3000 chars, same convention as
the confirmatory runner). Records predicted narrative, confidence (max softmax
prob) and margin (top1 minus top2 prob) per row, then computes:

  (a) AUROC of the score separating correct vs incorrect predictions,
      pooled and per author, for confidence and margin;
  (b) risk-coverage: accuracy on the top-C most confident rows for
      C in {1.0, 0.8, 0.6, 0.4}, plus the abstention rate needed for the
      retained accuracy to reach random-split-level accuracy;
  (c) the same AUROC/accuracy on the random-split test set, scored with the
      frozen random-split SBERT-only checkpoint
      (models/best_model_sbert_only.pth, MLP weights only; the SBERT encoder
      stays frozen and shared).

Positive bar: pooled AUROC clearly above 0.5 (point estimate > 0.55) AND
abstaining 20-40% closes most (fraction >= 0.5) of the fresh-author gap
(random-split accuracy minus pooled fresh-author accuracy).

CPU only, seed 42. Every number below comes from running this script::

    .venv/bin/python models/experiments/narrative_fresh_author_confirmatory/run_selective.py
"""

import glob
import json
import os
import sys

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from sentence_transformers import SentenceTransformer

SEED = 42
SBERT_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHECKPOINT_TEMPLATE = "models/experiments/narrative_fresh_author_confirmatory/sbert_original_{author}.pth"
RANDOM_CHECKPOINT = "models/best_model_sbert_only.pth"
OUT_DIR = "artifacts/experiments/selective_prediction"
RESULTS_FILE = os.path.join(OUT_DIR, "selective_results.json")
ROWS_FILE = os.path.join(OUT_DIR, "selective_row_predictions.csv")
COVERAGES = (1.0, 0.8, 0.6, 0.4)
AUROC_PASS_THRESHOLD = 0.55
GAP_CLOSED_PASS_FRACTION = 0.5

sys.path.insert(0, "src")
from narrative_lens.train import load_raw_data, split_random  # noqa: E402


def set_seed(seed=SEED):
    torch.manual_seed(seed)
    np.random.seed(seed)


class FrozenSbertMlp(torch.nn.Module):
    """MLP half of AblationDetector(empty arms) / SBERTOnlyDetector.classify_features.

    Linear(384 -> 128) -> ReLU -> Dropout -> Linear(128 -> 7) -> Softmax,
    identical to the trained modules; run in eval mode so dropout is inert.
    """

    def __init__(self, sbert_dim=384, hidden=128, n_classes=7):
        super().__init__()
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(sbert_dim, hidden),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(hidden, n_classes),
        )
        self.softmax = torch.nn.Softmax(dim=-1)

    def forward(self, emb):
        return self.softmax(self.mlp(emb))


def load_mlp_checkpoint(path):
    sd = torch.load(path, map_location="cpu", weights_only=True)
    mlp_sd = {k[len("mlp."):]: v for k, v in sd.items() if k.startswith("mlp.")}
    sbert_dim = int(mlp_sd["0.weight"].shape[1])
    n_classes = int(mlp_sd["3.weight"].shape[0])
    model = FrozenSbertMlp(sbert_dim=sbert_dim, n_classes=n_classes)
    model.mlp.load_state_dict(mlp_sd, strict=True)
    model.eval()
    return model


def score_rows(model, embeddings):
    with torch.no_grad():
        probs = model(torch.from_numpy(embeddings)).numpy()
    order = np.argsort(-probs, axis=1)
    top1 = probs[np.arange(len(probs)), order[:, 0]]
    top2 = probs[np.arange(len(probs)), order[:, 1]]
    pred = order[:, 0]
    return pred, probs, top1, top1 - top2


def auroc_safe(scores, labels):
    if len(set(labels)) < 2:
        return None
    return float(roc_auc_score(labels, scores))


def risk_coverage(correct, score, coverages=COVERAGES):
    """Accuracy on the top-C fraction by score. Ties broken by stable order."""
    n = len(correct)
    order = np.argsort(-np.asarray(score, dtype=float), kind="stable")
    out = {}
    for c in coverages:
        k = max(1, int(round(c * n)))
        sel = order[:k]
        out[str(c)] = {
            "coverage": c,
            "n_retained": int(k),
            "accuracy": float(np.mean(correct[sel])),
        }
    return out


def abstention_to_recover(correct, score, target_acc):
    """Smallest abstention rate whose retained top-confidence accuracy >= target.

    Sweeps every possible cutoff over rows sorted by descending score.
    Returns None when even the single most confident row misses the target.
    """
    order = np.argsort(-np.asarray(score, dtype=float), kind="stable")
    ranked = np.asarray(correct, dtype=float)[order]
    cumsum = np.cumsum(ranked)
    n = len(ranked)
    k_vals = np.arange(1, n + 1)
    acc = cumsum / k_vals
    ok = np.nonzero(acc >= target_acc)[0]
    if len(ok) == 0:
        return None
    k_best = int(k_vals[ok].max())  # retain as much as possible while hitting target
    k_first = int(k_vals[ok[0]])  # first (smallest retained set) hitting target
    return {
        "target_accuracy": float(target_acc),
        "min_abstention_rate": float(1.0 - k_first / n),
        "n_retained_at_min_abstention": int(k_first),
        "retained_accuracy_at_min_abstention": float(acc[ok[0]]),
        "max_retained_still_above_target": int(k_best),
    }


def list_authors():
    paths = sorted(glob.glob(CHECKPOINT_TEMPLATE.format(author="*")))
    authors = [os.path.basename(p)[len("sbert_original_"):-len(".pth")] for p in paths]
    assert len(authors) == 14, f"expected 14 sbert_original checkpoints, found {len(authors)}"
    return authors


def main():
    set_seed()
    os.makedirs(OUT_DIR, exist_ok=True)
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    df = load_raw_data()
    authors = list_authors()
    print(f"Authors ({len(authors)}): {authors}")

    sbert = SentenceTransformer(SBERT_NAME)

    all_rows = []  # (author, true, pred, conf, margin)
    per_author = {}
    for author in authors:
        test_df = df[df["author_source"] == author].reset_index(drop=True)
        texts = test_df["text"].astype(str).str.slice(0, 3000).tolist()
        true = test_df["label"].astype(int).to_numpy()
        emb = sbert.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        model = load_mlp_checkpoint(CHECKPOINT_TEMPLATE.format(author=author))
        pred, _, conf, margin = score_rows(model, emb.astype(np.float32))
        correct = (pred == true).astype(int)
        for t, p, c, m, ok in zip(true, pred, conf, margin, correct):
            all_rows.append((author, int(t), int(p), float(c), float(m), int(ok)))
        per_author[author] = {
            "n_test": int(len(true)),
            "accuracy": float(np.mean(correct)),
            "mean_confidence": float(np.mean(conf)),
            "mean_confidence_correct": float(np.mean(conf[correct == 1])) if (correct == 1).any() else None,
            "mean_confidence_incorrect": float(np.mean(conf[correct == 0])) if (correct == 0).any() else None,
            "auroc_confidence": auroc_safe(conf, correct),
            "auroc_margin": auroc_safe(margin, correct),
        }
        print(f"[{author}] n={len(true)} acc={np.mean(correct):.3f} "
              f"auroc_conf={per_author[author]['auroc_confidence']} "
              f"auroc_margin={per_author[author]['auroc_margin']}")

    correct_all = np.array([r[5] for r in all_rows])
    conf_all = np.array([r[3] for r in all_rows])
    margin_all = np.array([r[4] for r in all_rows])
    pooled_acc = float(np.mean(correct_all))
    pooled_auroc_conf = auroc_safe(conf_all, correct_all)
    pooled_auroc_margin = auroc_safe(margin_all, correct_all)
    rc_conf = risk_coverage(correct_all, conf_all)
    rc_margin = risk_coverage(correct_all, margin_all)

    # (c) Random-split comparison with the frozen SBERT-only random checkpoint.
    random_result = {"checkpoint": RANDOM_CHECKPOINT, "status": "missing"}
    if os.path.exists(RANDOM_CHECKPOINT):
        _, _, random_test = split_random(df)
        r_texts = random_test["text"].astype(str).str.slice(0, 3000).tolist()
        r_true = random_test["label"].astype(int).to_numpy()
        r_emb = sbert.encode(r_texts, convert_to_numpy=True, show_progress_bar=False)
        r_model = load_mlp_checkpoint(RANDOM_CHECKPOINT)
        r_pred, _, r_conf, r_margin = score_rows(r_model, r_emb.astype(np.float32))
        r_correct = (r_pred == r_true).astype(int)
        random_result = {
            "status": "ok",
            "checkpoint": RANDOM_CHECKPOINT,
            "n_test": int(len(r_true)),
            "accuracy": float(np.mean(r_correct)),
            "auroc_confidence": auroc_safe(r_conf, r_correct),
            "auroc_margin": auroc_safe(r_margin, r_correct),
        }
        print(f"[random-split] n={len(r_true)} acc={np.mean(r_correct):.3f} "
              f"auroc_conf={random_result['auroc_confidence']}")
    else:
        print("[random-split] checkpoint missing; comparison skipped.")

    fresh_gap = None
    gap_closed = {}
    abstention = None
    if random_result["status"] == "ok":
        random_acc = random_result["accuracy"]
        fresh_gap = float(random_acc - pooled_acc)
        for c in ("0.8", "0.6"):
            if fresh_gap > 1e-12:
                gap_closed[c] = float((rc_conf[c]["accuracy"] - pooled_acc) / fresh_gap)
            else:
                gap_closed[c] = None
        abstention = abstention_to_recover(correct_all, conf_all, random_acc)

    auroc_pass = pooled_auroc_conf is not None and pooled_auroc_conf > AUROC_PASS_THRESHOLD
    coverage_pass = any(
        gap_closed.get(c) is not None and gap_closed[c] >= GAP_CLOSED_PASS_FRACTION
        for c in ("0.8", "0.6")
    )
    overall_pass = bool(auroc_pass and coverage_pass)

    results = {
        "seed": SEED,
        "variant": "sbert_original",
        "n_authors": len(authors),
        "n_test_pooled": int(len(correct_all)),
        "pooled_accuracy_fresh_author": pooled_acc,
        "pooled_auroc_confidence": pooled_auroc_conf,
        "pooled_auroc_margin": pooled_auroc_margin,
        "per_author": per_author,
        "risk_coverage_confidence": rc_conf,
        "risk_coverage_margin": rc_margin,
        "random_split": random_result,
        "fresh_author_gap_random_minus_fresh": fresh_gap,
        "gap_closed_fraction_at_coverage": gap_closed,
        "abstention_to_recover_random_accuracy": abstention,
        "positive_bar": {
            "rule": f"pooled AUROC_conf > {AUROC_PASS_THRESHOLD} AND "
                    f"gap-closed fraction >= {GAP_CLOSED_PASS_FRACTION} at 20% or 40% abstention",
            "auroc_pass": bool(auroc_pass),
            "coverage_pass": bool(coverage_pass),
            "pass": overall_pass,
        },
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(ROWS_FILE, "w", encoding="utf-8") as f:
        f.write("author,true_label,pred_label,confidence,margin,correct\n")
        for author, t, p, c, m, ok in all_rows:
            f.write(f"{author},{t},{p},{c:.6f},{m:.6f},{ok}\n")

    print(f"\npooled fresh-author acc={pooled_acc:.4f} auroc_conf={pooled_auroc_conf} "
          f"auroc_margin={pooled_auroc_margin}")
    print(f"risk-coverage (conf): " + ", ".join(
        f"C={c}: {rc_conf[c]['accuracy']:.4f}" for c in rc_conf))
    print(f"gap_closed={gap_closed} abstention={abstention}")
    print(f"PASS={overall_pass} -> {RESULTS_FILE}")


if __name__ == "__main__":
    main()

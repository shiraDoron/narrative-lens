"""
Narrative Classification - group-DRO on (narrative, author_source) groups, LOAO.

Implements artifacts/experiments/debias_spec.md exactly:
- Backbone: SBERT-only MLP (Linear(384,128) -> ReLU -> Dropout(0.3) ->
  Linear(128,7) -> Softmax), identical to the ablation sbert_only / Section 25
  sbert_original backbone. SBERT (all-MiniLM-L6-v2) frozen, 384-dim.
- Groups: (narrative_idx, author_source) pairs from TRAIN rows only,
  MIN_GROUP_SIZE=5. Synthetic authors never form groups, never held out.
- Loss: per optimizer step (BATCH_SIZE=16 window), L_g = mean NLL of group g
  rows in the step; q <- q*exp(eta*L_g_adj) renormalized (groups present only);
  backprop loss = sum_g q_g * L_g_adj with L_g_adj = L_g + C/sqrt(n_g).
- Checkpoint: worst-group val recall (groups with >=5 val rows), tie-break
  val macro-F1. EPOCHS=20/BATCH_SIZE=16/lr=0.001/patience=3/seed=42 frozen.
- Phase 1 (selection): 6 configs (eta x C) on 3 exploratory authors
  (IDF, MariaZakharova, BernieSanders); winner by mean recall, frozen.
- Phase 2 (confirmatory): frozen winner on the 14 frozen authors, endpoints:
  mean >= 36.0% AND median >= 35.8% (baseline 39.0/38.8 minus 3pp),
  guardrail <=2/14 authors degrading >10pp, mean dominant-error
  concentration must not increase vs baseline 44.2%.

Run (from repo root):
  python experiments/author_generalization/narrative_group_dro_loao.py --authors IDF,MariaZakharova,BernieSanders --eta-grid 0.001,0.01,0.05 --c-grid 0,2 --seed 42
  python experiments/author_generalization/narrative_group_dro_loao.py --select-config
  python experiments/author_generalization/narrative_group_dro_loao.py --frozen-authors --seed 42
  python experiments/author_generalization/narrative_group_dro_loao.py --aggregate
"""
import argparse
import json
import math
import os
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer

from narrative_lens.config import NARRATIVES, NUM_NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from narrative_lens.train import (
    load_raw_data,
    split_leave_one_author,
    is_synthetic_author,
    evaluate,
    compute_metrics,
    save_confusion_matrix_csv,
)

SEED = 42
EXPLORATORY_AUTHORS = ("IDF", "MariaZakharova", "BernieSanders")
ETA_GRID = (0.001, 0.01, 0.05)
C_GRID = (0, 2)
MIN_GROUP_SIZE = 5
SBERT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CACHE_DIR = "data/cache"
FEATURE_CACHE_TEMPLATE = os.path.join(CACHE_DIR, "cached_features_group_dro_{author}.pt")
CHECKPOINT_DIR = "models/experiments/narrative_group_dro"
REPORT_DIR = "artifacts/experiments/group_dro"
RESULTS_FILE = os.path.join(REPORT_DIR, "results.json")
SELECTION_FILE = os.path.join(REPORT_DIR, "selection.json")
CONFIRMATORY_FILE = os.path.join(REPORT_DIR, "confirmatory.json")
FROZEN_SET_FILE = "artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json"

RIGHT_WING_IDX = NARRATIVES.index("Right-wing")


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


def variant_name(eta, c):
    return f"sbert_dro_eta{str(eta).replace('.', 'p')}_C{c}"


class SbertOnlyDetector(nn.Module):
    """SBERT-only backbone, same MLP template as the ablation sbert_only arm set."""

    def __init__(self, sbert_dim, hidden_size=128, dropout=0.3):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(sbert_dim, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, NUM_NARRATIVES),
        )
        self.softmax = nn.Softmax(dim=-1)

    def classify_features(self, features):
        if isinstance(features, dict):
            x = features["sbert_embedding"]
        else:
            x = features
        return self.softmax(self.mlp(x))


def build_or_load_author_cache(author, sbert_model):
    cache_file = FEATURE_CACHE_TEMPLATE.format(author=author)
    if os.path.exists(cache_file):
        print(f"Found existing group-DRO feature cache '{cache_file}'. Loading...")
        return torch.load(cache_file, weights_only=False)

    print(f"\n=== Building fresh group-DRO feature cache for held-out author '{author}' ===")
    df = load_raw_data()
    train_data, val_data, test_data = split_leave_one_author(df, author)
    for split_df in (train_data, val_data, test_data):
        split_df["text"] = split_df["text"].astype(str).str.slice(0, 3000)
    splits = {"train": train_data, "val": val_data, "test": test_data}

    result = {}
    sbert_dim = None
    for name, split_df in splits.items():
        print(f"--- Split '{name}' ({len(split_df)} rows): encoding SBERT ...")
        texts = split_df["text"].tolist()
        labels = split_df["label"].astype(int).tolist()
        emb = sbert_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        sbert_dim = int(emb.shape[1])
        rows = []
        for i in range(len(texts)):
            feat = {"sbert_embedding": torch.tensor(emb[i], dtype=torch.float32)}
            rows.append((feat, labels[i]))
        result[name] = rows

    # Group map from TRAIN rows only: (narrative_idx, author_source), min size 5.
    train_labels = train_data["label"].astype(int).tolist()
    train_authors = train_data["author_source"].astype(str).tolist()
    pair_counts = {}
    for lab, auth in zip(train_labels, train_authors):
        if is_synthetic_author(auth):
            continue
        key = (int(lab), auth)
        pair_counts[key] = pair_counts.get(key, 0) + 1
    kept = sorted([k for k, n in pair_counts.items() if n >= MIN_GROUP_SIZE])
    group_to_idx = {k: i for i, k in enumerate(kept)}
    n_g = np.array([pair_counts[k] for k in kept], dtype=np.float64)
    print(f"  -> G={len(kept)} kept groups (min size {MIN_GROUP_SIZE}), "
          f"dropped {len(pair_counts) - len(kept)} small pairs.")

    rare_idx = len(kept)  # pooled val-only reporting group, never used for q updates

    def group_ids_for(split_df):
        labs = split_df["label"].astype(int).tolist()
        auths = split_df["author_source"].astype(str).tolist()
        return np.array([group_to_idx.get((int(l), a), rare_idx) for l, a in zip(labs, auths)],
                        dtype=np.int64)

    # Train rows in dropped small pairs (<MIN_GROUP_SIZE) and synthetic rows get
    # group id -1: plain ERM gradient, never a q-weight update.
    train_group = np.array(
        [group_to_idx.get((int(l), a), -1) if not is_synthetic_author(a) else -1
         for l, a in zip(train_labels, train_authors)], dtype=np.int64)
    result["train_group"] = train_group
    result["train_is_grouped"] = train_group >= 0
    result["val_group"] = group_ids_for(val_data)
    result["_meta"] = {
        "sbert_dim": sbert_dim,
        "G": len(kept),
        "groups": [f"{NARRATIVES[lab]}||{auth}" for (lab, auth) in kept],
        "group_counts": [int(pair_counts[k]) for k in kept],
        "min_group_size": MIN_GROUP_SIZE,
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    torch.save(result, cache_file)
    print(f"Saved group-DRO feature cache to '{cache_file}'.")
    return result


def worst_group_val_recall(detector, val_features, val_group, n_groups):
    """min_g recall_g over groups (incl. pooled rare) with >=5 val rows."""
    detector.eval()
    with torch.no_grad():
        preds = []
        trues = []
        for features, label_idx in val_features:
            probs = detector.classify_features(features)
            if probs.dim() == 1:
                probs = probs.unsqueeze(0)
            preds.append(int(torch.argmax(probs, dim=-1).item()))
            trues.append(int(label_idx))
    preds = np.array(preds)
    trues = np.array(trues)
    recalls = {}
    for g in range(n_groups + 1):  # +1 = pooled rare group
        mask = val_group == g
        if int(mask.sum()) >= 5:
            recalls[g] = float(((preds[mask] == trues[mask]).sum()) / mask.sum())
    worst = min(recalls.values()) if recalls else 0.0
    return worst, recalls


def dro_step(optimizer, q, per_example_losses, group_ids, eta, c, sqrt_n):
    """One group-DRO optimizer step over a BATCH_SIZE accumulation window.

    Per spec section 4: L_g = mean NLL of group g's rows in the step, adjusted to
    L_g + C/sqrt(n_g) when C > 0; the backprop loss is sum_g q_g * L_g using the
    PRE-update q; then q_g <- q_g * exp(eta * L_g) for the groups present in the
    step, and q is renormalized. q stays a CPU float tensor, so only the
    scalar-weighted loss is in the autograd graph (no second-order cost).
    Returns the mean group loss of the step, for logging.
    """
    grads, detached = {}, {}
    for g in sorted(set(group_ids)):
        if g < 0:
            continue
        idx = [i for i, gi in enumerate(group_ids) if gi == g]
        Lg = torch.stack([per_example_losses[i] for i in idx]).mean()
        adj = Lg + (c / sqrt_n[g] if c else 0.0)
        grads[g] = adj
        detached[g] = float(adj.detach().item())
    if not grads:
        optimizer.step()
        optimizer.zero_grad()
        return 0.0

    loss = sum(float(q[g]) * grads[g] for g in grads)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

    for g, lv in detached.items():
        q[g] *= math.exp(eta * lv)
    q /= q.sum()
    return sum(detached.values()) / len(detached)


def train_variant_dro(author, eta, c, cache, epochs=EPOCHS, batch_size=BATCH_SIZE,
                      patience=3, lr=LEARNING_RATE, seed=SEED):
    vname = variant_name(eta, c)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{vname}_{author}.pth")

    train_features = cache["train"]
    val_features = cache["val"]
    test_features = cache["test"]
    sbert_dim = cache["_meta"]["sbert_dim"]
    G = cache["_meta"]["G"]
    n_g = np.array(cache["_meta"]["group_counts"], dtype=np.float64)
    train_group_full = cache["train_group"]
    train_is_grouped = cache["train_is_grouped"]
    val_group = cache["val_group"]

    # Group ids are positional: cache rows are stored in split order.
    assert len(train_features) == len(train_group_full) == len(train_is_grouped)

    set_seed(seed)
    detector = SbertOnlyDetector(sbert_dim)

    if os.path.exists(checkpoint_file):
        print(f"[{vname}/{author}] Found existing checkpoint - loading for eval only "
              f"(delete '{checkpoint_file}' manually to force a genuine re-run).")
        detector.load_state_dict(torch.load(checkpoint_file, weights_only=True))
    else:
        t0 = time.time()
        optimizer = optim.Adam(detector.parameters(), lr=lr)
        nll_none = nn.NLLLoss(reduction="none")
        loss_fn_mean = nn.NLLLoss()
        q = torch.full((G,), 1.0 / G, dtype=torch.float64)
        sqrt_n = np.sqrt(n_g)

        best_worst_recall = -1.0
        best_macro_f1 = -1.0
        epochs_no_improve = 0

        for epoch in range(epochs):
            detector.train()
            total_train_loss, train_correct = 0.0, 0
            optimizer.zero_grad()

            win_losses = []  # per-example NLLs inside the current 16-row window
            win_groups = []  # parallel group ids (-1 = ungrouped)

            for i, (features, label_idx) in enumerate(train_features):
                label = torch.tensor([label_idx], dtype=torch.long)
                probs = detector.classify_features(features)
                if probs.dim() == 1:
                    probs = probs.unsqueeze(0)
                predicted = torch.argmax(probs, dim=-1)
                if predicted.item() == label.item():
                    train_correct += 1
                per_ex = nll_none(torch.log(probs + 1e-8), label).squeeze(0)
                g = int(train_group_full[i])
                if g < 0:
                    # Synthetic rows and dropped small pairs: plain ERM gradient
                    # term (same loss/batch_size scaling as the ERM loop).
                    (per_ex / batch_size).backward()
                win_losses.append(per_ex)
                win_groups.append(g)

                if (i + 1) % batch_size == 0 or (i + 1) == len(train_features):
                    total_train_loss += dro_step(
                        optimizer, q, win_losses, win_groups, eta, c, sqrt_n)
                    win_losses = []
                    win_groups = []

            val_metrics, avg_val_loss, _, _ = evaluate(detector, val_features, loss_fn_mean)
            worst_rec, _ = worst_group_val_recall(detector, val_features, val_group, G)
            print(f"[{vname}/{author}] Epoch {epoch + 1}: "
                  f"Train Acc {100 * train_correct / len(train_features):.2f}% | "
                  f"Val Loss {avg_val_loss:.4f} | Val Acc {val_metrics['accuracy'] * 100:.2f}% | "
                  f"Val Macro-F1 {val_metrics['macro_f1']:.4f} | "
                  f"Worst-group Val Recall {worst_rec * 100:.2f}%")

            improved = (worst_rec > best_worst_recall + 1e-12 or
                        (abs(worst_rec - best_worst_recall) <= 1e-12 and
                         val_metrics["macro_f1"] > best_macro_f1))
            if improved:
                best_worst_recall = worst_rec
                best_macro_f1 = val_metrics["macro_f1"]
                epochs_no_improve = 0
                torch.save(detector.state_dict(), checkpoint_file)
                print(f">>> New best model saved (Worst-group Val Recall: "
                      f"{best_worst_recall:.4f}) -> '{checkpoint_file}'")
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"[{vname}/{author}] Early stopping at epoch {epoch + 1}.")
                    break
        print(f"[{vname}/{author}] Wall time {(time.time() - t0) / 60:.1f} min.")
        detector.load_state_dict(torch.load(checkpoint_file, weights_only=True))

    test_metrics, _, test_true, test_pred = evaluate(detector, test_features)
    worst_rec, group_recalls = worst_group_val_recall(detector, val_features, val_group, G)

    n = len(test_true)
    correct = sum(1 for t, p in zip(test_true, test_pred) if t == p)
    recall = correct / n if n else 0.0
    # Dominant-error concentration: share of errors going to top wrong narrative.
    true_narr = test_true[0] if n else -1
    err_preds = [p for t, p in zip(test_true, test_pred) if p != t]
    if err_preds:
        dom = max(set(err_preds), key=err_preds.count)
        dom_share = err_preds.count(dom) / len(err_preds)
        dom_name = NARRATIVES[dom]
    else:
        dom_name, dom_share = None, 0.0

    cm_path = os.path.join(REPORT_DIR, f"confusion_matrix_{vname}_{author}_test.csv")
    save_confusion_matrix_csv(test_metrics, cm_path)
    group_csv = os.path.join(REPORT_DIR, f"group_recall_{vname}_{author}.csv")
    os.makedirs(REPORT_DIR, exist_ok=True)
    groups = cache["_meta"]["groups"]
    grow = [{"group": (groups[g] if g < G else "RARE_VAL_ONLY"),
             "val_recall": r,
             "n_val": int((val_group == g).sum())}
            for g, r in sorted(group_recalls.items())]
    pd.DataFrame(grow).to_csv(group_csv, index=False, encoding="utf-8-sig")
    print(f"[{vname}/{author}] TEST: recall(true narrative)={recall * 100:.1f}% | "
          f"dominant wrong={dom_name} ({dom_share * 100:.1f}% of errors) | "
          f"macro_f1={test_metrics['macro_f1']:.4f}")
    return {
        "accuracy": test_metrics["accuracy"],
        "macro_precision": test_metrics["macro_precision"],
        "macro_recall": test_metrics["macro_recall"],
        "macro_f1": test_metrics["macro_f1"],
        "recall_true_narrative": recall,
        "n_test": n,
        "true_narrative": NARRATIVES[true_narr] if true_narr >= 0 else None,
        "dominant_wrong_narrative": dom_name,
        "dominant_wrong_narrative_error_share": dom_share,
        "worst_group_val_recall_at_selection": worst_rec,
        "G": G,
        "eta": eta,
        "C": c,
        "confusion_matrix_csv": cm_path,
        "group_recall_csv": group_csv,
    }


def run_grid(authors, etas, cs, seed):
    print(f"Loading SBERT model '{SBERT_MODEL_NAME}' (frozen, encode-only, shared)...")
    sbert_model = SentenceTransformer(SBERT_MODEL_NAME)
    os.makedirs(REPORT_DIR, exist_ok=True)
    all_results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    for author in authors:
        cache = build_or_load_author_cache(author, sbert_model)
        all_results.setdefault(author, {})
        for eta in etas:
            for c in cs:
                vname = variant_name(eta, c)
                if vname in all_results[author] and os.path.exists(
                        os.path.join(CHECKPOINT_DIR, f"{vname}_{author}.pth")):
                    print(f"[{vname}/{author}] Result already recorded, skipping.")
                    continue
                print(f"\n{'=' * 70}\n=== Config '{vname}' (eta={eta}, C={c}) "
                      f"- author '{author}' ===\n{'=' * 70}")
                res = train_variant_dro(author, eta, c, cache, seed=seed)
                all_results[author][vname] = res
                with open(RESULTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
                print(f"Saved results for '{vname}/{author}' to '{RESULTS_FILE}'.")
    return all_results


def select_config():
    """Phase 1: pick (eta, C) by mean recall over exploratory authors only."""
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)
    missing = [a for a in EXPLORATORY_AUTHORS if a not in all_results]
    if missing:
        raise FileNotFoundError(f"results.json missing exploratory authors {missing}")
    configs = set()
    for a in EXPLORATORY_AUTHORS:
        configs.update(all_results[a].keys())
    rows = []
    for vname in sorted(configs):
        try:
            recs = [all_results[a][vname]["recall_true_narrative"] for a in EXPLORATORY_AUTHORS]
        except KeyError:
            print(f"[!] Config '{vname}' incomplete over exploratory authors, skipping.")
            continue
        rows.append({"config": vname, "mean_recall": float(np.mean(recs)),
                     **{f"{a}_recall": r for a, r in zip(EXPLORATORY_AUTHORS, recs)}})
    df = pd.DataFrame(rows).sort_values("mean_recall", ascending=False)
    print("\n" + "=" * 100)
    print("GROUP-DRO SELECTION (exploratory authors only, sorted by mean recall):")
    print("=" * 100)
    print(df.to_string(index=False))
    winner = df.iloc[0]
    # sbert_only ERM baseline deltas (ablation results.json, same splits/authors).
    try:
        abl = json.load(open("artifacts/experiments/narrative_ablation_loao/results.json"))
        base = {a: abl[a]["sbert_only"]["recall_true_narrative"] for a in EXPLORATORY_AUTHORS}
    except Exception as e:
        print(f"[!] Could not load sbert_only baseline: {e}")
        base = {}
    selection = {
        "winner_config": winner["config"],
        "mean_recall": winner["mean_recall"],
        "per_author_recall": {a: winner[f"{a}_recall"] for a in EXPLORATORY_AUTHORS},
        "sbert_only_baseline": base,
        "deltas_vs_sbert_only": ({a: winner[f"{a}_recall"] - base[a]
                                  for a in EXPLORATORY_AUTHORS} if base else {}),
        "full_ranking": df.to_dict(orient="records"),
        "eta_grid": list(ETA_GRID),
        "c_grid": list(C_GRID),
        "frozen_note": "Winner frozen here. Post-hoc tuning on the 14-author set is forbidden.",
    }
    with open(SELECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(selection, f, ensure_ascii=False, indent=2)
    print(f"\nWinner: {winner['config']} (mean recall {winner['mean_recall'] * 100:.2f}%). "
          f"Frozen to '{SELECTION_FILE}'.")
    return selection


def load_frozen_authors():
    with open(FROZEN_SET_FILE, "r", encoding="utf-8") as f:
        frozen = json.load(f)
    return frozen["selected_authors"] if isinstance(frozen, dict) and "selected_authors" in frozen else frozen


def run_frozen(seed):
    sel = json.load(open(SELECTION_FILE))
    vname = sel["winner_config"]
    rec = next(r for r in sel["full_ranking"] if r["config"] == vname)
    # Recover eta/C from the recorded result entry.
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)
    sample = all_results[EXPLORATORY_AUTHORS[0]][vname]
    eta, c = sample["eta"], sample["C"]
    authors_cfg = load_frozen_authors()
    authors = [a["author_source"] if isinstance(a, dict) else a for a in authors_cfg]
    print(f"Confirmatory: frozen config '{vname}' (eta={eta}, C={c}) on {len(authors)} authors.")
    return run_grid(authors, (eta,), (c,), seed)


def aggregate():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)
    sel = json.load(open(SELECTION_FILE))
    vname = sel["winner_config"]
    base_all = json.load(
        open("artifacts/experiments/narrative_fresh_author_confirmatory/results.json"))
    authors_cfg = load_frozen_authors()
    authors = [a["author_source"] if isinstance(a, dict) else a for a in authors_cfg]
    present = [a for a in authors if a in all_results and vname in all_results[a]]
    missing = [a for a in authors if a not in present]
    if missing:
        print(f"[!] WARNING: confirmatory results missing for {missing} - "
              f"aggregation is partial/interim until all 14 authors have been run.")
    rows = []
    for a in present:
        r = all_results[a][vname]
        b = base_all[a]["sbert_original"]
        rows.append({
            "author": a,
            "dro_recall": r["recall_true_narrative"],
            "baseline_recall": b["recall_true_narrative"],
            "delta_pp": (r["recall_true_narrative"] - b["recall_true_narrative"]) * 100,
            "dro_dominant_error_concentration":
                r["dominant_wrong_narrative_error_share"],
            "baseline_dominant_error_concentration":
                b["dominant_wrong_narrative_error_share"],
        })
    df = pd.DataFrame(rows)
    print("\n" + "=" * 100)
    print(f"CONFIRMATORY (frozen {vname} vs sbert_original, n={len(df)}/14):")
    print("=" * 100)
    if len(df):
        print(df.to_string(index=False))
        dro = df["dro_recall"]
        base = df["baseline_recall"]
        mean_ok = dro.mean() >= base.mean() - 0.03
        med_ok = dro.median() >= base.median() - 0.03
        n_severe = int(((base - dro) > 0.10).sum())
        guard_ok = n_severe <= 2
        conc_ok = (df["dro_dominant_error_concentration"].mean()
                   <= df["baseline_dominant_error_concentration"].mean())
        print(f"\n  DRO mean={dro.mean() * 100:.1f}% vs baseline mean={base.mean() * 100:.1f}% "
              f"(need >= {base.mean() * 100 - 3:.1f}%): {mean_ok}")
        print(f"  DRO median={dro.median() * 100:.1f}% vs baseline median={base.median() * 100:.1f}% "
              f"(need >= {base.median() * 100 - 3:.1f}%): {med_ok}")
        print(f"  Authors degrading >10pp: {n_severe}/14 (guardrail <=2): {guard_ok}")
        print(f"  Mean dominant-error concentration DRO={df['dro_dominant_error_concentration'].mean() * 100:.1f}% "
              f"vs baseline={df['baseline_dominant_error_concentration'].mean() * 100:.1f}% "
              f"(must not increase): {conc_ok}")
        verdict = bool(mean_ok and med_ok and guard_ok and conc_ok)
        print(f"\n  => CONFIRMATORY VERDICT (all four must hold): "
              f"{'SUPPORTED' if verdict else 'NOT SUPPORTED'}")
    else:
        verdict = False
    confirmatory = {
        "frozen_config": vname,
        "n_complete": len(df),
        "n_total": len(authors),
        "complete": len(df) == len(authors),
        "per_author": df.to_dict(orient="records") if len(df) else [],
        "verdict": ("SUPPORTED" if (len(df) == len(authors) and verdict)
                    else ("INTERIM_RUNNING" if len(df) < len(authors) else "NOT_SUPPORTED")),
    }
    with open(CONFIRMATORY_FILE, "w", encoding="utf-8") as f:
        json.dump(confirmatory, f, ensure_ascii=False, indent=2)
    print(f"Saved confirmatory status to '{CONFIRMATORY_FILE}'.")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="group-DRO LOAO (debias spec).")
    parser.add_argument("--authors", default=None,
                        help="Comma-separated LOAO authors for the selection grid.")
    parser.add_argument("--author", default=None, help="Single LOAO author grid run.")
    parser.add_argument("--eta-grid", default=",".join(map(str, ETA_GRID)))
    parser.add_argument("--c-grid", default=",".join(map(str, C_GRID)))
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--select-config", action="store_true")
    parser.add_argument("--frozen-authors", action="store_true")
    parser.add_argument("--aggregate", action="store_true")
    args = parser.parse_args()

    if args.select_config:
        select_config()
    elif args.frozen_authors:
        run_frozen(args.seed)
    elif args.aggregate:
        aggregate()
    elif args.author or args.authors:
        authors = ([args.author] if args.author
                   else [a.strip() for a in args.authors.split(",") if a.strip()])
        etas = tuple(float(x) for x in args.eta_grid.split(","))
        cs = tuple(int(x) for x in args.c_grid.split(","))
        run_grid(authors, etas, cs, args.seed)
    else:
        parser.error("Specify --authors/--author, --select-config, --frozen-authors, or --aggregate.")

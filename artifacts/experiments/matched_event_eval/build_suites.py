"""Build frozen event-disjoint evaluation suites (seed 42 everywhere).

Reads: data/raw/twitter_natural_dataset.csv + telegram_natural_dataset.csv,
  artifacts/experiments/narrative_audit/matched_event_candidates_full.csv (+summary),
  data/candidates/v2_pilot/matched_event_pilot.csv,
  artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json
Writes (this dir): suite_<event_id>.csv, pairs_<event_id>.csv,
  spotcheck_sample_blind.csv, spotcheck_key.csv, suite_spec.json
Run: python3 artifacts/experiments/matched_event_eval/build_suites.py  (from repo root)
"""
import hashlib
import itertools
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
MIN_CELL = 30
OUT = Path("artifacts/experiments/matched_event_eval")
CHECKPOINT_DIR = Path("models/experiments/narrative_fresh_author_confirmatory")
VARIANTS = ["sbert_original", "sbert_soft_topic",
            "sbert_person_misc_masked_aug_soft_topic"]

TOPICS = {
    "israel_hezbollah_gaza": r"\b(?:israel|gaza|hezbollah|hamas|lebanon|beirut|idf|palestin|west bank|houthi)\w*\b",
    "russia_ukraine": r"\b(?:russia|ukrain|kyiv|kiev|moscow|kursk|zelensky|putin|donbas|crimea|zaporizh)\w*\b",
    "us_politics_trump": r"\b(?:trump|congress|republican|democrat|election|president|shutdown|impeach|senate|whitehouse|ice\b|dhs\b)\w*\b",
    "iran": r"\b(?:iran|tehran|irgc|khamenei|hormuz|nuclear|pezeshkian)\w*\b",
    "ceasefire_hostage_peace": r"\b(?:ceasefire|hostage|peace talks|negotiation|truce|prisoner exchange|cease-fire)\w*\b",
}

SUITES = [
    ("iran", "2026-03", "March 2026 US/Israel strikes on Iran and Hormuz/nuclear escalation; cross-narrative reaction window."),
    ("israel_hezbollah_gaza", "2026-03", "March 2026 Israel-Hezbollah-Lebanon escalation overlapping the Iran strikes (see pilot event_israel_hezbollah_lebanon_2026_03)."),
    ("russia_ukraine", "2026-03", "March 2026 Russia-Ukraine war coverage after the 4th invasion anniversary."),
    ("us_politics_trump", "2026-03", "March 2026 US politics: Trump Iran strikes plus ICE/DHS policy fight (see pilot event_us_politics_2026_03)."),
    ("russia_ukraine", "2026-02", "February 2026 4th anniversary of the full-scale invasion of Ukraine."),
    ("israel_hezbollah_gaza", "2026-02", "Late-February 2026 US/Israel strikes on Iran spilling into Israel-threat framing."),
    ("us_politics_trump", "2025-01", "January 2025 Trump inauguration and early Gaza-policy reaction (small older-window suite)."),
]

rng = np.random.RandomState(SEED)
OUT.mkdir(parents=True, exist_ok=True)

# ---- load corpus (per-frame date conversion: mixed-format concat coerces one
# ---- frame to NaT under a single pd.to_datetime call, so convert first) ----
frames = []
for fname, source in [("twitter_natural_dataset.csv", "twitter"),
                      ("telegram_natural_dataset.csv", "telegram")]:
    d = pd.read_csv(Path("data/raw") / fname)
    d["source"] = source
    d["date"] = pd.to_datetime(d["date"], errors="coerce", utc=True)
    assert d["date"].isna().sum() == 0, fname
    frames.append(d)
df = pd.concat(frames, ignore_index=True)
df["month"] = df["date"].dt.tz_convert(None).dt.to_period("M").astype(str)
df["uid"] = [hashlib.sha1("|".join(map(str, x)).encode()).hexdigest()[:16]
             for x in zip(df["source"], df["account"], df["date"].astype(str), df["text"].astype(str))]

# ---- inspect the two candidate inputs ----
full = pd.read_csv("artifacts/experiments/narrative_audit/matched_event_candidates_full.csv")
summ = pd.read_csv("artifacts/experiments/narrative_audit/matched_event_candidates_summary.csv")
pilot = pd.read_csv("data/candidates/v2_pilot/matched_event_pilot.csv")
frozen = json.load(open("artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json"))
frozen_names = set()
for n in frozen["selected_authors"]:
    frozen_names.add(n.get("author_source") or n.get("author") if isinstance(n, dict) else n)
print("frozen14:", sorted(frozen_names))

# twitter-only bias check: full.csv cell (iran,2026-03,Resistance) vs recomputed splits
tw_only = df[df["source"] == "twitter"]
pat = TOPICS["iran"]
tw_m = tw_only[tw_only["text"].astype(str).str.contains(pat, na=False, regex=True, case=False)]
tw_cell = len(tw_m[(tw_m["month"] == "2026-03") & (tw_m["narrative_name"] == "Resistance")])
full_cell = int(full[(full["topic"] == "iran") & (full["month"] == "2026-03")
                     & (full["narrative_name"] == "Resistance")]["text_count"].iloc[0])
all_m = df[df["text"].astype(str).str.contains(pat, na=False, regex=True, case=False)]
all_cell = len(all_m[(all_m["month"] == "2026-03") & (all_m["narrative_name"] == "Resistance")])
print(f"bias check (iran,2026-03,Resistance): full.csv={full_cell} twitter-only={tw_cell} twitter+telegram={all_cell}")

pilot_authors = set(pilot["author"].tolist())

# ---- build suites ----
spec_suites = []
suite_frames = {}
for topic, month, desc in SUITES:
    event_id = f"event_{topic}_{month}"
    m = df[(df["month"] == month)
           & df["text"].astype(str).str.contains(TOPICS[topic], na=False, regex=True, case=False)].copy()
    cells = m.groupby(["narrative_name", "account"]).size().reset_index(name="n")
    keep = cells[cells["n"] >= MIN_CELL].sort_values(["narrative_name", "account"])
    narratives = sorted(keep["narrative_name"].unique().tolist())
    assert len(keep) >= 2 and len(narratives) >= 2, (event_id, len(keep), narratives)
    m = m.merge(keep[["narrative_name", "account"]], on=["narrative_name", "account"])
    m["event_id"], m["topic"] = event_id, topic
    out = m[["event_id", "topic", "month", "narrative_name", "account", "source",
             "date", "label", "text", "uid"]].rename(
        columns={"narrative_name": "narrative", "account": "author"})
    out = out.sort_values(["narrative", "author", "date", "uid"]).reset_index(drop=True)
    out.to_csv(OUT / f"suite_{event_id}.csv", index=False)
    suite_frames[event_id] = out

    # directed cross-narrative pairs (both train/test directions, author-disjoint by construction)
    authors = keep.sort_values(["narrative_name", "account"])
    pairs = []
    for a, b in itertools.permutations(authors.itertuples(index=False), 2):
        if a.narrative_name == b.narrative_name:
            continue
        pairs.append({"train_author": a.account, "train_narrative": a.narrative_name,
                      "train_n": int(a.n), "test_author": b.account,
                      "test_narrative": b.narrative_name, "test_n": int(b.n)})
    pairs = pd.DataFrame(pairs).sort_values(["train_author", "test_author"]).reset_index(drop=True)
    pairs.insert(0, "pair_id", [f"{event_id}-P{i + 1:03d}" for i in range(len(pairs))])
    pairs.insert(1, "event_id", event_id)
    pairs.to_csv(OUT / f"pairs_{event_id}.csv", index=False)

    authors_in_frozen = sorted(set(authors["account"]) & frozen_names)
    ckpts = {}
    for a in authors_in_frozen:
        ckpts[a] = {v: str(CHECKPOINT_DIR / f"{v}_{a}.pth")
                    + (" [present]" if (CHECKPOINT_DIR / f"{v}_{a}.pth").exists() else " [MISSING]")
                    for v in VARIANTS}
    spec_suites.append({
        "event_id": event_id, "topic": topic, "month": month, "description": desc,
        "n_narratives": len(narratives), "narratives": narratives,
        "n_authors": len(keep), "n_rows": len(out),
        "cells": [{"author": r.account, "narrative": r.narrative_name, "n": int(r.n),
                   "in_frozen14": bool(r.account in frozen_names),
                   "in_pilot": bool(r.account in pilot_authors)} for r in keep.itertuples()],
        "n_directed_pairs": len(pairs),
        "frozen14_overlap": {"authors": authors_in_frozen, "checkpoints": ckpts,
                             "note": "Checkpoint reuse (zero-shot Mode Z) is possible for test authors listed here; "
                                     "all other test authors require fresh training (Mode T)."},
    })
    print(f"{event_id}: rows={len(out)} authors={len(keep)} narratives={len(narratives)} directed_pairs={len(pairs)}")

# ---- cross-suite row overlap (shared uids) ----
ids = list(suite_frames)
overlap = {}
for a, b in itertools.combinations(ids, 2):
    n = len(set(suite_frames[a]["uid"]) & set(suite_frames[b]["uid"]))
    if n:
        overlap[f"{a} x {b}"] = n
print("cross-suite shared rows:", overlap if overlap else "none")

# ---- blind spot-check: 50 same-suite + 50 cross-suite pairs, seed 42 ----
pool = {e: f.reset_index(drop=True) for e, f in suite_frames.items()}
blind_rows, key_rows = [], []
pid = 0
for _ in range(50):
    e = ids[rng.randint(len(ids))]
    f = pool[e]
    i, j = rng.choice(len(f), 2, replace=False)
    pid += 1
    blind_rows.append({"pair_id": f"SPOT-{pid:03d}", "text_a": f.loc[i, "text"], "text_b": f.loc[j, "text"]})
    key_rows.append({"pair_id": f"SPOT-{pid:03d}", "same_event": 1, "event_a": e, "event_b": e,
                     "author_a": f.loc[i, "author"], "author_b": f.loc[j, "author"]})
guard = 0
made = 0
while made < 50 and guard < 5000:
    guard += 1
    a, b = ids[rng.randint(len(ids))], ids[rng.randint(len(ids))]
    if a == b:
        continue
    fa, fb = pool[a], pool[b]
    i, j = rng.randint(len(fa)), rng.randint(len(fb))
    if fa.loc[i, "uid"] == fb.loc[j, "uid"]:
        continue
    made += 1
    pid += 1
    blind_rows.append({"pair_id": f"SPOT-{pid:03d}", "text_a": fa.loc[i, "text"], "text_b": fb.loc[j, "text"]})
    key_rows.append({"pair_id": f"SPOT-{pid:03d}", "same_event": 0, "event_a": a, "event_b": b,
                     "author_a": fa.loc[i, "author"], "author_b": fb.loc[j, "author"]})
assert made == 50
pd.DataFrame(blind_rows).to_csv(OUT / "spotcheck_sample_blind.csv", index=False)
pd.DataFrame(key_rows).to_csv(OUT / "spotcheck_key.csv", index=False)

total_rows = sum(len(f) for f in suite_frames.values())
total_pairs = sum(s["n_directed_pairs"] for s in spec_suites)

# ---- eval commands for the torch wave ----
ZEROSHOT_PROG = r'''
import json, os, sys
import numpy as np, pandas as pd, torch, torch.nn as nn, torch.optim as optim
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
sys.path.insert(0, "experiments/author_generalization")
from narrative_ablation_loao import AblationDetector, build_hard_soft_dense_vectors
from narrative_lens.config import NARRATIVES, EPOCHS, BATCH_SIZE, LEARNING_RATE
SUITE = "{SUITE}"; SEED = 42
torch.manual_seed(SEED); np.random.seed(SEED)
sbert = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
bt = BERTopic.load("models/experiments/soft_v2_baseline_seeded")
ntop = len([t for t in bt.get_topics().keys() if t != -1])
sdf = pd.read_csv("artifacts/experiments/matched_event_eval/suite_" + SUITE + ".csv")
pairs = pd.read_csv("artifacts/experiments/matched_event_eval/pairs_" + SUITE + ".csv")
lab = {n: i for i, n in enumerate(NARRATIVES)}
def feats(texts):
    se = sbert.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    _, soft = build_hard_soft_dense_vectors(texts, bt, ntop)
    return se.astype(np.float32), np.stack([np.asarray(s, dtype=np.float32) for s in soft])
def arm_vec(arms, se, sd):
    parts = [se] + ([sd] if "soft_topic" in arms else [])
    return np.concatenate(parts, axis=1)
def run_rows(Xtr, ytr, Xte, yte, in_dim, arms):
    Xtr_t = torch.tensor(Xtr); ytr_t = torch.tensor(ytr); Xte_t = torch.tensor(Xte)
    idx = np.arange(len(Xtr)); tr, va = train_test_split(idx, test_size=0.15, random_state=SEED)
    det = AblationDetector(arms=arms, ner_vocab_size=1, srl_vocab_size=1, bertopic_vec_size=Xtr.shape[1] - 384, sbert_dim=384)
    opt = optim.Adam(det.parameters(), lr=LEARNING_RATE); loss = nn.CrossEntropyLoss()
    best, best_state, bad = -1, None, 0
    for ep in range(EPOCHS):
        det.train()
        for s in range(0, len(tr), BATCH_SIZE):
            b = tr[s:s + BATCH_SIZE]
            opt.zero_grad(); loss(det.mlp(Xtr_t[b]), ytr_t[b]).backward(); opt.step()
        det.eval()
        with torch.no_grad():
            p = det.mlp(Xtr_t[va]).argmax(1).numpy()
        f1 = sum((p == c).sum() and ((p == c) & (ytr[va] == c)).sum() / max(1, ((p == c).sum() + (ytr[va] == c).sum()) / 2) for c in set(ytr)) / len(set(ytr))
        if f1 > best: best, best_state, bad = f1, {k: v.cpu() for k, v in det.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= 3: break
    det.load_state_dict(best_state); det.eval()
    with torch.no_grad(): pred = det.mlp(Xte_t).argmax(1).numpy()
    tn = NARRATIVES[yte[0]] if len(set(yte)) == 1 else None
    rec = float((pred == yte).mean()) if tn else None
    return {"n_test": len(yte), "true_narrative": tn, "recall_true_narrative": rec,
            "pred_hist": {NARRATIVES[c]: int((pred == c).sum()) for c in set(pred)}}
out = []
for r in pairs.itertuples():
    tr = sdf[sdf.author == r.train_author]; te = sdf[sdf.author == r.test_author]
    Xtr_se, Xtr_sd = feats(tr.text.astype(str).str.slice(0, 3000).tolist()); ytr = tr.narrative.map(lab).values
    Xte_se, Xte_sd = feats(te.text.astype(str).str.slice(0, 3000).tolist()); yte = te.narrative.map(lab).values
    res = {"pair_id": r.pair_id, "modes": {}}
    res["modes"]["T_sbert_original"] = run_rows(arm_vec(set(), Xtr_se, Xtr_sd), ytr, arm_vec(set(), Xte_se, Xte_sd), yte, 384, set())
    res["modes"]["T_sbert_soft_topic"] = run_rows(arm_vec({"soft_topic"}, Xtr_se, Xtr_sd), ytr, arm_vec({"soft_topic"}, Xte_se, Xte_sd), yte, 384 + ntop + 1, {"soft_topic"})
    for v, arms in [("sbert_original", set()), ("sbert_soft_topic", {"soft_topic"}), ("sbert_person_misc_masked_aug_soft_topic", {"soft_topic"})]:
        ck = f"models/experiments/narrative_fresh_author_confirmatory/{v}_{r.test_author}.pth"
        if os.path.exists(ck):
            in_dim = 384 + (ntop + 1 if arms else 0)
            det = AblationDetector(arms=arms, ner_vocab_size=1, srl_vocab_size=1, bertopic_vec_size=ntop + 1, sbert_dim=384)
            det.load_state_dict(torch.load(ck, map_location="cpu")); det.eval()
            with torch.no_grad(): pred = det.mlp(torch.tensor(arm_vec(arms, Xte_se, Xte_sd))).argmax(1).numpy()
            res["modes"][f"Z_{v}"] = {"n_test": len(yte), "true_narrative": r.test_narrative,
                                      "recall_true_narrative": float((pred == yte).mean()),
                                      "pred_hist": {NARRATIVES[c]: int((pred == c).sum()) for c in set(pred)}}
    out.append(res)
json.dump(out, open("artifacts/experiments/matched_event_eval/results_" + SUITE + ".json", "w"), indent=1)
print(f"[{SUITE}] pairs={len(out)} wrote results_{SUITE}.json")
'''.strip()

commands = []
for s in spec_suites:
    e = s["event_id"]
    covered = sorted({c["author"] for c in s["cells"] if c["in_frozen14"]})
    commands.append({
        "suite": e,
        "zero_shot_and_train_loop": f"python3 - <<'EOF'\n{ZEROSHOT_PROG.replace('{SUITE}', e)}\nEOF",
        "fallback_loao_for_covered_authors": [
            f"python experiments/author_generalization/narrative_fresh_author_confirmatory.py --author {a}"
            for a in covered] or ["(no frozen-14 author in this suite; Mode T only)"],
    })

spec = {
    "seed": SEED,
    "min_texts_per_author_event_cell": MIN_CELL,
    "build_command": "python3 artifacts/experiments/matched_event_eval/build_suites.py",
    "inputs_inspection": {
        "matched_event_candidates_full.csv": {
            "columns": full.columns.tolist(),
            "rows": len(full),
            "note": "Aggregated (topic, month, narrative) cells: text_count + author_count, but NO author identities, "
                    "so author overlap and the 30-text author-event rule cannot be computed from this file alone; "
                    "author-level mining was redone from data/raw (see method).",
            "n_topic_month_cells": len(summ),
            "cells_ge2_narratives": int((summ["narrative_count"] >= 2).sum()),
            "cells_ge3_narratives": int((summ["narrative_count"] >= 3).sum()),
        },
        "matched_event_pilot.csv": {
            "columns": pilot.columns.tolist(), "rows": len(pilot),
            "events": {e: int(n) for e, n in pilot["event_id"].value_counts().items()},
            "authors": sorted(pilot_authors),
            "note": "Text-level pilot (2 events x 2026-03). No author-event cell reaches 30 texts "
                    f"(max cell={int(pilot.groupby(['event_id', 'narrative', 'author']).size().max())}); "
                    "pilot therefore cannot supply frozen eval cells and is used only for event-description grounding "
                    "plus author-overlap reference.",
        },
        "date_bug_found": {
            "finding": "audit_matched_events.py concatenates twitter+telegram BEFORE pd.to_datetime; mixed ISO formats "
                       "coerce one frame to NaT, silently dropping telegram rows.",
            "evidence": {"full.csv (iran,2026-03,Resistance)": full_cell,
                         "recomputed twitter-only": tw_cell, "recomputed twitter+telegram": all_cell},
            "impact": "full.csv/summary.csv are effectively twitter-only; suite mining here converts dates per-frame first.",
        },
    },
    "method": "Per-frame date conversion, keyword topics identical to audit_matched_events.py, month bucketing, "
              "keep author-event cells with >= 30 texts, require >= 2 authors from >= 2 narratives per (topic, month). "
              "Pairs = all cross-narrative directed author pairs (train on all of train-author rows, test on all of "
              "test-author rows, both directions; author-disjoint by construction, event constant). "
              "Spot-check = 50 same-suite + 50 cross-suite blind pairs via numpy RandomState(42).",
    "suites": spec_suites,
    "pairing_instructions": "For each row of pairs_<event>.csv: train ONLY on <train_author> suite rows, test ONLY on "
                            "<test_author> suite rows (never mix authors across the split; never add out-of-event rows "
                            "to test). Metric: true-narrative recall on the test author rows plus predicted-label "
                            "histogram. Both directions are listed as separate pair_ids. Train from seed 42 with "
                            "Section 25 hyperparameters (EPOCHS=20, BATCH_SIZE=16, LR=0.001, patience=3, dropout=0.3, "
                            "hidden=128, all-MiniLM-L6-v2 + soft_v2_baseline_seeded).",
    "torch_wave_eval_commands": commands,
    "spotcheck": {"n_pairs": 100, "positive": 50, "negative": 50,
                   "protocol": "Annotator sees only text_a/text_b in spotcheck_sample_blind.csv and marks same-event (1/0); "
                               "score against spotcheck_key.csv. Report precision on positives and flag pairs where the "
                               "keyword match is topical but not the same real-world event."},
    "cross_suite_shared_rows": overlap,
    "totals": {"n_events": len(spec_suites), "n_directed_pairs": total_pairs, "n_eval_rows": total_rows},
    "frozen14_note": "Seed-42 frozen authors reused where their cells qualify (PressTV, Slavyangrad, Babel, "
                     "United24Media, @MiddleEastEye_TG, ThePostMillennial, AlJazeeraEnglish, BringThemHomeNow, "
                     "abualiexpress as applicable per suite); all remaining suite authors (AIPAC, IDF, StandWithUs, "
                     "FoxNews, mfa_russia, ZelenskyyUa, QudsNen, etc.) are outside the frozen set and noted per cell.",
}
json.dump(spec, open(OUT / "suite_spec.json", "w"), indent=1)
print("TOTALS:", json.dumps(spec["totals"]))

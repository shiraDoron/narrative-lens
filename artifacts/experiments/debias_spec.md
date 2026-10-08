# Debias spec: group-DRO on (narrative, author) groups for unseen-author recall

## 0. Decision

Use group-DRO (Sagawa et al. 2020, "Distributionally Robust Neural Networks for
Group Shifts", ICML 2020, arXiv 1911.08731, ref implementation
https://github.com/kohpangwei/group_DRO) with groups defined as
(narrative, author_source) pairs on the SBERT-only backbone.

One-line edge: group-DRO is the only candidate that directly optimizes
worst-(narrative, author) training recall using the already logged per-row
`author_source` labels, with no representation surgery and no new annotation,
which matches a failure mode that is author-concentrated (20-38pp LOAO recall
gaps, §18) rather than traceable to one removable feature (all of §19-§28
tried removing features and failed).

## 1. Why this method, and why not the other three

Each rejection is one line tied to a specific §18-§28 observation.

- IRM (Arjovsky et al. 2019, arXiv 1907.02893): rejected because §26 showed no
  stable per-example error mechanism under grouped cross-validation (no depth
  beat the 59.9% majority baseline), so there is no evidence for the kind of
  stable cross-environment invariant mechanism IRM needs, and IRMv1 is
  additionally unstable with ~50 author-environments.
- Author-adversarial gradient reversal (Elazar and Goldberg 2018, EMNLP
  D18-1002): rejected because §28 already ran the closest version of this idea
  (strip author-predictive signal, Part A cut author-signature F1 by ~15pp on
  average) and fresh-author recall got worse for 13/14 authors (mean -6.4pp,
  median -10.8pp), plus most authors write in a single narrative so an author
  adversary also erases narrative signal.
- JTT (Liu et al. 2021, ICML PMLR 139): rejected because §26 found LOAO errors
  are not a clean learnable subset (grouped-CV accuracy below baseline at every
  depth), so upweighting the ERM error set on in-distribution train rows has no
  reason to hit unseen-author errors, and JTT costs 2x training for that weak
  rationale.
- Group-DRO fits best because: (a) §18/§25 show the failure is concentrated
  variance across authors (fresh-author recall std 0.236, worst author 3.0%),
  which is exactly the worst-group objective; (b) group labels are free
  (`author_source` already exists in `train.py:load_raw_data`, real vs
  synthetic split already handled by `is_synthetic_author`); (c) it changes
  only the loss weighting, so it stays compatible with the SBERT-only backbone
  that tied or beat every feature-engineered variant on LOAO average recall
  (§20: soft 59.0% vs none 59.2%; §23-§24 augmentation never beat 59.2%
  on average).

## 2. Model and data setup (frozen, not part of the sweep)

- Backbone: `AblationDetector(arms=set())` (SBERT-only, zero engineered arms),
  identical to §20 `none` mode and §25 `sbert_original`. This isolates the
  training-objective effect; prior work confounded features with objectives.
- SBERT: `sentence-transformers/all-MiniLM-L6-v2`, frozen, 384-dim, precomputed
  in the existing per-author caches. No encoder fine-tuning.
- MLP: `Linear(combined_dim,128) -> ReLU -> Dropout(0.3) -> Linear(128,7) ->
  Softmax`. `hidden_size=128`, `dropout=0.3` unchanged.
- Optimizer: `Adam, lr=0.001`. `EPOCHS=20`, `BATCH_SIZE=16`, `patience=3`,
  `seed=42` everywhere (matches `src/narrative_lens/config.py`
  `LEARNING_RATE/BATCH_SIZE/EPOCHS` and §18-§25 convention).
- Splits: `train.split_leave_one_author` unmodified (it calls
  `verify_no_leakage` internally). One held-out author at a time.

## 3. Group definition (exact)

- For the current LOAO run, let `A` be the sorted set of distinct real
  (non-synthetic) `author_source` values in the TRAIN split only, and `Y` the
  set of narrative labels present in train.
- Group key: `(narrative_idx, author_source)`. Keep only pairs with at least
  `MIN_GROUP_SIZE=5` train rows; drop empties. Note: most authors write in one
  narrative, so for them this collapses to one group per author, which is
  intended.
- Map every train row to an integer `group_idx` in `[0, G)` using a dict built
  from train rows only. Attach as a third element of each cached training
  tuple: `(features, label_idx, group_idx)`. Val rows get group ids with the
  same mapping (val-only pairs, if any, map to a single pooled "rare" group
  used only for reporting, never for q-weight updates).
- Synthetic placeholder authors (`*_synthetic`) never form groups and are never
  held out (existing `is_synthetic_author` guard stays in place).

## 4. Loss change (exact recipe)

Replace the plain mean NLL in `train()` with the group-DRO objective:

1. Per optimizer step (one `BATCH_SIZE=16` accumulation window, same windows as
   today), compute per-example `NLLLoss(reduction="none")` on
   `log(probs + 1e-8)`.
2. For each group `g` present in the step, compute the step group loss
   `L_g = mean(example losses in group g)`. Groups absent from the step keep
   their previous loss value (no update to `q` from missing groups).
3. Maintain a simplex vector `q` of length `G`, init uniform `q_g = 1/G`.
   After each optimizer step, exponentiated-gradient update then renormalize:
   `q_g <- q_g * exp(eta * L_g)` for groups present in the step,
   `q <- q / sum(q)`.
4. Step loss for backprop: `loss = sum_g q_g * L_g` (weighted, not plain mean).
   With `GENERALIZATION_ADJUSTMENT C > 0`, use `L_g + C / sqrt(n_g)` where
   `n_g` is the group train count (Sagawa et al. adjustment for small groups).
5. `loss.backward()` / `optimizer.step()` / `optimizer.zero_grad()` cadence is
   otherwise unchanged (same accumulation boundaries as current lines 616-636).

Numerical notes: keep everything else identical (log-probs epsilon `1e-8`,
`NLLLoss`, gradient accumulation divisor). `q` lives on CPU as a plain
float tensor; only the scalar-weighted loss participates in autograd, so there
is no second-order cost.

## 5. Where in the code (files and hook points)

All edits are in the experiment script plus one small helper; `train.py` and
`fusion.py` are NOT modified:

- New script: `experiments/author_generalization/narrative_group_dro_loao.py`
  (clone the structure of
  `experiments/author_generalization/narrative_ablation_loao.py::train_variant`,
  arms fixed to `set()`).
- Build the group map in the new script right after the existing
  `split_leave_one_author` call, from `train_data[["narrative_name",
  "author_source"]]` (train only). Reuse `train.py::evaluate`,
  `train.py::compute_metrics`, `train.py::save_confusion_matrix_csv`
  unmodified.
- Loss hook: replace the inner per-example accumulation block of `train()`
  (`src/narrative_lens/train.py` lines ~616-638: `optimizer.zero_grad()`
  through the `optimizer.step()` accumulation boundary) with the 5-step recipe
  in §4 above. Mirror that block inside the new script's `train_variant_dro`
  rather than editing `train.py`.
- Checkpoint selection: early-stop and save on WORST-GROUP val recall
  (`min_g recall_g` over groups with >=5 val rows), tie-break on val macro-F1.
  Log both every epoch. Rationale in one line: the method optimizes the worst
  group, so model selection must measure the worst group, otherwise selection
  undoes training.
- Checkpoints: `models/experiments/narrative_group_dro/{variant}_{author}.pth`.
  Results: `artifacts/experiments/narrative_group_dro/results.json`,
  per-author confusion-matrix CSVs, per-group recall CSVs.

## 6. Hyperparams (ranges and selection protocol)

- `eta` (group-weight step size): sweep `{0.001, 0.01, 0.05}`, default `0.01`
  (Sagawa et al. default). This is the only sensitive knob.
- `C` (group-size generalization adjustment): sweep `{0, 2}` (Sagawa et al.
  use small integer values; start with `0` and `2`).
- Grid: 3 x 2 = 6 configs. `MIN_GROUP_SIZE=5` fixed. All §2 settings fixed.
- Selection WITHOUT touching the confirmatory set: pick `(eta, C)` by
  worst-group val recall averaged over the 3 exploratory authors only
  (`IDF`, `MariaZakharova`, `BernieSanders`, same caches/splits as §18-§19).
  Freeze the winning config in `results.json` BEFORE any of the 14 frozen
  authors is trained. Tuning `eta`/`C` on the 14 would repeat §24's
  test-informed error (hypothesis chosen on its own eval set), which §25 then
  falsified; this protocol explicitly avoids that.
- No other tuning: no LR schedule, no patience change, no architecture change,
  no second seed. One seed (`42`).

## 7. Extra training cost estimate (CPU)

- Feature extraction cost is ZERO new: reuse existing cached SBERT embeddings
  (`cached_features_ablation_loao_{author}.pt` / train.py caches). No SBERT
  re-encoding, no NER/SRL runs.
- Per optimizer step, DRO adds: one per-group mean over <=16 scalars plus `G`
  multiplies/exponentials for the `q` update (`G` is at most a few hundred,
  typically far fewer after the min-size filter). Expected overhead vs ERM:
  under 5% wall-clock on CPU.
- Calibration procedure (numbers, not guesses): time one ERM `sbert_only` run
  for one author on the target CPU (`time python
  experiments/author_generalization/narrative_group_dro_loao.py --author IDF
  --variant sbert_dro --dry-eta 0.01`), then budget `6 configs x 3 authors`
  for selection plus `1 frozen config x 14 authors` for confirmation, i.e.
  32 single trainings total, each of order minutes on cached 384-dim inputs
  (reference scale: ~11k train rows x 20 epochs of a 2-layer MLP with
  batch 16; early stopping at patience 3 usually halts well before epoch 20).
- Contrast: JTT would cost 2 full trainings per config by construction; DRO
  costs 1x per config plus negligible weighting overhead.

## 8. Eval protocol (exact, reuses the frozen confirmatory set)

- Frozen set (do NOT resample, do NOT swap):
  `artifacts/experiments/narrative_fresh_author_audit/fresh_author_confirmatory_set.json`
  (seed 42, 2 authors per narrative):
  Zionist `BringThemHomeNow`, `abualiexpress`; Resistance `AlJazeeraEnglish`,
  `PressTV`; Western `Bloomberg`, `NATO`; Russian `KremlinRussia_E`,
  `Slavyangrad`; Ukrainian `Babel`, `United24Media`; Right-wing
  `TheEpochTimes`, `ThePostMillennial`; Left-wing `@MiddleEastEye_TG`,
  `ViceNews` (n=200 each except `NATO` n=209, `PressTV` n=400).
- Train the ONE frozen DRO config per author (14 LOAO runs, seed 42, same
  `split_leave_one_author` row membership as §25). Baselines are REUSED as-is,
  never retrained: §25 `sbert_original` (mean recall 39.0%, median 38.8%,
  guardrail 1/14 authors degrade >10pp, mean dominant-error concentration
  44.2%) and optionally `sbert_soft_topic` for context.
- Primary metric: true-narrative recall (= test accuracy, single-narrative
  test sets), paired by held-out author. Report mean, median, std, IQR,
  worst-author recall across the 14.
- Pre-registered non-inferiority rule for `sbert_dro` vs `sbert_original`
  (same 3pp margin as §25): non-inferior only if BOTH mean recall >= baseline
  mean - 3pp AND median recall >= baseline median - 3pp (i.e. vs §25 numbers,
  mean >= 36.0% AND median >= 35.8%). Guardrail: at most 2 of 14 authors may
  degrade >10pp vs `sbert_original`, else fail regardless of mean/median.
- Secondary robustness endpoint (same as §25): per author, dominant
  wrong-narrative and fraction of errors going to it; compare mean
  dominant-error concentration vs baseline 44.2%.
- Interpretation (fixed now): DRO is supported only if ALL hold: (a) the 3pp
  mean+median rule passes; (b) the guardrail passes; (c) mean
  dominant-error concentration does not increase vs baseline. Single-author
  wins do not count (§25 lesson: Bernie-only gains did not replicate).
- Forbidden after unfreezing results: changing `eta`/`C`, swapping authors,
  re-running seeds, adding metrics. Any follow-up variant needs a NEW frozen
  author set, since §25 forbids further tuning against these 14.

## 9. Reproduction commands (exact)

```
# 0. selection grid on exploratory authors only (6 configs x 3 authors)
python experiments/author_generalization/narrative_group_dro_loao.py --authors IDF,MariaZakharova,BernieSanders --eta-grid 0.001,0.01,0.05 --c-grid 0,2 --seed 42
# 1. freeze best (eta, C) by mean worst-group val recall -> recorded in artifacts/experiments/narrative_group_dro/results.json
python experiments/author_generalization/narrative_group_dro_loao.py --select-config
# 2. confirmatory: one frozen config x 14 frozen authors (baselines reused from Section 25, never retrained)
python experiments/author_generalization/narrative_group_dro_loao.py --frozen-authors --seed 42
python experiments/author_generalization/narrative_group_dro_loao.py --aggregate
```

Config log per run (for the paper appendix): branch `thesis-hardening`, seed
42, `(eta, C)`, `G` (kept groups), `MIN_GROUP_SIZE=5`, backbone
`AblationDetector(arms=set())`, `EPOCHS=20, BATCH_SIZE=16, lr=0.001,
patience=3`, SBERT `all-MiniLM-L6-v2` frozen, checkpoint path, and the full
per-author recall table with the §25 baseline columns side by side.

## References

- Sagawa et al. 2020, Distributionally Robust Neural Networks for Group
  Shifts, ICML 2020, arXiv 1911.08731.
- Arjovsky et al. 2019, Invariant Risk Minimization, arXiv 1907.02893.
- Elazar and Goldberg 2018, Adversarial Removal of Demographic Attributes
  from Text Data, EMNLP 2018 (D18-1002).
- Liu et al. 2021, Just Train Twice, ICML 2021, PMLR 139.

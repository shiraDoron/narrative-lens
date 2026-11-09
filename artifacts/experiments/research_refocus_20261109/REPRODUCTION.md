# Reproduction — research refocus and frozen sensitivity, 2026-11-09

Run from repository root with the existing Python 3.11.9 environment. No new installation,
network model download, training or test evaluation is needed. Runtime used torch 2.13.0+cpu,
numpy 2.2.5, sentence-transformers 5.7.0 and the existing pinned local model resources.

```powershell
python artifacts/experiments/research_refocus_20261109/run_pilot.py infer
python artifacts/experiments/research_refocus_20261109/analyze.py
python -m unittest discover -s artifacts/experiments/research_refocus_20261109 -p test_pilot.py -v
```

`prepare` created protocol/input hashes **before successful inference**. Do not run prepare
again in this completed run; a changed protocol belongs in a new directory. `infer` only
reloads frozen weights and recomputes the same 90 predictions. It does not fit, optimize,
call a generator, change labels, or use test/validation texts for inference.

Checkpoint: `verified_human_style_followup_20261026/checkpoints/full_original_baseline_Original_seed42.pt`.
Encoder: exact `base.encoder()` behavior in `experiments/author_generalization/author_style_controlled.py`,
including strict loading of the production MiniLM encoder weights. Every source ID was in
the head's earlier training set. The 105 training and 43 validation counts describe the old
head selection, not new model fits. Class order is checked; seven-way probabilities are retained.

The model cache and checkpoints already exist locally and are intentionally not copied into
this run or Git. If missing, report blocked reproduction rather than train replacements or
substitute a model. All-30 inputs include pre-existing Paraphrases, including rejected ones.

`summary.csv`: paired flip/probability summaries; `predictions.csv`: all probabilities;
`transitions.csv`: every intervention relative to its Original; `per_id_comparison.csv`: all
texts, paired predictions, existing style metrics and guard reasons (no re-screening).
`paired_control_comparison.json`: discordant flips and edit strength. No accuracy/F1 is
reported as quality without human-gold source labels. Bootstrap CIs are descriptive for a
small purposive nine-author sample, not confirmatory inference.

`literature_sources.json` is a registry of primary links checked on 2026-11-09, not copied
paper text or a systematic-review completeness claim. `evidence_source_inventory.json`
records historical raw result sources read for the evidence audit; historical test results
were read, never rerun. `EXPERIMENTS.md` is mutable documentation, so its snapshot hash
is provenance only, not an invariant after adding this experiment.

Scope limitations and future design are in the three root documents. Reviewer claims are
preserved as reported, with disagreements flagged; none are converted to human gold.

CSV files preserve exact source bytes, including embedded line breaks and trailing spaces
inside the old Paraphrase machine preamble. Local Git attributes disable whitespace checks
for these raw CSV files rather than silently cleaning the experimental inputs.

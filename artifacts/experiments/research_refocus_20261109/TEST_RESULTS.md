# Verification — 2026-11-09

Executed:

```text
python -m unittest discover -s artifacts/experiments/research_refocus_20261109 -p test_pilot.py -v
Ran 10 tests — OK
```

Checks: frozen source/checkpoint SHA-256; exact all-30 ID joins and three-arm coverage;
train-only inference and exact label mapping; unchanged text bytes; finite normalized
seven-class probabilities and matching argmax; recomputation of all 60 transitions;
recomputation of summaries; no claimed human-gold accuracy/F1; full per-ID text join;
no training call/gradients or test predictions; 12 literature entries with seven required
fields; all local links in the three main documents resolve.

Two initial test assertions were corrected: CSV serializes Boolean `True` as a string;
float64 recomputation of float32 JS needs an absolute tolerance of 2e-7. These corrections
did not change the inference pipeline, predictions, protocol, thresholds or source texts.

The initial inference attempt failed at saving results because its new directory was
removed during concurrent repository changes. The run was restored with the same seed,
model and arms, then completed. No outcome-based method selection followed that failure.

No fitted model, generator output, human field or external review judgment was modified.

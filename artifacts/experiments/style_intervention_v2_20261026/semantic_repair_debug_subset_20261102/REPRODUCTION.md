# Reproduction

Use the existing Python 3.11 environment, pinned cached model and cached validation models. Run from this directory:

```powershell
python debug.py diagnose
python -m unittest -v test_patch_contract
python debug.py process
python debug.py validate
python report_debug.py
```

`process` makes one verification and, when issues exist, one repair request per selected TRAIN row. It launches the pinned local Qwen2.5-3B model on localhost:18096, hidden, and terminates it afterward. It does not call an external model. Saved request bodies contain Original/Rewrite and findings, never IDs, labels or external-review ratings. JSON-schema enums contain exact local catalogs. Re-running process overwrites only this debug subset's outputs; it never runs all 30. `validate` delegates to the unchanged existing validator and skips an already-present validation CSV; use a separate new debug directory for another run to avoid stale validation. `diagnose` only reads the frozen previous 30-row run.

Requests, raw completions, exact patch events and outputs are versioned; server logs, caches and weights are ignored. The copied analysis cohort contains six existing train rows with unchanged labels. The inherited validator also writes blank review templates in this new directory; those are not filled reviews and existing human-review files are untouched.

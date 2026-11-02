# Existing style-transfer tools — feasibility audit reproduction

2026-11-02. **No inference benchmark was run.** This directory is a research feasibility audit, not an experiment output folder. `planned_train_subset.json` contains nine existing TRAIN pairs and v2 results; every StyleRemix output is null. `baseline_subset_summary.json` explicitly marks all StyleRemix quality metrics null.

The only new Python script reads code/metadata and recomputes existing pure-Python style proxies. It never invokes upstream Python code, loads a model checkpoint, installs packages, creates an inference environment, trains a model, changes guards or generates/repairs text. Importing local torch is only for the CUDA capability probe.

## Exact source versions

- https://github.com/jfisher52/StyleRemix — `c999002c4a5e858ac452794b20b896d06137a13c`.
- https://github.com/laihuiyuan/pre-trained-formality-transfer — `6c6560caaa7828185ae914b207e3070da789a171`.
- Llama-3-8B metadata revision: `8cde5ca8380496c9a6cc7ef3a8b46a0372a1d920` (no weights downloaded).
- Official hosted demo metadata revision: `27cf7bd1271efbef322464252381293884f8998b`; runtime was `RUNTIME_ERROR` (PEFT/transformers import incompatibility), no inference request sent.
- All 16 adapter metadata revisions/configs: `adapter_inventory.json`. Metadata/config requests were anonymous, read-only; no credentials or account data are stored. The configs were fetched from `main` during the same audit; a future actual run must resolve them and weights at the recorded revisions and record file hashes.
- Zhang et al.: official implementation not identified; search details in `official_implementation_search.json`, not an inferred repo version.

## Re-run this audit on Windows

Keep external repositories **outside** the project. These commands retrieve metadata/code, not inference outputs:

```powershell
$taskExternal = Join-Path $env:TEMP 'narrative-lens-tool-feasibility-20261102'
New-Item -ItemType Directory -Force -Path $taskExternal | Out-Null
git clone https://github.com/jfisher52/StyleRemix.git (Join-Path $taskExternal 'StyleRemix')
git -C (Join-Path $taskExternal 'StyleRemix') checkout c999002c4a5e858ac452794b20b896d06137a13c
git clone https://github.com/laihuiyuan/pre-trained-formality-transfer.git (Join-Path $taskExternal 'pre-trained-formality-transfer')
git -C (Join-Path $taskExternal 'pre-trained-formality-transfer') checkout 6c6560caaa7828185ae914b207e3070da789a171
python artifacts/research_existing_style_tools_20261102/inspect_tools.py --external-root $taskExternal
```

Skip cloning an already-present checkout. The original inspection used shallow clones at the same exact commits. The BART upstream repository **contains** approximately 381MB of TextCNN classifier checkpoint blobs, downloaded as part of its clone. These remain outside the project, are never loaded and are not copied into our Git. For a lightweight code-only audit, use a sparse checkout excluding checkpoints, or read pinned raw files and the Git tree via GitHub API; then adapt the script's clean-checkout/tree probe accordingly.

Audit runtime: existing Python 3.11.9, stdlib and existing torch for hardware detection; no new dependencies. Network requests use public Hugging Face model metadata/config endpoints and GitHub repository search. Time-varying search results, disk free and timestamps will naturally differ. Snapshot output is versioned for the observed check.

## Evidence and constraints

- `external_repos.json`: code commits, inspected-file SHA-256, license headers, BART checkpoint tree.
- `hardware_environment.json`: measured CPU/RAM/GPU/CUDA and package versions.
- `base_checkpoint_probe.json`: public metadata, manual gate, anonymous config HTTP 401; does not establish whether the user has separate authorized access.
- `hosted_demo_probe.json`: official Space metadata and runtime failure, checked as an alternative to local GPU; no user texts submitted.
- `adapter_inventory.json`: all 16 metadata/config responses, base model, rank, revisions, model-card license metadata.
- `planned_train_subset.json`: frozen input/old output/old guards and recomputed existing style proxies, with reason for each selected ID.
- `audit_manifest.json`: input hashes and explicit non-execution scope. No test corpus is used; no classification/evaluation model is run.

## If inference is later made feasible

Use a **separate** Linux/CUDA environment for StyleRemix, based on upstream Python 3.10 guidance, with explicitly verified/pinned torch/transformers/PEFT/accelerate/numpy. The upstream requirements file is unpinned and includes heavy dependencies irrelevant to quickstart. Record the tested environment before drawing comparisons; this audit does not supply a falsely “tested” dependency lock.

Require authorized exact Llama-3-8B base + tokenizer and selected official adapters; pin all revisions. A BF16-loading adaptation with batch size one and a GPU around 24GB is a capacity estimate, not a tested setup. Upstream default loading has no explicit dtype, so do not assume it fits in 24GB unchanged. Do not silently substitute Llama-3.1 or an Instruct checkpoint. CPU/GGUF/4-bit conversion would be a separate backend adaptation requiring validation, not this benchmark.

The future wrapper should import/use the quickstart inference path, preserve raw outputs, capture truncation and generation configuration, and take only Original text. Keep labels/old v2 outputs/guard scores outside generator inputs. Fix sliders and seed before generation, start with all nine selected train examples, and run unchanged project guards and style metrics on **every** generated output. No postselection using classifier predictions or test data. Reuse the frozen v2 scores on the same IDs. Do not reuse upstream author classifiers as evidence for unseen Creators authors.

No wrapper or inference environment was created because local feasibility conditions failed. No new experiment folder, fabricated outputs, benchmark success claim or research-quality conclusion was produced.

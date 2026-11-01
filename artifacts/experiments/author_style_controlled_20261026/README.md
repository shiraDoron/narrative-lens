# Reproduce the controlled author-style pilot

From repository root, using the existing project Python and ML dependencies:

```powershell
$py = 'C:/Users/P0039126/.pyenv/pyenv-win/versions/3.11.9/python.exe'
& $py experiments/author_generalization/author_style_controlled.py --stage prepare
& $py experiments/author_generalization/author_style_controlled.py --stage baseline
& $py experiments/author_generalization/author_style_controlled.py --stage generate
& $py experiments/author_generalization/author_style_controlled.py --stage generate
& $py experiments/author_generalization/author_style_controlled.py --stage validate
& $py experiments/author_generalization/author_style_controlled.py --stage evaluate
& $py experiments/author_generalization/author_style_controlled.py --stage report
```

Requires the pinned official Qwen GGUF generator and native llama.cpp CPU runtime (run prepare_llama_runtime.py first), and the project's cached MiniLM, MPNet, BERT-NER and DeBERTa NLI models. Inference is local; the generation server binds only to 127.0.0.1:18091. Posts are not sent to external inference services. Generation resumes from completed JSONL records; stages reuse their completed outputs. Delete only this experiment's relevant completion marker/output when intentionally rerunning a stage. Never overwrite original models/data.

Split, sampling, prompts, training settings and validation thresholds were fixed before intervention evaluation. CPU inference feasibility adjustments are recorded in generation_implementation_note.txt; rejected feasibility outputs are excluded from every analysis. Final configuration is retained. Author aliases are case-folded. Global duplicate-cluster representatives are selected before sampling. Cross-split semantic candidates and generated duplicates are excluded symmetrically. No test predictions select a rewrite. Labels/authors are never included as generation metadata, though named people naturally present in the original text are preserved.

The existing checkpoint supplies the frozen encoder and architecture; narrative heads are initialized anew for disjoint training. Existing deployed head is not used as a disjoint baseline. Adam lr .001, batch 16, 20 fixed epochs, hidden 128/dropout .3; best validation macro-F1 checkpoint. Same accepted source rows, seeds, epoch budget and split across retraining conditions. Each seed's checkpoints and predictions are retained. Seed standard deviations do not replace author-level inference.

Author probes deliberately have the same author identities in their own train/test, with disjoint texts, within each narrative; they are fitted anew per condition. Their split is separate from author-disjoint narrative evaluation. No human validation or independent revised narrative labels were invented. Rejected generations remain available and are reported separately.

Generator preparation when runtime_llama/ is absent (network required):

```powershell
& $py experiments/author_generalization/prepare_llama_runtime.py
```

Run generate twice: the second pass normalizes the four counterfactual styles. The `all` stage performs both passes automatically. Generation feasibility attempts are excluded from analysis; see generation_implementation_note.txt. Analyzed outputs use official GGUF Q8_0 weights with floating point activations and four concurrent local slots; runtime/model revisions and checksums are in llama_runtime_manifest.json. The runtime helper verifies the official archive checksum. Read final_research_report_he.md for the Hebrew report and integrity_audit.json for execution checks.

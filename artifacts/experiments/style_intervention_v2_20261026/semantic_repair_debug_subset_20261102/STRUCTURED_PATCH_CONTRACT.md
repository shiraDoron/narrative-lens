# Structured Patch Contract — technical debug, 2026-11-02

Modify the smallest possible span required to restore semantic equivalence. Do not regenerate the paragraph.

Only `replace_exact`, `insert_after_exact`, `insert_before_exact`, `delete_exact` are supported. Every patch requires string fields `operation`, `target_text`, `evidence_original`, `reason`, `violation_type`. `replacement_text` is required and nonempty for replacement/insertion; deletion accepts it absent or empty. Unknown fields/types and unsupported violations are rejected.

`target_text` must occur exactly once in the **current Rewrite**, including overlapping matches. `evidence_original` must be a nonempty verbatim substring of Original. Evidence is not the edit target. Never reverse a failed patch or apply it to Original. No-op, missing/ambiguous targets and full-paragraph replacement are rejected.

Operational limits (not changes to experimental guards/thresholds): target ≤20 words, replacement ≤24 words, deletion ≤8 words. The model catalogs use only contiguous verbatim spans of 1, 2, 3, 4, 6 or 8 whitespace tokens. These conservative limits may reject a legitimate larger repair; that is recorded, never silently expanded. Several faults require several local patches. Patches run in list order with fresh current-text validation. Invalid patches leave the text unchanged; valid siblings may proceed. Each accepted patch records offsets and exact removed/inserted text. This is per-patch safety, not all-or-nothing transactionality.

Verification returns `issues`, each containing a rewrite-only `target_text`, original-only `evidence_original`, `reason`, `violation_type`. JSON-schema enumerations constrain each side to its own exact catalog. This removes free-form evidence transcription but cannot establish whether a chosen issue is semantically justified. Omission evidence still points to a present nearby rewrite anchor. Empty issue lists are allowed and explicitly counted; validity does not mean detection recall.

`locate()` separately resolves whitespace, case, curly quotes/apostrophes and en/em dashes to a unique **original surface span** with offsets. It never modifies the document. Missing or normalized-ambiguous matches fail. The patch executor never invokes normalization implicitly: a caller must use the resolved exact surface as `target_text`, which is again checked exactly. The model smoke test uses exact catalogs and does not use this optional resolver. NFC is not used for automatic execution; combining-character variations require an exact catalog selection. Punctuation changes other than the documented equivalent quote/dash forms are not fuzzy-matched.

Semantic validity, factual correctness and successful preservation screening are distinct from patch applicability. A technically applied patch can be wrong. No External LLM Review or Human Validation is performed here.

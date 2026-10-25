# Author style / native-language research audit

Analysis date: 2026-10-20. Main Hebrew report: [report](../../docs/author_style_native_language_research_he.md).

Future work and unresolved research questions: [TODO checklist](../../docs/AUTHOR_STYLE_RESEARCH_TODO.md).

## Local measurements

The audit reads the two real-post CSVs without changing them. `row_id=platform:record_number` identifies a one-based CSV record (not physical line); text hashes and source-file hashes are retained. The 83 account identifiers are not 83 verified individual writers. The two synthetic sources are excluded from personal L1 inference.

Language identification uses `langid==1.1.6`, installed under `artifacts/research_dependencies` without changing the project's requirements or global environment. Unrestricted language inventory, `norm_probs=True`; scores are not calibrated probabilities. Fewer than eight words or score below .9 is marked uncertain. High-score outputs can also be wrong. `language_content_checks.csv` is a small explicit content check, not exhaustive relabeling.

Surface feature definitions are in [research_author_style_language.py](../../scripts/research_author_style_language.py). URLs and handles are removed; sentence boundaries use punctuation/newlines, not a parser. English function-word features must not be interpreted as comparable linguistic measurements on non-English rows. MATTR uses 50-word sliding windows; shorter texts have missing values. Account metrics average per-text values, with every text receiving equal weight. No emotion model, sarcasm detector, rhetorical-question detector, or syntactic parser was run.

Prediction loads the local checkpoint's encoder and classifier state strictly, encodes the current real texts afresh, and saves all seven class probabilities. This is descriptive full-corpus inference including potential training exposure, not a held-out evaluation or new accuracy benchmark. No existing result tables are overwritten. The L1-prediction correlation is explicitly not identifiable: only one verified person/L1 group, with unknown post authorship/translation.

Reproduce from repository root using a Python environment with the project's existing ML dependencies:

```powershell
python scripts/research_author_style_language.py --predict
python scripts/finalize_author_language_research.py
```

`langid` must be installed in `artifacts/research_dependencies` or the active environment. The first command requires locally cached MiniLM resources and the existing checkpoint. The finalizer incorporates the hand-reviewed native-language registry, content checks, case registry, and creates the 83-row Markdown table. The finalizer itself contains the recorded content-check decisions so rerunning reproduces them; they are not newly performed human review on each run.

## External cases and metrics

`case_studies.json` retains short excerpts once, source URLs, dates and uncertainty. `case_study_texts.csv` contains metadata/paraphrases, not duplicate excerpts. Stance interpretations are provisional researcher readings, not model predictions or independent human gold labels. The case texts were not merged into training data.

Goldstein: three early candidate publications and three later ones were found. None of the three early candidates establishes an unambiguous left-wing narrative. One early source is only an accessible headline. Do not report the case as a validated 3-left / 3-right controlled corpus or compute stylistic equivalence from it.

Shapiro: three early sources and three later columns were located. BS3 is one 2016 DailyWire essay quoted in abridged form by a next-day report, not two texts. It is excluded from the full-column aggregate. The resulting comparison has two early vs three later full columns. Target-specific stance toward Trump is different from the project's broad Right-wing/Left-wing labels.

`ben_shapiro_source_metrics.json` stores numerical measurements from article bodies read through web tools, not copyrighted complete articles. Source segmentation used:

- BS1: Townhall column from its first substantive paragraph through its final appeal for goodwill. Search-index body used because direct fetch failed. Remove the leading search snippet and all `Advertisement` lines.
- BS2: Townhall body from the Simpsons example through the final appeal to reject the available choices; remove injected recommendations/ads.
- BS3: only the quoted DailyWire essay passage in the Breitbart report, beginning with the refusal to vote for Trump and ending with the final characterization of diluted conservatism. Abridged source; exclude from pooled columns.
- BS4: Townhall `This Is Not Normal`, opening through the final criticism of policy normalcy; exclude author biography and injected recommendation.
- BS5: Townhall Colorado-ballot column, opening through final warning of chaos; exclude biography/ads/recommendations.
- BS6: Townhall conviction column, opening through final warning about the world remaining aflame; exclude ads/recommendations/tags.

Numerical extraction used English alphabetic tokens with internal apostrophes, punctuation/newline sentence boundaries, and raw punctuation/uppercase counts. Averages in the report are unweighted article means. Whole columns include quotations and editor-controlled punctuation. Token diversity depends on length. The external metrics are a saved measurement snapshot: the local scripts do not automatically re-fetch articles, and the report does not claim exact web-content reproducibility if a publisher changes a page. Recheck source-body boundaries before extending this measurement.

No significance or equivalence test was performed on the tiny external sample. Qualitative observations about sarcasm/emotion are contextual, not calibrated scores. Original dataset labels, researcher case interpretations and classifier predictions must remain distinct.

## Researcher-provided L1 update

The registry and author tables now retain researcher-provided languages separately from external evidence. Confidence status: verified (existing explicit source), probable (researcher-requested for Khamenei, Shapiro and Kirk), user_reported_unverified (Sanders, Zakharova, Naftali), unknown (other accounts). Only verified counts as externally documented. Naftali's Hebrew / English remains unresolved and is not encoded as confirmed bilingual L1. Original search outcomes remain in the registry. No new correlation or classifier run was performed for this metadata update.

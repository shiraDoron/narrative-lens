"""
Assembles the FINAL gold-annotation-ready set for the Narrative Fingerprint
Actors->Roles + Relations validation round: 4 long-format CSVs (entities,
relations, values, agendas), one row per item, restricted to the EXACT SAME
small text set already used for manual review (default: the first 5 texts per
narrative of a calibration batch, i.e. the 35 texts already in
<prefix>_review_sample.csv) - NOT the full corpus, per the standing rule that
narrative_profiler.py and full-corpus runs stay deferred until this validation
round is done.

Does NOT run any model and does NOT change any extraction rule/threshold -
it only reads the ALREADY-PRODUCED data/profiles/text_profiles_<prefix>.json
(from build_profile_prototype.py) and re-uses the existing writer functions:
  - write_entity_review / write_relation_review / write_values_review
    (from build_profile_prototype.py)
  - write_agenda_review (from build_review_sample.py - agendas are a cheap
    on-the-fly lexicon regex, not part of the model pipeline, so no re-run
    needed there either)
restricted via build_review_sample.filter_first_n_per_narrative() to guarantee
these rows are IDENTICAL (same confidence/evidence values) to what's already
in <prefix>_review_sample.csv - no re-computation, just re-formatting.

Outputs (artifacts/experiments/profiler_prototype/):
  <prefix>_gold_entities.csv   - one row per actor mention
  <prefix>_gold_relations.csv  - one row per extracted relation
  <prefix>_gold_values.csv     - one row per values-lexicon hit
  <prefix>_gold_agendas.csv    - one row per agenda-lexicon hit

Each file has the SAME text_id/narrative_name/text columns (so no need to have
a separate file open just for context), the full predicted_*/confidence/
evidence columns, and blank gold_* + correct_incorrect_missing_uncertain +
annotator_notes columns (entities/relations additionally have a blank
error_stage column). See ANNOTATION GUIDE below for the exact conventions.

ANNOTATION GUIDE
----------------
1. correct_incorrect_missing_uncertain (all 4 files): fill in one of
   - "correct"   - the predicted_* fields are right.
   - "incorrect" - the system detected SOMETHING here but got it wrong
                   (wrong role/relation type/direction/value category etc).
   - "missing"   - see convention below: a real actor/relation/value/agenda
                   the system failed to detect AT ALL.
   - "uncertain" - you yourself aren't sure / it's genuinely ambiguous.

2. "missing" row convention: if you notice the system missed a real actor/
   relation/value/agenda in a text, ADD A NEW ROW for it (copy that text's
   text_id/narrative_name/text into the new row), set the predicted_* column
   to the literal string "(missing)" (NOT "(none detected)" - that literal is
   reserved for "the system found zero items in this whole text" and is
   auto-generated, don't repurpose it), leave the other predicted_*/confidence/
   evidence columns blank, fill in the gold_* column(s), and set
   correct_incorrect_missing_uncertain = "missing". This keeps "(missing)"
   universally meaning "not predicted by the system" for scoring purposes
   (evaluate_profile_extraction.py treats it as a straightforward miss/false
   negative - it never accidentally matches a real predicted label).

3. error_stage (entities/relations only, fill in ONLY when judgment is
   "incorrect" - helps separate WHERE in the pipeline the mistake happened):
   - entities.csv: "entity_extraction" (wrong/garbage span - shouldn't have
     been extracted as an entity at all, or is badly truncated/merged),
     "normalization" (right span, wrong canonical form - e.g. wrong alias
     mapping), "role_assignment" (right actor, wrong role).
   - relations.csv: "entity_extraction" (source/target isn't a real, correctly
     extracted entity), "relation_extraction" (entities are fine, but the
     relation type or direction is wrong).

4. Do NOT change any code, threshold, or heuristic while annotating - this
   round is purely about MEASURING current performance first (per explicit
   instruction). Tuning decisions come after evaluate_profile_extraction.py's
   metrics are reviewed.

Run (from repo root, AFTER build_profile_prototype.py has produced
text_profiles_<prefix>.json - no need to re-run it):
    python -m narrative_lens.evaluation.build_gold_annotation_set --prefix calibration --n-per-narrative 5
"""

import argparse
import json
import os

from narrative_lens.evaluation.build_profile_prototype import write_entity_review, write_relation_review, write_values_review
from narrative_lens.evaluation.build_review_sample import write_agenda_review, filter_first_n_per_narrative

PROFILES_DIR = "data/profiles"
REPORT_DIR = "artifacts/experiments/profiler_prototype"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prefix", type=str, default="calibration",
                         help="Prefix of the already-run build_profile_prototype.py batch to read from.")
    parser.add_argument("--n-per-narrative", type=int, default=5,
                         help="Must match the n_per_narrative already used for <prefix>_review_sample.csv "
                              "(default 5) so the gold set covers the exact same texts.")
    args = parser.parse_args()

    text_profiles_path = os.path.join(PROFILES_DIR, f"text_profiles_{args.prefix}.json")
    if not os.path.exists(text_profiles_path):
        raise FileNotFoundError(
            f"{text_profiles_path} not found - run build_profile_prototype.py --prefix {args.prefix} first."
        )

    with open(text_profiles_path, "r", encoding="utf-8") as f:
        text_profiles = json.load(f)

    gold_set = filter_first_n_per_narrative(text_profiles, args.n_per_narrative)

    os.makedirs(REPORT_DIR, exist_ok=True)
    entities_path = os.path.join(REPORT_DIR, f"{args.prefix}_gold_entities.csv")
    relations_path = os.path.join(REPORT_DIR, f"{args.prefix}_gold_relations.csv")
    values_path = os.path.join(REPORT_DIR, f"{args.prefix}_gold_values.csv")
    agendas_path = os.path.join(REPORT_DIR, f"{args.prefix}_gold_agendas.csv")

    write_entity_review(gold_set, entities_path)
    write_relation_review(gold_set, relations_path)
    write_values_review(gold_set, values_path)
    write_agenda_review(gold_set, agendas_path)

    n_narratives = len({tp["narrative_name"] for tp in gold_set})
    print(f"Gold annotation set: {len(gold_set)} texts across {n_narratives} narratives.")
    print(f"- {entities_path}")
    print(f"- {relations_path}")
    print(f"- {values_path}")
    print(f"- {agendas_path}")
    print("\nFill in the gold_*/error_stage/correct_incorrect_missing_uncertain/annotator_notes "
          "columns (see this script's module docstring for the annotation conventions), then run:")
    print(f"    python -m narrative_lens.evaluation.evaluate_profile_extraction --entities-csv {entities_path} "
          f"--relations-csv {relations_path} --values-csv {values_path} --agendas-csv {agendas_path}")


if __name__ == "__main__":
    main()

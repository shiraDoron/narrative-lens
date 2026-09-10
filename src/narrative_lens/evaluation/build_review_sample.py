"""
Builds a small, human-friendly REVIEW SAMPLE (5 texts per narrative) from an
ALREADY-RUN build_profile_prototype.py output (e.g. the "calibration" batch),
for a first manual look BEFORE any extraction-rule tuning or building the full
narrative_profiler.py.

Deliberately does NOT run any model (no NER/spaCy/etc. re-run) - it only reads
the existing data/profiles/text_profiles_<prefix>.json and formats it. The one
exception is "agendas": that facet was not part of build_profile_prototype.py's
output, so this script adds it here via the EXISTING, already-built lexicon-
regex AGENDA_PATTERNS (from analyze_agendas.py, same approach as values_hits) -
this is a plain regex lookup, not a new model, and is computed directly on the
text already stored in the JSON.

Output: ONE ROW PER TEXT (wide, easy-to-read-in-Excel format), with each
predicted facet (actors/roles, relations, values, agendas) rendered as a
multi-line human-readable cell (now including role/relation evidence text, not
just the label+confidence), and a blank free-text column per facet for a quick
qualitative note, per the "quick look before tuning" workflow. The RIGOROUS,
machine-scorable gold annotation (one row per item, structured gold_* columns)
happens in the separate long-format CSVs instead - see build_gold_annotation_set.py,
which uses this module's `write_agenda_review()` (+ build_profile_prototype.py's
entity/relation/values writers) to produce all 4 long-format reviews
(entities/relations/values/agendas) restricted to this exact same small text set.

Run (from repo root):
    python -m narrative_lens.evaluation.build_review_sample --prefix calibration --n-per-narrative 5
"""

import argparse
import json
import os

import pandas as pd

from narrative_lens.features.analyze_agendas import AGENDA_PATTERNS, clean_text as clean_lexicon_text, MENTION_RE, HASHTAG_RE

PROFILES_DIR = "data/profiles"
REPORT_DIR = "reports/results/profiler_prototype"


def _extract_agenda_hits(text):
    """Same evidence-bearing pattern as build_profile_prototype.py's
    _extract_values_hits, applied to AGENDA_PATTERNS instead of VALUES_PATTERNS.
    Also strips @mentions/#hashtags (not stripped by the shared
    analyze_agendas.clean_text) before matching - a word embedded in a handle
    or hashtag (e.g. "@media.somehandle", "#VoicesFromCentralAsia") can
    otherwise spuriously match a lexicon category term."""
    cleaned = clean_lexicon_text(text)
    cleaned = MENTION_RE.sub(" ", cleaned)
    cleaned = HASHTAG_RE.sub(" ", cleaned)
    hits = []
    for category, pattern in AGENDA_PATTERNS.items():
        match = pattern.search(cleaned)
        if match is None:
            continue
        start = max(0, match.start() - 30)
        end = min(len(cleaned), match.end() + 30)
        hits.append({
            "category": category,
            "matched_text": match.group(0),
            "evidence": cleaned[start:end].strip(),
        })
    return hits


def _format_actors_roles(entities):
    if not entities:
        return "(none detected)"
    lines = []
    for e in entities:
        role = e["predicted_role"]
        extra = f" [candidate: {e['candidate_role']}]" if role in ("unknown", "uncertain") else ""
        frag = " (reconstructed)" if e.get("was_reconstructed") else ""
        evidence = f" | evidence: {e['role_evidence']!r}" if e.get("role_evidence") else ""
        lines.append(
            f"{e['canonical']}{frag} = {role} (conf {e['role_confidence']}, agency {e['predicted_agency']}){extra}{evidence}"
        )
    return "\n".join(lines)


def _format_relations(relations):
    if not relations:
        return "(none detected)"
    lines = []
    for r in relations:
        rel = r["relation"]
        extra = f" [candidate: {r['candidate_relation']}]" if rel == "uncertain" else ""
        evidence = f" | evidence: {r['evidence']!r}" if r.get("evidence") else ""
        lines.append(f"{r['source']} --{rel}--> {r['target']} (conf {r['confidence']}){extra}{evidence}")
    return "\n".join(lines)


def _format_hits(hits):
    if not hits:
        return "(none detected)"
    return "\n".join(f"{h['category']}: {h['matched_text']!r}" for h in hits)


def filter_first_n_per_narrative(text_profiles, n_per_narrative):
    """Returns the same first-N-per-narrative subset of text_profiles (in
    existing JSON order) used by build_review_sample() - factored out so other
    scripts (build_gold_annotation_set.py) can restrict their own long-format
    reviews to the EXACT SAME small text set already used for manual review,
    without re-deriving the sampling logic."""
    filtered = []
    seen_per_narrative = {}
    for tp in text_profiles:
        nar = tp["narrative_name"]
        count = seen_per_narrative.get(nar, 0)
        if count >= n_per_narrative:
            continue
        seen_per_narrative[nar] = count + 1
        filtered.append(tp)
    return filtered


AGENDA_REVIEW_COLUMNS = [
    "text_id", "narrative_name", "text",
    "predicted_category", "matched_text", "agenda_evidence",
    "gold_agendas", "correct_incorrect_missing_uncertain", "annotator_notes",
]


def write_agenda_review(text_profiles, path):
    """Long-format review CSV for the agendas facet (one row per lexicon hit),
    matching the same predicted_*/gold_*/correct_incorrect_missing_uncertain/
    annotator_notes convention as build_profile_prototype.py's write_*_review
    functions - computed here (not there) since agendas are a cheap on-the-fly
    lexicon regex, not part of the model pipeline (see module docstring)."""
    rows = []
    for tp in text_profiles:
        hits = _extract_agenda_hits(tp["text"])
        if not hits:
            rows.append({
                "text_id": tp["text_id"], "narrative_name": tp["narrative_name"], "text": tp["text"],
                "predicted_category": "(none detected)", "matched_text": "", "agenda_evidence": "",
                "gold_agendas": "", "correct_incorrect_missing_uncertain": "", "annotator_notes": "",
            })
            continue
        for hit in hits:
            rows.append({
                "text_id": tp["text_id"], "narrative_name": tp["narrative_name"], "text": tp["text"],
                "predicted_category": hit["category"], "matched_text": hit["matched_text"],
                "agenda_evidence": hit["evidence"],
                "gold_agendas": "", "correct_incorrect_missing_uncertain": "", "annotator_notes": "",
            })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pd.DataFrame(rows, columns=AGENDA_REVIEW_COLUMNS).to_csv(path, index=False, encoding="utf-8-sig")


def build_review_sample(text_profiles, n_per_narrative=5):
    rows = []
    for tp in filter_first_n_per_narrative(text_profiles, n_per_narrative):
        nar = tp["narrative_name"]
        agenda_hits = _extract_agenda_hits(tp["text"])

        rows.append({
            "text_id": tp["text_id"],
            "narrative_name": nar,
            "text": tp["text"],
            "system_actors_roles": _format_actors_roles(tp["entities"]),
            "system_relations": _format_relations(tp["relations"]),
            "system_values": _format_hits(tp["values_hits"]),
            "system_agendas": _format_hits(agenda_hits),
            "manual_actors_roles_feedback": "",
            "manual_relations_feedback": "",
            "manual_values_feedback": "",
            "manual_agendas_feedback": "",
            "annotator_notes": "",
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prefix", type=str, default="calibration",
                         help="Prefix of the already-run build_profile_prototype.py batch to read from.")
    parser.add_argument("--n-per-narrative", type=int, default=5)
    parser.add_argument("--out", type=str, default=None,
                         help="Output CSV path (default: reports/results/profiler_prototype/<prefix>_review_sample.csv)")
    args = parser.parse_args()

    text_profiles_path = os.path.join(PROFILES_DIR, f"text_profiles_{args.prefix}.json")
    if not os.path.exists(text_profiles_path):
        raise FileNotFoundError(
            f"{text_profiles_path} not found - run build_profile_prototype.py --prefix {args.prefix} first."
        )

    with open(text_profiles_path, "r", encoding="utf-8") as f:
        text_profiles = json.load(f)

    rows = build_review_sample(text_profiles, args.n_per_narrative)

    out_path = args.out or os.path.join(REPORT_DIR, f"{args.prefix}_review_sample.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8-sig")

    n_narratives = len({r["narrative_name"] for r in rows})
    print(f"Wrote {len(rows)} texts across {n_narratives} narratives -> {out_path}")


if __name__ == "__main__":
    main()

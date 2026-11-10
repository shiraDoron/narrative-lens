"""Archive supplied diagnostics separately; compare records without admitting data.

No inference, label edits, human intake, or training entry point exists here.
Raw bytes are retained; blank human fields are never converted into judgments.
"""
from collections import Counter
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'artifacts/experiments/research_completion_20261110'))
from common import FOLLOW, RUN, read, save, sha, style_checks, style_scores, text_sha, verify

HANDOFF = ROOT / 'artifacts/experiments/human_validation_handoff_20261110'
RESEARCH = ROOT / 'artifacts/experiments/research_completion_20261110'
INPUTS = ('PAIRS_210_AI_DIAGNOSTIC.csv', 'LABELS_148_AI_PRELIMINARY.csv')


def binding_issues(actual, expected, keys, fields):
    expected = {tuple(r[k] for k in keys): r for r in expected}
    seen, issues = set(), []
    for row in actual:
        key = tuple(row.get(k, '') for k in keys)
        if key in seen:
            issues.append(dict(key=str(key), field='', problem='duplicate'))
        seen.add(key)
        if key not in expected:
            issues.append(dict(key=str(key), field='', problem='unexpected_key'))
            continue
        for field in fields:
            if row.get(field) != expected[key][field]:
                issues.append(dict(key=str(key), field=field, problem='binding_mismatch'))
        for field, textfield in [('source_sha256', 'Original'), ('rewrite_sha256', 'Rewrite')]:
            if textfield in row and row.get(field) != text_sha(row[textfield]):
                issues.append(dict(key=str(key), field=field, problem='content_hash_mismatch'))
    for key in expected.keys() - seen:
        issues.append(dict(key=str(key), field='', problem='missing_key'))
    return issues


def main():
    verify()
    raw = HERE / 'raw'
    raw.mkdir(exist_ok=True)
    source_hashes = {}
    for name in INPUTS:
        source = Path('C:/Users/P0039126/Downloads') / name
        target = raw / name
        if target.exists() and source.exists() and sha(target) != sha(source):
            raise ValueError('Never overwrite an archived review: ' + name)
        if not target.exists():
            shutil.copyfile(source, target)
        source_hashes[name] = sha(target)
    pairs, labels = [read(raw / name) for name in INPUTS]
    forms_pairs, forms_labels = [read(HANDOFF / 'forms' / name) for name in ('PAIRS_210.csv', 'LABELS_148.csv')]
    pair_issues = binding_issues(pairs, forms_pairs, ('ID', 'variant'),
                            ('Original', 'Rewrite', 'source_sha256', 'rewrite_sha256'))
    label_issues = binding_issues(labels, forms_labels, ('ID',),
                             ('Original', 'source_sha256', 'split', 'proposed_label'))
    issues = pair_issues + label_issues
    invalid_pair_keys = {i['key'] for i in pair_issues}
    human_pair = ('meaning', 'stance', 'style_change', 'semantic_drift', 'notes', 'reviewer_type', 'reviewer_id', 'review_date')
    human_label = ('human_label', 'proposed_label_correct', 'evidence_span', 'human_notes', 'reviewer_type', 'reviewer_id', 'review_date')
    nonblank = sum(bool(r.get(k)) for rows, fields in [(pairs, human_pair), (labels, human_label)] for r in rows for k in fields)
    required_pair = ('ai_meaning_assessment', 'ai_stance_assessment', 'ai_style_observation', 'ai_semantic_risk', 'ai_review_status')
    required_label = ('ai_candidate_label', 'ai_confidence', 'ai_evidence_excerpt', 'ai_review_status')
    for rows, fields in [(pairs, required_pair), (labels, required_label)]:
        for row in rows:
            for field in fields:
                if not row.get(field):
                    issues.append(dict(key=str((row['ID'], row.get('variant', ''))), field=field, problem='missing_ai_assessment'))
    checks = {(rid, 'Style'): row for rid, row in style_checks().items()}
    p75 = RUN / 'paraphrase_qc/rewrite_validation.csv'
    for row in read(p75):
        checks[row['row_id'], 'Paraphrase'] = row
    pold = FOLLOW / 'rewrite_validation.csv'
    oldids = {r['ID'] for r in forms_pairs} - {r['row_id'] for r in read(p75)}
    for row in read(pold):
        if row['condition'] == 'Paraphrase' and row['row_id'] in oldids:
            checks[row['row_id'], 'Paraphrase'] = row
    # Stored old Paraphrase checks must be bound to the exact canonical outputs.
    generation = [json.loads(line) for line in (FOLLOW / 'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
    matched = {(r['row_id'], r['condition']): r for r in generation}
    for row in forms_pairs:
        if row['variant'] == 'Paraphrase' and row['ID'] in oldids:
            gen = matched[row['ID'], 'Paraphrase']
            if gen['rewrite'] != row['Rewrite']:
                raise ValueError('Stored Paraphrase QC is for a different text')
    prior_path = RESEARCH / 'ai_review_audit_105_20261110/AI_REVIEW_ALL_105.csv'
    focus_path = RESEARCH / 'focused_quality_64_20261110/FOCUSED_QUALITY_REVIEW_64.csv'
    prior = {r['ID']: r for r in read(prior_path)}
    focus = {r['ID']: r for r in read(focus_path)}
    metrics = style_scores()
    comparison = []
    for row in pairs:
        key = row['ID'], row['variant']
        bound = str(key) not in invalid_pair_keys
        qc = checks.get(key, {}) if bound else {}
        old = prior.get(row['ID'], {}) if row['variant'] == 'Style' else {}
        focused = focus.get(row['ID'], {}) if row['variant'] == 'Style' else {}
        attention = [] if bound else ['exact_text_binding_failed_do_not_compare_scores_as_same_text']
        if row['ai_semantic_risk'].startswith('Low') and old.get('ai_meaning_preserved') in ('No', 'Borderline'):
            attention.append('low_surface_flags_but_prior_semantic_reservation')
        if row['ai_semantic_risk'].startswith('Low') and focused.get('disposition') in ('ai_identified_difference', 'unresolved_semantic_risk'):
            attention.append('low_surface_flags_but_focused_semantic_reservation')
        if qc.get('passed') == 'True' and not row['ai_semantic_risk'].startswith('Low'):
            attention.append('auto_pass_but_new_review_priority')
        if qc.get('passed') == 'False' and row['ai_semantic_risk'].startswith('Low'):
            attention.append('auto_reject_but_low_new_surface_flags')
        for ai_field, qc_field in [('ai_number_change', 'guard_numbers'), ('ai_quoted_span_change', 'guard_quotations')]:
            if qc and (row[ai_field] == 'True') != (qc[qc_field] == 'False'):
                attention.append(ai_field + '_definition_disagreement')
        comparison.append(dict(ID=row['ID'], variant=row['variant'],
                               **{k: v for k, v in row.items() if k.startswith('ai_')},
                               exact_binding_valid=bound,
                               old_qc_pass=qc.get('passed', 'N/A'), old_failed_guards=qc.get('rejection_reasons', 'N/A'),
                               old_nli_forward=qc.get('entailment_forward', 'N/A'), old_nli_reverse=qc.get('entailment_reverse', 'N/A'),
                               old_semantic_similarity=qc.get('semantic_similarity', 'N/A'),
                               old_style_proxy=metrics[row['ID']].get('substantial_style_change', 'N/A') if row['variant'] == 'Style' else 'N/A',
                               prior_ai_meaning=old.get('ai_meaning_preserved', 'N/A'),
                               prior_ai_stance=old.get('ai_narrative_preserved', 'N/A'),
                               prior_ai_style=old.get('ai_style_change_valid', 'N/A'),
                               prior_ai_notes=old.get('ai_notes', 'N/A'),
                               focused_disposition=focused.get('disposition', 'N/A'),
                               focused_finding=focused.get('finding', 'N/A'),
                               comparison_flags=';'.join(attention), is_human_review=False, eligible_for_training=False))
    save(HERE / 'PAIR_COMPARISON_210.csv', comparison)
    label_comparison = []
    for row in labels:
        relation = ('same_as_proposal' if row['ai_candidate_label'] == row['proposed_label'] else
                    'unclear_not_opposite' if row['ai_candidate_label'] == 'Unclear' else 'opposite_binary_label')
        label_comparison.append(dict(**row, comparison_to_proposal=relation,
                                     evidence_exact_substring=row['ai_evidence_excerpt'] in row['Original'],
                                     is_human_review=False, eligible_as_gold=False))
    save(HERE / 'LABEL_COMPARISON_148.csv', label_comparison)
    annotations = {r['row_id']: r for r in read(FOLLOW / 'text_annotations.csv')}
    lineage = []
    for row in labels:
        origin = annotations[row['ID']]
        if text_sha(origin['text']) != row['source_sha256']:
            raise ValueError('Label lineage does not bind to the same Original')
        lineage.append(dict(ID=row['ID'], split=row['split'], current_proposed_label=row['proposed_label'],
                            original_proposal_a=origin['label_a'], original_proposal_b=origin['label_b'],
                            original_agreement=origin['agreement'], original_gold_status=origin['gold_status'],
                            original_eligible_provisional_label=origin['eligible_provisional_label'],
                            new_ai_candidate_label=row['ai_candidate_label'],
                            source_sha256=row['source_sha256'], is_human_gold=False))
    save(HERE / 'LABEL_LINEAGE_148.csv', lineage)
    flagcounts = Counter(flag for r in comparison for flag in r['comparison_flags'].split(';') if flag)
    summary = dict(pair_rows=len(pairs), label_rows=len(labels), binding_issues=len(issues),
                   exact_bound_pair_rows=len(pairs) - len(invalid_pair_keys),
                   exact_bound_label_rows=len(labels) - len({i['key'] for i in label_issues}),
                   populated_human_fields_in_supplied_files=nonblank,
                   supplied_reviewer_model='unknown; not established by file metadata', supplied_review_date='unknown',
                   import_date='2026-11-10', original_file_sha256=source_hashes,
                   pair_counts_by_variant={v: {f: dict(Counter(r[f] for r in pairs if r['variant'] == v)) for f in required_pair}
                                           for v in ('Style', 'Paraphrase')},
                   label_counts_by_split={s: {f: dict(Counter(r[f] for r in labels if r['split'] == s))
                                             for f in ('ai_candidate_label', 'ai_confidence')} for s in ('train', 'validation')},
                   label_proposal_comparison=dict(Counter(r['comparison_to_proposal'] for r in label_comparison)),
                   nonexact_label_evidence=sum(not r['evidence_exact_substring'] for r in label_comparison),
                   pair_comparison_flag_counts=dict(flagcounts), qc_available=sum(r['old_qc_pass'] != 'N/A' for r in comparison),
                   source_sha256={str(p.relative_to(ROOT)): sha(p) for p in
                                  [prior_path, focus_path, p75, pold, HANDOFF / 'forms/PAIRS_210.csv', HANDOFF / 'forms/LABELS_148.csv']},
                   semantic_gold_created=False, human_validation_completed=False, scientific_training_ready=False,
                   main_training_executed=False, test_evaluated=False)
    (HERE / 'IMPORT_AUDIT.json').write_text(json.dumps(dict(summary=summary, issues=issues), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()

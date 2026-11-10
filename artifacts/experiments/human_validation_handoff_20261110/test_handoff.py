"""Synthetic metadata in memory only; never writes fake human judgments."""
import copy
import json
import unittest

from handoff import HERE, RUNTIME, inspect, templates, text_sha, sha, read


def fixtures():
    labels, pairs, _ = templates()
    for row in labels:
        row.update(human_label=row['proposed_label'], proposed_label_correct='Yes',
                   evidence_span=row['Original'][:30], reviewer_type='human',
                   reviewer_id='SYNTHETIC_UNIT_TEST_NOT_REAL_REVIEW', review_date='2026-11-10')
    for row in pairs:
        row.update(meaning='Yes', stance='Yes', semantic_drift='No', style_change='Yes',
                   reviewer_type='human', reviewer_id='SYNTHETIC_UNIT_TEST_NOT_REAL_REVIEW', review_date='2026-11-10')
    return labels, pairs


class HandoffTests(unittest.TestCase):
    def test_csv_preserves_all_text_including_embedded_whitespace(self):
        labels, pairs, _ = templates()
        self.assertEqual(read(HERE / 'forms/LABELS_148.csv'), labels)
        self.assertEqual(read(HERE / 'forms/PAIRS_210.csv'), pairs)

    def test_generated_forms_manifest(self):
        manifest = json.loads((HERE / 'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        for name, digest in manifest['forms_sha256'].items():
            self.assertEqual(sha(HERE / 'forms' / name), digest)

    def test_coverage_priority_blank_and_text_binding(self):
        labels, pairs, priority = templates()
        self.assertEqual(len(labels), 148)
        self.assertEqual(sum(r['split'] == 'train' for r in labels), 105)
        self.assertEqual(len(pairs), 210)
        self.assertEqual({r['ID'] for r in pairs[:30]}, priority)
        self.assertTrue(all(r['variant'] == 'Style' for r in pairs[:30]))
        self.assertEqual(len({(r['ID'], r['variant']) for r in pairs}), 210)
        for r in labels:
            self.assertEqual(r['source_sha256'], text_sha(r['Original']))
            self.assertEqual(r['human_label'], '')
        for r in pairs:
            self.assertEqual(r['rewrite_sha256'], text_sha(r['Rewrite']))
            self.assertEqual(r['meaning'], '')
            self.assertEqual(r['reviewer_id'], '')

    def test_blank_forms_block(self):
        labels, pairs, _ = templates()
        report = inspect(labels, pairs)
        self.assertFalse(report['human_intake_complete'])
        self.assertEqual(report['labels_complete'], 0)
        self.assertEqual(report['pairs_complete'], 0)

    def test_complete_fixtures_still_need_signed_frozen_gate(self):
        report = inspect(*fixtures())
        self.assertTrue(report['human_intake_complete'])
        self.assertFalse(report['scientific_training_ready'])

    def test_actual_frozen_policy_accepts_only_completed_signed_fixture(self):
        freeze = json.loads((RUNTIME / 'SIGNED_FREEZE_TEMPLATE.json').read_text())
        for key, value in freeze.items():
            if value is False:
                freeze[key] = True
        freeze.update(responsible_reviewer_id='SYNTHETIC_UNIT_TEST_NOT_REAL_SIGNOFF', freeze_date='2026-11-10')
        report = inspect(*fixtures(), freeze=freeze)
        self.assertTrue(report['frozen_policy_gate_passed'], report['frozen_policy_error'])
        self.assertFalse(report['training_executed'])

    def test_missing_duplicate_disagreement(self):
        labels, pairs = fixtures()
        labels.pop()
        other = copy.deepcopy(pairs[0])
        other['meaning'] = 'No'
        pairs.append(other)
        report = inspect(labels, pairs)
        self.assertIn('missing_record', report['issue_counts'])
        self.assertIn('disagreement', report['issue_counts'])

    def test_agreeing_duplicate_still_needs_adjudicated_unique_record(self):
        labels, pairs = fixtures()
        labels.append(copy.deepcopy(labels[0]))
        self.assertIn('duplicate_review', inspect(labels, pairs)['issue_counts'])

    def test_nonhuman_and_text_change_rejected(self):
        labels, pairs = fixtures()
        labels[0]['reviewer_type'] = 'llm'
        pairs[0]['Rewrite'] += ' edited'
        report = inspect(labels, pairs)
        self.assertIn('missing_or_nonhuman_provenance', report['issue_counts'])
        self.assertIn('binding_mismatch', report['issue_counts'])

    def test_borderline_not_coerced(self):
        labels, pairs = fixtures()
        pairs[0]['meaning'] = 'Borderline'
        pairs[0]['notes'] = 'Unresolved, synthetic test'
        self.assertIn('unresolved_borderline', inspect(labels, pairs)['issue_counts'])
        self.assertEqual(pairs[0]['meaning'], 'Borderline')

    def test_adverse_final_review_uses_frozen_fallback_not_missing(self):
        labels, pairs = fixtures()
        pairs[0].update(meaning='No', semantic_drift='Yes', notes='Synthetic adverse decision')
        report = inspect(labels, pairs)
        self.assertTrue(report['human_intake_complete'])
        self.assertEqual(report['pairs_human_rejected'], 1)

    def test_ambiguous_label_and_nonexact_evidence_block(self):
        labels, pairs = fixtures()
        labels[0].update(human_label='Unclear', evidence_span='not a source span')
        report = inspect(labels, pairs)
        self.assertIn('corpus_adjudication_required', report['issue_counts'])
        self.assertIn('missing_or_nonexact_evidence', report['issue_counts'])

    def test_inconsistent_ratings_and_bad_date(self):
        labels, pairs = fixtures()
        pairs[0].update(meaning='Yes', semantic_drift='Yes', notes='Synthetic', review_date='yesterday')
        report = inspect(labels, pairs)
        self.assertIn('inconsistent_answers', report['issue_counts'])
        self.assertIn('missing_or_nonhuman_provenance', report['issue_counts'])


if __name__ == '__main__':
    unittest.main()

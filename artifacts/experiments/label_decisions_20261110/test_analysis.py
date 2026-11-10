"""Integrity of hypothetical scenarios; no human labels or training fixtures."""
import hashlib
import json
import unittest

from analyze import AI, HERE, ROOT, categorized, read, scenarios, sources


class DecisionAuditTests(unittest.TestCase):
    def test_exact67_originals_and_no_relabel(self):
        rows = categorized()
        original = {r['ID']: r for r in read(AI) if r['ai_candidate_label'] == 'Unclear'}
        self.assertEqual(len(rows), 67)
        self.assertEqual({r['ID'] for r in rows}, set(original))
        self.assertEqual(sum(r['split'] == 'train' for r in rows), 43)
        for row in rows:
            self.assertEqual(row['Original'], original[row['ID']]['Original'])
            self.assertEqual(row['proposed_label'], original[row['ID']]['proposed_label'])
            self.assertIn(row['context_excerpt'], row['Original'])
            self.assertFalse(row['is_human_annotation'])
            self.assertFalse(row['label_changed'])

    def test_primary_label_lineage_matches_all148(self):
        rows, annotations = sources()
        self.assertEqual(len(rows), 148)
        for row in rows:
            prior = annotations[row['ID']]
            self.assertEqual(prior['label_a'], row['proposed_label'])
            self.assertGreaterEqual(float(prior['confidence_a']), 2)
            self.assertEqual(prior['gold_status'], 'text_only_assistant_proposal_pending_human')

    def test_scenario_arithmetic_and_arm_parity(self):
        summary, authors = scenarios()
        baseline, all_removed = summary[:2]
        self.assertEqual((baseline['train_sources'], baseline['validation_sources']), (105, 43))
        self.assertEqual((all_removed['train_sources'], all_removed['validation_sources']), (62, 19))
        self.assertEqual(all_removed['formula_updates_if_new_protocol_approved'], 80)
        for row in summary:
            self.assertEqual(row['train_sources'], row['train_Left'] + row['train_Right'])
            self.assertEqual(row['A'], row['B'])
            self.assertEqual(row['B'], row['C'])
            self.assertEqual(row['D'], row['E'])
            self.assertEqual(row['D'], 2*row['A'])
            self.assertFalse(row['applied'])
            retained = sum(a['retained'] for a in authors if a['scenario']==row['scenario'] and a['split']=='train')
            self.assertEqual(retained, row['train_sources'])

    def test_frozen_files_and_received_sources_unchanged(self):
        manifest = json.loads((HERE / 'PROVENANCE.json').read_text(encoding='utf-8'))
        for name, digest in manifest['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_newline_comparison_not_repair(self):
        result = json.loads((HERE / 'NEWLINE_DIAGNOSTIC.json').read_text())
        self.assertNotEqual(result['received_text_sha256'], result['supplied_hash'])
        self.assertEqual(result['canonical_text_sha256'], result['supplied_hash'])
        self.assertTrue(result['equal_only_after_documented_crlf_to_lf_comparison'])
        self.assertFalse(result['normalization_applied_to_data'])


if __name__ == '__main__':
    unittest.main()

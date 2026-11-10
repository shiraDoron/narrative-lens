"""Integrity checks for an AI audit, not tests of human/semantic truth."""
import csv
import hashlib
import json
import unittest

from build_analysis import GROUPS, HERE, ROOT, build_rows
from findings import findings


class FocusedAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = build_rows()

    def test_exact_previous_57_plus_7(self):
        with GROUPS.open(encoding='utf-8-sig', newline='') as stream:
            old = [r for r in csv.DictReader(stream)
                   if r['quality_group'] != 'all_available_ai_and_automatic_checks_passed']
        self.assertEqual(len(old), 64)
        self.assertEqual(sum(r['quality_group'] == 'ai_substantial_semantic_concern' for r in old), 7)
        self.assertEqual({r['ID'] for r in old}, set(findings()))

    def test_outputs_bind_to_canonical_texts_and_frozen_flags(self):
        # build_rows asserts canonical Original/Style equality and recomputes
        # all seven lexical flags from the actual frozen implementation AST.
        self.assertEqual(len({r['ID'] for r in self.rows}), 64)

    def test_all_cases_have_explanation_and_second_reading(self):
        for row in self.rows:
            for field in ('contrast', 'finding', 'second_reading', 'recommendation'):
                self.assertTrue(row[field].strip(), (row['ID'], field))
            self.assertTrue(row['second_reading_completed'])
            self.assertFalse(row['is_human_review'])
            self.assertFalse(row['changes_acceptance'])
            self.assertFalse(row['blind_review'])

    def test_source_manifest_unchanged(self):
        manifest = json.loads((HERE / 'PROVENANCE.json').read_text(encoding='utf-8'))
        for relative, expected in manifest['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected)

    def test_saved_csv_is_reproducible(self):
        with (HERE / 'FOCUSED_QUALITY_REVIEW_64.csv').open(encoding='utf-8-sig', newline='') as stream:
            saved = list(csv.DictReader(stream))
        self.assertEqual(saved, [{k: str(v) for k, v in row.items()} for row in self.rows])

    def test_previous_no_not_silently_promoted_to_acceptance(self):
        row = next(r for r in self.rows if r['ID'] == 'creators:11db638844f4')
        self.assertEqual(row['prior_ai_meaning'], 'No')
        self.assertEqual(row['disposition'], 'unresolved_semantic_risk')
        self.assertFalse(row['changes_acceptance'])


if __name__ == '__main__':
    unittest.main()

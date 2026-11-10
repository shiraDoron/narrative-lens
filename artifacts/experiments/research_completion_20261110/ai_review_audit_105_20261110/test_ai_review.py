"""Review artifact integrity tests; these do not establish semantic correctness."""

import ast
from collections import Counter
import json
import unittest

from build_reports import HERE, FIELDS, SPECIAL, parse_source, protected_hashes, counts, build, candidates, read, sha, text_sha, verify
from review_decisions import DECISIONS


class AIReviewTests(unittest.TestCase):
    def test_01_raw_source_is_preserved(self):
        receipt = json.loads((HERE / 'SOURCE_RECEIPT.json').read_text())
        self.assertEqual(receipt['original_sha256'], receipt['archived_sha256'])
        self.assertEqual(sha(HERE / 'SOURCE_CHATGPT_REVIEW_15_RECEIVED.md'), receipt['original_sha256'])
        self.assertFalse(receipt['original_review_edited'])
        self.assertEqual(len(parse_source(HERE / 'SOURCE_CHATGPT_REVIEW_15_RECEIVED.md')), 15)

    def test_02_105_canonical_text_bindings(self):
        expected = {row['ID']: row for row in candidates()}
        rows = read(HERE / 'AI_REVIEW_ALL_105.csv')
        self.assertEqual(len(rows), 105)
        self.assertEqual({row['ID'] for row in rows}, set(expected))
        for row in rows:
            self.assertEqual(row['Original'], expected[row['ID']]['Original'])
            self.assertEqual(row['Style_Rewrite'], expected[row['ID']]['Style'])
            self.assertEqual(row['source_sha256'], text_sha(row['Original']))
            self.assertEqual(row['rewrite_sha256'], text_sha(row['Style_Rewrite']))

    def test_03_first15_remaining90_are_disjoint(self):
        first = read(HERE / 'SECOND_AI_REVIEW_15.csv')
        remaining = read(HERE / 'AI_REVIEW_REMAINING_90.csv')
        self.assertEqual(len(first), 15)
        self.assertEqual(len(remaining), 90)
        self.assertFalse({row['ID'] for row in first} & {row['ID'] for row in remaining})
        self.assertEqual({row['ID'] for row in first + remaining}, set(DECISIONS))

    def test_04_valid_ratings_are_ai_only(self):
        rows = read(HERE / 'AI_REVIEW_ALL_105.csv')
        self.assertFalse(any(key.startswith('human_') for key in rows[0]))
        for row in rows:
            self.assertTrue(all(row[field] in {'Yes', 'No', 'Borderline'} for field in FIELDS))
            self.assertTrue(row['ai_notes'])
            self.assertEqual(row['is_human_review'], 'False')
            self.assertEqual(row['blind_review'], 'False')

    def test_05_change_log_agrees_with_both_versions(self):
        prior = {row['ID']: row for row in parse_source(HERE / 'SOURCE_CHATGPT_REVIEW_15_RECEIVED.md')}
        current = {row['ID']: row for row in read(HERE / 'SECOND_AI_REVIEW_15.csv')}
        rows = read(HERE / 'DECISION_COMPARISON_15.csv')
        self.assertEqual(len(rows), 15)
        for row in rows:
            changes = []
            for name, field in zip(['meaning', 'narrative', 'style'], FIELDS):
                self.assertEqual(row['source_ai_' + name], prior[row['ID']][name])
                self.assertEqual(row['audited_ai_' + name], current[row['ID']][field])
                if row['source_ai_' + name] != row['audited_ai_' + name]:
                    changes.append(name.title())
            self.assertEqual(row['changed_fields'], '|'.join(changes))
            self.assertEqual(row['source_ai_notes'], prior[row['ID']]['notes'])

    def test_06_four_cases_have_explicit_second_pass(self):
        rows = {row['ID']: row for row in read(HERE / 'DECISION_COMPARISON_15.csv')}
        self.assertTrue(all(rows[rid]['second_pass_notes'] for rid in SPECIAL))

    def test_07_summary_recounts_stored_ratings(self):
        summary = json.loads((HERE / 'REVIEW_SUMMARY.json').read_text())
        for key, filename in [('audited15', 'SECOND_AI_REVIEW_15.csv'),
                              ('remaining90', 'AI_REVIEW_REMAINING_90.csv'), ('all105', 'AI_REVIEW_ALL_105.csv')]:
            self.assertEqual(summary[key], counts(read(HERE / filename)))
        rows = read(HERE / 'AI_REVIEW_ALL_105.csv')
        self.assertEqual(summary['all_three_yes'], sum(all(row[field] == 'Yes' for field in FIELDS) for row in rows))
        self.assertTrue(summary['all_three_yes_not_training_acceptance'])

    def test_08_no_duplicate_manual_keys(self):
        tree = ast.parse((HERE / 'review_decisions.py').read_text(encoding='utf-8'))
        node = next(node for node in tree.body if isinstance(node, ast.Assign))
        keys = [key.value for key in node.value.keys]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(set(keys), {row['ID'] for row in candidates()})

    def test_09_human_files_and_sources_unchanged(self):
        verify()
        provenance = json.loads((HERE / 'REVIEW_PROVENANCE.json').read_text())
        self.assertEqual(provenance['protected_source_sha256'], protected_hashes())
        self.assertFalse(provenance['is_human'])
        self.assertFalse(provenance['independent_different_model_verified'])
        self.assertTrue(provenance['source_review_visible'])

    def test_10_rebuild_cannot_overwrite_reviews(self):
        source = HERE / 'SOURCE_CHATGPT_REVIEW_15_RECEIVED.md'
        before = sha(source)
        with self.assertRaisesRegex(ValueError, 'no overwrite'):
            build(source)
        self.assertEqual(sha(source), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)

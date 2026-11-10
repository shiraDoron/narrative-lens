"""Archive/binding and separation checks; not semantic adjudication."""
import json
import sys
import unittest

from audit_import import HERE, HANDOFF, INPUTS, binding_issues, read, sha


class ImportTests(unittest.TestCase):
    def test_raw_files_are_byte_identical(self):
        from pathlib import Path
        audit = json.loads((HERE / 'IMPORT_AUDIT.json').read_text(encoding='utf-8'))
        for name in INPUTS:
            self.assertEqual(sha(HERE / 'raw' / name), audit['summary']['original_file_sha256'][name])
            received = Path('C:/Users/P0039126/Downloads') / name
            if received.exists():
                self.assertEqual(sha(HERE / 'raw' / name), sha(received))

    def test_coverage_and_exact_original_binding(self):
        for name, form, keys, count in [
            (INPUTS[0], 'PAIRS_210.csv', ('ID', 'variant'), 210),
            (INPUTS[1], 'LABELS_148.csv', ('ID',), 148),
        ]:
            actual, expected = read(HERE / 'raw' / name), read(HANDOFF / 'forms' / form)
            self.assertEqual(len(actual), count)
            issues = binding_issues(actual, expected, keys, ('Original', 'source_sha256'))
            self.assertFalse([i for i in issues if i['field'] in ('Original', 'source_sha256') or
                              i['problem'] in ('missing_key', 'unexpected_key', 'duplicate')])
            self.assertEqual(len({tuple(r[k] for k in keys) for r in actual}), count)

    def test_newline_mismatch_reported_not_silently_normalized(self):
        audit = json.loads((HERE / 'IMPORT_AUDIT.json').read_text(encoding='utf-8'))
        self.assertEqual(audit['summary']['exact_bound_pair_rows'], 209)
        self.assertEqual(audit['summary']['exact_bound_label_rows'], 148)
        self.assertEqual(len(audit['issues']), 2)
        self.assertTrue(all('0105f26ef9f1' in i['key'] and 'Paraphrase' in i['key'] for i in audit['issues']))
        row = next(r for r in read(HERE / 'PAIR_COMPARISON_210.csv') if r['exact_binding_valid'] == 'False')
        self.assertEqual(row['old_qc_pass'], 'N/A')

    def test_no_human_answers_or_acceptance(self):
        for name, fields in [(INPUTS[0], ('meaning', 'stance', 'style_change', 'semantic_drift', 'reviewer_type')),
                              (INPUTS[1], ('human_label', 'proposed_label_correct', 'reviewer_type'))]:
            for row in read(HERE / 'raw' / name):
                self.assertTrue(all(row[k] == '' for k in fields))
        for row in read(HERE / 'PAIR_COMPARISON_210.csv'):
            self.assertEqual(row['eligible_for_training'], 'False')
            self.assertEqual(row['is_human_review'], 'False')
        # Verify the actual frozen human gate rejects these raw AI records.
        sys.path.insert(0, str(HERE.parents[0] / 'main_training_runtime_20261110'))
        from contract import assert_human
        with self.assertRaises(ValueError):
            assert_human(read(HERE / 'raw' / INPUTS[0])[0])

    def test_duplicate_and_changed_hash_are_detected(self):
        source = dict(ID='synthetic', Original='text', source_sha256='invalid')
        problems = binding_issues([source, source], [source], ('ID',), ('Original',))
        self.assertIn('duplicate', {p['problem'] for p in problems})
        self.assertIn('content_hash_mismatch', {p['problem'] for p in problems})


if __name__ == '__main__':
    unittest.main()

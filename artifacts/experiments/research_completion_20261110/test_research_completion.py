"""Technical fixtures only. No experimental generation, human labeling, or model runs."""

import copy
import json
import re
import subprocess
import sys
import unittest

from common import HERE, ROOT, COMPLETION, RUN, CANDIDATE, FOLLOW, candidates, read, verify
from audit_readiness import check_candidates, check_disjoint
from evaluation_contract import classification_metrics, aligned_arm_metrics
import import_review


class ResearchCompletionTests(unittest.TestCase):
    def test_01_frozen_inputs_and_exact105(self):
        verify()
        rows = candidates()
        check_candidates(rows)
        self.assertEqual(len(rows), 105)
        self.assertEqual(sum(row['style_protocol_cohort'].startswith('legacy') for row in rows), 30)

    def test_02_availability_flag_regression(self):
        rows = copy.deepcopy(candidates())
        rows[0]['style_present'] = 'False'
        with self.assertRaisesRegex(ValueError, 'availability'):
            check_candidates(rows)

    def test_03_author_disjoint_and_overlap_rejection(self):
        assignments = read(FOLLOW / 'author_splits.csv')
        groups = check_disjoint(assignments)
        self.assertEqual({key: len(value) for key, value in groups.items()}, {'train': 9, 'val': 4, 'test': 6})
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            check_disjoint(assignments + [dict(assignments[0], split='test')])

    def test_04_packages_have_blank_answers_and_exact_pairs(self):
        expected = {row['ID']: row for row in candidates()}
        pairs = read(HERE / 'HUMAN_STYLE_REVIEW_105.csv')
        self.assertEqual(len(pairs), 105)
        for row in pairs:
            self.assertEqual(row['Original'], expected[row['ID']]['Original'])
            self.assertEqual(row['ChatGPT_Style_Rewrite'], expected[row['ID']]['Style'])
            self.assertTrue(all(not value for key, value in row.items() if key.startswith('human_')))
        intake = read(HERE / 'PAIRED_QC_INTAKE_210.csv')
        self.assertEqual(len({(row['ID'], row['variant']) for row in intake}), 210)
        self.assertTrue(all(row['Rewrite'] == expected[row['ID']][row['variant']] for row in intake))
        self.assertTrue(all(not row['meaning'] and not row['reviewer_id'] for row in intake))

    def test_05_blind_and_assisted_separate(self):
        blind = (HERE / 'HUMAN_STYLE_REVIEW_105.md').read_text(encoding='utf-8')
        assisted = (HERE / 'HUMAN_STYLE_REVIEW_105_QC_ASSISTED.md').read_text(encoding='utf-8')
        self.assertNotIn('סימני סיכון אוטומטיים', blind)
        self.assertNotIn('semantic_similarity', blind)
        self.assertEqual(assisted.count('**סימני סיכון אוטומטיים בלבד:**'), 105)
        self.assertIn('אינה עיוורת', assisted)
        self.assertIn('style proxy below existing substantial rule', assisted)

    def test_06_label_intakes_are_proposals_no_test(self):
        cohort = {row['row_id']: row for row in read(FOLLOW / 'analysis_cohort.csv')}
        for name, count, split in [('NARRATIVE_LABEL_VALIDATION_105.csv', 105, 'train'),
                                   ('NARRATIVE_LABEL_VALIDATION_43_VALIDATION.csv', 43, 'val')]:
            rows = read(HERE / name)
            self.assertEqual(len(rows), count)
            self.assertTrue(all(cohort[row['ID']]['split'] == split for row in rows))
            self.assertTrue(all(not row['human_label'] and not row['reviewer_id'] for row in rows))

    def test_07_full105_and_val43_import_bindings(self):
        self.assertEqual(len(import_review.registry('pairs105', 'extension_v1_run01')), 105)
        expected = import_review.registry('labels43')
        self.assertEqual(len(expected), 43)
        parsed = import_review.parse(HERE / 'NARRATIVE_LABEL_VALIDATION_43_VALIDATION.md', 'labels43')
        self.assertEqual({row['ID'] for row in parsed}, set(expected))
        self.assertTrue(all(row['Original'] == expected[row['ID']]['Original'] for row in parsed))
        with self.assertRaisesRegex(ValueError, 'missing/invalid'):
            import_review.validate(parsed, expected, 'labels43', 'human')

    def test_08_full105_markdown_parses_without_text_edits(self):
        rows = import_review.parse(HERE / 'HUMAN_STYLE_REVIEW_105.md', 'pairs105')
        expected = import_review.registry('pairs105', 'extension_v1_run01')
        self.assertEqual(len(rows), 105)
        self.assertTrue(all(row['Original'] == expected[row['ID']]['Original'] and
                            row['ChatGPT_Style_Rewrite'] == expected[row['ID']]['Style'] for row in rows))

    def test_09_readiness_fails_closed_with_current_coverage(self):
        result = subprocess.run([sys.executable, str(HERE / 'audit_readiness.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        audit = json.loads(result.stdout)
        self.assertFalse(audit['training_ready'])
        self.assertEqual(audit['missing_styles'], 0)
        self.assertEqual(audit['configs_checked'], 25)
        self.assertEqual(audit['schedules_checked'], 25)
        self.assertEqual(audit['training_runs'], 0)

    def test_10_qc_triage_is_complete_not_adjudication(self):
        rows = read(HERE / 'QC_FAILURE_TRIAGE_150.csv')
        self.assertEqual(len(rows), 150)
        self.assertEqual(len({(row['ID'], row['method']) for row in rows}), 150)
        self.assertTrue(all(row['semantic_drift_status'] == 'not adjudicated' for row in rows))
        self.assertTrue(all(row['rhetorical_intensity_status'] == 'not independently measured' for row in rows))

    def test_11_inactive_predictions_not_dropped_or_renormalized(self):
        result = classification_metrics(['Right-wing', 'Left-wing'],
                                        [[.6, 0, 0, 0, 0, .3, .1], [0, 0, 0, 0, 0, .1, .9]])
        self.assertEqual(result['accuracy'], .5)
        self.assertEqual(result['macro_f1'], .5)
        self.assertEqual(result['inactive_output_rate'], .5)

    def test_12_task_and_probability_contract(self):
        for label, probabilities in [('Zionist', [1, 0, 0, 0, 0, 0, 0]),
                                     ('Left-wing', [.5, .5]),
                                     ('Left-wing', [0, 0, 0, 0, 0, .1, .1]),
                                     ('Left-wing', [float('nan'), 0, 0, 0, 0, 0, 1])]:
            with self.assertRaises(ValueError):
                classification_metrics([label], [probabilities])

    def fixture_predictions(self):
        return [dict(ID='technical_fixture', seed=7, arm=arm, gold='Left-wing',
                     probabilities=[0, 0, 0, 0, 0, .1, .9]) for arm in 'ABCDE']

    def test_13_arm_alignment_and_duplicate_rejection(self):
        records = self.fixture_predictions()
        self.assertEqual(len(aligned_arm_metrics(records)), 5)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            aligned_arm_metrics(records + [records[0]])
        with self.assertRaisesRegex(ValueError, 'same evaluation IDs'):
            aligned_arm_metrics(records[:-1])

    def test_14_gold_consistency_across_arms(self):
        records = self.fixture_predictions()
        records[0]['gold'] = 'Right-wing'
        with self.assertRaisesRegex(ValueError, 'Inconsistent gold'):
            aligned_arm_metrics(records)

    def test_15_document_links_and_historical_numbers(self):
        for path in [ROOT / 'THESIS_RESEARCH_DIRECTION_HE.md', HERE / 'README_HE.md', HERE / 'QC_FAILURE_ANALYSIS_HE.md']:
            text = path.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if not target.startswith(('https:', 'http:', '#')):
                    self.assertTrue((path.parent / target.split('#')[0]).exists(), target)
        thesis = (ROOT / 'THESIS_RESEARCH_DIRECTION_HE.md').read_text(encoding='utf-8')
        for number in ['0.3895', '0.3255', '0.5903', '0.5437', '0.4842', '0.6565', '22/30', '6/30', '9/30']:
            self.assertIn(number, thesis)

    def test_16_numeric_nli_and_similarity_guards_match_frozen_thresholds(self):
        for folder in ['automatic_qc', 'paraphrase_qc']:
            rows = read(RUN / folder / 'rewrite_validation.csv')
            self.assertEqual(len(rows), 75)
            for row in rows:
                forward = float(row['entailment_forward'])
                reverse = float(row['entailment_reverse'])
                self.assertTrue(0 <= forward <= 1 and 0 <= reverse <= 1)
                self.assertEqual(row['guard_bidirectional_nli'] == 'True', min(forward, reverse) >= .6)
                self.assertEqual(row['guard_similarity'] == 'True', float(row['semantic_similarity']) >= .85)


if __name__ == '__main__':
    unittest.main(verbosity=2)

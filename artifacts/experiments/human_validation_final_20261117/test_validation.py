"""Regression tests for independent packets, incremental agreement and safe adjudication."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from bundle import HERE, read, text_sha
from merge_reviews import agreement, merge, run, verify_handoff


class ValidationTests(unittest.TestCase):
    def test_immutable_source_collection_and_handoff(self):
        verify_handoff()

    def test_all348_once_and_first122_in_both_independent_orders(self):
        key = {r['review_id']: r for r in read(HERE / 'COORDINATOR_PRIVATE_KEY.csv')}
        priority = {rid for rid, r in key.items() if r['priority_block'] == 'True'}
        self.assertEqual(len(priority), 122)
        a, b = self.forms()
        for rows in (a, b):
            self.assertEqual(len(rows), 348)
            self.assertEqual({r['review_id'] for r in rows}, set(key))
            self.assertEqual(len({r['review_id'] for r in rows}), 348)
            self.assertEqual({r['review_id'] for r in rows[:122]}, priority)
            self.assertEqual(len(rows[122:]), 226)
            for row in rows:
                self.assertEqual(text_sha(row['Original']), key[row['review_id']]['source_sha256'])
                self.assertEqual(row['label'], '')
                self.assertNotIn('priority_block', row)
                self.assertNotIn('author', row)
                self.assertNotIn('triage_score', row)
        self.assertNotEqual([r['review_id'] for r in a[:122]], [r['review_id'] for r in b[:122]])
        self.assertNotEqual([r['review_id'] for r in a[122:]], [r['review_id'] for r in b[122:]])

    def test_zip_packages_never_include_private_key_or_other_reviewer(self):
        for role in ('A', 'B'):
            with zipfile.ZipFile(HERE / f'REVIEWER_{role}_ONLY.zip') as archive:
                names = set(archive.namelist())
                self.assertEqual(len(names), 16)
                self.assertIn('REVIEW.csv', names)
                self.assertIn('START_HE.md', names)
                self.assertFalse(any('PRIVATE' in name or 'KEY' in name or 'AI' in name for name in names))
                self.assertEqual(archive.read('REVIEW.csv'), (HERE / ('reviewer_'+role) / 'REVIEW.csv').read_bytes())

    def test_nine_remain_quarantined_with_refined_evidence(self):
        rows = read(HERE / 'HISTORICAL_NINE_AUDIT.csv')
        self.assertEqual(len(rows), 9)
        key_ids = {r['ID'] for r in read(HERE / 'COORDINATOR_PRIVATE_KEY.csv')}
        self.assertFalse(key_ids & {r['ID'] for r in rows})
        overlaps = [r for r in rows if r['issue_type'].startswith('exact_')]
        self.assertEqual(len(overlaps), 5)
        self.assertTrue(all(r['protected_split'] == 'test' and r['body_jaccard'] == '1.0' for r in overlaps))
        carter = next(r for r in rows if r['ID'] == 'creators:209914')
        self.assertIn('James Carter', carter['credit_or_relation'])
        self.assertIn('BOOK', carter['initial_flag_refinement'])

    def test_blank_or_partial_reviews_have_pending_not_false_errors(self):
        a, b = self.forms()
        result = merge(a, b, [])
        self.assertEqual(result['report']['verified_binary_labels'], 0)
        self.assertEqual(result['report']['missing_to200'], 200)
        self.assertEqual(result['report']['errors'], 0)
        self.assertIsNone(result['report']['agreement_before_adjudication']['raw_agreement'])
        self.assertIsNone(result['report']['agreement_before_adjudication']['cohen_kappa'])
        self.fill(a[0], 'Left', 'reviewer_A')
        partial = merge(a[:1], [], [])
        self.assertEqual(partial['report']['valid_reviews_A'], 1)
        self.assertEqual(partial['report']['pending_B'], 348)
        self.assertEqual(partial['report']['verified_binary_labels'], 0)
        self.assertEqual(partial['report']['errors'], 0)

    def test_raw_agreement_and_kappa_include_unclear_before_adjudication(self):
        pairs = [('Left', 'Left'), ('Right', 'Right'), ('Unclear', 'Unclear'),
                 ('Left', 'Right'), ('Right', 'Left'), ('Unclear', 'Right')]
        result = agreement(pairs)
        self.assertEqual(result['valid_independent_pairs'], 6)
        self.assertEqual(result['raw_agreement'], .5)
        self.assertAlmostEqual(result['cohen_kappa'], .25)
        self.assertIsNone(agreement([('Left', 'Left')])['cohen_kappa'])

    def test_binary_agreement_counts_but_unclear_does_not(self):
        a, b = self.forms()
        bmap = {r['review_id']: r for r in b}
        self.fill(a[0], 'Left', 'reviewer_A')
        self.fill(bmap[a[0]['review_id']], 'Left', 'reviewer_B')
        self.fill(a[1], 'Unclear', 'reviewer_A')
        self.fill(bmap[a[1]['review_id']], 'Unclear', 'reviewer_B')
        result = merge(a, b, [])['report']
        self.assertEqual(result['verified_binary_labels'], 1)
        self.assertEqual(result['missing_to200'], 199)
        self.assertEqual(result['resolved_unclear'], 1)
        self.assertEqual(result['agreement_before_adjudication']['raw_agreement'], 1.)
        self.assertFalse(result['training_ready'])

    def test_disagreement_requires_distinct_bound_human_adjudication(self):
        a, b, rid = self.disagreement()
        first = merge(a, b, [])
        self.assertEqual(first['report']['verified_binary_labels'], 0)
        decision = first['to_fill'][0]
        decision.update(final_label='Right', evidence_span=a[0]['Original'][:20], rationale='synthetic test decision only',
                        reviewer_type='human', adjudicator_id='third_reviewer', review_date='2026-11-17', assistance_used='none')
        result = merge(a, b, [decision])
        self.assertEqual(result['report']['verified_binary_labels'], 1)
        self.assertEqual(result['to_fill'], [])
        self.assertEqual(result['report']['agreement_before_adjudication']['raw_agreement'], 0.)
        decision['adjudicator_id'] = 'reviewer_A'
        self.assertEqual(merge(a, b, [decision])['report']['verified_binary_labels'], 0)
        decision['adjudicator_id'] = 'third_reviewer'
        a[0]['reason'] = 'corrected synthetic review reason'
        stale = merge(a, b, [decision])
        self.assertEqual(stale['report']['verified_binary_labels'], 0)
        self.assertEqual(len(stale['to_fill']), 1)
        self.assertTrue(any('stale' in row['issues'] for row in stale['issues']))
        self.assertEqual(stale['disputes'][0]['review_id'], rid)

    def test_same_person_ai_assistance_and_missing_metadata_never_verify(self):
        a, b = self.forms()
        rb = next(r for r in b if r['review_id'] == a[0]['review_id'])
        self.fill(a[0], 'Left', 'SamePerson')
        self.fill(rb, 'Left', 'sameperson')
        self.assertEqual(merge(a, b, [])['report']['verified_binary_labels'], 0)
        rb['reviewer_id'] = 'other'
        a[0]['reviewer_type'] = 'ai'
        self.assertEqual(merge(a, b, [])['report']['valid_reviews_A'], 0)
        a[0]['reviewer_type'] = 'human'
        a[0]['assistance_used'] = 'AI proposed label'
        self.assertEqual(merge(a, b, [])['report']['verified_binary_labels'], 0)
        a[0]['assistance_used'] = 'none'
        a[0]['review_date'] = ''
        self.assertEqual(merge(a, b, [])['report']['verified_binary_labels'], 0)

    def test_source_corruption_including_pending_rows_and_bad_evidence_rejected(self):
        a, b = self.forms()
        a[0]['Original'] += ' altered'
        result = merge(a, b, [])
        self.assertEqual(result['report']['invalid_A'], 1)
        a, b = self.forms()
        self.fill(a[0], 'Left', 'reviewer_A')
        a[0]['evidence_span'] = 'invented exact evidence not present'
        self.assertEqual(merge(a, b, [])['report']['valid_reviews_A'], 0)
        with self.assertRaises(ValueError):
            merge(a+[copy.deepcopy(a[0])], b, [])
        a[0]['review_id'] = 'unknown'
        with self.assertRaises(ValueError):
            merge(a, b, [])

    def test_output_archives_raw_files_and_never_overwrites_a_previous_run(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'round01'
            ap, bp = HERE / 'reviewer_A/REVIEW.csv', HERE / 'reviewer_B/REVIEW.csv'
            report = run(ap, bp, None, out)
            self.assertEqual(report['verified_binary_labels'], 0)
            self.assertEqual((out / 'reviewer_A_received.csv').read_bytes(), ap.read_bytes())
            self.assertTrue((out / 'ENGINE_SNAPSHOT.py').exists())
            self.assertTrue((out / 'PROGRESS_HE.md').exists())
            self.assertEqual(read(out / 'ADJUDICATION_TO_FILL.csv'), [])
            self.assertFalse(json.loads((out / 'PROGRESS.json').read_text(encoding='utf-8'))['corpus_modified'])
            with self.assertRaises(ValueError):
                run(ap, bp, None, out)

    @staticmethod
    def forms():
        return read(HERE / 'reviewer_A/REVIEW.csv'), read(HERE / 'reviewer_B/REVIEW.csv')

    @staticmethod
    def fill(row, label, who):
        row.update(label=label, evidence_span=row['Original'][:20] if label != 'Unclear' else '',
                   reason='synthetic unit-test decision only', confidence='2', reviewer_type='human',
                   reviewer_id=who, review_date='2026-11-17', assistance_used='none')

    def disagreement(self):
        a, b = self.forms()
        rid = a[0]['review_id']
        self.fill(a[0], 'Left', 'reviewer_A')
        self.fill(next(r for r in b if r['review_id'] == rid), 'Right', 'reviewer_B')
        return a, b, rid


if __name__ == '__main__':
    unittest.main()

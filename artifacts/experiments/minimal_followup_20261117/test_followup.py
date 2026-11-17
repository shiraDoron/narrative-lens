"""Meaningful regression tests for fixed pairing, isolation and human/AI separation."""
import copy
import json
import unittest

from prepare import HERE, PREVIOUS, ROOT, LEXICAL, SYNTAX, literal_edits, previous, quotations, numbers, read, sha, text_sha
from check_labels import validate


class FollowupTests(unittest.TestCase):
    def test_frozen_sources_and_prepared_outputs(self):
        manifest = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
        for path, digest in manifest['source_sha256'].items():
            self.assertEqual(sha(ROOT / path), digest, path)
        for path, digest in manifest['output_sha256'].items():
            self.assertEqual(sha(HERE / path), digest, path)

    def test_same_train_sources_for_every_method(self):
        cohort = read(HERE / 'analysis_cohort.csv')
        self.assertEqual(len(cohort), 9)
        self.assertTrue(all(r['split'] == 'train' for r in cohort))
        variants = [json.loads(s) for s in (HERE / 'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(len(variants), 54)
        for method in ('Original', 'Paraphrase', 'Style', 'Minimal_v1', 'Minimal_v2', 'Minimal_v3'):
            rows = [r for r in variants if r['condition'] == method]
            self.assertEqual(len(rows), 9)
            self.assertEqual({r['row_id'] for r in rows}, {r['row_id'] for r in cohort})
        for row in variants:
            if row['condition'] not in ('Minimal_v2', 'Minimal_v3'):
                continue
            expected = literal_edits(row['original'], LEXICAL[row['row_id']])
            if row['condition'] == 'Minimal_v3':
                expected = literal_edits(expected, SYNTAX[row['row_id']])
            self.assertEqual(row['rewrite'], expected)
            self.assertEqual(previous.anchors(row['original']), previous.anchors(row['rewrite']))
            self.assertEqual(quotations(row['original']), quotations(row['rewrite']))
            self.assertEqual(numbers(row['original']), numbers(row['rewrite']))

    def test_label_package_exact97_and_original_text_binding(self):
        extra = {r['ID']: r for r in read(PREVIOUS / 'TRAIN_POOL_202.csv') if r['existing105'] == 'False'}
        key = {r['review_id']: r for r in read(HERE / 'LABEL_97_PRIVATE_KEY.csv')}
        forms = read(HERE / 'LABEL_97_BLIND.csv')
        self.assertEqual(len(forms), 97)
        self.assertEqual({r['ID'] for r in key.values()}, set(extra))
        for row in forms:
            source = extra[key[row['review_id']]['ID']]
            self.assertEqual(row['Original'], source['Original'])
            self.assertEqual(text_sha(row['Original']), source['source_sha256'])
            self.assertEqual(row['label'], '')
            self.assertNotIn('author', row)
            self.assertNotIn('original_label_a', row)
        ai = read(HERE / 'AI_LABEL_SCREEN.csv')
        self.assertEqual(len(ai), 97)
        self.assertTrue(all(r['reviewer_type'] == 'ai' and r['human_validated'] == 'False' and r['source_label_changed'] == 'False' for r in ai))
        self.assertEqual({r['review_id'] for r in ai}, set(key))

    def test_pilot_blind_review_key(self):
        forms = read(HERE / 'PILOT_HUMAN_BLIND.csv')
        key = {r['review_id']: r for r in read(HERE / 'PILOT_HUMAN_KEY.csv')}
        self.assertEqual(len(forms), 45)
        self.assertEqual(len(key), 45)
        for row in forms:
            self.assertEqual(text_sha(row['Rewrite']), key[row['review_id']]['rewrite_sha256'])
            self.assertEqual(row['meaning'], '')
            self.assertNotIn('method', row)

    def test_human_intake_rejects_blank_ai_duplicates_and_changed_text(self):
        rows = read(HERE / 'LABEL_97_BLIND.csv')
        self.assertEqual(validate(rows)['completed'], 0)
        modified = copy.deepcopy(rows)
        modified[0].update(label='Left', evidence_span='invented evidence', reason='synthetic test',
                           confidence='3', reviewer_type='ai', reviewer_id='synthetic', review_date='2026-11-17', assistance_used='AI')
        self.assertEqual(validate(modified)['completed'], 0)
        modified[0]['Original'] += 'changed'
        errors = validate(modified)['errors']
        self.assertTrue(any(isinstance(e, dict) and 'Original changed' in e['issues'] for e in errors))
        duplicated = rows[:-1] + [rows[0]]
        self.assertTrue(any(isinstance(e, str) and 'distinct' in e for e in validate(duplicated)['errors']))

    def test_replayed_historical_style_metrics_unchanged(self):
        old = {(r['ID'], 'Minimal_v1' if r['method'] == 'Minimal' else r['method']): r for r in read(PREVIOUS / 'PILOT_METRICS.csv')}
        new = read(HERE / 'PILOT_METRICS.csv')
        for r in new:
            key = r['ID'], r['method']
            if key in old:
                for field in ('word_edit_fraction', 'substantial_style_change', 'punctuation_l1_per100'):
                    self.assertEqual(r[field], old[key][field])

    def test_semantic_screen_complete_and_historical_decisions_replayed(self):
        new = read(HERE / 'rewrite_validation.csv')
        self.assertEqual(len(new), 54)
        old = {(r['row_id'], 'Minimal_v1' if r['condition'] == 'Minimal' else r['condition']): r
               for r in read(PREVIOUS / 'rewrite_validation.csv')}
        for row in new:
            self.assertEqual(row['human_verified'], 'False')
            key = row['row_id'], row['condition']
            if key in old:
                self.assertEqual(row['passed'], old[key]['passed'])
                self.assertEqual(row['rejection_reasons'], old[key]['rejection_reasons'])
        surface = read(HERE / 'SURFACE_STYLE_66.csv')
        self.assertEqual(len(surface), 54)
        for row in surface:
            if row['method'] == 'Original':
                self.assertEqual(float(row['standardized_mean_abs_change']), 0.)


if __name__ == '__main__':
    unittest.main()

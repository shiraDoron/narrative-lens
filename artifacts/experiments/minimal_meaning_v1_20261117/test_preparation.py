"""Regression checks for isolation, provenance and paired pilot integrity."""
import json
import unittest

from prepare import HERE, ROOT, anchors, read, sha, text_sha


class PreparationTests(unittest.TestCase):
    def test_frozen_inputs_and_outputs_unchanged(self):
        manifest = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
        for path, digest in manifest['source_sha256'].items():
            self.assertEqual(sha(ROOT / path), digest, path)
        for path, digest in manifest['output_sha256'].items():
            self.assertEqual(sha(HERE / path), digest, path)

    def test_pool_is_train_and_never_gold(self):
        pool = read(HERE / 'TRAIN_POOL_202.csv')
        self.assertEqual(len(pool), 202)
        self.assertEqual(len({r['ID'] for r in pool}), 202)
        self.assertTrue(all(r['split'] == 'train' and r['human_label'] == '' and r['training_ready'] == 'False' for r in pool))
        self.assertEqual(len(read(HERE / 'PROVISIONAL_200.csv')), 200)
        old = read(ROOT / 'artifacts/experiments/main_training_preparation_20261109/TRAIN_CONDITION_ID_MAP.csv')
        self.assertTrue({r['ID'] for r in old} <= {r['ID'] for r in read(HERE / 'PROVISIONAL_200.csv')})

    def test_paired_pilot_and_blind_key(self):
        variants = [json.loads(line) for line in (HERE / 'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(len(variants), 36)
        sources = {r['row_id'] for r in read(HERE / 'analysis_cohort.csv')}
        self.assertEqual(len(sources), 9)
        for method in ('Original', 'Paraphrase', 'Style', 'Minimal'):
            self.assertEqual({r['row_id'] for r in variants if r['condition'] == method}, sources)
        key = {r['review_id']: r for r in read(HERE / 'HUMAN_REVIEW_KEY.csv')}
        forms = read(HERE / 'HUMAN_REVIEW_BLIND.csv')
        self.assertEqual(len(forms), 27)
        for row in forms:
            self.assertEqual(text_sha(row['Rewrite']), key[row['review_id']]['rewrite_sha256'])
            self.assertNotIn('method', row)
            self.assertNotIn('author', row)
            self.assertEqual(row['meaning'], '')

    def test_protected_claim_changes_are_flagged(self):
        for a, b in [('all people', 'most people'), ('no one', 'few people'), ('will win', 'might win'),
                     ('will not win', 'will win'), ('every person may leave', 'some person will leave')]:
            self.assertNotEqual(anchors(a), anchors(b))
        # Explicit limitation: anchor equality cannot detect changed actor/claim.
        self.assertEqual(anchors('Alice will win'), anchors('Bob will win'))

    def test_budget_and_test_lock(self):
        config = json.loads((HERE / 'DRAFT_CONFIG.json').read_text(encoding='utf-8'))
        self.assertEqual(config['optimizer_updates'] * config['batch_size'], 4160)
        self.assertEqual(len(config['arms']) * len(config['seeds']), 35)
        self.assertEqual(config['test'], 'disabled')
        self.assertEqual(config['status'], 'preparation_only_not_training_ready')

    def test_draft_schedule_coverage_and_matched_augmentation(self):
        from schedules import schedule
        ids = sorted(r['ID'] for r in read(HERE / 'PROVISIONAL_200.csv'))
        for seed in (7, 42, 123, 2026, 31415):
            single = schedule(ids, ['Original'], seed)
            double = schedule(ids, ['Original', 'Style'], seed)
            self.assertEqual(len(single), 4160)
            self.assertEqual(len(double), 4160)
            self.assertEqual(len(set(single[:200])), 200)
            self.assertEqual(len(set(double[:400])), 400)
            self.assertEqual(double, schedule(ids, ['Original', 'Minimal'], seed))
            self.assertEqual(double, schedule(ids, ['Original', 'Paraphrase'], seed))
        with self.assertRaises(ValueError):
            schedule(ids[:-1], ['Original'], 42)


if __name__ == '__main__':
    unittest.main()

"""Collection/provenance/leakage and two-rater intake regression tests."""
import copy
import json
import unittest

from collect import HERE, ROOT, FOLLOW, alias_key, read, sha, text_sha
from prepare import parse_body, score, windows
from review_intake import check


class CollectionTests(unittest.TestCase):
    def test_frozen_inputs_and_outputs(self):
        manifest = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
        for path, digest in manifest['protected_inputs_sha256'].items():
            self.assertEqual(sha(ROOT / path), digest, path)
        for path, digest in manifest['output_sha256'].items():
            self.assertEqual(sha(HERE / path), digest, path)
        for path, digest in manifest['source_snapshots_sha256'].items():
            self.assertEqual(sha(ROOT / path), digest, path)

    def test_more_than200_unique_sources_and_assigned_train_writers_only(self):
        rows = read(HERE / 'CANDIDATES.csv')
        splits = {r['author']: r['split'] for r in read(FOLLOW / 'author_splits.csv')}
        self.assertGreater(len(rows), 200)
        for key in ('ID', 'article_group', 'source_sha256'):
            self.assertEqual(len({r[key] for r in rows}), len(rows))
        self.assertEqual(len({alias_key(r['source_url']) for r in rows}), len(rows))
        self.assertTrue(all(splits[r['author']] == r['split'] == 'train' for r in rows))
        self.assertEqual(len({r['author'] for r in rows}), 9)
        self.assertTrue(all(r['human_label'] == '' and r['training_ready'] == 'False' for r in rows))

    def test_literal_source_text_and_preserved_old_originals(self):
        old = {r['ID']: r['Original'] for r in read(HERE.parent / 'minimal_meaning_v1_20261117/TRAIN_POOL_202.csv')}
        for row in read(HERE / 'CANDIDATES.csv'):
            self.assertEqual(text_sha(row['Original']), row['source_sha256'])
            _, raw, _, bylines = parse_body(ROOT / row['source_snapshot'], row['byline'])
            self.assertEqual(bylines, [row['byline']])
            if row['original105'] == 'True':
                self.assertEqual(row['Original'], old[row['ID']])
            else:
                self.assertEqual(row['Original'], ' '.join(raw[int(row['paragraph_start']):int(row['paragraph_end_exclusive'])]))
                self.assertTrue(35 <= int(row['word_count']) <= 100)

    def test_two_separate_blind_packets_and_unfilled_adjudication(self):
        a, b = read(HERE / 'REVIEWER_A_BLIND.csv'), read(HERE / 'REVIEWER_B_BLIND.csv')
        key = {r['review_id']: r for r in read(HERE / 'PRIVATE_REVIEW_KEY.csv')}
        self.assertEqual(len(a), len(key))
        self.assertEqual({r['review_id'] for r in a}, {r['review_id'] for r in b})
        self.assertNotEqual([r['review_id'] for r in a], [r['review_id'] for r in b])
        for row in a+b:
            self.assertEqual(text_sha(row['Original']), key[row['review_id']]['source_sha256'])
            self.assertNotIn('author', row)
            self.assertNotIn('triage_score', row)
            self.assertNotIn('source_url', row)
            self.assertEqual(row['label'], '')
        self.assertTrue(all(r['final_label'] == '' for r in read(HERE / 'ADJUDICATION_TEMPLATE.csv')))

    def test_observed_cross_split_and_authorship_risks_are_excluded(self):
        rows = read(HERE / 'CANDIDATES.csv')
        rejected = read(HERE / 'QUARANTINED_SOURCES.csv')
        self.assertFalse({r['source_url'] for r in rows} & {r['source_url'] for r in rejected})
        evidence = read(HERE / 'HOLDOUT_DUPLICATE_EVIDENCE.csv')
        self.assertTrue(all(float(r['full_body_jaccard']) >= .8 or r['exact_normalized_body'] == 'True' for r in evidence))
        self.assertTrue(all(r['protected_split'] in ('val', 'test') for r in evidence))
        audit = json.loads((HERE / 'FULL_BODY_AUDIT.json').read_text(encoding='utf-8'))
        self.assertEqual(audit['flagged_pairs'], [])
        self.assertEqual(audit['candidate_articles'], len(rows))

    def test_new_retrieval_receipts_have_real_logged_sources(self):
        events = [json.loads(s) for s in (HERE / 'FETCH_LOG.jsonl').read_text(encoding='utf-8').splitlines()]
        successful = {e['retrieved_at_utc'] for e in events if e.get('status') == 200}
        receipts = read(HERE / 'NEW_ARTICLE_RECEIPTS.csv')
        self.assertGreater(len(receipts), 0)
        self.assertTrue(all(r['retrieved_at_utc'] in successful for r in receipts))
        self.assertTrue(all(r['byline_verified'] == 'True' for r in receipts))
        self.assertFalse(any('/api/features/releases/' in e.get('request_url', '') and e['request_url'].endswith('/6') for e in events))

    def test_blank_and_ai_reviews_never_count_as_human_gold(self):
        a, b, adjud = self.forms()
        result = check(a, b, adjud)
        self.assertEqual(result['binary_candidates_after_human_labels'], 0)
        self.assertEqual(result['missing_to200'], 200)
        self.fill(a[0], 'Left', 'assistant')
        a[0]['reviewer_type'] = 'ai'
        self.assertEqual(check(a, b, adjud)['binary_candidates_after_human_labels'], 0)

    def test_independence_and_adjudication_not_last_row_wins(self):
        a, b, adjud = self.forms()
        rid = a[0]['review_id']
        rb = next(r for r in b if r['review_id'] == rid)
        decision = next(r for r in adjud if r['review_id'] == rid)
        self.fill(a[0], 'Left', 'synthetic_reviewer_A')
        self.fill(rb, 'Right', 'synthetic_reviewer_B')
        result = check(a, b, adjud)
        self.assertEqual(result['binary_candidates_after_human_labels'], 0)
        self.assertIn(rid, result['disagreement_sources'])
        decision.update(final_label='Unclear', rationale='synthetic ambiguity', reviewer_type='human',
                        adjudicator_id='synthetic_adjudicator', review_date='2026-11-17', assistance_used='none')
        self.assertEqual(check(a, b, adjud)['unclear_after_human_labels'], 1)
        rb['label'] = 'Left'
        self.assertEqual(check(a, b, adjud)['binary_candidates_after_human_labels'], 1)
        rb['reviewer_id'] = a[0]['reviewer_id']
        self.assertEqual(check(a, b, adjud)['binary_candidates_after_human_labels'], 0)

    def test_changed_text_invalid_evidence_and_duplicate_ids_rejected(self):
        a, b, adjud = self.forms()
        rid = a[0]['review_id']
        rb = next(r for r in b if r['review_id'] == rid)
        self.fill(a[0], 'Left', 'synthetic_A')
        self.fill(rb, 'Left', 'synthetic_B')
        a[0]['Original'] += ' changed'
        self.assertEqual(check(a, b, adjud)['binary_candidates_after_human_labels'], 0)
        a[0]['Original'] = rb['Original']
        a[0]['evidence_span'] = 'fabricated support that is absent'
        self.assertEqual(check(a, b, adjud)['binary_candidates_after_human_labels'], 0)
        with self.assertRaises(ValueError):
            check(a+[copy.deepcopy(a[0])], b, adjud)

    def test_text_cue_triage_is_not_an_author_based_label(self):
        text = 'Government should protect workers and their rights.'
        self.assertTrue(score(text)['priority_political_review'])
        self.assertNotIn('label', score(text))
        self.assertFalse(score('I walked home and fed my cat.')['priority_political_review'])
        choices = list(windows([(0, 'These are the words of a paragraph with too few words.')]))
        self.assertEqual(choices, [])

    @staticmethod
    def forms():
        return (read(HERE / 'REVIEWER_A_BLIND.csv'), read(HERE / 'REVIEWER_B_BLIND.csv'), read(HERE / 'ADJUDICATION_TEMPLATE.csv'))

    @staticmethod
    def fill(row, label, reviewer):
        row.update(label=label, evidence_span=row['Original'][:20], reason='synthetic unit-test judgment only', confidence='2',
                   reviewer_type='human', reviewer_id=reviewer, review_date='2026-11-17', assistance_used='none')


if __name__ == '__main__':
    unittest.main()

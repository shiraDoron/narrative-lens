"""Safety/integrity tests for data planning, not tests of political label truth."""
import json
import math
import unittest

from inventory import HERE, ROOT, FOLLOW, V1, paragraphs, normalized_url, read, sha, text_sha, words


class ExpansionTests(unittest.TestCase):
    def test_frozen_and_consumed_inputs_unchanged(self):
        hashes = json.loads((HERE / 'SOURCE_BINDINGS.json').read_text(encoding='utf-8'))
        for name, digest in hashes.items():
            self.assertEqual(sha(ROOT / name), digest, name)

    def test_only_assigned_train_authors_and_no_heldout_urls(self):
        splits = {r['author']: r['split'] for r in read(FOLLOW / 'author_splits.csv')}
        inventory = read(HERE / 'TRAIN_ARTICLE_INVENTORY.csv')
        self.assertEqual(len({r['source_url'] for r in inventory}), len(inventory))
        heldout = {normalized_url(r['source_url']) for r in read(FOLLOW / 'text_annotations.csv') if splits[r['author']] != 'train'}
        self.assertTrue(all(r['split'] == 'train' and splits[r['author']] == 'train' for r in inventory))
        self.assertFalse({r['source_url'] for r in inventory} & heldout)

    def test_candidates_are_literal_new_windows_and_distinct_noncore_articles(self):
        candidates = read(HERE / 'AI_CANDIDATES_14.csv')
        core = {normalized_url(r['source_url']) for r in read(V1 / 'TRAIN_POOL_202.csv') if r['existing105'] == 'True'}
        self.assertEqual(len(candidates), 14)
        self.assertEqual(len({r['article_group'] for r in candidates}), 14)
        for r in candidates:
            _, ps = paragraphs((ROOT / r['source_snapshot']).read_text(encoding='utf-8'))
            expected = ' '.join(ps[int(r['paragraph_start']):int(r['paragraph_end_exclusive'])])
            self.assertEqual(r['Original'], expected)
            self.assertEqual(r['source_sha256'], text_sha(expected))
            self.assertTrue(35 <= words(expected) <= 100)
            self.assertIn(r['evidence_span'], expected)
            self.assertNotIn(r['source_url'], core)
            self.assertEqual(r['training_ready'], 'False')
            self.assertEqual(r['human_validated'], 'False')
            self.assertEqual(r['corpus_label_changed'], 'False')

    def test_blind_forms_are_unfilled_and_bound(self):
        forms = read(HERE / 'CANDIDATE_HUMAN_BLIND_14.csv')
        key = {r['review_id']: r for r in read(HERE / 'CANDIDATE_PRIVATE_KEY_14.csv')}
        self.assertEqual(len(forms), 14)
        self.assertEqual({r['review_id'] for r in forms}, set(key))
        for r in forms:
            self.assertNotIn('author', r)
            self.assertNotIn('ai_proposed_label', r)
            self.assertEqual(r['label'], '')
            self.assertEqual(r['reviewer_type'], '')
            self.assertEqual(text_sha(r['Original']), key[r['review_id']]['source_sha256'])

    def test_aliases_and_authorship_flags_do_not_inflate_candidates(self):
        aliases = read(HERE / 'ARCHIVE_ALIAS_AUDIT.csv')
        self.assertTrue(all(r['counted_as_new'] == 'False' and r['matched_cached_urls'] for r in aliases))
        flags = read(HERE / 'AUTHORSHIP_REVIEW_FLAGS.csv')
        candidates = read(HERE / 'AI_CANDIDATES_14.csv')
        self.assertFalse({r['article_group'] for r in flags} & {r['article_group'] for r in candidates})
        summary = json.loads((HERE / 'CANDIDATE_SUMMARY.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['confirmed_novel_archive_articles'], 0)
        self.assertEqual(summary['human_accepted_new'], 0)

    def test_planning_arithmetic_and_unchanged_training_budget(self):
        for row in read(HERE / 'WORKLOAD_SCENARIOS.csv'):
            deficit = 200-int(row['accepted_core_assumption'])-int(row['accepted_local_assumption'])
            self.assertEqual(int(row['deficit']), deficit)
            self.assertEqual(int(row['candidate_articles_to_screen']), math.ceil(deficit/float(row['assumed_yield'])))
            self.assertEqual(row['empirical_yield'], 'False')
        plan = json.loads((HERE / 'COLLECTION_PLAN_PROPOSED.json').read_text(encoding='utf-8'))
        self.assertFalse(plan['training_protocol_changed'])
        self.assertFalse(plan['training_updates_changed'])
        self.assertFalse(plan['train_run'])
        self.assertFalse(plan['test_run'])
        self.assertEqual(plan['minimal_prompt_development'], 'stopped; possible control only; retain all negative results')

    def test_duplicate_screen_is_metadata_or_train_only(self):
        audit = json.loads((HERE / 'CANDIDATE_ISOLATION_AUDIT.json').read_text(encoding='utf-8'))
        self.assertFalse(audit['heldout_text_used'])
        self.assertFalse(audit['heldout_predictions'])
        self.assertEqual(audit['exact_match_existing_all_split_source_hashes'], [])
        self.assertEqual(audit['train_only_near_duplicates_jaccard_ge_08'], [])

    def test_starter119_covers_exact_old105_plus14_without_showing_ai_labels(self):
        forms = read(HERE / 'LABEL_STARTER_119_BLIND.csv')
        key = {r['review_id']: r for r in read(HERE / 'LABEL_STARTER_PRIVATE_KEY_119.csv')}
        old_ids = {r['ID'] for r in read(V1 / 'TRAIN_POOL_202.csv') if r['existing105'] == 'True'}
        new_ids = {r['candidate_id'] for r in read(HERE / 'AI_CANDIDATES_14.csv')}
        self.assertEqual(len(forms), 119)
        self.assertEqual({r['ID'] for r in key.values()}, old_ids | new_ids)
        self.assertEqual(len({r['article_group'] for r in key.values()}), 119)
        for r in forms:
            self.assertEqual(text_sha(r['Original']), key[r['review_id']]['source_sha256'])
            self.assertEqual(r['label'], '')
            self.assertNotIn('source_kind', r)
            self.assertNotIn('prior_ai_proposal_as_recorded', r)
            self.assertNotIn('author', r)


if __name__ == '__main__':
    unittest.main()

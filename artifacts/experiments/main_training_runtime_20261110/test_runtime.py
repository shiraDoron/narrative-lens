"""Technical tests; fabricated fixture reviews never become study Human Validation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import contract as c
import data as d
import trainer as t


class RuntimeTests(unittest.TestCase):
    def fixtures(self):
        # Wholly fabricated IDs/text/ratings for contract tests in TemporaryDirectory.
        train = [dict(ID=f'fixture_train{i}', author=f'fixture_author{i}', split='train',
                      label=c.ACTIVE[i], Original=f'fictional source{i}', Paraphrase=f'fictional paraphrase{i}',
                      Style=f'fictional style{i}') for i in range(2)]
        validation = [dict(ID=f'fixture_val{i}', author='fixture_validation_author',
                           Original=f'fictional validation{i}', label=c.ACTIVE[i % 2]) for i in range(43)]
        person = dict(reviewer_type='human', reviewer_id='fictional-unit-test-rater', review_date='2026-11-10')
        labels = lambda rows: [dict(ID=row['ID'], human_label=row['label'], source_sha256=c.text_sha(row['Original']), **person) for row in rows]
        pairs = [dict(ID=row['ID'], variant=variant, source_sha256=c.text_sha(row['Original']),
                      rewrite_sha256=c.text_sha(row[variant]), meaning='Yes', stance='Yes', style_change='Yes',
                      semantic_drift='No', notes='', **person) for row in train for variant in ('Paraphrase', 'Style')]
        freeze = dict(responsible_reviewer_id='fictional-unit-test-rater', freeze_date='2026-11-10',
                      protocol_sha256=c.sha(c.PROTOCOL), human_source_labels_confirmed=True,
                      paired_human_qc_finalized=True, adjudication_complete=True,
                      mixed_generator_protocol_documented=True, unknown_generator_parameters_acknowledged=True)
        return train, validation, labels(train), labels(validation), pairs, freeze

    def test_01_actual_sources_disjoint_no_exact_leakage(self):
        audit = d.source_audit()
        self.assertEqual(audit['train_sources'], 105)
        self.assertEqual(audit['validation_sources'], 43)
        self.assertEqual(audit['authors'], {'train': 9, 'validation': 4, 'test': 6})
        self.assertEqual(audit['test_model_inputs'], 0)

    def test_02_scientific_spec_is_frozen(self):
        c.assert_frozen()
        self.assertEqual(c.SEEDS, (7, 42, 123, 2026, 31415))
        self.assertEqual(c.LABELS[5:], c.ACTIVE)

    def test_03_raw_ai_cannot_be_gold(self):
        row = c.read(c.RESEARCH / 'ai_review_audit_105_20261110/AI_REVIEW_ALL_105.csv')[0]
        row['reviewer_type'] = 'human'  # Relabeling metadata must not admit raw AI rows.
        with self.assertRaisesRegex(ValueError, 'AI judgments'):
            c.assert_human(row)

    def test_04_nonhuman_provenance_rejected(self):
        for row in [dict(reviewer_type='llm', reviewer_id='AI', review_date='2026-11-10'),
                    dict(reviewer_type='human', reviewer_id='r', review_date='2026-11-10', is_human_review=False)]:
            with self.assertRaises(ValueError):
                c.assert_human(row)

    def test_05_unfilled_freeze_does_not_approve(self):
        with self.assertRaises(ValueError):
            c.validate_freeze(json.loads((c.HERE / 'SIGNED_FREEZE_TEMPLATE.json').read_text()))

    def test_06_missing_labels_block(self):
        train, _, labels, _, _, _ = self.fixtures()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            c.validate_labels(labels[:-1], train)

    def test_07_wrong_label_hash_blocks(self):
        train, _, labels, _, _, _ = self.fixtures()
        labels[0]['source_sha256'] = 'bad'
        with self.assertRaisesRegex(ValueError, 'hash'):
            c.validate_labels(labels, train)

    def test_08_gold_disagreement_is_not_relabel(self):
        train, _, labels, _, _, _ = self.fixtures()
        labels[0]['human_label'] = c.ACTIVE[1]
        with self.assertRaisesRegex(ValueError, 'corpus decision'):
            c.validate_labels(labels, train)

    def test_09_symmetric_human_fallback(self):
        train, validation, labels, val_labels, pairs, freeze = self.fixtures()
        pairs[1]['style_change'] = 'Borderline'
        pairs[1]['notes'] = 'Fictional fixture: limited style'
        with patch.object(c, 'candidates', return_value=train), patch.object(c, 'validation_sources', return_value=validation):
            policy, val = c.policy_inputs(labels, val_labels, pairs, freeze)
        self.assertEqual(len(val), 43)
        self.assertEqual(policy['primary_all_attempted']['B'][0]['text'], train[0]['Original'])
        self.assertEqual(policy['primary_all_attempted']['C'][0]['text'], train[0]['Original'])
        self.assertEqual(len(policy['primary_all_attempted']['D']), len(policy['primary_all_attempted']['E']))

    def test_10_missing_or_duplicate_pair_blocked(self):
        train, validation, labels, val_labels, pairs, freeze = self.fixtures()
        with patch.object(c, 'candidates', return_value=train), patch.object(c, 'validation_sources', return_value=validation):
            for bad in [pairs[:-1], pairs + [pairs[0]]]:
                with self.assertRaises(ValueError):
                    c.policy_inputs(labels, val_labels, bad, freeze)

    def test_11_rewrite_mutation_blocked(self):
        train, validation, labels, val_labels, pairs, freeze = self.fixtures()
        pairs[0]['Rewrite'] = 'an edited fictional text'
        with patch.object(c, 'candidates', return_value=train), patch.object(c, 'validation_sources', return_value=validation):
            with self.assertRaisesRegex(ValueError, 'rewrite edited'):
                c.policy_inputs(labels, val_labels, pairs, freeze)

    def test_12_snapshot_roundtrip_and_tamper_rejection(self):
        train, validation, labels, val_labels, pairs, freeze = self.fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for name, rows in [('train.csv', labels), ('val.csv', val_labels), ('pairs.csv', pairs)]:
                c.save(directory / name, rows)
            c.dump(directory / 'freeze.json', freeze)
            with patch.object(d, 'HERE', directory), patch.object(d, 'source_audit', return_value={'fixture_only': True}), \
                 patch.object(d, 'candidates', return_value=train), patch.object(c, 'candidates', return_value=train), \
                 patch.object(c, 'validation_sources', return_value=validation):
                snapshot = d.approve(directory / 'train.csv', directory / 'val.csv', directory / 'pairs.csv', directory / 'freeze.json', 'fixture')
                views, val, _ = d.load_approved(snapshot)
                self.assertEqual(len(views['D']), 4)
                self.assertEqual(len(val), 43)
                with (snapshot / 'primary_all_attempted/ARM_C.csv').open('a') as file:
                    file.write('tamper')
                with self.assertRaisesRegex(ValueError, 'changed'):
                    d.load_approved(snapshot)

    def test_13_no_snapshot_no_model_load(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(t, 'load_backend') as loader:
            with self.assertRaises(FileNotFoundError):
                t.run_scientific(Path(tmp) / 'no-snapshot', Path(tmp) / 'no-run', 'primary_all_attempted')
            loader.assert_not_called()

    def test_14_actual_smoke_passed_all_arms(self):
        report = json.loads((c.HERE / 'smoke_runtime/SMOKE_RESULT.json').read_text())
        self.assertEqual(report['status'], 'passed')
        self.assertEqual({row['arm'] for row in report['arms']}, set(c.ARMS))
        self.assertTrue(all(row['updates'] == 2 and row['processed_examples'] == 32 and row['reload_logits_identical'] for row in report['arms']))
        self.assertEqual(len({row['initial_head_sha256'] for row in report['arms']}), 1)
        self.assertTrue(report['encoder_unchanged'] and report['encoder_gradients_absent'])
        self.assertEqual(report['validation_inputs'] + report['test_inputs'], 0)
        self.assertFalse(report['scientific_result'])

    def test_15_smoke_checkpoint_shape_and_reload(self):
        path = c.HERE / 'smoke_runtime/A/head_seed42.pt'
        if not path.exists():
            repeats = sorted(c.HERE.glob('smoke*/A/head_seed42.pt'))
            if not repeats:
                self.skipTest('Weights intentionally excluded from Git; rerun smoke to recreate')
            path = repeats[0]
        import torch
        checkpoint = torch.load(path, map_location='cpu', weights_only=True)
        self.assertEqual(tuple(checkpoint['head_state']['0.weight'].shape), (128, 384))
        self.assertEqual(tuple(checkpoint['head_state']['3.weight'].shape), (7, 128))
        self.assertEqual(checkpoint['updates'], 2)
        self.assertFalse(checkpoint['scientific_result'])

    def test_16_all25_full_budget_schedules_match(self):
        for seed in c.SEEDS:
            plans = {}
            for arm, variants in c.ARMS.items():
                view = c.read(c.CANDIDATE / f'DRAFT_ARM_{arm}.csv')
                plan = c.schedule(view, seed, 140)
                self.assertEqual(len(view), 105 * len(variants))
                self.assertEqual(len(plan), 2240)
                plans[arm] = [(row['ID'], row['view_index']) for row in plan]
            self.assertEqual(plans['D'], plans['E'])

    def test_17_common_validation_contract_and_active_labels(self):
        records = []
        for seed in [7, 42]:
            for arm in c.ARMS:
                for index, label in enumerate(c.ACTIVE):
                    probabilities = [0] * 7
                    probabilities[5 + index] = 1
                    if arm == 'B' and index == 0:
                        probabilities = [1, 0, 0, 0, 0, 0, 0]
                    records.append(dict(ID=f'fixture{index}', author=f'fixture_author{index}', gold=label,
                                        seed=seed, arm=arm, probabilities=probabilities))
        summary = t.summarize_validation(records)
        self.assertEqual(summary['arms']['B']['inactive_output_rate']['mean'], .5)
        self.assertEqual(summary['primary_contrasts']['C-B']['mean'], .5)
        self.assertFalse(summary['checkpoint_selection'])
        self.assertEqual(summary['split'], 'validation_only')

    def test_18_ai_quality_groups_are_not_accepted(self):
        rows = c.read(c.HERE / 'QUALITY_GROUPS_105.csv')
        self.assertEqual(len(rows), 105)
        self.assertTrue(all(row['scientifically_accepted'] == 'False' and row['human_validation_status'] == 'pending' for row in rows))
        self.assertEqual(sum(row['quality_group'] == 'ai_substantial_semantic_concern' for row in rows), 7)

    def test_19_tokenization_and_no_hidden_truncation(self):
        audit = json.loads((c.HERE / 'TOKEN_AUDIT_SUMMARY.json').read_text())
        self.assertEqual(audit['n'], 358)
        self.assertEqual(audit['test_rows'], 0)
        self.assertEqual(audit['encoder_max_seq_length'], 256)
        budgets = c.read(c.HERE / 'DRAFT_TOKEN_BUDGET_25.csv')
        self.assertEqual(len(budgets), 25)
        self.assertTrue(all(row['processed_examples'] == '2240' for row in budgets))

    def test_20_all25_orchestration_with_mocked_training_only(self):
        # No fit/inference here: stub predictions and fake sources in a temporary directory.
        import numpy as np
        sources = [dict(ID=f'fictional_source{i}', author=f'fictional_author{i % 9}', label=c.ACTIVE[i % 2],
                        Original=f'fictional original{i}', Paraphrase=f'fictional paraphrase{i}', Style=f'fictional style{i}')
                   for i in range(105)]
        views = {arm: [dict(ID=row['ID'], author=row['author'], label=row['label'], variant=variant, text=row[variant])
                       for row in sources for variant in variants] for arm, variants in c.ARMS.items()}
        val = [dict(ID=f'fictional_val{i}', author='fictional_val_author', label=c.ACTIVE[i % 2], text=f'fictional val{i}') for i in range(43)]
        texts = {row['text'] for view in views.values() for row in view} | {row['text'] for row in val}
        lookup = {text: np.zeros(384, dtype=np.float32) for text in texts}
        token_audit = [dict(text_sha256=c.text_sha(text), tokens_before_truncation=1, encoder_max_seq_length=256, truncated=False) for text in texts]
        backend = SimpleNamespace(np=np, probs=lambda head, vectors: np.tile([0, 0, 0, 0, 0, .9, .1], (len(vectors), 1)))
        def fake_train(backend, view, vectors, seed, updates, out, mode, identity):
            return object(), dict(initial_head_sha256=f'fictional-init{seed}'), c.schedule(view, seed, updates)
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(d, 'load_approved', return_value=(views, val, {})), \
             patch.object(t, 'load_backend', return_value=(backend, object())), \
             patch.object(t, 'encoder_identity', return_value={'fictional_fixture': True}), \
             patch.object(t, 'encode_texts', return_value=(lookup, token_audit)), \
             patch.object(t, 'train_head', side_effect=fake_train) as mocked_train:
            snapshot = Path(tmp) / 'fictional-snapshot'
            snapshot.mkdir()
            c.dump(snapshot / 'MANIFEST.json', {'fictional_fixture': True})
            out = Path(tmp) / 'fictional-run'
            t.run_scientific(snapshot, out, 'primary_all_attempted')
            self.assertEqual(mocked_train.call_count, 25)
            self.assertTrue(all(call.args[4] == 140 for call in mocked_train.call_args_list))
            predictions = json.loads((out / 'validation_predictions.json').read_text())
            self.assertEqual(len(predictions), 25 * 43)
            manifest = json.loads((out / 'RUN_MANIFEST.json').read_text())
            self.assertFalse(manifest['validation_used_for_checkpoint_selection'])
            self.assertFalse(manifest['test_evaluated'])

    def test_21_actual_blank_human_intake_fails_cli(self):
        command = [sys.executable, str(c.HERE / 'cli.py'), 'prepare-human',
                   '--train-labels', str(c.RESEARCH / 'NARRATIVE_LABEL_VALIDATION_105.csv'),
                   '--validation-labels', str(c.RESEARCH / 'NARRATIVE_LABEL_VALIDATION_43_VALIDATION.csv'),
                   '--pair-reviews', str(c.RESEARCH / 'PAIRED_QC_INTAKE_210.csv'),
                   '--signed-freeze', str(c.HERE / 'SIGNED_FREEZE_TEMPLATE.json'), '--name', 'must_not_exist']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('freeze/reviewer required', result.stderr)
        self.assertFalse((c.HERE / 'approved/must_not_exist').exists())

    def test_22_missing_provenance_gives_clear_gate_error(self):
        with self.assertRaisesRegex(ValueError, 'provenance field'):
            c.assert_human(dict(reviewer_type='human', reviewer_id=None, review_date='2026-11-10'))

    def test_23_malformed_optional_note_cell_not_silently_filled(self):
        train, validation, labels, val_labels, pairs, freeze = self.fixtures()
        pairs[0]['notes'] = None  # csv.DictReader missing trailing field, not a human judgment.
        with patch.object(c, 'candidates', return_value=train), patch.object(c, 'validation_sources', return_value=validation):
            with self.assertRaisesRegex(ValueError, 'CSV schema'):
                c.policy_inputs(labels, val_labels, pairs, freeze)

    def test_24_real_head_initialization_matches_for_all_five_seeds(self):
        # Construct fresh untrained heads only; no encoder loading, fit or predictions.
        backend = c.module_from_file('runtime_seed_only', c.ROOT / 'experiments/author_generalization/author_style_controlled.py')
        hashes = []
        for seed in c.SEEDS:
            per_arm = []
            for arm in c.ARMS:
                backend.seed(seed)
                per_arm.append(t.state_digest(backend.head().state_dict()))
            self.assertEqual(len(set(per_arm)), 1)
            hashes.append(per_arm[0])
        self.assertEqual(len(set(hashes)), 5)

    def test_25_nonhuman_import_manifest_cannot_be_relabelled(self):
        train, validation, labels, val_labels, pairs, freeze = self.fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for name, rows in [('train.csv', labels), ('val.csv', val_labels), ('pairs.csv', pairs)]:
                c.save(directory / name, rows)
            c.dump(directory / 'freeze.json', freeze)
            c.dump(directory / 'IMPORT_MANIFEST.json', {'reviewer_type': 'llm'})
            with patch.object(d, 'HERE', directory), patch.object(d, 'source_audit', return_value={'fixture_only': True}), \
                 patch.object(d, 'candidates', return_value=train), patch.object(c, 'candidates', return_value=train), \
                 patch.object(c, 'validation_sources', return_value=validation):
                with self.assertRaisesRegex(ValueError, 'non-human reviewer'):
                    d.approve(directory / 'train.csv', directory / 'val.csv', directory / 'pairs.csv', directory / 'freeze.json', 'must_not_exist')
                self.assertFalse((directory / 'approved/must_not_exist').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)

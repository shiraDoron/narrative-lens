"""Frozen A-E specification and read-only imports. No ML imports or execution."""

import datetime
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESEARCH = ROOT / 'artifacts/experiments/research_completion_20261110'
sys.path.insert(0, str(RESEARCH))
from common import PREP, FOLLOW, CANDIDATE, candidates, read, save as save, dump as dump, sha, text_sha, verify

PROTOCOL = ROOT / 'MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md'
PRODUCTION_WEIGHTS = ROOT / 'models/best_model_sbert_only.pth'
SEEDS = (7, 42, 123, 2026, 31415)
ARMS = {'A': ['Original'], 'B': ['Paraphrase'], 'C': ['Style'],
        'D': ['Original', 'Style'], 'E': ['Original', 'Paraphrase']}
LABELS = ('Zionist', 'Resistance', 'Western', 'Russian', 'Ukrainian', 'Right-wing', 'Left-wing')
ACTIVE = ('Right-wing', 'Left-wing')
BATCH_SIZE = 16
LEARNING_RATE = .001


def module_from_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_policy():
    return module_from_file('runtime_frozen_qc_contract', PREP / 'qc_contract.py')


def schedule(view, seed, updates):
    return module_from_file('runtime_frozen_prepare', PREP / 'prepare.py').schedules(view, seed, updates, BATCH_SIZE)


def validation_sources():
    return [dict(ID=row['row_id'], author=row['author'], Original=row['text'], label=row['narrative_name'])
            for row in read(FOLLOW / 'analysis_cohort.csv') if row['split'] == 'val']


def assert_frozen():
    verify()
    specification = json.loads((HERE / 'FROZEN_BINDINGS.json').read_text())
    for path, digest in specification['protected_files'].items():
        if sha(ROOT / path) != digest:
            raise ValueError('Frozen input/implementation changed: ' + path)
    configs = [json.loads((CANDIDATE / f'CONFIG_{arm}_seed{seed}.json').read_text()) for arm in ARMS for seed in SEEDS]
    for config in configs:
        if (config['lr'], config['batch_size'], config['optimizer_updates'], config['processed_examples']) != (.001, 16, 140, 2240):
            raise ValueError('Candidate configuration differs from frozen protocol')
        if config['output_label_order'] != list(LABELS) or config['optimizer'] != 'Adam':
            raise ValueError('Architecture/label contract differs')


def assert_human(row):
    if any(key.startswith('ai_') for key in row):
        raise ValueError('AI judgments cannot be human gold/QC')
    if str(row.get('is_human_review', '')).lower() == 'false':
        raise ValueError('Source explicitly declares non-human review')
    for field in ('reviewer_type', 'reviewer_id', 'review_date'):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError('Missing/malformed human provenance field: ' + field)
    frozen_policy().provenance(row)
    if any(token in str(row.get('review_type', '')).lower() for token in ['llm', 'ai review']):
        raise ValueError('LLM source cannot be human gold')


def validate_labels(records, expected):
    by_id = frozen_policy().keyed(records, lambda row: row['ID'])
    if set(by_id) != {row['ID'] for row in expected}:
        raise ValueError('Exact human source-label coverage required')
    for source in expected:
        row = by_id[source['ID']]
        assert_human(row)
        if row.get('source_sha256') != text_sha(source['Original']):
            raise ValueError('Human label source hash mismatch')
        if 'Original' in row and row['Original'] != source['Original']:
            raise ValueError('Original text edited in label intake')
        if row.get('human_label') not in ACTIVE:
            raise ValueError('Left/Right human gold required; unclear/mixed need corpus adjudication')
        if row['human_label'] != source['label']:
            raise ValueError('Gold/proposal disagreement requires explicit corpus decision, no silent relabel')
    return by_id


def validate_freeze(record):
    if not isinstance(record.get('responsible_reviewer_id'), str) or not record['responsible_reviewer_id'].strip():
        raise ValueError('Signed development freeze/reviewer required')
    if not isinstance(record.get('freeze_date'), str):
        raise ValueError('Freeze date must be an ISO date string')
    datetime.date.fromisoformat(record['freeze_date'])
    if record.get('protocol_sha256') != sha(PROTOCOL):
        raise ValueError('Freeze must bind the unchanged research protocol')
    required = ('human_source_labels_confirmed', 'paired_human_qc_finalized', 'adjudication_complete',
                'mixed_generator_protocol_documented', 'unknown_generator_parameters_acknowledged')
    if not all(record.get(key) is True for key in required):
        raise ValueError('Human gold/QC/adjudication/provenance freeze is incomplete')


def policy_inputs(train_labels, val_labels, pair_reviews, freeze):
    """Canonical texts + explicit human provenance; AI rows never control acceptance."""
    assert_frozen()
    rows = candidates()
    val = validation_sources()
    validate_freeze(freeze)
    labels = validate_labels(train_labels, rows)
    validation_labels = validate_labels(val_labels, val)
    pairs = frozen_policy().keyed(pair_reviews, lambda row: (row['ID'], row['variant']))
    for (rid, variant), review in pairs.items():
        assert_human(review)
        if not isinstance(review.get('notes'), str):
            raise ValueError('QC notes column missing/malformed; preserve raw file and complete its CSV schema')
        source = next((row for row in rows if row['ID'] == rid), None)
        if source is None or variant not in ('Style', 'Paraphrase'):
            raise ValueError('Unexpected pair ID/variant')
        if 'Original' in review and review['Original'] != source['Original']:
            raise ValueError('Human QC Original edited')
        if 'Rewrite' in review and review['Rewrite'] != source[variant]:
            raise ValueError('Human QC rewrite edited')
    policy = frozen_policy().build_policy(rows, list(labels.values()), list(pairs.values()))
    validation = [dict(ID=row['ID'], author=row['author'], text=row['Original'], label=validation_labels[row['ID']]['human_label']) for row in val]
    if len(validation) != 43:
        raise ValueError('Expected unchanged43 validation Originals')
    return policy, validation

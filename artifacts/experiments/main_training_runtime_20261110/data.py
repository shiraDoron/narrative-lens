"""Human-only scientific data approval, immutable snapshots and exact binding checks."""

import json
import re
import shutil
import unicodedata

from contract import (HERE, FOLLOW, PROTOCOL, ARMS, candidates, validation_sources,
                      policy_inputs, assert_frozen, read, save, dump, sha)


def source_audit():
    assert_frozen()
    train = candidates()
    validation = validation_sources()
    assignments = read(FOLLOW / 'author_splits.csv')
    author_split = {row['author']: row['split'] for row in assignments}
    if len(author_split) != len(assignments):
        raise ValueError('Duplicate/overlapping author assignments')
    train_authors = {row['author'] for row in train}
    val_authors = {row['author'] for row in validation}
    test_authors = {row['author'] for row in assignments if row['split'] == 'test'}
    if train_authors & val_authors or train_authors & test_authors or val_authors & test_authors:
        raise ValueError('Author overlap')
    if not all(author_split[row['author']] == 'train' and row['split'] == 'train' for row in train):
        raise ValueError('Non-train source in105')
    if {row['ID'] for row in train} & {row['ID'] for row in validation}:
        raise ValueError('Source ID leakage')
    annotations = read(FOLLOW / 'text_annotations.csv')
    for field in ('text_sha256', 'article_snapshot_sha256'):
        groups = {}
        for row in annotations:
            groups.setdefault(row[field], set()).add(author_split[row['author']])
        if any(len(splits) > 1 for splits in groups.values()):
            raise ValueError('Cross-split exact source/article hash collision')
    def canonical(text):
        return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC', text).casefold()))
    # Check actual train variants against development validation; never inspect test variants.
    validation_texts = {canonical(row['Original']) for row in validation}
    if any(canonical(row[variant]) in validation_texts for row in train for variant in ('Original', 'Paraphrase', 'Style')):
        raise ValueError('Train variant exactly overlaps validation Original')
    return dict(train_sources=105, validation_sources=43,
                authors=dict(train=len(train_authors), validation=len(val_authors), test=len(test_authors)),
                exact_source_article_hash_collisions=0, train_variant_validation_exact_collisions=0,
                test_model_inputs=0,
                limitation='Exact/hash and author checks do not exclude semantic/event/topic overlap; no test semantic scan')


def approve(train_path, validation_path, pair_path, freeze_path, name):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
        raise ValueError('Use a unique simple snapshot name')
    out = HERE / 'approved' / name
    if out.exists():
        raise ValueError('Approved snapshots are immutable')
    audit = source_audit()
    freeze = json.loads(freeze_path.read_text(encoding='utf-8-sig'))
    policy, validation = policy_inputs(read(train_path), read(validation_path), read(pair_path), freeze)
    attachments = []
    for path, prefix in [(train_path, 'train_labels'), (validation_path, 'validation_labels'), (pair_path, 'pair_qc')]:
        imported_manifest = path.parent / 'IMPORT_MANIFEST.json'
        if imported_manifest.exists():
            provenance = json.loads(imported_manifest.read_text(encoding='utf-8-sig'))
            if provenance.get('reviewer_type') != 'human':
                raise ValueError('Import manifest declares a non-human reviewer; cannot admit as gold/QC')
            attachments.append((imported_manifest, prefix + '_import_manifest.json'))
            for suffix in ('csv', 'md'):
                raw = path.parent / ('received.' + suffix)
                if raw.exists():
                    attachments.append((raw, prefix + '_received.' + suffix))
    out.mkdir(parents=True)
    for path, filename in [(train_path, 'human_train_labels.csv'), (validation_path, 'human_validation_labels.csv'),
                           (pair_path, 'human_pair_reviews.csv'), (freeze_path, 'signed_freeze.json')]:
        shutil.copyfile(path, out / filename)
    for path, filename in attachments:
        shutil.copyfile(path, out / filename)
    save(out / 'validation_originals.csv', validation)
    save(out / 'human_qc_coverage.csv', policy['coverage'])
    author_by_id = {row['ID']: row['author'] for row in candidates()}
    secondary_labels = {label: {author_by_id[row['ID']] for row in policy['secondary_common_accepted']['A'] if row['label'] == label}
                        for label in ('Right-wing', 'Left-wing')}
    secondary_runnable = all(len(authors) >= 2 for authors in secondary_labels.values())
    for cohort in ('primary_all_attempted', 'secondary_common_accepted'):
        directory = out / cohort
        directory.mkdir()
        for arm, view in policy[cohort].items():
            view = [dict(row, author=author_by_id[row['ID']]) for row in view]
            save(directory / f'ARM_{arm}.csv', view, fields=['ID', 'label', 'variant', 'text', 'author'])
    manifest = dict(
        scientific_input_gate_passed=True, protocol_sha256=sha(PROTOCOL),
        human_provenance_basis='Explicit reviewer metadata/declaration; identity not independently authenticated',
        source_audit=audit, n_sources=len(policy['primary_all_attempted']['A']), secondary_runnable=secondary_runnable,
        primary_rule='Frozen human-QC symmetric Original fallback; AI judgments never admit data',
        validation_selection='same43 gold Originals for all arms; fixed-final checkpoint, no selection by validation score',
        files_sha256={str(path.relative_to(out)): sha(path) for path in out.rglob('*') if path.is_file()},
    )
    dump(out / 'MANIFEST.json', manifest)
    return out


def load_approved(directory, cohort='primary_all_attempted'):
    """Revalidate human evidence, canonical texts and hashes before importing ML."""
    source_audit()
    if cohort not in ('primary_all_attempted', 'secondary_common_accepted'):
        raise ValueError('Unknown cohort')
    manifest = json.loads((directory / 'MANIFEST.json').read_text())
    if not manifest.get('scientific_input_gate_passed') or manifest['protocol_sha256'] != sha(PROTOCOL):
        raise ValueError('Snapshot is not bound to the frozen scientific gate')
    for relative, digest in manifest['files_sha256'].items():
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory.resolve()) or sha(path) != digest:
            raise ValueError('Approved snapshot changed: ' + relative)
    policy, expected_validation = policy_inputs(
        read(directory / 'human_train_labels.csv'), read(directory / 'human_validation_labels.csv'),
        read(directory / 'human_pair_reviews.csv'), json.loads((directory / 'signed_freeze.json').read_text()),
    )
    if cohort == 'secondary_common_accepted' and not manifest['secondary_runnable']:
        raise ValueError('Secondary cohort lacks both classes/multiple authors; do not run')
    views = {arm: read(directory / cohort / f'ARM_{arm}.csv') for arm in ARMS}
    authors = {row['ID']: row['author'] for row in candidates()}
    for arm, view in views.items():
        expected = policy[cohort][arm]
        if [{key: row[key] for key in ('ID', 'label', 'variant', 'text')} for row in view] != expected:
            raise ValueError('Arm differs from approved human policy')
        if any(row['author'] != authors[row['ID']] for row in view):
            raise ValueError('Arm author metadata differs from canonical sources')
    validation = read(directory / 'validation_originals.csv')
    if validation != expected_validation:
        raise ValueError('Validation differs from the common43 approved Originals')
    return views, validation, manifest

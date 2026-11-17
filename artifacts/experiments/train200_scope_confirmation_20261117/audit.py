"""Read-only accounting: target200 TRAIN gold sources, held-out authors separate."""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPERIMENTS = HERE.parent


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    if (HERE / 'STATUS.json').exists():
        raise ValueError('Preserve this dated status; create a new audit version')
    paths = [
        ('data_completion_20261109/NARRATIVE_LABEL_VALIDATION_105.csv', 'human_label'),
        ('minimal_followup_20261117/LABEL_97_BLIND.csv', 'label'),
        ('data_expansion_plan_20261117/LABEL_STARTER_119_BLIND.csv', 'label'),
        ('data_expansion_plan_20261117/CANDIDATE_HUMAN_BLIND_14.csv', 'label'),
    ]
    coverage, bindings = [], {}
    for name, field in paths:
        path = EXPERIMENTS / name
        rows = read(path)
        coverage.append(dict(path=name, rows=len(rows), nonblank_label_answers=sum(bool(r.get(field, '').strip()) for r in rows)))
        bindings[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert all(r['nonblank_label_answers'] == 0 for r in coverage)
    assignments = read(EXPERIMENTS / 'verified_human_style_followup_20261026/author_splits.csv')
    author_sets = {split: {r['author'] for r in assignments if r['split'] == split} for split in ('train', 'val', 'test')}
    assert not (author_sets['train'] & author_sets['val'] or author_sets['train'] & author_sets['test'] or author_sets['val'] & author_sets['test'])
    pool = read(EXPERIMENTS / 'minimal_meaning_v1_20261117/TRAIN_POOL_202.csv')
    assert len(pool) == 202 and all(r['author'] in author_sets['train'] and r['split'] == 'train' for r in pool)
    assert sum(r['existing105'] == 'True' for r in pool) == 105
    candidates = read(EXPERIMENTS / 'data_expansion_plan_20261117/AI_CANDIDATES_14.csv')
    assert len(candidates) == 14 and all(r['author'] in author_sets['train'] and r['human_validated'] == 'False' for r in candidates)
    assert len({r['article_group'] for r in candidates}) == 14
    old97 = {r['ID'] for r in pool if r['existing105'] == 'False'}
    alternate = [r for r in candidates if r['role'] == 'alternate_excerpt_of_unclear_article']
    assert len(alternate) == 8 and all(r['old_ID'] in old97 for r in alternate)
    approved = EXPERIMENTS / 'main_training_runtime_20261110/approved'
    approved_dirs = sorted(p.name for p in approved.iterdir() if p.is_dir()) if approved.exists() else []
    assert not approved_dirs
    for path in [ROOT / 'MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md',
                 EXPERIMENTS / 'verified_human_style_followup_20261026/author_splits.csv',
                 EXPERIMENTS / 'minimal_meaning_v1_20261117/DRAFT_CONFIG.json',
                 EXPERIMENTS / 'data_expansion_plan_20261117/COLLECTION_PLAN_PROPOSED.json']:
        bindings[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    status = dict(date='2026-11-17', target=dict(train_human_accepted_sources=200, validation_included_in_target=False, test_included_in_target=False),
                  author_counts={key: len(value) for key, value in author_sets.items()}, authors_disjoint=True,
                  existing_train_sources=202, old_binary_proposals=105, unresolved_original_excerpts=97,
                  additional_candidate_texts=14, alternate_excerpts_from_old97=8, recovered_other_train_articles=6,
                  confirmed_human_gold_in_documented_experiment=0, approved_snapshots=approved_dirs,
                  additional_acquisition_gap_if_old105_all_accepted=95,
                  conditional_acquisition_gap_if_old105_and_new14_all_accepted=81,
                  total_target_pending_human_confirmation=200,
                  distinction='Zero documented approved gold does not mean200 brand-new texts must be collected: validate existing proposals first; acquisition gap95 is conditional.',
                  original97_review='AI screen only:61 insufficient evidence,36 research decisions; no human acceptance yet; alternate passages do not relabel original excerpts',
                  checked_forms=coverage, repeated_forms_not_additional_sources=True,
                  source_sha256=bindings, frozen_protocol_changed=False, training_run=False, test_evaluation=False)
    (HERE / 'STATUS.json').write_text(json.dumps(status, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()

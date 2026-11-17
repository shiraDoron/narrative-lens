"""Train-only preparation. No classifier training or held-out model evaluation."""
import ast
import csv
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLLOW = ROOT / 'artifacts/experiments/verified_human_style_followup_20261026'
CANDIDATE = ROOT / 'artifacts/experiments/data_completion_20261109/runs/extension_v1_run01/candidate_105/CANDIDATE_ID_MAP_105.csv'
STUDY = ROOT / 'artifacts/experiments/style_intervention_v2_20261026/study.py'
# Context-specific decisions by Codex in this session; NOT a general synonym dictionary.
EDITS = {
    'creators:222877': ('along with', 'alongside'),
    'creators:421269': ('by attempting to kill', 'by trying to kill'),
    'creators:122279': ('he who resides at', 'he who lives at'),
    'creators:421241': ('to win over even Democrats', 'to persuade even Democrats'),
    'creators:423633': ('That was just a prelude', 'That was merely a prelude'),
    'creators:2644c7547b3b': ('to reflect on the historical significance', 'to consider the historical significance'),
    'creators:417181': ('to hide funding from their donors', 'to conceal funding from their donors'),
    'creators:417610': ('in pursuit of a distorted sense of justice', 'in pursuit of a distorted notion of justice'),
    'creators:418904': None,  # Quotes and rhetorically loaded imagery: retain original.
}


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def save(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def frozen_style_metrics():
    # Extract only this pure function: no imports/execution of historic training code.
    tree = ast.parse(STUDY.read_text(encoding='utf-8-sig'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'style_metrics')
    import difflib
    scope = {'re': re, 'difflib': difflib}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(STUDY), 'exec'), scope)
    return scope['style_metrics']


PROTECTED = r"\b(?:all|every|each|any|some|most|many|few|none|no|not|never|neither|nor|without|only|always|ever|will|shall|would|should|could|can|may|might|must|likely|probably|possibly|certainly|firmly|allegedly|alleges|purportedly)\b|n['’]t\b|['’]ll\b"


def anchors(text):
    return re.findall(PROTECTED, text.casefold())


def main():
    if (HERE / 'MANIFEST.json').exists():
        raise ValueError('Immutable prepared bundle exists; create a new version instead')
    paths = [FOLLOW / 'author_splits.csv', FOLLOW / 'text_annotations.csv', CANDIDATE,
             ROOT / 'MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md', STUDY,
             HERE / 'PROMPT.txt', HERE / 'PROTOCOL_HE.md', HERE / 'prepare.py']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    assignments = read(FOLLOW / 'author_splits.csv')
    splits = {r['author']: r['split'] for r in assignments}
    assert len(splits) == len(assignments)
    annotations = read(FOLLOW / 'text_annotations.csv')
    # Held-out records are used for identity/hash isolation checks ONLY.
    collisions = []
    for field in ('row_id', 'text_sha256', 'article_snapshot_sha256'):
        groups = {}
        for row in annotations:
            assert row[field]
            groups.setdefault(row[field], set()).add(splits[row['author']])
        collisions.extend(dict(field=field, digest=k, splits=sorted(v)) for k, v in groups.items() if len(v) > 1)
    assert not collisions, 'Cross-split identity/hash collision; stop preparation'
    train = [r for r in annotations if splits[r['author']] == 'train']
    assert len(train) == 202 and all(r['byline_verified'] == 'True' for r in train)
    assert len({r['row_id'] for r in train}) == 202
    assert all(text_sha(r['text']) == r['text_sha256'] for r in train)
    candidates = read(CANDIDATE)
    by_id = {r['row_id']: r for r in train}
    assert len(candidates) == 105 and all(r['ID'] in by_id and r['Original'] == by_id[r['ID']]['text'] for r in candidates)
    extra = sorted([r for r in train if r['row_id'] not in {c['ID'] for c in candidates}], key=lambda r: r['row_id'])
    # Provisional candidate pool only: retain old105, nominate first95 by source ID.
    nominated = {r['ID'] for r in candidates} | {r['row_id'] for r in extra[:95]}
    pool = [dict(ID=r['row_id'], author=r['author'], split='train', Original=r['text'],
                 source_url=r['source_url'], byline=r['byline'], source_sha256=r['text_sha256'],
                 article_sha256=r['article_snapshot_sha256'], source_label_a=r['label_a'],
                 source_label_b=r['label_b'], proposed_binary_label=r['provisional_narrative'],
                 label_provenance=r['gold_status'], existing105=r['row_id'] in {c['ID'] for c in candidates},
                 provisional200=r['row_id'] in nominated, human_label='', reviewer_type='', reviewer_id='',
                 review_date='', evidence_span='', adjudication='', training_ready=False) for r in train]
    save(HERE / 'TRAIN_POOL_202.csv', pool)
    save(HERE / 'PROVISIONAL_200.csv', [r for r in pool if r['provisional200']])
    # TRAIN-only near-duplicate screen; connected groups must stay together in future probes.
    def shingles(text):
        w = re.findall(r'\w+', text.casefold())
        return {tuple(w[i:i+5]) for i in range(len(w)-4)}
    near = []
    for a, b in itertools.combinations(train, 2):
        sa, sb = shingles(a['text']), shingles(b['text'])
        j = len(sa & sb) / max(1, len(sa | sb))
        if a['article_snapshot_sha256'] == b['article_snapshot_sha256'] or j >= .8:
            near.append(dict(ID_a=a['row_id'], ID_b=b['row_id'], jaccard=j))
    dump(HERE / 'AUDIT.json', dict(train_sources=202, verified_named_bylines=202,
         train_authors=len({r['author'] for r in train}), existing_binary_proposals=105,
         additional_sources=97, additional_label_a_counts={label: sum(r['label_a'] == label for r in extra) for label in sorted({r['label_a'] for r in extra})},
         provisional200_not_approved=True, binary200_feasibility='not established: need at least95 of97 additional sources independently eligible after human review, retaining old105 subject to review',
         cross_split_hash_collisions=collisions, train_duplicate_pairs=near,
         heldout_usage='author assignment/source ID/text hash/article hash only; no held-out text metrics, predictions or selection',
         semantic_event_leakage='not excluded by identity/hash checks; independent data stewardship review remains pending'))
    selected = []
    seen = set()
    for r in candidates:
        if r['author'] not in seen:
            selected.append(r)
            seen.add(r['author'])
    assert {r['ID'] for r in selected} == set(EDITS)
    metrics = frozen_style_metrics()
    generated, measured, ledger, intake = [], [], [], []
    for r in selected:
        a = r['Original']
        edit = EDITS[r['ID']]
        if edit:
            old, new = edit
            assert a.count(old) == 1
            minimal = a.replace(old, new)
        else:
            old, new, minimal = '', '', a
        assert anchors(a) == anchors(minimal)
        ledger.append(dict(ID=r['ID'], old=old, new=new, rationale='Context-specific near synonym; AI judgment pending independent review' if edit else 'Retain quotes and loaded imagery; no safe edit selected', reviewer_type='ai', human_validated=False))
        for method, text in [('Original', a), ('Paraphrase', r['Paraphrase']), ('Style', r['Style']), ('Minimal', minimal)]:
            generated.append(dict(row_id=r['ID'], condition=method, original=a, rewrite=text, truncated=False,
                                  truncation_metadata_available=False, human_verified=False))
            measured.append(dict(ID=r['ID'], method=method, protected_sequence_equal=anchors(a) == anchors(text), **metrics(a, text)))
            if method != 'Original':
                intake.append(dict(review_id=f'R{len(intake)+1:03}', Original=a, Rewrite=text,
                                   meaning='', quantifier_scope='', certainty='', negation='', actors_attribution='',
                                   narrative_stance='', style_change='', acceptable='', notes='', reviewer_type='', reviewer_id='', review_date=''))
    random.Random(20261117).shuffle(intake)
    save(HERE / 'PILOT_METRICS.csv', measured)
    save(HERE / 'EDIT_LEDGER.csv', ledger)
    save(HERE / 'HUMAN_REVIEW_BLIND.csv', intake)
    keys = [dict(review_id=f'R{i+1:03}', ID=r['row_id'], method=r['condition'], rewrite_sha256=text_sha(r['rewrite'])) for i, r in enumerate(g for g in generated if g['condition'] != 'Original')]
    save(HERE / 'HUMAN_REVIEW_KEY.csv', keys)
    save(HERE / 'analysis_cohort.csv', [dict(row_id=r['ID'], author=r['author'], narrative_name=r['label'], split='train') for r in selected])
    (HERE / 'generated_rewrites.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in generated), encoding='utf-8')
    summary = {}
    for method in ('Original', 'Paraphrase', 'Style', 'Minimal'):
        rows = [r for r in measured if r['method'] == method]
        summary[method] = dict(n=len(rows), edit_fraction_mean=statistics.mean(r['word_edit_fraction'] for r in rows),
             exact_copies=sum(r['exact_copy'] for r in rows), substantial_style_changes=sum(r['substantial_style_change'] for r in rows),
             protected_sequence_equal=sum(r['protected_sequence_equal'] for r in rows),
             sentence_relative_change_mean=statistics.mean(r['sentence_mean_relative_change'] for r in rows),
             punctuation_l1_mean=statistics.mean(r['punctuation_l1_per100'] for r in rows))
    dump(HERE / 'PILOT_SUMMARY.json', summary)
    dump(HERE / 'DRAFT_CONFIG.json', dict(version='minimal_meaning_v1_20261117', status='preparation_only_not_training_ready',
         arms=dict(A=['Original'], B=['Paraphrase'], C=['Style'], D=['Original', 'Style'], E=['Original', 'Paraphrase'], F=['Minimal'], G=['Original', 'Minimal']),
         n_sources_target=200, batch_size=16, optimizer_updates=260, processed_examples=4160,
         budget_rule='20 * ceil(200/16); equal full batches across all seven arms; not epoch-equality',
         old_updates=140, old_examples=2240, seeds=[7, 42, 123, 2026, 31415],
         validation='unchanged43 Originals; fixed final checkpoint; no rewrite selection', test='disabled',
         required_before_training=['human binary labels and adjudication', 'all three rewrites per200', 'human QC600 pairs',
                                  'common symmetric fallback across three rewrites', 'signed new freeze', 'new versioned trainer adapter and safety tests'],
         generator=dict(identity='Codex assistant in this conversation', exact_revision=None, temperature=None,
                        provenance='eight context-specific literal substitutions plus one unchanged source; no external generation API', main_generation_not_started=True)))
    assert all(sha(ROOT / p) == digest for p, digest in hashes.items())
    dump(HERE / 'MANIFEST.json', dict(source_sha256=hashes, no_training=True, no_test_evaluation=True,
         pilot_selection='first record per author in existing105 order; nine authors; convenience pilot not representative',
         output_sha256={p.name: sha(p) for p in HERE.iterdir() if p.is_file() and p.name != 'MANIFEST.json'}))


if __name__ == '__main__':
    main()

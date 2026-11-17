"""Versioned TRAIN-only follow-up. Never train, relabel or edit historical inputs."""
import importlib.util
import json
from pathlib import Path
import random
import re
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / 'minimal_meaning_v1_20261117'
spec = importlib.util.spec_from_file_location('minimal_previous_prepare', PREVIOUS / 'prepare.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
read, save, dump, sha, text_sha = previous.read, previous.save, previous.dump, previous.sha, previous.text_sha

# All spans reviewed in context before scoring; no automatic synonym dictionary.
LEXICAL = {
 'creators:222877': [('along with', 'alongside'), ('good things to come', 'good things ahead')],
 'creators:421269': [('by attempting to kill', 'by trying to kill'), ('rather than always depending on politicians', 'instead of always relying on politicians')],
 'creators:122279': [('take our attention off something', 'divert our attention from something'), ('put it on something', 'direct it toward something'), ('he who resides at', 'he who lives at')],
 'creators:421241': [('keeps calling himself', 'keeps describing himself as'), ('to win over even Democrats', 'to persuade even Democrats'), ('he would do as they say', 'he would do as they tell him')],
 'creators:423633': [('That was just a prelude', 'That was merely a prelude'), ('shut the building', 'closed the building')],
 'creators:2644c7547b3b': [('to reflect on the historical significance', 'to consider the historical significance'), ('in this role, in this time', 'in this role, at this time')],
 'creators:417181': [('secretly paid informants', 'covertly paid informants'), ('fictitious entities', 'fictitious organizations'), ('to hide funding from their donors', 'to conceal funding from their donors')],
 'creators:417610': [('would scheme to seize', 'would plot to seize'), ('in pursuit of a distorted sense of justice', 'in pursuit of a distorted notion of justice'), ("the people who hold such ideas", "the people who hold these ideas")],
 'creators:418904': [],
}
SYNTAX = {
 'creators:222877': [('The Trump administration and the Republicans in Congress have passed one of the best pro-growth tax bills ever.', 'One of the best pro-growth tax bills ever has been passed by the Trump administration and the Republicans in Congress.')],
 'creators:421269': [],  # Moving the initiative adjunct risks changing causal emphasis.
 'creators:122279': [],  # Retain rhetorical rhythm and chief-among-those-masters emphasis.
 'creators:421241': [],  # Leave attribution and once-elected scope in place.
 'creators:423633': [],  # Preserve the narrative victim/killer progression.
 'creators:2644c7547b3b': [],
 'creators:417181': [('The organization covertly paid informants to engage in the active promotion and funding of racist groups while denouncing and "fighting" the very same groups in public.', 'The organization covertly paid informants to engage in the active promotion and funding of racist groups while, in public, denouncing and "fighting" the very same groups.')],
 'creators:417610': [],
 'creators:418904': [('The Confederates surrendered, as was their habit.', 'As was their habit, the Confederates surrendered.')],
}


def extra_blind():
    rows = [r for r in read(PREVIOUS / 'TRAIN_POOL_202.csv') if r['existing105'] == 'False']
    random.Random(20261118).shuffle(rows)
    return [(f'L{i+1:03}', row) for i, row in enumerate(rows)]


def literal_edits(text, edits):
    for before, after in edits:
        if text.count(before) != 1:
            raise ValueError('Edit span is not unique: ' + before)
        text = text.replace(before, after, 1)
    return text


def quotations(text):
    return re.findall(r'"[^"\n]*"|“[^”\n]*”', text)


def numbers(text):
    return re.findall(r'\b\d+(?:[.,]\d+)*\b', text)


def main():
    if (HERE / 'MANIFEST.json').exists():
        raise ValueError('Immutable follow-up exists; create a new version')
    bindings = [p for p in PREVIOUS.iterdir() if p.is_file() and p.name != 'nli_progress.json']
    bindings += [ROOT / 'MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md', HERE / 'prepare.py',
                 HERE / 'PROMPT_V2.txt', HERE / 'PROMPT_V3.txt', HERE / 'DESIGN_HE.md',
                 previous.STUDY, ROOT / 'artifacts/experiments/verified_human_style_followup_20261026/author_splits.csv']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in bindings}
    originals = [json.loads(line) for line in (PREVIOUS / 'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(originals) == 36
    cohort = read(PREVIOUS / 'analysis_cohort.csv')
    assert len(cohort) == 9 and all(r['split'] == 'train' for r in cohort)
    original_by_id = {r['row_id']: r for r in originals if r['condition'] == 'Original'}
    assert set(original_by_id) == set(LEXICAL) == set(SYNTAX)
    variants, ledger = [], []
    for rid, row in original_by_id.items():
        a = row['original']
        v2 = literal_edits(a, LEXICAL[rid])
        v3 = literal_edits(v2, SYNTAX[rid])
        for method, text, edits in [('Minimal_v2', v2, LEXICAL[rid]), ('Minimal_v3', v3, LEXICAL[rid] + SYNTAX[rid])]:
            assert previous.anchors(a) == previous.anchors(text), rid
            assert numbers(a) == numbers(text) and quotations(a) == quotations(text), rid
            variants.append(dict(row_id=rid, condition=method, original=a, rewrite=text, truncated=False,
                                 truncation_metadata_available=False, human_verified=False))
            if not edits:
                ledger.append(dict(ID=rid, method=method, before='', after='', decision='retain original: no safe lexical edit selected', reviewer_type='ai'))
            for before, after in edits:
                ledger.append(dict(ID=rid, method=method, before=before, after=after,
                                   decision='contextual candidate; equivalence and rhetorical force require independent human review', reviewer_type='ai'))
    # Freeze candidates before metrics; one candidate/version/source, including copies.
    all_variants = [dict(r, condition='Minimal_v1' if r['condition'] == 'Minimal' else r['condition']) for r in originals] + variants
    save(HERE / 'analysis_cohort.csv', cohort)
    (HERE / 'generated_rewrites.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in all_variants), encoding='utf-8')
    save(HERE / 'EDIT_LEDGER.csv', ledger)
    metrics_fn = previous.frozen_style_metrics()
    metrics = [dict(ID=r['row_id'], method=r['condition'], protected_sequence_equal=previous.anchors(r['original']) == previous.anchors(r['rewrite']),
                    **metrics_fn(r['original'], r['rewrite'])) for r in all_variants]
    save(HERE / 'PILOT_METRICS.csv', metrics)
    summary = {}
    for method in sorted({r['method'] for r in metrics}):
        rs = [r for r in metrics if r['method'] == method]
        summary[method] = dict(n=len(rs), edit_fraction_mean=statistics.mean(r['word_edit_fraction'] for r in rs),
                              substantial_style_changes=sum(r['substantial_style_change'] for r in rs), exact_copies=sum(r['exact_copy'] for r in rs),
                              sentence_relative_change_mean=statistics.mean(r['sentence_mean_relative_change'] for r in rs),
                              punctuation_l1_mean=statistics.mean(r['punctuation_l1_per100'] for r in rs))
    dump(HERE / 'PILOT_SUMMARY.json', summary)
    pairs = [r for r in all_variants if r['condition'] != 'Original']
    random.Random(20261119).shuffle(pairs)
    review, key = [], []
    for i, row in enumerate(pairs):
        rid = f'P{i+1:03}'
        review.append(dict(review_id=rid, Original=row['original'], Rewrite=row['rewrite'], meaning='', quantifier_negation_scope='', certainty='',
                           attribution_roles='', rhetoric_framing='', entities_numbers_quotes='', style_change='', acceptable='', notes='', reviewer_type='', reviewer_id='', review_date=''))
        key.append(dict(review_id=rid, ID=row['row_id'], method=row['condition'], rewrite_sha256=text_sha(row['rewrite'])))
    save(HERE / 'PILOT_HUMAN_BLIND.csv', review)
    save(HERE / 'PILOT_HUMAN_KEY.csv', key)
    label_forms, label_key = [], []
    for blind, row in extra_blind():
        assert row['split'] == 'train' and text_sha(row['Original']) == row['source_sha256']
        label_forms.append(dict(review_id=blind, Original=row['Original'], label='', evidence_span='', reason='',
                                confidence='', reviewer_type='', reviewer_id='', review_date='', assistance_used=''))
        label_key.append(dict(review_id=blind, ID=row['ID'], author=row['author'], source_sha256=row['source_sha256'],
                              source_url=row['source_url'], original_label_a=row['source_label_a'], original_label_b=row['source_label_b'],
                              old_provisional200=row['provisional200']))
    save(HERE / 'LABEL_97_BLIND.csv', label_forms)
    save(HERE / 'LABEL_97_PRIVATE_KEY.csv', label_key)
    for start in range(0, 97, 20):
        pages = ['# תיוג עצמאי — Original בלבד', '', 'Left / Right / Unclear. יש לקרוא את LABEL_GUIDE_HE.md. אין להיעזר בזהות כותב או בהצעות AI.', '']
        for r in label_forms[start:start+20]:
            pages += [f"## {r['review_id']}", '', r['Original'], '', '| שדה | תשובה |', '|---|---|',
                      '| Left / Right / Unclear | |', '| ראיה מדויקת | |', '| נימוק / סיבת Unclear | |', '| סוקר / תאריך / סיוע | |', '']
        (HERE / f'LABEL_BOOKLET_{start//20+1:02}.md').write_text('\n'.join(pages), encoding='utf-8')
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    dump(HERE / 'MANIFEST.json', dict(version='minimal_followup_20261117', source_sha256=hashes,
         output_sha256={p.name: sha(p) for p in HERE.iterdir() if p.is_file() and p.name != 'MANIFEST.json'},
         generator='Codex contextual edits in current conversation, exact revision and sampling parameters unavailable',
         candidate_policy='one candidate/version/source; fixed before metrics; all retained; no post-score retry',
         no_training=True, no_test_evaluation=True, frozen_protocol_and_budgets_unchanged=True,
         label_review='AI text-only developmental screen, not independent human labels; author and old label not supplied to decision table'))


if __name__ == '__main__':
    main()

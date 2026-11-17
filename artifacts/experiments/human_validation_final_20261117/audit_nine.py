"""Deep audit of nine blocked historical sources. Never restores or changes splits."""
import importlib.util
import sys

from bundle import HERE, ROOT, COLLECTION, read, save, dump, sha, verify_collection

FOLLOW = COLLECTION.parent / 'verified_human_style_followup_20261026'

EXTERNAL_CREDIT = {
 'creators:222877': ('Larry Kudlow; Arthur B. Laffer; Stephen Moore', 'Stephen Moore belongs to frozen Test',
                    'https://www.nationalreview.com/author/larry-kudlow/', 'publisher author index credits the King Dollar article jointly; local footer also names Kudlow/Moore'),
 'creators:223861': ('Larry Kudlow; Arthur B. Laffer; Stephen Moore', 'Stephen Moore belongs to frozen Test',
                    'https://www.nationalreview.com/author/larry-kudlow/', 'publisher author index credits Tariffs Are Taxes jointly; local footer also names Kudlow/Moore'),
 'creators:218236': ('Lawrence Kudlow; Stephen Moore', 'Stephen Moore belongs to frozen Test',
                    'https://www.rasmussenreports.com/public_content/political_commentary/commentary_by_lawrence_kudlow/republicans_tax_plan_takes_a_quirky_swipe_at_the_little_guys', 'syndicated publication explicitly gives two-author commentary credit; local footer gives both biographies'),
 'creators:209914': ('Lawrence Kudlow; James Carter', 'James Carter is not assigned to any frozen author split',
                    'https://www.realclearpolitics.com/articles/2017/08/12/index_capital_gains_for_inflation_mr_president_134734.html', 'syndicated article credits Kudlow and James Carter; local Carter biography agrees. co-authored with Brian Domitrovic refers to a BOOK, not this article'),
}


def main():
    if (HERE / 'HISTORICAL_NINE_AUDIT.csv').exists():
        raise ValueError('Keep prior source audit; use a new version')
    verify_collection()
    sys.path.insert(0, str(COLLECTION))
    spec = importlib.util.spec_from_file_location('nine_collection_prepare', COLLECTION / 'prepare.py')
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    pool = read(COLLECTION.parent / 'minimal_meaning_v1_20261117/TRAIN_POOL_202.csv')
    old = {r['source_url']: r for r in pool if r['existing105'] == 'True'}
    collected = {r['row_id']: r for r in read(FOLLOW / 'collected_texts.csv')}
    inventory = {r['source_url']: r for r in read(COLLECTION / 'SOURCE_INVENTORY.csv')}
    splits = {r['author']: r['split'] for r in read(FOLLOW / 'author_splits.csv')}
    rows, bindings = [], {}
    for evidence in read(COLLECTION / 'HOLDOUT_DUPLICATE_EVIDENCE.csv'):
        if evidence['original105'] != 'True':
            continue
        source = inventory[evidence['train_source_url']]
        parent = collected[evidence['protected_source_ID']]
        train_path = ROOT / source['snapshot']
        protected_path = FOLLOW / 'sources' / parent['author'] / ('article_'+parent['row_id'].split(':', 1)[1]+'.html')
        _, _, ap, _ = engine.parse_body(train_path, source['byline'])
        _, _, bp, _ = engine.parse_body(protected_path, parent['author_name'])
        a = ' '.join(t for _, t in ap)
        b = ' '.join(t for _, t in bp)
        assert engine.canon(a) == engine.canon(b)
        assert splits[parent['author']] == 'test'
        for path in (train_path, protected_path):
            bindings[str(path.relative_to(ROOT))] = sha(path)
        original = old[evidence['train_source_url']]
        rows.append(dict(ID=original['ID'], title=source['title'], recorded_train_author=source['author'],
                         issue_type='exact_normalized_full_body_overlap_with_Test',
                         protected_source_ID=parent['row_id'], protected_author=parent['author'], protected_split='test',
                         body_jaccard=1.0, source_url=evidence['train_source_url'], corroborating_url=parent['source_url'],
                         credit_or_relation='Same normalized article body under Jim Hightower and Joe Conason source records; cannot infer correct sole author from conflicting pages',
                         initial_flag_refinement='Exact article-body overlap, not a mere shared topic or short quote; different HTML/excerpt hashes can miss it',
                         decision='remain quarantined; do not restore, reassign author, move splits or relabel automatically'))
    for evidence in read(COLLECTION / 'AUTHORSHIP_CREDIT_EVIDENCE.csv'):
        if evidence['original105'] != 'True':
            continue
        original = old[evidence['source_url']]
        source = inventory[evidence['source_url']]
        credit, relation, url, note = EXTERNAL_CREDIT[original['ID']]
        bindings[source['snapshot']] = sha(ROOT / source['snapshot'])
        rows.append(dict(ID=original['ID'], title=source['title'], recorded_train_author=source['author'],
                         issue_type='joint_article_credit_not_single_Train_author', protected_source_ID='',
                         protected_author='stephen-moore' if 'Stephen Moore' in credit else 'unassigned:James Carter',
                         protected_split='test' if 'Stephen Moore' in credit else 'not_assigned', body_jaccard='',
                         source_url=evidence['source_url'], corroborating_url=url,
                         credit_or_relation=credit+'; '+relation, initial_flag_refinement=note,
                         decision='remain quarantined; no automatic restoration or authorship/split changes'))
    assert len(rows) == 9 and len({r['ID'] for r in rows}) == 9
    included = {r['ID'] for r in read(COLLECTION / 'CANDIDATES.csv')}
    assert not included & {r['ID'] for r in rows}
    save(HERE / 'HISTORICAL_NINE_AUDIT.csv', rows)
    dump(HERE / 'NINE_AUDIT_BINDINGS.json', bindings)
    dump(HERE / 'NINE_AUDIT_SUMMARY.json', dict(
        sources=9, exact_Test_body_overlaps=5, exact_Validation_body_overlaps_among_these9=0,
        joint_credits_with_Test_author=3, joint_credit_with_unassigned_author=1,
        still_excluded=9, restored=0, frozen_files_changed=False,
        refinement='Book co-authorship mention is not proof of article co-authorship; the Carter article has separate explicit two-author publication evidence.',
        external_credit_sources_checked='2026-11-17; verification of existing sources only, no candidate collection'))


if __name__ == '__main__':
    main()

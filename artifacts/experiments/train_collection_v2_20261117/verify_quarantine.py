"""Record reproducible evidence for protective exclusions, without scoring a classifier."""
import collections

from collect import HERE, ROOT, FOLLOW, dump, read, save, sha
from prepare import authorship_flags, canon, parse_body, shingles, similarity


def main():
    if (HERE / 'QUARANTINE_AUDIT.json').exists():
        raise ValueError('Preserve the prior exclusion evidence')
    sources = {r['source_url']: r for r in read(HERE / 'SOURCE_INVENTORY.csv')}
    originals = {r['row_id']: r for r in read(FOLLOW / 'collected_texts.csv')}
    splits = {r['author']: r['split'] for r in read(FOLLOW / 'author_splits.csv')}
    registry = {r['author']: r['name'] for r in read(FOLLOW / 'author_registry.csv')}
    old105 = read(HERE.parent / 'main_training_preparation_20261109/TRAIN_CONDITION_ID_MAP.csv')
    old_pool = read(HERE.parent / 'minimal_meaning_v1_20261117/TRAIN_POOL_202.csv')
    old_ids = {r['ID'] for r in old105}
    old_url_ids = {r['source_url']: r['ID'] for r in old_pool}
    evidence, body_flags, protected_hashes = [], [], {}
    for flag in read(HERE / 'QUARANTINED_SOURCES.csv'):
        source = sources[flag['source_url']]
        _, raw, indexed, _ = parse_body(ROOT / source['snapshot'], registry[source['author']])
        if flag['reasons'].startswith('heldout_full_article_duplicate:'):
            protected_id = flag['reasons'].split('heldout_full_article_duplicate:', 1)[1]
            target = originals[protected_id]
            assert splits[target['author']] in ('val', 'test')
            path = FOLLOW / 'sources' / target['author'] / ('article_'+protected_id.split(':', 1)[1]+'.html')
            _, _, target_indexed, _ = parse_body(path, target['author_name'])
            a, b = ' '.join(t for _, t in indexed), ' '.join(t for _, t in target_indexed)
            j = similarity(shingles(a), shingles(b))
            assert canon(a) == canon(b) or j >= .8
            protected_hashes[str(path.relative_to(ROOT))] = sha(path)
            evidence.append(dict(train_source_url=flag['source_url'], protected_source_ID=protected_id,
                                 protected_split=splits[target['author']], exact_normalized_body=canon(a) == canon(b),
                                 full_body_jaccard=j, original105=old_url_ids.get(flag['source_url']) in old_ids,
                                 action='excluded from new review packet; historical files unchanged'))
        else:
            assert authorship_flags(raw, source['author'], registry[source['author']])
            # Credits are local source evidence; never fed to political label reviewers.
            body_flags.append(dict(source_url=flag['source_url'], recorded_author=source['author'],
                                   reasons=flag['reasons'], credit_context='\n'.join(raw[-5:]),
                                   original105=old_url_ids.get(flag['source_url']) in old_ids))
    save(HERE / 'HOLDOUT_DUPLICATE_EVIDENCE.csv', evidence)
    save(HERE / 'AUTHORSHIP_CREDIT_EVIDENCE.csv', body_flags)
    dump(HERE / 'GUARD_SNAPSHOT_BINDINGS.json', protected_hashes)
    dump(HERE / 'QUARANTINE_AUDIT.json', dict(full_article_overlap_exclusions=len(evidence),
         overlap_by_protected_split=dict(collections.Counter(r['protected_split'] for r in evidence)),
         authorship_exclusions=len(body_flags), original105_excluded=sum(r['original105'] for r in evidence+body_flags),
         previous105_files_changed=False, classifier_metrics_computed=False,
         explanation='Earlier zero exact HTML/text hash collisions did not exclude shared article bodies with differing pages/excerpts. Full-body fingerprint audit now blocks these sources in the new candidate bank.'))


if __name__ == '__main__':
    main()

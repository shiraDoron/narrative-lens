"""Blinded119-source starter batch: old105 plus14 new candidates; no gold decisions."""
import random

from inventory import HERE, V1, dump, normalized_url, read, save, text_sha


def main():
    if (HERE / 'LABEL_STARTER_119_BLIND.csv').exists():
        raise ValueError('Do not overwrite a labeling packet')
    articles = {normalized_url(r['source_url']): r for r in read(HERE / 'TRAIN_ARTICLE_INVENTORY.csv')}
    items = []
    for row in read(V1 / 'TRAIN_POOL_202.csv'):
        if row['existing105'] != 'True':
            continue
        group = articles[normalized_url(row['source_url'])]['article_group']
        items.append(dict(ID=row['ID'], article_group=group, Original=row['Original'], source_sha256=row['source_sha256'],
                          author=row['author'], split='train', source_kind='old105', prior_ai_proposal_as_recorded=row['proposed_binary_label']))
    for row in read(HERE / 'AI_CANDIDATES_14.csv'):
        items.append(dict(ID=row['candidate_id'], article_group=row['article_group'], Original=row['Original'],
                          source_sha256=row['source_sha256'], author=row['author'], split='train',
                          source_kind='new_candidate14', prior_ai_proposal_as_recorded=row['ai_proposed_label']))
    assert len(items) == len({r['article_group'] for r in items}) == 119
    random.Random(2026111704).shuffle(items)
    forms, key = [], []
    for i, row in enumerate(items):
        rid = f'U{i+1:03}'
        assert text_sha(row['Original']) == row['source_sha256']
        forms.append(dict(review_id=rid, Original=row['Original'], label='', evidence_span='', reason='', confidence='',
                          reviewer_type='', reviewer_id='', review_date='', assistance_used=''))
        key.append(dict(review_id=rid, **{k: v for k, v in row.items() if k != 'Original'}))
    save(HERE / 'LABEL_STARTER_119_BLIND.csv', forms)
    save(HERE / 'LABEL_STARTER_PRIVATE_KEY_119.csv', key)
    dump(HERE / 'LABEL_STARTER_SUMMARY.json', dict(n_sources=119, distinct_article_groups=119, human_answers_filled=0,
         includes='old105 source texts unchanged plus14 literal candidate windows',
         use='two independent human copies; no author, prior AI label or source cohort in blind form',
         source_labels_changed=False, automatic_training_acceptance=False))


if __name__ == '__main__':
    main()

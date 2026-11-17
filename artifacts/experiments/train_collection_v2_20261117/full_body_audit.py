"""Conservative within-Train full-article near-duplicate audit, no model or labels."""
import itertools

from collect import HERE, ROOT, dump, read, save
from prepare import parse_body, shingles, similarity


def main():
    if (HERE / 'FULL_BODY_AUDIT.json').exists():
        raise ValueError('Keep prior audit results')
    rows = read(HERE / 'CANDIDATES.csv')
    prepared = []
    for row in rows:
        _, _, indexed, _ = parse_body(ROOT / row['source_snapshot'], row['byline'])
        prepared.append((row, shingles(' '.join(t for _, t in indexed))))
    near = []
    for (a, sa), (b, sb) in itertools.combinations(prepared, 2):
        j = similarity(sa, sb)
        if j >= .8:
            near.append(dict(ID_a=a['ID'], ID_b=b['ID'], jaccard=j, reason='full_article_near_duplicate'))
    if near:
        save(HERE / 'FULL_BODY_DUPLICATE_FLAGS.csv', near)
    dump(HERE / 'FULL_BODY_AUDIT.json', dict(candidate_articles=len(rows), flagged_pairs=near,
         threshold=.8, labels_used=False, test_used=False,
         no_exact_or_near_train_full_bodies_at_this_threshold=not near,
         semantic_or_event_independence_proven=False))


if __name__ == '__main__':
    main()

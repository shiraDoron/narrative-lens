"""Offline Train-only source inventory; no labels, training or historical edits."""
import csv
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

from lxml import html

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLLOW = HERE.parent / 'verified_human_style_followup_20261026'
V1 = HERE.parent / 'minimal_meaning_v1_20261117'
V2 = HERE.parent / 'minimal_followup_20261117'


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def save(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def normalized_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/'), '', ''))


def words(text):
    return len(re.findall(r"\b\w+(?:['’]\w+)*\b", text))


def paragraphs(raw):
    doc = html.fromstring(raw)
    ps = [' '.join(p.text_content().split()) for p in doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," article-content ")]/p')]
    return doc, [p for p in ps if p and not re.search(r'COPYRIGHT|DISTRIBUTED BY|To find out more|To learn more about|Visit the Creators|Write to .* at|email .*@', p, re.I)]


def windows(ps):
    for start in range(len(ps)):
        for end in range(start+1, min(len(ps), start+3)+1):
            text = ' '.join(ps[start:end])
            if words(text) > 100:
                break
            if words(text) >= 35:
                yield start, end, text
                break


def main():
    if (HERE / 'INVENTORY.json').exists():
        raise ValueError('Keep prior inventory immutable; use a new version')
    sources = [FOLLOW / 'collected_texts.csv', FOLLOW / 'text_annotations.csv', FOLLOW / 'author_splits.csv',
               FOLLOW / 'author_registry.csv', V1 / 'TRAIN_POOL_202.csv', V1 / 'DRAFT_CONFIG.json',
               V2 / 'LABEL_SCREEN_SUMMARY.json', V2 / 'PILOT_SUMMARY.json',
               ROOT / 'MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md', HERE / 'inventory.py']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    assignments = read(FOLLOW / 'author_splits.csv')
    splits = {r['author']: r['split'] for r in assignments}
    assert len(splits) == len(assignments)
    names = {r['author']: r['name'] for r in read(FOLLOW / 'author_registry.csv')}
    pool = read(V1 / 'TRAIN_POOL_202.csv')
    assert len(pool) == 202 and all(splits[r['author']] == 'train' for r in pool)
    old_urls = {normalized_url(r['source_url']): r for r in pool}
    core_urls = {normalized_url(r['source_url']) for r in pool if r['existing105'] == 'True'}
    heldout_urls = {normalized_url(r['source_url']) for r in read(FOLLOW / 'text_annotations.csv') if splits[r['author']] != 'train'}
    collected = [r for r in read(FOLLOW / 'collected_texts.csv') if splits[r['author']] == 'train']
    inventory, bank, failures = [], [], []
    seen = set()
    for row in sorted(collected, key=lambda r: (r['author'], r['source_url'], r['row_id'])):
        url = normalized_url(row['source_url'])
        if url in seen:
            continue
        seen.add(url)
        assert url not in heldout_urls
        slug = row['author']
        snapshot = FOLLOW / 'sources' / slug / ('article_'+row['row_id'].split(':', 1)[1]+'.html')
        if not snapshot.exists():
            failures.append(dict(ID=row['row_id'], reason='snapshot missing'))
            continue
        hashes[str(snapshot.relative_to(ROOT))] = sha(snapshot)
        doc, ps = paragraphs(snapshot.read_text(encoding='utf-8'))
        byline = [s.strip() for s in doc.xpath('//*[@itemprop="creator"]//a/text()')]
        if byline != [names[slug]]:
            failures.append(dict(ID=row['row_id'], reason='byline mismatch'))
            continue
        article_group = 'article:'+text_sha(url)[:16]
        old = old_urls.get(url)
        role = 'existing105_do_not_replace' if url in core_urls else 'alternate_excerpt_of_unclear_article' if old else 'unrepresented_cached_article'
        body_hash = text_sha('\n'.join(ps))
        inventory.append(dict(article_group=article_group, author=slug, split='train', source_url=url,
                              source_date=row['source_date'], title=row['title'], source_snapshot=str(snapshot.relative_to(ROOT)),
                              article_snapshot_sha256=sha(snapshot), body_sha256=body_hash, role=role,
                              old_ID=old['ID'] if old else '', byline_verified=True, paragraph_count=len(ps)))
        if role == 'existing105_do_not_replace':
            continue
        for start, end, text in windows(ps):
            if any(text == r['Original'] for r in pool):
                continue
            wid = article_group+f':p{start}-{end}'
            bank.append(dict(candidate_id=wid, article_group=article_group, Original=text, word_count=words(text),
                             paragraph_start=start, paragraph_end_exclusive=end, source_sha256=text_sha(text),
                             author=slug, split='train', source_url=url, source_date=row['source_date'],
                             source_snapshot=str(snapshot.relative_to(ROOT)), role=role, old_ID=old['ID'] if old else '',
                             human_label='', training_ready=False))
    save(HERE / 'TRAIN_ARTICLE_INVENTORY.csv', inventory)
    save(HERE / 'LOCAL_WINDOW_BANK.csv', bank)
    # Archive metadata/full bodies can identify collection targets; publisher categories are never exported as labels.
    targets = {}
    archive_urls = set()
    for author in sorted(a for a, split in splits.items() if split == 'train'):
        for archive in sorted((FOLLOW / 'sources' / author).glob('page*.json')):
            hashes[str(archive.relative_to(ROOT))] = sha(archive)
            for release in json.loads(archive.read_text(encoding='utf-8'))['releases']:
                url = normalized_url(release['formatted_url'])
                assert url not in heldout_urls
                archive_urls.add(url)
                if url not in seen:
                    targets[url] = dict(author=author, split='train', source_url=url, title=release['title'],
                                        source_date=release['release_date'][:10], archive=str(archive.relative_to(ROOT)),
                                        article_byline_verified=False, label='', status='requires retrieval_and_text_review')
    if targets:
        save(HERE / 'UNRETRIEVED_ARCHIVE_TARGETS.csv', list(targets.values()))
    raw_inventory = []
    for path in sorted((ROOT / 'data/raw').glob('*.csv')):
        rows = read(path)
        fields = list(rows[0])
        raw_inventory.append(dict(path=str(path.relative_to(ROOT)), n=len(rows), columns=fields,
                                  known_named_single_author_field='author' in fields,
                                  eligibility='not automatically eligible: synthetic or social/account-level origin; cannot identify the same nine named Train writers from supplied schema alone'))
    roles = {role: sum(r['role'] == role for r in inventory) for role in sorted({r['role'] for r in inventory})}
    per_author = []
    for author in sorted(a for a, split in splits.items() if split == 'train'):
        per_author.append(dict(author=author, split='train', existing105=sum(r['author'] == author and r['existing105'] == 'True' for r in pool),
                               existing_unclear_articles=sum(r['author'] == author and r['role'] == 'alternate_excerpt_of_unclear_article' for r in inventory),
                               recovered_articles=sum(r['author'] == author and r['role'] == 'unrepresented_cached_article' for r in inventory),
                               feature_url='https://www.creators.com/features/'+author,
                               bio_url='https://www.creators.com/author/'+author,
                               collection_batch1_target=5, collection_additional_target=15,
                               label_inferred_from_author=False))
    save(HERE / 'TRAIN_COLLECTION_TARGETS.csv', per_author)
    dump(HERE / 'INVENTORY.json', dict(raw_train_rows=len(collected), unique_train_article_urls=len(inventory),
         existing_pool202_unique_urls=len(old_urls), existing105_unique_urls=len(core_urls), roles=roles,
         candidate_windows=len(bank), candidate_article_groups=len({r['article_group'] for r in bank}),
         archive_urls_seen=len(archive_urls), unretrieved_archive_urls=len(targets), errors=failures,
         raw_other_corpora=raw_inventory, heldout_usage='author/source URL metadata isolation only; no held-out text metrics, labels or predictions',
         limitation='URL grouping plus TRAIN full-body hashes; syndication/semantic/event overlap and all human labels remain pending',
         one_excerpt_per_article_required=True, no_source_labels_changed=True, no_training=True))
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    dump(HERE / 'SOURCE_BINDINGS.json', hashes)


if __name__ == '__main__':
    main()

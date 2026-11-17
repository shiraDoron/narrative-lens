"""Public-source collection from frozen Train authors only. No classification/training."""
import argparse
import concurrent.futures
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import threading
import time
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

import requests
from lxml import html

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLLOW = HERE.parent / 'verified_human_style_followup_20261026'
SOURCES = HERE / 'raw_sources'
LOCK = threading.Lock()
STOP_HOST = set()


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def save(path, rows):
    if not rows:
        return
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def canonical_url(url):
    p = urlsplit(url)
    host = p.netloc.lower().removeprefix('www.')
    return urlunsplit(('https', host, p.path.rstrip('/'), '', ''))


def alias_key(url):
    return re.sub(r'-[0-9a-f]{5,8}$', '', canonical_url(url))


def train_authors():
    return sorted(r['author'] for r in read(FOLLOW / 'author_splits.csv') if r['split'] == 'train')


def record(event):
    with LOCK:
        with (HERE / 'FETCH_LOG.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, ensure_ascii=False)+'\n')


def fetch(url, path):
    if path.exists():
        return path.read_text(encoding='utf-8')
    host = urlsplit(url).netloc
    if host in STOP_HOST:
        raise ValueError('Host temporarily stopped after rate limit')
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    time.sleep(.15)
    response = requests.get(url, timeout=25, headers={'User-Agent': 'Mozilla/5.0 (compatible; academic corpus preparation)'})
    record(dict(request_url=url, response_url=response.url, status=response.status_code, retrieved_at_utc=started,
                bytes=len(response.content), destination=str(path.relative_to(HERE))))
    if response.status_code == 429:
        STOP_HOST.add(host)
    response.raise_for_status()
    response.encoding = 'utf-8'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(response.text, encoding='utf-8')
    return response.text


def discover_author(author):
    out = SOURCES / author
    feature_url = 'https://www.creators.com/features/'+author
    raw = fetch(feature_url, out / 'feature.html')
    doc = html.fromstring(raw)
    ids = doc.xpath('//a[@data-feature-id]/@data-feature-id')
    urls = [urljoin(feature_url, u) for u in doc.xpath('//a[contains(@href,"/read/")]/@href')]
    result = [dict(author=author, url=u, discovery='current_public_feature') for u in urls if '/read/'+author+'/' in u]
    if not ids:
        return result
    # Only pages1–5 already known to be public. Never request/bypass previously blocked page6.
    for page in range(1, 6):
        url = 'https://www.creators.com/api/features/releases/'+ids[0]+'/'+str(page)
        try:
            data = json.loads(fetch(url, out / f'page{page}.json'))
            result.extend(dict(author=author, url=r['formatted_url'], discovery=f'public_archive_page{page}') for r in data['releases'])
        except (requests.RequestException, ValueError, KeyError) as exc:
            record(dict(stage='discovery', author=author, url=url, error=str(exc)))
            break
    return result


def discover():
    HERE.mkdir(exist_ok=True)
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(discover_author, a): a for a in train_authors()}
        for future in concurrent.futures.as_completed(futures):
            author = futures[future]
            try:
                found = future.result()
                rows.extend(found)
                print(author, 'discovered', len(found), flush=True)
            except (requests.RequestException, ValueError) as exc:
                record(dict(stage='discovery', author=author, error=str(exc)))
                print(author, str(exc), flush=True)
    save(HERE / 'DISCOVERED_PUBLIC_URLS.csv', rows)


def discover_search_author(author):
    registry = {r['author']: r['name'] for r in read(FOLLOW / 'author_registry.csv')}
    first = 'https://www.creators.com/search?q='+quote(registry[author])
    queue, visited, results = [first], set(), []
    while queue and len(visited) < 4:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        path = SOURCES / author / ('search_'+text_sha(url)[:16]+'.html')
        try:
            doc = html.fromstring(fetch(url, path))
        except (requests.RequestException, ValueError) as exc:
            record(dict(stage='public_search', author=author, url=url, error=str(exc)))
            break
        links = [urljoin(url, u) for u in doc.xpath('//a/@href')]
        results.extend(dict(author=author, url=u, discovery='public_publisher_search:'+url) for u in links if '/read/'+author+'/' in u)
        # Follow visible HTML pagination only, never hidden/authenticated archive endpoints.
        queue.extend(u for u in links if '/search?' in u and re.search(r'[?&]p=\d+', u) and u not in visited)
    print(author, 'public search URLs', len(results), 'pages', len(visited), flush=True)
    return results


def discover_search():
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for found in pool.map(discover_search_author, train_authors()):
            rows.extend(found)
    save(HERE / 'SEARCH_SEEDS.csv', rows)


def discover_author_tags(author):
    registry = {r['author']: r['name'] for r in read(FOLLOW / 'author_registry.csv')}
    first = 'https://www.creators.com/search?tag='+quote(registry[author].lower())
    queue, visited, results = [first], set(), []
    while queue and len(visited) < 4:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        path = SOURCES / author / ('tagsearch_'+text_sha(url)[:16]+'.html')
        try:
            doc = html.fromstring(fetch(url, path))
        except (requests.RequestException, ValueError) as exc:
            record(dict(stage='public_author_tag', author=author, url=url, error=str(exc)))
            break
        links = [urljoin(url, u) for u in doc.xpath('//a/@href')]
        results.extend(dict(author=author, url=u, discovery='public_author_tag:'+url) for u in links if '/read/'+author+'/' in u)
        queue.extend(u for u in links if '/search?' in u and re.search(r'[?&]p=\d+', u) and u not in visited)
    print(author, 'tag URLs', len(results), 'pages', len(visited), flush=True)
    return results


def discover_tags():
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for found in pool.map(discover_author_tags, train_authors()):
            rows.extend(found)
    save(HERE / 'AUTHOR_TAG_SEEDS.csv', rows)


def get_article(row):
    author, url = row['author'], row['url']
    assert author in train_authors()
    path = SOURCES / author / ('article_'+text_sha(canonical_url(url))[:20]+'.html')
    try:
        raw = fetch(url, path)
        doc = html.fromstring(raw)
        bylines = [v.strip() for v in doc.xpath('//*[@itemprop="creator"]//a/text()')]
        registry = {r['author']: r['name'] for r in read(FOLLOW / 'author_registry.csv')}
        author_links = doc.xpath('//*[@itemprop="creator"]//a/@href')
        canon = doc.xpath('//link[@rel="canonical"]/@href')
        date = doc.xpath('//*[@data-default-date]/@data-default-date')
        title = ' '.join(doc.xpath('//h1/text()')).strip()
        ps = [' '.join(p.text_content().split()) for p in doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," article-content ")]/p')]
        destination = str(path.relative_to(HERE))
        events = [json.loads(line) for line in (HERE / 'FETCH_LOG.jsonl').read_text(encoding='utf-8').splitlines()]
        received = next((event['retrieved_at_utc'] for event in events if event.get('destination') == destination and event.get('status') == 200), None)
        result = dict(author=author, split='train', source_url=canonical_url(canon[0] if canon else url), request_url=url,
                      title=title, source_date=date[0] if date else '', byline='|'.join(bylines),
                      byline_verified=bylines == [registry[author]] and any('/author/'+author in u for u in author_links),
                      bio_url='https://www.creators.com/author/'+author,
                      snapshot=str(path.relative_to(ROOT)), snapshot_sha256=sha(path),
                      raw_body_sha256=text_sha('\n'.join(ps)), paragraph_count=len(ps),
                      discovery=row['discovery'], retrieved_at_utc=received,
                      parsed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      status='retrieved_pending_QA')
        if not result['byline_verified'] or not ps:
            result['status'] = 'reject_byline_or_body'
        return result
    except (requests.RequestException, ValueError) as exc:
        record(dict(stage='article', author=author, url=url, error=str(exc)))
        return None


def collect():
    discovered = read(HERE / 'DISCOVERED_PUBLIC_URLS.csv')
    for name in ('SEARCH_SEEDS.csv', 'AUTHOR_TAG_SEEDS.csv', 'WEB_SEARCH_SEEDS.csv'):
        seeds = HERE / name
        if seeds.exists():
            discovered += read(seeds)
    old = read(HERE.parent / 'data_expansion_plan_20261117/TRAIN_ARTICLE_INVENTORY.csv')
    old_keys = {alias_key(r['source_url']) for r in old}
    seen, selected, author_counts = set(), [], {}
    for row in discovered:
        key = alias_key(row['url'])
        if row['author'] not in train_authors() or '/read/'+row['author']+'/' not in row['url']:
            continue
        if key in old_keys or key in seen:
            continue
        if author_counts.get(row['author'], 0) >= 30:
            continue
        seen.add(key)
        selected.append(row)
        author_counts[row['author']] = author_counts.get(row['author'], 0)+1
    save(HERE / 'NEW_URL_QUEUE.csv', selected)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(get_article, selected):
            if result:
                results.append(result)
                print(result['author'], len(results), result['status'], flush=True)
    save(HERE / 'NEW_ARTICLE_RECEIPTS.csv', results)
    print('novel URL queue', len(selected), 'retrieved', len(results), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['discover', 'search', 'tags', 'collect'])
    args = parser.parse_args()
    if args.stage == 'discover':
        discover()
    elif args.stage == 'search':
        discover_search()
    elif args.stage == 'tags':
        discover_tags()
    else:
        collect()

"""Build a deduplicated Train candidate bank and independent human packets."""
import collections
import datetime
import itertools
import random
import re

from lxml import html

from collect import HERE, ROOT, FOLLOW, alias_key, dump, read, save, sha, text_sha

POLICY = re.compile(r'\b(?:government|congress|president|politic\w*|democra\w*|republican\w*|conservative\w*|liberal\w*|progressive\w*|socialis\w*|capitalis\w*|tax\w*|regulat\w*|immigra\w*|border\w*|abortion|racis\w*|equality|inequality|welfare|labor|workers|union\w*|vot\w*|elect\w*|constitution\w*|supreme court|climate|subsid\w*|military|public policy|health care|medicare|social security)\b', re.I)
NORM = re.compile(r'\b(?:should|must|ought|rights|freedom|liberty|unfair|fairness|justice|equal\w*|discriminat\w*|oppres\w*|tyrann\w*|racis\w*|sexist|repress\w*|corrupt\w*|greed|democracy|socialis\w*|capitalis\w*)\b', re.I)
EVAL = re.compile(r'\b(?:wrong|right|danger\w*|fail\w*|cruel|harm\w*|destroy\w*|protect\w*|oppose\w*|support\w*|against|catastroph\w*|disaster|shame\w*|outrage\w*|rig\w*|abuse\w*|rob\w*|exploit\w*)\b', re.I)
BOILER = re.compile(r'^(?:COPYRIGHT|DISTRIBUTED BY|Photo credit:|To find out more|To learn more|Visit the Creators|Write to |Every Tuesday at|Follow .{0,60} on )', re.I)


def canon(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))


def shingles(text):
    ws = canon(text).split()
    return {tuple(ws[i:i+5]) for i in range(max(0, len(ws)-4))}


def similarity(a, b):
    return len(a & b)/max(1, len(a | b))


def parse_body(path, expected_name):
    doc = html.fromstring(path.read_text(encoding='utf-8'))
    raw = [' '.join(p.text_content().split()) for p in doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," article-content ")]/p')]
    names = [s.strip() for s in doc.xpath('//*[@itemprop="creator"]//a/text()')]
    # Preserve actual paragraph offsets in raw body; never truncate or rewrite paragraphs.
    indexed = []
    for i, text in enumerate(raw):
        is_bio = i >= len(raw)-5 and (expected_name in text or 'Stossel' in text or 'Margenau' in text) and re.search(r'\bis (?:a|an|the)\b|posts a new video|syndicated|author of', text, re.I)
        if not text or BOILER.search(text) or is_bio:
            continue
        if text.isupper() and len(text.split()) <= 15:
            continue
        indexed.append((i, text))
    return doc, raw, indexed, names


def authorship_flags(raw, author, expected):
    flags = []
    tail = '\n'.join(raw[-5:])
    for foreign in ('John Stossel', 'Tom Margenau'):
        surname = foreign.split()[-1]
        if surname.lower() not in author and re.search(r'\b'+surname+r'\b', tail) and re.search(r'posts a new video|is (?:a|an|the) .{0,100}(?:author|columnist|writer)|Social Security column', tail, re.I):
            flags.append('body_signature_conflict:'+foreign)
    if author == 'lawrence-kudlow' and re.search(r'(?:Lawrence Kudlow and Stephen Moore|Kudlow and Moore|Kudlow, Laffer and Moore)', tail, re.I):
        flags.append('joint_credit_with_other_writer_potential_test_author')
    if re.search(r'\b(?:co-written|coauthored|co-authored|guest column|guest columnist)\b', tail, re.I):
        flags.append('possible_joint_or_guest_credit')
    return flags


def score(text):
    policy = len(set(s.casefold() for s in POLICY.findall(text)))
    normative = len(set(s.casefold() for s in NORM.findall(text)))
    evaluative = len(set(s.casefold() for s in EVAL.findall(text)))
    return dict(policy_hits=policy, normative_hits=normative, evaluative_hits=evaluative,
                triage_score=2*policy+3*normative+min(evaluative, 3),
                priority_political_review=policy >= 2 and (normative >= 1 or evaluative >= 2))


def windows(indexed):
    for pos, (start, _) in enumerate(indexed):
        for length in range(1, 4):
            entries = indexed[pos:pos+length]
            if len(entries) != length or any(j != start+i for i, (j, _) in enumerate(entries)):
                break
            text = ' '.join(t for _, t in entries)
            n = len(re.findall(r"\b\w+(?:['’]\w+)*\b", text))
            if n > 100:
                break
            if 35 <= n <= 100 and re.search(r'[.!?]["”’\']?$', text):
                yield dict(Original=text, paragraph_start=start, paragraph_end_exclusive=entries[-1][0]+1,
                           word_count=n, **score(text))


def heldout_guard():
    """Mechanical data hygiene only; never model evaluation or candidate ranking."""
    splits = {r['author']: r['split'] for r in read(FOLLOW / 'author_splits.csv')}
    metadata = [r for r in read(FOLLOW / 'text_annotations.csv') if splits[r['author']] != 'train']
    protected_urls = {alias_key(r['source_url']) for r in metadata}
    protected_hashes = {r['text_sha256'] for r in metadata}
    # These frozen texts are used ONLY for deterministic duplicate exclusion.
    protected_excerpt_shingles = [(r['row_id'], shingles(r['text'])) for r in metadata]
    protected_bodies = []
    seen = set()
    for r in read(FOLLOW / 'collected_texts.csv'):
        if splits[r['author']] == 'train' or alias_key(r['source_url']) in seen:
            continue
        seen.add(alias_key(r['source_url']))
        path = FOLLOW / 'sources' / r['author'] / ('article_'+r['row_id'].split(':', 1)[1]+'.html')
        if not path.exists():
            raise ValueError('Missing protected-source snapshot for duplicate safeguard')
        _, _, indexed, _ = parse_body(path, r['author_name'])
        body = ' '.join(t for _, t in indexed)
        protected_bodies.append((r['row_id'], text_sha(canon(body)), shingles(body)))
    return protected_urls, protected_hashes, protected_excerpt_shingles, protected_bodies


def build():
    if (HERE / 'MANIFEST.json').exists():
        raise ValueError('Prepared collection is immutable; create a new version')
    names = {r['author']: r['name'] for r in read(FOLLOW / 'author_registry.csv')}
    splits = {r['author']: r['split'] for r in read(FOLLOW / 'author_splits.csv')}
    old_articles = read(HERE.parent / 'data_expansion_plan_20261117/TRAIN_ARTICLE_INVENTORY.csv')
    inputs = [dict(author=r['author'], source_url=r['source_url'], source_date=r['source_date'], title=r['title'],
                   snapshot=r['source_snapshot'], snapshot_sha256=r['article_snapshot_sha256'], origin='existing_cached_article',
                   retrieved_at_utc='see original collection timestamp in SOURCE_LINEAGE') for r in old_articles]
    for r in read(HERE / 'NEW_ARTICLE_RECEIPTS.csv'):
        if r['status'] == 'retrieved_pending_QA':
            inputs.append(dict(author=r['author'], source_url=r['source_url'], source_date=r['source_date'], title=r['title'],
                               snapshot=r['snapshot'], snapshot_sha256=r['snapshot_sha256'], origin='new_public_collection', retrieved_at_utc=r['retrieved_at_utc']))
    old_pool = read(HERE.parent / 'minimal_meaning_v1_20261117/TRAIN_POOL_202.csv')
    old105 = {alias_key(r['source_url']): r for r in old_pool if r['existing105'] == 'True'}
    original_lineage = {alias_key(r['source_url']): r for r in read(FOLLOW / 'collected_texts.csv') if splits[r['author']] == 'train'}
    protected_urls, protected_hashes, protected_excerpt_shingles, protected_bodies = heldout_guard()
    source_inventory, candidates, excluded, duplicates = [], [], [], []
    body_seen, url_seen, source_hashes = {}, set(), {}
    for row in sorted(inputs, key=lambda r: (0 if alias_key(r['source_url']) in old105 else 1, r['author'], r['source_url'])):
        assert splits[row['author']] == 'train'
        key = alias_key(row['source_url'])
        if key in url_seen:
            duplicates.append(dict(source_url=row['source_url'], duplicate_of=key, reason='canonical_URL_alias'))
            continue
        url_seen.add(key)
        path = ROOT / row['snapshot']
        assert sha(path) == row['snapshot_sha256']
        source_hashes[row['snapshot']] = sha(path)
        doc, raw, indexed, bylines = parse_body(path, names[row['author']])
        flags = authorship_flags(raw, row['author'], names[row['author']])
        links = doc.xpath('//*[@itemprop="creator"]//a/@href')
        if bylines != [names[row['author']]] or not any('/author/'+row['author'] in u for u in links):
            flags.append('single_matching_byline_not_verified')
        if not row['source_date'] or row['source_date'][:10] > '2026-11-17':
            flags.append('date_missing_or_future')
        if key in protected_urls:
            flags.append('heldout_source_URL')
        body = ' '.join(t for _, t in indexed)
        body_hash = text_sha(canon(body))
        if body_hash in body_seen:
            duplicates.append(dict(source_url=row['source_url'], duplicate_of=body_seen[body_hash], reason='exact_full_body'))
            continue
        body_seen[body_hash] = row['source_url']
        body_shingles = shingles(body)
        for protected_id, phash, ps in protected_bodies:
            if body_hash == phash or similarity(body_shingles, ps) >= .8:
                flags.append('heldout_full_article_duplicate:'+protected_id)
                break
        old = old105.get(key)
        choices = list(windows(indexed))
        chosen = None
        if old:
            chosen = dict(Original=old['Original'], paragraph_start='', paragraph_end_exclusive='',
                          word_count=len(re.findall(r"\b\w+(?:['’]\w+)*\b", old['Original'])), **score(old['Original']))
            if old['Original'] not in ' '.join(raw):
                flags.append('old_original_not_traceable_in_snapshot')
        elif choices:
            chosen = max(choices, key=lambda c: (c['triage_score'], -c['paragraph_start'], -c['word_count']))
        if not chosen:
            flags.append('no_complete_35_100_word_window')
        if row['origin'] == 'existing_cached_article':
            row['retrieved_at_utc'] = original_lineage[key]['retrieved_at']
        source_record = dict(**row, canonical_alias_key=key, body_sha256=body_hash,
                             byline='|'.join(bylines), byline_verified='single_matching_byline_not_verified' not in flags,
                             authorship_scope='publisher attribution, not proof of sole unaided authorship',
                             status='quarantine' if flags else 'source_QA_pass', flags='|'.join(flags))
        source_inventory.append(source_record)
        if flags:
            excluded.append(dict(source_url=row['source_url'], author=row['author'], reasons='|'.join(flags)))
            continue
        text = chosen['Original']
        text_hash = text_sha(text)
        excerpt_shingles = shingles(text)
        leak = []
        if text_hash in protected_hashes:
            leak.append('heldout_exact_excerpt')
        for protected_id, ps in protected_excerpt_shingles:
            if similarity(excerpt_shingles, ps) >= .8:
                leak.append('heldout_near_excerpt:'+protected_id)
                break
        if leak:
            excluded.append(dict(source_url=row['source_url'], author=row['author'], reasons='|'.join(leak)))
            continue
        cid = old['ID'] if old else 'trainv2:'+text_sha(key)[:16]+f":p{chosen['paragraph_start']}-{chosen['paragraph_end_exclusive']}"
        candidates.append(dict(ID=cid, article_group='article:'+text_sha(key)[:16], author=row['author'], split='train',
                               source_url=row['source_url'], source_date=row['source_date'], title=row['title'],
                               source_snapshot=row['snapshot'], snapshot_sha256=row['snapshot_sha256'], body_sha256=body_hash,
                               source_sha256=text_hash, origin=row['origin'], original105=bool(old),
                               byline=names[row['author']], bio_url='https://www.creators.com/author/'+row['author'],
                               retrieved_at_utc=row['retrieved_at_utc'],
                               **chosen, human_label='', training_ready=False))
    # Connected duplicate groups stay out of the human packet except one deterministic representative.
    parent = list(range(len(candidates)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, j in itertools.combinations(range(len(candidates)), 2):
        a, b = candidates[i], candidates[j]
        if a['source_sha256'] == b['source_sha256'] or similarity(shingles(a['Original']), shingles(b['Original'])) >= .8:
            parent[find(j)] = find(i)
            duplicates.append(dict(source_url=b['source_url'], duplicate_of=a['source_url'], reason='exact_or_near_selected_excerpt_ge08'))
    seen_groups, retained = set(), []
    for i, row in enumerate(candidates):
        group = find(i)
        if group not in seen_groups:
            seen_groups.add(group)
            retained.append(row)
    candidates = retained
    assert len({r['article_group'] for r in candidates}) == len(candidates)
    assert len({r['source_sha256'] for r in candidates}) == len(candidates)
    save(HERE / 'SOURCE_INVENTORY.csv', source_inventory)
    save(HERE / 'CANDIDATES.csv', candidates)
    save(HERE / 'QUARANTINED_SOURCES.csv', excluded)
    save(HERE / 'DUPLICATE_LOG.csv', duplicates)
    priority = [r for r in candidates if r['priority_political_review']]
    save(HERE / 'PRIORITY_POLITICAL_REVIEW.csv', priority)
    summary = dict(unique_article_urls_considered=len(url_seen), new_retrieved_receipts=len(read(HERE / 'NEW_ARTICLE_RECEIPTS.csv')),
                   unique_candidate_texts=len(candidates), priority_political_review=len(priority),
                   lower_priority_candidates=len(candidates)-len(priority), quarantined_sources=len(excluded), duplicate_events=len(duplicates),
                   original105_retained=sum(r['original105'] for r in candidates),
                   new_public_articles_in_candidates=sum(r['origin'] == 'new_public_collection' for r in candidates),
                   by_author=dict(collections.Counter(r['author'] for r in candidates)), human_gold_confirmed=0,
                   protected_heldout_excerpt_fingerprints=len(protected_excerpt_shingles), protected_heldout_article_fingerprints=len(protected_bodies),
                   heldout_use='deterministic URL/exact/5-shingle duplication safeguard only; no labels, predictions, feature fitting or candidate ranking',
                   duplicate_threshold=.8, semantic_event_overlap_proven_absent=False,
                   triage='text-only transparent cue prioritization, not a political label or a validated meaning/stance assessment',
                   no_training=True, no_test_evaluation=True, no_rewriting=True)
    dump(HERE / 'SUMMARY.json', summary)
    packet(candidates)
    protected_files = [FOLLOW / 'author_splits.csv', FOLLOW / 'text_annotations.csv', FOLLOW / 'collected_texts.csv',
                       ROOT / 'MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md', HERE / 'COLLECTION_DESIGN_HE.md',
                       HERE / 'collect.py', HERE / 'prepare.py']
    dump(HERE / 'MANIFEST.json', dict(created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         source_snapshots_sha256=source_hashes,
         protected_inputs_sha256={str(p.relative_to(ROOT)): sha(p) for p in protected_files},
         output_sha256={p.name: sha(p) for p in HERE.iterdir() if p.is_file() and p.name != 'MANIFEST.json'},
         two_raters_independent_pending=True, no_automatic_gold=True))


def packet(candidates):
    blind_map = {}
    order = list(candidates)
    random.Random(2026111705).shuffle(order)
    for i, row in enumerate(order):
        blind_map[row['ID']] = f'TR{i+1:04}'
    key = [dict(review_id=blind_map[r['ID']], **{k: r[k] for k in ('ID', 'article_group', 'author', 'source_sha256', 'source_url', 'original105')}) for r in candidates]
    save(HERE / 'PRIVATE_REVIEW_KEY.csv', key)
    for reviewer, seed in [('A', 2026111706), ('B', 2026111707)]:
        ordered = list(candidates)
        random.Random(seed).shuffle(ordered)
        forms = [dict(review_id=blind_map[r['ID']], Original=r['Original'], label='', evidence_span='', reason='',
                      confidence='', reviewer_type='', reviewer_id='', review_date='', assistance_used='') for r in ordered]
        save(HERE / f'REVIEWER_{reviewer}_BLIND.csv', forms)
        folder = HERE / ('reviewer_'+reviewer)
        folder.mkdir(exist_ok=True)
        for start in range(0, len(forms), 25):
            lines = ['# תיוג עצמאי — Original בלבד', '', 'Left / Right / Unclear. יש למלא את קובץ CSV של הסוקר. אין להיעזר בזהות כותב, מקור או ציוני AI.', '']
            for row in forms[start:start+25]:
                lines += [f"## {row['review_id']}", '', row['Original'], '', '| שדה | תשובה |', '|---|---|',
                          '| Left / Right / Unclear | |', '| ראיה מדויקת | |', '| נימוק / סיבת Unclear | |', '']
            (folder / f'BOOKLET_{start//25+1:02}.md').write_text('\n'.join(lines), encoding='utf-8')
    save(HERE / 'ADJUDICATION_TEMPLATE.csv', [dict(review_id=blind_map[r['ID']], source_sha256=r['source_sha256'],
         final_label='', evidence_span='', rationale='', reviewer_type='', adjudicator_id='', review_date='', assistance_used='') for r in candidates])


if __name__ == '__main__':
    build()

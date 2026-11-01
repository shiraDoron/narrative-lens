"""Collect single-bylined essays, never infer writers from social handles.
One deterministic excerpt per article; no account/category labels used as gold.
Run from repository root with Python 3.11. Source snapshots are research inputs.
"""
from pathlib import Path
import concurrent.futures, datetime, hashlib, json, re, time
import requests
import pandas as pd
from lxml import html

OUT=Path(__file__).resolve().parent
AUTHORS=['ben-shapiro','david-harsanyi','stephen-moore','dennis-prager',
         'star-parker','debra-saunders','jim-hightower','froma-harrop',
         'joe-conason','susan-estrich','marc-dion','jamie-stiehm',
         'veronique-de-rugy','lawrence-kudlow','chuck-norris','mona-charen',
         'connie-schultz','robert-scheer','jeff-robbins','roger-simon']
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
def get(url,path):
    if path.exists():return path.read_text(encoding='utf8')
    for attempt in range(4):
        try:
            r=requests.get(url,timeout=45);r.raise_for_status();r.encoding='utf8'
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(r.text,encoding='utf8');return r.text
        except requests.RequestException:
            if 'r' in locals() and r.status_code in (401,403,404,410):raise
            if attempt==3:raise
            time.sleep(2+attempt)
def wc(t):return len(re.findall(r"\b\w+(?:['’]\w+)*\b",t))
def collect_author(slug):
    base='https://www.creators.com';cache=OUT/'sources'/slug
    feature_url=f'{base}/features/{slug}';bio_url=f'{base}/author/{slug}'
    if slug=='debra-saunders':bio_url=f'{base}/author/debra-j-saunders'
    feature=html.fromstring(get(feature_url,cache/'feature.html'))
    bios=feature.xpath('//a[contains(@href,"/author/")]/@href')
    if bios:bio_url=requests.compat.urljoin(base,bios[0])
    bio=html.fromstring(get(bio_url,cache/'bio.html'))
    names=feature.xpath('//h1/text()');name=' '.join(names).strip()
    ids=feature.xpath('//a[@data-feature-id]/@data-feature-id')
    if not ids:raise ValueError(f'No explicit feature id for {slug}')
    fid=ids[0];releases=[]
    for u in dict.fromkeys(feature.xpath('//a[contains(@href,"/read/")]/@href')):
        releases.append({'id':hashlib.sha256(u.encode()).hexdigest()[:12],'formatted_url':u,'title':'','release_date':''})
    for page in range(1,6):
        api=f'{base}/api/features/releases/{fid}/{page}'
        data=json.loads(get(api,cache/f'page{page}.json'))
        releases.extend(data['releases'])
    seen=set();rows=[];reject=[]
    for r in releases:
        if r['id'] in seen:continue
        seen.add(r['id']);url=r['formatted_url']
        if len(rows)>=24:break
        try:
            try:raw=get(url,cache/f"article_{r['id']}.html")
            except requests.HTTPError:
                alternative=re.sub(r'-[0-9a-f]{5,8}$','',url)
                if alternative==url:raise
                url=alternative;raw=get(url,cache/f"article_{r['id']}.html")
            doc=html.fromstring(raw)
            canonical=doc.xpath('//link[@rel="canonical"]/@href')
            if canonical:url=canonical[0]
        except requests.RequestException as exc:
            reject.append({'author':slug,'url':url,'reason':'source_unavailable','error':str(exc)});continue
        bylines=doc.xpath('//*[@itemprop="creator"]//a/text()')
        date=doc.xpath('//*[@data-default-date]/@data-default-date')
        # Require a single explicit byline and matching feature/bio identity.
        if len(bylines)!=1 or bylines[0].strip().casefold()!=name.casefold() or bio_url.rsplit('/',1)[-1] not in ''.join(doc.xpath('//*[@itemprop="creator"]//a/@href')):
            reject.append({'author':slug,'url':url,'reason':'single_matching_byline_not_verified','bylines':bylines});continue
        paragraphs=[' '.join(p.text_content().split()) for p in doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," article-content ")]/p')]
        paragraphs=[p for p in paragraphs if p and not re.search(r'COPYRIGHT|DISTRIBUTED BY|To find out more|To learn more about|Visit the Creators|Write to .* at|email .*@',p,re.I)]
        # First eligible contiguous paragraph(s), chosen before any label/model outcome.
        selected=None;offset=None
        for i,p in enumerate(paragraphs):
            t=p
            if wc(t)<35 and i+1<len(paragraphs):t+=' '+paragraphs[i+1]
            if 35<=wc(t)<=100:selected=t;offset=i;break
        if not selected:
            reject.append({'author':slug,'url':url,'reason':'no_35_to_100_word_contiguous_excerpt'});continue
        rows.append({'row_id':f"creators:{r['id']}",'author':slug,'author_name':name,
            'account':feature_url,'source_url':url,'source_date':date[0] if date else r['release_date'][:10],
            'title':r['title'] or ' '.join(doc.xpath('//h1/text()')),'text':selected,'word_count':wc(selected),'paragraph_start':offset,
            'byline':bylines[0],'byline_verified':True,'bio_url':bio_url,
            'text_sha256':hashlib.sha256(selected.encode()).hexdigest(),
            'article_snapshot_sha256':hashlib.sha256((cache/f"article_{r['id']}.html").read_bytes()).hexdigest(),
            'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'authorship_scope':'publisher single named byline, not forensic proof of sole unaided composition'})
    bios=' '.join(bio.xpath('//h1/text()'))
    reg={'author':slug,'name':name,'bio_heading':bios,'bio_url':bio_url,'feature_url':feature_url,
         'verification':'Publisher biography identifies named person; each included article explicitly carries that person as its single byline.',
         'verified_single_bylined_person':bool(name and name.casefold() in ' '.join(bio.itertext()).casefold() and rows),
         'n_articles':len(rows),'account_posts_verified':False,
         'limitation':'Editorial assistance/ghostwriting cannot be excluded; not evidence that social posts were personally written.'}
    return rows,reg,reject
def main():
    if all((OUT/n).exists() for n in ['collected_texts.csv','collection_protocol.json','author_registry.json']):
        print('Using frozen collection; create a new versioned directory to recollect.',flush=True);return
    allrows=[];registry=[];reject=[];errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(collect_author,a):a for a in AUTHORS}
        for f in concurrent.futures.as_completed(futures):
            a=futures[f]
            try:
                rows,reg,rej=f.result();allrows.extend(rows);registry.append(reg);reject.extend(rej);print(a,len(rows),flush=True)
            except Exception as exc:errors.append({'author':a,'error':repr(exc)});print(a,repr(exc),flush=True)
    pd.DataFrame(allrows).sort_values(['author','source_date','row_id']).to_csv(OUT/'collected_texts.csv',index=False,encoding='utf-8-sig')
    dump(OUT/'author_registry.json',registry);dump(OUT/'collection_rejections.json',reject);dump(OUT/'collection_errors.json',errors)
    dump(OUT/'collection_protocol.json',{'authors_prespecified':AUTHORS,'articles_per_author_target':24,'selection':'Public feature page plus 5 publicly accessible archive pages; one first eligible contiguous 35–100 word excerpt per article. API page 6 returned 401 during feasibility and was not used or bypassed.','source_category_used_as_gold':False,'scope':'Exploratory individually bylined English opinion essays, potential Right-wing/Left-wing contrast, not a seven-narrative replication. Other labels and unclear remain available at text annotation.','sole_unaided_authorship_proven':False})
if __name__=='__main__':main()

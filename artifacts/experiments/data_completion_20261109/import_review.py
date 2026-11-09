"""Explicit, immutable reviewer import. Never infer human ratings from counts or LLMs."""
import argparse
import datetime
import json
from pathlib import Path
import re
import shutil
from bundle import HERE,legacy,missing,mapping,read,save,dump,sha,text_sha,verify

FIELDS=['human_meaning_preserved','human_narrative_stance_preserved','human_style_change_valid','human_semantic_drift','human_notes']
def parse(source,kind):
    if source.suffix.lower()=='.csv':return read(source)
    if source.suffix.lower()!='.md':raise ValueError('Supported formats: UTF-8 CSV or Markdown')
    text=source.read_text(encoding='utf-8-sig');rows=[]
    for match in re.finditer(r'^## (creators:[^\r\n]+)\s*\n(.*?)(?=^## creators:|\Z)',text,re.S|re.M):
        rid,block=match.groups();fields=dict(re.findall(r'^\| ([a-z_]+) \| (.*?) \|\s*$',block,re.M))
        if kind in ('labels105','labels43'):
            original=block.split('**תווית מוצעת')[0].strip()
            proposed=re.search(r'\*\*תווית מוצעת בלבד, לא gold:\*\* ([^\r\n]+)',block)
            rows.append(dict(ID=rid,Original=original,proposed_label=proposed.group(1) if proposed else '',**fields))
        else:
            original=re.search(r'### Original\s*\n\n(.*?)\n\n### (?:ChatGPT Style Rewrite|Style Rewrite)',block,re.S)
            rewrite=re.search(r'### (?:ChatGPT Style Rewrite|Style Rewrite)\s*\n\n(.*?)\n\n\| field',block,re.S)
            if not original or not rewrite:raise ValueError('Cannot bind Markdown review to exact text pair')
            rows.append(dict(ID=rid,Original=original.group(1).strip(),ChatGPT_Style_Rewrite=rewrite.group(1).strip(),**fields))
    return rows
def registry(kind,run=None):
    if kind=='pairs30':return legacy()
    if kind=='labels105':return {r['ID']:r for r in mapping()}
    if kind=='labels43':
        from bundle import FOLLOW
        return {r['row_id']:dict(ID=r['row_id'],Original=r['text'],label=r['narrative_name'])
                for r in read(FOLLOW/'analysis_cohort.csv') if r['split']=='val'}
    if kind=='pairs105':
        combined={**legacy(),**registry('pairs75',run)}
        if len(combined)!=105:raise ValueError('Expected exact105 combined text pairs')
        return combined
    if not run:raise ValueError('pairs75 requires an ingested run name')
    run_dir=(HERE/'runs'/run).resolve()
    if run_dir.parent!=(HERE/'runs').resolve():raise ValueError('Invalid run name')
    receipt=json.loads((run_dir/'RECEIPT.json').read_text())
    if sha(run_dir/'received_rewrites_75.csv')!=receipt['canonical_output_sha256']:raise ValueError('Canonical output changed after receipt')
    expected={r['ID']:r for r in missing()};data=read(run_dir/'received_rewrites_75.csv')
    if len(data)!=75 or {r['ID'] for r in data}!=set(expected):raise ValueError('Wrong new75 ID registry')
    if any(r['Original']!=expected[r['ID']]['Original'] for r in data):raise ValueError('New75 Original mismatch')
    return {r['ID']:dict(ID=r['ID'],Original=r['Original'],Style=r['ChatGPT_Style_Rewrite']) for r in data}
def validate(rows,expected,kind,reviewer_type):
    ids=[r.get('ID',r.get('id','')) for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate review ID')
    if set(ids)!=set(expected):raise ValueError(f'ID mismatch: missing={sorted(set(expected)-set(ids))}, unexpected={sorted(set(ids)-set(expected))}')
    results=[]
    for row,rid in zip(rows,ids):
        original=expected[rid]['Original']
        if row.get('Original')!=original:raise ValueError(f'{rid}: Original differs from frozen source')
        declared=(row.get('reviewer_type') or '').lower()
        if declared and declared!=reviewer_type:raise ValueError(f'{rid}: reviewer_type contradicts import metadata')
        if reviewer_type=='human' and 'llm' in (row.get('review_type') or '').lower():raise ValueError('LLM review cannot be imported as human')
        if kind in ('labels105','labels43'):
            if row.get('proposed_label')!=expected[rid]['label']:raise ValueError('Proposed label changed')
            if row.get('human_label') not in ['Right-wing','Left-wing','Unclear','Mixed','Other']:raise ValueError(f'{rid}: missing/invalid human_label')
            if row.get('proposed_label_correct') not in ['Yes','No','Borderline']:raise ValueError('Missing label agreement rating')
            evidence=row.get('evidence_span') or ''
            if evidence and evidence not in original:raise ValueError(f'{rid}: evidence span is not verbatim Original')
            payload={k:row.get(k) or '' for k in ['human_label','proposed_label_correct','evidence_span','human_notes']}
        else:
            rewrite=expected[rid]['Style']
            if row.get('ChatGPT_Style_Rewrite')!=rewrite:raise ValueError(f'{rid}: rewrite differs from frozen text version')
            for k in FIELDS[:-1]:
                if row.get(k) not in ['Yes','No','Borderline']:raise ValueError(f'{rid}: missing/invalid {k}')
            if 'human_notes' not in row:raise ValueError('Notes column required; may be blank')
            payload={k:row.get(k) or '' for k in FIELDS}
            payload['rewrite_sha256']=text_sha(rewrite)
        results.append(dict(ID=rid,reviewer_type=reviewer_type,source_sha256=text_sha(original),**payload))
    return results
def import_file(source,kind,reviewer_type,reviewer_id,review_date,name,run=None,assistance='not supplied'):
    verify();datetime.date.fromisoformat(review_date)
    if not reviewer_id.strip():raise ValueError('Reviewer identity required')
    if not re.fullmatch(r'[A-Za-z0-9_-]+',name):raise ValueError('Use a simple unique import name')
    raw=source.read_bytes();header=raw.decode('utf-8-sig')[:1800]
    if reviewer_type=='human' and (re.search(r'Reviewer[^\n]*Claude[^\n]*(?:LLM|AI)',header,re.I) or re.search(r'This is an.*(?:LLM-based|automated AI) review',header,re.I)):
        raise ValueError('Source explicitly declares LLM review; refusing human attribution')
    parsed=parse(source,kind)
    for row in parsed:
        if row.get('reviewer_id') and row['reviewer_id']!=reviewer_id:raise ValueError('Reviewer ID contradicts row metadata; do not overwrite')
        if row.get('review_date') and row['review_date']!=review_date:raise ValueError('Review date contradicts row metadata; do not overwrite')
    rows=validate(parsed,registry(kind,run),kind,reviewer_type)
    dest=HERE/('human_imports' if reviewer_type=='human' else 'llm_imports')/name
    if dest.exists():raise ValueError('Import is immutable; choose a new version name')
    dest.mkdir(parents=True)
    shutil.copyfile(source,dest/('received'+source.suffix.lower()))
    for row in rows:row.update(reviewer_id=reviewer_id,review_date=review_date)
    save(dest/'reviews_by_id.csv',rows)
    issues=[]
    for r in rows:
        if kind not in ('labels105','labels43') and r['human_meaning_preserved']=='Yes' and r['human_semantic_drift']=='Yes':issues.append(dict(ID=r['ID'],issue='meaning Yes and drift Yes; retain ratings, clarify'))
        if any(v=='Borderline' for v in r.values()) and not r.get('human_notes'):issues.append(dict(ID=r['ID'],issue='Borderline without notes; retain ratings, clarify'))
    dump(dest/'IMPORT_MANIFEST.json',dict(kind=kind,n=len(rows),source_sha256=sha(source),reviewer_type=reviewer_type,
      reviewer_id=reviewer_id,review_date=review_date,assistance_used=assistance,
      attribution_basis='Explicit user-supplied metadata; reviewer identity not independently verified',
      ratings_edited=False,original_human_files_overwritten=False,issues=issues,
      text_version=('train105_20261026' if kind=='labels105' else 'validation43_20261026' if kind=='labels43' else run or 'legacy_chatgpt30_20261102')))
    verify();return dest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--kind',choices=['pairs30','pairs75','pairs105','labels105','labels43'],required=True)
    p.add_argument('--reviewer-type',choices=['human','llm'],required=True);p.add_argument('--reviewer-id',required=True)
    p.add_argument('--review-date',required=True);p.add_argument('--name',required=True);p.add_argument('--run');p.add_argument('--assistance-used',default='not supplied')
    a=p.parse_args()
    try:print(import_file(a.source,a.kind,a.reviewer_type,a.reviewer_id,a.review_date,a.name,a.run,a.assistance_used))
    except (ValueError,AssertionError,FileNotFoundError) as e:p.error(str(e))

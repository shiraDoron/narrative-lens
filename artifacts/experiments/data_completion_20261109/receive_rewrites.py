"""Receive 75 outputs unchanged, reject wrong IDs, generate blind human package."""
import argparse
import json
from pathlib import Path
import re
import shutil
from bundle import HERE,VERSION,missing,read,save,dump,sha,text_sha,make_pair_package,verify
def combine(sources):
    expected={r['ID']:r for r in missing()};out=[];seen=set()
    for source in sources:
        for r in read(source):
            rid=r.get('id',r.get('ID',''));text=r.get('chatgpt_style_rewrite','')
            if rid in seen:raise ValueError('Duplicate output ID: '+rid)
            if rid not in expected:raise ValueError('Unknown/legacy/non-train ID: '+rid)
            if not text.strip():raise ValueError('Empty output: '+rid)
            if 'original' in r and r['original']!=expected[rid]['Original']:raise ValueError('Original changed: '+rid)
            seen.add(rid);out.append(dict(ID=rid,Original=expected[rid]['Original'],ChatGPT_Style_Rewrite=text,
              source_sha256=text_sha(expected[rid]['Original']),rewrite_sha256=text_sha(text),protocol_version=VERSION))
    if seen!=set(expected):raise ValueError(f'Expected all75; missing {len(set(expected)-seen)} IDs')
    order={r['ID']:i for i,r in enumerate(missing())};return sorted(out,key=lambda r:order[r['ID']])
def receive(sources,name,metadata):
    verify()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',name):raise ValueError('Invalid run name')
    data=combine(sources);meta=json.loads(metadata.read_text(encoding='utf-8-sig'))
    if meta.get('protocol_version')!=VERSION or meta.get('prompt_sha256')!=sha(HERE/'STYLE_REWRITE_PROMPT_V1.txt'):raise ValueError('Generation protocol/prompt hash mismatch')
    dest=HERE/'runs'/name
    if dest.exists():raise ValueError('Run already exists; no overwrite')
    dest.mkdir(parents=True)
    for i,p in enumerate(sources):shutil.copyfile(p,dest/f'received_{i+1:02d}.csv')
    shutil.copyfile(metadata,dest/'received_generation_metadata.json')
    save(dest/'received_rewrites_75.csv',data)
    make_pair_package(data,dest/'HUMAN_PAIR_REVIEW_NEW75',75)
    dump(dest/'RECEIPT.json',dict(n=75,prompt_sha256=meta['prompt_sha256'],protocol_version=VERSION,
      canonical_output_sha256=sha(dest/'received_rewrites_75.csv'),
      source_files=[dict(name=p.name,sha256=sha(p)) for p in sources],
      provenance_complete=all(meta.get(k) for k in ['interface','visible_model_name','actual_generation_date']),
      exact_model_revision_known=bool(meta.get('exact_model_revision')),legacy30_overwritten=False,
      automatic_screen_executed=False,human_validation_complete=False,training_ready=False))
    verify();return dest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sources',nargs='+',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--metadata',type=Path,required=True);a=p.parse_args()
    try:print(receive(a.sources,a.name,a.metadata))
    except (ValueError,AssertionError,FileNotFoundError) as e:p.error(str(e))

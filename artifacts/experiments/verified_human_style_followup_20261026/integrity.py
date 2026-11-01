"""Freeze/check all previous-pilot files and original data/model by SHA-256."""
from pathlib import Path
import hashlib,json,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
manifest=OUT/'protected_inputs_sha256.json'
if not manifest.exists():
    paths=list((ROOT/'artifacts/experiments/author_style_controlled_20261026').rglob('*'))
    paths+=[ROOT/'models/best_model_sbert_only.pth',ROOT/'data/raw/twitter_natural_dataset.csv',ROOT/'data/raw/telegram_natural_dataset.csv']
    data={str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}
    manifest.write_text(json.dumps(data,indent=2),encoding='utf8');print('Frozen',len(data),'protected files')
else:
    data=json.loads(manifest.read_text());changed=[p for p,h in data.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    (OUT/'protected_inputs_audit.json').write_text(json.dumps({'checked_files':len(data),'unchanged':not changed,'changed':changed},indent=2),encoding='utf8')
    print('Checked',len(data),'changed',len(changed));assert not changed,changed

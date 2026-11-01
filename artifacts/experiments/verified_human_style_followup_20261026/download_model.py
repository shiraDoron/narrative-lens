from pathlib import Path
import hashlib,json,requests,time
OUT=Path(__file__).resolve().parent
REV='7dabda4d13d513e3e842b20f0d435c732f172cbe'
REPO='Qwen/Qwen2.5-3B-Instruct-GGUF'
FILE='qwen2.5-3b-instruct-q4_k_m.gguf'
path=OUT/'runtime'/FILE;path.parent.mkdir(exist_ok=True)
url=f'https://huggingface.co/{REPO}/resolve/{REV}/{FILE}?download=true&cache=20261026'
if not path.exists():
    with requests.get(url,stream=True,timeout=30) as r:
        r.raise_for_status()
        print('Download response',r.status_code,r.headers.get('Content-Length'),flush=True)
        staging=path.parent/'model_download.tmp'
        with staging.open('wb') as f:
            for i,b in enumerate(r.iter_content(65536)):
                f.write(b)
                if i%1024==0:print('Downloaded MiB',round((i+1)/16),flush=True)
    staging.rename(path)
h=hashlib.sha256()
with path.open('rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
assert h.hexdigest()=='626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d','Pinned official LFS SHA-256 mismatch'
(OUT/'generator_manifest.json').write_text(json.dumps({'repo':REPO,'revision':REV,'url':url,'file':FILE,'sha256':h.hexdigest(),'bytes':path.stat().st_size,'quantization':'Q4_K_M','reason':'3B instruction model replaces previous pilot 0.5B and excluded 1.5B feasibility generator; no LoRA or DoRA.','cpu_threads':8,'parallel_slots':4,'cache_prompt':True,'max_tokens':240,'temperature':0,'seed':20261026},indent=2),encoding='utf8')
print('Model ready',path.stat().st_size,flush=True)

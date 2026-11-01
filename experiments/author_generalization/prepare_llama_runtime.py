"""Download pinned official CPU runtime/model; do not install system software."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/experiments/author_style_controlled_20261026'
RUNTIME=OUT/'runtime_llama'
RUNTIME.mkdir(exist_ok=True)
release='b11887'
archive=RUNTIME/'llama-cpu.zip'
url=f'https://github.com/ggml-org/llama.cpp/releases/download/{release}/llama-{release}-bin-win-cpu-x64.zip'
expected='cf6a48560e0c32baf875f0b84ac578b111e16115ccf2382836489b5e268809c4'
if not archive.exists():urllib.request.urlretrieve(url,archive)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
assert sha(archive)==expected,'Official runtime archive checksum mismatch'
with zipfile.ZipFile(archive) as z:
    for member in z.namelist():
        assert (RUNTIME/member).resolve().is_relative_to(RUNTIME.resolve())
    z.extractall(RUNTIME)
revision='9217f5db79a29953eb74d5343926648285ec7e67'
filename='qwen2.5-0.5b-instruct-q8_0.gguf'
model=RUNTIME/filename
model_url=f'https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/{revision}/{filename}'
if not model.exists():urllib.request.urlretrieve(model_url,model)
metadata={'engine':'llama.cpp','release':release,'runtime_url':url,'runtime_archive_sha256':expected,
    'model':'Qwen/Qwen2.5-0.5B-Instruct-GGUF','revision':revision,'file':filename,
    'model_url':model_url,'model_sha256':sha(model),'quantization':'GGUF Q8_0 weights; floating point activations'}
(OUT/'llama_runtime_manifest.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metadata),flush=True)

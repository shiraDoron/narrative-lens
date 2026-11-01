"""Prepare a pinned CPU runtime in this study, without touching the old pilot."""
from pathlib import Path
import hashlib,json,shutil,urllib.request,zipfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2];D=P/'runtime_llama';D.mkdir(exist_ok=True)
release='b11887';expected='cf6a48560e0c32baf875f0b84ac578b111e16115ccf2382836489b5e268809c4'
archive=D/'llama-cpu.zip';old=ROOT/'artifacts/experiments/author_style_controlled_20261026/runtime_llama/llama-cpu.zip'
url=f'https://github.com/ggml-org/llama.cpp/releases/download/{release}/llama-{release}-bin-win-cpu-x64.zip'
if not archive.exists():
    if old.exists():shutil.copyfile(old,archive)
    else:urllib.request.urlretrieve(url,archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
with zipfile.ZipFile(archive) as z:
    assert all((D/n).resolve().is_relative_to(D.resolve()) for n in z.namelist())
    z.extractall(D)
(P/'runtime_manifest.json').write_text(json.dumps({'release':release,'url':url,'archive_sha256':expected,'runtime_directory':'runtime_llama','previous_pilot_modified':False},indent=2),encoding='utf8')
print('Pinned CPU runtime prepared in new study directory',flush=True)

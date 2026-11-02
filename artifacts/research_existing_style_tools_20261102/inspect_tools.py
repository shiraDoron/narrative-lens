"""Read-only tool feasibility audit. Never installs packages or runs generation."""
from pathlib import Path
import argparse, ast, concurrent.futures, csv, datetime, hashlib, importlib.metadata
import importlib.util, json, os, platform, subprocess, urllib.error, urllib.parse, urllib.request

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
STYLE_COMMIT='c999002c4a5e858ac452794b20b896d06137a13c'
BART_COMMIT='6c6560caaa7828185ae914b207e3070da789a171'
SELECTED={
    '417181':'certainty, attribution, omitted quotation',
    '120177':'rhetorical intensity, temporal information',
    '212505':'numeric detail, quantifier, certainty',
    '421951':'participant roles, rhetorical intensity',
    '423315':'event characterization, certainty',
    '8b0d99b23d03':'quote fidelity, metaphor, factual detail',
    '298495':'factual detail, attribution',
    '418904':'direct quotation, historical detail, rhetoric',
    '459e183c1d0d':'attribution, certainty, numbers',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Narrative-Lens-feasibility-audit','Accept':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=40) as response:
            data=response.read(); status=response.status
        try: value=json.loads(data)
        except json.JSONDecodeError: value=data.decode('utf8','replace')
        return dict(url=url,status=status,value=value)
    except urllib.error.HTTPError as e: return dict(url=url,status=e.code,error=e.read(1000).decode('utf8','replace'))
    except Exception as e: return dict(url=url,status=None,error=str(e))
def git(repo,*args): return subprocess.check_output(['git','-C',str(repo),*args],text=True,encoding='utf8').strip()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--external-root',type=Path,required=True);args=parser.parse_args()
    repos={};paths={}
    for name,commit,files in [('StyleRemix',STYLE_COMMIT,['README.md','quickstart.py','obfuscate.py','src/eval_data.py','src/generate_lora_adapters.py','requirements.txt','LICENSE']),('pre-trained-formality-transfer',BART_COMMIT,['README.md','infer.py','model.py','pg.sh','train.py','LICENSE'])]:
        repo=args.external_root/name; assert git(repo,'rev-parse','HEAD')==commit
        assert not git(repo,'status','--porcelain')
        tree=git(repo,'ls-tree','-rl','HEAD').splitlines()
        repos[name]=dict(commit=commit,commit_date=git(repo,'log','-1','--format=%cI'),remote=git(repo,'remote','get-url','origin'),inspected_file_sha256={f:sha(repo/f) for f in files},checkpoint_tree=[line for line in tree if 'checkpoint' in line.lower()],license_first_lines=(repo/'LICENSE').read_text(encoding='utf8').splitlines()[:4])
        paths[name]=repo
    tree=ast.parse((paths['StyleRemix']/'quickstart.py').read_text(encoding='utf8'))
    adapters=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MODEL_PATHS' for t in n.targets))
    assert len(adapters)==16
    def metadata(item):
        axis,model=item
        data=fetch('https://huggingface.co/api/models/'+model)
        config=fetch('https://huggingface.co/'+model+'/resolve/main/adapter_config.json')
        value=data.get('value',{})
        return dict(axis=axis,model_id=model,status=data['status'],revision=value.get('sha'),gated=value.get('gated'),license=value.get('cardData',{}).get('license'),config=config,metadata_url=data['url'])
    with concurrent.futures.ThreadPoolExecutor(4) as pool: adapter_info=list(pool.map(metadata,adapters.items()))
    dump('external_repos.json',repos);dump('adapter_inventory.json',adapter_info)
    base=fetch('https://huggingface.co/api/models/meta-llama/Meta-Llama-3-8B');value=base.get('value',{})
    base_small={k:value.get(k) for k in ('id','sha','gated','safetensors','config')}
    base_small['cardData']={'license':value.get('cardData',{}).get('license')}
    dump('base_checkpoint_probe.json',dict(metadata_url=base['url'],status=base['status'],metadata=base_small,anonymous_config=fetch('https://huggingface.co/meta-llama/Meta-Llama-3-8B/resolve/main/config.json')))
    demo=fetch('https://huggingface.co/api/spaces/hallisky/StyleRemix');space=demo.get('value',{});runtime=space.get('runtime',{})
    dump('hosted_demo_probe.json',dict(url=demo['url'],status=demo['status'],revision=space.get('sha'),host=space.get('host'),sdk=space.get('sdk'),runtime_stage=runtime.get('stage'),hardware=runtime.get('hardware'),error_summary=runtime.get('errorMessage','').splitlines()[-1:] or [],inference_request_sent=False))
    queries=['"A Decoupled Multi-Agent Framework for Complex Text Style Transfer"','"style transfer" "Lingxi"']
    found=[]
    for q in queries:
        result=fetch('https://api.github.com/search/repositories?q='+urllib.parse.quote(q));v=result.get('value',{})
        found.append(dict(query=q,status=result['status'],total_count=v.get('total_count'),items=[dict(name=i['full_name'],url=i['html_url'],description=i.get('description')) for i in v.get('items',[])[:10]]))
    dump('official_implementation_search.json',dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),queries=found,other_sources=['https://aclanthology.org/2025.findings-emnlp.1166/','https://aclanthology.org/2025.findings-emnlp.1166.pdf','https://lingxi-zhang.github.io/'],conclusion='No official public implementation identified in checked sources; not proof that none exists.'))
    ps="[ordered]@{cpu=(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors);memory=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory;gpu=@(Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM);disk_free=(Get-PSDrive C).Free} | ConvertTo-Json -Depth 4"
    hardware=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',ps],text=True))
    import torch
    hardware.update(python=platform.python_version(),torch=torch.__version__,cuda_available=torch.cuda.is_available(),cuda_device_count=torch.cuda.device_count(),packages={})
    for name in ('transformers','peft','bitsandbytes','accelerate','vllm'):
        try: hardware['packages'][name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: hardware['packages'][name]=None
    dump('hardware_environment.json',hardware)
    study=ROOT/'artifacts/experiments/style_intervention_v2_20261026';v2=study/'train_prompt_revision_30_20261101'
    def records(p):
        with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
    cohort={r['row_id']:r for r in records(v2/'analysis_cohort.csv')}
    comparisons=records(v2/'comparison_30.csv');guards={r['row_id']:r for r in records(v2/'rewrite_validation.csv') if r['condition']=='Normalized'}
    spec=importlib.util.spec_from_file_location('existing_style_proxies',study/'study.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    planned=[]
    for r in comparisons:
        suffix=r['ID'].split(':')[1]
        if suffix not in SELECTED: continue
        assert cohort[r['ID']]['split']=='train' and cohort[r['ID']]['text']==r['Original']
        planned.append(dict(ID=r['ID'],split='train',coverage=SELECTED[suffix],Original=r['Original'],v2_output=r['New_Normalized'],v2_guards=guards[r['ID']],v2_style=m.style_metrics(r['Original'],r['New_Normalized']),StyleRemix_output=None,status='planned_only_not_generated'))
    assert len(planned)==9
    dump('planned_train_subset.json',planned)
    summary=dict(n=9,v2=dict(preservation_pass=sum(r['v2_guards']['passed']=='True' for r in planned),style_change=sum(r['v2_style']['substantial_style_change'] for r in planned),both=sum(r['v2_guards']['passed']=='True' and r['v2_style']['substantial_style_change'] for r in planned),exact_copy=sum(r['v2_style']['exact_copy'] for r in planned)),StyleRemix=dict(status='not_run_hardware_and_checkpoint_access_blocked',n_generated=0,preservation_pass=None,style_change=None,both=None,exact_copy=None),not_a_completed_benchmark=True)
    dump('baseline_subset_summary.json',summary)
    dump('audit_manifest.json',dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),project_commit=git(ROOT,'rev-parse','HEAD'),scope='Static feasibility and frozen TRAIN subset preparation only',source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [v2/'comparison_30.csv',v2/'analysis_cohort.csv',v2/'rewrite_validation.csv',study/'study.py']},inference_run=False,model_weights_downloaded_for_inference=False,external_clone_note='BART repository itself includes TextCNN classifier checkpoint blobs; external clones stay outside project/Git. No classifier weights loaded.',packages_installed=False,repair_development=False,external_review=False,training=False,test_evaluation=False))
    print(json.dumps(summary))
if __name__=='__main__': main()

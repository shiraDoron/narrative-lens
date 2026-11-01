"""Same frozen prompts/greedy requests, without loading PyTorch into client RAM."""
from pathlib import Path
import concurrent.futures,csv,json,os,subprocess,sys,time,urllib.request
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'src'))
from narrative_lens.features.style_normalization import normalize_style
def read(name):return json.loads((P/name).read_text(encoding='utf8'))
def records(name):return list(csv.DictReader((P/name).open(encoding='utf-8-sig',newline='')))
def log(s):print(time.strftime('%H:%M:%S'),s,flush=True)
endpoint='http://127.0.0.1:18092';manifest=read('generator_manifest.json')
try:
    with urllib.request.urlopen(endpoint+'/health',timeout=2) as r:assert r.status==200
except Exception:
    runtime=P/'runtime';exe=P/'runtime_llama/llama-server.exe'
    if not exe.exists():exe=ROOT/'artifacts/experiments/author_style_controlled_20261026/runtime_llama/llama-server.exe'
    proc=subprocess.Popen([str(exe),'-m',str(runtime/manifest['file']),'--host','127.0.0.1','--port','18092','-t','8','-tb','8','-np','4','-c','8192','--no-webui'],cwd=runtime,stdout=(runtime/'server_stdout.log').open('a'),stderr=(runtime/'server_stderr.log').open('a'),creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    (P/'server_process.json').write_text(json.dumps({'pid':proc.pid,'executable':str(exe),'model':str(runtime/manifest['file']),'port':18092}),encoding='utf8')
    for _ in range(90):
        try:
            with urllib.request.urlopen(endpoint+'/health',timeout=2) as r:
                if r.status==200:break
        except Exception:time.sleep(1)
    else:raise RuntimeError('Generator server unavailable')
prompts=read('rewrite_prompts.json')['prompts'];x=records('analysis_cohort.csv');cf={r['row_id'] for r in records('counterfactual_selection.csv')}
path=P/'generated_rewrites.jsonl';done=[json.loads(s) for s in path.read_text(encoding='utf8').splitlines() if s.strip()] if path.exists() else [];keys={(r['row_id'],r['condition']) for r in done}
with path.open('a',encoding='utf8') as f:
    for r in x:
        if (r['row_id'],'Formatting') not in keys:f.write(json.dumps({'row_id':r['row_id'],'condition':'Formatting','original':r['text'],'rewrite':normalize_style(r['text']),'truncated':False,'engine':'project deterministic formatter'},ensure_ascii=False)+'\n')
tasks=[{'row_id':r['row_id'],'condition':c,'original':r['text']} for r in x for c in ['Paraphrase','Normalized']+(['Formal','Conversational','Concise','Elaborate'] if r['row_id'] in cf else []) if (r['row_id'],c) not in keys]
def run(t):
    payload={'messages':[{'role':'system','content':prompts[t['condition']]},{'role':'user','content':t['original']}],'temperature':0,'seed':20261026,'max_tokens':240,'repeat_penalty':1.,'top_k':1,'top_p':1.,'min_p':0.,'cache_prompt':True}
    req=urllib.request.Request(endpoint+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'});begin=time.perf_counter()
    with urllib.request.urlopen(req,timeout=600) as response:r=json.load(response)
    c=r['choices'][0]
    return {**t,'rewrite':c['message']['content'].strip(),'truncated':c['finish_reason']=='length','seconds':time.perf_counter()-begin,'usage':r.get('usage'),'generator':manifest['repo']}
log(f'Light client resumes {len(tasks)} remaining rewrites, identical generation settings')
with concurrent.futures.ThreadPoolExecutor(4) as pool,path.open('a',encoding='utf8') as f:
    for i,r in enumerate(pool.map(run,tasks),1):
        f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
        if i%8==0 or i==len(tasks):log(f'Rewrites {i}/{len(tasks)} (resumed client)')
(P/'generation_complete.json').write_text(json.dumps({'complete':True,'expected_main_llm':2*len(x),'expected_counterfactual':4*len(cf),'client':'light standard-library HTTP client; same prompts, seed, weights, budget and decoder settings as initial requests'}),encoding='utf8')

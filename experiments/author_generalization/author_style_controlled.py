"""Isolated, resumable, CPU pilot of style normalization versus paraphrase.

No original data/model/result files are modified. Run --stage prepare|baseline|
generate|validate|evaluate|report|all from repository root. See generated README.
"""
from pathlib import Path
import argparse
import collections
import gc
import hashlib
import itertools
import json
import os
import random
import re
import sys
import time
import unicodedata

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('TRANSFORMERS_OFFLINE','1')
os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score, recall_score, log_loss
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from narrative_lens.features.style_normalization import normalize_style
from narrative_lens.data.text_dedup import (get_shingles,build_minhash_signatures,
    lsh_candidate_pairs,jaccard,UnionFind)

OUT=ROOT/'artifacts/experiments/author_style_controlled_20261026'
LABELS=['Zionist','Resistance','Western','Russian','Ukrainian','Right-wing','Left-wing']
SEEDS=[42,7,123]
GEN_MODEL='Qwen/Qwen2.5-0.5B-Instruct-GGUF'
NER_REVISION='d1a3e8f13f8c3566299d95fcfc9a8d2382a9affc'
NLI_REVISION='cf44676c28ba7312e5c5f8f8d2c22b3e0c9cdae2'
SEMANTIC_REVISION='e8c3b32edf5434bc2275fc9bab85f82640a19130'
CONFIG={'split_seed':20261026,'authors_per_label':4,'texts_per_author':12,
    'train_authors_per_label':2,'val_authors_per_label':1,'test_authors_per_label':1,
    'min_words':20,'max_words':65,'seeds':SEEDS,'epochs':20,'batch_size':16,
    'lr':.001,'hidden_size':128,'dropout':.3,'encoder':'sentence-transformers/all-MiniLM-L6-v2',
    'semantic_validation_encoder':'sentence-transformers/all-mpnet-base-v2',
    'generator':GEN_MODEL,'generation_seed':20261026,'generation_batch_size':4,
    'generator_quantization':'GGUF Q8_0 weights; floating point activations',
    'max_new_tokens':180,'do_sample':False,'similarity_threshold':.85,
    'bidirectional_entailment_threshold':.60,'entity_retention_threshold':1.,
    'counterfactual_per_label':2,'stance_control_per_label':1,'threads':4,
    'interpretation':'Exploratory CPU pilot; source-account labels, automated semantic screening, no independent human gold validation.'}
torch.set_num_threads(CONFIG['threads'])

def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(t):
    t=unicodedata.normalize('NFKC',str(t)).casefold()
    t=re.sub(r'https?://\S+|www\.\S+|@[\w_]+',' ',t)
    return ' '.join(re.findall(r'\w+',t))
def wordcount(t):return len(re.findall(r"\b\w+(?:['’]\w+)*\b",str(t)))
def log(s):print(time.strftime('%H:%M:%S'),s,flush=True)
def seed(s):random.seed(s);np.random.seed(s);torch.manual_seed(s)
def frame(name):return pd.read_csv(OUT/name).fillna('')
def csv(name,x):pd.DataFrame(x).to_csv(OUT/name,index=False,encoding='utf-8-sig')

def prepare():
    if (OUT/'split_definitions.csv').exists():
        assert read('config.json')==CONFIG,'Frozen config mismatch'
        log('Using frozen split');return
    OUT.mkdir(parents=True,exist_ok=True)
    dump('config.json',CONFIG)
    frames=[];hashes={}
    for source in ['twitter','telegram']:
        p=ROOT/f'data/raw/{source}_natural_dataset.csv';hashes[str(p.relative_to(ROOT))]=sha(p)
        f=pd.read_csv(p).fillna('');f['source']=source
        f['row_id']=[f'{source}:{i+1}' for i in range(len(f))]
        # Case aliases cannot be treated as disjoint authors.
        f['author']=f.account.str.removeprefix('@').str.casefold()
        frames.append(f)
    x=pd.concat(frames,ignore_index=True)
    x['canonical']=x.text.map(canon);x['word_count']=x.text.map(wordcount)
    audit=pd.read_csv(ROOT/'artifacts/research_author_style_language/text_language_and_style.csv')
    language=audit.set_index('row_id')
    x['english_candidate']=x.row_id.map(language.language_candidate).eq('en')
    # Verify language cache against current text, not row ID alone.
    assert all(hashlib.sha256(t.encode()).hexdigest()==language.loc[r,'text_sha256'] for r,t in zip(x.row_id,x.text))
    log('Global exact/near-duplicate clustering before sampling')
    uf=UnionFind(len(x));exact={}
    for i,t in enumerate(x.canonical):
        if t in exact:uf.union(i,exact[t])
        else:exact[t]=i
    shingles=[get_shingles(t) for t in x.canonical]
    candidates=lsh_candidate_pairs(build_minhash_signatures(shingles))
    near=0
    for i,j in candidates:
        if jaccard(shingles[i],shingles[j])>=.7:uf.union(i,j);near+=1
    x['duplicate_cluster']=[uf.find(i) for i in range(len(x))]
    x['rank']=x.row_id.map(lambda s:hashlib.sha256(('sample:'+s).encode()).hexdigest())
    # One global representative prevents a shared duplicate cluster crossing any split.
    eligible=x[x.english_candidate & x.word_count.between(CONFIG['min_words'],CONFIG['max_words'])].sort_values('rank').drop_duplicates('duplicate_cluster')
    chosen=[];author_rows=[]
    for label in LABELS:
        g=eligible[eligible.narrative_name==label]
        counts=g.author.value_counts();authors=sorted(counts[counts>=CONFIG['texts_per_author']].index)
        rng=random.Random(str(CONFIG['split_seed'])+label);rng.shuffle(authors)
        assert len(authors)>=4,(label,len(authors))
        for ai,author in enumerate(authors[:4]):
            split='train' if ai<2 else 'val' if ai==2 else 'test'
            a=g[g.author==author].head(CONFIG['texts_per_author']).copy();a['split']=split
            chosen.append(a);author_rows.append({'author':author,'narrative':label,'split':split,'n':len(a)})
    selected=pd.concat(chosen,ignore_index=True)
    # Exhaustive lexical verification within pilot, beyond probabilistic LSH candidates.
    conflicts=[]
    for i,j in itertools.combinations(range(len(selected)),2):
        a,b=selected.iloc[i],selected.iloc[j]
        if a.split==b.split:continue
        sim=jaccard(get_shingles(a.canonical),get_shingles(b.canonical))
        if sim>=.7:conflicts.append((a.row_id,b.row_id,sim))
    assert not conflicts,conflicts[:5]
    assert not set(selected[selected.split=='train'].author)&set(selected[selected.split=='test'].author)
    selected['label']=selected.narrative_name.map(LABELS.index)
    csv('split_definitions.csv',selected.drop(columns=['rank','english_candidate']))
    csv('author_splits.csv',author_rows)
    dump('split_audit.json',{'source_hashes':hashes,'original_checkpoint_sha256':sha(ROOT/'models/best_model_sbert_only.pth'),
        'raw_rows':len(x),'eligible_rows':len(eligible),'pilot_rows':len(selected),
        'global_duplicate_clusters':x.duplicate_cluster.nunique(),'verified_near_pairs':near,
        'cross_split_lexical_duplicate_pairs':conflicts,'author_disjoint':True,
        'limitation':'Exact normalization plus MinHash candidate Jaccard >= .7 and exhaustive pilot word-trigram Jaccard; semantic paraphrases require additional embedding audit. No universal guarantee against all semantic variants.'})
    csv('counterfactual_selection.csv',selected[selected.split=='test'].groupby('narrative_name',sort=False).head(2)[['row_id']])
    dump('environment.json',{'python':sys.version,'torch':torch.__version__,'cuda':torch.cuda.is_available(),'created':'2026-10-26'})
    log(f'Frozen pilot: {len(selected)} texts, {selected.author.nunique()} authors')

def encoder():
    from sentence_transformers import SentenceTransformer
    e=SentenceTransformer(CONFIG['encoder'],local_files_only=True,device='cpu')
    state=torch.load(ROOT/'models/best_model_sbert_only.pth',map_location='cpu',weights_only=True)
    e.load_state_dict({k[6:]:v for k,v in state.items() if k.startswith('sbert.')},strict=True)
    return e
def embed(texts,e):return e.encode(list(texts),batch_size=32,convert_to_numpy=True,show_progress_bar=False)
def head():return torch.nn.Sequential(torch.nn.Linear(384,128),torch.nn.ReLU(),torch.nn.Dropout(.3),torch.nn.Linear(128,7))
def probs(h,z):
    h.eval()
    with torch.no_grad():return torch.softmax(h(torch.as_tensor(z,dtype=torch.float32)),dim=1).numpy()
def metrics(y,p):
    if not len(y):return {'n':0,'macro_f1':None,'accuracy':None}
    y=np.asarray(y,dtype=int);pred=p.argmax(1)
    recalls=recall_score(y,pred,labels=range(7),average=None,zero_division=0)
    return {'n':len(y),'accuracy':accuracy_score(y,pred),'macro_f1':f1_score(y,pred,labels=range(7),average='macro',zero_division=0),
        'nll':log_loss(y,p,labels=range(7)), 'brier':float(np.mean(np.sum((p-np.eye(7)[y])**2,axis=1))),
        **{f'recall_{n}':v for n,v in zip(LABELS,recalls)}}
def train(z,y,splits,s,tag):
    seed(s);h=head();optimizer=torch.optim.Adam(h.parameters(),lr=CONFIG['lr'])
    train_idx=np.where(splits=='train')[0];val_idx=np.where(splits=='val')[0]
    assert len(train_idx) and len(val_idx),'No matched training/validation data'
    best=-1;beststate=None;history=[]
    # Fixed epoch budget for all arms; select checkpoint on validation macro-F1 only.
    for epoch in range(CONFIG['epochs']):
        h.train();order=np.random.permutation(train_idx)
        for start in range(0,len(order),CONFIG['batch_size']):
            ix=order[start:start+CONFIG['batch_size']]
            optimizer.zero_grad();loss=torch.nn.functional.cross_entropy(h(torch.tensor(z[ix],dtype=torch.float32)),torch.tensor(y[ix],dtype=torch.long));loss.backward();optimizer.step()
        val=metrics(y[val_idx],probs(h,z[val_idx]));history.append({'epoch':epoch+1,**val})
        if val['macro_f1']>best:
            best=val['macro_f1'];beststate={k:v.detach().clone() for k,v in h.state_dict().items()}
    h.load_state_dict(beststate)
    (OUT/'checkpoints').mkdir(exist_ok=True)
    torch.save(beststate,OUT/'checkpoints'/f'{tag}_seed{s}.pt');dump(f'training_history_{tag}_seed{s}.json',history)
    return h

def baseline():
    if (OUT/'baseline_metrics.json').exists():return
    x=frame('split_definitions.csv');e=encoder();z=embed(x.text,e);np.save(OUT/'embeddings_Original.npy',z)
    # Semantic near-duplicate removal is checked before any baseline result is accepted.
    zn=z/np.linalg.norm(z,axis=1,keepdims=True);sims=zn@zn.T
    suspicious=[]
    for i,j in itertools.combinations(range(len(x)),2):
        if x.iloc[i].split!=x.iloc[j].split and sims[i,j]>=.97:
            suspicious.append({'row_a':x.iloc[i].row_id,'row_b':x.iloc[j].row_id,'cosine':float(sims[i,j])})
    dump('cross_split_semantic_candidates.json',suspicious)
    # Deterministically drop all members of high-similarity cross-split pairs, not just test.
    bad={r[k] for r in suspicious for k in ['row_a','row_b']}
    x['semantic_duplicate_excluded']=x.row_id.isin(bad)
    csv('split_definitions.csv',x)
    active=~x.semantic_duplicate_excluded
    csv('analysis_cohort.csv',x[active])
    y=x.label.to_numpy(int);split=x.split.to_numpy()
    results=[];pred=[]
    for s in SEEDS:
        h=train(z[active],y[active],split[active],s,'baseline_original')
        mask=(split=='test')&active.to_numpy();p=probs(h,z[mask]);results.append({'seed':s,**metrics(y[mask],p)})
        for row,pp in zip(x[mask].itertuples(),p):pred.append({'row_id':row.row_id,'author':row.author,'narrative':row.narrative_name,'label':row.label,'seed':s,'predicted':LABELS[pp.argmax()],'true_probability':pp[row.label],'max_probability':pp.max()})
    csv('baseline_predictions.csv',pred);dump('baseline_metrics.json',results)
    log('Author-disjoint baseline complete')

COMMON='Preserve all facts, named entities, claims, negation, certainty, attribution, political stance and framing. Do not add or remove claims. Do not explain, judge, correct, summarize, or name a narrative. Return only the rewritten text, without a preface.'
PROMPTS={
 'Paraphrase':COMMON+' Paraphrase the text while preserving its original writing style, tone, emotional intensity, point of view, rhetorical devices and level of formality. Keep approximately the same length.',
 'Normalized':COMMON+' Rewrite in uniform plain written English: straightforward complete sentences, standard punctuation, consistent moderately formal wording, no decorative formatting. Preserve evaluative wording and the strength of the position; do not make the politics neutral. Keep approximately the same length.',
 'Formal':COMMON+' Use a formal written register. Keep approximately the same length.',
 'Conversational':COMMON+' Use natural conversational English without adding opinions. Keep approximately the same length.',
 'Concise':COMMON+' Use concise short sentences without dropping any claim.',
 'Elaborate':COMMON+' Use more explicit sentence connections, without adding facts, explanations, opinions or claims.',
 'StanceChanged':'Create a controlled research contrast. Change the main evaluative stance toward the principal actor or policy to the opposing stance, while preserving names, factual event descriptions, length and writing style as far as possible. Do not invent events. Return only the changed text.'}

def generate():
    import concurrent.futures
    import urllib.request
    import subprocess
    x=frame('analysis_cohort.csv');cf=set(frame('counterfactual_selection.csv').row_id)
    contrast=set(x[(x.split=='test')&x.row_id.isin(cf)].groupby('narrative_name').head(1).row_id)
    tasks=[]
    for row in x.itertuples():
        for condition in ['Paraphrase','Normalized']+(['Formal','Conversational','Concise','Elaborate'] if row.row_id in cf else [])+(['StanceChanged'] if row.row_id in contrast else []):
            tasks.append({'row_id':row.row_id,'condition':condition,'original':row.text})
    dump('prompts.json',{'common':COMMON,'conditions':PROMPTS,'author_and_gold_label_sent':False,'prompt_inputs':'instruction plus text only; metadata excluded'})
    path=OUT/'generated_rewrites.jsonl';done=[]
    if path.exists():done=[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
    existing={(r['row_id'],r['condition']) for r in done}
    formatting=[{'row_id':r.row_id,'condition':'Formatting','original':r.text,'rewrite':normalize_style(r.text),
                 'model':'project deterministic normalize_style','revision':'existing project implementation',
                 'truncated':False,'batch_seconds':0.} for r in x.itertuples() if (r.row_id,'Formatting') not in existing]
    if formatting:
        with path.open('a',encoding='utf-8') as out:
            for r in formatting:out.write(json.dumps(r,ensure_ascii=False)+'\n')
        done.extend(formatting)
    keys={(r['row_id'],r['condition']) for r in done};tasks=[r for r in tasks if (r['row_id'],r['condition']) not in keys]
    # Once style variants exist, normalize each of them in a separate, resumable pass.
    if not tasks:
        tasks=[{'row_id':r['row_id'],'condition':'Normalized'+r['condition'],'original':r['rewrite'],'source_style':r['condition']}
               for r in done if r['condition'] in ['Formal','Conversational','Concise','Elaborate']
               and (r['row_id'],'Normalized'+r['condition']) not in keys]
    if not tasks:log('Generation already complete');return
    revision=read('generator_revision.json')['revision']
    runtime=OUT/'runtime_llama';manifest=read('llama_runtime_manifest.json')
    endpoint='http://127.0.0.1:18091'
    try:
        with urllib.request.urlopen(endpoint+'/health',timeout=2) as response:assert response.status==200
    except Exception:
        executable=runtime/'llama-server.exe';model=runtime/manifest['file']
        subprocess.Popen([str(executable),'-m',str(model),'--host','127.0.0.1','--port','18091',
            '-t','4','-tb','4','-np','4','-c','4096','--no-webui'],
            stdout=(runtime/'server_stdout.log').open('a'),stderr=(runtime/'server_stderr.log').open('a'),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        for attempt in range(30):
            try:
                with urllib.request.urlopen(endpoint+'/health',timeout=2) as response:
                    if response.status==200:break
            except Exception:time.sleep(1)
        else:raise RuntimeError('Local CPU generation server did not become ready')
    def rewrite(r):
        instruction=PROMPTS['Normalized' if r['condition'].startswith('Normalized') else r['condition']]
        request={'messages':[{'role':'system','content':instruction},{'role':'user','content':r['original']}],
            'temperature':0,'seed':CONFIG['generation_seed'],'max_tokens':CONFIG['max_new_tokens'],
            'repeat_penalty':1.,'top_k':1,'top_p':1.,'min_p':0.,'cache_prompt':False}
        t=time.perf_counter()
        req=urllib.request.Request(endpoint+'/v1/chat/completions',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=180) as response:result=json.load(response)
        choice=result['choices'][0]
        return {**r,'rewrite':choice['message']['content'].strip(),'model':GEN_MODEL,'revision':revision,
            'quantization':CONFIG['generator_quantization'],'engine_release':manifest['release'],
            'truncated':choice['finish_reason']=='length','seconds':time.perf_counter()-t,
            'usage':result.get('usage'),'timings':result.get('timings')}
    log(f'Generating {len(tasks)} rewrites with pinned local LLM')
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG['generation_batch_size']) as pool,path.open('a',encoding='utf-8') as out:
        # map preserves frozen task order despite concurrent local requests.
        for count,record in enumerate(pool.map(rewrite,tasks),1):
            out.write(json.dumps(record,ensure_ascii=False)+'\n');out.flush()
            if count%16==0 or count==len(tasks):log(f'Generated {count}/{len(tasks)}')

NEG={'no','not','never','neither','nor','without',"isn't","wasn't","don't","doesn't","didn't","can't","cannot","won't","wouldn't","shouldn't","hasn't","haven't"}
CERT={'may','might','could','possibly','probably','allegedly','reportedly','apparently','certainly','definitely','must'}
ATTR={'said','says','claimed','claims','according','reported','reports','alleged','alleges','stated','states','quoted','quotes'}
FRAME={'terrorist','terrorists','occupation','occupiers','invasion','aggression','aggressor','illegal','legitimate','illegitimate','liberation','resistance','genocide','murder','murdered','victim','victims','hero','heroes','criminal','criminals','corrupt','dictator','dictatorship','sovereignty','freedom','oppression','oppressed'}
def words(t):return set(re.findall(r"\b[a-z]+(?:['’][a-z]+)*\b",t.lower().replace('’',"'")))

def validate():
    if (OUT/'rewrite_validation.csv').exists():return
    from transformers import pipeline,AutoTokenizer,AutoModelForSequenceClassification
    rows=[json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
    from sentence_transformers import SentenceTransformer
    e=SentenceTransformer(CONFIG['semantic_validation_encoder'],revision=SEMANTIC_REVISION,local_files_only=True,device='cpu')
    texts=[r['original'] for r in rows]+[r['rewrite'] for r in rows]
    unique_texts=list(dict.fromkeys(texts));positions={t:i for i,t in enumerate(unique_texts)}
    log(f'Semantic encoding {len(unique_texts)} unique texts instead of {len(texts)} repeated inputs')
    vectors=embed(unique_texts,e)
    original=vectors[[positions[r['original']] for r in rows]];rewritten=vectors[[positions[r['rewrite']] for r in rows]]
    similarity=(original*rewritten).sum(1)/(np.linalg.norm(original,axis=1)*np.linalg.norm(rewritten,axis=1))
    del e;gc.collect()
    from transformers import AutoModelForTokenClassification
    ner_name='dslim/bert-base-NER'
    ner=pipeline('token-classification',model=AutoModelForTokenClassification.from_pretrained(ner_name,revision=NER_REVISION,local_files_only=True),tokenizer=AutoTokenizer.from_pretrained(ner_name,revision=NER_REVISION,local_files_only=True),aggregation_strategy='simple',device=-1)
    log('Extracting named entities for semantic checks')
    ents=ner(unique_texts,batch_size=16)
    def names(es):return {canon(en['word'].replace(' ##','').replace('##','')) for en in es if en['score']>=.8 and en['entity_group'] in {'PER','ORG','LOC'} and canon(en['word'])}
    unique_entity_sets=[names(es) for es in ents]
    entity_sets=[unique_entity_sets[positions[t]] for t in texts]
    del ner;gc.collect()
    name='MoritzLaurer/deberta-v3-large-zeroshot-v2.0'
    tokenizer=AutoTokenizer.from_pretrained(name,revision=NLI_REVISION,local_files_only=True)
    nli=AutoModelForSequenceClassification.from_pretrained(name,revision=NLI_REVISION,local_files_only=True,dtype=torch.float32);nli.eval()
    ent_idx=next(int(i) for i,label in nli.config.id2label.items() if label=='entailment')
    premises=[];hypotheses=[]
    for r in rows:
        premises.extend([r['original'],r['rewrite']]);hypotheses.extend([r['rewrite'],r['original']])
    all_pairs=list(zip(premises,hypotheses));unique_pairs=list(dict.fromkeys(all_pairs))
    pair_positions={pair:i for i,pair in enumerate(unique_pairs)}
    premises=[p for p,h in unique_pairs];hypotheses=[h for p,h in unique_pairs]
    dump('validation_exact_input_memoization.json',{'text_inputs':len(texts),'unique_text_inputs':len(unique_texts),
        'nli_ordered_pair_inputs':len(all_pairs),'unique_ordered_nli_pairs':len(unique_pairs),
        'method':'Exact input memoization only; no rewritten text or validation threshold changed; identical inputs share one model evaluation.'})
    signature=sha(OUT/'generated_rewrites.jsonl')
    score_path=OUT/'nli_scores_progress.json'
    cached=read('nli_scores_progress.json') if score_path.exists() else {}
    scores=cached.get('scores',[]) if cached.get('generation_sha256')==signature else []
    assert len(scores)%8==0 or len(scores)==len(premises)
    for start in range(len(scores),len(premises),8):
        batch=tokenizer(premises[start:start+8],hypotheses[start:start+8],padding=True,truncation=True,max_length=384,return_tensors='pt')
        with torch.inference_mode():p=torch.softmax(nli(**batch).logits,dim=1)[:,ent_idx].tolist()
        scores.extend(p)
        dump('nli_scores_progress.json',{'generation_sha256':signature,'scores':scores})
        if start%160==0:log(f'Bidirectional NLI {start}/{len(premises)}')
    dump('validation_method.json',{'nli_model':name,'nli_revision':NLI_REVISION,'ner_revision':NER_REVISION,'id2label':nli.config.id2label,'entailment_index':ent_idx,
      'semantic_model':CONFIG['semantic_validation_encoder'],'semantic_revision':SEMANTIC_REVISION,'ner':'dslim/bert-base-NER','thresholds':CONFIG,
      'stance_framing_check':'Conservative lexical guardrails plus bidirectional NLI, not independent stance/framing proof.',
      'human_validation_performed':False,'validation_score':'minimum of cosine similarity, forward/reverse entailment and entity recall/precision; structural flags additionally gate acceptance'})
    scores=[scores[pair_positions[pair]] for pair in all_pairs]
    results=[]
    for i,r in enumerate(rows):
        a,b=words(r['original']),words(r['rewrite']);ea,eb=entity_sets[i],entity_sets[i+len(rows)]
        er=len(ea&eb)/len(ea) if ea else 1.;ep=len(ea&eb)/len(eb) if eb else 1.
        nums=lambda t:set(re.findall(r'\b\d+(?:[.,]\d+)*\b',t))
        flags={'entities_preserved':er>=1 and ep>=1,'numbers_preserved':nums(r['original'])==nums(r['rewrite']),
               'negation_guard':(a&NEG)==(b&NEG),'certainty_guard':(a&CERT)==(b&CERT),
               'attribution_guard':bool(a&ATTR)==bool(b&ATTR),'framing_anchor_guard':(a&FRAME)==(b&FRAME),
               'length_guard':.60<=wordcount(r['rewrite'])/max(1,wordcount(r['original']))<=1.65,
               'complete_output':not r['truncated'] and bool(r['rewrite'])}
        forward,reverse=scores[2*i:2*i+2]
        reasons=[k for k,v in flags.items() if not v]
        if similarity[i]<CONFIG['similarity_threshold']:reasons.append('semantic_similarity')
        if min(forward,reverse)<CONFIG['bidirectional_entailment_threshold']:reasons.append('bidirectional_NLI_claim_change_risk')
        style_changed=canon(r['original'])!=canon(r['rewrite'])
        results.append({'row_id':r['row_id'],'condition':r['condition'],'semantic_similarity':similarity[i],
          'entailment_original_to_rewrite':forward,'entailment_rewrite_to_original':reverse,
          'added_claim_risk':forward<.6,'removed_claim_risk':reverse<.6,
          'original_entities':json.dumps(sorted(ea)),'rewrite_entities':json.dumps(sorted(eb)),
          'entity_recall':er,'entity_precision':ep,**flags,'validation_score':min(float(similarity[i]),forward,reverse,er,ep),
          'passed':not reasons,'rejection_reasons':'|'.join(reasons),'changed_text':style_changed,
          'raw_text_changed':r['original']!=r['rewrite'],'canonical_word_sequence_changed':style_changed,
          'surface_style_distance':float(np.linalg.norm(np.array(style_features(r['original']))-np.array(style_features(r['rewrite'])))),
          'stance_preservation':'automated_screen_only','framing_preservation':'automated_screen_only','human_verified':False})
    csv('rewrite_validation.csv',results)
    log('Validation complete')

def transitions(y,base,p):
    correct=base.argmax(1)==y;after=p.argmax(1)==y
    return {'label_flip_rate':float(np.mean(base.argmax(1)!=p.argmax(1))),
      'label_flips':int(np.sum(base.argmax(1)!=p.argmax(1))),
      'original_correct':int(correct.sum()),'after_correct':int(after.sum()),
      'correct_to_incorrect':int(np.sum(correct&~after)),'incorrect_to_correct':int(np.sum(~correct&after)),
      'true_probability_delta':float(np.mean(p[np.arange(len(y)),y]-base[np.arange(len(y)),y])),
      'max_probability_delta':float(np.mean(p.max(1)-base.max(1)))}
def style_features(t):
    w=re.findall(r'\b\w+\b',t);n=max(len(w),1);sent=max(1,len([s for s in re.split(r'[.!?]+',t) if s.strip()]))
    return [len(t),len(w),len(w)/sent,sum(c.isupper() for c in t)/max(1,sum(c.isalpha() for c in t)),
      *[100*t.count(c)/n for c in ['?', '!', ',', ';', ':','\n']],np.mean([len(v) for v in w]) if w else 0]

def evaluate():
    if (OUT/'evaluation_complete.json').exists():return
    x=frame('analysis_cohort.csv');v=frame('rewrite_validation.csv');generated=[json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
    lookup={(r['row_id'],r['condition']):r['rewrite'] for r in generated}
    passed={(r.row_id,r.condition):str(r.passed).lower()=='true' for r in v.itertuples()}
    e=encoder();allz={};alltexts={}
    for cond in ['Original','Formatting','Paraphrase','Normalized']:
        ts=[t if cond=='Original' else normalize_style(t) if cond=='Formatting' else lookup[(rid,cond)] for rid,t in zip(x.row_id,x.text)]
        alltexts[cond]=ts;allz[cond]=embed(ts,e);np.save(OUT/f'embeddings_{cond}_analysis.npy',allz[cond])
    csv('text_variants.csv',[{'row_id':row.row_id,'author':row.author,'split':row.split,
        'narrative':row.narrative_name,'condition':cond,'text':alltexts[cond][i]}
        for i,row in enumerate(x.itertuples()) for cond in alltexts])
    feature_names=['characters','words','words_per_sentence','uppercase_fraction',
        'questions_per_100_words','exclamations_per_100_words','commas_per_100_words',
        'semicolons_per_100_words','colons_per_100_words','newlines_per_100_words','mean_word_length']
    csv('surface_style_measurements.csv',[{'row_id':row.row_id,'author':row.author,'split':row.split,
        'narrative':row.narrative_name,'condition':cond,
        **dict(zip(feature_names,style_features(alltexts[cond][i])))}
        for i,row in enumerate(x.itertuples()) for cond in alltexts])
    # Recheck generator-induced duplicate/near-duplicate leakage across splits.
    leaks=[];excluded=set();probe_duplicate_sources=set()
    conditions=list(alltexts);variants=[(i,c,canon(t)) for c in conditions for i,t in enumerate(alltexts[c])]
    sh=[get_shingles(t) for _,_,t in variants]
    z=np.concatenate([allz[c] for c in conditions]);zn=z/np.maximum(np.linalg.norm(z,axis=1,keepdims=True),1e-12)
    similarity=zn@zn.T;source_splits=x.split.to_numpy();row_ids=x.row_id.to_numpy()
    # Includes Original-train versus Normalized-test and every other cross-arm pairing.
    # The same source record in two arms is intentional and is never called leakage.
    for a,b in itertools.combinations(range(len(variants)),2):
        i,ca,ta=variants[a];j,cb,tb=variants[b]
        if i==j:continue
        if ta==tb or similarity[a,b]>=.97 or jaccard(sh[a],sh[b])>=.7:
            probe_duplicate_sources.update([row_ids[i],row_ids[j]])
            if source_splits[i]!=source_splits[j]:
                leaks.append({'condition':ca+' -> '+cb,'row_a':row_ids[i],'row_b':row_ids[j],'cosine':float(similarity[a,b])})
                excluded.update([row_ids[i],row_ids[j]])
    csv('author_probe_duplicate_exclusions.csv',[{'row_id':rid,'excluded':rid in probe_duplicate_sources} for rid in row_ids])
    csv('generated_cross_split_duplicate_candidates.csv',leaks or [{'condition':'none','row_a':'','row_b':'','cosine':0}])
    common=np.array([passed[(rid,'Paraphrase')] and passed[(rid,'Normalized')] and rid not in excluded for rid in x.row_id])
    formatting_pass=np.array([passed[(rid,'Formatting')] for rid in x.row_id])
    csv('matched_cohort.csv',[{'row_id':rid,'included':bool(ok),
        'included_for_four_way_fixed':bool(ok and passed[(rid,'Formatting')]),
        'generated_duplicate_excluded':rid in excluded} for rid,ok in zip(x.row_id,common)])
    rows=[];predictions=[];perauthor=[];y=x.label.to_numpy(int);splits=x.split.to_numpy();test=splits=='test'
    def savepred(scope,s,traincond,testcond,mask,p,base=None):
        yy=y[mask];m={'scope':scope,'seed':s,'train_condition':traincond,'test_condition':testcond,**metrics(yy,p)}
        if base is not None and len(yy):m.update(transitions(yy,base,p))
        rows.append(m)
        for row,pp in zip(x[mask].itertuples(),p):
            predictions.append({'scope':scope,'seed':s,'train_condition':traincond,'test_condition':testcond,
              'row_id':row.row_id,'author':row.author,'true_label':row.label,'predicted_label':int(pp.argmax()),
              'max_probability':pp.max(),'true_probability':pp[row.label],**{f'p_{n}':pp[j] for j,n in enumerate(LABELS)}})
        for a in x[mask].author.unique():
            select=x[mask].author.to_numpy()==a
            pm=metrics(yy[select],p[select]);label=int(yy[select][0])
            perauthor.append({'scope':scope,'seed':s,'train_condition':traincond,'test_condition':testcond,
                'author':a,'source_narrative':LABELS[label],'n':int(select.sum()),
                'accuracy':pm['accuracy'],'recall_for_source_narrative':pm['accuracy'],
                'mean_source_label_probability':float(p[select,label].mean()),'nll':pm['nll'],'brier':pm['brier']})
    # Existing checkpoint is descriptive only: it is not author-disjoint.
    deployed=head();state=torch.load(ROOT/'models/best_model_sbert_only.pth',map_location='cpu',weights_only=True)
    deployed.load_state_dict({k[4:]:t for k,t in state.items() if k.startswith('mlp.')})
    eligible_test=test&np.array([rid not in excluded for rid in x.row_id])
    for cond in allz:
        savepred('existing_deployed_overlap_not_disjoint',-1,'Existing',cond,eligible_test,probs(deployed,allz[cond][eligible_test]),probs(deployed,allz['Original'][eligible_test]))
    for s in SEEDS:
        h=head();h.load_state_dict(torch.load(OUT/'checkpoints'/f'baseline_original_seed{s}.pt',weights_only=True))
        for cohort,mask in [('all_generated_descriptive',eligible_test),('matched_automated_pass',test&common&formatting_pass)]:
            if not mask.any():continue
            base=probs(h,allz['Original'][mask])
            for cond in allz:savepred('fixed_'+cohort,s,'Original',cond,mask,probs(h,allz[cond][mask]),base)
        mask=test&common
        if mask.any():
            base=probs(h,allz['Original'][mask])
            for cond in ['Original','Paraphrase','Normalized']:
                savepred('fixed_matched_paraphrase_normalized',s,'Original',cond,mask,probs(h,allz[cond][mask]),base)
    primary_status={}
    # Refit original, paraphrase and normalized on exactly the same accepted rows.
    for cohort,keep in [('all_generated_descriptive',np.array([rid not in excluded for rid in x.row_id])),('matched_automated_pass',common)]:
        counts={split:np.bincount(y[keep&(splits==split)],minlength=7).tolist() for split in ['train','val','test']}
        valid=all(min(c)>0 for c in counts.values())
        primary_status[cohort]={'counts':counts,'all_labels_in_each_split':valid}
        if not valid:continue
        for s in SEEDS:
            for tr in ['Original','Paraphrase','Normalized']:
                h=train(allz[tr][keep],y[keep],splits[keep],s,cohort+'_'+tr)
                for te in ['Original','Paraphrase','Normalized']:
                    mask=test&keep;savepred('retrain_'+cohort,s,tr,te,mask,probs(h,allz[te][mask]))
    csv('metrics_summary.csv',rows);csv('fixed_and_retrained_predictions.csv',predictions);csv('per_author_metrics.csv',perauthor)
    dump('retraining_cohort_status.json',primary_status)
    # Closed-set author probes: same authors in train/test, different texts; retrain each arm.
    probe=[];probe_splits=[];probe_predictions=[]
    probe_keep=np.array([rid not in probe_duplicate_sources for rid in x.row_id])
    for cohort,keep in [('all_generated_descriptive',probe_keep),('matched_automated_pass',common&probe_keep)]:
        for narrative in LABELS:
            ix=np.where(keep&(x.narrative_name.to_numpy()==narrative))[0]
            groups={a:[i for i in ix if x.iloc[i].author==a] for a in x.iloc[ix].author.unique()}
            groups={a:sorted(ii,key=lambda i:x.iloc[i].row_id) for a,ii in groups.items() if len(ii)>=4}
            if len(groups)<2:continue
            author_names=sorted(groups);tr=[];te=[]
            for a,ii in groups.items():
                n=max(1,round(len(ii)*.3));te+=ii[:n];tr+=ii[n:]
            for i in tr+te:probe_splits.append({'cohort':cohort,'narrative':narrative,'row_id':x.iloc[i].row_id,'author':x.iloc[i].author,'split':'train' if i in tr else 'test'})
            for cond in ['Original','Paraphrase','Normalized']:
                for representation,z in [('embedding',allz[cond]),('surface_style',np.array([style_features(t) for t in alltexts[cond]]))]:
                    yy=x.author.to_numpy();model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,random_state=42))
                    model.fit(z[tr],yy[tr]);pp=model.predict(z[te])
                    probe_predictions.extend({'cohort':cohort,'narrative':narrative,'condition':cond,
                        'representation':representation,'row_id':x.iloc[i].row_id,'true_author':yy[i],
                        'predicted_author':p,'correct':bool(yy[i]==p)} for i,p in zip(te,pp))
                    probe.append({'cohort':cohort,'narrative':narrative,'condition':cond,'representation':representation,'n_authors':len(groups),'n_train':len(tr),'n_test':len(te),
                        'accuracy':accuracy_score(yy[te],pp),'macro_f1':f1_score(yy[te],pp,average='macro',zero_division=0),'balanced_chance':1/len(groups)})
    csv('author_probe_results.csv',probe);csv('author_probe_splits.csv',probe_splits)
    csv('author_probe_predictions.csv',probe_predictions)
    # Crossed style targets on unseen-author originals and after normalization.
    cfrows=[];contrastrows=[]
    for s in SEEDS:
        h=head();h.load_state_dict(torch.load(OUT/'checkpoints'/f'baseline_original_seed{s}.pt',weights_only=True))
        taskrows=[r for r in generated if r['condition'] in ['Formal','Conversational','Concise','Elaborate','StanceChanged','NormalizedFormal','NormalizedConversational','NormalizedConcise','NormalizedElaborate']]
        z=embed([r['rewrite'] for r in taskrows],e);pp=probs(h,z)
        for r,p in zip(taskrows,pp):
            ix=int(np.where(x.row_id.to_numpy()==r['row_id'])[0][0])
            chain=r['condition'].startswith('Normalized')
            base=probs(h,allz['Normalized' if chain else 'Original'][ix:ix+1])[0]
            accepted=passed[(r['row_id'],r['condition'])]
            if chain:accepted=accepted and passed[(r['row_id'],r['source_style'])] and passed[(r['row_id'],'Normalized')]
            result={'seed':s,'row_id':r['row_id'],'author':x.iloc[ix].author,'style':r['condition'],
                'after_normalization':chain,'passed_semantic_preservation_screen':accepted,
                'original_label':int(base.argmax()),'variant_label':int(p.argmax()),
                'label_flip':bool(base.argmax()!=p.argmax()),
                'correct_to_incorrect':bool(base.argmax()==y[ix] and p.argmax()!=y[ix]) if r['condition']!='StanceChanged' else None,
                'incorrect_to_correct':bool(base.argmax()!=y[ix] and p.argmax()==y[ix]) if r['condition']!='StanceChanged' else None,
                'max_probability_delta':float(p.max()-base.max()),'original_stance_label_valid_for_variant':r['condition']!='StanceChanged',
                'true_probability_delta':float(p[y[ix]]-base[y[ix]]) if r['condition']!='StanceChanged' else None}
            (contrastrows if r['condition']=='StanceChanged' else cfrows).append(result)
    csv('counterfactual_results.csv',cfrows);csv('stance_change_control_results.csv',contrastrows)
    # Stance changes have no automatically established new 7-way gold labels.
    dump('evaluation_complete.json',{'matched_rows':int(common.sum()),'matched_test_rows':int((common&test).sum()),
        'fixed_four_way_matched_test_rows':int((common&test&formatting_pass).sum()),
        'generated_duplicate_excluded':len(excluded),'primary_comparison_estimable':primary_status.get('matched_automated_pass',{}).get('all_labels_in_each_split',False),
        'stance_control_new_gold_labels':False,'causal_claim_supported':False})
    log('Evaluation complete')

def report():
    import importlib.metadata
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dump('dependency_versions.json',{name:importlib.metadata.version(name) for name in
        ['numpy','pandas','torch','transformers','sentence-transformers','scikit-learn','matplotlib','huggingface-hub']})
    environment=read('environment.json');environment['python_executable']=sys.executable;dump('environment.json',environment)
    m=frame('metrics_summary.csv');v=frame('rewrite_validation.csv');x=frame('analysis_cohort.csv')
    aggregate=m.groupby(['scope','train_condition','test_condition'])[['macro_f1','accuracy','nll','brier']].agg(['mean','std']).reset_index()
    aggregate.columns=['_'.join(t).rstrip('_') if isinstance(t,tuple) else t for t in aggregate.columns];csv('metrics_aggregated.csv',aggregate)
    failure=v.merge(x[['row_id','author','narrative_name','split']],on='row_id')
    failure['passed']=failure.passed.astype(str).str.lower().eq('true')
    rates=failure.groupby(['condition','split']).passed.agg(['count','mean']).reset_index();rates['failure_rate']=1-rates['mean'];csv('validation_failure_rates.csv',rates)
    csv('validation_failure_by_author.csv',failure.groupby(['condition','author']).passed.agg(['count','mean']).reset_index())
    csv('validation_failure_by_narrative.csv',failure.groupby(['condition','narrative_name']).passed.agg(['count','mean']).reset_index())
    selected=aggregate[aggregate.scope.eq('retrain_all_generated_descriptive') & (aggregate.train_condition==aggregate.test_condition)]
    if len(selected):
        fig,ax=plt.subplots(figsize=(7,4));ax.bar(selected.train_condition,selected.macro_f1_mean,yerr=selected.macro_f1_std.fillna(0));ax.set_ylabel('Macro-F1');ax.set_title('Unvalidated generated cohort: descriptive only');fig.tight_layout();fig.savefig(OUT/'narrative_performance.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4));rr=rates[rates.split=='test'];ax.bar(rr.condition,rr.failure_rate);ax.set_ylabel('Automated screening failure rate');ax.tick_params(axis='x',rotation=35);fig.tight_layout();fig.savefig(OUT/'rewrite_failures.png',dpi=160);plt.close(fig)
    info=read('evaluation_complete.json');baseline_results=read('baseline_metrics.json')
    summary={'baseline':baseline_results,'evaluation':info,'automated_validation_failure_rates':rates.to_dict('records')}
    dump('results_summary.json',summary)
    lines=['# Author Style Controlled Experiment — executed CPU pilot','',
      'This is an executed exploratory pilot, not an independent confirmatory study. Original data and checkpoint hashes are recorded in split_audit.json.',
      '',f'## Executed\n\n{x.author.nunique()} account-author identifiers; {len(x)} texts after original semantic-duplicate exclusions; three training seeds. Four primary conditions; local pinned LLM generation; bidirectional NLI, NER, numeric/negation/certainty/framing-anchor checks; author-disjoint narrative evaluation; independently refitted closed-set within-narrative author probes; crossed counterfactual styles and stance-change controls.',
      '',f'## Semantic screening\n\nMatched accepted rows: {info["matched_rows"]}; test: {info["matched_test_rows"]}. Full seven-label primary comparison estimable: {info["primary_comparison_estimable"]}. Automated checks are not independent human verification. Failure rates are in validation_failure_rates.csv. Invalid rewrites are never silently called preserved semantics.',
      '', '## Results\n',pd.DataFrame(baseline_results).to_string(index=False),'',aggregate.to_string(index=False),
      '', '## Interpretation\n\nThe all_generated_descriptive cohort includes rejected outputs and cannot establish a benefit from style-only intervention. The matched cohort, when estimable, is conditional on automated acceptance and still lacks human semantic gold validation. Same-account source labels are not independently annotated text narratives. StanceChanged is a manipulation attempt, not a verified seven-class narrative change; label flips alone do not demonstrate appropriate stance sensitivity.',
      '', '## Limitations\n\nSmall stratified pilot; only one test author per class; single author split; pre-existing author identities already explored in this repository; weak local 0.5B generator; one generation draw; lexical guards can reject harmless paraphrases and miss changed agency/stance; binary NLI is not a factuality or framing oracle; automatic language selection; account not necessarily individual writer; semantic-near-duplicate thresholds are operational, not a guarantee against every latent variant. Reported seed variability is training variability, not uncertainty over unseen authors.',
      '', '## Verdict\n\nStyle sensitivity: evaluate counterfactual_results.csv only among semantically accepted variants, with automated-only qualification. Author-information reduction: compare newly trained probes, not cross-domain probe transfer. Unseen-author benefit beyond paraphrase: interpret matched cohort only if all classes survive. Causality: NOT ESTABLISHED. LoRA/DoRA: not justified solely by this pilot; first improve generation/independent validation and enlarge untouched author evaluation.',
      '', '## Reproduce\n\nSee README.md. All outputs are isolated under this experiment directory. No original model was overwritten.']
    (OUT/'final_research_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (OUT/'README.md').write_text('''# Reproduce the controlled author-style pilot

From repository root, using the existing project Python and ML dependencies:

```
python experiments/author_generalization/author_style_controlled.py --stage prepare
python experiments/author_generalization/author_style_controlled.py --stage baseline
python experiments/author_generalization/author_style_controlled.py --stage generate
python experiments/author_generalization/author_style_controlled.py --stage generate
python experiments/author_generalization/author_style_controlled.py --stage validate
python experiments/author_generalization/author_style_controlled.py --stage evaluate
python experiments/author_generalization/author_style_controlled.py --stage report
```

Requires the pinned official Qwen GGUF generator and native llama.cpp CPU runtime (run prepare_llama_runtime.py first), and the project's cached MiniLM, MPNet, BERT-NER and DeBERTa NLI models. Inference is local; the generation server binds only to 127.0.0.1:18091. Posts are not sent to external inference services. Generation resumes from completed JSONL records; stages reuse their completed outputs. Delete only this experiment's relevant completion marker/output when intentionally rerunning a stage. Never overwrite original models/data.

Split, sampling, prompts, training settings and validation thresholds were fixed before intervention evaluation. CPU inference feasibility adjustments are recorded in generation_implementation_note.txt; rejected feasibility outputs are excluded from every analysis. Final configuration is retained. Author aliases are case-folded. Global duplicate-cluster representatives are selected before sampling. Cross-split semantic candidates and generated duplicates are excluded symmetrically. No test predictions select a rewrite. Labels/authors are never included as generation metadata, though named people naturally present in the original text are preserved.

The existing checkpoint supplies the frozen encoder and architecture; narrative heads are initialized anew for disjoint training. Existing deployed head is not used as a disjoint baseline. Adam lr .001, batch 16, 20 fixed epochs, hidden 128/dropout .3; best validation macro-F1 checkpoint. Same accepted source rows, seeds, epoch budget and split across retraining conditions. Each seed's checkpoints and predictions are retained. Seed standard deviations do not replace author-level inference.

Author probes deliberately have the same author identities in their own train/test, with disjoint texts, within each narrative; they are fitted anew per condition. Their split is separate from author-disjoint narrative evaluation. No human validation or independent revised narrative labels were invented. Rejected generations remain available and are reported separately.
''',encoding='utf-8')
    readme=OUT/'README.md'
    text=readme.read_text(encoding='utf-8')
    text=text.replace('```\npython experiments/',"```powershell\n$py = '"+sys.executable.replace('\\','/')+"'\n& $py experiments/")
    text=text.replace('\npython experiments/','\n& $py experiments/')
    text+='\nGenerator preparation when runtime_llama/ is absent (network required):\n\n```powershell\n& $py experiments/author_generalization/prepare_llama_runtime.py\n```\n\n'
    text+='Run generate twice: the second pass normalizes the four counterfactual styles. The `all` stage performs both passes automatically. Generation feasibility attempts are excluded from analysis; see generation_implementation_note.txt. Analyzed outputs use official GGUF Q8_0 weights with floating point activations and four concurrent local slots; runtime/model revisions and checksums are in llama_runtime_manifest.json. The runtime helper verifies the official archive checksum. Read final_research_report_he.md for the Hebrew report and integrity_audit.json for execution checks.\n'
    readme.write_text(text,encoding='utf-8')
    log('Reports and plots saved')
    from author_style_reporting import build
    build(OUT)
    audit_outputs()

def audit_outputs():
    x=frame('analysis_cohort.csv');definitions=frame('split_definitions.csv')
    assert definitions.groupby('author').split.nunique().max()==1
    assert x.groupby('author').split.nunique().max()==1
    assert all(LABELS[int(label)]==name for label,name in zip(x.label,x.narrative_name))
    provenance=read('split_audit.json')
    for relative,expected in provenance['source_hashes'].items():
        assert sha(ROOT/relative.replace('\\','/'))==expected,f'Source changed: {relative}'
    assert sha(ROOT/'models/best_model_sbert_only.pth')==provenance['original_checkpoint_sha256']
    generated=[json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
    keys=[(r['row_id'],r['condition']) for r in generated]
    assert len(keys)==len(set(keys)),'Repeated generation records'
    v=frame('rewrite_validation.csv')
    assert set(keys)==set(zip(v.row_id,v.condition)),'Missing validation records'
    variants=frame('text_variants.csv')
    assert len(variants)==4*len(x)
    assert variants.groupby('row_id').condition.nunique().eq(4).all()
    p=frame('fixed_and_retrained_predictions.csv')
    probability=p[[f'p_{label}' for label in LABELS]].to_numpy(float)
    assert np.isfinite(probability).all() and np.allclose(probability.sum(1),1,atol=1e-5)
    assert p.groupby(['scope','seed','train_condition','test_condition','row_id']).size().max()==1
    matched=frame('matched_cohort.csv')
    included=set(matched[matched.included.astype(str).str.lower().eq('true')].row_id)
    primary=p[p.scope.str.contains('matched_')]
    assert set(primary.row_id)<=included
    for s in SEEDS:
        for condition in ['Original','Formatting','Paraphrase','Normalized']:
            rows=p[(p.scope=='fixed_all_generated_descriptive')&(p.seed==s)&(p.test_condition==condition)]
            duplicate_free=set(matched[~matched.generated_duplicate_excluded.astype(str).str.lower().eq('true')].row_id)
            assert len(rows)==int((x.split.eq('test')&x.row_id.isin(duplicate_free)).sum())
    dump('integrity_audit.json',{'passed':True,'original_sources_unchanged':True,
        'original_checkpoint_unchanged':True,'author_disjoint_train_validation_test':True,
        'unique_generation_records':len(keys),'validated_generation_records':len(v),
        'four_variants_per_source_text':True,'prediction_probability_checks':True,
        'generated_file_sha256':sha(OUT/'generated_rewrites.jsonl'),
        'implementation_sha256':sha(Path(__file__)),
        'formatting_implementation_sha256':sha(ROOT/'src/narrative_lens/features/style_normalization.py'),
        'reporting_implementation_sha256':sha(Path(__file__).with_name('author_style_reporting.py')),
        'scope':'File and execution integrity; does not certify semantic correctness or causal validity.'})
    log('Output integrity audit passed; original sources and checkpoint unchanged')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['prepare','baseline','generate','validate','evaluate','report','all'],required=True)
    args=parser.parse_args()
    functions={'prepare':prepare,'baseline':baseline,'generate':generate,'validate':validate,'evaluate':evaluate,'report':report}
    for name,fn in functions.items():
        if args.stage in [name,'all']:
            log('Stage '+name);fn()
            if name=='generate' and args.stage=='all':fn()

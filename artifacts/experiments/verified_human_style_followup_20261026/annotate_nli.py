"""Independent text-only NLI assessment; diagnostic agreement, not human gold."""
from pathlib import Path
import json,os,time
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import numpy as np,pandas as pd,torch
from transformers import AutoTokenizer,AutoModelForSequenceClassification
P=Path(__file__).resolve().parent;torch.set_num_threads(8)
HYP={
 'Zionist':'The writer endorses Israeli legitimacy and security and justifies Israeli actions in the conflict.',
 'Resistance':'The writer legitimizes Iran-aligned or Palestinian armed resistance against Israel and the United States.',
 'Western':'The writer explicitly endorses Western international alliances, institutions or the rules-based international order.',
 'Russian':'The writer legitimizes Russian state actions in the war against Ukraine or endorses Russian anti-Western war framing.',
 'Ukrainian':'The writer defends Ukrainian sovereignty and resistance against Russian aggression.',
 'Right-wing':'The writer advocates American conservative or right-wing politics, criticizes progressive or socialist policies, or defends free-market and traditional conservative positions.',
 'Left-wing':'The writer advocates progressive or left-wing politics, criticizes Trump or right-wing policies, or defends workers and economic equality.',
 'Unclear':'The text reports facts or tells a story without clearly endorsing a political or ideological position.'}
rows=[json.loads(s) for s in (P/'assistant_annotation_blind.jsonl').read_text(encoding='utf8').splitlines()];labels=list(HYP)
name='MoritzLaurer/deberta-v3-large-zeroshot-v2.0';rev='cf44676c28ba7312e5c5f8f8d2c22b3e0c9cdae2'
tok=AutoTokenizer.from_pretrained(name,revision=rev,local_files_only=True);model=AutoModelForSequenceClassification.from_pretrained(name,revision=rev,local_files_only=True,dtype=torch.float32).eval();ei=next(int(k) for k,v in model.config.id2label.items() if v=='entailment')
progress=P/'independent_nli_scores.json';scores=json.loads(progress.read_text()) if progress.exists() else []
pairs=[(r['text'],h) for r in rows for h in HYP.values()]
for i in range(len(scores),len(pairs),8):
    batch=pairs[i:i+8];t=tok([a for a,b in batch],[b for a,b in batch],padding=True,truncation=True,max_length=384,return_tensors='pt')
    with torch.inference_mode():scores.extend(torch.softmax(model(**t).logits,1)[:,ei].tolist())
    progress.write_text(json.dumps(scores),encoding='utf8')
    if i%128==0:print(time.strftime('%H:%M:%S'),i,len(pairs),flush=True)
out=[]
for r,s in zip(rows,np.array(scores).reshape(len(rows),len(labels))):
    order=np.argsort(s)[::-1];top=labels[order[0]];best=float(s[order[0]]);margin=float(s[order[0]]-s[order[1]])
    label=top if best>=.55 and margin>=.05 else 'Unclear'
    out.append({'blind_id':r['blind_id'],'nli_label':label,'top_hypothesis':top,'entailment_score':best,'margin':margin,'confidence':3 if best>=.8 and margin>=.2 else 2 if label!='Unclear' else 1,'evidence':r['text'],'reason':'Highest independently assessed stance hypothesis; scores are not calibrated annotation accuracy.',**{f'score_{l}':float(v) for l,v in zip(labels,s)}})
pd.DataFrame(out).to_csv(P/'independent_nli_annotations.csv',index=False,encoding='utf-8-sig')
(P/'independent_nli_method.json').write_text(json.dumps({'model':name,'revision':rev,'hypotheses':HYP,'abstention_threshold':.55,'minimum_margin':.05,'metadata_provided':False,'role':'Independent machine assessment, not gold and not used to override the assistant label. Same NLI model also screens rewrites; agreement does not replace human adjudication.'},indent=2),encoding='utf8')
print('Independent NLI annotation complete',flush=True)

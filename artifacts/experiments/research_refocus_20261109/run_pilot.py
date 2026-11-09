"""All-30 train-source sensitivity with existing frozen classifier. No fitting."""
import csv, hashlib, json, os, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
F=ROOT/'artifacts/experiments/verified_human_style_followup_20261026'
C=ROOT/'artifacts/experiments/chatgpt_style_rewrite_30_20261102'
R=ROOT/'artifacts/experiments/style_intervention_v2_20261026/external_review_30_20261101/review_30_train_only.csv'
H=F/'checkpoints/full_original_baseline_Original_seed42.pt'
LABELS=['Zionist','Resistance','Western','Russian','Ukrainian','Right-wing','Left-wing']
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(HERE/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(n,rows):
    with (HERE/n).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def inputs():
    pairs=read(C/'frozen_comparison_inputs.csv');review={x['ID']:x for x in read(R)}
    cohort={x['row_id']:x for x in read(F/'analysis_cohort.csv')}
    assert len(pairs)==len({x['ID'] for x in pairs})==30
    rows=[]
    for p in pairs:
        rid=p['ID'];c=cohort[rid];r=review[rid]
        assert p['split']==c['split']==r['split']=='train'
        assert p['Original']==c['text']==r['Original']
        assert p['label']==c['narrative_name']==r['proposed_narrative']==LABELS[int(c['label'])]
        assert c['narrative_name'] in LABELS[5:]
        for arm,text in [('Original',p['Original']),('ChatGPT',p['ChatGPT_Style_Rewrite']),('Paraphrase',r['Paraphrase'])]:
            rows.append(dict(ID=rid,author=c['author'],split='train',condition=arm,text=text,
                             text_sha256=hashlib.sha256(text.encode()).hexdigest(),source_seen_in_head_training=True))
    return rows
def paths():
    return [C/'frozen_comparison_inputs.csv',C/'CHATGPT_STYLE_REWRITE_30_20261102.csv',R,
            F/'analysis_cohort.csv',F/'author_splits.csv',H,ROOT/'models/best_model_sbert_only.pth',
            ROOT/'experiments/author_generalization/author_style_controlled.py',
            ROOT/'src/narrative_lens/config.py',Path(__file__)]
def verify():
    frozen=json.loads((HERE/'protected_hashes.json').read_text(encoding='utf-8'))
    assert all(digest(ROOT/p)==h for p,h in frozen.items())
def prepare():
    assert not (HERE/'predictions.csv').exists(),'Protocol cannot be redefined after outcomes'
    save('pilot_inputs.csv',inputs())
    dump('protocol.json',dict(date='2026-11-09',primary_model=str(H.relative_to(ROOT)),
      seed_selection='42 fixed convention, no outcome selection',
      encoder='Existing production MiniLM weights, exactly base.encoder()',
      architecture='384->128 ReLU Dropout(.3)->7, eval mode, strict state loading',
      label_order=LABELS,active_training_labels=LABELS[5:],
      compatibility='Exact same source corpus, label definitions and index order; two active labels, not seven-class validation',
      scope='All 30 train sources including rejected/borderline; no test/val predictions',
      head_training='Existing 105-source train head; all 30 Originals seen in earlier fitting; validation selection used earlier 43 sources',
      primary_metrics=['argmax flips','probability TV','JS nats','delta original predicted class probability','delta confidence','delta margin'],
      performance_metrics=None,performance_reason='Source labels are machine proposals, not human gold',
      control='Existing Paraphrase for exact same IDs; imperfect unmatched-strength, non-human-verified control',
      analysis='Descriptive training-source sensitivity, no causal effect or generalization estimate',
      bootstrap='2000 author-cluster draws, seed 20261109, descriptive only',
      new_fits=0,new_rewrites=0,new_external_reviews=0,threshold_changes=False))
    dump('protected_hashes.json',{str(p.relative_to(ROOT)):digest(p) for p in paths()})
def infer():
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    verify()
    import numpy as np
    import torch
    sys.path.insert(0,str(ROOT/'experiments/author_generalization'))
    import author_style_controlled as base
    torch.set_num_threads(4);torch.manual_seed(42)
    rows=inputs();encoder=base.encoder();z=base.embed([r['text'] for r in rows],encoder)
    head=base.head();head.load_state_dict(torch.load(H,weights_only=True,map_location='cpu'),strict=True);head.eval()
    p=base.probs(head,z);np.testing.assert_allclose(p.sum(1),1,atol=1e-6)
    predictions=[];lookup={}
    for r,q in zip(rows,p):
        predictions.append({k:r[k] for k in ['ID','author','split','condition','text_sha256']}|
          dict(prediction=LABELS[int(q.argmax())],confidence=float(q.max()),margin=float(np.diff(np.sort(q)[-2:])[0]))|
          {f'p_{label}':float(q[i]) for i,label in enumerate(LABELS)})
        lookup[r['ID'],r['condition']]=q
    save('predictions.csv',predictions)
    transitions=[]
    for r in [x for x in rows if x['condition']=='Original']:
        a=lookup[r['ID'],'Original']
        for arm in ['ChatGPT','Paraphrase']:
            b=lookup[r['ID'],arm];m=(a+b)/2
            kl=lambda v:float(np.sum(v*np.log(np.maximum(v,1e-30)/np.maximum(m,1e-30))))
            transitions.append(dict(ID=r['ID'],author=r['author'],condition=arm,
              original_prediction=LABELS[int(a.argmax())],new_prediction=LABELS[int(b.argmax())],
              flip=int(a.argmax()!=b.argmax()),total_variation=float(np.abs(b-a).sum()/2),
              js_nats=(kl(a)+kl(b))/2,delta_original_predicted_probability=float(b[a.argmax()]-a.max()),
              delta_confidence=float(b.max()-a.max()),
              delta_margin=float(np.diff(np.sort(b)[-2:])[0]-np.diff(np.sort(a)[-2:])[0])))
    save('transitions.csv',transitions);summaries=[];authors=sorted({x['author'] for x in rows})
    for arm in ['ChatGPT','Paraphrase']:
        g=[x for x in transitions if x['condition']==arm];rng=np.random.default_rng(20261109);draws=[]
        for _ in range(2000):
            draws.append(np.mean([x['flip'] for a in rng.choice(authors,len(authors),replace=True) for x in g if x['author']==a]))
        summaries.append(dict(condition=arm,n=len(g),flips=sum(x['flip'] for x in g),
          **{f'mean_{k}':float(np.mean([x[k] for x in g])) for k in ['flip','total_variation','js_nats','delta_original_predicted_probability','delta_confidence','delta_margin']},
          flip_cluster_ci_low=float(np.quantile(draws,.025)),flip_cluster_ci_high=float(np.quantile(draws,.975))))
    save('summary.csv',summaries);verify()
    dump('execution_audit.json',dict(n_predictions=len(predictions),n_train_sources=30,n_val_or_test_predictions=0,
      new_fits=0,new_rewrites=0,protected_inputs_unchanged=True,torch=torch.__version__,numpy=np.__version__))
if __name__=='__main__':
    stage=sys.argv[-1];assert stage in ['prepare','infer'];{'prepare':prepare,'infer':infer}[stage]()

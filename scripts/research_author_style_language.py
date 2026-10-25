"""Read-only corpus audit. Outputs are isolated from existing experiments.

Run with the project's Python, with langid installed in artifacts/research_dependencies.
Language ID describes stored text, never a person's native language.
"""
from pathlib import Path
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'research_author_style_language'
sys.path.insert(0, str(ROOT / 'artifacts' / 'research_dependencies'))
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import numpy as np
import pandas as pd
import torch
from langid.langid import LanguageIdentifier, model as language_model

NARRATIVES = ['Zionist', 'Resistance', 'Western', 'Russian', 'Ukrainian', 'Right-wing', 'Left-wing']
PERSON_ASSOCIATED = {'khamenei_ir', 'ZelenskyyUa', 'BenShapiro', 'BernieSanders',
                     'HananyaNaftali', 'MariaZakharova', 'CharlieKirk'}
CONNECTORS = {'and','but','or','because','although','however','therefore','moreover',
              'nevertheless','whereas','thus','since','while','yet','so','if'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def clean(text):
    return re.sub(r'https?://\S+|www\.\S+|@[\w_]+', ' ', str(text))

def style(text):
    t = clean(text)
    words = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)*", t, re.UNICODE)
    low = [w.lower() for w in words]
    sentences = [s for s in re.split(r'[.!?。！？]+|\n+', t) if re.search(r'[^\W\d_]', s)]
    n = len(words)
    alpha = [c for c in t if c.isalpha()]
    windows = [len(set(low[i:i+50]))/50 for i in range(max(0,n-49))]
    denom = max(n,1)
    return {'words':n, 'sentences':len(sentences),
            'mean_sentence_words':n/max(len(sentences),1),
            'mean_word_chars':np.mean([len(w) for w in words]) if words else 0,
            'type_token_ratio':len(set(low))/denom,
            'mattr50':float(np.mean(windows)) if windows else np.nan,
            'connectors_per100_words':100*sum(w in CONNECTORS for w in low)/denom,
            'first_person_en_per100_words':100*sum(w in {'i','me','my','mine','we','us','our','ours'} for w in low)/denom,
            'questions_per100_words':100*t.count('?')/denom,
            'exclamations_per100_words':100*t.count('!')/denom,
            'commas_per100_words':100*t.count(',')/denom,
            'uppercase_fraction':sum(c.isupper() for c in alpha)/max(len(alpha),1),
            'hebrew_letters':len(re.findall(r'[\u0590-\u05ff]',t)),
            'cyrillic_letters':len(re.findall(r'[\u0400-\u04ff]',t)),
            'arabic_letters':len(re.findall(r'[\u0600-\u06ff]',t))}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames=[]
    manifest={}
    for platform in ['twitter','telegram']:
        p=ROOT/'data'/'raw'/f'{platform}_natural_dataset.csv'
        f=pd.read_csv(p).fillna('')
        f['platform']=platform
        f['source_csv']=str(p.relative_to(ROOT)).replace('\\','/')
        f['csv_record_number']=np.arange(len(f))+1
        f['row_id']=[f'{platform}:{i}' for i in f['csv_record_number']]
        manifest[str(p.relative_to(ROOT))]={'sha256':sha(p),'rows':len(f)}
        frames.append(f)
    data=pd.concat(frames,ignore_index=True)
    data['text_sha256']=data.text.map(lambda s:hashlib.sha256(s.encode()).hexdigest())
    features=pd.DataFrame([style(t) for t in data.text])
    print('Loaded',len(data),'rows;',data.account.nunique(),'account identifiers',flush=True)
    lid=LanguageIdentifier.from_modelstring(language_model,norm_probs=True)
    language_rows=[]
    for i,t in enumerate(data.text):
        c=clean(t)
        lang,score=lid.classify(c) if c.strip() else ('und',0.0)
        # Posterior is a model score, not calibrated truth; short texts stay uncertain.
        status='automatic_candidate' if features.iloc[i]['words']>=8 and score>=.9 else 'uncertain_short_or_low_score'
        language_rows.append({'language_candidate':lang,'language_model_score':float(score),'language_status':status})
        if i%2000==0: print('Language ID',i,flush=True)
    data=pd.concat([data,features,pd.DataFrame(language_rows)],axis=1)
    data.to_csv(OUT/'text_language_and_style.csv',index=False,encoding='utf-8-sig')
    accounts=[]
    feature_names=[c for c in features if not c.endswith('_letters')]
    for account,g in data.groupby('account',sort=True):
        langs=g.language_candidate.value_counts().to_dict()
        primary='person_associated_account' if account in PERSON_ASSOCIATED else 'account_or_channel_no_verified_individual_writer'
        accounts.append({'Author':account,'Native Language':'לא נמצא מקור אמין',
          'Text Language':json.dumps(langs,ensure_ascii=False),
          'Narrative':'|'.join(sorted(g.narrative_name.unique())),
          'Evidence/Source':'; '.join(sorted(g.source_csv.unique())),
          'Possible Linguistic Influence':'מאפייני טקסט נמדדו; אין לייחס לשפת אם ללא מקור וזהות הכותב/המתרגם',
          'unit_type':primary,'n_texts':len(g),'platforms':'|'.join(sorted(g.platform.unique())),
          'date_min':g.date.min(),'date_max':g.date.max(),
          'n_narrative_labels':g.narrative_name.nunique(),
          'language_uncertain_n':int((g.language_status!='automatic_candidate').sum()),
          **{f'mean_{c}':float(g[c].mean()) for c in feature_names}})
    roster=pd.DataFrame(accounts)
    native_registry=OUT/'native_language_registry.json'
    if native_registry.exists():
        registry=json.loads(native_registry.read_text(encoding='utf-8'))
        for account,record in registry.items():
            match=roster.Author==account
            if record.get('native_language'):
                roster.loc[match,'Native Language']=record['native_language']
                roster.loc[match,'Native Language Status']=record.get('confidence_status','verified' if record.get('status')=='explicit_reliable_source' else 'unknown')
                roster.loc[match,'Evidence/Source']=roster.loc[match,'Evidence/Source']+'; '+record.get('source_url','user-provided; no external L1 source supplied')
    roster.to_csv(OUT/'author_language_evidence.csv',index=False,encoding='utf-8-sig')
    # Examples are pointers into original data, not reconstructed social-media URLs.
    examples=pd.concat([g.sort_values(['date','row_id']).iloc[np.unique(np.linspace(0,len(g)-1,min(3,len(g))).astype(int))] for _,g in data.groupby('account')])
    examples.to_csv(OUT/'account_language_review_samples.csv',index=False,encoding='utf-8-sig')
    data.groupby(['narrative_name','language_candidate']).size().rename('n').reset_index().to_csv(OUT/'stored_language_by_provenance_narrative.csv',index=False,encoding='utf-8-sig')
    manifest.update({'analysis_date':'2026-10-20','language_detector':'langid 1.1.6; unrestricted language inventory; norm_probs=True',
      'human_rows':len(data),'accounts':len(roster),'person_associated_accounts':len(PERSON_ASSOCIATED),
      'accounts_with_multiple_provenance_labels':int((roster.n_narrative_labels>1).sum()),
      'language_counts':data.language_candidate.value_counts().to_dict(),
      'automatic_candidate_counts':data.loc[data.language_status=='automatic_candidate','language_candidate'].value_counts().to_dict(),
      'uncertain_language_rows':int((data.language_status!='automatic_candidate').sum()),
      'sha256_this_script':sha(Path(__file__))})
    (OUT/'audit_summary.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=True,indent=2),flush=True)
    if '--predict' in sys.argv:
        from sentence_transformers import SentenceTransformer
        torch.set_num_threads(4)
        checkpoint=ROOT/'models'/'best_model_sbert_only.pth'
        state=torch.load(checkpoint,map_location='cpu',weights_only=True)
        encoder=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2',local_files_only=True,device='cpu')
        encoder.load_state_dict({k[len('sbert.'):]:v for k,v in state.items() if k.startswith('sbert.')},strict=True)
        head=torch.nn.Sequential(torch.nn.Linear(384,128),torch.nn.ReLU(),torch.nn.Dropout(.3),torch.nn.Linear(128,7))
        head.load_state_dict({k[len('mlp.'):]:v for k,v in state.items() if k.startswith('mlp.')},strict=True)
        head.eval()
        print('Fresh encoding from checkpoint encoder; descriptive full-corpus inference',flush=True)
        embeddings=encoder.encode(data.text.tolist(),batch_size=64,show_progress_bar=True,convert_to_tensor=True)
        with torch.no_grad():
            probs=torch.softmax(head(embeddings.cpu()),dim=1).numpy()
        data['predicted_narrative']=[NARRATIVES[i] for i in probs.argmax(axis=1)]
        data['max_probability']=probs.max(axis=1)
        for i,n in enumerate(NARRATIVES): data[f'p_{n}']=probs[:,i]
        data.to_csv(OUT/'text_language_style_predictions.csv',index=False,encoding='utf-8-sig')
        data.groupby(['account','predicted_narrative']).size().rename('n').reset_index().to_csv(OUT/'predictions_by_account.csv',index=False,encoding='utf-8-sig')
        manifest['checkpoint_sha256']=sha(checkpoint)
        manifest['prediction_scope']='Descriptive inference on ALL current real posts; includes training exposure, not a generalization test. No native-language correlation claimed.'
        (OUT/'audit_summary.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()

"""Assemble the assistant's blinded, text-only proposals; no account gold."""
from pathlib import Path
import json
import pandas as pd
from sklearn.metrics import cohen_kappa_score
P=Path(__file__).resolve().parent
def main():
    raw=pd.read_csv(P/'collected_texts.csv').drop_duplicates('text_sha256').drop_duplicates('source_url')
    key=pd.read_csv(P/'assistant_annotation_key.csv');a=pd.read_csv(P/'assistant_annotations.tsv',sep='\t')
    assert not a.blind_id.duplicated().any() and set(a.blind_id)==set(key.blind_id)
    x=key.merge(raw,on='row_id',validate='one_to_one').merge(a,on='blind_id',validate='one_to_one')
    assert all(r.evidence.casefold() in r.text.casefold() for r in x.itertuples()),'Evidence must be a literal input span'
    x=x.rename(columns={'label':'label_a','confidence':'confidence_a','evidence':'evidence_a'})
    x['reason_a']='Text-only assistant proposal; the exact supporting or ambiguous span is retained in evidence_a.'
    nli=P/'independent_nli_annotations.csv'
    if nli.exists():
        b=pd.read_csv(nli).rename(columns={'nli_label':'label_b','confidence':'confidence_b','evidence':'evidence_b','reason':'reason_b'})
        x=x.merge(b[['blind_id','label_b','confidence_b','evidence_b','reason_b','entailment_score','margin']],on='blind_id',validate='one_to_one')
        x['agreement']=x.label_a==x.label_b
        ag={'n':len(x),'agreement':float(x.agreement.mean()),'cohen_kappa':float(cohen_kappa_score(x.label_a,x.label_b)),
            'independence':'Text-only conversation assistant vs separately evaluated DeBERTa NLI model. Both machine raters, not human inter-rater reliability. NLI is diagnostic and does not override assistant proposals.'}
        pd.crosstab(x.label_a,x.label_b).to_csv(P/'annotation_agreement_confusion.csv',encoding='utf-8-sig')
        x[~x.agreement][['blind_id','text','label_a','label_b','confidence_a','confidence_b','evidence_a']].to_csv(P/'annotation_disagreements.csv',index=False,encoding='utf-8-sig')
    else:
        for c in ['label_b','confidence_b','evidence_b','reason_b','agreement']:x[c]=''
        ag={'n':0,'agreement':None,'cohen_kappa':None,'independence':'Independent NLI assessment running; not available yet. No human assessment performed.'}
    x['eligible_provisional_label']=x.label_a.isin(['Right-wing','Left-wing'])&x.confidence_a.ge(2)
    x['provisional_narrative']=x.label_a.where(x.eligible_provisional_label,'')
    if (P/'analysis_cohort.csv').exists():
        frozen=pd.read_csv(P/'analysis_cohort.csv').set_index('row_id')
        refreshed=x.set_index('row_id').loc[frozen.index]
        assert list(refreshed.provisional_narrative)==list(frozen.narrative_name),'Frozen primary labels changed: create a new study version'
        assert list(refreshed.text_sha256)==list(frozen.text_sha256),'Frozen source text changed'
    x['gold_status']='text_only_assistant_proposal_pending_human'
    for c in ['human_label','human_confidence','human_notes']:x[c]=''
    x.to_csv(P/'text_annotations.csv',index=False,encoding='utf-8-sig')
    pd.crosstab(x.author,x.label_a).to_csv(P/'author_text_label_distribution.csv',encoding='utf-8-sig')
    blind=x[['blind_id','text']].rename(columns={'blind_id':'annotation_id'})
    for c in ['human_label','human_confidence','ambiguous','evidence','notes']:blind[c]=''
    blind.to_csv(P/'human_annotation_blind.csv',index=False,encoding='utf-8-sig');x[['blind_id','row_id']].rename(columns={'blind_id':'annotation_id'}).to_csv(P/'human_annotation_key.csv',index=False,encoding='utf-8-sig')
    ag.update({'eligible_provisional':int(x.eligible_provisional_label.sum()),'a_counts':x.label_a.value_counts().to_dict(),'human_gold_completed':False})
    (P/'annotation_agreement.json').write_text(json.dumps(ag,indent=2),encoding='utf8')
    (P/'annotation_method.json').write_text(json.dumps({'primary_annotator':'Codex conversation assistant, exact backend revision not exposed','input':'blind_id plus text only; no author, source, article title, account category or narrative classifier prediction','definitions':'Project annotation guide: seven classes plus Unclear; neutral factual reporting and unendorsed quotations are not automatically political narratives. Confidence 1 uncertain, 2 plausible, 3 clear.','main_label_selection':'Primary assistant label Right-wing or Left-wing and confidence >=2, exact evidence span. Other classes and unclear remain saved for human review, not silently recoded.','independent_assessor':'Separately run DeBERTa NLI, diagnostic agreement only.','human_review_completed':False,'excluded_weak_local_model_attempt':'annotation_feasibility_1p5b_aborted.jsonl'},indent=2),encoding='utf8')
    print('Assembled',len(x),'text annotations;',ag['eligible_provisional'],'eligible',flush=True)
if __name__=='__main__':main()

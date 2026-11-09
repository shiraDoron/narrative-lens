"""Future human-intake validation and common-cohort views. No model calls."""
import datetime
import hashlib

RATINGS={'Yes','No','Borderline'}
ARMS={'A':['Original'],'B':['Paraphrase'],'C':['Style'],'D':['Original','Style'],'E':['Original','Paraphrase']}
def text_hash(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def provenance(row):
    if row.get('reviewer_type')!='human':raise ValueError('Human reviewer_type required; LLM reviews cannot be human intake')
    if not row.get('reviewer_id','').strip():raise ValueError('reviewer_id missing')
    datetime.date.fromisoformat(row.get('review_date',''))
def validate_pair(row,source,rewrite,variant):
    provenance(row)
    if row.get('source_sha256')!=text_hash(source):raise ValueError('Source hash mismatch')
    if row.get('rewrite_sha256')!=text_hash(rewrite):raise ValueError('Rewrite hash mismatch')
    required=['meaning','stance','semantic_drift']+(['style_change'] if variant=='Style' else [])
    if any(row.get(k) not in RATINGS for k in required):raise ValueError('Invalid/missing rating')
    if any(row[k]=='Borderline' for k in required) and not row.get('notes','').strip():raise ValueError('Borderline needs notes')
    return row['meaning']=='Yes' and row['stance']=='Yes' and row['semantic_drift']=='No' and (variant!='Style' or row['style_change']=='Yes')
def keyed(rows,key):
    result={}
    for row in rows:
        k=key(row)
        if k in result:raise ValueError('Duplicate ID/review; adjudicate explicitly before policy construction')
        result[k]=row
    return result
def build_policy(mapping,source_labels,pair_reviews):
    """Requires complete attempted outputs/QC, then symmetric fallback, never silently drops IDs."""
    originals=keyed(mapping,lambda x:x['ID']);labels=keyed(source_labels,lambda x:x['ID'])
    reviews=keyed(pair_reviews,lambda x:(x['ID'],x['variant']))
    if set(originals)!=set(labels):raise ValueError('Exact source-label coverage required')
    if set(reviews)!={(rid,v) for rid in originals for v in ['Paraphrase','Style']}:raise ValueError('Exact paired QC coverage required')
    policy=[];coverage=[];accepted=[]
    for rid,r in originals.items():
        if r.get('split','train')!='train':raise ValueError('Training views accept train only')
        label=labels[rid];provenance(label)
        if label.get('source_sha256')!=text_hash(r['Original']):raise ValueError('Label source mismatch')
        if label.get('human_label')!=r['label']:raise ValueError('Gold/proposal disagreement requires explicit corpus decision')
        passed={}
        for variant in ['Paraphrase','Style']:
            if not r.get(variant):raise ValueError('Missing generation is not an attempted failure; cannot replace it by Original silently')
            passed[variant]=validate_pair(reviews[rid,variant],r['Original'],r[variant],variant)
        ok=all(passed.values())
        coverage.append(dict(ID=rid,Paraphrase_accepted=passed['Paraphrase'],Style_accepted=passed['Style'],common_accepted=ok))
        row={**r,'Paraphrase':r['Paraphrase'] if ok else r['Original'],'Style':r['Style'] if ok else r['Original']}
        policy.append(row)
        if ok:accepted.append(r)
    def views(rows):return {a:[dict(ID=r['ID'],label=r['label'],variant=v,text=r[v]) for r in rows for v in variants] for a,variants in ARMS.items()}
    return dict(primary_all_attempted=views(policy),secondary_common_accepted=views(accepted),coverage=coverage)

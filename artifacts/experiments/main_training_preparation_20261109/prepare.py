"""Prepare auditable draft views and fixed-budget schedules. Never fit/generate/test."""
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
F=ROOT/'artifacts/experiments/verified_human_style_followup_20261026'
C=ROOT/'artifacts/experiments/chatgpt_style_rewrite_30_20261102'
Q=C/'review_author_analysis_20261102'
LABELS=['Right-wing','Left-wing']
SEEDS=[7,42,123,2026,31415]
ARMS={'A':['Original'],'B':['Paraphrase'],'C':['Style'],'D':['Original','Style'],'E':['Original','Paraphrase']}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,rows,fields=None):
    with (HERE/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def dump(name,data):(HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def source_paths():
    return [F/'analysis_cohort.csv',F/'text_annotations.csv',F/'author_splits.csv',F/'generated_rewrites.jsonl',
      C/'CHATGPT_STYLE_REWRITE_30_20261102.csv',C/'protocol.json',Q/'HUMAN_VALIDATION_30.csv',
      Q/'HUMAN_VALIDATION_30.md',Q/'EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md']
def schedules(view,seed,steps,batch_size=16):
    """Fixed processed-example budget; cycles use every variant once before repeating."""
    rng=random.Random(seed);order=[];cycle=0
    while len(order)<steps*batch_size:
        round_rows=list(range(len(view)));rng.shuffle(round_rows)
        order.extend((i,cycle) for i in round_rows);cycle+=1
    return [dict(step=k//batch_size,slot=k%batch_size,view_index=i,ID=view[i]['ID'],variant=view[i]['variant'],cycle=cycle)
            for k,(i,cycle) in enumerate(order[:steps*batch_size])]
def human_status():
    r=read(Q/'HUMAN_VALIDATION_30.csv');fields=[k for k in r[0] if k.startswith('human_')]
    complete=[x for x in r if all((x.get(k) or '').strip() for k in fields if k!='human_notes')]
    return dict(rows=len(r),completed_rows=len(complete),filled_fields={k:sum(bool((x[k] or '').strip()) for x in r) for k in fields},
      conclusion='No attributable completed human judgments found on disk' if not complete else 'Requires reviewer identity/date/provenance audit; nonblank fields alone do not prove human review',
      user_reported_counts=dict(meaning_Yes=30,stance_Yes=30,style_Yes=28,style_Borderline=2,drift_No=30),
      user_reported_counts_are_not_per_id_import=True)
def main():
    before={str(p.relative_to(ROOT)):sha(p) for p in source_paths()}
    if (HERE/'SOURCE_HASHES.json').exists():
        assert before==json.loads((HERE/'SOURCE_HASHES.json').read_text()),'Source changed: create a new versioned preparation run'
    cohort=read(F/'analysis_cohort.csv');train=[x for x in cohort if x['split']=='train']
    assignments={x['author']:x['split'] for x in read(F/'author_splits.csv')}
    annotations=read(F/'text_annotations.csv')
    assert len(train)==105 and all(x['narrative_name'] in LABELS for x in train)
    assert all(assignments[x['author']]==x['split'] for x in cohort)
    texts={x['row_id']:x for x in train}
    chat={x['id']:x['chatgpt_style_rewrite'] for x in read(C/'CHATGPT_STYLE_REWRITE_30_20261102.csv')}
    assert len(chat)==30 and set(chat)<=set(texts)
    para={}
    # Only retain train Paraphrases; frozen test text is never exported/inferred/generated.
    with (F/'generated_rewrites.jsonl').open(encoding='utf-8') as f:
        for line in f:
            x=json.loads(line)
            if x['row_id'] in texts and x['condition']=='Paraphrase':
                assert x['original']==texts[x['row_id']]['text']
                assert x['row_id'] not in para
                para[x['row_id']]=x['rewrite']
    assert set(para)==set(texts)
    mapping=[]
    for rid,c in texts.items():
        mapping.append(dict(ID=rid,author=c['author'],split='train',label=c['narrative_name'],
          original_present=True,paraphrase_present=rid in para,style_present=rid in chat,
          source_label_human=c['human_label'],label_status='machine proposal; not human gold',
          Original=c['text'],Paraphrase=para[rid],Style=chat.get(rid,'')))
    save('TRAIN_CONDITION_ID_MAP.csv',mapping)
    common=[x for x in mapping if x['style_present']]
    missing=[x for x in mapping if not x['style_present']]
    save('STYLE_REWRITE_MISSING_75.csv',[dict(ID=x['ID'],Original=x['Original'],source_split='train',generation_status='blocked_unknown_original_protocol') for x in missing])
    save('SOURCE_LABEL_INTAKE.csv',[dict(ID=x['row_id'],Original=x['text'],split=x['split'],
      source_sha256=hashlib.sha256(x['text'].encode()).hexdigest(),
      human_label='',reviewer_type='',reviewer_id='',review_date='',notes='') for x in cohort if x['split']!='test'])
    save('PAIRED_QC_INTAKE.csv',[dict(ID=x['ID'],variant=arm,Original=x['Original'],Rewrite=x[arm],
      generation_status='available' if x[arm] else 'missing_do_not_rate',source_sha256=hashlib.sha256(x['Original'].encode()).hexdigest(),
      rewrite_sha256=hashlib.sha256(x[arm].encode()).hexdigest() if x[arm] else '',
      meaning='',stance='',style_change='',semantic_drift='',reviewer_type='',reviewer_id='',review_date='',notes='') for x in mapping for arm in ['Paraphrase','Style']])
    # Raw views are explicitly NOT training-approved; no labels or ratings are altered.
    configs=[];schedules_meta=[]
    for arm,variants in ARMS.items():
        view=[dict(ID=x['ID'],author=x['author'],label=x['label'],label_status=x['label_status'],variant=v,text=x[v]) for x in common for v in variants]
        save(f'DRAFT_ARM_{arm}.csv',view)
        for seed in SEEDS:
            steps=20*math.ceil(len(common)/16)
            config=dict(condition=arm,seed=seed,view_file=f'DRAFT_ARM_{arm}.csv',n_sources=len(common),n_examples=len(view),
              label_space=LABELS,output_label_order=['Zionist','Resistance','Western','Russian','Ukrainian','Right-wing','Left-wing'],
              encoder='same frozen production MiniLM; no encoder fine-tuning',head='fresh 384->128 ReLU Dropout(.3)->7',
              optimizer='Adam',lr=.001,batch_size=16,optimizer_updates=steps,processed_examples=steps*16,
              checkpoint_rule='evaluate all fixed steps; no condition-specific early stopping; one final checkpoint',
              validation='original validation texts only; no frozen-test inputs; labels must pass human gate',
              training_ready=False,readiness_reason='missing verified human gold/QC and original ChatGPT generation metadata',
              schedule=f'SCHEDULE_{arm}_seed{seed}.csv')
            dump(f'CONFIG_{arm}_seed{seed}.json',config);configs.append(config)
            plan=schedules(view,seed,steps);save(config['schedule'],plan)
            schedules_meta.append(dict(condition=arm,seed=seed,updates=steps,processed_examples=steps*16,n_sources=len(common),n_examples=len(view)))
    save('SCHEDULE_SUMMARY.csv',schedules_meta)
    byauthor=[]
    for author,split in assignments.items():
        group=[x for x in annotations if x['author']==author]
        eligible=[x for x in cohort if x['author']==author]
        byauthor.append(dict(author=author,split=split,unique_texts=len(group),eligible=len(eligible),
          Right=sum(x['narrative_name']=='Right-wing' for x in eligible),Left=sum(x['narrative_name']=='Left-wing' for x in eligible),
          style_present=sum(x['author']==author and x['style_present'] for x in mapping)))
    save('AUTHOR_CLASS_COUNTS.csv',byauthor)
    human=human_status();dump('HUMAN_REVIEW_IMPORT_STATUS.json',human)
    llm=(Q/'EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md').read_text(encoding='utf-8')
    llm_rows=[]
    pattern=r'### \d+\. (creators:[^\n]+)\n\*\*Meaning:\*\* (Yes|No|Borderline) \| \*\*Stance:\*\* (Yes|No|Borderline) \| \*\*Style:\*\* (Yes|No|Borderline) \| \*\*Drift:\*\* (Yes|No|Borderline)\s*\n\*\*Notes:\*\* ([^\n]+)'
    for rid,meaning,stance,style,drift,notes in re.findall(pattern,llm):
        llm_rows.append(dict(ID=rid,review_type='External LLM Review',reviewer='Claude, exact version unknown',
          review_date='2026-11-09',meaning_preserved=meaning,stance_preserved=stance,style_change_valid=style,semantic_drift=drift,notes=notes))
    assert len(llm_rows)==30 and {x['ID'] for x in llm_rows}==set(chat)
    save('CLAUDE_REVIEW_PER_ID_IMPORTED.csv',llm_rows)
    proto=json.loads((C/'protocol.json').read_text())
    dump('GENERATOR_PROVENANCE.json',dict(generator=proto['generator_name'],model=proto['generator_model_version'],
      prompt=proto['generator_prompt'],parameters=proto['generator_decoding'],date='2026-11-02 received-file date; actual generation timestamp unknown',
      source_file_sha256=proto['received_file_sha256'],original_only='user-reported, not independently auditable',
      recovered_constraints='Original only; preserve claims, stance, attribution, certainty, roles, events, intensity, quotes, quantifiers, negation, entities, numbers, time, causality',
      recovered_constraints_are_not_original_prompt=True,generation_permitted=False))
    hashes=[x['text_sha256'] for x in annotations];cross=[]
    for field in ['text_sha256','article_snapshot_sha256']:
        groups=collections.defaultdict(set)
        for x in annotations:groups[x[field]].add(assignments[x['author']])
        cross.extend((field,h) for h,v in groups.items() if len(v)>1)
    assert not cross and len(hashes)==len(set(hashes))==429
    coverage={s:dict(n=sum(x['split']==s for x in cohort),classes=dict(collections.Counter(x['narrative_name'] for x in cohort if x['split']==s))) for s in ['train','val','test']}
    audit=dict(raw_unique=429,train_raw=sum(x['unique_texts'] for x in byauthor if x['split']=='train'),train_eligible=len(train),
      train_classes=dict(collections.Counter(x['label'] for x in mapping)),common_ids=len(common),missing_style=len(missing),missing_paraphrase=len(set(texts)-set(para)),
      common_classes=dict(collections.Counter(x['label'] for x in common)),split_coverage=coverage,
      cross_split_exact_hash_collisions=cross,author_disjoint=True,human_source_labels=sum(bool(x['human_label'].strip()) for x in cohort),
      human_pair_reviews_completed=human['completed_rows'],required_human_labels_development=148,required_pair_qc_full105=210,
      new_training=0,new_rewrites=0,test_predictions=0,
      training_ready=False,all_views_are_drafts=True,near_duplicate_scope='Prior train202 audit only; no new semantic/test near-duplicate scan',
      historical_test_repeatedly_used=True)
    dump('DATA_READINESS_AUDIT.json',audit)
    assert before=={str(p.relative_to(ROOT)):sha(p) for p in source_paths()}
    dump('SOURCE_HASHES.json',before)
    dump('PREPARATION_COMPLETE.json',dict(status='prepared_but_blocked',conditions=5,configs=len(configs),
      inputs_unchanged=True,no_fitting=True,no_test_evaluation=True))
if __name__=='__main__':main()

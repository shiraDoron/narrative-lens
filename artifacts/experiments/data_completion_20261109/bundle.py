"""Data-completion bundle only. No rewriting, training or classifier predictions."""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREP=ROOT/'artifacts/experiments/main_training_preparation_20261109'
CHAT=ROOT/'artifacts/experiments/chatgpt_style_rewrite_30_20261102'
FOLLOW=ROOT/'artifacts/experiments/verified_human_style_followup_20261026'
VERSION='chatgpt_style_extension_v1_20261109'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text_sha(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(p,rows,fields=None):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def mapping():return read(PREP/'TRAIN_CONDITION_ID_MAP.csv')
def legacy():return {x['ID']:x for x in mapping() if x['Style']}
def missing():return [x for x in mapping() if not x['Style']]
def protected():
    paths=[CHAT/'CHATGPT_STYLE_REWRITE_30_20261102.csv',CHAT/'frozen_comparison_inputs.csv',
      CHAT/'review_author_analysis_20261102/HUMAN_VALIDATION_30.csv',
      CHAT/'review_author_analysis_20261102/HUMAN_VALIDATION_30.md',
      CHAT/'review_author_analysis_20261102/EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md',
      FOLLOW/'author_splits.csv',FOLLOW/'analysis_cohort.csv',PREP/'TRAIN_CONDITION_ID_MAP.csv',
      ROOT/'artifacts/experiments/verified_human_style_followup_20261026/experiment.py',
      ROOT/'artifacts/experiments/style_intervention_v2_20261026/study.py',
      ROOT/'artifacts/experiments/style_intervention_v2_20261026/style_feature_scaling.json']
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}
def verify():
    frozen=json.loads((HERE/'SOURCE_HASHES.json').read_text())
    assert frozen==protected(),'Protected source changed; create a new bundle version'
def make_pair_package(rows,out,expected=75):
    """Blind pairs only, no labels/authors/guards/scores or prior reviews."""
    items=[];md=['# בדיקת שימור ושינוי סגנון — חבילה עצמאית','',
      'למילוי אדם: Yes / No / Borderline בכל הכרעה. semantic_drift=No פירושו שלא זוהה שינוי משמעות. יש לתעד סוקר ותאריך בקובץ metadata נפרד. אין לערוך את הטקסטים. שורות ללא Rewrite מסומנות pending ואסור לדרג אותן.','']
    for r in rows:
        rewrite=r.get('chatgpt_style_rewrite',r.get('ChatGPT_Style_Rewrite',r.get('Style','')))
        original=r.get('original',r.get('Original',''));rid=r.get('id',r.get('ID'))
        row=dict(ID=rid,Original=original,ChatGPT_Style_Rewrite=rewrite,
          review_status='ready_for_human' if rewrite else 'pending_generation_do_not_rate',
          human_meaning_preserved='',human_narrative_stance_preserved='',human_style_change_valid='',human_semantic_drift='',human_notes='')
        items.append(row)
        md += [f'## {rid}','','### Original','',original,'','### Style Rewrite','',rewrite or '**Pending generation — אין לדרג עדיין.**','',
          '| field | answer |','|---|---|',*[f'| {k} | |' for k in row if k.startswith('human_')],'']
    assert len(items)==expected
    save(out.with_suffix('.csv'),items);out.with_suffix('.md').write_text('\n'.join(md),encoding='utf-8')
def main():
    # Never erase answers or generation metadata entered after handoff.
    template_manifest=HERE/'TEMPLATE_HASHES.json'
    if template_manifest.exists():
        for name,digest in json.loads(template_manifest.read_text()).items():
            assert (HERE/name).exists() and sha(HERE/name)==digest, f'Edited intake/template: {name}; preserve it and do not regenerate this bundle'
    frozen=protected()
    if (HERE/'SOURCE_HASHES.json').exists():verify()
    if (HERE/'GENERATION_PROTOCOL.json').exists():
        prior=json.loads((HERE/'GENERATION_PROTOCOL.json').read_text())
        assert prior['prompt_sha256']==sha(HERE/'STYLE_REWRITE_PROMPT_V1.txt'),'Prompt changed; create a new version'
    rows=mapping();new=missing();old=legacy()
    assert len(rows)==105 and len(new)==75 and len(old)==30
    splits={x['author']:x['split'] for x in read(FOLLOW/'author_splits.csv')}
    assert all(x['split']=='train' and splits[x['author']]=='train' for x in rows)
    assert len({x['ID'] for x in new})==75 and not set(old)&{x['ID'] for x in new}
    assert len({text_sha(x['Original']) for x in new})==75
    inputs=[dict(id=x['ID'],original=x['Original'],source_sha256=text_sha(x['Original']),protocol_version=VERSION) for x in new]
    save(HERE/'STYLE_REWRITE_INPUT_75.csv',inputs)
    batches=HERE/'chatgpt_batches';batches.mkdir(exist_ok=True)
    for i in range(5):save(batches/f'BATCH_{i+1:02d}_15.csv',inputs[i*15:(i+1)*15])
    save(HERE/'STYLE_REWRITE_OUTPUT_TEMPLATE_75.csv',[dict(id=x['id'],chatgpt_style_rewrite='') for x in inputs])
    private=[dict(ID=x['ID'],author=x['author'],split=x['split'],proposed_label=x['label'],source_sha256=text_sha(x['Original'])) for x in new]
    save(HERE/'PRIVATE_SPLIT_AND_LABEL_KEY_75.csv',private)
    intake=[dict(ID=x['ID'],Original=x['Original'],proposed_label=x['label'],human_label='',proposed_label_correct='',
      evidence_span='',human_notes='',reviewer_type='',reviewer_id='',review_date='') for x in rows]
    save(HERE/'NARRATIVE_LABEL_VALIDATION_105.csv',intake)
    definitions=(HERE/'LABEL_GUIDE_HE.md').read_text(encoding='utf-8')
    md=['# אימות אנושי של תוויות — 105 טקסטי train','',definitions,'']
    for r in intake:
        md += [f"## {r['ID']}",'',r['Original'],'',f"**תווית מוצעת בלבד, לא gold:** {r['proposed_label']}",'',
          '| field | answer |','|---|---|',*[f'| {k} | |' for k in ['human_label','proposed_label_correct','evidence_span','human_notes','reviewer_type','reviewer_id','review_date']],'']
    (HERE/'NARRATIVE_LABEL_VALIDATION_105.md').write_text('\n'.join(md),encoding='utf-8')
    make_pair_package(list(old.values()),HERE/'HUMAN_PAIR_REVIEW_LEGACY30',30)
    make_pair_package(new,HERE/'HUMAN_PAIR_REVIEW_NEW75_TEMPLATE',75)
    dump(HERE/'GENERATION_METADATA_TEMPLATE.json',dict(protocol_version=VERSION,prompt_sha256=sha(HERE/'STYLE_REWRITE_PROMPT_V1.txt'),
      generator='ChatGPT',interface=None,visible_model_name=None,exact_model_revision=None,actual_generation_date=None,
      temperature=None,top_p=None,seed=None,output_limit=None,parameters_exposure='fill actual values, or explicitly record unavailable in UI',
      unknown_fields_are_not_legacy_defaults=True,batches=[],original30_unchanged=True))
    dump(HERE/'GENERATION_PROTOCOL.json',dict(version=VERSION,prompt_sha256=sha(HERE/'STYLE_REWRITE_PROMPT_V1.txt'),
      legacy_prompt_reconstruction=False,new_generator='ChatGPT; actual selected model to be recorded before batch1',
      frozen_input_file_sha256=sha(HERE/'STYLE_REWRITE_INPUT_75.csv'),
      batch_sha256={p.name:sha(p) for p in sorted(batches.glob('*.csv'))},
      attempts='one candidate per ID; technical failure retries only, retain all receipts; no classifier-driven retries',
      new75_and_legacy30_are_different_protocol_cohorts=True,automatic_thresholds=dict(similarity=.85,bidirectional_nli=.6),
      existing_guards_and_style_metrics_unchanged=True))
    save(HERE/'REVIEWER_METADATA_TEMPLATE.csv',[dict(reviewer_type='',reviewer_id='',review_date='',model_version_if_llm='',
      text_version='',source_file='',assistance_used='',notes='')])
    dump(HERE/'SOURCE_HASHES.json',frozen)
    dump(HERE/'BUNDLE_AUDIT.json',dict(train_sources=105,proposed_counts=dict(__import__('collections').Counter(r['label'] for r in rows)),
      missing_style=75,legacy_style=30,unique_missing_ids=75,unique_missing_texts=75,all_train_authors=True,test_rows_exported=0,
      human_completed_file_found=False,human_import_status='Awaiting actual per-ID completed file; current templates blank; Claude review kept separate',
      new_generation_protocol=VERSION,legacy_generator_metadata_unknown=True,generation_executed=False,training_executed=False))
    templates=['NARRATIVE_LABEL_VALIDATION_105.csv','NARRATIVE_LABEL_VALIDATION_105.md',
      'HUMAN_PAIR_REVIEW_LEGACY30.csv','HUMAN_PAIR_REVIEW_LEGACY30.md',
      'HUMAN_PAIR_REVIEW_NEW75_TEMPLATE.csv','HUMAN_PAIR_REVIEW_NEW75_TEMPLATE.md',
      'GENERATION_METADATA_TEMPLATE.json','REVIEWER_METADATA_TEMPLATE.csv']
    dump(template_manifest,{name:sha(HERE/name) for name in templates})
    verify()
if __name__=='__main__':main()

"""Reuse exact frozen preservation engine/style metrics in an isolated output sink."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
from bundle import HERE,ROOT,FOLLOW,read,save,dump,sha,text_sha,verify,missing
STUDY=ROOT/'artifacts/experiments/style_intervention_v2_20261026'
def run_path(name):
    path=(HERE/'runs'/name).resolve()
    if path.parent!=(HERE/'runs').resolve():raise ValueError('Invalid run name')
    return path
def binding(name):
    path=run_path(name);rows=read(path/'received_rewrites_75.csv')
    if len(rows)!=75 or len({r['ID'] for r in rows})!=75:raise ValueError('Need exact75 ingested outputs')
    receipt=json.loads((path/'RECEIPT.json').read_text())
    if sha(path/'received_rewrites_75.csv')!=receipt['canonical_output_sha256']:raise ValueError('Output changed after receipt')
    expected={r['ID']:r for r in missing()}
    if {r['ID'] for r in rows}!=set(expected):raise ValueError('Wrong ID cohort')
    for r in rows:
        if r['Original']!=expected[r['ID']]['Original'] or r['source_sha256']!=text_sha(r['Original']) or r['rewrite_sha256']!=text_sha(r['ChatGPT_Style_Rewrite']):raise ValueError('Text binding mismatch')
    modules=[FOLLOW/'experiment.py',STUDY/'study.py',ROOT/'experiments/author_generalization/author_style_controlled.py']
    return path,rows,dict(semantic_similarity=.85,bidirectional_nli=.6,code_sha256={str(p.relative_to(ROOT)):sha(p) for p in modules},
      style_scaling_sha256=sha(STUDY/'style_feature_scaling.json'),classifier_predictions=False,thresholds_changed=False)
def screen(name,dry_run=False):
    verify();path,rows,identity=binding(name)
    if dry_run:return identity
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    out=path/'automatic_qc';out.mkdir(exist_ok=True)
    cohort={r['row_id']:r for r in read(FOLLOW/'analysis_cohort.csv')}
    selected=[cohort[r['ID']] for r in rows]
    assert all(r['split']=='train' for r in selected)
    save(out/'analysis_cohort.csv',selected)
    generated=[dict(row_id=r['ID'],condition='Normalized',original=r['Original'],rewrite=r['ChatGPT_Style_Rewrite'],truncated=False,
      truncation_metadata_available=False,truncation_note='False is legacy interface default, not observed finish_reason; human review required') for r in rows]
    (out/'generated_rewrites.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in generated),encoding='utf-8')
    spec=importlib.util.spec_from_file_location('completion_frozen_style',STUDY/'study.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.OUT=out
    engine=helper.load_engine();assert engine.OUT==out and engine.base.OUT==out
    engine.validate()
    scaling=json.loads((STUDY/'style_feature_scaling.json').read_text())['scale']
    styles=[]
    for r in rows:
        metrics=helper.style_metrics(r['Original'],r['ChatGPT_Style_Rewrite'])
        a=engine.np.array(engine.style_features(r['Original']));b=engine.np.array(engine.style_features(r['ChatGPT_Style_Rewrite']))
        metrics['explicit_style_mean_abs_standardized_change']=float(engine.np.mean(engine.np.abs(b-a)/engine.np.array(scaling)))
        styles.append(dict(ID=r['ID'],**metrics))
    save(out/'style_metrics.csv',styles)
    dump(out/'VALIDATOR_IDENTITY.json',identity)
    verify();return identity
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    print(json.dumps(screen(a.run,a.dry_run),indent=2))

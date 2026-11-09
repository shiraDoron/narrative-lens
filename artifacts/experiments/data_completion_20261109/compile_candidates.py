"""Bridge received75 + unchanged legacy30 to all105 draft A-E inputs; never approve/train."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
from bundle import HERE,ROOT,PREP,VERSION,mapping,legacy,save,dump,verify
from import_review import registry

def compile_run(name):
    verify();received=registry('pairs75',name)
    run=(HERE/'runs'/name).resolve();out=run/'candidate_105'
    if out.exists():raise ValueError('Candidate snapshot is immutable; do not overwrite')
    rows=[]
    for r in mapping():
        row=dict(r)
        if r['ID'] in received:
            assert not r['Style'] and r['Original']==received[r['ID']]['Original']
            row['Style']=received[r['ID']]['Style'];row['style_protocol_cohort']=VERSION
        else:
            assert r['ID'] in legacy() and r['Style']==legacy()[r['ID']]['Style']
            row['style_protocol_cohort']='legacy_chatgpt30_20261102_unknown_prompt'
        row['training_ready']=False;rows.append(row)
    assert len(rows)==105 and len({r['ID'] for r in rows})==105 and all(r['split']=='train' and r['Style'] and r['Paraphrase'] for r in rows)
    spec=importlib.util.spec_from_file_location('frozen_main_prep_schedules',PREP/'prepare.py')
    prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
    out.mkdir()
    save(out/'CANDIDATE_ID_MAP_105.csv',rows)
    for arm,variants in prep.ARMS.items():
        view=[dict(ID=r['ID'],author=r['author'],label=r['label'],label_status='machine proposal, human/QC pending',
          variant=v,text=r[v],style_protocol_cohort=r['style_protocol_cohort']) for r in rows for v in variants]
        save(out/f'DRAFT_ARM_{arm}.csv',view)
        for seed in prep.SEEDS:
            cfg=json.loads((PREP/f'CONFIG_{arm}_seed{seed}.json').read_text())
            cfg.update(n_sources=105,n_examples=len(view),optimizer_updates=140,processed_examples=2240,
              schedule=f'SCHEDULE_{arm}_seed{seed}.csv',training_ready=False,
              readiness_reason='Received generation is not human-gold/QC approval; mixed legacy/extension protocol must be recorded')
            dump(out/f'CONFIG_{arm}_seed{seed}.json',cfg)
            save(out/cfg['schedule'],prep.schedules(view,seed,140))
    dump(out/'STATUS.json',dict(n_sources=105,conditions=5,legacy30_unchanged=True,new75_received=True,
      mixed_protocol=True,training_ready=False,source_label_gold_not_assumed=True,no_training=True,no_test_evaluation=True))
    verify();return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
    try:print(compile_run(a.run))
    except (ValueError,AssertionError,FileNotFoundError) as e:p.error(str(e))

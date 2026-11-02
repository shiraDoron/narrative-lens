"""Import supplied ChatGPT outputs unchanged; reuse frozen v2/v3 screening."""
from pathlib import Path
import argparse, collections, csv, hashlib, importlib.util, json, math, shutil, subprocess, sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
STUDY=ROOT/'artifacts/experiments/style_intervention_v2_20261026'
V2=STUDY/'train_prompt_revision_30_20261101'
V3=STUDY/'train_prompt_revision_v3_30_20261102'
PREVIOUS=ROOT/'artifacts/experiments/verified_human_style_followup_20261026'
RAW='CHATGPT_STYLE_REWRITE_30_20261102.csv'
ALLOWED_DOCS={STUDY/'EXPERIMENT_GUIDE_HE.md',STUDY/'FINAL_REPORT_HE.md'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf8'))
def dump(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def records(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def inherited():
    spec=importlib.util.spec_from_file_location('frozen_v2_helpers',V2/'run.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT;return m
def protected():
    hashes=read('protected_inputs_sha256.json')
    bad=[n for n,h in hashes.items() if ROOT/n not in ALLOWED_DOCS and sha(ROOT/n)!=h]
    assert not bad,bad
    assert sha(OUT/RAW)==read('protocol.json')['received_file_sha256']
    return len(hashes)
def prepare(source):
    if (OUT/'protocol.json').exists():
        protected()
        if source:assert sha(source)==sha(OUT/RAW)
        return
    assert source and source.is_file(), 'Supply the received CSV once via --source'
    if (OUT/RAW).exists():assert sha(source)==sha(OUT/RAW)
    else:shutil.copyfile(source,OUT/RAW)
    imported=records(OUT/RAW);assert len(imported)==30
    assert all(set(r)=={'id','chatgpt_style_rewrite'} for r in imported)
    assert len({r['id'] for r in imported})==30 and all(r['chatgpt_style_rewrite'].strip() for r in imported)
    cohort=records(V2/'analysis_cohort.csv');before={r['ID']:r for r in records(V2/'comparison_30.csv')}
    incoming={r['id']:r['chatgpt_style_rewrite'] for r in imported}
    v3={r['row_id']:r for r in [json.loads(s) for s in (V3/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]}
    assert set(incoming)==set(before)==set(v3)=={r['row_id'] for r in cohort}
    rows=[]
    for r in cohort:
        rid=r['row_id'];assert r['split']=='train' and r['text']==before[rid]['Original']==v3[rid]['original']
        rows.append(dict(ID=rid,Original=r['text'],v2=before[rid]['New_Normalized'],v3=v3[rid]['rewrite'],ChatGPT_Style_Rewrite=incoming[rid],split='train',label=r['narrative_name']))
    write('analysis_cohort.csv',cohort);write('frozen_comparison_inputs.csv',rows)
    with (OUT/'generated_rewrites.jsonl').open('w',encoding='utf8') as f:
        for r in rows:f.write(json.dumps(dict(row_id=r['ID'],condition='Normalized',original=r['Original'],rewrite=r['ChatGPT_Style_Rewrite'],truncated=False,engine='Imported user-supplied ChatGPT output; no generation performed here'),ensure_ascii=False)+'\n')
    tracked=subprocess.check_output(['git','ls-files','artifacts/experiments/style_intervention_v2_20261026'],cwd=ROOT,text=True).splitlines()
    refs=[ROOT/n for n in tracked]+[V2/'run.py',PREVIOUS/'experiment.py',PREVIOUS/'author_splits.csv',PREVIOUS/'split_definitions.csv',ROOT/'experiments/author_generalization/author_style_controlled.py']
    dump('protected_inputs_sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in refs if p.is_file()})
    dump('protocol.json',dict(scope='same frozen 30 TRAIN originals, externally generated ChatGPT rewrites; screening only',received_filename=RAW,received_file_sha256=sha(OUT/RAW),original_only_generation='user-reported; request history not supplied',no_v2_v3_guards_or_prior_reviews_used_during_generation='user-reported; not independently auditable from CSV',generator_name='ChatGPT (user-reported)',generator_model_version=None,generator_prompt=None,generator_decoding=None,generation_run_here=False,output_editing=False,reviews_used_for_screening=False,external_review_performed=False,human_validation=False,training=False,test_evaluation=False,semantic_threshold=.85,nli_threshold=.6,legacy_condition='Normalized for unchanged validator compatibility',truncation_metadata_available=False,legacy_truncated_flag=False,truncation_note='False is an interface default, not an observed finish_reason. guard_complete cannot independently certify external generation completeness.',style_metrics='Inherited style_metrics + 66 frozen standardized feature deltas; no scaling refit',row_count=30))
    dump('validator_identity_audit.json',dict(unchanged_code_sha256={str(p.relative_to(ROOT)):sha(p) for p in [V2/'run.py',STUDY/'study.py',PREVIOUS/'experiment.py',ROOT/'experiments/author_generalization/author_style_controlled.py',STUDY/'style_feature_scaling.json']},thresholds=dict(similarity=.85,bidirectional_nli=.6)))
    print('Imported 30 unique TRAIN IDs; received bytes and rewrite strings preserved.',flush=True)
def validate():
    protected();inherited().validate();protected()
def table(headers,rows):
    def c(v):return str(v).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(c(v) for v in r)+' |' for r in rows])
def report():
    protected();m=inherited();helper=m.imported_style_module();engine=helper.load_engine();np=engine.np
    rows=records(OUT/'frozen_comparison_inputs.csv');metrics=[];explicit=[];comparisons=[];flag_changes=[]
    screens={v:{r['row_id']:r for r in records(p/'rewrite_validation.csv') if r['condition']=='Normalized'} for v,p in [('v2',V2),('v3',V3),('ChatGPT',OUT)]}
    saved_styles={v:{r['ID']:r for r in records(V3/'style_metrics_v2_v3.csv') if r['version']==v} for v in ('v2','v3')}
    scaling=json.loads((STUDY/'style_feature_scaling.json').read_text(encoding='utf8'));scale=np.array(scaling['scale']);assert len(scale)==len(scaling['names'])==66
    totals={v:dict(preservation_pass=0,substantial_style=0,both=0,exact_copies=0) for v in ('v2','v3','ChatGPT')}
    diagnostics=[]
    def truth(v):return str(v).lower()=='true'
    for r in rows:
        rid=r['ID'];original=r['Original'];base=np.array(engine.style_features(original));row=dict(r)
        for version,text in [('v2',r['v2']),('v3',r['v3']),('ChatGPT',r['ChatGPT_Style_Rewrite'])]:
            screen=screens[version][rid];style=helper.style_metrics(original,text);features=np.array(engine.style_features(text))
            style['explicit_style_mean_abs_standardized_change']=float(np.mean(np.abs(features-base)/scale))
            metrics.append(dict(ID=rid,version=version,**style))
            if version!='ChatGPT':
                for k,v in style.items():
                    old=saved_styles[version][rid][k]
                    if isinstance(v,bool):assert truth(old)==v,(rid,k)
                    elif isinstance(v,(float,int)):assert math.isclose(float(old),v,rel_tol=1e-10,abs_tol=1e-10),(rid,k)
                    else:assert old==v,(rid,k)
            for name,a,b in zip(scaling['names'],base,features):explicit.append(dict(ID=rid,version=version,feature=name,original=float(a),rewrite=float(b),delta=float(b-a)))
            passed=truth(screen['passed']);substantial=style['substantial_style_change']
            row.update({version+'_preservation_pass':passed,version+'_substantial_style':substantial,version+'_both':passed and substantial,version+'_exact_copy':style['exact_copy'],version+'_guards_json':json.dumps(screen,ensure_ascii=False),version+'_style_metrics_json':json.dumps(style,ensure_ascii=False)})
            totals[version]['preservation_pass']+=passed;totals[version]['substantial_style']+=substantial;totals[version]['both']+=passed and substantial;totals[version]['exact_copies']+=style['exact_copy']
        sets={v:set(filter(None,screens[v][rid]['rejection_reasons'].split('|'))) for v in screens}
        new=sets['ChatGPT']-(sets['v2']|sets['v3']);row['new_failures_vs_both_prior_versions']='|'.join(sorted(new))
        for v in ('v2','v3'):
            a=(row['ChatGPT_preservation_pass'],row['ChatGPT_substantial_style']);b=(row[v+'_preservation_pass'],row[v+'_substantial_style'])
            outcome='unchanged' if a==b else 'improved' if all(x>=y for x,y in zip(a,b)) else 'worsened' if all(x<=y for x,y in zip(a,b)) else 'mixed'
            row['automatic_outcome_vs_'+v]=outcome
            flag_changes.append(dict(ID=rid,baseline=v,automatic_outcome=outcome,new_guard_failures='|'.join(sorted(sets['ChatGPT']-sets[v])),resolved_guard_failures='|'.join(sorted(sets[v]-sets['ChatGPT']))))
        diagnostics.append(dict(ID=rid,new_failures_vs_both_prior_versions=row['new_failures_vs_both_prior_versions'],ChatGPT_rejection_reasons=screens['ChatGPT'][rid]['rejection_reasons'],automatic_outcome_vs_v2=row['automatic_outcome_vs_v2'],automatic_outcome_vs_v3=row['automatic_outcome_vs_v3']))
        comparisons.append(row)
    assert totals['v2']==dict(preservation_pass=6,substantial_style=24,both=6,exact_copies=0)
    assert totals['v3']==dict(preservation_pass=9,substantial_style=26,both=9,exact_copies=0)
    write('comparison_v2_v3_chatgpt_30.csv',comparisons);write('style_metrics_v2_v3_chatgpt.csv',metrics);write('explicit_style_changes_v2_v3_chatgpt.csv',explicit);write('automatic_flag_changes.csv',flag_changes);write('automatic_diagnostics_30.csv',diagnostics)
    counts={v:collections.Counter(reason for r in screens[v].values() for reason in r['rejection_reasons'].split('|') if reason) for v in screens}
    all_reasons=sorted(set().union(*(c.keys() for c in counts.values())))
    reason_rows=[dict(guard=k,v2=counts['v2'][k],v3=counts['v3'][k],ChatGPT=counts['ChatGPT'][k],new_guard_type_in_ChatGPT=counts['ChatGPT'][k]>0 and counts['v2'][k]==counts['v3'][k]==0) for k in all_reasons]
    write('guard_failure_counts.csv',reason_rows)
    dump('summary.json',dict(n=30,totals=totals,failure_counts={v:dict(c.most_common()) for v,c in counts.items()},new_guard_types=[r['guard'] for r in reason_rows if r['new_guard_type_in_ChatGPT']],new_id_guard_failures=[r for r in diagnostics if r['new_failures_vs_both_prior_versions']],outcomes={v:dict(collections.Counter(r['automatic_outcome_vs_'+v] for r in comparisons)) for v in ('v2','v3')},semantic_success_established=False,external_review='Pending',human_validation='Pending'))
    matrix=table(['Metric','v2','v3','ChatGPT Rewrite'],[[name]+[f"{totals[v][key]}/30" for v in ('v2','v3','ChatGPT')] for name,key in [('automated preservation pass','preservation_pass'),('substantial style change','substantial_style'),('both preservation + style','both'),('exact copies','exact_copies')]])
    md='# Original / v2 / v3 / ChatGPT — 30 TRAIN examples\n\nAutomated signals only; no output was edited. Full guard/metric fields are in the paired CSV.\n\n'
    md+=table(['ID','Original','v2','v3','ChatGPT Rewrite','ChatGPT guards failed','ChatGPT style metrics'],[[r['ID'],r['Original'],r['v2'],r['v3'],r['ChatGPT_Style_Rewrite'],screens['ChatGPT'][r['ID']]['rejection_reasons'] or 'none',r['ChatGPT_style_metrics_json']] for r in comparisons])+'\n'
    (OUT/'COMPARISON_30.md').write_text(md,encoding='utf8')
    # Blind package contains ONLY these three fields; no guard/style/review metadata.
    blind='\n\n'.join('## '+r['ID']+'\n\n### Original\n\n'+r['Original']+'\n\n### ChatGPT Style Rewrite\n\n'+r['ChatGPT_Style_Rewrite'] for r in rows)+'\n'
    (OUT/'REVIEW_PACKAGE_BLIND_30.md').write_text(blind,encoding='utf8')
    report_text='# ChatGPT Style Rewrite — 30 train examples\n\n'
    report_text+='ניסוי generator חלופי על אותם 30 Original מ־train. ה־CSV התקבל מהמשתמש; לפי דיווחו ChatGPT ראה Original בלבד ולא ראה v2/v3, guards או review קודם. אין request history, גרסת מודל מדויקת, prompt מלא או decoding settings לאימות עצמאי. כאן לא נוצרו שכתובים ולא שונה שום output.\n\n'+matrix+'\n\n'
    report_text+='## מגבלות והפרדת מקורות ראיה\n\nAutomated pass הוא signal בלבד, לא קביעה שהמשמעות נשמרה. substantial הוא proxy תפעולי, לא הוכחה לשינוי author style. Human Validation ו־External LLM Review חדשים לא בוצעו; שניהם Pending. אין מכאן מסקנת generalization או הצלחת פתרון. השוואת generator אינה ניסוי מבוקר בגרסת מודל/תקציב/decoding: פרטים אלה חסרים ל־ChatGPT.\n\n'
    report_text+='לא סופקו finish_reason או פרטי truncation: שדה truncated=False הוא ברירת ממשק ל־validator הקיים, ולא ראיה שהדור החיצוני הסתיים. בדיקות אורך הקלט המלא פועלות ללא שינוי; guard_complete אינו יכול לאמת עצמאית השלמת generation חיצוני.\n\n'
    report_text+='## כשלי guards\n\n'+table(['guard','v2','v3','ChatGPT','new guard type'],[[r[k] for k in ('guard','v2','v3','ChatGPT','new_guard_type_in_ChatGPT')] for r in reason_rows])+'\n\n'
    report_text+='סוג guard חדש מוגדר ככשל שלא הופיע בשום ID ב־v2 או v3. בנפרד, כשל חדש ברמת ID הוא guard שנכשל כאן לאותו ID אך עבר בשתי הגרסאות הקודמות; אין בכך כשלעצמו הוכחה ל־drift חדש.\n\n'
    new_id_rows=[r for r in diagnostics if r['new_failures_vs_both_prior_versions']]
    report_text+='לא הופיע סוג guard חדש ברמה הגלובלית. כשלי ID/guard חדשים הופיעו ב־'+str(len(new_id_rows))+' דוגמאות: '+', '.join(r['ID']+' ('+r['new_failures_vs_both_prior_versions']+')' for r in new_id_rows)+'.\n\n'
    maximum=max(counts['ChatGPT'].values(),default=0)
    report_text+='כשלי ה־guards השכיחים ביותר ב־ChatGPT: '+', '.join(k for k,v in counts['ChatGPT'].items() if v==maximum)+' — '+str(maximum)+' דוגמאות לכל guard (ייתכנו כמה כשלי guard לאותה רשומה).\n\n'
    report_text+='## השוואה אוטומטית לפי ID\n\nOutcome מבוסס Pareto על שני דגלים בלבד: preservation pass ו־substantial style. improved/worsened משמעם שיפור/ירידה בדגל אחד לפחות בלי תנועה הפוכה באחר; mixed משמעו trade-off; unchanged אינו שקילות טקסטים או סיכונים. עוצמת המדדים וכשלי guard מפורטים נשמרו בנפרד.\n\n'
    report_text+=table(['Baseline','improved','worsened','unchanged','mixed'],[[v]+[sum(r['automatic_outcome_vs_'+v]==outcome for r in diagnostics) for outcome in ('improved','worsened','unchanged','mixed')] for v in ('v2','v3')])+'\n\n'
    report_text+=table(['ID','ChatGPT failures','new vs both','vs v2','vs v3'],[[r['ID'],r['ChatGPT_rejection_reasons'] or 'none',r['new_failures_vs_both_prior_versions'] or 'none',r['automatic_outcome_vs_v2'],r['automatic_outcome_vs_v3']] for r in diagnostics])+'\n\n'
    report_text+='ברמה האוטומטית יש יותר מעברי preservation ושני התנאים יחד לעומת v2/v3, אך פחות substantial-style flags. זו עדות לאיזון תפעולי אחר, לא הוכחה לשימור משמעות או להסרת סגנון כותב.\n\n'
    report_text+='## תוצרים ועצירה\n\n[השוואת טקסטים](COMPARISON_30.md), [CSV מזווג](comparison_v2_v3_chatgpt_30.csv), [כל מדדי style](style_metrics_v2_v3_chatgpt.csv), [66 מאפיינים](explicit_style_changes_v2_v3_chatgpt.csv), [guards](rewrite_validation.csv), [blind package](REVIEW_PACKAGE_BLIND_30.md), [שחזור](REPRODUCTION.md). חבילת הביקורת כוללת רק ID, Original ו־ChatGPT Style Rewrite, ללא מחבר, labels, גרסאות קודמות או מדדים. לא בוצע review כחלק מהריצה.\n\nכל 30 הרשומות הן train; התוויות, החלוקה, השדות האנושיים הקודמים, guards, thresholds ו־scaling לא שונו. לא בוצעו retraining, LoRA או test evaluation. עוצרים לפני External LLM Review עצמאי.\n'
    (OUT/'REPORT_HE.md').write_text(report_text,encoding='utf8')
    # Verify strings against the raw import and deterministic replay of blind contents.
    incoming={r['id']:r['chatgpt_style_rewrite'] for r in records(OUT/RAW)}
    generated={r['row_id']:r for r in [json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]}
    assert all(incoming[r['ID']]==r['ChatGPT_Style_Rewrite']==generated[r['ID']]['rewrite'] for r in rows)
    for r in rows:assert ('### Original\n\n'+r['Original']+'\n\n### ChatGPT Style Rewrite\n\n'+incoming[r['ID']]) in blind
    human=records(OUT/'rewrite_human_review.csv');fields=['facts_preserved','stance_preserved','framing_preserved','negation_preserved','certainty_preserved','attribution_preserved','entities_preserved','style_changed','acceptable','notes']
    assert len(human)==30 and all(not r[k] for r in human for k in fields)
    dump('integrity_audit.json',dict(raw_bytes_sha256=sha(OUT/RAW),all_30_rewrite_strings_unchanged=True,all_30_originals_match=True,ids_unique_train_only=True,v2_v3_style_recomputed_identically=True,blind_package_sha256=sha(OUT/'REVIEW_PACKAGE_BLIND_30.md'),blind_content_exact=True,blank_new_review_templates=True,protected_file_count=protected(),review_performed=False))
    print(json.dumps(totals),flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','validate','report'],required=True);p.add_argument('--source',type=Path);a=p.parse_args()
    prepare(a.source) if a.stage=='prepare' else globals()[a.stage]()
if __name__=='__main__':main()

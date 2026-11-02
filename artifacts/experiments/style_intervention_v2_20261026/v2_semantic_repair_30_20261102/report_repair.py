"""Descriptive repair-report construction only, using frozen output/guard scores."""
from pathlib import Path
import collections
import difflib
import hashlib
import json
import math
import re
import csv

from run import OUT, STUDY, ROOT, V2, V3, PREVIOUS, CATEGORIES, helper, check_protected, apply_edits, schema


def table(headers,rows):
    def c(x):return str(x).replace('|','\\|').replace('\n','<br>')
    return '\n'.join('| '+' | '.join(map(c,r))+' |' for r in [headers,['---']*len(headers),*rows])


def quotes(t):return [a or b for a,b in re.findall(r'"([^"\n]+)"|“([^”\n]+)”',t)]


def main():
    m=helper();nprotected=check_protected(m)
    protocol=m.read('protocol.json')
    assert m.sha(OUT/'SEMANTIC_VERIFICATION_PROMPT.txt')==protocol['verification_prompt_sha256']
    assert m.sha(OUT/'SEMANTIC_REPAIR_PROMPT.txt')==protocol['repair_prompt_sha256']
    helper_style=m.imported_style_module();engine=helper_style.load_engine();np=engine.np
    inputs={r['ID']:r for r in m.records(OUT/'frozen_inputs.csv')}
    raw=[json.loads(s) for s in (OUT/'model_stage_outputs.jsonl').read_text(encoding='utf8').splitlines()]
    repaired={r['ID']:r for r in m.records(OUT/'repaired_outputs.csv')}
    verification={r['ID']:r for r in m.records(OUT/'verification_results.csv')}
    v2={r['ID']:r for r in m.records(V2/'comparison_30.csv')}
    v3={r['ID']:r for r in m.records(V3/'comparison_v2_v3_30.csv')}
    validation={r['row_id']:r for r in m.records(OUT/'rewrite_validation.csv')}
    assert len(raw)==len(inputs)==len(repaired)==len(validation)==30
    scaling=json.loads((STUDY/'style_feature_scaling.json').read_text(encoding='utf8'));scale=np.array(scaling['scale'])
    rows=[];metrics=[];explicit=[];editrows=[];request_audit=[]
    for r in raw:
        rid=r['ID'];original=inputs[rid]['Original'];rewrite=inputs[rid]['New_Normalized_v2']
        assert r['Original']==original==v2[rid]['Original']==v3[rid]['Original'] and inputs[rid]['split']=='train'
        assert r['v2_rewrite']==rewrite==v2[rid]['New_Normalized']
        assert r['verification']['request_data']==dict(Original=original,Rewrite=rewrite)
        if r['repair']:
            assert r['repair']['request_data']==dict(Original=original,Rewrite=rewrite,verification=r['verification']['parsed'])
        for call in [r['verification']]+([r['repair']] if r['repair'] else []):
            stage=call['stage'];promptfile='SEMANTIC_VERIFICATION_PROMPT.txt' if stage=='verification' else 'SEMANTIC_REPAIR_PROMPT.txt'
            payload=dict(messages=[dict(role='system',content=(OUT/promptfile).read_text(encoding='utf8')),
                dict(role='user',content=json.dumps(call['request_data'],ensure_ascii=False))],
                temperature=0,seed=20261026,max_tokens=1536 if stage=='verification' else 1024,
                repeat_penalty=1.,top_k=1,top_p=1.,min_p=0.,cache_prompt=True,
                response_format=dict(type='json_schema',json_schema=dict(name=stage,strict=True,schema=schema(stage))))
            assert hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()==call['request_sha256']
        reproduced,edits,errors=apply_edits(rewrite,r['applied_edits'],(r['verification']['parsed'] or {}).get('issues',[]))
        assert reproduced==r['repaired'] and not errors
        request_audit.append(dict(ID=rid,verification_input_original_and_v2_only=True,
            repair_received_detected_findings=r['repair'] is not None,patch_reconstruction_matches=True))
        row=dict(ID=rid,split='train',Original=original,New_Normalized_v2=rewrite,New_Normalized_v3=v3[rid]['New_v3'],Repaired_v2=r['repaired'],
            verification_issues_json=verification[rid]['issues_json'],verification_errors='|'.join(r['verification_errors']),
            repairs_applied_json=json.dumps(r['applied_edits'],ensure_ascii=False),patch_errors='|'.join(r['patch_errors']),
            repair_requested=r['repair'] is not None,changed=r['changed'],verification_is_not_external_review=True,human_verified=False)
        original_features=np.array(engine.style_features(original))
        for version,text,screen in [('v2',rewrite,json.loads(v2[rid]['new_validation_json'])),
              ('v3',v3[rid]['New_v3'],json.loads(v3[rid]['v3_automatic_checks_json'])),('repair',r['repaired'],validation[rid])]:
            style=helper_style.style_metrics(original,text);features=np.array(engine.style_features(text))
            style['explicit_style_mean_abs_standardized_change']=float(np.mean(np.abs(features-original_features)/scale))
            metrics.append(dict(ID=rid,version=version,**style))
            for name,a,b in zip(scaling['names'],original_features,features):explicit.append(dict(ID=rid,version=version,feature=name,original=float(a),rewrite=float(b),delta=float(b-a)))
            row[version+'_preservation_pass']=str(screen['passed']).lower()=='true'
            row[version+'_substantial_style']=style['substantial_style_change'];row[version+'_exact_copy']=style['exact_copy']
            row[version+'_both']=row[version+'_preservation_pass'] and style['substantial_style_change']
            row[version+'_rejection_reasons']=screen['rejection_reasons']
            row[version+'_guard_results_json']=json.dumps(screen,ensure_ascii=False)
            row[version+'_style_metrics_json']=json.dumps(style,ensure_ascii=False)
        editmetrics=helper_style.style_metrics(rewrite,r['repaired'])
        row['repair_word_edit_fraction_from_v2']=editmetrics['word_edit_fraction']
        row['v2_verbatim_quotes_preserved']=sorted(quotes(original))==sorted(quotes(rewrite))
        row['repair_verbatim_quotes_preserved']=sorted(quotes(original))==sorted(quotes(r['repaired']))
        row['original_exact_copy_after_repair']=original==r['repaired']
        before_flags=set(row['v2_rejection_reasons'].split('|'))-{''}
        after_flags=set(row['repair_rejection_reasons'].split('|'))-{''}
        row['removed_guard_flags']='|'.join(sorted(before_flags-after_flags))
        row['added_guard_flags']='|'.join(sorted(after_flags-before_flags))
        rows.append(row)
        for e in r['applied_edits']:
            issue=r['verification']['parsed']['issues'][e['issue_index']]
            editrows.append(dict(ID=rid,category=issue['category'],old=e['old'],new=e['new'],
                verification_explanation=issue['explanation'],issue_index=e['issue_index']))
    m.write_csv('comparison_v2_v3_repair.csv',rows);m.write_csv('style_metrics_v2_v3_repair.csv',metrics)
    m.write_csv('explicit_style_changes_v2_v3_repair.csv',explicit)
    if editrows:m.write_csv('repairs_applied.csv',editrows)
    else:
        with (OUT/'repairs_applied.csv').open('w',encoding='utf-8-sig',newline='') as f:
            csv.writer(f).writerow(['ID','category','old','new','verification_explanation','issue_index'])
    totals={v:dict(automated_preservation_pass=sum(r[v+'_preservation_pass'] for r in rows),substantial_style_change=sum(r[v+'_substantial_style'] for r in rows),
        both=sum(r[v+'_both'] for r in rows),exact_copies=sum(r[v+'_exact_copy'] for r in rows)) for v in ['v2','v3','repair']}
    assert list(totals['v2'].values())==[6,24,6,0] and list(totals['v3'].values())==[9,26,9,0]
    category_counts=collections.Counter(e['category'] for e in editrows if e['old']!=e['new'])
    summary=dict(n=30,scope='train-only intervention development',totals=totals,
        verification_invalid_ids=[r['ID'] for r in raw if r['verification_errors']],
        repair_invalid_ids=[r['ID'] for r in raw if r['patch_errors']],
        verification_call_count=30,repair_call_count=sum(r['repair'] is not None for r in raw),
        issue_category_marked_preserved_count=sum(i['category'] in (r['verification']['parsed'] or {}).get('checks',{}) and
            r['verification']['parsed']['checks'][i['category']]=='preserved' for r in raw for i in (r['verification']['parsed'] or {}).get('issues',[])),
        changed_count=sum(r['changed'] for r in raw),applied_edit_count=len(editrows),repair_categories=dict(category_counts),
        fallback_count=sum(bool(r['verification_errors'] or r['patch_errors']) for r in raw),
        fallback_ids=[r['ID'] for r in raw if r['verification_errors'] or r['patch_errors']],
        process_completed_without_contract_error=sum(not r['verification_errors'] and not r['patch_errors'] for r in raw),
        actually_changed_ids=[r['ID'] for r in raw if r['changed']],
        changed_subset_automatic=dict(n=sum(r['changed'] for r in rows),pass_count=sum(r['changed'] and r['repair_preservation_pass'] for r in rows),
            substantial_style_count=sum(r['changed'] and r['repair_substantial_style'] for r in rows),
            both_count=sum(r['changed'] and r['repair_both'] for r in rows)),
        effective_edit_count=sum(e['old']!=e['new'] for e in editrows),noop_edit_count=sum(e['old']==e['new'] for e in editrows),
        both_ids=[r['ID'] for r in rows if r['repair_both']],
        guard_pass_gained_ids=[r['ID'] for r in rows if r['repair_preservation_pass'] and not r['v2_preservation_pass']],
        guard_pass_lost_ids=[r['ID'] for r in rows if not r['repair_preservation_pass'] and r['v2_preservation_pass']],
        exact_quote_failures=[r['ID'] for r in rows if not r['repair_verbatim_quotes_preserved']],
        verification_truncated=sum(r['verification']['truncated'] for r in raw),repair_truncated=sum(r['repair']['truncated'] for r in raw if r['repair']),
        mean_word_edit_fraction_from_v2=sum(r['repair_word_edit_fraction_from_v2'] for r in rows)/30,
        external_review='Pending; not performed',human_validation='Pending; not performed',no_training=True,no_test_evaluation=True)
    m.dump('summary.json',summary);m.dump('request_integrity_audit.json',dict(all_passed=True,checks=request_audit,
        no_previous_reviews_ids_labels_or_scores_sent=True,no_first_stage_regeneration=True))
    m.dump('implementation_manifest.json',dict(
        orchestration_code_sha256=m.sha(OUT/'run.py'),report_code_sha256=m.sha(Path(__file__)),
        verification_prompt_sha256=m.sha(OUT/'SEMANTIC_VERIFICATION_PROMPT.txt'),repair_prompt_sha256=m.sha(OUT/'SEMANTIC_REPAIR_PROMPT.txt'),
        runtime_sha256=m.sha(PREVIOUS/'runtime_llama/llama-server.exe'),model=m.read('generator_manifest.json'),
        response_format='json_schema',verification_max_tokens=1536,repair_max_tokens=1024,
        no_model_retry=True,final_guard_source_unchanged=True))
    blind=[]
    for r in rows:blind.extend([f"## {r['ID']}",'','### Original','',r['Original'],'','### Repaired v2','',r['Repaired_v2'],''])
    (OUT/'REVIEW_PACKAGE_BLIND_30.md').write_text('\n'.join(blind),encoding='utf8')
    comparison=table(['ID','Original','v2','Repaired v2','verification issues','repairs applied','repair guards','repair style'],
        [[r[k] for k in ['ID','Original','New_Normalized_v2','Repaired_v2','verification_issues_json','repairs_applied_json','repair_rejection_reasons','repair_substantial_style']] for r in rows])
    (OUT/'COMPARISON_30.md').write_text('# Fixed v2 versus targeted semantic repair — TRAIN only\n\n'+comparison+'\n',encoding='utf8')
    focused={'creators:'+s for s in ['120669','423315','421951','417181','8b0d99b23d03','423545','298495','418904','418827','459e183c1d0d']}
    report='''# v2 + Semantic Verification and Targeted Repair — 30 TRAIN examples

## למה עברנו לשני שלבים

v3 attempted to encode more semantic-preservation constraints in a single rewrite prompt, but external review showed overall degradation relative to v2. Therefore the next experiment separates style rewriting from semantic verification and minimal repair.

זהו **train-only intervention development**, לא final/test result, לא Human Validation ולא הוכחה להכללה משופרת. v2 הוא baseline הפיתוח המועדף לפי הסקירות שסופקו, בכפוף להבדלי מעריכים/הקשר. קלט שלב השכתוב הראשון הוא v2 הקיים: לא נוצר שכתוב ראשוני חדש.

## מה הורץ

אותו Qwen2.5-3B-Instruct Q4_K_M מקומי בשני תפקידים: verification על Original/v2, ואז repair מותנה על Original/v2/ממצאי האימות. נבדקו 17 קטגוריות ב־preserved/not_preserved/borderline. לא הועברו IDs, תוויות, ציונים או דירוגי External LLM Review. האימות המקומי הוא חלק ממערכת ההתערבות, **לא External LLM Review עצמאי**; אין להציג את preserved שלו כאישור משמעות.

ה־repair מחזיר patches ולא פסקה חדשה. רק החלפות של spans ייחודיים שאינם חופפים מיושמות, ללא החלפת כל הטקסט. אין בחירת מועמד לפי guards ואין retries לשיפור איכות. אם JSON/ראיות/patch אינו תקין, נשמר v2 והרשומה מסומנת ככשל תהליך, לא כהצלחת תיקון. זהו חוזה הפעלת patch, לא שינוי של automated filtering הקיים.

המודל/כימות נשמרו, אך זהו ניסוי ארכיטקטורת pipeline חדש: schema-constrained JSON, שני prompts, תקציבי פלט 1536/1024 ו־context של 16384 בארבעה slots. אין לייחס הבדל בתוצאה רק לנוסח prompt אחד. ה־guards, ספי MPNet≥0.85 / NLI≥0.6, קוד NER/lexical, מדדי style ו־66 מאפיינים וה־scaling נשארו ללא שינוי.

## תוצאות אוטומטיות בלבד

'''
    report+=table(['Metric','v2','v3','v2 + Repair'],[[k,totals['v2'][k],totals['v3'][k],totals['repair'][k]] for k in totals['v2']])
    report+='\n\n'+table(['Process measure','Value'],[[k,summary[k]] for k in ['repair_call_count','changed_count','fallback_count','process_completed_without_contract_error','changed_subset_automatic','applied_edit_count','effective_edit_count','noop_edit_count','verification_invalid_ids','repair_invalid_ids','verification_truncated','repair_truncated','issue_category_marked_preserved_count','mean_word_edit_fraction_from_v2']])
    report+='\n\nהטבלה הראשית כוללת את כל 30 הקלטים, גם fallback ל־v2. changed_subset_automatic הוא תיאור נפרד של הטקסטים שבהם הוחל שינוי, לא השוואה סיבתית או קבוצה שנבחרה לפי איכות. כאשר fallback גבוה, דמיון ל־baseline אינו ראיה שה־repair עובד: לעיתים לא הייתה התערבות בפועל. כשלי JSON/ראיות/patch מעידים על מגבלת מימוש/מודל בניסוי הזה, ואינם מפריכים כשלעצמם את הרעיון הדו־שלבי.\n\n'
    report+=f"**מסקנת המימוש הנוכחי:** רק {summary['changed_count']}/30 טקסטים השתנו, ו־{summary['fallback_count']}/30 נשמרו ללא תיקון בגלל כשל בחוזה התהליך. לכן לא הודגם שיפור בשימור סמנטי, ואין בסיס לאמץ את המימוש הזה כ־semantic repair אמין. גם התיקון שהוחל דורש בדיקה חיצונית; אין להסיק מכאן שהארכיטקטורה הדו־שלבית כשלעצמה אינה יכולה לעבוד.\n\n"
    report+='\n\nשינוי word_edit_fraction ביחס ל־v2 מתאר את היקף ההתערבות, לא מוכיח minimality אופטימלית. כל עריכה מיושמת נשמרת ב־[repairs_applied.csv](repairs_applied.csv). תיקון יכול להחזיר ביטויי מקור ולהפחית style; exact copies ביחס ל־Original מסוכמים בנפרד.\n\n'
    report+='## סוגי התיקונים שהוחלו\n\n'+table(['Verification issue category','Text-changing patch count'],sorted(category_counts.items()))
    report+='\n\n'+table(['ID','Detected category','Old span','New span','Caution'],
        [[e['ID'],e['category'],e['old'],e['new'],'Deletion: verify that no original claim was removed' if not e['new'] else 'Replacement: requires separate semantic review']
         for e in editrows if e['old']!=e['new']])
    report+='\n\n'+table(['Changed ID','Removed guard flags','Added guard flags'],
        [[r['ID'],r['removed_guard_flags'],r['added_guard_flags']] for r in rows if r['changed']])
    report+='\n\nב־417181 נעלם דגל certainty בעקבות מחיקת המשפט שמכיל allegedly, ונוסף bidirectional_nli. זהו מקרה שבו הסרת דגל אינה תיקון סמנטי: מילת marker נעלמה יחד עם הטענה כולה, והבדיקה הדו־כיוונית מסמנת סיכון לאי־שקילות. אין להציג זאת כשיפור certainty מאומת.\n\n'
    report+='\n\n## דוגמאות רגישות — ללא fixes לפי ID\n\n'
    report+=table(['ID','Verification issues','Applied repairs','Process errors','v2 pass','repair pass','repair style'],
        [[r[k] for k in ['ID','verification_issues_json','repairs_applied_json','patch_errors','v2_preservation_pass','repair_preservation_pass','repair_substantial_style']] for r in rows if r['ID'] in focused])
    report+='''

## האם נוצרו בעיות חדשות?

לא בוצעה בדיקה סמנטית חיצונית לאחר התיקון, ולכן אין כאן קביעה שאין drift חדש או ספירות No/Borderline חדשות. כל `old→new` ב־repairs_applied.csv הוא תצפית טקסטואלית לבדיקה; המודל המקומי יכול לפספס הפרות, להצביע על הפרה שגויה או להציע תיקון שמוסיף בעיה. דגלי guards שהתווספו אינם כשלעצמם הוכחה ל־drift, ומעבר אינו הוכחת תקינות. כשל תהליך נשאר מפורש, בלי להסתירו באמצעות הפקת מועמד נוסף. החבילה העיוורת מוכנה לשלב הבא בלבד.

בפרט, מחיקת משפט על הקמת ישויות/הסתרת מימון, כאשר גם במקור יש טענה על יצירת ישויות פיקטיביות, היא סיכון חדש להשמטת טענה — לא תיקון משמעות מאומת. התצפית היא השוואת טקסטים, ללא תיוג Human/External חדש. יש לשמר גם את הפלט הכושל כדי שהבודק החיצוני יוכל להעריכו.

## קישורים

- [השוואה מלאה לכל ID](COMPARISON_30.md), [CSV](comparison_v2_v3_repair.csv).
- [אימות מקומי](verification_results.csv), [פלטים מתוקנים](repaired_outputs.csv), [guards ללא שינוי](rewrite_validation.csv).
- [style metrics](style_metrics_v2_v3_repair.csv), [66 מאפיינים](explicit_style_changes_v2_v3_repair.csv).
- [חבילת ID/Original/Repaired בלבד](REVIEW_PACKAGE_BLIND_30.md).
- [Prompt תיקון](SEMANTIC_REPAIR_PROMPT.txt), [Prompt אימות](SEMANTIC_VERIFICATION_PROMPT.txt), [פרוטוקול](protocol.json), [סיכום](summary.json), [תקינות](integrity_audit.json), [שחזור](REPRODUCTION.md).

לא שונו split, labels, human-review fields או קוד אימון. לא הורצו retraining, test evaluation, LoRA, External LLM Review חדש או Human Validation. עוצרים לפני הבדיקה החיצונית העיוורת של Repaired v2.
'''
    (OUT/'REPORT_HE.md').write_text(report,encoding='utf8')
    review=m.records(OUT/'rewrite_human_review.csv')
    fields=['facts_preserved','stance_preserved','framing_preserved','negation_preserved','certainty_preserved','attribution_preserved','entities_preserved','style_changed','acceptable','notes']
    assert all(not r[k] for r in review for k in fields)
    baseline_method=json.loads((V2/'validation_method.json').read_text(encoding='utf8'))
    current_method=m.read('validation_method.json')
    assert all(current_method[k]==baseline_method[k] for k in ['ner_revision','nli_revision','semantic_revision','classifier_token_limit','semantic_token_limit','nli_pair_token_limit'])
    check_protected(m)
    m.dump('integrity_audit.json',dict(passed=True,protected_files=nprotected,changed_experimental_files=[],same_30_originals=True,
        same_v2_inputs=True,all_train=True,no_first_stage_regeneration=True,no_external_ratings_used_for_routing=True,
        patches_reconstruct_outputs=True,no_single_whole_text_replacement=True,human_fields_blank=True,no_training=True,no_test=True,
        authorized_doc_updates_separate=['EXPERIMENT_GUIDE_HE.md','FINAL_REPORT_HE.md'],
        guard_source_sha256={str(p.relative_to(ROOT)):m.sha(p) for p in [STUDY/'study.py',PREVIOUS/'experiment.py',ROOT/'experiments/author_generalization/author_style_controlled.py']}))
    m.event('repair_report',n=30,summary_sha256=m.sha(OUT/'summary.json'))
    print(json.dumps(totals),flush=True)


if __name__=='__main__':main()

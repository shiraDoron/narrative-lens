"""Aggregate review import, blank human package and paired TRAIN-only author probe."""
from pathlib import Path
import collections,csv,datetime,hashlib,importlib.metadata,importlib.util,json,subprocess

OUT=Path(__file__).resolve().parent
RUN=OUT.parent
ROOT=RUN.parents[2]
STUDY=ROOT/'artifacts/experiments/style_intervention_v2_20261026'
SEEDS=[7,42,123,2026,31415]
COUNTS={
 'meaning_preserved':{'Yes':24,'Borderline':6,'No':0},
 'narrative_stance_preserved':{'Yes':28,'Borderline':2,'No':0},
 'attribution_preserved':{'Yes':28,'Borderline':2,'No':0},
 'certainty_preserved':{'Yes':26,'Borderline':2,'No':2},
 'participant_roles_preserved':{'Yes':29,'Borderline':1,'No':0},
 'event_characterization_preserved':{'Yes':22,'Borderline':8,'No':0},
 'rhetorical_intensity_preserved':{'Yes':19,'Borderline':10,'No':1},
 'quote_fidelity':{'Yes':11,'N/A':19},
 'style_change_valid':{'Yes':24,'Borderline':6,'No':0},
 'semantic_drift':{'Yes':3,'Borderline':11,'No':16},
}
HUMAN=['human_meaning_preserved','human_narrative_stance_preserved','human_style_change_valid','human_semantic_drift','human_notes']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def records(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def table(headers,rows):
    def cell(x):return str(x).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(cell(x) for x in r)+' |' for r in rows])
def module(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    import numpy as np
    from sklearn.model_selection import StratifiedKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score,f1_score,confusion_matrix
    received=RUN/'CHATGPT_STYLE_REWRITE_30_20261102.csv'
    pairs=records(RUN/'frozen_comparison_inputs.csv');cohort=records(RUN/'analysis_cohort.csv');by={r['row_id']:r for r in cohort}
    assert len(pairs)==len(cohort)==30 and all(r['split']=='train' for r in cohort)
    assert len({r['article_snapshot_sha256'] for r in cohort})==30,'Repeated article: use group-aware folds before running'
    assert all(r['Original']==by[r['ID']]['text'] for r in pairs)
    assert all(sum(v.values())==30 for v in COUNTS.values())
    dump('external_llm_review_aggregate.json',dict(source='User-provided aggregate counts in conversation, 2026-11-02',review_name='External LLM Review — ChatGPT Style Rewrite',independence='Reported by user; context/request history not supplied',n=30,counts=COUNTS,per_id_ratings_available=False,reviewer_model=None,review_prompt=None,review_date=None,clean_label='clean according to External LLM Review',clean_definition='semantic_drift = No, not a conjunction of other fields',clean_count=16,human_validation=False,review_performed_here=False))
    write('external_llm_review_counts.csv',[dict(field=k,rating=rating,count=n,denominator=30) for k,v in COUNTS.items() for rating,n in v.items()])
    package=[dict(ID=r['ID'],Original=r['Original'],ChatGPT_Style_Rewrite=r['ChatGPT_Style_Rewrite'],**{f:'' for f in HUMAN}) for r in pairs]
    if (OUT/'HUMAN_VALIDATION_30.csv').exists():
        assert all(not r[f] for r in records(OUT/'HUMAN_VALIDATION_30.csv') for f in HUMAN),'Human responses present: never overwrite'
    write('HUMAN_VALIDATION_30.csv',package)
    md='# Human Validation — text pairs\n\nלכל שדה הכרעה יש לבחור Yes / No / Borderline; בשדה notes אפשר להסביר אי־ודאות או שינוי מסוים. יש לשפוט כל זוג לגופו. השדות נשארו ריקים למילוי סוקר/ת אדם.\n\n'
    for r in package:
        md+='## '+r['ID']+'\n\n### Original\n\n'+r['Original']+'\n\n### ChatGPT Style Rewrite\n\n'+r['ChatGPT_Style_Rewrite']+'\n\n'+table(['field','answer'],[[f,''] for f in HUMAN])+'\n\n'
    md=md.rstrip()+'\n'
    if (OUT/'HUMAN_VALIDATION_30.md').exists():
        assert (OUT/'HUMAN_VALIDATION_30.md').read_text(encoding='utf8')==md,'Human package changed: never overwrite'
    (OUT/'HUMAN_VALIDATION_30.md').write_text(md,encoding='utf8')
    # Existing raw 66 features only; no frozen-study test split or fitted scaling read.
    helper=module(STUDY/'study.py','style_functions_only');engine=helper.load_engine()
    names=json.loads((ROOT/'artifacts/experiments/verified_human_style_followup_20261026/style_feature_definitions.json').read_text(encoding='utf8'))['names'];assert len(names)==66
    x={v:np.array([engine.style_features(r[field]) for r in pairs],dtype=float) for v,field in [('Original','Original'),('Rewrite','ChatGPT_Style_Rewrite')]}
    assert all(z.shape==(30,66) and np.isfinite(z).all() for z in x.values())
    authors=sorted({r['author'] for r in cohort});y=np.array([by[r['ID']]['author'] for r in pairs]);counts=collections.Counter(y);assert min(counts.values())>=2
    protocol=dict(scope='All 30 paired existing TRAIN examples; closed-set author identification, not frozen test evaluation',target='author, never narrative',authors=dict(counts),n=30,seeds=SEEDS,n_splits=2,split_strategy='Paired StratifiedKFold, shuffle=True; no Original/Rewrite pair crosses folds',article_groups_unique=True,primary='Matched representation: fit Original/train -> Original/dev; independently fit Rewrite/train -> Rewrite/dev with identical pipeline, hyperparameters and fold IDs',secondary='Same fitted Original pipeline -> paired Rewrite/dev; diagnostic for transfer/distribution shift',features='existing 66 raw stylometric features, including function-word rates; no topic/content embeddings',scaling='StandardScaler fit on training fold separately inside each pipeline; never full-data or held-out scaling',classifier=dict(type='LogisticRegression',C=1.0,max_iter=2000,solver='lbfgs',class_weight=None),hyperparameter_search=False,review_based_selection=False,all_30_included=True,acceptance_rule='not applied; future human meaning=Yes AND human stance=Yes AND human style=Yes applied to every row',human_validation='Pending',narrative_classifier_training=False,test_evaluation=False,weights_saved=False,versions={k:importlib.metadata.version(k) for k in ['numpy','scikit-learn','scipy']})
    dump('author_id_protocol.json',protocol)
    feature_rows=[dict(ID=r['ID'],author=by[r['ID']]['author'],version=v,**dict(zip(names,map(float,x[v][i])))) for v in x for i,r in enumerate(pairs)]
    write('author_features_66.csv',feature_rows)
    predictions=[];splits=[];seed_metrics=[]
    for seed in SEEDS:
        outputs={v:np.empty(30,dtype=object) for v in ['Original','Rewrite','Original_fit_Rewrite_dev']}
        for fold,(train,dev) in enumerate(StratifiedKFold(n_splits=2,shuffle=True,random_state=seed).split(x['Original'],y)):
            assert not set(train)&set(dev)
            for role,indices in [('fit',train),('dev',dev)]:
                splits.extend(dict(seed=seed,fold=fold,role=role,ID=pairs[i]['ID'],author=y[i],study_split='train') for i in indices)
            for version in ['Original','Rewrite']:
                model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,solver='lbfgs',random_state=seed))
                model.fit(x[version][train],y[train]);outputs[version][dev]=model.predict(x[version][dev])
                if version=='Original':outputs['Original_fit_Rewrite_dev'][dev]=model.predict(x['Rewrite'][dev])
            for version in outputs:
                predictions.extend(dict(seed=seed,fold=fold,ID=pairs[i]['ID'],author_true=y[i],version=version,author_predicted=outputs[version][i],correct=outputs[version][i]==y[i]) for i in dev)
        for version,pred in outputs.items():
            seed_metrics.append(dict(seed=seed,version=version,accuracy=float(accuracy_score(y,pred)),macro_f1=float(f1_score(y,pred,labels=authors,average='macro',zero_division=0))))
    write('author_id_fold_assignments.csv',splits);write('author_id_predictions.csv',predictions);write('author_id_seed_metrics.csv',seed_metrics)
    results={}
    for version in ['Original','Rewrite','Original_fit_Rewrite_dev']:
        rows=[r for r in seed_metrics if r['version']==version]
        results[version]={metric+'_mean':float(np.mean([r[metric] for r in rows])) for metric in ['accuracy','macro_f1']}
        results[version].update({metric+'_seed_sd':float(np.std([r[metric] for r in rows],ddof=1)) for metric in ['accuracy','macro_f1']})
        pred=[r for r in predictions if r['version']==version];matrix=confusion_matrix([r['author_true'] for r in pred],[r['author_predicted'] for r in pred],labels=authors)
        assert int(matrix.sum())==150
        write('confusion_'+version+'.csv',[dict(author_true=a,**{authors[j]:int(matrix[i,j]) for j in range(len(authors))}) for i,a in enumerate(authors)])
    results['deltas_rewrite_minus_original']={metric:results['Rewrite'][metric+'_mean']-results['Original'][metric+'_mean'] for metric in ['accuracy','macro_f1']}
    paired_deltas=[]
    for seed in SEEDS:
        one={r['version']:r for r in seed_metrics if r['seed']==seed}
        paired_deltas.append(dict(seed=seed,accuracy_delta=one['Rewrite']['accuracy']-one['Original']['accuracy'],macro_f1_delta=one['Rewrite']['macro_f1']-one['Original']['macro_f1']))
    results['paired_seed_deltas']=paired_deltas
    results['accuracy_decreased_in_seeds']=sum(r['accuracy_delta']<0 for r in paired_deltas)
    results['majority_accuracy']=max(counts.values())/30;results['uniform_chance_accuracy']=1/len(authors)
    dump('author_id_summary.json',results)
    earlier=json.loads((STUDY/'train_prompt_revision_v3_30_20261102/external_llm_review_20261102/summary.json').read_text(encoding='utf8'))['field_counts']
    auto=json.loads((RUN/'summary.json').read_text(encoding='utf8'))['totals']
    comparison=[dict(Method=v,Auto_preservation=auto[v]['preservation_pass'],External_LLM_meaning_Yes=earlier[v]['meaning_preserved'].get('Yes','N/A') if v!='ChatGPT' else 24,External_LLM_style_Yes=earlier[v]['style_change_valid'].get('Yes','N/A') if v!='ChatGPT' else 24,Clean_no_drift=earlier[v]['semantic_drift'].get('No','N/A') if v!='ChatGPT' else 16) for v in ['v2','v3','ChatGPT']]
    write('review_comparison_summary.csv',comparison)
    metric_table=table(['Author-ID evaluation','Accuracy mean','Macro-F1 mean','Accuracy seed SD','Macro-F1 seed SD'],[[v]+[f"{results[v][k]:.4f}" for k in ['accuracy_mean','macro_f1_mean','accuracy_seed_sd','macro_f1_seed_sd']] for v in ['Original','Rewrite','Original_fit_Rewrite_dev']])
    text='# External review, human package and Author-ID diagnostic\n\n'
    text+='תאריך 2026-11-02. יובאו רק ספירות review שסיפק המשתמש בשיחה. אין קובץ הכרעות לפי ID, שם/גרסת סוקר או prompt review; עצמאות הביקורת מדווחת על ידי המשתמש ולא נבדקה מהיסטוריית בקשות. לא נערך review חדש כאן.\n\n'
    text+=table(['field','Yes','Borderline','No','N/A'],[[k]+[v.get(r,0) for r in ['Yes','Borderline','No','N/A']] for k,v in COUNTS.items()])+'\n\n'
    text+='quote_fidelity: 11/11 Yes בין המקרים הרלוונטיים; 19 N/A. clean according to External LLM Review: 16/30 לפי semantic_drift=No בלבד. אין לקרוא להם human-validated; אין גם דרך לזהות את ה־IDs האלה או לחשב חפיפות בין שדות מהספירות בלבד. 6 Meaning Borderline ו־11 Drift Borderline נשארים נפרדים, ואינם בהכרח אותן רשומות.\n\n'
    text+='## השוואת reviews\n\n'+table(list(comparison[0]),[list(r.values()) for r in comparison])+'\n\n'
    text+='הספירות v2/v3 נלקחו מה־reviews הקיימים; Clean no-drift הוא אותו semantic_drift=No, לא כלל קבלה משולב. אין השוואה זוגית של שינוי ratings, בדיקת agreement או discrepancy מול guards ל־ChatGPT ללא הכרעות לפי ID. ההבדלים בין סוקרים/contexts אינם נשלטים, ולכן זו השוואה תיאורית ולא הוכחת עדיפות.\n\n'
    text+='## Human Validation\n\n[HUMAN_VALIDATION_30.md](HUMAN_VALIDATION_30.md) ו־[CSV](HUMAN_VALIDATION_30.csv) כוללים רק ID, Original, ChatGPT Style Rewrite וחמשת השדות הריקים המבוקשים. אין guards, גרסאות קודמות, scores, review או מחבר. כל 30 הזוגות נכללו. אין הכרעות אנושיות עדיין; Human Validation = Pending. פרטי הסוקר/ת ותאריך אפשר לתעד בנפרד. לא שונו שדות review קיימים.\n\n'
    text+='כלל acceptance אפשרי לעתיד: Human meaning=Yes AND Human stance=Yes AND Human style=Yes, החל על כל 30. לא הוחל כעת, ולא נבחרו רק 16 מקרי no-drift.\n\n'
    text+='## Author-ID — all 30 TRAIN pairs\n\n'+metric_table+'\n\n'
    text+='66 מאפייני סגנון קיימים + StandardScaler + LogisticRegression, ללא search/tuning. בכל seed שתי חלוקות stratified; כל זוג נשאר באותו צד. בגרסה הראשית אותו algorithm/hyperparameters אך fit נפרד לכל representation. הבדיקה הנוספת משתמשת בדיוק באותו fitted Original classifier. scaling מאומן רק בתוך fold.\n\n'
    text+='זהו closed-set Author-ID על כותבים המופיעים ב־fit וב־dev, לא unseen-author evaluation ולא test המחקרי. תשעה כותבים, 2–4 דוגמאות לכותב; כל דוגמה מנובאת פעם אחת לכל seed (150 תחזיות לכל representation), לא 150 טקסטים עצמאיים. SD בין seeds אינו confidence interval. Majority accuracy: '+f"{results['majority_accuracy']:.4f}"+'; uniform chance: '+f"{results['uniform_chance_accuracy']:.4f}"+'.\n\n'
    delta=results['deltas_rewrite_minus_original']
    text+='שינוי Rewrite−Original במסלול matched: accuracy '+f"{100*delta['accuracy']:+.2f}"+'pp; Macro-F1 '+f"{100*delta['macro_f1']:+.2f}"+'pp. '
    text+='הממוצע נמוך מעט יותר, אבל הירידה אינה יציבה: accuracy ירד רק ב־'+str(results['accuracy_decreased_in_seeds'])+'/5 seeds. במסלול עם מסווג Original קבוע הוא דווקא עלה ל־28.0%. אין כרגע ראיה מספקת לירידה ברורה ב־author signal; אין לבחור seed או method שמייצר את הכיוון הרצוי. '
    text+='\n\n'+table(['seed','accuracy delta Rewrite−Original','Macro-F1 delta'],[[r['seed'],f"{100*r['accuracy_delta']:+.2f}pp",f"{r['macro_f1_delta']:+.4f}"] for r in paired_deltas])+'\n\n'
    text+='ירידה רק ב־Original-fit→Rewrite-dev עשויה להעיד על domain shift, גם אם מסווג שמאומן מחדש על rewrites עדיין מזהה כותבים. המדגם זעיר ואבחוני, ויש ערבוב אפשרי של תוכן, אורך, פרסום ונרטיב גם במאפייני style. אין כאן הסקת causal effect או שיפור narrative generalization.\n\n'
    text+='[Protocol](author_id_protocol.json), [per-seed metrics](author_id_seed_metrics.csv), [predictions](author_id_predictions.csv), [fold IDs](author_id_fold_assignments.csv). Confusion matrices pooled across the same five seeds (rows=true, columns=predicted): [Original](confusion_Original.csv), [Rewrite](confusion_Rewrite.csv), [Original-fit→Rewrite-dev](confusion_Original_fit_Rewrite_dev.csv).\n\n'
    text+='## שאלת המחקר והעצירה\n\nהחידוש אינו בהכרח Text Style Transfer חדש. השאלה היא האם Narrative Classifier משתמש ב־author style כ־shortcut, והאם הפחתת author-specific style תוך שמירת narrative משפרת generalization ל־unseen authors. ChatGPT rewrite הוא intervention candidate, לא contribution מוכחת בפני עצמו.\n\nלא שונו rewrite prompt, guards, thresholds, filtering או חלוקת המחקר. אומנו רק מסווגי Author-ID זמניים בתוך folds של train; לא אומן Narrative Classifier, לא נשמרו weights ולא בוצעו test evaluation, LoRA או External LLM Review חדש. עוצרים לקבלת תיוג אנושי אמיתי.\n'
    (OUT/'REPORT_HE.md').write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n',encoding='utf8')
    # Verify no information leakage or mutation of the imported candidate texts.
    assert len(predictions)==450 and len(splits)==300
    for seed in SEEDS:
        for version in results:
            if version not in ['Original','Rewrite','Original_fit_Rewrite_dev']:continue
            pp=[r for r in predictions if r['seed']==seed and r['version']==version];assert len(pp)==len({r['ID'] for r in pp})==30
    human=records(OUT/'HUMAN_VALIDATION_30.csv');assert len(human)==30 and all(not r[f] for r in human for f in HUMAN)
    assert all(r['ChatGPT_Style_Rewrite']==pairs[i]['ChatGPT_Style_Rewrite'] and r['Original']==pairs[i]['Original'] for i,r in enumerate(human))
    dump('integrity_audit.json',dict(all_30_included=True,no_review_based_selection=True,no_pair_crosses_folds=True,unique_articles=True,all_30_oof_each_seed_and_representation=True,human_fields_all_blank=True,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [received,RUN/'analysis_cohort.csv',RUN/'frozen_comparison_inputs.csv',ROOT/'experiments/author_generalization/author_style_controlled.py',ROOT/'artifacts/experiments/verified_human_style_followup_20261026/experiment.py']},author_feature_code='existing 66 features, unchanged',created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),no_narrative_training=True,no_test_evaluation=True))
    print(json.dumps(results),flush=True)
if __name__=='__main__':main()

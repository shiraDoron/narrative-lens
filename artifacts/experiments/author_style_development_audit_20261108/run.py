"""Development-only corpus audit and prespecified author-style diagnostics."""
from pathlib import Path
import argparse,collections,csv,datetime,hashlib,importlib.util,itertools,json,math,os,re,subprocess,sys
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('MKL_NUM_THREADS','4')
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'artifacts/experiments/verified_human_style_followup_20261026'
CHAT=ROOT/'artifacts/experiments/chatgpt_style_rewrite_30_20261102'
PREVIOUS=CHAT/'review_author_analysis_20261102'
SEEDS=[7,42,123,2026,31415]
METHODS=['surface_66','function_punctuation','char_tfidf','word_content_control']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def records(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def dump(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf8')
def read(name):return json.loads((OUT/name).read_text(encoding='utf8'))
def write(name,rows,fields=None):
    rows=list(rows)
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def module(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def normalized(t):return ' '.join(re.findall(r'\w+',t.casefold()))
def words(t):return re.findall(r'\b\w+\b',t.casefold())
def protected():
    assert all(sha(ROOT/p)==h for p,h in read('source_hashes.json').items()),'Frozen source changed'
def prepare():
    paths=[SOURCE/n for n in ['collected_texts.csv','text_annotations.csv','analysis_cohort.csv','author_splits.csv','split_definitions.csv','split_audit.json','generated_cross_split_duplicates.json','experiment.py','human_annotation_blind.csv','human_annotation_key.csv']]+[CHAT/n for n in ['CHATGPT_STYLE_REWRITE_30_20261102.csv','frozen_comparison_inputs.csv','analysis_cohort.csv','rewrite_validation.csv','protocol.json']]+[PREVIOUS/n for n in ['HUMAN_VALIDATION_30.md','HUMAN_VALIDATION_30.csv','author_id_predictions.csv','author_id_protocol.json','author_id_summary.json','external_llm_review_aggregate.json']]+[ROOT/'experiments/author_generalization/author_style_controlled.py']
    if (OUT/'protocol.json').exists():protected();return
    dump('source_hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in paths})
    dump('protocol.json',dict(created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='TRAIN authors only for every feature, fit, topic and model-choice diagnostic; val/test metadata counts only',seeds=SEEDS,methods=METHODS,model='LogisticRegression C=1, lbfgs, max_iter=3000; no search',character_features=dict(analyzer='char',ngram_range=[3,5],min_df=2,max_features=30000,sublinear_tf=True),word_control=dict(ngram_range=[1,2],stop_words='english',min_df=2,max_features=10000,sublinear_tf=True),cohorts=['train_all_annotations','train_eligible_narrative','train_eligible_Left-wing','train_eligible_Right-wing'],cv='StratifiedGroupKFold; at most five folds, minimum distinct groups/author; same folds for all methods; five seeds',groups='same article/text or TRAIN-only word-5-shingle Jaccard>=0.80 or word-TFIDF cosine>=0.95; graph connected components',new_duplicate_thresholds_are_not_preservation_guards=True,paired_primary='Fit each method on all TRAIN originals excluding every group represented in the fixed 30 pairs. Predict unseen Original and corresponding ChatGPT Rewrite using precisely the same fitted model.',paired_secondary='Repeat fixed-30 comparison after stratified 80% resampling of training pool by author; five seeds. Also eligible-only pool as prespecified sensitivity.',feature_scaling='fit on each fit portion only',topic_audit='TRAIN-only word unigram TFIDF and KMeans(k=6,n_init=10,random_state=42); exploratory cluster-author NMI, not topic labels or causal shortcut proof',paired_inference='two-sided exact McNemar via binomial test, Holm over four primary all-TRAIN methods; paired accuracy cluster bootstrap by author, 2000 draws seed 20261108',selection='All 30 pairs regardless of guard/review; no filtering by external clean status',syntax='No English parser model installed at feasibility; sentence structure metrics are proxies, not syntactic analysis',no_new_rewrites=True,no_narrative_classifier_training=True,no_frozen_test_evaluation=True,no_paid_cloud=True,script_sha256_before_results=sha(Path(__file__))))
def audit():
    prepare()
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics import normalized_mutual_info_score
    raw=records(SOURCE/'collected_texts.csv');allrows=records(SOURCE/'text_annotations.csv');eligible=records(SOURCE/'analysis_cohort.csv');splits={r['author']:r['split'] for r in records(SOURCE/'author_splits.csv')}
    # Frozen test content is never passed to feature extraction, embeddings or similarity.
    dev=[r for r in allrows if splits[r['author']]=='train'];train_ids={r['row_id'] for r in dev};assert len(dev)==202
    eligible_train=[r for r in eligible if r['split']=='train'];assert {r['row_id'] for r in eligible_train}<=train_ids
    pairs=records(CHAT/'frozen_comparison_inputs.csv');assert len(pairs)==30 and {r['ID'] for r in pairs}<=train_ids
    authorrows=[]
    for a in sorted(splits):
        values=[r for r in allrows if r['author']==a];e=[r for r in eligible if r['author']==a]
        authorrows.append(dict(author=a,split=splits[a],raw_collected=sum(r['author']==a for r in raw),unique_corpus=len(values),narrative_eligible=len(e),current_ChatGPT_pairs=sum(r['ID'] in {v['row_id'] for v in values} for r in pairs),human_label_count=sum(bool(r.get('human_label','').strip()) for r in values),development_used=splits[a]=='train'))
    write('corpus_by_author.csv',authorrows)
    write('development_originals.csv',[dict(ID=r['row_id'],author=r['author'],Original=r['text'],article=r['article_snapshot_sha256'],source_date=r['source_date'],label_proposal=r['label_a'],eligible=r['row_id'] in {e['row_id'] for e in eligible_train},study_split='train') for r in dev])
    parent=list(range(len(dev)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(i,j):parent[find(j)]=find(i)
    sh=[set(zip(words(r['text']),words(r['text'])[1:],words(r['text'])[2:],words(r['text'])[3:],words(r['text'])[4:])) for r in dev]
    vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words='english',min_df=1);z=vectorizer.fit_transform([r['text'] for r in dev]);similarity=(z@z.T).toarray()
    near=[]
    for i,j in itertools.combinations(range(len(dev)),2):
        jac=len(sh[i]&sh[j])/max(1,len(sh[i]|sh[j]));same=dev[i]['article_snapshot_sha256']==dev[j]['article_snapshot_sha256'] or normalized(dev[i]['text'])==normalized(dev[j]['text'])
        if same or jac>=.8 or similarity[i,j]>=.95:
            union(i,j);near.append(dict(ID_a=dev[i]['row_id'],ID_b=dev[j]['row_id'],same_source_or_exact=same,jaccard=jac,tfidf_cosine=float(similarity[i,j]),same_author=dev[i]['author']==dev[j]['author']))
    write('development_near_duplicates.csv',near,['ID_a','ID_b','same_source_or_exact','jaccard','tfidf_cosine','same_author'])
    group_rows=[dict(ID=r['row_id'],group='G'+str(find(i)),author=r['author']) for i,r in enumerate(dev)];write('development_groups.csv',group_rows)
    cross_hash=collections.defaultdict(set)
    for r in allrows:cross_hash[r['text_sha256']].add(splits[r['author']])
    cross={h:sorted(ss) for h,ss in cross_hash.items() if len(ss)>1}
    cross_articles=collections.defaultdict(set)
    for r in allrows:cross_articles[r['article_snapshot_sha256']].add(splits[r['author']])
    # Length and year summaries restricted to development; test lengths not used for decisions.
    lengths=[]
    for a in sorted({r['author'] for r in dev}):
        group=[r for r in dev if r['author']==a];n=np.array([len(words(r['text'])) for r in group])
        lengths.append(dict(author=a,n=len(group),min_words=int(n.min()),median_words=float(np.median(n)),max_words=int(n.max()),under_50=int((n<50).sum()),under_80=int((n<80).sum()),years='|'.join(sorted({r['source_date'][:4] for r in group}))))
    write('development_lengths_and_dates.csv',lengths)
    topicvec=TfidfVectorizer(stop_words='english',min_df=2,max_features=10000);topics_x=topicvec.fit_transform([r['text'] for r in dev]);km=KMeans(n_clusters=6,n_init=10,random_state=42).fit(topics_x);terms=topicvec.get_feature_names_out();topic_rows=[]
    for k in range(6):
        members=[r for i,r in enumerate(dev) if int(km.labels_[i])==k]
        topic_rows.append(dict(topic=k,n=len(members),top_terms=' | '.join(terms[km.cluster_centers_[k].argsort()[-12:][::-1]]),authors=json.dumps(dict(collections.Counter(r['author'] for r in members))),label_proposals=json.dumps(dict(collections.Counter(r['label_a'] for r in members)))))
    write('development_topics.csv',topic_rows);write('development_topic_assignments.csv',[dict(ID=r['row_id'],author=r['author'],topic=int(km.labels_[i]),year=r['source_date'][:4],label_proposal=r['label_a']) for i,r in enumerate(dev)])
    label_source=collections.Counter(r['label_a'] for r in allrows)
    inventory=[dict(path=str(p.relative_to(ROOT)),role=role,n=n,unique_additional_sources=False) for p,role,n in [(SOURCE/'collected_texts.csv','raw article collection, repeats included',len(raw)),(SOURCE/'text_annotations.csv','unique annotated source universe, machine proposals',len(allrows)),(SOURCE/'analysis_cohort.csv','two-narrative eligible subset, all study splits',len(eligible)),(CHAT/'frozen_comparison_inputs.csv','same 30 source articles, not 30 new sources',len(pairs))]]
    write('source_inventory.csv',inventory)
    human=records(PREVIOUS/'HUMAN_VALIDATION_30.csv');humanfields=[k for k in human[0] if k.startswith('human_')]
    assert len(human)==30 and all(not r[k] for r in human for k in humanfields)
    pair_by={r['ID']:r for r in pairs};assert all(r['Original']==pair_by[r['ID']]['Original'] and r['ChatGPT_Style_Rewrite']==pair_by[r['ID']]['ChatGPT_Style_Rewrite'] for r in human)
    assert set(human[0])=={'ID','Original','ChatGPT_Style_Rewrite',*humanfields}
    review_files=[]
    for p in (ROOT/'artifacts/experiments').rglob('*.csv'):
        if 'review' not in str(p).lower():continue
        if p.stat().st_size>3_000_000:continue
        header=p.open(encoding='utf-8-sig',newline='').readline().strip()
        if 'meaning_preserved' in header or 'semantic_drift' in header:review_files.append(dict(path=str(p.relative_to(ROOT)),header=header))
    write('review_file_inventory.csv',review_files)
    remaining=[r for r in eligible_train if r['row_id'] not in pair_by];assert len(remaining)==75
    write('additional_75_rewrites_manifest.csv',[dict(ID=r['row_id'],author=r['author'],Original=r['text'],study_split='train',narrative_status='machine proposal, human pending',generation_status='not_generated') for r in sorted(remaining,key=lambda r:hashlib.sha256(r['row_id'].encode()).hexdigest())])
    summary=dict(raw_collected=len(raw),unique_corpus=len(allrows),authors=len(splits),corpus_by_author_split=dict(collections.Counter(splits[r['author']] for r in allrows)),eligible_by_split=dict(collections.Counter(r['split'] for r in eligible)),development_authors=sorted({r['author'] for r in dev}),all_train_available=len(dev),eligible_train=len(eligible_train),all_train_plus_val_metadata=sum(splits[r['author']]!='test' for r in allrows),train_plus_val_authors=sum(s!='test' for s in splits.values()),test_authors=sum(s=='test' for s in splits.values()),current_pairs=30,additional_eligible_rewrites=75,additional_all_train_rewrites=172,filled_human_source_labels=sum(bool(r.get('human_label','').strip()) for r in allrows),machine_label_distribution=dict(label_source),metadata_cross_split_exact_hash_collisions=cross,metadata_cross_split_article_collisions=sum(len(v)>1 for v in cross_articles.values()),development_near_pair_count=len(near),development_groups=len({r['group'] for r in group_rows}),historical_218_split_audit=json.loads((SOURCE/'split_audit.json').read_text(encoding='utf8')),historical_generated_cross_split_pairs=json.loads((SOURCE/'generated_cross_split_duplicates.json').read_text(encoding='utf8')),fresh_test_near_duplicate_scan=False,test_content_features_computed=False,topic_author_nmi=float(normalized_mutual_info_score([r['author'] for r in dev],km.labels_)),year_author_nmi=float(normalized_mutual_info_score([r['author'] for r in dev],[r['source_date'][:4] for r in dev])),human_package_blind_fields_verified=True,filled_human_pair_fields=0,chatgpt_review_per_id_imported=False,missing_review='ChatGPT per-ID ratings + notes + reviewer/model/prompt/date; aggregate only available')
    dump('corpus_audit_summary.json',summary);protected();print(json.dumps(summary,ensure_ascii=True),flush=True)

def engine_and_features(rows):
    import numpy as np
    h=module(ROOT/'artifacts/experiments/style_intervention_v2_20261026/study.py','existing_styles');engine=h.load_engine()
    names=json.loads((SOURCE/'style_feature_definitions.json').read_text(encoding='utf8'))['names'];assert len(names)==66
    x=np.array([engine.style_features(r['Original']) for r in rows]);assert x.shape==(len(rows),66)
    # Rate-based surface + function words, excluding raw length, word length/MATTR/length variance.
    indices=[i for i,name in enumerate(names) if i in range(3,10) or i in (13,14,15) or i>=16]
    return engine,names,x,indices
def pipeline(method,seed):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    lr=LogisticRegression(C=1,max_iter=3000,solver='lbfgs',random_state=seed)
    if method in ['surface_66','function_punctuation']:return make_pipeline(StandardScaler(),lr)
    vector=TfidfVectorizer(analyzer='char',ngram_range=(3,5),min_df=2,max_features=30000,sublinear_tf=True) if method=='char_tfidf' else TfidfVectorizer(ngram_range=(1,2),stop_words='english',min_df=2,max_features=10000,sublinear_tf=True)
    return make_pipeline(vector,lr)
def baselines():
    prepare();protected()
    import numpy as np
    from sklearn.model_selection import StratifiedGroupKFold
    from sklearn.metrics import accuracy_score,f1_score,confusion_matrix
    from scipy.stats import binomtest
    rows=records(OUT/'development_originals.csv');groups={r['ID']:r['group'] for r in records(OUT/'development_groups.csv')};eng,names,x,indices=engine_and_features(rows)
    y=np.array([r['author'] for r in rows]);texts=np.array([r['Original'] for r in rows],dtype=object);g=np.array([groups[r['ID']] for r in rows]);classes=sorted(set(y))
    write('style_feature_definition.csv',[dict(index=i,name=name,used_in_function_punctuation=i in indices) for i,name in enumerate(names)])
    features={'surface_66':x,'function_punctuation':x[:,indices],'char_tfidf':texts,'word_content_control':texts}
    cohorts={'train_all_annotations':np.arange(len(rows)),'train_eligible_narrative':np.array([i for i,r in enumerate(rows) if r['eligible']=='True'])}
    for label in ['Left-wing','Right-wing']:cohorts['train_eligible_'+label]=np.array([i for i,r in enumerate(rows) if r['eligible']=='True' and r['label_proposal']==label])
    predictions=[];assignments=[];metrics=[]
    for cohort,ix in cohorts.items():
        labels=sorted(set(y[ix]));minimum=min(len(set(g[ix][y[ix]==a])) for a in labels);nfold=min(5,minimum);assert nfold>=2
        for seed in SEEDS:
            fold_output={method:np.empty(len(ix),dtype=object) for method in METHODS}
            for fold,(tr,ev) in enumerate(StratifiedGroupKFold(n_splits=nfold,shuffle=True,random_state=seed).split(texts[ix],y[ix],g[ix])):
                train=ix[tr];dev=ix[ev];assert not set(g[train])&set(g[dev]);assert set(y[train])==set(labels)
                assignments.extend(dict(cohort=cohort,seed=seed,fold=fold,ID=rows[i]['ID'],role=role,group=g[i],author=y[i]) for role,idx in [('fit',train),('dev',dev)] for i in idx)
                for method in METHODS:
                    model=pipeline(method,seed);model.fit(features[method][train],y[train]);p=model.predict(features[method][dev]);fold_output[method][ev]=p
                    predictions.extend(dict(cohort=cohort,seed=seed,fold=fold,method=method,ID=rows[i]['ID'],author_true=y[i],author_predicted=v,correct=bool(y[i]==v)) for i,v in zip(dev,p))
            for method in METHODS:
                p=fold_output[method];metrics.append(dict(cohort=cohort,seed=seed,method=method,n=len(ix),authors=len(labels),folds=nfold,accuracy=float(accuracy_score(y[ix],p)),macro_f1=float(f1_score(y[ix],p,labels=labels,average='macro',zero_division=0)),majority_accuracy=max(collections.Counter(y[ix]).values())/len(ix),uniform_chance=1/len(labels)))
        print('CV finished:',cohort,len(ix),flush=True)
    write('cv_predictions.csv',predictions);write('cv_fold_assignments.csv',assignments);write('cv_seed_metrics.csv',metrics)
    summary=[]
    for cohort in cohorts:
        for method in METHODS:
            mm=[r for r in metrics if r['cohort']==cohort and r['method']==method]
            summary.append(dict(cohort=cohort,method=method,n=mm[0]['n'],authors=mm[0]['authors'],folds=mm[0]['folds'],accuracy_mean=float(np.mean([r['accuracy'] for r in mm])),accuracy_seed_sd=float(np.std([r['accuracy'] for r in mm],ddof=1)),macro_f1_mean=float(np.mean([r['macro_f1'] for r in mm])),macro_f1_seed_sd=float(np.std([r['macro_f1'] for r in mm],ddof=1)),majority_accuracy=mm[0]['majority_accuracy'],uniform_chance=mm[0]['uniform_chance']))
    write('cv_summary.csv',summary)
    for method in METHODS:
        pp=[p for p in predictions if p['cohort']=='train_all_annotations' and p['method']==method];cm=confusion_matrix([p['author_true'] for p in pp],[p['author_predicted'] for p in pp],labels=classes)
        write('cv_confusion_'+method+'.csv',[dict(author_true=a,**{b:int(cm[i,j]) for j,b in enumerate(classes)}) for i,a in enumerate(classes)])
    # Primary intervention: every paired source is held out from the larger original-only pool.
    pairs=records(CHAT/'frozen_comparison_inputs.csv');index={r['ID']:i for i,r in enumerate(rows)};eval_ix=np.array([index[r['ID']] for r in pairs]);eval_groups=set(g[eval_ix]);all_pool=np.array([i for i in range(len(rows)) if g[i] not in eval_groups]);eligible_pool=np.array([i for i in all_pool if rows[i]['eligible']=='True'])
    rewrite_x=np.array([eng.style_features(r['ChatGPT_Style_Rewrite']) for r in pairs]);rewrite_text=np.array([r['ChatGPT_Style_Rewrite'] for r in pairs],dtype=object);orig_features={m:features[m][eval_ix] for m in METHODS};rewrite_features={'surface_66':rewrite_x,'function_punctuation':rewrite_x[:,indices],'char_tfidf':rewrite_text,'word_content_control':rewrite_text}
    fixed=[];fixed_predictions=[];pool_manifest=[];stability=[]
    for pool_name,pool in [('all_train_excluding_pairs',all_pool),('eligible_train_excluding_pairs',eligible_pool)]:
        assert not set(g[pool])&eval_groups and set(y[pool])==set(y[eval_ix])
        pool_manifest.extend(dict(pool=pool_name,ID=rows[i]['ID'],author=y[i],group=g[i],role='fit') for i in pool)
        for method in METHODS:
            model=pipeline(method,20261108);model.fit(features[method][pool],y[pool]);po=model.predict(orig_features[method]);pr=model.predict(rewrite_features[method]);yy=y[eval_ix]
            co=po==yy;cr=pr==yy;loss=int((co&~cr).sum());gain=int((~co&cr).sum());discord=loss+gain;pvalue=float(binomtest(gain,discord,.5).pvalue) if discord else 1.
            rng=np.random.default_rng(20261108);groupids=[np.where(yy==a)[0] for a in classes];samples=[]
            for _ in range(2000):
                bi=np.concatenate([groupids[j] for j in rng.integers(0,len(classes),len(classes))]);samples.append(float(np.mean(cr[bi])-np.mean(co[bi])))
            fixed.append(dict(pool=pool_name,method=method,n_fit=len(pool),n_dev=30,accuracy_original=float(co.mean()),accuracy_rewrite=float(cr.mean()),accuracy_delta=float(cr.mean()-co.mean()),macro_f1_original=float(f1_score(yy,po,labels=classes,average='macro',zero_division=0)),macro_f1_rewrite=float(f1_score(yy,pr,labels=classes,average='macro',zero_division=0)),original_correct_rewrite_wrong=loss,original_wrong_rewrite_correct=gain,mcnemar_exact_p=pvalue,cluster_bootstrap_delta_lo=float(np.quantile(samples,.025)),cluster_bootstrap_delta_hi=float(np.quantile(samples,.975))))
            fixed_predictions.extend(dict(pool=pool_name,method=method,ID=r['ID'],author_true=yy[j],original_prediction=po[j],rewrite_prediction=pr[j],original_correct=bool(co[j]),rewrite_correct=bool(cr[j])) for j,r in enumerate(pairs))
            for seed in SEEDS:
                rng=np.random.default_rng(seed);selected=np.concatenate([rng.choice(pool[y[pool]==a],max(1,int(.8*sum(y[pool]==a))),replace=False) for a in classes]);probe=pipeline(method,seed);probe.fit(features[method][selected],y[selected]);a=probe.predict(orig_features[method]);b=probe.predict(rewrite_features[method])
                stability.append(dict(pool=pool_name,method=method,seed=seed,n_fit=len(selected),accuracy_original=float(accuracy_score(yy,a)),accuracy_rewrite=float(accuracy_score(yy,b)),accuracy_delta=float(accuracy_score(yy,b)-accuracy_score(yy,a)),macro_f1_original=float(f1_score(yy,a,labels=classes,average='macro',zero_division=0)),macro_f1_rewrite=float(f1_score(yy,b,labels=classes,average='macro',zero_division=0))))
        print('Paired fixed-model finished:',pool_name,len(pool),flush=True)
    primary=sorted([r for r in fixed if r['pool']=='all_train_excluding_pairs'],key=lambda r:r['mcnemar_exact_p']);running=0.
    for i,r in enumerate(primary):running=max(running,min(1.,(len(primary)-i)*r['mcnemar_exact_p']));r['holm_primary_p']=running
    for r in fixed:r.setdefault('holm_primary_p','N/A_secondary')
    write('paired_fixed_model_results.csv',fixed);write('paired_fixed_model_predictions.csv',fixed_predictions);write('paired_training_pool.csv',pool_manifest);write('paired_training_resample_stability.csv',stability)
    import importlib.metadata
    dump('baseline_runtime_audit.json',dict(versions={k:importlib.metadata.version(k) for k in ['numpy','scipy','scikit-learn']},n_original_train=len(rows),n_paired=30,all_train_fit_excluding_pairs=len(all_pool),eligible_fit_excluding_pairs=len(eligible_pool),same_fitted_classifier_for_original_and_rewrite=True,no_test_features=True,no_narrative_models=True,source_code_sha256=sha(Path(__file__)),protocol_sha256=sha(OUT/'protocol.json'),methods_fixed_before_results=True))
    protected()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['prepare','audit','baselines'],required=True);args=parser.parse_args();globals()[args.stage]()

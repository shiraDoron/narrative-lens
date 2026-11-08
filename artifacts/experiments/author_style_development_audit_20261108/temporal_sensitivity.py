"""Post-hoc calendar control, motivated by the corpus audit; no new methods."""
from run import *
def main():
    import numpy as np
    from sklearn.model_selection import StratifiedGroupKFold
    from sklearn.metrics import accuracy_score,f1_score
    protected();rows=records(OUT/'development_originals.csv');by={r['ID']:r for r in rows}
    # Select authors for whom ALL available train texts are from 2026, before fitting.
    authors=sorted(a for a in {r['author'] for r in rows} if {r['source_date'][:4] for r in rows if r['author']==a}=={'2026'})
    cohort=[r for r in rows if r['author'] in authors];pairs=[r for r in records(CHAT/'frozen_comparison_inputs.csv') if by[r['ID']]['author'] in authors]
    dump('temporal_control_protocol.json',dict(status='post-hoc sensitivity after main results; no confirmatory inference',motivation='Strong author/year association identified in development metadata',selection='All authors whose available train sources all date to 2026; independent of review, guards and rewrite outcomes',authors=authors,n_sources=len(cohort),n_pairs=len(pairs),methods=METHODS,seeds=SEEDS,all_30_primary_results_retained=True,narrative_training=False,test_used=False))
    eng,names,x,indices=engine_and_features(cohort);y=np.array([r['author'] for r in cohort]);texts=np.array([r['Original'] for r in cohort]);groupmap={r['ID']:r['group'] for r in records(OUT/'development_groups.csv')};g=np.array([groupmap[r['ID']] for r in cohort]);features={'surface_66':x,'function_punctuation':x[:,indices],'char_tfidf':texts,'word_content_control':texts}
    predictions=[];metrics=[]
    for seed in SEEDS:
        pred={m:np.empty(len(cohort),dtype=object) for m in METHODS}
        for fold,(fit,dev) in enumerate(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=seed).split(texts,y,g)):
            assert not set(g[fit])&set(g[dev])
            for method in METHODS:
                model=pipeline(method,seed);model.fit(features[method][fit],y[fit]);pp=model.predict(features[method][dev]);pred[method][dev]=pp
                predictions.extend(dict(seed=seed,fold=fold,method=method,ID=cohort[i]['ID'],author_true=y[i],author_predicted=p) for i,p in zip(dev,pp))
        for method in METHODS:metrics.append(dict(seed=seed,method=method,n=len(cohort),authors=len(authors),accuracy=float(accuracy_score(y,pred[method])),macro_f1=float(f1_score(y,pred[method],average='macro',zero_division=0))))
    write('temporal_cv_predictions.csv',predictions);write('temporal_cv_seed_metrics.csv',metrics)
    summary=[dict(method=m,n=len(cohort),authors=len(authors),accuracy_mean=float(np.mean([r['accuracy'] for r in metrics if r['method']==m])),accuracy_seed_sd=float(np.std([r['accuracy'] for r in metrics if r['method']==m],ddof=1)),macro_f1_mean=float(np.mean([r['macro_f1'] for r in metrics if r['method']==m]))) for m in METHODS];write('temporal_cv_summary.csv',summary)
    pairgroups={groupmap[r['ID']] for r in pairs};fit=np.array([i for i,r in enumerate(cohort) if g[i] not in pairgroups]);ox=np.array([eng.style_features(r['Original']) for r in pairs]);wx=np.array([eng.style_features(r['ChatGPT_Style_Rewrite']) for r in pairs]);yy=np.array([by[r['ID']]['author'] for r in pairs]);fixed=[];fp=[]
    for method in METHODS:
        a=ox if method=='surface_66' else ox[:,indices] if method=='function_punctuation' else np.array([r['Original'] for r in pairs]);b=wx if method=='surface_66' else wx[:,indices] if method=='function_punctuation' else np.array([r['ChatGPT_Style_Rewrite'] for r in pairs]);model=pipeline(method,20261108);model.fit(features[method][fit],y[fit]);po=model.predict(a);pr=model.predict(b)
        fixed.append(dict(method=method,n_fit=len(fit),n_pairs=len(pairs),authors=len(authors),accuracy_original=float(accuracy_score(yy,po)),accuracy_rewrite=float(accuracy_score(yy,pr)),macro_f1_original=float(f1_score(yy,po,average='macro',zero_division=0)),macro_f1_rewrite=float(f1_score(yy,pr,average='macro',zero_division=0))))
        fp.extend(dict(method=method,ID=r['ID'],author_true=yy[i],original_prediction=po[i],rewrite_prediction=pr[i]) for i,r in enumerate(pairs))
    write('temporal_fixed_results.csv',fixed);write('temporal_fixed_predictions.csv',fp);write('temporal_fit_ids.csv',[dict(ID=cohort[i]['ID'],group=g[i],author=y[i]) for i in fit]);protected();print(json.dumps(dict(cv=summary,fixed=fixed)),flush=True)
if __name__=='__main__':main()

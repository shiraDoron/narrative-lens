"""Training-fold-only majority reference; no text, tuning or new author models."""
from run import *
def main():
    import numpy as np
    from sklearn.metrics import accuracy_score,f1_score
    rows=records(OUT/'cv_fold_assignments.csv');metrics=[];predictions=[]
    for cohort in sorted({r['cohort'] for r in rows}):
        for seed in SEEDS:
            ss=[r for r in rows if r['cohort']==cohort and int(r['seed'])==seed];pp=[]
            for fold in sorted({r['fold'] for r in ss}):
                fit=[r for r in ss if r['fold']==fold and r['role']=='fit'];dev=[r for r in ss if r['fold']==fold and r['role']=='dev'];counts=collections.Counter(r['author'] for r in fit);majority=sorted(counts,key=lambda a:(-counts[a],a))[0]
                pp.extend(dict(cohort=cohort,seed=seed,fold=fold,ID=r['ID'],author_true=r['author'],majority_prediction=majority) for r in dev)
            predictions.extend(pp);metrics.append(dict(cohort=cohort,seed=seed,accuracy=float(accuracy_score([r['author_true'] for r in pp],[r['majority_prediction'] for r in pp])),macro_f1=float(f1_score([r['author_true'] for r in pp],[r['majority_prediction'] for r in pp],average='macro',zero_division=0))))
    write('majority_fold_predictions.csv',predictions);write('majority_seed_metrics.csv',metrics)
    write('majority_cv_summary.csv',[dict(cohort=c,accuracy_mean=float(np.mean([r['accuracy'] for r in metrics if r['cohort']==c])),macro_f1_mean=float(np.mean([r['macro_f1'] for r in metrics if r['cohort']==c]))) for c in sorted({r['cohort'] for r in metrics})])
    original={r['ID']:r for r in records(OUT/'development_originals.csv')};pools=records(OUT/'paired_training_pool.csv');pairs=records(CHAT/'frozen_comparison_inputs.csv');result=[]
    for pool in sorted({r['pool'] for r in pools}):
        counts=collections.Counter(r['author'] for r in pools if r['pool']==pool);label=sorted(counts,key=lambda a:(-counts[a],a))[0];truth=[original[r['ID']]['author'] for r in pairs];pred=[label]*len(pairs)
        result.append(dict(pool=pool,majority_fit_author=label,accuracy=float(accuracy_score(truth,pred)),macro_f1=float(f1_score(truth,pred,average='macro',zero_division=0)),uniform_chance=1/len(set(truth))))
    write('majority_paired_reference.csv',result);dump('baseline_control_note.json',dict(purpose='Audit reference only, appended after the four fixed model runs; no model method or parameter selected from results',tie_break='Lexicographic author ID',uniform_chance='Analytic 1 / fit author classes',no_test=True));protected()
if __name__=='__main__':main()

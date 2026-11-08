"""Reconstruct sampling metadata and record the real integrity-test results."""
from run import *
import io,unittest
def main():
    import numpy as np
    pools=records(OUT/'paired_training_pool.csv');sample_rows=[]
    for pool in sorted({r['pool'] for r in pools}):
        pp=[r for r in pools if r['pool']==pool]
        for seed in SEEDS:
            rng=np.random.default_rng(seed)
            for author in sorted({r['author'] for r in pp}):
                subset=[r for r in pp if r['author']==author]
                sample_rows.extend(dict(pool=pool,seed=seed,ID=subset[j]['ID'],author=author) for j in rng.choice(len(subset),max(1,int(.8*len(subset))),replace=False))
    write('paired_resample_fit_ids.csv',sample_rows)
    for r in records(OUT/'paired_training_resample_stability.csv'):assert sum(v['pool']==r['pool'] and str(v['seed'])==r['seed'] for v in sample_rows)==int(r['n_fit'])
    pairs=records(CHAT/'analysis_cohort.csv');counts=collections.Counter(r['author'] for r in pairs);need={a:5-n for a,n in counts.items()};extra=[]
    for r in records(OUT/'additional_75_rewrites_manifest.csv'):
        if need[r['author']]>0:extra.append(r);need[r['author']]-=1
    assert len(extra)==15 and not any(need.values());write('additional_15_balanced_rewrites_manifest.csv',extra)
    ids={r['row_id'] for r in pairs};source=[r for r in records(OUT/'development_originals.csv') if r['ID'] not in ids];assert len(source)==172
    write('additional_172_author_only_manifest.csv',[dict(ID=r['ID'],author=r['author'],Original=r['Original'],eligible_narrative_proposal=r['eligible'],study_split='train',generation_status='not_generated') for r in source])
    result=dict(source_original_cv_model_fits=sum(int(r['folds']) for r in records(OUT/'cv_seed_metrics.csv')),fixed_paired_model_fits=len(records(OUT/'paired_fixed_model_results.csv')),training_resample_model_fits=len(records(OUT/'paired_training_resample_stability.csv')),posthoc_temporal_cv_model_fits=len(records(OUT/'temporal_cv_seed_metrics.csv'))*5,posthoc_temporal_fixed_model_fits=len(records(OUT/'temporal_fixed_results.csv')),narrative_classifier_model_fits=0,new_rewrites_generated=0,frozen_test_predictions=0,human_fields_filled=0)
    result['total_author_probe_fits']=sum(v for k,v in result.items() if k.endswith('model_fits'));dump('execution_summary.json',result)
    suite=unittest.defaultTestLoader.discover(str(OUT),pattern='test_integrity.py');stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);print(stream.getvalue(),flush=True)
    assert tests.wasSuccessful()
    report='# Integrity test results\n\n'+str(tests.testsRun)+' tests passed, 0 failures, 0 errors. Verified sources, paired/grouped folds, recomputed metrics, Holm adjustment, reconstruction of fit subsets, temporal-control separation and blank human fields. No Narrative Classifier or frozen test evaluation was run.\n\n```text\n'+stream.getvalue()+'```\n'
    (OUT/'TEST_RESULTS.md').write_text(report,encoding='utf8')
    dump('verification_audit.json',dict(tests_run=tests.testsRun,failures=len(tests.failures),errors=len(tests.errors),all_passed=True,test_code_sha256=sha(OUT/'test_integrity.py'),recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_inputs_unchanged=True,human_fields_blank=True,all_30_in_primary_paired_evaluation=True,posthoc_temporal_control_labeled_separately=True,narrative_classifier_fit_or_test=False))
if __name__=='__main__':main()

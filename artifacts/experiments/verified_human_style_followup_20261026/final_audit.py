"""Check reported results against saved predictions and experimental cohorts."""
from pathlib import Path
import hashlib,itertools,json
import numpy as np,pandas as pd
from sklearn.metrics import accuracy_score,f1_score
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def df(n):return pd.read_csv(P/n)
checks={}
def check(k,v):checks[k]=bool(v);assert v,k
x=df('analysis_cohort.csv');m=df('matched_cohort.csv');r=[json.loads(s) for s in (P/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
reg=read('author_registry.json');check('all_included_profiles_have_publisher_person_biography_and_byline_verification',all(a['verified_single_bylined_person'] for a in reg))
check('no_duplicate_person_names_or_biography_profiles',len({a['name'].casefold() for a in reg})==len(reg) and len({a['bio_url'].casefold() for a in reg})==len(reg))
check('complete_single_person_byline_header_audit',bool(df('full_byline_audit.csv').passed.all()))
check('analysis_authors_in_verified_byline_registry',set(x.author)<=set(a['author'] for a in reg))
check('source_text_hashes_match',all(hashlib.sha256(a.text.encode()).hexdigest()==a.text_sha256 for a in x.itertuples()))
check('author_disjoint_all_three_splits',all(not(set(x[x.split==a].author)&set(x[x.split==b].author)) for a,b in itertools.combinations(['train','val','test'],2)))
check('unique_generated_pair_keys',len({(a['row_id'],a['condition']) for a in r})==len(r))
keys={(a['row_id'],a['condition']) for a in r}
check('complete_three_transforms_for_every_source',all((rid,c) in keys for rid in x.row_id for c in ['Formatting','Paraphrase','Normalized']))
cf=df('counterfactual_selection.csv');check('complete_four_styles_for_every_selected_source',all((rid,c) in keys for rid in cf.row_id for c in ['Formal','Conversational','Concise','Elaborate']))
check('only_final_generator_in_primary_jsonl',all(a.get('generator')=='Qwen/Qwen2.5-3B-Instruct-GGUF' for a in r if a['condition']!='Formatting'))
v=df('rewrite_validation.csv');check('every_generated_pair_screened_once',len(v)==len(r) and not v.duplicated(['row_id','condition']).any())
passed=v.set_index(['row_id','condition']).passed
check('matched_rows_pass_all_three_screens',all(bool(passed.loc[rid,c]) for rid in m.row_id for c in ['Formatting','Paraphrase','Normalized']))
bad={a[k] for a in read('generated_cross_split_duplicates.json') for k in ['a','b']};check('generated_duplicate_members_excluded_symmetrically',not(set(m.row_id)&bad))
pred=df('narrative_predictions.csv');metrics=df('retraining_results.csv');active=[5,6];seeds={7,42,123,2026,31415}
check('five_seeds_per_comparison',all(set(g.seed)==seeds for _,g in metrics.groupby(['cohort','train_condition','test_condition'])))
probs=np.array([json.loads(t) for t in pred.probabilities]);check('finite_valid_seven_way_probabilities',probs.shape==(len(pred),7) and np.isfinite(probs).all() and (probs>=0).all() and np.allclose(probs.sum(1),1,atol=1e-6))
check('prediction_argmax_matches_saved_vectors',np.array_equal(probs.argmax(1),pred.predicted.to_numpy(int)))
check('true_probability_matches_label_index',np.allclose(probs[np.arange(len(pred)),pred.label.to_numpy(int)],pred.true_probability,atol=1e-7))
recomputed=[]
for key,g in pred.groupby(['cohort','seed','train_condition','test_condition']):
    selected=metrics[(metrics.cohort==key[0])&(metrics.seed==key[1])&(metrics.train_condition==key[2])&(metrics.test_condition==key[3])]
    assert len(selected)==1
    row=selected.iloc[0];f=f1_score(g.label,g.predicted,labels=active,average='macro',zero_division=0);a=accuracy_score(g.label,g.predicted)
    recomputed.append(abs(f-row.macro_f1)<1e-12 and abs(a-row.accuracy)<1e-12 and len(g)==row.n)
check('metrics_recomputed_from_predictions_match',all(recomputed))
cohorts={'full_original_baseline':x,'matched_all_four':m,'matched_confidence3':m[m.confidence_a>=3],'matched_nontrivial_rewrites':df('nontrivial_rewrite_cohort.csv')}
check('same_test_sources_in_every_condition_within_each_cohort',all(set(g.row_id)==set(cohorts[key[0]].query('split=="test"').row_id) for key,g in pred.groupby(['cohort','seed','train_condition','test_condition'])))
histories=list(P.glob('training_history_*.json'));check('every_training_run_used_twenty_epochs',bool(histories) and all(len(json.loads(f.read_text()))==20 for f in histories))
ap=P/'author_probe_predictions.csv'
if ap.exists() and ap.stat().st_size>10:
    p=df('author_probe_predictions.csv');ok=[]
    for _,g in p.groupby(['scope','seed','representation']):
        sets=[set(q.row_id) for _,q in g.groupby('condition')];ok.append(len(sets)==3 and all(a==sets[0] for a in sets))
    check('probe_conditions_use_identical_test_sources_and_refitted_representation',all(ok))
check('original_data_checkpoint_and_entire_previous_pilot_unchanged',read('protected_inputs_audit.json')['unchanged'])
check('human_adjudication_not_falsely_claimed',not read('verdict.json')['annotations_and_rewrites_independently_human_verified'])
check('report_and_plots_exist',(P/'final_research_report_he.md').exists() and len(list((P/'plots').glob('*.png')))>=2)
result={'checks':checks,'all_passed':all(checks.values()),'source_rows':len(x),'matched_rows':len(m),'narrative_prediction_rows':len(pred),'retraining_metric_rows':len(metrics),'training_runs':len(histories),'interpretation':'Integrity checks are not proof of semantic validity, human authorship beyond publisher bylines, or causality.'}
(P/'final_integrity_audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('Final artifact audit passed:',len(checks),'checks',flush=True)

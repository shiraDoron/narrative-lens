"""Small live status file; no model input/output is changed."""
from pathlib import Path
import collections,csv,datetime,json,time
P=Path(__file__).resolve().parent
def load(name,default):
    try:return json.loads((P/name).read_text(encoding='utf8'))
    except (OSError,ValueError):return default
def n_csv(name):
    p=P/name
    return sum(1 for _ in csv.DictReader(p.open(encoding='utf-8-sig',newline=''))) if p.exists() else 0
for _ in range(1440):
    records=[]
    try:
        for s in (P/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines():
            try:records.append(json.loads(s))
            except ValueError:pass
    except OSError:pass
    counts=collections.Counter(r['condition'] for r in records)
    baseline=load('evaluation_complete.json',{})
    finished=(P/'final_research_report_he.md').exists() and load('protected_inputs_audit.json',{}).get('unchanged',False)
    status={'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'computational_experiment_complete':finished,
      'scope':'two narrative classes, single publisher bylines, machine text-label proposals; human adjudication pending',
      'source_texts':n_csv('analysis_cohort.csv'),'generation_completed_by_condition':dict(counts),
      'generation_expected_main_per_condition':218,'generation_expected_counterfactual_per_style':32,
      'independent_nli_annotation_pairs_done':len(load('independent_nli_scores.json',[])),'independent_nli_annotation_pairs_total':3432,
      'rewrite_validation_rows':n_csv('rewrite_validation.csv'),'retraining_metric_rows':n_csv('retraining_results.csv'),
      'author_probe_metric_rows':n_csv('author_probe_results.csv'),'evaluation':baseline,'human_review_complete':False}
    (P/'run_status.json').write_text(json.dumps(status,indent=2),encoding='utf8')
    if finished:break
    time.sleep(30)

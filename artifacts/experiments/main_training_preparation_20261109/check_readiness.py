"""Fail closed. This command cannot launch a training job."""
import json
from prepare import HERE,read
from qc_contract import build_policy

def blockers():
    audit=json.loads((HERE/'DATA_READINESS_AUDIT.json').read_text())
    gen=json.loads((HERE/'GENERATOR_PROVENANCE.json').read_text())
    result=[]
    if audit['human_source_labels']<audit['required_human_labels_development']:result.append('Complete train/validation human source narrative labels missing')
    if audit['human_pair_reviews_completed']<105:result.append('Complete attributable human pair judgments missing; both Paraphrase/Style need QC; Claude is not human')
    if audit['missing_style']:result.append(f"{audit['missing_style']} Style rewrites missing for full105")
    for field in ['model','prompt','parameters']:
        if gen[field] is None:result.append(f'Original ChatGPT {field} unknown')
    try:
        labels=[r for r in read(HERE/'SOURCE_LABEL_INTAKE.csv') if r['split']=='train']
        build_policy(read(HERE/'TRAIN_CONDITION_ID_MAP.csv'),labels,read(HERE/'PAIRED_QC_INTAKE.csv'))
    except (ValueError,KeyError) as exc:
        result.append('Approved human intake contract blocked: '+str(exc))
    return result
if __name__=='__main__':
    reasons=blockers();print(json.dumps({'training_ready':not reasons,'blockers':reasons},indent=2))
    raise SystemExit(2 if reasons else 0)

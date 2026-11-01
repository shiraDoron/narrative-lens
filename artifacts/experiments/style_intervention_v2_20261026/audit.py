"""Check source/split/variant integrity and verify that human-review gating works.

Inputs: frozen predecessor artifacts and current outputs. Output: artifact_audit.json.
Passing computational checks does not imply human semantic validation or support
for the research hypothesis.
"""
import json
from study import OUT, PREVIOUS, rows, sha, read_json, write_json, reviewed_cohort, style_metrics


def main():
    """Fail on altered controls, mixed splits, missing outputs or fake review status."""
    checks=[]
    def check(name,condition):
        """Record an independently observable artifact assertion."""
        checks.append(dict(check=name,passed=bool(condition)))
        assert condition,name
    source=rows(OUT/'analysis_cohort.csv')
    for name in ['analysis_cohort.csv','author_splits.csv','split_definitions.csv']:
        check('Frozen '+name,sha(OUT/name)==sha(PREVIOUS/name))
    authors={s:{r['author'] for r in source if r['split']==s} for s in ['train','val','test']}
    check('Authors disjoint',all(not authors[a]&authors[b] for a,b in [('train','val'),('train','test'),('val','test')]))
    generated=[json.loads(line) for line in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
    keys=[(r['row_id'],r['condition']) for r in generated]
    check('Exactly one version per source and condition',len(keys)==654 and len(set(keys))==654)
    old={(r['row_id'],r['condition']):r for r in [json.loads(s) for s in (PREVIOUS/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]}
    check('Control rewrites frozen',all(r['rewrite']==old[r['row_id'],r['condition']]['rewrite'] for r in generated if r['condition']!='Normalized'))
    check('All versions screened',len(rows(OUT/'rewrite_validation.csv'))==654)
    check('Review pack has all 218 originals and both rewrites',len(rows(OUT/'human_review.csv'))==218 and all(r['original'] and r['Paraphrase'] and r['Normalized'] for r in rows(OUT/'human_review.csv')))
    check('Style measurements complete',len(rows(OUT/'style_change_metrics.csv'))==654)
    check('Explicit feature changes present',len(rows(OUT/'explicit_style_changes.csv'))==218*2*len(read_json(OUT/'style_feature_scaling.json')['names']))
    check('Identity edit metric zero',style_metrics('A sentence.','A sentence.')['word_edit_fraction']==0)
    check('Punctuation alone is not substantial',not style_metrics('A sentence!','A sentence.')['substantial_style_change'])
    check('Human gate detects pending labels',not read_json(OUT/'STATUS.json')['human_validation_complete'])
    try:
        reviewed_cohort()
        gate=False
    except RuntimeError as error:
        gate='Human review incomplete' in str(error)
    check('No evaluation permitted before real review',gate)
    check('No invented V2 model results',(not (OUT/'retraining_results.csv').exists()))
    check('Previous outputs unchanged',read_json(OUT/'previous_outputs_integrity.json')['passed'])
    for name in ['EXPERIMENT_GUIDE_HE.md','FINAL_REPORT_HE.md','README.md','HUMAN_REVIEW_HE.md','HUMAN_REVIEW.html','plots/style_intervention.png','plots/automatic_screen.png']:
        check('Readable artifact '+name,(OUT/name).exists() and (OUT/name).stat().st_size>0)
    import re
    html=(OUT/'HUMAN_REVIEW.html').read_text(encoding='utf8')
    embedded=json.loads(re.search(r'<script id="research-data" type="application/json">(.*?)</script>',html,re.S).group(1))
    check('Review HTML contains complete current CSV',embedded==rows(OUT/'human_review.csv'))
    write_json('artifact_audit.json',dict(checks=checks,all_passed=True,human_review_complete=False,scientific_verdict='pending human review, not evidence for hypothesis'))
    print(f'Passed {len(checks)} artifact checks; human review pending.',flush=True)


if __name__=='__main__':main()

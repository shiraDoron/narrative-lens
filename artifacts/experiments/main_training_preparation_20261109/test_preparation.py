import collections
import copy
import json
import re
import subprocess
import sys
import unittest
from prepare import HERE,ROOT,F,C,ARMS,SEEDS,read,sha,schedules
from qc_contract import build_policy,text_hash
from check_readiness import blockers


class PreparationTests(unittest.TestCase):
    def test_01_raw_sources_unchanged(self):
        frozen=json.loads((HERE/'SOURCE_HASHES.json').read_text())
        self.assertTrue(all(sha(ROOT/p)==h for p,h in frozen.items()))

    def test_02_id_coverage_and_missing75_exact(self):
        mapping=read(HERE/'TRAIN_CONDITION_ID_MAP.csv')
        self.assertEqual(len(mapping),105);self.assertEqual(len({r['ID'] for r in mapping}),105)
        missing={r['ID'] for r in read(HERE/'STYLE_REWRITE_MISSING_75.csv')}
        self.assertEqual(len(missing),75)
        self.assertEqual(missing,{r['ID'] for r in mapping if not r['Style']})
        self.assertTrue(all(r['Original'] and r['Paraphrase'] for r in mapping))

    def test_03_views_same_labels_ids_and_counts(self):
        views={a:read(HERE/f'DRAFT_ARM_{a}.csv') for a in ARMS}
        base={r['ID']:r['label'] for r in views['A']}
        self.assertEqual(len(base),30)
        for a,rows in views.items():
            self.assertEqual(len(rows),30*len(ARMS[a]))
            self.assertEqual({r['ID']:r['label'] for r in rows},base)
            self.assertEqual(collections.Counter(r['ID'] for r in rows),{rid:len(ARMS[a]) for rid in base})
        self.assertEqual([r['ID'] for r in views['D']],[r['ID'] for r in views['E']])

    def test_04_disjoint_authors_and_no_test_in_training_views(self):
        cohort=read(F/'analysis_cohort.csv')
        authors={s:{r['author'] for r in cohort if r['split']==s} for s in ['train','val','test']}
        self.assertFalse(authors['train']&authors['val']);self.assertFalse(authors['train']&authors['test'])
        self.assertFalse(authors['val']&authors['test'])
        train={r['row_id'] for r in cohort if r['split']=='train'}
        self.assertTrue({r['ID'] for r in read(HERE/'TRAIN_CONDITION_ID_MAP.csv')}<=train)

    def test_05_schedules_reproduce_equal_budget_all_seeds(self):
        for seed in SEEDS:
            for a in ARMS:
                config=json.loads((HERE/f'CONFIG_{a}_seed{seed}.json').read_text())
                view=read(HERE/config['view_file']);stored=read(HERE/config['schedule'])
                expected=[{k:str(v) for k,v in r.items()} for r in schedules(view,seed,40)]
                self.assertEqual(stored,expected)
                self.assertEqual(len(stored),640);self.assertEqual(len({r['step'] for r in stored}),40)
                self.assertFalse(config['training_ready'])
            d=read(HERE/f'SCHEDULE_D_seed{seed}.csv');e=read(HERE/f'SCHEDULE_E_seed{seed}.csv')
            self.assertEqual([(r['ID'],r['view_index']) for r in d],[(r['ID'],r['view_index']) for r in e])

    def test_06_generation_provenance_missing_blocks(self):
        meta=json.loads((HERE/'GENERATOR_PROVENANCE.json').read_text())
        self.assertIsNone(meta['prompt']);self.assertIsNone(meta['model']);self.assertFalse(meta['generation_permitted'])
        self.assertTrue(blockers())
        cli=subprocess.run([sys.executable,str(HERE/'check_readiness.py')],capture_output=True,text=True)
        self.assertEqual(cli.returncode,2)
        self.assertFalse(json.loads(cli.stdout)['training_ready'])

    def test_07_review_separation_and_notes(self):
        human=json.loads((HERE/'HUMAN_REVIEW_IMPORT_STATUS.json').read_text())
        self.assertEqual(human['completed_rows'],0)
        reviews=read(HERE/'CLAUDE_REVIEW_PER_ID_IMPORTED.csv')
        self.assertEqual(len(reviews),30);self.assertEqual(len({r['ID'] for r in reviews}),30)
        self.assertTrue(all(r['notes'] and r['review_type']=='External LLM Review' for r in reviews))
        self.assertEqual(sum(r['style_change_valid']=='Borderline' for r in reviews),2)

    def fixture(self):
        # Tiny technical fixtures, not experimental text generation or human judgments.
        rows=[dict(ID='fixture1',label='Left-wing',split='train',Original='source1',Paraphrase='para1',Style='style1'),
              dict(ID='fixture2',label='Right-wing',split='train',Original='source2',Paraphrase='para2',Style='style2')]
        person=dict(reviewer_type='human',reviewer_id='test-person',review_date='2026-11-09')
        labels=[dict(ID=r['ID'],human_label=r['label'],source_sha256=text_hash(r['Original']),**person) for r in rows]
        reviews=[dict(ID=r['ID'],variant=v,source_sha256=text_hash(r['Original']),rewrite_sha256=text_hash(r[v]),
          meaning='Yes',stance='Yes',style_change='Yes',semantic_drift='No',notes='',**person) for r in rows for v in ['Paraphrase','Style']]
        return rows,labels,reviews

    def test_08_symmetric_fallback_and_secondary_cohort(self):
        rows,labels,reviews=self.fixture();reviews[1]['style_change']='Borderline';reviews[1]['notes']='minimal'
        result=build_policy(rows,labels,reviews)
        self.assertEqual(result['primary_all_attempted']['B'][0]['text'],'source1')
        self.assertEqual(result['primary_all_attempted']['C'][0]['text'],'source1')
        for a in ARMS:self.assertEqual({r['ID'] for r in result['primary_all_attempted'][a]},{'fixture1','fixture2'})
        self.assertEqual({r['ID'] for r in result['secondary_common_accepted']['A']},{'fixture2'})

    def test_09_llm_not_human(self):
        rows,labels,reviews=self.fixture();reviews[0]['reviewer_type']='LLM'
        with self.assertRaisesRegex(ValueError,'Human'):build_policy(rows,labels,reviews)

    def test_10_hash_mismatch_rejected(self):
        rows,labels,reviews=self.fixture();reviews[0]['rewrite_sha256']='bad'
        with self.assertRaisesRegex(ValueError,'hash'):build_policy(rows,labels,reviews)

    def test_11_missing_generation_is_not_silent_fallback(self):
        rows,labels,reviews=self.fixture();rows[0]['Style']=''
        with self.assertRaisesRegex(ValueError,'Missing generation'):build_policy(rows,labels,reviews)

    def test_12_duplicate_or_missing_qc_rejected(self):
        rows,labels,reviews=self.fixture()
        with self.assertRaisesRegex(ValueError,'Duplicate'):build_policy(rows,labels,reviews+[reviews[0]])
        with self.assertRaisesRegex(ValueError,'coverage'):build_policy(rows,labels,reviews[:-1])

    def test_13_gold_disagreement_not_silent_relabel(self):
        rows,labels,reviews=self.fixture();labels[0]['human_label']='Right-wing'
        with self.assertRaisesRegex(ValueError,'disagreement'):build_policy(rows,labels,reviews)

    def test_14_intake_blank_not_invented(self):
        rows=read(HERE/'SOURCE_LABEL_INTAKE.csv');self.assertEqual(len(rows),148)
        self.assertTrue(all(not r['human_label'] and not r['reviewer_id'] for r in rows))
        pairs=read(HERE/'PAIRED_QC_INTAKE.csv');self.assertEqual(len(pairs),210)
        self.assertTrue(all(not r['meaning'] and not r['reviewer_id'] for r in pairs))

    def test_15_bibtex_catalog_and_fields(self):
        catalog=json.loads((HERE/'LITERATURE_CATALOG.json').read_text(encoding='utf-8'))
        bib=(ROOT/'REFERENCES.bib').read_text(encoding='utf-8');self.assertEqual(len(catalog),18)
        keys=re.findall(r'@\w+\{([^,]+),',bib);self.assertEqual(set(keys),{r['key'] for r in catalog})
        self.assertEqual(len(keys),len(set(keys)));self.assertEqual(bib.count('{'),bib.count('}'))
        for r in catalog:
            self.assertTrue(all(r[k] for k in ['title','authors','year','venue','official_url','datasets','evaluation','limitations','untested']))
        cato=next(r for r in catalog if r['key']=='cato')
        self.assertEqual(cato['title'],'Data Augmentations for Improved (Large) Language Model Generalization')

    def test_16_document_links(self):
        for name in ['THESIS_RESEARCH_DIRECTION_HE.md','MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md',
          'RELATED_WORK_DEEP_REVIEW_HE.md','RELATED_WORK_COMPARISON.md','RESEARCH_GAP_AND_CONTRIBUTION_HE.md']:
            text=(ROOT/name).read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('http:','https:','#')):self.assertTrue((ROOT/link.split('#')[0]).exists(),(name,link))

if __name__=='__main__':unittest.main(verbosity=2)

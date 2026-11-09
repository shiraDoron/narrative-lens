import hashlib
import json
import math
from pathlib import Path
import re
import unittest
import numpy as np
import run_pilot as run


class FrozenSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=run.read(run.HERE/'pilot_inputs.csv')
        cls.pred=run.read(run.HERE/'predictions.csv')
        cls.trans=run.read(run.HERE/'transitions.csv')
        cls.summary=run.read(run.HERE/'summary.csv')
        cls.probs={(r['ID'],r['condition']):np.array([float(r['p_'+l]) for l in run.LABELS]) for r in cls.pred}

    def test_01_frozen_sources_and_checkpoints_unchanged(self):
        run.verify()

    def test_02_all_30_same_ids_all_three_conditions(self):
        self.assertEqual(len(self.inputs),90)
        expected={r['ID'] for r in run.read(run.C/'frozen_comparison_inputs.csv')}
        for arm in ['Original','ChatGPT','Paraphrase']:
            rows=[x for x in self.pred if x['condition']==arm]
            self.assertEqual(len(rows),30)
            self.assertEqual({x['ID'] for x in rows},expected)
        self.assertEqual({r['split'] for r in self.inputs},{'train'})

    def test_03_frozen_input_bytes_and_label_compatibility(self):
        expected=[{k:str(v) for k,v in row.items()} for row in run.inputs()]
        self.assertEqual(expected,self.inputs)

    def test_04_probabilities_finite_normalized_and_predictions_match(self):
        for r in self.pred:
            p=self.probs[r['ID'],r['condition']]
            self.assertTrue(np.isfinite(p).all())
            self.assertTrue(((p>=0)&(p<=1)).all())
            self.assertAlmostEqual(p.sum(),1,places=6)
            self.assertEqual(run.LABELS[p.argmax()],r['prediction'])
            self.assertAlmostEqual(float(r['confidence']),p.max(),places=7)

    def test_05_every_transition_recomputed(self):
        self.assertEqual(len(self.trans),60)
        for r in self.trans:
            a=self.probs[r['ID'],'Original'];b=self.probs[r['ID'],r['condition']];m=(a+b)/2
            self.assertEqual(int(r['flip']),int(a.argmax()!=b.argmax()))
            self.assertAlmostEqual(float(r['total_variation']),abs(b-a).sum()/2,places=7)
            js=sum(np.sum(x*np.log(np.maximum(x,1e-30)/m)) for x in [a,b])/2
            # Inference used float32; CSV recomputation here is float64.
            self.assertAlmostEqual(float(r['js_nats']),js,delta=2e-7)
            self.assertAlmostEqual(float(r['delta_original_predicted_probability']),b[a.argmax()]-a.max(),places=7)

    def test_06_summaries_recompute_no_accuracy_claim(self):
        for s in self.summary:
            g=[r for r in self.trans if r['condition']==s['condition']]
            self.assertEqual(int(s['n']),len(g))
            self.assertEqual(int(s['flips']),sum(int(x['flip']) for x in g))
            for field in ['flip','total_variation','js_nats','delta_confidence','delta_margin']:
                self.assertAlmostEqual(float(s['mean_'+field]),np.mean([float(x[field]) for x in g]),places=9)
        c=json.loads((run.HERE/'paired_control_comparison.json').read_text())
        self.assertIsNone(c['accuracy']);self.assertIsNone(c['macro_f1'])

    def test_07_case_table_exact_join(self):
        cases=run.read(run.HERE/'per_id_comparison.csv')
        self.assertEqual(len(cases),30)
        source={(r['ID'],r['condition']):r['text'] for r in self.inputs}
        for r in cases:
            for field,arm in [('Original','Original'),('ChatGPT','ChatGPT'),('Paraphrase','Paraphrase')]:
                self.assertEqual(r[field],source[r['ID'],arm])

    def test_08_no_new_fit_or_test_inference(self):
        audit=json.loads((run.HERE/'execution_audit.json').read_text())
        self.assertEqual(audit['new_fits'],0);self.assertEqual(audit['new_rewrites'],0)
        self.assertEqual(audit['n_val_or_test_predictions'],0)
        protocol=json.loads((run.HERE/'protocol.json').read_text())
        self.assertIn('all 30 Originals seen',protocol['head_training'])
        source=Path(run.__file__).read_text()
        self.assertNotIn('.backward(',source);self.assertNotIn('base.train(',source)

    def test_09_literature_sources_and_seven_fields(self):
        papers=json.loads((run.HERE/'literature_sources.json').read_text(encoding='utf-8'))
        self.assertEqual(len(papers),12)
        for p in papers:self.assertTrue(p['urls'])
        text=(run.ROOT/'RESEARCH_GAP_AND_NOVELTY_HE.md').read_text(encoding='utf-8')
        blocks=[b for b in re.split(r'\n## ',text) if re.match(r'\d+\.',b)]
        for b in blocks:
            self.assertEqual(len(re.findall(r'^- \*\*',b,re.M)),7)

    def test_10_document_local_links_exist(self):
        for name in ['RESEARCH_GAP_AND_NOVELTY_HE.md','EVIDENCE_MATRIX_HE.md','STYLE_SENSITIVITY_PILOT_HE.md']:
            text=(run.ROOT/name).read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('http:','https:','#')):
                    self.assertTrue((run.ROOT/link.split('#')[0]).exists(),(name,link))


if __name__=='__main__':unittest.main(verbosity=2)

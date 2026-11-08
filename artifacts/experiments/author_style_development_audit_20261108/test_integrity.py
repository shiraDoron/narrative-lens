"""Real-data invariants for source preservation, grouped evaluation and reporting."""
import unittest
from run import *
import numpy as np
from sklearn.metrics import accuracy_score,f1_score
from scipy.stats import binomtest

class IntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=records(OUT/'development_originals.csv');cls.ids={r['ID'] for r in cls.rows};cls.authors={r['ID']:r['author'] for r in cls.rows};cls.pairs=records(CHAT/'frozen_comparison_inputs.csv');cls.pairids={r['ID'] for r in cls.pairs}
        cls.cv=records(OUT/'cv_predictions.csv');cls.folds=records(OUT/'cv_fold_assignments.csv');cls.fixed=records(OUT/'paired_fixed_model_predictions.csv')
    def test_01_frozen_sources_unchanged(self):protected()
    def test_02_only_train_authors_used(self):
        frozen={r['author']:r['split'] for r in records(SOURCE/'author_splits.csv')}
        self.assertEqual(len(self.rows),202);self.assertEqual(len(set(self.authors.values())),9)
        self.assertTrue(all(frozen[a]=='train' for a in self.authors.values()))
        self.assertTrue(all(p['author_true'] in set(self.authors.values()) for p in self.cv+self.fixed))
    def test_03_no_pair_filtered(self):
        self.assertEqual(len(self.pairids),30)
        for pool in {r['pool'] for r in self.fixed}:
            for method in METHODS:
                rows=[r for r in self.fixed if r['pool']==pool and r['method']==method]
                self.assertEqual(len(rows),30);self.assertEqual({r['ID'] for r in rows},self.pairids)
    def test_04_group_disjoint_cv(self):
        for key in {(r['cohort'],r['seed'],r['fold']) for r in self.folds}:
            rows=[r for r in self.folds if (r['cohort'],r['seed'],r['fold'])==key]
            fit={r['group'] for r in rows if r['role']=='fit'};dev={r['group'] for r in rows if r['role']=='dev'}
            self.assertFalse(fit&dev)
            sourcefit={r['ID'] for r in rows if r['role']=='fit'};sourcedev={r['ID'] for r in rows if r['role']=='dev'}
            self.assertFalse(sourcefit&sourcedev)
    def test_05_every_cv_metric_recomputes(self):
        for m in records(OUT/'cv_seed_metrics.csv'):
            pp=[r for r in self.cv if (r['cohort'],r['seed'],r['method'])==(m['cohort'],m['seed'],m['method'])]
            self.assertEqual(len(pp),int(m['n']));self.assertEqual(len({r['ID'] for r in pp}),len(pp))
            self.assertAlmostEqual(accuracy_score([r['author_true'] for r in pp],[r['author_predicted'] for r in pp]),float(m['accuracy']))
            self.assertAlmostEqual(f1_score([r['author_true'] for r in pp],[r['author_predicted'] for r in pp],average='macro',zero_division=0),float(m['macro_f1']))
    def test_06_fixed_fit_excludes_all_paired_groups(self):
        groups={r['ID']:r['group'] for r in records(OUT/'development_groups.csv')};evalgroups={groups[i] for i in self.pairids}
        pools=records(OUT/'paired_training_pool.csv')
        for row in pools:self.assertNotIn(row['group'],evalgroups);self.assertNotIn(row['ID'],self.pairids)
        self.assertEqual(sum(r['pool']=='all_train_excluding_pairs' for r in pools),172)
        self.assertEqual(sum(r['pool']=='eligible_train_excluding_pairs' for r in pools),75)
    def test_07_fixed_metrics_and_mcnemar(self):
        for m in records(OUT/'paired_fixed_model_results.csv'):
            pp=[r for r in self.fixed if r['pool']==m['pool'] and r['method']==m['method']];truth=[r['author_true'] for r in pp]
            for v in ['original','rewrite']:
                pred=[r[v+'_prediction'] for r in pp];self.assertAlmostEqual(accuracy_score(truth,pred),float(m['accuracy_'+v]));self.assertAlmostEqual(f1_score(truth,pred,average='macro',zero_division=0),float(m['macro_f1_'+v]))
            loss=sum(r['original_correct']=='True' and r['rewrite_correct']=='False' for r in pp);gain=sum(r['original_correct']=='False' and r['rewrite_correct']=='True' for r in pp)
            self.assertEqual(loss,int(m['original_correct_rewrite_wrong']));self.assertEqual(gain,int(m['original_wrong_rewrite_correct']))
            self.assertAlmostEqual(float(binomtest(gain,gain+loss,.5).pvalue) if gain+loss else 1.,float(m['mcnemar_exact_p']))
    def test_08_holm_uses_all_four_primary_methods(self):
        rr=sorted([r for r in records(OUT/'paired_fixed_model_results.csv') if r['pool']=='all_train_excluding_pairs'],key=lambda r:float(r['mcnemar_exact_p']));self.assertEqual(len(rr),4);maximum=0.
        for i,r in enumerate(rr):maximum=max(maximum,min(1.,(4-i)*float(r['mcnemar_exact_p'])));self.assertAlmostEqual(maximum,float(r['holm_primary_p']))
    def test_09_original_human_package_blank_and_exact(self):
        hh=records(PREVIOUS/'HUMAN_VALIDATION_30.csv');fields=['human_meaning_preserved','human_narrative_stance_preserved','human_style_change_valid','human_semantic_drift','human_notes'];by={r['ID']:r for r in self.pairs}
        self.assertEqual(set(hh[0]),{'ID','Original','ChatGPT_Style_Rewrite',*fields});self.assertEqual(len(hh),30)
        for r in hh:
            self.assertTrue(all(r[k]=='' for k in fields));self.assertEqual(r['Original'],by[r['ID']]['Original']);self.assertEqual(r['ChatGPT_Style_Rewrite'],by[r['ID']]['ChatGPT_Style_Rewrite'])
    def test_10_additional_rewrite_manifest_exact(self):
        rr=records(OUT/'additional_75_rewrites_manifest.csv');eligible={r['ID'] for r in self.rows if r['eligible']=='True'}
        self.assertEqual(len(rr),75);self.assertEqual({r['ID'] for r in rr},eligible-self.pairids)
        self.assertTrue(all(r['generation_status']=='not_generated' and r['study_split']=='train' for r in rr))
    def test_11_no_test_or_val_in_topics_and_style(self):
        self.assertEqual({r['ID'] for r in records(OUT/'development_topic_assignments.csv')},self.ids)
        self.assertEqual({r['ID'] for r in records(OUT/'paired_lexical_structure_metrics.csv')},self.pairids)
        self.assertFalse(read('corpus_audit_summary.json')['test_content_features_computed'])
    def test_12_confusion_totals(self):
        for method in METHODS:
            rr=records(OUT/('cv_confusion_'+method+'.csv'));self.assertEqual(sum(int(v) for r in rr for k,v in r.items() if k!='author_true'),202*5)
    def test_13_old_30_probe_is_recomputed_without_retraining(self):
        pp=records(PREVIOUS/'author_id_predictions.csv');scores=records(PREVIOUS/'author_id_seed_metrics.csv')
        for m in scores:
            r=[r for r in pp if r['seed']==m['seed'] and r['version']==m['version']];self.assertEqual(len({v['ID'] for v in r}),30)
            self.assertAlmostEqual(accuracy_score([v['author_true'] for v in r],[v['author_predicted'] for v in r]),float(m['accuracy']))
    def test_14_protocol_frozen_before_results(self):
        self.assertEqual(read('protocol.json')['script_sha256_before_results'],sha(OUT/'run.py'))
        self.assertEqual(read('baseline_runtime_audit.json')['protocol_sha256'],sha(OUT/'protocol.json'))
    def test_15_source_article_groups_unique(self):
        self.assertEqual(len({r['article'] for r in self.rows}),202);self.assertEqual(len({r['ID'] for r in self.rows}),202)
    def test_16_aggregate_review_not_invented_per_id(self):
        review=json.loads((PREVIOUS/'external_llm_review_aggregate.json').read_text(encoding='utf8'));self.assertFalse(review['per_id_ratings_available']);self.assertEqual(review['clean_count'],16)
    def test_17_temporal_sensitivity_is_train_only_and_pair_disjoint(self):
        p=read('temporal_control_protocol.json');self.assertEqual(p['n_sources'],139);self.assertEqual(p['n_pairs'],20);self.assertEqual(len(p['authors']),6)
        selected={r['ID'] for r in self.rows if r['author'] in p['authors']}
        self.assertTrue(all(r['source_date'].startswith('2026') for r in self.rows if r['ID'] in selected))
        fixed=records(OUT/'temporal_fixed_predictions.csv');fit={r['ID'] for r in records(OUT/'temporal_fit_ids.csv')}
        self.assertTrue(all(r['ID'] in selected for r in fixed));self.assertFalse(fit&{r['ID'] for r in fixed})
        self.assertEqual(len(fit),119)
        for m in records(OUT/'temporal_fixed_results.csv'):
            pp=[r for r in fixed if r['method']==m['method']]
            self.assertEqual(len(pp),20)
            for v in ['original','rewrite']:self.assertAlmostEqual(accuracy_score([r['author_true'] for r in pp],[r[v+'_prediction'] for r in pp]),float(m['accuracy_'+v]))
    def test_18_source_human_forms_are_not_machine_gold(self):
        forms=records(SOURCE/'human_annotation_blind.csv');self.assertEqual(len(forms),429)
        self.assertTrue(all(not r.get(k,'').strip() for r in forms for k in ['human_label','human_confidence','ambiguous','evidence','notes']))
    def test_19_resample_and_expansion_metadata(self):
        poolrows=records(OUT/'paired_training_pool.csv');samples=records(OUT/'paired_resample_fit_ids.csv')
        for r in samples:self.assertIn(r['ID'],{p['ID'] for p in poolrows if p['pool']==r['pool']});self.assertNotIn(r['ID'],self.pairids)
        for m in records(OUT/'paired_training_resample_stability.csv'):self.assertEqual(sum(r['pool']==m['pool'] and r['seed']==m['seed'] for r in samples),int(m['n_fit']))
        extra=records(OUT/'additional_15_balanced_rewrites_manifest.csv');self.assertEqual(len(extra),15);self.assertFalse({r['ID'] for r in extra}&self.pairids)
        counts=collections.Counter(self.authors[i] for i in self.pairids);counts.update(r['author'] for r in extra);self.assertEqual(set(counts.values()),{5})
        self.assertEqual({r['ID'] for r in records(OUT/'additional_172_author_only_manifest.csv')},self.ids-self.pairids)

if __name__=='__main__':unittest.main(verbosity=2)

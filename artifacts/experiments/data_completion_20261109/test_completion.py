import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
import bundle as b
import import_review as ir
import receive_rewrites as rr
import automatic_qc as aq
import compile_candidates as cc


class CompletionTests(unittest.TestCase):
    def test_01_protected_legacy_inputs(self):b.verify()

    def test_02_75_exact_train_no_duplicates_or_legacy(self):
        rows=b.read(b.HERE/'STYLE_REWRITE_INPUT_75.csv');expected={r['ID'] for r in b.missing()}
        self.assertEqual(len(rows),75);self.assertEqual({r['id'] for r in rows},expected)
        self.assertFalse(expected&set(b.legacy()));self.assertEqual(len({r['source_sha256'] for r in rows}),75)
        cohort={r['row_id']:r for r in b.read(b.FOLLOW/'analysis_cohort.csv')}
        self.assertTrue(all(cohort[r['id']]['split']=='train' for r in rows))
        self.assertEqual(set(rows[0]),{'id','original','source_sha256','protocol_version'})

    def test_03_five_batches_exact_partition(self):
        rows=[]
        for p in sorted((b.HERE/'chatgpt_batches').glob('*.csv')):
            batch=b.read(p);self.assertEqual(len(batch),15);rows+=batch
        self.assertEqual(rows,b.read(b.HERE/'STYLE_REWRITE_INPUT_75.csv'))

    def test_04_labels_105_unfilled_correct_proposals(self):
        rows=b.read(b.HERE/'NARRATIVE_LABEL_VALIDATION_105.csv');expected={r['ID']:r for r in b.mapping()}
        self.assertEqual(len(rows),105);self.assertEqual({r['ID'] for r in rows},set(expected))
        for r in rows:
            self.assertEqual(r['Original'],expected[r['ID']]['Original']);self.assertEqual(r['proposed_label'],expected[r['ID']]['label'])
            self.assertFalse(r['human_label']);self.assertFalse(r['reviewer_id'])
        self.assertNotIn('author',rows[0])

    def test_05_review_templates_blank_and_pending(self):
        old=b.read(b.HERE/'HUMAN_PAIR_REVIEW_LEGACY30.csv');new=b.read(b.HERE/'HUMAN_PAIR_REVIEW_NEW75_TEMPLATE.csv')
        self.assertEqual(len(old),30);self.assertEqual(len(new),75)
        self.assertTrue(all(r['ChatGPT_Style_Rewrite'] for r in old))
        self.assertTrue(all(not r['ChatGPT_Style_Rewrite'] and 'pending' in r['review_status'] for r in new))
        for r in old+new:
            self.assertTrue(all(not r[k] for k in ir.FIELDS))
            self.assertFalse(set(r)&{'label','author','scores','passed','guard_entities'})

    def fixture(self):
        expected={'fixture':dict(Original='source',Style='rewrite',label='Left-wing')}
        row=dict(ID='fixture',Original='source',ChatGPT_Style_Rewrite='rewrite',
          human_meaning_preserved='Yes',human_narrative_stance_preserved='Yes',human_style_change_valid='Borderline',
          human_semantic_drift='No',human_notes='unit-test fixture only')
        return expected,row

    def test_06_import_ratings_preserved_not_autoaccepted(self):
        expected,row=self.fixture();result=ir.validate([row],expected,'pairs30','human')
        self.assertEqual(result[0]['human_style_change_valid'],'Borderline');self.assertEqual(result[0]['human_notes'],row['human_notes'])

    def test_07_import_duplicate_missing_wrong_id(self):
        expected,row=self.fixture()
        for rows in [[row,row],[],[{**row,'ID':'test-author-id'}]]:
            with self.assertRaises(ValueError):ir.validate(rows,expected,'pairs30','human')

    def test_08_import_exact_text_binding(self):
        expected,row=self.fixture()
        for field in ['Original','ChatGPT_Style_Rewrite']:
            with self.assertRaises(ValueError):ir.validate([{**row,field:'changed'}],expected,'pairs30','human')

    def test_09_blank_review_is_not_complete(self):
        rows=ir.parse(b.HERE/'HUMAN_PAIR_REVIEW_LEGACY30.md','pairs30')
        self.assertEqual(len(rows),30)
        with self.assertRaisesRegex(ValueError,'missing/invalid'):ir.validate(rows,b.legacy(),'pairs30','human')

    def test_10_llm_not_human(self):
        expected,row=self.fixture()
        with self.assertRaises(ValueError):ir.validate([{**row,'review_type':'External LLM Review'}],expected,'pairs30','human')
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'claude.md';source.write_text('**Reviewer:** Claude (LLM-based review)',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'LLM review'):ir.import_file(source,'pairs30','human','test','2026-11-09','fixture')

    def test_11_immutable_import_receipt_and_raw_bytes(self):
        expected,row=self.fixture()
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/'fixture.csv';b.save(source,[row]);raw=source.read_bytes()
            with patch.object(ir,'HERE',tmp),patch.object(ir,'verify',lambda:None),patch.object(ir,'registry',lambda *a:expected):
                dest=ir.import_file(source,'pairs30','human','unit-test-person','2026-11-09','fixture')
                self.assertEqual((dest/'received.csv').read_bytes(),raw)
                self.assertEqual(b.read(dest/'reviews_by_id.csv')[0]['human_style_change_valid'],'Borderline')
                with self.assertRaises(ValueError):ir.import_file(source,'pairs30','human','unit-test-person','2026-11-09','fixture')

    def test_12_receive75_binds_original_and_builds_full_blind_review(self):
        # Identity outputs exercise IO only, not a new generator or scientific rewrite run.
        rows=[dict(id=r['ID'],chatgpt_style_rewrite=r['Original']) for r in b.missing()]
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/'fixture.csv';b.save(source,rows)
            data=rr.combine([source]);self.assertEqual(len(data),75)
            b.make_pair_package(data,tmp/'pairs',75)
            package=b.read(tmp/'pairs.csv');self.assertTrue(all(r['ChatGPT_Style_Rewrite'] and r['review_status']=='ready_for_human' for r in package))
            duplicate=tmp/'dupe.csv';b.save(duplicate,rows+[rows[0]])
            with self.assertRaises(ValueError):rr.combine([duplicate])
            unknown=tmp/'wrong.csv';b.save(unknown,[{**r,'id':next(iter(b.legacy()))} if i==0 else r for i,r in enumerate(rows)])
            with self.assertRaises(ValueError):rr.combine([unknown])

    def test_13_real_receive_then_qc_dryrun_no_models_or_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/'fixture.csv'
            b.save(source,[dict(id=r['ID'],chatgpt_style_rewrite=r['Original']) for r in b.missing()])
            meta=tmp/'meta.json';b.dump(meta,json.loads((b.HERE/'GENERATION_METADATA_TEMPLATE.json').read_text()))
            # Receiver needs the immutable prompt, copied into this technical sandbox.
            (tmp/'STYLE_REWRITE_PROMPT_V1.txt').write_bytes((b.HERE/'STYLE_REWRITE_PROMPT_V1.txt').read_bytes())
            with patch.object(rr,'HERE',tmp),patch.object(rr,'verify',lambda:None):dest=rr.receive([source],'fixture',meta)
            with patch.object(aq,'HERE',tmp):
                identity=aq.screen('fixture',dry_run=True)
                self.assertEqual(identity['semantic_similarity'],.85);self.assertEqual(identity['bidirectional_nli'],.6)
                self.assertFalse((dest/'automatic_qc').exists())
                # Tampering after receipt is rejected before loading ML models.
                with (dest/'received_rewrites_75.csv').open('a') as f:f.write('\n')
                with self.assertRaises(ValueError):aq.screen('fixture',dry_run=True)

    def test_14_prompt_and_batch_hashes_frozen(self):
        protocol=json.loads((b.HERE/'GENERATION_PROTOCOL.json').read_text())
        self.assertEqual(protocol['prompt_sha256'],b.sha(b.HERE/'STYLE_REWRITE_PROMPT_V1.txt'))
        self.assertFalse(protocol['legacy_prompt_reconstruction'])
        for name,digest in protocol['batch_sha256'].items():self.assertEqual(b.sha(b.HERE/'chatgpt_batches'/name),digest)
        audit=json.loads((b.CHAT/'validator_identity_audit.json').read_text())
        for path,digest in audit['unchanged_code_sha256'].items():self.assertEqual(b.sha(b.ROOT/path),digest)

    def test_15_markdown_label_intake_parses(self):
        rows=ir.parse(b.HERE/'NARRATIVE_LABEL_VALIDATION_105.md','labels105')
        self.assertEqual(len(rows),105)
        expected={r['ID']:r for r in b.mapping()}
        self.assertTrue(all(r['Original']==expected[r['ID']]['Original'] for r in rows))

    def test_16_local_links(self):
        for name in ['README_HE.md','QC_RULES_HE.md']:
            text=(b.HERE/name).read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('http:','https:','#')):self.assertTrue((b.HERE/link).exists(),link)

    def test_17_full105_bridge_same_ids_and_unchanged_legacy(self):
        # Fixture echoes source; tests compilation only, not generation quality.
        received={r['ID']:dict(Original=r['Original'],Style=r['Original']) for r in b.missing()}
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);(tmp/'runs'/'fixture').mkdir(parents=True)
            with patch.object(cc,'HERE',tmp),patch.object(cc,'registry',lambda *a:received):out=cc.compile_run('fixture')
            rows=b.read(out/'CANDIDATE_ID_MAP_105.csv');self.assertEqual(len(rows),105)
            for r in rows:
                if r['ID'] in b.legacy():self.assertEqual(r['Style'],b.legacy()[r['ID']]['Style'])
            for arm,mult in [('A',1),('B',1),('C',1),('D',2),('E',2)]:
                view=b.read(out/f'DRAFT_ARM_{arm}.csv');self.assertEqual(len(view),105*mult)
                self.assertEqual({r['ID'] for r in view},{r['ID'] for r in rows})
            self.assertFalse(json.loads((out/'STATUS.json').read_text())['training_ready'])

    def test_18_regeneration_preserves_edited_intake(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); intake=tmp/'answers.csv';intake.write_text('completed human answers')
            b.dump(tmp/'TEMPLATE_HASHES.json',{'answers.csv':'old-template-hash'})
            with patch.object(b,'HERE',tmp),self.assertRaisesRegex(AssertionError,'Edited intake'):
                b.main()
            self.assertEqual(intake.read_text(),'completed human answers')

if __name__=='__main__':unittest.main(verbosity=2)

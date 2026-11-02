import unittest
from patch_contract import apply_patch,apply_patches,locate

class ContractTests(unittest.TestCase):
    def patch(self,op,target,replacement,evidence):
        return dict(operation=op,target_text=target,replacement_text=replacement,evidence_original=evidence,reason='Restore source',violation_type='other')
    def check(self,source,target,replacement,expected,op='replace_exact',original=None):
        result,event=apply_patch(source,self.patch(op,target,replacement,original or replacement or target),original or replacement or target)
        self.assertEqual(result,expected)
        self.assertEqual(result,source[:event['start']]+event['after']+source[event['end']:])
    def test_number(self): self.check('Wait ten weeks. End.','ten','10','Wait 10 weeks. End.')
    def test_quote(self): self.check('He said "distinct". End.','distinct','different','He said "different". End.')
    def test_certainty(self): self.check('It is certain. End.','is certain','may happen','It may happen. End.')
    def test_attribution(self): self.check('The tax will rise. End.','will rise','may rise, he claims','The tax may rise, he claims. End.')
    def test_roles(self): self.check('Men you face in battle. End.','face in battle','want to fight your wars','Men you want to fight your wars. End.')
    def test_event(self): self.check('There were protests. End.','protests','riots','There were riots. End.')
    def test_insert_after(self): self.check('He spoke. End.','He',' allegedly','He allegedly spoke. End.','insert_after_exact', 'allegedly')
    def test_insert_before(self): self.check('He spoke. End.','spoke','never ','He never spoke. End.','insert_before_exact','never')
    def test_delete(self): self.check('He secretly spoke. End.','secretly ','','He spoke. End.','delete_exact','He spoke.')
    def test_multiple(self):
        with self.assertRaisesRegex(ValueError,'multiple'): apply_patch('a a',self.patch('replace_exact','a','b','b'),'b')
    def test_missing(self):
        with self.assertRaisesRegex(ValueError,'missing target'): apply_patch('a b',self.patch('replace_exact','c','d','d'),'d')
    def test_lookup(self): self.assertEqual(locate('He said “Yes”— now.','"yes"-  now'),'“Yes”— now')
    def test_lookup_ambiguous(self):
        with self.assertRaisesRegex(ValueError,'multiple'): locate('YES yes','yes')
    def test_whitespace(self): self.assertEqual(locate('one\n  two end','one two'),'one\n  two')
    def test_broad(self):
        with self.assertRaisesRegex(ValueError,'over-broad'): apply_patch('whole paragraph',self.patch('replace_exact','whole paragraph','new','new'),'new')
    def test_current_text(self):
        out,events=apply_patches('a b end',[self.patch('replace_exact','a','c','c'),self.patch('replace_exact','a','d','d')],'c d')
        self.assertEqual(out,'c b end');self.assertFalse(events[1]['applied'])
    def test_evidence(self):
        with self.assertRaisesRegex(ValueError,'evidence'): apply_patch('a b',self.patch('replace_exact','a','c','invented'),'source')
    def test_noop(self):
        with self.assertRaisesRegex(ValueError,'no-op'): apply_patch('a b',self.patch('replace_exact','a','a','a'),'a')

if __name__=='__main__': unittest.main(verbosity=2)

"""Patch integrity tests; no model calls or evaluation data."""
import unittest
from run import apply_edits


class PatchContract(unittest.TestCase):
    def test_preserves_unedited_text_and_uses_original_offsets(self):
        text='First red claim. Second blue claim. End.'
        result,applied,errors=apply_edits(text,[dict(old='red',new='very dark red',issue_index=0),dict(old='blue',new='green',issue_index=1)],[{},{}])
        self.assertEqual(result,'First very dark red claim. Second green claim. End.')
        self.assertEqual(len(applied),2);self.assertEqual(errors,[])

    def test_ambiguous_span_rejects_whole_patch_set(self):
        text='same same end'
        result,applied,errors=apply_edits(text,[dict(old='end',new='finish',issue_index=0),dict(old='same',new='other',issue_index=0)],[{}])
        self.assertEqual(result,text);self.assertFalse(applied);self.assertTrue(errors)

    def test_overlap_whole_text_and_invalid_issue_index_are_rejected(self):
        text='abc def ghi'
        for edits in [
            [dict(old=text,new='replacement',issue_index=0)],
            [dict(old='abc def',new='x',issue_index=0),dict(old='def ghi',new='y',issue_index=0)],
            [dict(old='abc',new='x',issue_index=3)]]:
            result,applied,errors=apply_edits(text,edits,[{}])
            self.assertEqual(result,text);self.assertFalse(applied);self.assertTrue(errors)

    def test_deletion_and_missing_information_anchor(self):
        result,_,errors=apply_edits('A invented fact. End.',[dict(old='invented ',new='',issue_index=0),dict(old='End.',new='End, with detail.',issue_index=1)],[{},{}])
        self.assertEqual(result,'A fact. End, with detail.');self.assertFalse(errors)


if __name__=='__main__':unittest.main()

"""Inventory research language; textual matches are not semantic verification.

Read-only over all tracked Markdown. Never edits frozen protocols or history.
"""
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CURRENT = ['README.md', 'THESIS_RESEARCH_DIRECTION_HE.md', 'EVIDENCE_MATRIX_HE.md',
           'RESEARCH_GAP_AND_NOVELTY_HE.md', 'RESEARCH_GAP_AND_CONTRIBUTION_HE.md',
           'RELATED_WORK_DEEP_REVIEW_HE.md', 'RELATED_WORK_COMPARISON.md', 'STYLE_SENSITIVITY_PILOT_HE.md']
MARKER = 'WORKING_TASK_AND_TRAINING_HANDOFF_HE.md'


def main():
    names = subprocess.check_output(['git', 'ls-files', '-z', '*.md'], cwd=ROOT).decode('utf-8').split('\0')
    records = []
    for name in filter(None, names):
        text = (ROOT / name).read_text(encoding='utf-8-sig')
        if not re.search(r'shortcut|author.id|סגנון|הכללה', text, re.I):
            continue
        records.append(dict(path=name, current_direction_document=name in CURRENT,
                            contains_author_id=bool(re.search(r'author.id|זיהוי כותב', text, re.I)),
                            contains_shortcut_term=bool(re.search(r'shortcut|קיצור דרך', text, re.I)),
                            contains_generalization=bool(re.search(r'generaliz|הכללה', text, re.I)),
                            explicit_current_scope_link=MARKER in text,
                            interpretation='Inventory only; lexical co-occurrence does not verify scientific claims'))
    for name in CURRENT:
        assert MARKER in (ROOT/name).read_text(encoding='utf-8-sig'), name
    result = dict(current_scope_documents=CURRENT, relevant_tracked_markdown=len(records),
                  records=records, historical_results_edited=False,
                  limitation='Current direction documents reviewed for claim scope; archived prose remains historical, not individually re-adjudicated')
    (HERE/'DOCUMENT_SCOPE_INVENTORY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Current scope links verified:', len(CURRENT), '; relevant tracked Markdown inventoried:', len(records))


if __name__ == '__main__':
    main()

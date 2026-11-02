"""Publish concise navigation/status summaries from the frozen repair report."""
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
STUDY=OUT.parent
ROOT=STUDY.parents[2]
MARKER='## Two-stage v2 semantic repair — 2026-11-02'


def main():
    s=json.loads((OUT/'summary.json').read_text(encoding='utf8'))
    t=s['totals'];r=t['repair']
    explanation='v3 attempted to encode more semantic-preservation constraints in a single rewrite prompt, but external review showed overall degradation relative to v2. Therefore the next experiment separates style rewriting from semantic verification and minimal repair.'
    short=f'''{MARKER}

**Train-only intervention development** על אותם 30 מקורות, עם v2 הקיים כקלט — ללא יצירת rewrite ראשוני חדש. {explanation}

אותו מודל מקומי מבצע checklist על Original/v2, ואז תיקון מותנה באמצעות patches ממוקדים בלבד. רשימת ההפרות נשלחת לשלב התיקון; דירוגי review קודמים, IDs ותוצאות guards אינם נשלחים למודל. אימות זה הוא חלק מההתערבות ולא External LLM Review או Human Validation. ה־guards והספים נשארו קפואים.

| Metric | v2 | v3 | v2 + Repair |
|---|---:|---:|---:|
| Automated preservation pass | {t['v2']['automated_preservation_pass']} | {t['v3']['automated_preservation_pass']} | {r['automated_preservation_pass']} |
| Substantial style proxy | {t['v2']['substantial_style_change']} | {t['v3']['substantial_style_change']} | {r['substantial_style_change']} |
| Both | {t['v2']['both']} | {t['v3']['both']} | {r['both']} |
| Exact copies | {t['v2']['exact_copies']} | {t['v3']['exact_copies']} | {r['exact_copies']} |

שונו בפועל {s['changed_count']}/30 טקסטים, באמצעות {s['effective_edit_count']} עריכות משנות־טקסט; {len(s['verification_invalid_ids'])} אימותים ו־{len(s['repair_invalid_ids'])} הצעות repair נכשלו בחוזה התהליך. בכשל נשמר v2, ללא retry או בחירה לפי ציונים. המימוש לא סיפק מספיק תיקונים תקינים לביסוס שיפור סמנטי; אין בכך הפרכה של הרעיון הדו־שלבי. שינוי במעברי guards יכול לשקף גם תיקון לקסיקלי טכני; אין עדיין דירוגי משמעות/סגנון חיצוניים ל־Repaired v2. לא נמדדו תוצאות test או generalization, לא אומנו מודלים, ולא מולאו שדות אנושיים. עוצרים לפני External LLM Review עיוור חדש.
'''
    targets=[ROOT/'CURRENT_STATE.md',ROOT/'EXPERIMENTS.md',STUDY/'EXPERIMENT_GUIDE_HE.md',STUDY/'FINAL_REPORT_HE.md']
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in targets+[ROOT/'artifacts/README.md']}
    relroot='artifacts/experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/'
    for p in targets:
        text=p.read_text(encoding='utf8').split(MARKER,1)[0].rstrip()
        prefix='v2_semantic_repair_30_20261102/' if p.parent==STUDY else relroot
        content=short
        if p.name=='CURRENT_STATE.md':
            text=text.replace('the user-supplied blind-package external review has now been imported and paired with v2 by ID. Stop before further changes.', 'the v3 external review/comparison is complete; a new two-stage verification/minimal-repair run on fixed v2 has now completed (see below).')
            start=text.index('## Next decision')
            end=text.find('\n## ',start+3)
            if end<0:end=len(text)
            text=text[:start]+'''## Next decision

Obtain a separately performed External LLM Review of **Repaired v2**, using the blind package linked below. The current local pipeline changed only one text and retained v2 for 29 process failures, so its automatic scores do not establish semantic improvement. No further prompt/guard changes, training, test evaluation or LoRA/DoRA now. Human Validation remains Pending and required by the study's training gate.
'''+text[end:]
            content=f'''{MARKER}

Active follow-up: **train-only intervention development**, fixed v2 → local verification → conditional patch repair → unchanged guards. No new first-stage rewriting. {explanation}

Automatic results for repair: pass {r['automated_preservation_pass']}/30, substantial style {r['substantial_style_change']}/30, both {r['both']}/30, exact copies {r['exact_copies']}. Actual changes: {s['changed_count']}/30; verification/patch failures retain v2 and are reported, not hidden by retries. Local verification is part of the pipeline, not independent external approval. No new external/human review, training or test evaluation. Next step: separately review the Repaired v2 blind package; no further tuning now.
'''
        p.write_text(text+'\n\n'+content+f'\n[Repair report]({prefix}REPORT_HE.md) · [Blind package]({prefix}REVIEW_PACKAGE_BLIND_30.md) · [Reproduce]({prefix}REPRODUCTION.md)\n',encoding='utf8')
    p=ROOT/'artifacts/README.md';text=p.read_text(encoding='utf8')
    entry='| v2 semantic verification + minimal repair | Current; run completed, external review Pending | Train-only two-stage intervention on fixed v2; process failures preserved | [Report](experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REPORT_HE.md) | [Outputs](experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/) | [Reproduce](experiments/style_intervention_v2_20261026/v2_semantic_repair_30_20261102/REPRODUCTION.md) |'
    if entry not in text:
        lines=text.splitlines()
        idx=next(i for i,line in enumerate(lines) if line.startswith('| External LLM Review — New Normalized |'))
        lines[idx+1:idx+1]=[
            '| Prompt v3 + external comparison | Closed; motivates repair follow-up | More constraints in one prompt did not establish improvement | [Paired review](experiments/style_intervention_v2_20261026/train_prompt_revision_v3_30_20261102/external_llm_review_20261102/V2_V3_EXTERNAL_REVIEW_COMPARISON_HE.md) | [v3 outputs](experiments/style_intervention_v2_20261026/train_prompt_revision_v3_30_20261102/) | [Reproduce](experiments/style_intervention_v2_20261026/train_prompt_revision_v3_30_20261102/README.md) |',entry]
        text='\n'.join(lines)+'\n'
        p.write_text(text,encoding='utf8')
    (OUT/'documentation_update_audit.json').write_text(json.dumps(dict(authorized_doc_paths=list(before),
        note='Only documentation updated; experimental-input integrity audited separately',
        initial_or_previous_doc_sha256=before,
        current_doc_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in targets+[ROOT/'artifacts/README.md']}),ensure_ascii=False,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':main()

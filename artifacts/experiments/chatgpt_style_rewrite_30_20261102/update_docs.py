"""Idempotently append the automatic checkpoint; do not alter prior evidence."""
import re
from run import ROOT,STUDY,OUT,read,table

def append(path,marker,text):
    old=path.read_bytes().decode('utf8')
    end='\n<!-- END_CHATGPT_REWRITE_30 -->\n'
    block=marker+text.rstrip()+end
    actual_marker=marker if marker in old else marker.replace('\n','\r\n')
    if actual_marker in old:
        start=old.index(actual_marker)
        actual_end=end if end in old[start:] else end.replace('\n','\r\n')
        finish=old.index(actual_end,start)+len(actual_end)
        updated=old[:start]+block+old[finish:]
    else:updated=old+block
    path.write_bytes(updated.encode('utf8'))

def main():
    s=read('summary.json');t=s['totals']
    matrix=table(['Metric','v2','v3','ChatGPT Rewrite'],[[name]+[str(t[v][key])+'/30' for v in ('v2','v3','ChatGPT')] for name,key in [('automated preservation pass','preservation_pass'),('substantial style change','substantial_style'),('both preservation + style','both'),('exact copies','exact_copies')]])
    p=ROOT/'CURRENT_STATE.md';text=p.read_text(encoding='utf8')
    next_step='Prepare a separately performed External LLM Review of the imported **ChatGPT Style Rewrite** outputs using the [new blind package](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REVIEW_PACKAGE_BLIND_30.md). Automatic screening is complete; these outputs are not independently reviewed or human validated. Stop before review, retraining, test evaluation, new LoRA or any guard/threshold changes. Existing-tool feasibility and repair development remain separate historical checkpoints.'
    text,n=re.subn(r'(## Next decision\n\n).*?(?=\n## )',lambda m:m.group(1)+next_step+'\n',text,count=1,flags=re.S);assert n==1
    text,n=re.subn(r'(## Current active experiment\n\n).*?(?=\n\n)',lambda m:m.group(1)+'A separate **ChatGPT-generated Style Rewrite experiment** on the same 30 frozen TRAIN originals has completed import and unchanged automatic screening. Generation was performed outside this repo, according to the user from Original only; model version/prompt/request history were not supplied. Independent review is Pending. No process is running. Prior v2/v3/repair outputs remain intact.',text,count=1,flags=re.S);assert n==1
    lines=text.splitlines();start=next(i for i,line in enumerate(lines) if line.startswith('| Measure on the same 30 examples |'))
    if 'ChatGPT' not in lines[start]:
        additions=[' ChatGPT Rewrite |','---:|']+[str(t['ChatGPT'][k])+' |' for k in ('preservation_pass','substantial_style','both','exact_copies')]
        for offset,addition in enumerate(additions):
            assert lines[start+offset].startswith('|')
            lines[start+offset]+=' '+addition
        text='\n'.join(lines)+'\n'
    p.write_text(text,encoding='utf8')
    marker='\n\n## ChatGPT Style Rewrite — 2026-11-02\n\n'
    summary='ניסוי נפרד של generator חלופי, לבדיקת style change + semantic preservation על אותם 30 מקורות train בלבד. ה־CSV המקורי נשמר byte-for-byte; כל ID חובר למקורו והשכתובים לא נערכו. לפי דיווח המשתמש נכתבו מ־Original בלבד, ללא גרסאות/מדדים/ביקורות קודמות; פרטי generation מלאים אינם זמינים לאימות עצמאי.\n\n'+matrix+'\n\nAutomated pass הוא signal בלבד; substantial style הוא proxy. אין עדיין External LLM Review עצמאי לתוצרים אלה או Human Validation, ואין להסיק הצלחת פתרון או generalization. לא שונו guards, ספים, חלוקה, תוויות, scaling או שדות אנושיים קיימים; לא בוצעו training, test evaluation או LoRA. עוצרים לפני ביקורת חיצונית חדשה.\n\n'
    append(p,marker,summary+'[Report](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPORT_HE.md) · [Blind review input](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REVIEW_PACKAGE_BLIND_30.md) · [Reproduce](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPRODUCTION.md)')
    append(ROOT/'EXPERIMENTS.md',marker,summary+'[Report and per-ID diagnostics](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPORT_HE.md) · [Blind package](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REVIEW_PACKAGE_BLIND_30.md) · [Reproduce](artifacts/experiments/chatgpt_style_rewrite_30_20261102/REPRODUCTION.md)')
    for name in ('EXPERIMENT_GUIDE_HE.md','FINAL_REPORT_HE.md'):
        append(STUDY/name,marker,summary+'[Separate experiment report](../chatgpt_style_rewrite_30_20261102/REPORT_HE.md) · [Paired comparison](../chatgpt_style_rewrite_30_20261102/COMPARISON_30.md) · [Blind package](../chatgpt_style_rewrite_30_20261102/REVIEW_PACKAGE_BLIND_30.md) · [Reproduce](../chatgpt_style_rewrite_30_20261102/REPRODUCTION.md)')
    p=ROOT/'artifacts/README.md';text=p.read_text(encoding='utf8')
    row='| ChatGPT Style Rewrite, 30 TRAIN texts | Automatic screening complete; independent review Pending | Alternative generator, imported unchanged; preservation/style signals only | [Report](experiments/chatgpt_style_rewrite_30_20261102/REPORT_HE.md) | [Comparison](experiments/chatgpt_style_rewrite_30_20261102/COMPARISON_30.md) / [Blind package](experiments/chatgpt_style_rewrite_30_20261102/REVIEW_PACKAGE_BLIND_30.md) | [Reproduce](experiments/chatgpt_style_rewrite_30_20261102/REPRODUCTION.md) |'
    if row not in text:
        anchor='\n\n**External LLM Review ≠ Human Validation.**';assert anchor in text;text=text.replace(anchor,'\n'+row+anchor,1);p.write_text(text,encoding='utf8')

if __name__=='__main__':main()

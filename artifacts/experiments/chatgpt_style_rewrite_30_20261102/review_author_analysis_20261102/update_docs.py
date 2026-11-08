from analyze import OUT,RUN,ROOT,STUDY,COUNTS,table
import json,re

def block(path,body):
    marker='\n\n## ChatGPT external review and author signals — 2026-11-02\n\n'
    end='\n<!-- END_CHATGPT_REVIEW_AUTHOR_20261102 -->\n'
    old=path.read_bytes().decode('utf8');new=marker+body.rstrip()+end
    actual=marker if marker in old else marker.replace('\n','\r\n')
    if actual in old:
        start=old.index(actual);stop_marker=end if end in old[start:] else end.replace('\n','\r\n');stop=old.index(stop_marker,start)+len(stop_marker);text=old[:start]+new+old[stop:]
    else:text=old+new
    path.write_bytes(text.encode('utf8'))

def main():
    result=json.loads((OUT/'author_id_summary.json').read_text(encoding='utf8'))
    comparisons=[]
    import csv
    with (OUT/'review_comparison_summary.csv').open(encoding='utf-8-sig',newline='') as f:comparisons=list(csv.DictReader(f))
    matrix=table(list(comparisons[0]),[list(r.values()) for r in comparisons])
    author=table(['Author-ID setting','Accuracy','Macro-F1'],[[v,f"{100*result[v]['accuracy_mean']:.2f}%",f"{result[v]['macro_f1_mean']:.4f}"] for v in ['Original','Rewrite','Original_fit_Rewrite_dev']])
    summary='נשמרו ספירות External LLM Review שסיפק המשתמש: Meaning 24 Yes / 6 Borderline / 0 No; Style 24 Yes / 6 Borderline / 0 No; Semantic drift 3 Yes / 11 Borderline / 16 No. **16 clean according to External LLM Review**, לפי drift=No בלבד — לא Human Validation ולא כלל קבלה משולב. אין הכרעות לפי ID, ולכן אין שיוך 16 אלה לרשומות או חישוב חפיפות בין שדות. כל הספירות הנוספות והמקור המצרפי נשמרו בדוח הניתוח. לא נערך review חדש כאן.\n\n'+matrix+'\n\n'
    summary+='חבילת Human Validation נוצרה לכל 30 הזוגות עם חמשת השדות הריקים, ללא scores, guards, מחבר, גרסאות קודמות או review. טרם הוחזרה בדיקה אנושית: **Human Validation Pending**. לא נבחר subset של 16. כלל קבלה עתידי אפשרי: human meaning=Yes וגם stance=Yes וגם style=Yes, המוחל על כל ה־30; לא הוחל כעת.\n\n'+author+'\n\n'
    summary+='Author-ID השתמש בכל 30 זוגות ה־train, בתשעה כותבים וב־66 מאפייני style קיימים. Logistic Regression זהה מבחינת pipeline/פרמטרים, עם fit נפרד לכל representation, שתי חלוקות stratified לכל אחד מחמישה seeds ו־scaling בתוך fold בלבד. במסלול המשני אותו fitted Original classifier נבחן על paired Rewrite. זהו development closed-set, לא test או unseen-author evaluation. הירידה הממוצעת קטנה: accuracy −1.33pp ו־Macro-F1 −0.0097; accuracy יורד רק ב־2/5 seeds, ובמסווג המקור הקבוע עולה ל־28%. **אין כרגע ראיה יציבה שה־author signal ירד.** אין להציג את הממוצע הקטן כהסרת סגנון כותב מוכחת או כהשפעה על narrative generalization.\n\n'
    summary+='החידוש אינו בהכרח Text Style Transfer חדש. השאלה המחקרית היא האם Narrative Classifier משתמש ב־author style כ־shortcut, והאם הפחתת author-specific style תוך שמירת narrative משפרת generalization ל־unseen authors. ChatGPT rewrite הוא intervention candidate, לא contribution בפני עצמו. לא שונו prompt/guards/thresholds/split, לא אומן Narrative Classifier ולא בוצעו LoRA או test evaluation. אומנו רק probes זמניים של Author-ID, ללא שמירת weights.\n\n'
    rootlinks='[Analysis report](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPORT_HE.md) · [Human package](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md) · [Reproduce](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPRODUCTION.md)'
    p=ROOT/'CURRENT_STATE.md';text=p.read_text(encoding='utf8')
    next_step='Obtain actual human judgments for **all 30 pairs** using the [blank Human Validation package](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md). External LLM Review aggregate counts are imported (24 meaning Yes; 16 clean according to External LLM Review); per-ID ratings were not supplied. Human Validation remains Pending. The paired Author-ID diagnostic shows only a small, seed-unstable matched decrease, and an increase with a fixed Original classifier; author-signal reduction is not established. Do not select the 16, tune prompts/guards, train the Narrative Classifier, run LoRA or evaluate the frozen test.'
    text,n=re.subn(r'(## Next decision\n\n).*?(?=\n## )',lambda m:m.group(1)+next_step+'\n',text,count=1,flags=re.S);assert n==1
    text=text.replace('Independent review is Pending. No process is running.','External LLM Review aggregate counts are now imported; per-ID ratings are unavailable. Human Validation remains Pending. No process is running.',1)
    p.write_text(text,encoding='utf8');block(p,summary+rootlinks)
    block(ROOT/'EXPERIMENTS.md',summary+rootlinks)
    block(STUDY/'FINAL_REPORT_HE.md',summary+'[Analysis report](../chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPORT_HE.md) · [Human package](../chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md) · [Reproduce](../chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/REPRODUCTION.md)')
    p=RUN/'REPORT_HE.md';old=p.read_bytes().decode('utf8')
    notice='\n\nעדכון סטטוס: External LLM Review שסוכם על ידי המשתמש יובא כספירות מצרפיות בלבד. Human Validation עדיין Pending; Author-ID לא מספק ראיה יציבה לירידת author signal. [הדוח העדכני וחבילת האימות האנושי](review_author_analysis_20261102/REPORT_HE.md). הסעיפים האוטומטיים להלן מתעדים את השלב שלפני ייבוא ה־review; סטטוס Pending של review בהם הוא היסטורי.\n'
    if 'עדכון סטטוס: External LLM Review שסוכם' not in old:
        first=old.index('\n');old=old[:first]+notice+old[first:];p.write_bytes(old.encode('utf8'))
    block(p,summary+'[Detailed analysis](review_author_analysis_20261102/REPORT_HE.md) · [Human package](review_author_analysis_20261102/HUMAN_VALIDATION_30.md) · [Reproduce](review_author_analysis_20261102/REPRODUCTION.md)')
if __name__=='__main__':main()

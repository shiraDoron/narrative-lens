"""Render a standalone, offline human-review form from human_review.csv.

Input: CSV containing originals, proposed labels and paired rewrites.
Output: HUMAN_REVIEW.html. The form never calls an LLM or fills judgments itself.
Human edits stay in browser localStorage until exported to CSV; the exported file
must replace human_review.csv before gated evaluation. No external dependencies.
"""
import json
from study import OUT, rows, event


def main():
    """Embed frozen review rows safely and create the local manual annotation UI."""
    data=rows(OUT/'human_review.csv')
    encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template=r'''<!doctype html><html lang="he" dir="rtl"><meta charset="utf-8">
<title>אימות אנושי — Author Style V2</title>
<style>
body{font:16px Arial,sans-serif;background:#f4f6fa;color:#172234;margin:24px;line-height:1.5}
main{max-width:1400px;margin:auto}h1{font-size:25px}button,select,input{font:inherit;padding:7px;border:1px solid #9aa8bb;border-radius:5px;background:white}button{cursor:pointer;background:#e6efff}.toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;padding:15px;background:white;border-radius:9px;margin:14px 0}.card{background:white;border:1px solid #dae0ea;border-radius:8px;padding:18px;margin:12px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.english{direction:ltr;text-align:left;white-space:pre-wrap;font-size:18px;line-height:1.65}.field{display:flex;justify-content:space-between;align-items:center;gap:12px;border-bottom:1px solid #eee;padding:6px 0}.original{border-right:5px solid #5384c7}.muted{color:#52627b}#status{font-weight:bold}textarea{width:96%;height:65px;font:inherit}.warn{background:#fff3d5;padding:12px;border-radius:6px}@media(max-width:850px){.grid{grid-template-columns:1fr}body{margin:10px}}
</style><main><h1>אימות אנושי: מקור, פרפרזה ונרמול</h1>
<p>קראו את המקור ואת שתי הגרסאות. סמנו שימור משמעות בכל סעיף, והכריעו בתווית. השדות נשארו ריקים במכוון.</p>
<p class="warn">הטופס אינו מאמת דבר באופן אוטומטי. הצעת התווית גלויה ולכן זהו אימות בסיוע AI, לא תיוג עיוור. confidence הוא ציון 1–3, לא הסתברות. <b>נוספה/הושמטה טענה: “כן” פירושו כשל.</b></p>
<div class="toolbar"><label>מזהה סוקר/ת: <input id="reviewer" placeholder="שם או מזהה אמיתי"></label><button id="export">הורדת CSV מסומן</button><label>טעינת CSV קודם: <input id="import" type="file" accept=".csv"></label></div>
<p class="muted">הסימונים נשמרים בדפדפן זה בלבד. בסיום הורידו CSV והחליפו בו את human_review.csv בתיקיית הניסוי. מומלץ להוריד גיבוי לאורך העבודה. אל תשלחו את הטקסטים לשירות חיצוני.</p>
<div class="toolbar"><button id="previous">הקודם</button><select id="jump"></select><button id="next">הבא</button><button id="incomplete">הבא שטרם הושלם</button><span id="status"></span></div>
<section class="card original"><h2 id="record"></h2><p id="proposal"></p><p id="evidence" class="english muted"></p><h3>Original</h3><div id="original" class="english"></div>
<div class="toolbar"><label>תווית אנושית: <select id="label"><option value="">טרם נבדק</option>Left-wing</option><option>Right-wing</option><option>Unclear</option></select></label><label>confidence אנושי (רשות): <input id="confidence" type="number" min="1" max="3"></label></div></section>
<div class="grid"><section class="card"><h2>Paraphrase</h2><div id="paraphrase" class="english"></div><p id="screenP" class="muted"></p><div id="fieldsP"></div></section><section class="card"><h2>Normalized V2</h2><div id="normalized" class="english"></div><p id="screenN" class="muted"></p><div id="fieldsN"></div></section></div>
<section class="card"><label>הערות:<br><textarea id="notes"></textarea></label><p id="saved" class="muted"></p></section></main>
<script id="research-data" type="application/json">__DATA__</script><script>
'use strict';
const base=JSON.parse(document.getElementById('research-data').textContent);
let records=JSON.parse(JSON.stringify(base)),index=0;
const storageKey='author-style-v2-human-review-20261026';
const fields=[['narrative_preserved','האם נשמר הנרטיב?'],['stance_preserved','האם נשמרה העמדה?'],['framing_preserved','האם נשמר המסגור?'],['facts_preserved','האם נשמרו העובדות?'],['entities_preserved','האם נשמרו הישויות?'],['negation_preserved','האם נשמרה השלילה והיקפה?'],['certainty_preserved','האם נשמרה מידת הוודאות?'],['attribution_preserved','האם נשמר הייחוס?'],['claim_added','האם נוספה טענה?'],['claim_omitted','האם הושמטה טענה?']];
const judgmentKeys=['human_narrative','human_label_confidence','reviewer','reviewed_at','notes',...['Paraphrase','Normalized'].flatMap(c=>fields.map(f=>c+'_'+f[0]))];
const byId=id=>document.getElementById(id);
function merge(saved){const map=new Map(saved.map(r=>[r.row_id,r]));for(const r of records){const s=map.get(r.row_id);if(!s)continue;if(s.original!==r.original||s.Paraphrase!==r.Paraphrase||s.Normalized!==r.Normalized)throw Error('טקסט שונה באותה רשומה; אין לערבב גרסאות ניסוי.');for(const k of judgmentKeys)r[k]=s[k]||'';}}
try{const saved=localStorage.getItem(storageKey);if(saved)merge(JSON.parse(saved));}catch(e){alert('לא נטענו סימונים קודמים: '+e.message);}
for(const [condition,suffix] of [['Paraphrase','P'],['Normalized','N']])for(const [key,title] of fields){const label=document.createElement('label');label.className='field';const span=document.createElement('span');span.textContent=title;const select=document.createElement('select');select.id=condition+'_'+key;for(const [value,text] of [['','טרם נבדק'],['yes','כן'],['no','לא'],['unclear','לא ברור']]){const option=document.createElement('option');option.value=value;option.textContent=text;select.append(option);}select.onchange=()=>edit(condition+'_'+key,select.value);label.append(span,select);byId('fields'+suffix).append(label);}
for(let i=0;i<records.length;i++){const option=document.createElement('option');option.value=i;option.textContent=(i+1)+' — '+records[i].row_id;byId('jump').append(option);}
function complete(r){return r.reviewer.trim()&&r.reviewed_at&&['Left-wing','Right-wing','Unclear'].includes(r.human_narrative)&&['Paraphrase','Normalized'].every(c=>fields.every(([key])=>['yes','no','unclear'].includes(r[c+'_'+key])));}
function persist(){try{localStorage.setItem(storageKey,JSON.stringify(records));byId('saved').textContent='נשמר בדפדפן. יש להוריד CSV כדי להעביר את הסימונים לניסוי.';}catch(e){byId('saved').textContent='לא ניתן לשמור בדפדפן. הורידו CSV עכשיו.';}byId('status').textContent=records.filter(complete).length+' / '+records.length+' רשומות הושלמו';}
function edit(key,value){const r=records[index];r[key]=value;r.reviewer=byId('reviewer').value.trim();r.reviewed_at=new Date().toISOString();persist();}
function show(){const r=records[index];byId('jump').value=index;byId('record').textContent=(index+1)+' / '+records.length+' — '+r.row_id;byId('proposal').textContent='הצעת Narrative: '+r.proposed_narrative+' | confidence AI: '+r.proposed_confidence_1_to_3+'/3';byId('evidence').textContent=r.label_evidence;byId('original').textContent=r.original;byId('paraphrase').textContent=r.Paraphrase;byId('normalized').textContent=r.Normalized;for(const [c,s] of [['Paraphrase','P'],['Normalized','N']]){byId('screen'+s).textContent='סינון אוטומטי: '+r[c+'_automatic_pass']+'; סיבות: '+(r[c+'_automatic_reasons']||'אין')+' — אינו אימות אנושי';for(const [key] of fields)byId(c+'_'+key).value=r[c+'_'+key]||'';}byId('label').value=r.human_narrative;byId('confidence').value=r.human_label_confidence;byId('notes').value=r.notes;if(r.reviewer)byId('reviewer').value=r.reviewer;persist();}
byId('previous').onclick=()=>{index=Math.max(0,index-1);show();};byId('next').onclick=()=>{index=Math.min(records.length-1,index+1);show();};byId('jump').onchange=e=>{index=Number(e.target.value);show();};byId('incomplete').onclick=()=>{for(let offset=1;offset<=records.length;offset++){const next=(index+offset)%records.length;if(!complete(records[next])){index=next;show();return;}}alert('כל הרשומות סומנו. יש להוריד CSV.');};
byId('label').onchange=e=>edit('human_narrative',e.target.value);byId('confidence').onchange=e=>edit('human_label_confidence',e.target.value);byId('notes').onchange=e=>edit('notes',e.target.value);byId('reviewer').onchange=()=>{const r=records[index];if(r.reviewed_at){r.reviewer=byId('reviewer').value.trim();persist();}};
function csvEscape(value){return '"'+String(value??'').replace(/"/g,'""')+'"';}
byId('export').onclick=()=>{const keys=Object.keys(base[0]);const csv='\uFEFF'+[keys,...records.map(r=>keys.map(k=>r[k]))].map(r=>r.map(csvEscape).join(',')).join('\r\n');const link=document.createElement('a');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));link.href=url;link.download='human_review.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
function parseCSV(text){text=text.replace(/^\uFEFF/,'');const out=[];let row=[],field='',quoted=false;for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}else if(c===','&&!quoted){row.push(field);field='';}else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(field);out.push(row);row=[];field='';}else field+=c;}if(quoted)throw Error('CSV לא תקין: ציטוט לא נסגר');if(field||row.length){row.push(field);out.push(row);}const header=out.shift();return out.filter(r=>r.some(Boolean)).map(r=>Object.fromEntries(header.map((k,i)=>[k,r[i]||''])));}
byId('import').onchange=async e=>{try{const text=await e.target.files[0].text();merge(parseCSV(text));show();alert('הסימונים נטענו.');}catch(error){alert('הטעינה נכשלה: '+error.message);}};
show();
</script></html>'''
    (OUT/'HUMAN_REVIEW.html').write_text(template.replace('__DATA__',encoded),encoding='utf8')
    event('render_review',[OUT/'human_review.csv'],[OUT/'HUMAN_REVIEW.html'],len(data),len(data))


if __name__=='__main__':main()

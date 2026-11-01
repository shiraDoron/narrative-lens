"""Import user-supplied External LLM Evaluation without human-field updates.

Input: Downloads/LLM_EXTERNAL_REVIEW_30_20261101.csv and frozen 30-example pack.
Outputs: byte-identical source copy, namespaced joined results, descriptive counts,
Hebrew summary and hash audit. No LLM calls, adjudication, filtering or training.
"""
from pathlib import Path
import collections, csv, datetime, hashlib, json, shutil

OUT=Path(__file__).resolve().parent
STUDY=OUT.parent
SOURCE=Path.home()/'Downloads/LLM_EXTERNAL_REVIEW_30_20261101.csv'
PACK=STUDY/'external_review_30_20261101/review_30_train_only.csv'
FIELDS=['llm_narrative_label','machine_label_correct','paraphrase_meaning_preserved',
        'normalized_meaning_preserved','paraphrase_style_change_valid','normalized_style_change_valid','llm_notes']


def sha(path):
    """Return exact-byte hash for provenance and non-modification checks."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    """Load CSV strings; never reinterpret free text as instructions."""
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))


def save_csv(name, records):
    """Write derived External LLM Review rows with explicit column names."""
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)


def table(headers, rows):
    """Format a concise Markdown summary of supplied judgments."""
    def cell(value):return str(value).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(cell(v) for v in row)+' |' for row in rows])


def main():
    """Validate IDs/schema, preserve source, summarize verbatim external ratings."""
    protected=[p for p in STUDY.rglob('*') if p.is_file() and p.suffix in ['.csv','.json','.jsonl','.html','.py','.pt','.pth'] and
               OUT not in p.parents and '__pycache__' not in p.parts]
    before={str(p.relative_to(STUDY)):sha(p) for p in protected}
    raw=read(SOURCE);pack=read(PACK);lookup={r['ID']:r for r in pack}
    assert len(raw)==30 and len({r['id'] for r in raw})==30
    assert {r['id'] for r in raw}==set(lookup),'External IDs differ from frozen selected IDs'
    assert all(lookup[r['id']]['split']=='train' for r in raw)
    assert set(raw[0])=={'id',*FIELDS}
    for r in raw:
        assert r['llm_narrative_label'] in ['Left-wing','Right-wing','Unclear']
        assert r['machine_label_correct'] in ['Yes','No','Borderline']
        assert all(r[k] in ['Yes','No','Borderline'] for k in FIELDS[2:-1])
    copied=OUT/SOURCE.name
    if copied.exists():assert sha(copied)==sha(SOURCE),'Refuse to replace different imported source'
    else:shutil.copyfile(SOURCE,copied)
    assert copied.read_bytes()==SOURCE.read_bytes()
    joined=[]
    for r in raw:
        base=lookup[r['id']]
        row=dict(ID=r['id'],Author=base['Author'],split='train',selection_group=base['selection_group'],
            proposed_narrative=base['proposed_narrative'],evaluation_type='External LLM Evaluation / LLM External Review',
            evaluator='ChatGPT (reported by user; exact model/version not supplied)',human_verified=False)
        row.update({'external_'+k:v for k,v in r.items() if k!='id'})
        for c in ['Paraphrase','Normalized']:
            screen=json.loads(base[c+'_automatic_checks_json'])
            row[c+'_automatic_pass']=screen['passed'];row[c+'_automatic_reasons']=screen['rejection_reasons']
            row[c+'_style_proxy_substantial']=json.loads(base[c+'_style_metrics_json'])['substantial_style_change']
        joined.append(row)
    save_csv('external_llm_review_joined.csv',joined)
    counts={field:dict(collections.Counter(r[field] for r in raw)) for field in FIELDS[:-1]}
    combinations={c:dict(collections.Counter(('meaning_'+r[c+'_meaning_preserved']+'__style_'+r[c+'_style_change_valid']) for r in raw)) for c in ['paraphrase','normalized']}
    cross=[]
    for c,lower in [('Paraphrase','paraphrase'),('Normalized','normalized')]:
        counter=collections.Counter((r[c+'_automatic_pass'],r['external_'+lower+'_meaning_preserved']) for r in joined)
        cross.extend(dict(condition=c,automatic_pass=a,external_llm_meaning_preserved=b,n=n) for (a,b),n in sorted(counter.items()))
    save_csv('automatic_vs_external_llm.csv',cross)
    by_group=[]
    for group in sorted({r['selection_group'] for r in joined}):
        subset=[r for r in joined if r['selection_group']==group]
        by_group.append(dict(group=group,n=len(subset),normalized_meaning_yes=sum(r['external_normalized_meaning_preserved']=='Yes' for r in subset),
            normalized_style_yes=sum(r['external_normalized_style_change_valid']=='Yes' for r in subset),
            normalized_style_borderline=sum(r['external_normalized_style_change_valid']=='Borderline' for r in subset)))
    save_csv('external_llm_by_selection_group.csv',by_group)
    summary=dict(n=30,scope='Purposively stratified TRAIN-only diagnostic sample; not representative rates or human gold',
        evaluation_type='External LLM Evaluation / LLM External Review',counts=counts,meaning_style_combinations=combinations,
        automatic_comparison=cross,by_selection_group=by_group,
        evaluator_model_version='not supplied',evaluation_prompt='not supplied',evaluation_time='not supplied',
        blinding='Not blinded: pack exposed author, proposed narrative, automatic decisions and style metrics',
        human_review_completed_by_this_import=False,no_training=True,no_threshold_or_label_changes=True)
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# External LLM Evaluation / LLM External Review — סיכום 30 דוגמאות','',
        '**מקור:** קובץ CSV שהמשתמשת העבירה מבדיקת ChatGPT נפרדת. התוצאות שלהלן הן דיווחי אותו LLM; לא בוצעה כאן הכרעה חדשה בתוכן.',
        '**סטטוס:** הערכת LLM חיצונית בלבד. אין אימות אנושי חדש; human_verified נשאר False. אין שינוי בתוויות, בספים, בחלוקה, ב־test או בקוד האימון. לא בוצע אימון מחדש.','',
        '## הספירות כפי שהתקבלו','',table(['שדה בהערכה','Yes / אושר','No / נכשל','Borderline','Unclear'],[
            ['נכונות הצעת הנרטיב',counts['machine_label_correct'].get('Yes',0),counts['machine_label_correct'].get('No',0),counts['machine_label_correct'].get('Borderline',0),counts['llm_narrative_label'].get('Unclear',0)],
            *[[field,counts[field].get('Yes',0),counts[field].get('No',0),counts[field].get('Borderline',0),'—'] for field in FIELDS[2:-1]]]),'',
        'Unclear מתייחס לתווית שהציע ה־LLM החיצוני, ולא לשינוי שבוצע בתווית הדאטה. כל הספירות מתוך 30 הדוגמאות שנבחרו במכוון.','',
        '## השוואה למסננים האוטומטיים','',table(['תנאי','עבר סינון אוטומטי','שימור משמעות לפי LLM','N'],[[r['condition'],r['automatic_pass'],r['external_llm_meaning_preserved'],r['n']] for r in cross]),'',
        'אי־הסכמה אינה הוכחה שהמסנן טעה: הסינון דורש גם נאמנות מילולית לציטוטים, ישויות והסתייגויות, בעוד שיפוט LLM יכול להתייחס למשמעות כללית. הספים והפסילות המקוריים נשארו ללא שינוי.','',
        '## מקרים שה־LLM תיאר כסינון מחמיר או כפער בהגדרת השימור','']
    # Predefined IDs reference only the explicit supplied notes; no new adjudication.
    by_id={r['id']:r for r in raw}
    for rid in ['creators:421024','creators:423545','creators:418904','creators:120177']:
        lines.extend([f"- **{rid}**: לפי ההערכה החיצונית: {by_id[rid]['llm_notes']}"])
    lines.extend(['','## מקרים שסומנו כפגיעה במשמעות, certainty או attribution',''])
    for r in raw:
        if r['paraphrase_meaning_preserved']!='Yes' or r['normalized_meaning_preserved']!='Yes':
            lines.append(f"- **{r['id']}** — Paraphrase: {r['paraphrase_meaning_preserved']}; Normalized: {r['normalized_meaning_preserved']}. הערת ה־LLM: {r['llm_notes']}")
    lines.extend(['','## שילוב שימור משמעות ושינוי סגנון לפי ה־LLM','',
        table(['תנאי','צירוף דירוגים','N'],[[c,k,n] for c,values in combinations.items() for k,n in sorted(values.items())]),'',
        '## מסקנה ראשונית מהבדיקה החיצונית','',
        'לפי הערכת ה־LLM שהתקבלה, הבעיה אינה רק בסינון: במקרים רבים Normalized שומר משמעות אך כמעט אינו משנה סגנון. במקרים שבהם השינוי הסגנוני גדול יותר יש לעיתים פגיעה בפרטים סמנטיים. זו מסקנה אבחונית מהדירוגים שנמסרו, לא אימות עצמאי או מסקנה על כל הדאטה.',
        'שינוי סגנון שסומן Yes אינו מוכיח הסרת מידע על הכותב או הגעה לסגנון יעד אחיד. הבדיקה אינה מודדת Author Identification, Macro-F1 או generalization, ואינה מצדיקה טענה חדשה להסרת shortcut או מעבר ל־LoRA.','',
        '## מה עדיין חסר','',
        'אימות של סוקר/ת אדם לתוויות ולשימור משמעות/סגנון עדיין ממתין. גרסת מודל ה־ChatGPT, prompt ההערכה ותאריך ההערכה לא סופקו ואין להשלים אותם בניחוש. הדירוג אינו עיוור: החבילה הציגה כותב, הצעת תווית ותוצאות מסננים. לא חושב agreement בין בני אדם, ולא ניתן להניח עצמאות מההצעות הקודמות.','',
        '## כל 30 הדוגמאות — כפי שדורגו חיצונית','',
        table(['ID','נרטיב LLM','הצעת נרטיב אושרה','P משמעות','N משמעות','P סגנון','N סגנון','הערת LLM'],[[r['id']]+[r[k] for k in FIELDS] for r in raw])])
    (OUT/'EXTERNAL_LLM_REVIEW_SUMMARY_HE.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    after={str(p.relative_to(STUDY)):sha(p) for p in protected}
    assert before==after,'Protected inputs changed during import'
    audit=dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_path=str(SOURCE),source_sha256=sha(SOURCE),
        imported_copy_sha256=sha(copied),source_copy_byte_identical=True,n=30,ids_match_frozen_pack=True,
        protected_files=len(before),protected_inputs_unchanged=True,protected_sha256=before,
        external_llm_only=True,human_fields_not_modified=True,training_not_run=True,code_sha256=sha(Path(__file__)))
    (OUT/'import_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(counts,ensure_ascii=False))


if __name__=='__main__':main()

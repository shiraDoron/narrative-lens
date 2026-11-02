"""Import supplied v3 review and compare immutable external ratings by ID.

Reporting only. No models, new judging, filtering, human labels or training.
"""
from pathlib import Path
import collections
import csv
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
V3 = OUT.parent
STUDY = V3.parent
V2 = STUDY / 'train_prompt_revision_30_20261101/external_llm_review_20261101'
NAME = 'V3_BLIND_EXTERNAL_LLM_REVIEW_30_20261102.csv'
COMMON = ['meaning_preserved', 'stance_preserved', 'attribution_preserved', 'certainty_preserved', 'style_change_valid']
# Codes summarize supplied notes only. Missing mention never proves no error/fix.
Q, C, A, F, E, P, R, O, T, L = ('quote_fidelity', 'certainty', 'attribution', 'factual_claims',
    'event_characterization', 'participant_roles', 'rhetorical_intensity', 'omissions_additions', 'temporal_information', 'lexical_or_discourse_nuance')
NOTE_CODING = {
 '0105f26ef9f1':([],[], 'Both reviews approve meaning and style; no reported error change.'),
 '421024':([R],[T,R], 'New review flags Saturday night to next night; both mention evaluative rephrasing.'),
 '422329':([T,A],[A], 'V2 notes duration and blame changes; v3 notes the opposing-party versus governing-party blame change. Missing duration mention alone is not proof of repair.'),
 '417181':([C,A],[F,C], 'Rank and claim structure remain problematic; attribution rating improves No to Borderline while certainty worsens Borderline to No.'),
 '120177':([],[T], 'New timing concern: not yet Thanksgiving becomes barely Thanksgiving.'),
 '212505':([],[], 'Meaning remains Yes; style rating declines Yes to Borderline. V2 numeric-format concern was not external semantic drift.'),
 '421951':([],[P], 'V3 reviewer identifies fight-for-you versus face-in-battle role reversal; v2 reviewer approved its rewrite. Not proof the defect originated only in v3.'),
 '422331':([O,R],[R], 'Reported error focus moves from added tradespeople interpretation to tough women versus tough uniforms; meaning remains Borderline.'),
 '120669':([], [F,A,P], 'Obama/Washington subject error returns according to v3 review; v2 review explicitly reported it fixed.'),
 '216128':([L],[L], 'Bet to strategy remains the reported expectation/planning nuance.'),
 '421279':([L],[L], 'Answer revealed versus explanation made public remains Borderline.'),
 '419062':([],[], 'Both reviews approve meaning, stance and style.'),
 '295188':([F],[R], 'Both meaning ratings are Borderline; reported focus changes from final-sentence equivalence to strengthened emotional intensity. Earlier defect is not thereby proved fixed.'),
 '423315':([E,C],[E,C], 'Riots to protests and going-to-lose to destined-to-lose remain; meaning and certainty/stance ratings deteriorate.'),
 '422146':([R,F],[C], 'Reported focus moves from bullying/Epstein framing to speculative perhaps; certainty and style ratings decline. No proof all earlier issues are gone.'),
 '421853':([O],[O,R], 'Proverb interpretation persists; v3 also flags intensified schemes/seize wording.'),
 '418620':([],[R], 'V3 adds a metaphor-framing concern; v2 had accepted meaning and certainty.'),
 '114783':([Q],[Q], 'Quoted never forget is still not retained as a quotation; meaning remains Borderline.'),
 '224770':([],[], 'Meaning remains Yes; v3 style is rated Borderline rather than Yes.'),
 '8b0d99b23d03':([Q,R],[Q,R,O], 'Quote alteration and two-countries issue remain; v3 additionally reports omission of Saturday/Sunday. Shared scores remain unchanged.'),
 '97c9d6b9ac1b':([C,R],[R,O], 'V3 notes omitted/weakened destruction, axe, fancy and sneakily; certainty rating declines despite a different notes focus.'),
 '423545':([R],[R], 'Meaning improves No to Borderline; weakened hoisting metaphor remains. This is partial improvement, not full preservation.'),
 '298495':([F],[F], 'Strangers to anonymous sources remains; v3 also notes different version of God to different God.'),
 '418904':([Q,R],[Q,T,F,O], 'Quote error persists; v3 reports a new surrender-on-this-day claim and branded. Meaning stays No; stance/certainty worsen.'),
 '2e34435c6ccf':([C],[C], 'Inevitability/expectation strengthening remains; certainty rating worsens Yes to No.'),
 '459e183c1d0d':([],[], 'Both reviews approve meaning, uncertainty, attribution and style; ratings alone show no gain.'),
 '416436':([R],[F,O], 'Reported focus moves from superiority softened to virtues toward cheap/easy replaced by effective. Borderline rating persists; error substitution is not proof of overall improvement.'),
 '116358':([P,R],[P,A,O], 'Relationship shift remains; v3 also reports voluntary departure and lowers attribution to Borderline.'),
 '218236':([L],[C,L], 'Normative reframing persists; v3 additionally flags uncertainty emphasis and rates certainty Borderline.'),
 '418827':([R],[R,F], 'Murder to slash remains; v3 also reports brandish to rewrite changing the action. Meaning worsens Borderline to No.')
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def save(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def table(headers, rows):
    def cell(x):return str(x).replace('|','\\|').replace('\n',' ')
    return '\n'.join('| '+' | '.join(map(cell,r))+' |' for r in [headers,['---']*len(headers),*rows])


def main():
    protected={p:sha(p) for p in STUDY.rglob('*') if p.is_file() and OUT not in p.parents
        and not {'runtime','__pycache__'}.intersection(p.parts)}
    source=OUT/NAME
    external=Path.home()/'Downloads'/NAME
    if source.exists():
        if external.exists():assert sha(source)==sha(external)
    else:shutil.copyfile(external,source)
    old=read(V2/'NEW_NORMALIZED_EXTERNAL_LLM_REVIEW_30_20261101.csv');new=read(source)
    old_by={r['id']:r for r in old};new_by={r['id']:r for r in new}
    texts={r['ID']:r for r in read(V3/'comparison_v2_v3_30.csv')}
    assert len(old)==len(new)==len(old_by)==len(new_by)==30
    assert set(old_by)==set(new_by)==set(texts)
    assert all(r['split']=='train' for r in texts.values())
    assert set(new[0])=={'id',*COMMON,'semantic_drift','quote_fidelity','rhetorical_intensity_preserved','notes'}
    assert all(r[f] in {'Yes','Borderline','No'} for r in old+new for f in COMMON+['semantic_drift'])
    assert all(r[f] in {'Yes','Borderline','No'} for r in new for f in ['quote_fidelity','rhetorical_intensity_preserved'])
    rank={'No':0,'Borderline':1,'Yes':2}
    rows=[]
    for rid,a in old_by.items():
        b=new_by[rid]
        changes={f:rank[b[f]]-rank[a[f]] for f in COMMON}
        # Drift Yes/Borderline are both a reported risk; severity comes from meaning/other ratings.
        risk=lambda r:r['semantic_drift']!='No'
        changes['semantic_drift_risk_presence']=int(risk(a))-int(risk(b))
        gains=[f for f,d in changes.items() if d>0];losses=[f for f,d in changes.items() if d<0]
        outcome='mixed' if gains and losses else 'improved' if gains else 'worsened' if losses else 'unchanged'
        t2,t3,note=NOTE_CODING[rid.split(':')[1]]
        row=dict(id=rid,split='train',v3_outcome_vs_v2=outcome,error_change_summary=note,
            improved_fields='|'.join(gains),worsened_fields='|'.join(losses),
            reported_v2_error_types='|'.join(t2),reported_v3_error_types='|'.join(t3),
            reported_error_profile_changed=set(t2)!=set(t3),
            note_coding_limit='Reported notes only; omitted mention is unknown, not a fixed error',
            v2_evaluation_type='External LLM Review — New Normalized v2',
            v3_evaluation_type='External LLM Review — v3 blind package (reported; blinding not independently verified)',
            human_verified=False)
        for f in COMMON+['semantic_drift','notes']:
            row['v2_'+f]=a[f];row['v3_'+f]=b[f]
        row.update(v2_quote_fidelity='Not collected',v3_quote_fidelity=b['quote_fidelity'],
            v2_rhetorical_intensity_preserved='Not collected',v3_rhetorical_intensity_preserved=b['rhetorical_intensity_preserved'],
            v2_text_sha256=hashlib.sha256(texts[rid]['New_v2'].encode()).hexdigest(),
            v3_text_sha256=hashlib.sha256(texts[rid]['New_v3'].encode()).hexdigest())
        rows.append(row)
    save('V2_V3_EXTERNAL_REVIEW_COMPARISON_30.csv',rows)
    outcomes=collections.Counter(r['v3_outcome_vs_v2'] for r in rows)
    save('OUTCOME_COUNTS.csv',[dict(Outcome=k,Count=outcomes[k]) for k in ['improved','worsened','unchanged','mixed']])
    errors=[]
    for t in [Q,C,A,F,E,P,R,O,T,L]:
        ids2=[r['id'] for r in rows if t in r['reported_v2_error_types'].split('|')]
        ids3=[r['id'] for r in rows if t in r['reported_v3_error_types'].split('|')]
        errors.append(dict(error_type=t,v2_count=len(ids2),v3_count=len(ids3),delta=len(ids3)-len(ids2),
            v2_ids='|'.join(ids2),v3_ids='|'.join(ids3),
            measurement='Qualitative coding of supplied notes, not full-error prevalence or direct missing-column comparison'))
    save('REPORTED_ERROR_TYPE_COUNTS.csv',errors)
    counts={v:{f:dict(collections.Counter(r[f] for r in records)) for f in COMMON+['semantic_drift']}
            for v,records in [('v2',old),('v3',new)]}
    transitions=[dict(field=f,v2_value=a,v3_value=b,count=sum(r['v2_'+f]==a and r['v3_'+f]==b for r in rows))
        for f in COMMON+['semantic_drift'] for a in ['Yes','Borderline','No'] for b in ['Yes','Borderline','No']]
    save('FIELD_TRANSITIONS.csv',transitions)
    summary=dict(n=30,outcomes=dict(outcomes),field_counts=counts,reported_error_type_counts=errors,
        outcome_rule='Pareto comparison on five shared preservation/style fields (No<Borderline<Yes) plus drift-risk presence; Yes and Borderline drift are both risk. No scalar averaging.',
        unchanged_means='Shared ordinal ratings unchanged, not identical text or identical defects',
        note_types_are_assistant_coding=True,style_semantic_tradeoffs_remain_mixed=True,
        v3_new_field_counts={f:dict(collections.Counter(r[f] for r in new)) for f in ['quote_fidelity','rhetorical_intensity_preserved']},
        evaluator_model_version='Not supplied for either review',evaluation_prompt='Not supplied',
        v3_blinding='Reported use of blind package; actual evaluator context not independently logged',
        no_new_llm_judge=True,no_human_validation=True,no_training=True,no_test_evaluation=True)
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report(rows,counts,outcomes,errors)
    assert all(sha(p)==h for p,h in protected.items())
    audit=dict(source_sha256=sha(source),v2_review_sha256=sha(V2/'NEW_NORMALIZED_EXTERNAL_LLM_REVIEW_30_20261101.csv'),
        v3_comparison_sha256=sha(V3/'comparison_v2_v3_30.csv'),protected_files=len(protected),changed_files=[],
        unique_ids=30,all_train=True,ratings_preserved=True,human_fields_unchanged=True,
        model_version_unknown=True,review_text_binding='ID and user context only; supplied review lacks reviewed-text hashes')
    (OUT/'import_comparison_audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(outcomes=outcomes,field_counts=counts)))


def report(rows,counts,outcomes,errors):
    focused={'creators:'+s for s in ['120669','423315','421951','8b0d99b23d03','418904','298495','418827','459e183c1d0d']}
    text='''# השוואה רשמית לפי ID — External LLM Review v2 מול v3

2026-11-02; אותם 30 מקורות train. יובא קובץ סקירת v3 שסופק ללא שינוי בתים, ונשמר בנפרד מסקירת v2 ומ־Human Validation. זהו ניתוח דירוגים שסופקו, לא שופט חדש. גרסאות מודלי ההערכה, prompt ההערכה והקשר השיחה לא סופקו; העיוורון של v3 מבוסס על דיווח/חבילת המקור, ואינו מאומת עצמאית. הקבצים אינם מכילים hashes של הטקסט שנסקר; שיוך הגרסאות נשען על ID והקשר המסירה.

## כלל ההכרעה

השוואת Pareto בחמשת שדות השימור/style המשותפים: No < Borderline < Yes. improved = שיפור בשדה אחד לפחות וללא הרעה; worsened = הרעה ללא שיפור; mixed = שיפור והרעה בשדות שונים; unchanged = ללא שינוי בציונים המשותפים. אין ממוצע מספרי ואין ביטול של פגיעה במשמעות באמצעות שיפור style. כל ערכי Borderline המקוריים נשמרים.

semantic_drift נשמר בשתי גרסאותיו, אך לצורך כלל ההכרעה בלבד Yes ו־Borderline נחשבים נוכחות סיכון: v2 סימן Yes גם ל־15 מקרי meaning=Borderline, בעוד v3 משתמש ב־drift=Borderline. אין לספור שינוי מוסכמת דירוג כשיפור סמנטי. ההשוואה אינה משנה thresholds או filtering של הניסוי.

unchanged פירושו ציונים זהים, לא טקסט או שגיאה זהים. error_change_summary ושדות reported_error_types מתארים בנפרד את מוקד השגיאה בהערות. היעלמות אזכור אינה הוכחה לתיקון; קטגוריות ההערות הן קידוד איכותני של הסוכן, לא תיוג אנושי. כך למשל 295188/416436 משנים מוקד שגיאה מתואר, אף שציוני המשמעות נשארו Borderline.

## תוצאות ההשוואה

'''
    text+=table(['Outcome','Count'],[[x,outcomes[x]] for x in ['improved','worsened','unchanged','mixed']])
    text+='\n\n'+table(['Field','v2 Yes / Borderline / No','v3 Yes / Borderline / No'],
        [[f,' / '.join(str(counts['v2'][f].get(k,0)) for k in ['Yes','Borderline','No']),
          ' / '.join(str(counts['v3'][f].get(k,0)) for k in ['Yes','Borderline','No'])] for f in COMMON+['semantic_drift']])
    text+='\n\n## סוגי שגיאות שדווחו בהערות — לא ספירה מלאה של שגיאות\n\n'
    text+='v2 לא אסף quote_fidelity/rhetorical_intensity כשדות נפרדים. לכן הטבלה הבאה מקודדת רק את ההערות בשני הסבבים, באותה טקסונומיה; היא אינה משווה היעדר שדה ב־v2 ל־Yes. קטגוריות חופפות וכיסוי ההערות שונה. גם certainty/attribution כאן הם אזכורי שגיאות בהערות, בנפרד מספירת שדות הדירוג לעיל.\n\n'
    text+=table(['Error type','v2 count','v3 count','delta'],[[e[k] for k in ['error_type','v2_count','v3_count','delta']] for e in errors])
    text+='\n\n## דוגמאות המיקוד\n\n'
    text+=table(['ID','Outcome','v2 meaning','v3 meaning','error_change_summary'],
        [[r[k] for k in ['id','v3_outcome_vs_v2','v2_meaning_preserved','v3_meaning_preserved','error_change_summary']] for r in rows if r['id'] in focused])
    text+='''

ב־421951 הסקירה החדשה מזהה היפוך תפקיד, אבל תבנית דומה כבר נצפתה בטקסט v2 ב־Error Analysis; זהו גם פער גילוי בין הבודקים, לא הוכחה שהשגיאה נוצרה לראשונה ב־v3. ב־8b0d99b23d03 נשאר meaning=No ונוספה בהערות השמטת ימים; unchanged אינו אומר שלא נוספה בעיה. ב־417181 יש mixed: attribution משתפר No→Borderline בעוד certainty מידרדר Borderline→No. ב־423545 meaning משתפר No→Borderline, אך המטאפורה עדיין בעייתית. ב־459e183c1d0d שני הבודקים מאשרים; אין מכאן הוכחה שכל סיכון שזוהה בניתוח העצמי נשלל.

סקירת v3 מסמנת quote_fidelity=Yes גם ב־417181, אף שבדיקת הטקסט הקודמת הראתה מחיקת fighting; ב־423545/416436 דגל הציטוטים האוטומטי מתייחס לפסיק בתוך ציטוט. אלה אי־הסכמות/פערי קריטריון שיש לשמר, לא לתקן בקובץ המקור. אין להסיק מספירת quote=Yes שהוראת verbatim נאכפה בכל הטקסט.

## האם v3 טוב יותר?

**לפי הדירוגים שסופקו, לא הודגם שיפור כולל של v3.** meaning=Yes ירד 10→5, ‏No עלה 5→8 ו־Borderline עלה 15→17; style=Yes ירד 30→27 עם 3 Borderline. המעברים האוטומטיים עלו 6→9 וה־style proxy עלה 24→26, אך זה אינו גידול באישורי משמעות חיצוניים. 423545 מציג שיפור חלקי; 120669, ‏423315 ו־418904 מספקים דוגמאות להרעה בדירוגים. שימור סמנטי עדיין צוואר הבקבוק.

זו השוואה תיאורית בין סקירות עם הקשר ושדות לא זהים, לא ניסוי מבוקר בין מעריכים ולא הוכחה סיבתית שה־prompt לבדו גרם להחמרה. אי אפשר לחשב ממנה שיעור semantic-safe מאומת או להסיק על unseen authors/test. שלוש שאלות הסיכום הנוספות מהבקשה המקורית לא התקבלו; הדוח אינו ממציא אותן.

## כל 30 ההשוואות

'''
    text+=table(['ID','Outcome','improved fields','worsened fields','error_change_summary'],[[r[k] for k in ['id','v3_outcome_vs_v2','improved_fields','worsened_fields','error_change_summary']] for r in rows])
    text+='''

## תוצרים ושחזור

- [כל השדות, ההערות והתוצאות לפי ID](V2_V3_EXTERNAL_REVIEW_COMPARISON_30.csv).
- [ספירות outcome](OUTCOME_COUNTS.csv), [מעברי שדות](FIELD_TRANSITIONS.csv), [סוגי שגיאות מדווחות](REPORTED_ERROR_TYPE_COUNTS.csv).
- [מקור v3 ללא שינוי](V3_BLIND_EXTERNAL_LLM_REVIEW_30_20261102.csv), [סיכום](summary.json), [בדיקת תקינות](import_comparison_audit.json).

להרצה חוזרת של הייבוא/הסיכום בלבד, מתיקיית הרפו:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_v3_30_20261102/external_llm_review_20261102/compare_reviews.py
```

לא שונו prompt, guards, thresholds, filtering, split, labels, human-review fields או קוד אימון. לא הורצו מודל שופט, training או test evaluation. External LLM Review ≠ Human Validation. עוצרים לפני שינוי נוסף.
'''
    (OUT/'V2_V3_EXTERNAL_REVIEW_COMPARISON_HE.md').write_text(text,encoding='utf-8')


if __name__=='__main__':main()

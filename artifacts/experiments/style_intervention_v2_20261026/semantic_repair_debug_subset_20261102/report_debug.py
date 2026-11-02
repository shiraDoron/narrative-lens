from debug import *
import io,unittest

def main():
    suite=unittest.defaultTestLoader.discover(str(OUT),pattern='test_patch_contract.py')
    stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    assert tests.wasSuccessful()
    (OUT/'PATCH_UNIT_TEST_RESULTS.md').write_text('# Patch unit tests\n\n'+str(tests.testsRun)+' tests passed; 0 failures/errors. Every successful fixture asserts the complete expected text and reconstruction from exact edited offsets; rejection fixtures assert the expected exception/current-text behavior.\n\n```text\n'+stream.getvalue()+'```\n',encoding='utf8')
    rows=json.loads((OUT/'subset_model_outputs.json').read_text(encoding='utf8'));assert len(rows)==6
    from jsonschema import validate as validate_schema
    for r in rows:
        for stage in (r['verification'],r['repair']):
            if stage and stage['parsed'] is not None and stage['finish_reason']!='length':
                validate_schema(stage['parsed'],stage['request']['response_format']['json_schema']['schema'])
    m=previous.helper();m.OUT=OUT
    validation={r['row_id']:r for r in m.records(OUT/'rewrite_validation.csv')}
    baseline={r['row_id']:r for r in m.records(previous.V2/'rewrite_validation.csv') if r['condition']=='Normalized'}
    events=[e for r in rows for e in r['patch_events']]
    applied=[e for e in events if e['applied']]
    audits=[]
    for r in rows:
        reconstructed=r['v2_rewrite']
        for e in r['patch_events']:
            if e['applied']:
                result,edit=apply_patch(reconstructed,e['patch'],r['Original']);assert edit==e['edit'];reconstructed=result
        assert reconstructed==r['repaired']
        audits.append(dict(ID=r['ID'],replay_exact=True,changed=r['repaired']!=r['v2_rewrite'],schema_valid=r['verification_valid'],proposed=len(r['patch_events']),applied=sum(e['applied'] for e in r['patch_events']),old_reasons=baseline[r['ID']]['rejection_reasons'],new_reasons=validation[r['ID']]['rejection_reasons']))
    write('subset_technical_audit.csv',audits)
    # Hash protected inputs and ensure no old experiment data, style prompt or guards changed.
    import subprocess
    changed=subprocess.check_output(['git','diff','--name-only'],cwd=previous.ROOT,text=True).splitlines()
    allowed={str((OLD/'REPORT_HE.md').relative_to(previous.ROOT)).replace('\\','/'),'CURRENT_STATE.md'}
    assert all(p in allowed or '/semantic_repair_debug_subset_20261102/' in p for p in changed),changed
    refs=[OLD/'model_stage_outputs.jsonl',OLD/'repaired_outputs.csv',previous.V2/'prompt.txt',previous.PREVIOUS/'experiment.py',previous.ROOT/'experiments/author_generalization/author_style_controlled.py']
    dump('integrity_audit.json',dict(replays=audits,reference_sha256={str(p.relative_to(previous.ROOT)):m.sha(p) for p in refs},scope='All six are existing TRAIN rows; no full 30 regeneration, training, test evaluation or External LLM Review',changed_existing_files=changed))
    counts=dict(verification_valid=sum(r['verification_valid'] for r in rows),verification_empty=sum(not r['verification']['parsed'].get('issues',[]) for r in rows if r['verification']['parsed']),repair_calls=sum(r['repair'] is not None for r in rows),proposals=len(events),applied=len(applied),changed_rows=sum(r['repaired']!=r['v2_rewrite'] for r in rows),guard_pass=sum(validation[r['ID']]['passed']=='True' for r in rows),tests=tests.testsRun)
    dump('technical_summary.json',counts)
    report='# Semantic Verification + Structured Repair — debug subset\n\n'
    report+='בדיקה טכנית בלבד על שש דוגמאות train קיימות. זו אינה הערכה מחקרית, External LLM Review או אימות אנושי. ה־style prompt, ה־guards והספים נשארו קבועים.\n\n'
    report+='## אבחון המנגנון הקודם\n\n11/30 כשלי verification היו כשלי ראיות מילוליות, ולא malformed JSON, שדות חסרים או schema לא תקין. בקובץ הניתוח יש שורה לכל ID ופירוט כל הראיות שנכשלו. 18 קבוצות תיקון שנדחו כללו 41 edits, ולא 18 edits בודדים. הסיבה העיקרית: שימוש בטקסט מה־Original כיעד בתוך Rewrite, לעיתים עם replacement שכבר קיים ב־Rewrite. היו גם patches רחבים ו־no-ops; כשל אחד ביטל קבוצה שלמה. יש להבחין בין כשל טכני זה לבין נכונות הטענה הסמנטית של המודל.\n\n'
    report+='התיקון היחיד שהוחל בניסוי הקודם כלל no-op ומחיקת המשפט על fictitious entities, אף שהטענה קיימת במקור. מעבר בדיקת certainty בעקבות מחיקה כזו אינו ראיה לתיקון משמעות. החוזה החדש דוחה no-op ומחיקות ארוכות.\n\n'
    report+='## תוצאות טכניות\n\n'+f"Verification contract valid: {counts['verification_valid']}/6; empty issue lists: {counts['verification_empty']}/6; repair calls: {counts['repair_calls']}; applied proposals: {counts['applied']}/{counts['proposals']}; changed texts: {counts['changed_rows']}/6. Unit tests: {counts['tests']} passed.\n\n"
    report+='| ID | verification valid | proposed | applied | changed | old guard failures | new guard failures |\n|---|---|---|---|---|---|---|\n'
    for r in audits: report+='| '+' | '.join((str(r[k]) or 'none').replace('|','\\|') for k in ['ID','schema_valid','proposed','applied','changed','old_reasons','new_reasons'])+' |\n'
    report+='\nכל patch שהוחל שוחזר בדיוק לפי offsets, והטקסט מחוץ לטווח העריכה נשמר. אין החלפת פסקה שלמה ואין מחיקה של יותר משמונה מילים. פירוט היעדים, ההחלפות, הדחיות והפלטים המלאים נשמר ב־subset_model_outputs.json וב־subset_outputs.csv. בדיקות ה־guards הופעלו על כל השש, כולל fallback ללא שינוי. שינוי בדגלים הוא מידע אבחוני בלבד.\n\n'
    report+='## מגבלות שנחשפו ב־debug\n\nגם לאחר תיקון כיוון היעדים, המודל המקומי מציע תיקונים לא מספקים: ב־417181 patch אחד רק מסיר נקודה במקום להחזיר fighting, וב־423315 הוא משנה את מיקום yet במקום לתקן riots/protests או destined. ב־8b0d99b23d03 הוא מחליף רק תחילת ציטוט, משאיר אחריו את שארית הציטוט הישן ויוצר ציטוט פגום. ב־421951 הוצעה מחיקה עם replacement לא ריק והיא נדחתה. אלה תצפיות debug פנימיות על הטקסט וה־patch, ולא External LLM Review חדש. תקינות החוזה אינה מונעת repair סמנטי שגוי או בחירת גבולות עריכה לא מתאימים. בפרט אין לטעון ש־quote restoration הצליח במודל רק מפני שבדיקת היחידה עוברת.\n\n'
    rate=counts['applied']/max(1,counts['proposals'])
    report+=('החוזה וההחלה הוכיחו יכולת טכנית בסיסית ב־subset זה; אין מכאן ראיה לשימור משמעות או הצדקה אוטומטית להרצת 30.\n' if counts['verification_valid']==6 and rate>.5 and counts['applied'] else 'קריטריון ההצלחה הטכני המלא עדיין לא הושג. אין לחזור אוטומטית לניסוי 30.\n')
    report+='\nתקינות schema אינה recall של verifier: רשימה ריקה עשויה להיות החמצה. הסכמה מונעת ראיות מומצאות אך אינה מונעת בחירת span לא רלוונטי או replacement שגוי. יש לבדוק זאת לפני החלטה על ניסוי נוסף. לא בוצעו retries או בחירת מועמד לפי ציוני guards.\n'
    (OUT/'DEBUG_SUBSET_RESULTS.md').write_text(report,encoding='utf8')
    appendix='\n\n## Technical debug checkpoint — 2026-11-02\n\n'+f"On six fixed TRAIN v2 candidates only: verification contract {counts['verification_valid']}/6; applicable/applied patches {counts['applied']}/{counts['proposals']}; changed rows {counts['changed_rows']}/6; unit tests {counts['tests']} passed. This measures technical execution, not semantic success. Original 30-row outputs remain unchanged. No style prompt, experimental guard/threshold, split, label or existing human-review field changed. No training, test evaluation or External LLM Review. See [debug results](../semantic_repair_debug_subset_20261102/DEBUG_SUBSET_RESULTS.md).\n"
    p=OLD/'REPORT_HE.md';text=p.read_text(encoding='utf8');marker='\n\n## Technical debug checkpoint — 2026-11-02';p.write_text(text.split(marker)[0]+appendix,encoding='utf8')

if __name__=='__main__': main()

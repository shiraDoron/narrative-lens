"""Build reviewable evidence tables from the isolated audit outputs (no raw-data writes)."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/research_author_style_language'
UNKNOWN='לא נמצא מקור אמין'

def main():
    x=pd.read_csv(OUT/'text_language_style_predictions.csv').fillna('')
    roster=pd.read_csv(OUT/'author_language_evidence.csv').fillna('')
    registry=json.loads((OUT/'native_language_registry.json').read_text(encoding='utf-8'))
    # Direct content checks only. This is not an exhaustive correction of language ID.
    checked={
      'twitter:910':('es','Spanish text, not evidence of account holder L1'),
      'twitter:1476':('pt','Portuguese text'),
      'twitter:1501':('pt','Portuguese text'),
      'twitter:1505':('fr','French text'),
      'twitter:1531':('es','Spanish text'),
      'twitter:1535':('es','Spanish text'),
      'twitter:2091':('fr','French text'),
      'twitter:2873':('es','Spanish text; repost/quotation authorship not established'),
      'twitter:3424':('uk+en','Ukrainian and English bilingual text; automatic ru was inaccurate'),
      'telegram:436':('he','Hebrew prose'),
      'telegram:1809':('ru','Russian prose; one checked example, not a statement about every Rybar row'),
      'twitter:2783':('en','English headline; automatic fr was inaccurate'),
      'telegram:286':('en','English uppercase headline; automatic zh was inaccurate'),
      'telegram:2236':('en','English text plus channel footer; automatic la was inaccurate'),
    }
    review=[]
    for row_id,(language,note) in checked.items():
        g=x[x.row_id==row_id]
        assert len(g)==1,row_id
        r=g.iloc[0]
        review.append({'row_id':row_id,'account':r.account,'source_csv':r.source_csv,
                       'csv_record_number':r.csv_record_number,'automatic_candidate':r.language_candidate,
                       'content_checked_language':language,'note':note,'text_sha256':r.text_sha256})
    pd.DataFrame(review).to_csv(OUT/'language_content_checks.csv',index=False,encoding='utf-8-sig')
    def esc(v):return str(v).replace('|',' / ').replace('\n',' ')
    lines=['# טבלת כל החשבונות: שפת אם, שפת טקסט ונרטיב','',
      'תאריך: 20.10.2026. 83 מזהי חשבון, 10,330 רשומות אמיתיות. החשבון אינו בהכרח המחבר בפועל.',
      '',
      'Native Language כולל גם מידע שמסרה החוקרת, המסומן בנפרד: verified = מקור חיצוני מפורש; probable = שיוך משוער שמסרה החוקרת; user_reported_unverified = מידע שמסרה החוקרת ללא מקור מצורף. Hebrew / English אינו קובע ששתי השפות הן שפות אם. בחשבונות ללא מידע נשמר סטטוס חסר. תחזיות Text Language הן פלט ראשוני של langid ולא בדיקה אנושית מלאה.',
      '',
      'Narrative הוא התיוג המקורי לפי מקור החשבון. תחזיות המסווג נמצאות בקובץ predictions_by_account.csv ובעמודות נוספות ב-CSV; הן לא הוחלפו בתיוג המקורי.',
      '',
      '| Author | Native Language | Native Language Status | Text Language | Narrative | Evidence/Source | Possible Linguistic Influence |',
      '|---|---|---|---|---|---|---|']
    for i,r in roster.iterrows():
        g=x[x.account==r.Author]
        known=registry.get(r.Author,{})
        if known.get('status')=='explicit_reliable_source':
            roster.at[i,'Native Language']=known['native_language']
        elif known.get('native_language'):
            roster.at[i,'Native Language']=known['native_language']
        confidence=known.get('confidence_status','verified' if known.get('status')=='explicit_reliable_source' else 'unknown')
        roster.at[i,'Native Language Status']=confidence
        roster.at[i,'Native Language Provenance']='external_source' if confidence=='verified' else ('user_provided' if confidence!='unknown' else 'missing')
        roster.at[i,'Native Language Source']=known.get('source_url','')
        if confidence in {'probable','user_reported_unverified'}:
            roster.at[i,'Evidence/Source']='; '.join(sorted(g.source_csv.unique()))+'; user-provided; no external L1 source supplied'
        langs=g.language_candidate.value_counts().to_dict()
        checked_langs=sorted({language for rowid,(language,_) in checked.items() if rowid in set(g.row_id)})
        description=f"en candidate: {langs.get('en',0)}/{len(g)}; other/und: {len(g)-langs.get('en',0)}"
        if checked_langs:description+='; content checks: '+', '.join(checked_langs)
        roster.at[i,'Text Language']=description
        pred=g.predicted_narrative.value_counts()
        roster.at[i,'Predicted Narrative (most frequent)']=pred.index[0]
        roster.at[i,'Most frequent prediction count']=int(pred.iloc[0])
        influence=(f"משפט: {r.mean_mean_sentence_words:.2f} מילים; מילה: {r.mean_mean_word_chars:.2f} תווים; "
          f"קישור: {r.mean_connectors_per100_words:.2f}/100 מילים. השפעת שפת אם לא הוכחה; ייתכנו עריכה/תרגום.")
        roster.at[i,'Possible Linguistic Influence']=influence
        source_links=[]
        for path in sorted(g.source_csv.unique()):
            source_links.append(f'[{Path(path).name}](../../{path})')
        if known.get('status')=='explicit_reliable_source':
            source_links.append(f"[Reuters/Euronews]({known['source_url']})")
        else:
            source_links.append('[סטטוס מקור](native_language_registry.json)' if r.Author in registry else 'אין כותב יחיד ושפת אם מאומתים ברמת הרשומה')
        if confidence in {'probable','user_reported_unverified'}:
            source_links.append('מידע שמסרה החוקרת; ללא מקור חיצוני מצורף')
        lines.append('| '+' | '.join([esc(r.Author),esc(roster.at[i,'Native Language']),confidence,esc(description),esc(r.Narrative),'; '.join(source_links),esc(influence)])+' |')
    roster.to_csv(OUT/'author_language_evidence.csv',index=False,encoding='utf-8-sig')
    (OUT/'author_language_table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    person=roster[roster.Author.isin(registry)]
    person.to_csv(OUT/'person_associated_accounts_summary.csv',index=False,encoding='utf-8-sig')
    summary=json.loads((OUT/'audit_summary.json').read_text(encoding='utf-8'))
    summary['verified_native_language_accounts']=int((roster['Native Language Status']=='verified').sum())
    summary['native_language_status_counts']=roster['Native Language Status'].value_counts().to_dict()
    summary['native_language_correlation']={'status':'not_identifiable','reason':'Only one independently documented L1 group/person-associated account. Unknown L1 is missing data, not a language category. Account holder is not verified post writer.'}
    summary['checks']={'roster_unique':bool(roster.Author.is_unique),'all_real_rows_accounted_for':int(roster.n_texts.sum())==len(x),'prediction_rows':len(x),'probability_sums_valid':bool(np.allclose(x[[c for c in x if c.startswith('p_')]].sum(axis=1),1,atol=1e-5)), 'shai_goldstein_author_present':bool(x.account.str.contains('goldstein|theshelterradio',case=False).any())}
    summary['analysis_script_sha256_current']=hashlib.sha256((ROOT/'scripts/research_author_style_language.py').read_bytes()).hexdigest()
    summary['script_changed_after_measurement']='Registry integration and removal of unused expression only; numeric measurements unchanged. Original run hash retained.'
    (OUT/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    cases=json.loads((OUT/'case_studies.json').read_text(encoding='utf-8'))
    rows=[]
    for case in cases['cases']:
        for text in case['texts']:
            rows.append({'author':case['author'],**{k:v for k,v in text.items() if k!='excerpt'}})
    pd.DataFrame(rows).to_csv(OUT/'case_study_texts.csv',index=False,encoding='utf-8-sig')
    print(json.dumps(summary['checks']))
    print('Documented L1 accounts:',summary['verified_native_language_accounts'])

if __name__=='__main__':main()

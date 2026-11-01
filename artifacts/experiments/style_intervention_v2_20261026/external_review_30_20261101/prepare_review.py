"""Prepare 30 TRAIN-only review examples from existing machine outputs.

Inputs: frozen V2 cohort, rewrites, validation and style measurements.
Outputs: one readable Markdown pack, companion CSV, and selection audit.
No model calls, semantic judgments, human-field filling, split edits or training.
Run with Python 3.11; outputs stay beside this script.
"""
from pathlib import Path
import collections
import csv
import datetime
import hashlib
import json

OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent
HUMAN_FIELDS=['human_narrative_label','narrative_label_correct',
    'paraphrase_meaning_preserved','normalized_meaning_preserved',
    'style_change_valid','human_notes']
SEED='20261101-external-review-30'


def read_csv(name):
    """Read existing UTF-8 CSV without changing it."""
    with (SOURCE/name).open(encoding='utf-8-sig',newline='') as stream:
        return list(csv.DictReader(stream))


def digest(path):
    """Hash an artifact to verify immutable inputs and split definitions."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(value):
    """Return a reproducible ordering independent of filesystem enumeration."""
    return hashlib.sha256((SEED+'|'+value).encode()).hexdigest()


def pick_diverse(candidates, count):
    """Round-robin across authors using hash order; never inspect semantic quality."""
    buckets=collections.defaultdict(list)
    for record in candidates:buckets[record['author']].append(record)
    for author in buckets:buckets[author].sort(key=lambda r:rank(r['row_id']))
    authors=sorted(buckets,key=rank)
    selected=[]
    while len(selected)<count:
        previous=len(selected)
        for author in authors:
            if buckets[author] and len(selected)<count:selected.append(buckets[author].pop(0))
        if len(selected)==previous:raise ValueError('Insufficient examples for fixed group size')
    return selected


def cell(value):
    """Escape values for compact Markdown tables."""
    return str(value).replace('|','\\|').replace('\n',' ')


def main():
    """Select disjoint diagnostic groups and export existing scores verbatim."""
    protected_names=['analysis_cohort.csv','split_definitions.csv','author_splits.csv',
        'generated_rewrites.jsonl','rewrite_validation.csv','style_change_metrics.csv',
        'human_review.csv','HUMAN_REVIEW.html']
    before={name:digest(SOURCE/name) for name in protected_names}
    corpus=read_csv('analysis_cohort.csv')
    validation={(r['row_id'],r['condition']):r for r in read_csv('rewrite_validation.csv')}
    styles={(r['row_id'],r['condition']):r for r in read_csv('style_change_metrics.csv')}
    rewrites={(r['row_id'],r['condition']):r for r in
        [json.loads(line) for line in (SOURCE/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]}
    train=[r for r in corpus if r['split']=='train']
    def passed_all(record):
        """Use saved automatic pass flags only, without reassessing meaning."""
        return all(validation[record['row_id'],c]['passed']=='True' for c in ['Formatting','Paraphrase','Normalized'])
    used=set();selected=[]
    groups=[('substantial_style_proxy',lambda r:styles[r['row_id'],'Normalized']['substantial_style_change']=='True'),
            ('minimal_style_proxy',lambda r:styles[r['row_id'],'Normalized']['style_change_group']=='minimal' and passed_all(r)),
            ('automatic_screen_rejected',lambda r:not passed_all(r))]
    availability={}
    for group,predicate in groups:
        candidates=[r for r in train if r['row_id'] not in used and predicate(r)]
        availability[group]=len(candidates)
        for record in pick_diverse(candidates,10):
            selected.append((group,record));used.add(record['row_id'])
    selected_authors={r['author'] for _,r in selected}
    held_out_authors={r['author'] for r in corpus if r['split']!='train'}
    assert len(selected)==30 and len(used)==30 and not selected_authors&held_out_authors
    preface='''# חבילת בדיקה חיצונית — 30 טקסטים מכותבי האימון בלבד

## מה יש כאן

30 דוגמאות קיימות: 10 עם שינוי משמעותי לפי proxy אוטומטי, 10 עם שינוי מזערי שעברו את כל המסננים, ו־10 שנפסלו לפחות באחת מזרועות השכתוב/Formatting. כל רשומה מופיעה פעם אחת. קבוצות הבחירה נפרדות, אך דוגמה בקבוצת השינוי המשמעותי יכולה גם להיות פסולה אוטומטית.

הבחירה נעשתה לפי ציונים ודגלים קיימים בלבד, בסבב בין כותבים ובסדר hash קבוע. לא בוצעה הכרעה אם הנרטיב נכון, אם המשמעות נשמרה או אם השינוי הסגנוני אמיתי. זה מדגם אבחוני מכוון, לא מדגם מייצג להערכת שיעורי הצלחה. ה־test וה־validation לא נכללו ולא שונו.

## הוראות למי שמקבל את החבילה

הצעת הנרטיב והמדדים הם פלט מכונה, לא אמת מאומתת. confidence הוא ציון AI בסולם 1–3, לא הסתברות מכוילת. passed=True פירושו מעבר בסינון אוטומטי בלבד. שדות guard הם בדיקות אוטומטיות; human_verified=False הוא שדה מקור קיים, לא הכרעה חדשה.

לכל רשומה יש שישה שדות ריקים בסופה. החבילה הוכנה ללא מילוי שלהם וללא שימוש ב־LLM נוסף לשיפוט. אפשר להחזיר טבלת תוצאות עם ID וששת השדות. שמרו על ניסוח המקור והשכתובים ללא עריכה.

**הבחנה מחקרית:** בדיקה על ידי ChatGPT היא בדיקת LLM חיצונית, גם אם נקראת בשיחה “Human Review”. היא אינה אימות אנושי או agreement בין בני אדם. יש לתעד מי/איזה מודל ביצע את הבדיקה, ולא להציג תשובת ChatGPT כתיוג אנושי. אימות אנושי מחקרי דורש סוקר/ת אדם.

## פירוש מדדי הסגנון

word_edit_fraction הוא אי־דמיון סימטרי של רצף מילים (1 פחות SequenceMatcher), ולא שיעור מילים שהוחלפו מילולית. אחוזי החלפה/מחיקה/הוספה נשמרים בנפרד. sentence_mean_relative_change הוא proxy לפי אורך משפט, לא ניתוח תחבירי. punctuation_l1_per100 הוא שינוי בתדירות סימני פיסוק ל־100 מילים. formality_proxy_delta מבוסס על כיווצים ומילות דיבור ואינו מדד פורמליות מתוקף. substantial_style_change הוא דגל תפעולי קיים, לא אימות סגנון.

כלל substantial: word_edit_fraction ≥0.15 וגם לפחות אחד: שינוי יחסי בממוצע אורך משפט ≥0.15, מרחק פיסוק ≥1 ל־100 מילים, או שינוי מוחלט בכיווצים ≥1 ל־100 מילים. minimal: עריכת מילים <0.05 ללא עמידה בכלל substantial. הספים לא שונו.

'''
    markdown=[preface,'## אינדקס','', '| # | ID | Author | קבוצת בחירה | הצעת נרטיב |','|---|---|---|---|---|']
    for index,(group,r) in enumerate(selected,1):markdown.append(f"| {index} | {r['row_id']} | {r['author_name']} | {group} | {r['narrative_name']} |")
    export=[]
    for index,(group,r) in enumerate(selected,1):
        rid=r['row_id'];record=dict(ID=rid,Author=r['author_name'],author_id=r['author'],split='train',selection_group=group,
            source_url=r['source_url'],source_date=r['source_date'],Original=r['text'],
            Paraphrase=rewrites[rid,'Paraphrase']['rewrite'],Normalized=rewrites[rid,'Normalized']['rewrite'],
            proposed_narrative=r['narrative_name'],proposed_confidence_1_to_3=r['confidence_a'],proposed_evidence=r['evidence_a'])
        markdown.extend(['',f'## דוגמה {index:02d} — {rid}',f"**Author:** {r['author_name']} | **Split:** train | **קבוצה:** {group}",
            f"**מקור:** {r['source_url']} | **תאריך:** {r['source_date']}",
            f"**הצעת נרטיב:** {r['narrative_name']} | **confidence:** {r['confidence_a']}/3",
            '**Evidence שמור מהמערכת:** '+r['evidence_a'],'','### Original',r['text'],'','### Paraphrase',record['Paraphrase'],'','### Normalized',record['Normalized'],'',
            '### תוצאות הבדיקות האוטומטיות — ללא הכרעה אנושית','',
            '| בדיקה/שדה | Formatting | Paraphrase | Normalized |','|---|---|---|---|'])
        fields=[k for k in validation[rid,'Normalized'] if k not in ['row_id','condition']]
        for field in fields:
            values=[validation[rid,c][field] for c in ['Formatting','Paraphrase','Normalized']]
            markdown.append('| '+cell(field)+' | '+' | '.join(cell(v) for v in values)+' |')
        for condition in ['Formatting','Paraphrase','Normalized']:
            screen=validation[rid,condition]
            explanation='עבר: כל הבדיקות האוטומטיות המסומנות guard עברו; אין בכך אישור שימור משמעות.' if screen['passed']=='True' else 'נפסל אוטומטית: '+screen['rejection_reasons']
            record[condition+'_automatic_decision']=explanation
            record[condition+'_automatic_checks_json']=json.dumps(screen,ensure_ascii=False)
            markdown.extend(['',f'**{condition}:** {explanation}'])
        markdown.extend(['','### מדדי style שמורים','', '| מדד | Paraphrase | Normalized |','|---|---|---|'])
        for field in styles[rid,'Normalized']:
            if field not in ['row_id','condition','split']:
                markdown.append('| '+cell(field)+' | '+cell(styles[rid,'Paraphrase'][field])+' | '+cell(styles[rid,'Normalized'][field])+' |')
        for condition in ['Paraphrase','Normalized']:
            record[condition+'_style_metrics_json']=json.dumps(styles[rid,condition],ensure_ascii=False)
        markdown.extend(['','### שדות למילוי חיצוני — הושארו ריקים','', '| שדה | תשובה |','|---|---|'])
        for field in HUMAN_FIELDS:record[field]='';markdown.append('| '+field+' | |')
        export.append(record)
    (OUT/'REVIEW_30_TRAIN_ONLY_HE.md').write_text('\n'.join(markdown)+'\n',encoding='utf8')
    with (OUT/'review_30_train_only.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(export[0]));writer.writeheader();writer.writerows(export)
    assert all(r[f]=='' for r in export for f in HUMAN_FIELDS)
    after={name:digest(SOURCE/name) for name in protected_names};assert before==after
    audit=dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seed=SEED,n=30,
        source_split='train',group_counts=dict(collections.Counter(g for g,_ in selected)),
        availability_at_selection=availability,selected_author_counts=dict(collections.Counter(r['author'] for _,r in selected)),
        selected_ids=[r['row_id'] for _,r in selected],held_out_authors_included=False,
        all_six_human_fields_blank=True,no_new_model_calls=True,no_new_semantic_judgments=True,
        no_training=True,inputs_unchanged=before==after,input_sha256=before,
        outputs_sha256={name:digest(OUT/name) for name in ['REVIEW_30_TRAIN_ONLY_HE.md','review_30_train_only.csv']},
        caution='ChatGPT review is external machine review, not human gold.')
    (OUT/'selection_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Prepared 30 train-only examples; {len(selected_authors)} authors; all review fields blank.')


if __name__=='__main__':main()

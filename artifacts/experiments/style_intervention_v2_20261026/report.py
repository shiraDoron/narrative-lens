"""Create a readable Hebrew experiment guide, review instructions and plots.

Inputs: frozen protocol, generated versions, screen results and optional genuinely
human-reviewed evaluations. Outputs: EXPERIMENT_GUIDE_HE.md, FINAL_REPORT_HE.md,
README.md and plots/. Missing stages are explicitly reported as pending.
"""
from pathlib import Path
import collections, json, sys
from study import OUT, PREVIOUS, rows, read_json, write_json, sha, event


def table(headers, records):
    """Render a small human-readable Markdown table, escaping source delimiters."""
    def clean(value):return str(value).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(clean(v) for v in record)+' |' for record in records])


def main():
    """Summarize actual artifacts without relabelling old results as new results."""
    corpus=rows(OUT/'analysis_cohort.csv'); registry=read_json(OUT/'author_registry.json')
    generated=[json.loads(line) for line in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
    generated_n=sum(r['condition']=='Normalized' for r in generated)
    validation=rows(OUT/'rewrite_validation.csv') if (OUT/'rewrite_validation.csv').exists() else []
    measurements=rows(OUT/'style_change_metrics.csv') if (OUT/'style_change_metrics.csv').exists() else []
    human=rows(OUT/'human_review.csv') if (OUT/'human_review.csv').exists() else []
    complete=sum(bool(r['reviewer'].strip()) and bool(r['reviewed_at'].strip()) and
        r['human_narrative'] in ['Left-wing','Right-wing','Unclear'] and
        all(r[c+'_'+f].strip().lower() in ['yes','no','unclear'] for c in ['Paraphrase','Normalized'] for f in
        ['narrative_preserved','stance_preserved','framing_preserved','facts_preserved','entities_preserved','negation_preserved','certainty_preserved','attribution_preserved','claim_added','claim_omitted']) for r in human)
    automatic=[r for r in corpus if all(any(v['row_id']==r['row_id'] and v['condition']==c and v['passed']=='True' for v in validation) for c in ['Formatting','Paraphrase','Normalized'])]
    results=rows(OUT/'metrics_summary.csv') if (OUT/'metrics_summary.csv').exists() else []
    stage='הערכה לאחר אימות הושלמה' if results else ('ממתין לאימות אנושי' if generated_n==218 and validation else 'יצירה/בדיקה אוטומטית בתהליך')
    status=dict(stage=stage,normalized_generated=generated_n,total=218,human_reviews_complete=complete,
        automatically_matched=len(automatic),new_training_performed=bool(results),human_validation_complete=complete==218)
    write_json('STATUS.json',status)
    splits=collections.Counter(r['split'] for r in corpus)
    previous=rows(PREVIOUS/'intervention_strength_summary.csv')
    causes='''בדוח הקודם שיעור העתקה מדויקת ב־Normalized במדגם המשותף היה כ־50.4%, ובנרמול מילים כ־63.7%.
אלו קטעי מאמרים קצרים שכבר עברו עריכה, ולכן חלקם קרובים לסגנון היעד. בנוסף ה־prompt הקודם דרש ניסוח קרוב,
שמירת ביטויים מעריכים ושאלות רטוריות. הדוגמאות שלו המחישו שינויים קטנים מאוד.
אלה הסברים סבירים מהטקסטים ומההוראות; לא נערך ablation המפריד את תרומתם. אין הוכחה איזה מהם גרם להעתקה.'''
    screen_rows=[]
    for condition in ['Formatting','Paraphrase','Normalized']:
        subset=[v for v in validation if v['condition']==condition]
        if subset:screen_rows.append([condition,len(subset),sum(v['passed']=='True' for v in subset),sum(v['passed']!='True' for v in subset)])
    failures=collections.Counter((v['condition'],reason) for v in validation for reason in v['rejection_reasons'].split('|') if reason)
    strength=[]
    for condition in ['Previous_Normalized','Paraphrase','Normalized']:
        subset=[r for r in measurements if r['condition']==condition]
        if subset:
            strength.append([condition,len(subset),sum(r['exact_copy']=='True' for r in subset),sum(r['substantial_style_change']=='True' for r in subset),
                f"{100*sum(float(r['word_edit_fraction']) for r in subset)/len(subset):.1f}%"])
    substantial_ids={r['row_id'] for r in measurements if r['condition']=='Normalized' and r['substantial_style_change']=='True'}
    normalized_pass={r['row_id'] for r in validation if r['condition']=='Normalized' and r['passed']=='True'}
    matched_ids={r['row_id'] for r in automatic}
    count_table=table(['שלב','מספר'],[['קטעים ייחודיים במאגר הקודם',429],['טקסטים בניסוי הקפוא',218],['כותבים',19],
        ['Train / Validation / Test לפני סינון',f"{splits['train']} / {splits['val']} / {splits['test']}"],['Normalized V2 שנוצרו',generated_n],
        ['עברו אוטומטית את כל הזרועות',len(automatic) if validation else 'טרם נבדק'],
        ['שינוי סגנוני משמעותי לפני סינון',len(substantial_ids)],
        ['שינוי משמעותי וגם עבר סינון Normalized',len(substantial_ids&normalized_pass) if validation else 'טרם נבדק'],
        ['שינוי משמעותי וגם עבר את כל הזרועות',len(substantial_ids&matched_ids) if validation else 'טרם נבדק'],['אימותים אנושיים מלאים',complete],
        ['מדגם משותף קודם (להקשר בלבד)',113]])
    split_flow=table(['split','לפני סינון','עברו כל התנאים אוטומטית','מהם שינוי משמעותי','כותבים אחרי סינון'],[
        [part,sum(r['split']==part for r in corpus),sum(r['split']==part for r in automatic),
         sum(r['split']==part and r['row_id'] in substantial_ids for r in automatic),
         len({r['author'] for r in automatic if r['split']==part})] for part in ['train','val','test']])
    quality=[dict(split=part,proposed_narrative=label,n=sum(r['split']==part and r['narrative_name']==label for r in automatic),
        n_authors=len({r['author'] for r in automatic if r['split']==part and r['narrative_name']==label})) for part in ['train','val','test'] for label in ['Left-wing','Right-wing']]
    write_json('automatic_cohort_quality.json',dict(human_gold=False,coverage=quality))
    significant_matched=[r for r in automatic if r['row_id'] in substantial_ids]
    significant_splits=dict(collections.Counter(r['split'] for r in significant_matched))
    from study import write_csv
    write_csv('substantial_automatic_subset.csv',significant_matched,list(corpus[0]))
    write_json('substantial_automatic_subset_status.json',dict(n=len(significant_matched),by_split=significant_splits,
        human_review_pending=complete<218,can_estimate_now=False,
        reason='Requires human review and >=3 examples / >=2 writers per class per split. One validation/test source is insufficient.'))
    author_rows=[]
    for person in registry:
        selected=[r for r in corpus if r['author']==person['author']]
        author_rows.append([f"[{person['name']}]({person['bio_url']})",len(selected),','.join(sorted({r['split'] for r in selected})),
                            dict(collections.Counter(r['narrative_name'] for r in selected))])
    example_rows=[]
    lookup={(r['row_id'],r['condition']):r['rewrite'] for r in generated}
    # Show fixed first rows AND first train-only substantial changes by input order.
    # Never use classifier outcomes to choose illustrative examples.
    changed_ids={m['row_id'] for m in measurements if m['condition']=='Normalized' and m['substantial_style_change']=='True'}
    examples=corpus[:3]+[r for r in corpus if r['split']=='train' and r['row_id'] in changed_ids][:2]
    for r in examples:
        example_rows.extend([f"### {r['row_id']}",f"[מקור ותאריך: {r['source_date']}]({r['source_url']})",'',
            '**Original**',r['text'],'','**Paraphrase**',lookup[r['row_id'],'Paraphrase'],'','**Normalized V2**',lookup.get((r['row_id'],'Normalized'),'טרם נוצר'),''])
    result_text='**טרם הורצו מודלים חדשים.** ההרצה מותנית באימות אנושי אמיתי של התוויות ושל שני השכתובים. אין להציג את תוצאות הניסוי הקודם כתוצאות V2.'
    if results:
        result_text=table(['מדגם','אימון','בדיקה','Macro-F1','סטיית תקן','N בדיקה'],[[r['cohort'],r['train_condition'],r['test_condition'],r['macro_f1_mean'],r['macro_f1_std'],r['n']] for r in results])
    verdict='האם השתנה Style? ראו מדדי V2; זהו אומדן צורני שדורש גם בדיקה אנושית. האם נשמר Narrative? טרם אומת אנושית. האם זיהוי הכותב ירד? אין תוצאת V2 לפני הרצה מאומתת. האם השתפר Macro-F1 והאם N טוב מ־P? עדיין לא ניתן לקבוע. האם לבנות LoRA? אין כרגע הצדקה חדשה. אין תמיכה מחקרית חדשה בהשערה עד השלמת האימות וההרצה.'
    if results:
        diagonal={r['train_condition']:float(r['macro_f1_mean']) for r in results if r['cohort']=='human_matched' and r['train_condition']==r['test_condition']}
        if len(diagonal)==3:
            delta_p=diagonal['Normalized']-diagonal['Paraphrase'];delta_o=diagonal['Normalized']-diagonal['Original']
            differences=[r for r in rows(OUT/'paired_seed_comparisons.csv') if r['cohort']=='human_matched']
            consistent=all(float(r['normalized_minus_paraphrase'])>0 and float(r['normalized_minus_original'])>0 for r in differences)
            probe=rows(OUT/'author_probe_summary.csv') if (OUT/'author_probe_summary.csv').exists() else []
            probe_reduction=[]
            for rep in ['embedding','explicit_style']:
                values={r['condition']:float(r['accuracy_mean']) for r in probe if r['scope']=='all_writers' and r['representation']==rep}
                probe_reduction.append(len(values)==3 and values['Normalized']<min(values['Original'],values['Paraphrase']))
            support=complete==218 and delta_p>0 and delta_o>0 and consistent and all(probe_reduction)
            verdict=f"תוצאות תיאוריות לאחר אימות: N−P={delta_p:+.4f}; N−O={delta_o:+.4f}. יתרון בשני ההשוואות בכל חמשת ה־seeds: {consistent}. ירידת Accuracy בזיהוי כותב ביחס לשני התנאים בשני הייצוגים: {all(probe_reduction)}. כללי הכיוון יחד מתקיימים: {support}. גם כאשר הם מתקיימים, אין בכך הוכחת causality או מובהקות, ונדרש לבדוק יציבות על פני כותבים ומדגם חיצוני. אין לעבור ל־LoRA על סמך ממוצע בודד."
    intro=f'''# ניסוי המשך: האם נרמול סגנון עוזר לזהות נרטיב אצל כותבים חדשים?

## תקציר

בדקנו כיצד לתקן את ההתערבות הסגנונית ואת האימות בניסוי הקודם. מצב נוכחי: **{stage}**.
נשמרו אותם 218 טקסטים, אותם 19 כותבים ואותה חלוקת train/validation/test.
נוצרו עד כה {generated_n} נרמולים חדשים. אומתו אנושית {complete} מתוך 218 טקסטים.
הפרפרזה נשארה קבועה כדי לבודד את שינוי ה־prompt של הנרמול. רמת הסינון לא הורדה.
נוצרה חבילת קריאה וסימון, ומדדי שינוי סגנון הוגדרו לפני תוצאות המסווג.
עברו אוטומטית את כל התנאים {len(automatic)} טקסטים. מתוכם רק {len(significant_matched)} עם שינוי סגנוני משמעותי;
חלוקתם היא {significant_splits}. לכן המדגם עם התערבות אמיתית עדיין קטן מדי להערכת generalization מבוססת.
{result_text}

אין עדיין ראיה חדשה לשיפור ב־generalization או להסרת shortcut. תוצאות הסינון האוטומטי אינן אימות Narrative.
אין כרגע בסיס חדש לבניית LoRA/DoRA. אימון נוסף לבדו לא יפתור תוויות לא מאומתות או התערבות חלשה.
'''
    sections=[intro,
        '## 1. שאלת המחקר וההשערה\n\nהאם סגנון הכותב הוא shortcut מזיק, והאם שינוי סגנון תוך שימור תוכן משפר Macro-F1 על כותבים חדשים? השערה תיתמך רק אם נרמול עולה על Original ועל Paraphrase, זיהוי כותב יורד יחסית לשניהם, והתוכן מאומת והשיפור עקבי.',
        '## 2. דאטה וספירות\n\n'+count_table+'\n\n'+split_flow+'\n\nספירות המעבר כאן אוטומטיות בלבד, לפני הכרעה אנושית ובדיקת כפילויות שכתובים נוספת בשלב ההערכה.\n\nכל רשומה היא קטע רציף בן כ־35–100 מילים ממאמר. גרסאות אינן דוגמאות עצמאיות. התוויות הקיימות הן הצעות AI ברמת הטקסט, בסולם confidence של 1–3; זה אינו ציון הסתברות מכויל. המחקר מוגבל ל־Left-wing ו־Right-wing.',
        '## 3. הכותבים\n\n'+table(['כותב ומקור ביוגרפי','טקסטים לפני סינון','split','הצעות תווית'],author_rows)+'\n\nהייחוס מבוסס על byline יחיד ועמוד מחבר אצל המפרסם, כפי שנאספו בניסוי הקודם. אין בכך הוכחה להיעדר עורך או כותב צללים. לא נאספו מקורות זהות חדשים בשלב זה.',
        '## 4. חלוקת הדאטה\n\nקובצי analysis_cohort.csv, author_splits.csv ו־split_definitions.csv הועתקו ללא שינוי; hash מאמת זהות. כותבי test אינם ב־train/validation. אחרי אימות יוסרו זוגות בעלי דמיון חוצה split: cosine לפחות 0.97 או Jaccard shingles לפחות 0.7 באיזושהי גרסה. הסרה נעשית לשני הצדדים ולכל התנאים. אין להעביר כותב כדי לשפר ציון.',
        '## 5. שלושת התנאים\n\nOriginal: ללא שינוי. Paraphrase: גרסת הביקורת הקפואה מהניסוי הקודם, שביקשה לשמר סגנון ועמדה. Normalized V2: שכתוב חדש למבנה ישיר ואחיד; מותר לשנות סדר פסוקיות, פיסוק, פיצול משפטים וביטויים שאינם מעריכים. אין לשנות מסגור. Formatting נשמר לצורכי הסינון; במאמרים הקודמים היה זהה למקור.',
        '## 6. מדוע הנרמול הקודם כמעט לא שינה\n\n'+causes,
        '## 7. ה־prompt החדש ומודל היצירה\n\nQwen2.5-3B-Instruct, Q4_K_M, revision 7dabda4d13d513e3e842b20f0d435c732f172cbe; llama.cpp מקומי, b11887. משקלים קפואים, seed 20261026, temperature=0, max_tokens=320 (בקודם 240). אין תווית אמת או שם כותב במטא־דאטה הנשלח; שמות שעולים בטקסט עצמו נשארים. שינוי התקציב מתועד ולכן שינוי התוצאות אינו מזוהה כשינוי prompt בלבד. אין ניסיונות חוזרים או בחירה לפי תחזית.\n\nה־prompts המלאים לשתי הזרועות: rewrite_prompts.json. הוראת הנרמול בפועל:\n\n```text\n'+read_json(OUT/'rewrite_prompts.json')['Normalized']+'\n```',
        '## 8. כמה הסגנון השתנה\n\n'+(table(['תנאי','N','העתקים מדויקים','שינוי משמעותי לפי כלל תפעולי','ממוצע עריכת מילים'],strength) if strength else 'ממתין ליצירה.')+'\n\nword_edit_fraction הוא 1 פחות יחס SequenceMatcher על רצף מילים; הוא מדד אי־דמיון סימטרי, ולא אחוז מילים שהוחלפו מילולית. נשמרים בנפרד אחוז מילים מקוריות שהוחלפו/נמחקו ומילים שנוספו. נשמרים שינוי אורך, מספר משפטים, ממוצע מילים במשפט, מרחק פיסוק ו־66 מאפייני הסגנון הקיימים. סטנדרטיזציה רק על Original ב־train. מדד פורמליות הוא proxy מצומצם של כיווצים ומילות דיבור, ולא כלי פורמליות מתוקף. שינוי מבנה הוא proxy לפי אורכי משפטים, ללא parser תחבירי.\n\nכלל שנקבע מראש: עריכת מילים ≥15% וגם שינוי ממוצע אורך משפט ≥15%, או מרחק פיסוק ≥1 ל־100 מילים, או שינוי כיווצים ≥1 ל־100 מילים. מתחת ל־5% עריכת מילים מסומן minimal; יתר המקרים שאינם substantial מסומנים intermediate. זה אינו מוכיח סגנון אחיד או שמירת משמעות.',
        '## 9. סינון ושיעורי פסילה\n\nMPNet cosine ≥0.85; DeBERTa NLI בשני הכיוונים ≥0.6; שמירת ישויות, מספרים, שלילה, ודאות, ייחוס, anchors של מסגור, זמן עתיד וציטוטים; יחס אורך 0.6–1.65; אין קטיעת קלט או פלט. אלה בדיוק הבדיקות הקודמות. אין הקלה כדי להגדיל N.\n\n'+(table(['תנאי','נבדקו','עברו','נפסלו'],screen_rows) if screen_rows else 'ממתין לסיום הבדיקה.')+'\n\n'+(table(['תנאי','סיבה אוטומטית','מספר'],[[c,r,n] for (c,r),n in failures.most_common()]) if failures else '')+'\n\nסיבות יכולות לחפוף. כשל אוטומטי הוא דגל סיכון, לא הוכחה לשינוי משמעות. מעבר אוטומטי אינו הוכחה לשימור stance/framing.',
        '## 10. הרחבת המדגם\n\nנרמול חדש מוחל על כל 218 הטקסטים. מאחר שהפרפרזה מוחזקת קבועה ועברה קודם רק ב־120, התקרה לשלב זה היא 120 טקסטים משותפים לעומת 113 קודם. לכן לא ניתן לצפות להגדלה גדולה משינוי הנרמול לבדו. לא נאספים טקסטים/כותבים חדשים ולא משנים split. הרחבת בסיס הדאטה או שיפור שתי הזרועות דורשים גרסה נפרדת, עם תקציב שווה לשתי זרועות ה־LLM.',
        '## 11. אימות אנושי פשוט\n\nפתחו HUMAN_REVIEW_HE.md לקריאה או human_review.csv לסימון. בכל שורה מופיעים המקור, הצעת תווית, confidence, evidence ושני השכתובים. סמנו yes/no/unclear בכל שדה; claim_added/claim_omitted צריכים להיות no כדי לעבור. הזינו שם/מזהה סוקר אמיתי, תאריך ISO ותווית אנושית. Unclear הוא מותר ומוסר מהניסוי. השארת שדה ריק פירושה לא נבדק. אין למלא שם סוקר או yes באופן אוטומטי. שתי הערכות אנושיות בלתי תלויות לא בוצעו כאן.\n\nלתווית ללא הצעת AI: human_labels_blind.csv, עם מפתח נפרד. הקובץ המשולב הוא אימות בסיוע הצעה, לא הערכה עיוורת. אפשר לשמור שתי גרסאות לסוקרים, אך אין קוד המניח agreement אנושי שלא נמדד. הסקר האנושי יכול לפסול מעבר אוטומטי; אינו עוקף את הגדרות הסינון בשלב הזה.',
        '## 12. אימון, מדדים ו־seeds\n\nלאחר שכל הרשומות סומנו: MiniLM הקפוא הקיים בפרויקט וראש חדש 384→128→7, ReLU, dropout 0.3; Adam, lr 0.001, batch 16, 20 epochs. חמישה seeds: 7,42,123,2026,31415. אותה ארכיטקטורה, תקציב ומקורות בכל זרוע. checkpoint נבחר לפי validation בלבד. Macro-F1 העיקרי הוא לשתי הקטגוריות הפעילות; גם F1 לשבע יציאות נשמר. נשמרים Accuracy, Recall לכל קטגוריה, NLL ו־Brier וכל הסתברויות התחזית.\n\nנבדקות כל 9 צירופי train/test. הניתוח העיקרי משווה את האלכסון N→N מול P→P, ובנפרד N→Original לבדיקת העברה לטקסטים מקוריים. חמש חזרות אינן חמישה מדגמי test עצמאיים. בדיקות זיהוי כותב מאומנות מחדש לכל תנאי, בנפרד ל־embeddings ולמאפיינים מפורשים, עם scaler על train בלבד ובדיקת חפיפה משלהן. אלו probes על אותם כותבים בשתי המחיצות; ניסוי הנרטיב הוא author-disjoint.',
        f'## 13. ניתוח שינוי משמעותי\n\nכעת נשארו במדגם המשותף רק {len(significant_matched)} טקסטים עם שינוי משמעותי, בחלוקה {significant_splits}. אין בכך בסיס להערכת subset, אפילו לפני אפשרות לפסילות אנושיות נוספות. הקובץ substantial_automatic_subset.csv מאפשר לבדוק בדיוק אילו טקסטים נשארו.\n\nאותו כלל שנקבע מראש יוצר subset לפי Normalized בלבד; בכל השוואה נשמרות בדיוק אותן רשומות ל־Original ול־Paraphrase. אלו טקסטים שנבחרו לפי תגובה להתערבות, ולכן אינם מדגם אקראי ואינם אומדן השפעה סיבתי. אימון subset ירוץ רק אם נשארו ≥3 דוגמאות ו־≥2 כותבים מכל קטגוריה בכל split. אם לא, תירשם אי־יכולת להעריך ולא ייוצר ציון מטעה.',
        '## 14. תוצאות\n\n'+result_text+'\n\nתוצאות העבר, להקשר בלבד: Original 0.532; Paraphrase 0.590; Normalized 0.544. הן ממדגם אחר ואינן baseline ישיר למדגם V2 אם הסינון משתנה.',
        '## 15. גרפים\n\n'+('![עוצמת התערבות](plots/style_intervention.png)\n\n![סינון](plots/automatic_screen.png)\n\n![התפלגות שינוי מילים ואורכי משפטים לפני סינון](plots/style_change_distributions.png)' if measurements and validation else 'הגרפים ייווצרו לאחר יצירה/סינון; אין גרף תוצאות סיווג ללא הרצה.'),
        '## 16. דוגמאות אמיתיות\n\nשלוש הרשומות הראשונות בסדר הקלט, ובנוסף שני מקרים ראשונים מ־train שמסומנים כשינוי משמעותי (אם קיימים). הבחירה מבוססת על עוצמת שינוי צורני, לא על תוצאת מסווג. דוגמאות נבחרות אינן שיעור הצלחה, ואינן בהכרח עברו סינון משמעות.\n\n'+'\n'.join(example_rows),
        '## 17. מה ניתן להסיק\n\nאפשר למדוד עד כמה ההתערבות החדשה משנה מדדים צורניים ואילו זוגות עברו את אותו מסנן. אם השינוי משמעותי ונשמרו meaning/stance/framing באימות אנושי, אפשר יהיה לבדוק את ההשערה על התערבות אמיתית יותר. אין להכריז שיפור לפני הרצה על תוויות מאומתות.',
        '## 18. מה לא ניתן להסיק ומגבלות\n\nהמסננים אינם מוכיחים שימור נרטיב. ירידת probe אינה מוכיחה הסרת Author Style בלבד: גם תוכן קשור לכותב. גידול Macro-F1 לבדו אינו מוכיח מנגנון סגנוני. מדגם קטן, שני נרטיבים, מקור חדשותי אחד, קטעים קצרים, attribution שאינו הוכחת מחבר יחיד בפועל, תוויות AI ואימות בסיוע הצעה מגבילים הכללה. גם תוצאת אפס לא תפריך את ההשערה. אין ניסוי counterfactual נוסף ב־V2 ואין לייחס לו תוצאות כאלה מהעבר.',
        '## 19. Verdict\n\n'+verdict,
        '## 20. המשך מומלץ ושחזור\n\nראשית השלימו סימון אנושי. לאחריו הריצו evaluate ו־report לפי README. אם המדגם קטן או ההתערבות לא השתנתה מספיק, הרחיבו דאטה או בצעו השוואת generator/prompt בתקציב זהה בשתי הזרועות, בגרסה חדשה. אל תעברו ל־LoRA כדי לפצות על תוויות/התערבות לא מאומתות. audit_trail.jsonl שומר שלב, זמן UTC, hash קלט/פלט, prompt/model, seed וספים; קובצי JSON משלימים ספירות וגרסאות.'
    ]
    review_pack=OUT/'external_review_30_20261101/REVIEW_30_TRAIN_ONLY_HE.md'
    if review_pack.exists():
        sections.append('## עדכון 2026-11-01 — השלב הבא: בדיקה חיצונית של 30 דוגמאות\n\n'
            'הוכנה [חבילת בדיקה אחת לקריאה ולהעברה](external_review_30_20261101/REVIEW_30_TRAIN_ONLY_HE.md), '
            'וכן CSV מקביל באותה תיקייה. נבחרו 30 טקסטים מ־9 כותבי האימון בלבד: 10 עם שינוי משמעותי לפי proxy, '
            '10 עם שינוי מזערי שעברו סינון, ו־10 שנפסלו אוטומטית. הבחירה מתועדת ב־selection_audit.json '
            'וניתן לשחזר אותה באמצעות prepare_review.py. זהו מדגם אבחוני מכוון, לא מדגם להערכת שיעורי הצלחה.\n\n'
            'לכל רשומה נשמרו המקור, שני השכתובים, הצעת הנרטיב, confidence, כל הבדיקות האוטומטיות, '
            'סיבות המעבר/הפסילה ומדדי הסגנון. ששת השדות human_narrative_label, narrative_label_correct, '
            'paraphrase_meaning_preserved, normalized_meaning_preserved, style_change_valid, human_notes '
            'הושארו ריקים. לא בוצעו שיפוט חדש, קריאה למודל, שינוי תוויות, שינוי test/validation, הקלת סינון או אימון מחדש.\n\n'
            '**השלב הבא הוא Human Review חיצוני של 30 הדוגמאות.** רק לאחר קבלת התיוגים ותיעוד זהות הבודק '
            'יהיה אפשר להחליט על שינוי השכתוב או על אימון מחדש. בדיקה ב־ChatGPT היא בדיקת LLM חיצונית, '
            'ואינה תחליף לסוקר אנושי או ל־human gold; יש לתעד אותה בהתאם. אין לשייך בדיקה כזו לאימות האנושי שבשער האימון.')
    (OUT/'EXPERIMENT_GUIDE_HE.md').write_text('\n\n'.join(sections)+'\n',encoding='utf8')
    (OUT/'FINAL_REPORT_HE.md').write_text(intro+'\n\n'+sections[8]+'\n\n'+sections[9]+'\n\n'+sections[14]+'\n\n'+sections[18]+'\n\n'+sections[19]+'\n',encoding='utf8')
    # Documentation-only import: external machine ratings never enter human labels.
    if (OUT/'external_llm_review_20261101/summary.json').exists():
        import subprocess
        subprocess.run([sys.executable,str(OUT/'external_llm_review_20261101/update_docs.py')],check=True)
    if measurements and validation:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        (OUT/'plots').mkdir(exist_ok=True)
        labels=[r[0] for r in strength]
        fig,ax=plt.subplots(figsize=(8,4)); ax.bar(labels,[r[3]/r[1] for r in strength]);ax.set(title='Substantial style intervention (predefined proxy)',ylabel='Fraction of 218 source texts',ylim=(0,1));fig.tight_layout();fig.savefig(OUT/'plots/style_intervention.png',dpi=160);plt.close(fig)
        fig,ax=plt.subplots(figsize=(7,4));ax.bar([r[0] for r in screen_rows],[r[2] for r in screen_rows]);ax.set(title='Unchanged automatic meaning screen: accepted versions',ylabel='Accepted source texts',ylim=(0,218));fig.tight_layout();fig.savefig(OUT/'plots/automatic_screen.png',dpi=160);plt.close(fig)
        conditions=['Previous_Normalized','Paraphrase','Normalized']
        fig,axes=plt.subplots(1,2,figsize=(12,4))
        for ax,metric,title in zip(axes,['word_edit_fraction','sentence_mean_relative_change'],['Word-sequence edit (%)','Relative mean sentence-length change (%)']):
            ax.boxplot([[100*float(m[metric]) for m in measurements if m['condition']==c] for c in conditions],tick_labels=['Previous N','Paraphrase','New N'],showmeans=True)
            ax.set(title=title,ylabel='Percent; 218 same source texts per condition')
        fig.suptitle('Intervention strength before automatic/human screening');fig.tight_layout();fig.savefig(OUT/'plots/style_change_distributions.png',dpi=160);plt.close(fig)
    from study import write_csv
    write_csv('cohort_audit.csv',[dict(row_id=r['row_id'],author=r['author'],split=r['split'],proposed_narrative=r['narrative_name'],
        normalized_substantial_style=r['row_id'] in substantial_ids,normalized_auto_pass=r['row_id'] in normalized_pass,
        all_conditions_auto_pass=r['row_id'] in matched_ids,human_validation_complete=False if complete==0 else 'see human_review.csv') for r in corpus])
    protected=read_json(OUT/'protected_previous_sha256.json')
    changed=[name for name,digest in protected.items() if not (OUT.parents[2]/name).exists() or sha(OUT.parents[2]/name)!=digest]
    write_json('previous_outputs_integrity.json',dict(checked=len(protected),changed=changed,passed=not changed))
    assert not changed,changed
    inherited=read_json(PREVIOUS/'protected_inputs_sha256.json')
    changed_original=[name for name,digest in inherited.items() if not (OUT.parents[2]/name).exists() or sha(OUT.parents[2]/name)!=digest]
    write_json('original_inputs_integrity.json',dict(checked=len(inherited),changed=changed_original,passed=not changed_original,
        scope='Raw data, original checkpoint and old pilot artifacts protected by predecessor snapshot'))
    assert not changed_original,changed_original
    event('report',[OUT/'protocol.json'],[OUT/'EXPERIMENT_GUIDE_HE.md',OUT/'FINAL_REPORT_HE.md',OUT/'STATUS.json'],218,len(automatic),human_complete=complete)
    print(json.dumps(status,ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
    revision_docs = OUT/'train_prompt_revision_30_20261101/update_docs.py'
    if revision_docs.exists():
        import subprocess
        subprocess.run([sys.executable,str(revision_docs)],check=True)

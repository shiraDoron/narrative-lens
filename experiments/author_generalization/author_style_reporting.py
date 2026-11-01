"""Generate readable result tables without treating automatic screens as human gold."""
import json
from pathlib import Path
import numpy as np
import pandas as pd


def table(df):
    if df.empty:
        return 'אין תוצאות הניתנות לאמידה בקבוצה זו.'
    df = df.copy()
    for c in df.select_dtypes(include='number'):
        integer = pd.api.types.is_integer_dtype(df[c])
        df[c] = df[c].map(lambda x: (str(int(x)) if integer else f'{x:.4f}') if pd.notna(x) else '')
    def cell(x):
        return str(x).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(map(cell, df.columns)) + ' |',
                      '| ' + ' | '.join(['---'] * len(df.columns)) + ' |'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in df.to_numpy()])


def build(out):
    out = Path(out)
    load = lambda name: pd.read_csv(out / name)
    baseline = pd.DataFrame(json.loads((out / 'baseline_metrics.json').read_text(encoding='utf-8')))
    m = load('metrics_summary.csv')
    agg = load('metrics_aggregated.csv')
    x = load('analysis_cohort.csv')
    v = load('rewrite_validation.csv')
    v['passed'] = v.passed.astype(str).str.lower().eq('true')
    v['changed_text'] = v.changed_text.astype(str).str.lower().eq('true')
    v['raw_text_changed'] = v.raw_text_changed.astype(str).str.lower().eq('true')
    failures = v.groupby('condition').agg(n=('passed','size'), accepted=('passed','sum'),
                  canonical_word_change_fraction=('changed_text','mean'),raw_change_fraction=('raw_text_changed','mean')).reset_index()
    failures['failure_rate'] = 1 - failures.accepted / failures.n
    failures.to_csv(out / 'validation_summary.csv', index=False, encoding='utf-8-sig')
    records=[json.loads(line) for line in (out/'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
    pairs=pd.DataFrame(records)[['row_id','condition','original','rewrite']].merge(v,on=['row_id','condition'])
    examples=pairs[pairs.condition.isin(['Paraphrase','Normalized'])].sort_values(['condition','row_id']).groupby(['condition','passed']).head(2)
    examples.to_csv(out/'rewrite_validation_examples.csv',index=False,encoding='utf-8-sig')
    review=pairs[pairs.condition.isin(['Paraphrase','Normalized'])].merge(x[['row_id','narrative_name']],on='row_id')
    review=review.sort_values('row_id').groupby(['condition','narrative_name','passed']).head(1).sample(frac=1,random_state=20261026).reset_index(drop=True)
    review['review_id']=[f'blind_{i+1:03d}' for i in range(len(review))]
    review[['review_id','row_id','condition','narrative_name','passed']].to_csv(out/'human_review_key.csv',index=False,encoding='utf-8-sig')
    blind=review[['review_id','original','rewrite']].copy()
    for c in ['facts_preserved','entities_preserved','claims_preserved','stance_preserved','framing_preserved',
              'negation_preserved','certainty_preserved','attribution_preserved','style_changed','acceptable','reviewer_notes']:
        blind[c]=''
    blind.to_csv(out/'human_review_blind_queue.csv',index=False,encoding='utf-8-sig')
    reasons = v.rejection_reasons.fillna('').str.split('|').explode()
    reasons[reasons.ne('')].value_counts().rename_axis('reason').reset_index(name='count').to_csv(
        out / 'validation_rejection_reason_counts.csv', index=False, encoding='utf-8-sig')
    probes = load('author_probe_results.csv')
    pa = probes.groupby(['cohort','representation','condition']).agg(
        accuracy_mean=('accuracy','mean'), macro_f1_mean=('macro_f1','mean'),
        narrative_groups=('narrative','nunique'), n_test=('n_test','sum'),
        uniform_chance_accuracy=('balanced_chance','mean')).reset_index()
    pa.to_csv(out / 'author_probe_aggregated.csv', index=False, encoding='utf-8-sig')
    cf = load('counterfactual_results.csv')
    cf['passed_semantic_preservation_screen'] = cf.passed_semantic_preservation_screen.astype(str).str.lower().eq('true')
    cf['after_normalization'] = cf.after_normalization.astype(str).str.lower().eq('true')
    cf_summary = []
    for scope, d in [('all_generated_descriptive',cf), ('automated_pass_only',cf[cf.passed_semantic_preservation_screen])]:
        for after, g in d.groupby('after_normalization'):
            cf_summary.append({'scope':scope,'after_normalization':after,'n_source_texts':g.row_id.nunique(),
                'n_predictions_including_seeds':len(g),'label_flip_rate':g.label_flip.mean(),
                'correct_to_incorrect_rate':g.correct_to_incorrect.mean(),
                'incorrect_to_correct_rate':g.incorrect_to_correct.mean(),
                'mean_max_probability_delta':g.max_probability_delta.mean(),
                'mean_true_probability_delta':g.true_probability_delta.mean()})
    cs = pd.DataFrame(cf_summary)
    cs.to_csv(out/'counterfactual_summary.csv', index=False, encoding='utf-8-sig')
    consistency = []
    for (after, seed, rid), g in cf.groupby(['after_normalization','seed','row_id']):
        consistency.append({'after_normalization':after,'seed':seed,'row_id':rid,
            'n_targets':len(g),'all_four_targets_present':len(g)==4,
            'all_targets_passed':bool(g.passed_semantic_preservation_screen.all()),
            'target_label_consistency':g.variant_label.nunique()==1,
            'original_plus_target_consistency':not g.label_flip.any()})
    consistency = pd.DataFrame(consistency)
    consistency.to_csv(out/'counterfactual_consistency.csv', index=False, encoding='utf-8-sig')
    # Fair before/after comparison requires all four variants and both chains to pass.
    eligible = consistency[consistency.all_four_targets_present & consistency.all_targets_passed]
    paired_ids = eligible.groupby(['seed','row_id']).filter(lambda g: g.after_normalization.nunique()==2)
    paired_keys = set(zip(paired_ids.seed, paired_ids.row_id))
    matched_cf = cf[[ (s,r) in paired_keys for s,r in zip(cf.seed,cf.row_id) ]]
    matched_cf.to_csv(out/'counterfactual_matched_before_after.csv', index=False, encoding='utf-8-sig')
    consistency_summary=[]
    for scope,g in [('all_generated_descriptive',consistency),('all_four_targets_automated_pass',eligible),
                    ('matched_before_after_automated_pass',paired_ids)]:
        for after,h in g.groupby('after_normalization'):
            consistency_summary.append({'scope':scope,'after_normalization':after,'n_source_texts':h.row_id.nunique(),
                'n_groups_including_seeds':len(h),'narrative_consistency_rate':h.target_label_consistency.mean(),
                'original_plus_variants_consistency_rate':h.original_plus_target_consistency.mean()})
    consistency_summary=pd.DataFrame(consistency_summary)
    consistency_summary.to_csv(out/'counterfactual_consistency_summary.csv',index=False,encoding='utf-8-sig')
    contrast = load('stance_change_control_results.csv')
    # Probability calibration is descriptive: these labels are source proxies.
    pred = load('fixed_and_retrained_predictions.csv')
    calibration = []
    for keys, g in pred.groupby(['scope','seed','train_condition','test_condition']):
        correct = (g.true_label == g.predicted_label).to_numpy()
        confidence = g.max_probability.to_numpy()
        bins = np.minimum((confidence*10).astype(int),9)
        ece = sum(np.mean(bins==b)*abs(correct[bins==b].mean()-confidence[bins==b].mean())
                  for b in range(10) if (bins==b).any())
        calibration.append(dict(zip(['scope','seed','train_condition','test_condition'],keys), ece_10bin=ece))
    pd.DataFrame(calibration).to_csv(out/'calibration_metrics.csv', index=False, encoding='utf-8-sig')
    info = json.loads((out/'evaluation_complete.json').read_text(encoding='utf-8'))
    primary = agg[agg.scope.eq('retrain_matched_automated_pass')]
    descriptive = agg[agg.scope.eq('retrain_all_generated_descriptive')]
    probe_text=[]
    for (cohort,representation),g in pa.groupby(['cohort','representation']):
        scores=g.set_index('condition').accuracy_mean
        if {'Original','Paraphrase','Normalized'}.issubset(scores.index):
            probe_text.append(f'{cohort}, {representation}: Original={scores.Original:.4f}, '
                f'Paraphrase={scores.Paraphrase:.4f}, Normalized={scores.Normalized:.4f}; '
                f'Normalized−Original={scores.Normalized-scores.Original:+.4f}, '
                f'Normalized−Paraphrase={scores.Normalized-scores.Paraphrase:+.4f}.')
    probe_verdict=' '.join(probe_text)
    generalization_verdict='לא ניתן לאמוד שיפור מבוקר מלא: לא שרדה נציגות לכל המחלקות בכל החלוקות.'
    advantage_verdict='לא ניתן לקבוע יתרון על פרפרזה רגילה בקבוצה מבוקרת מלאה.'
    if info['primary_comparison_estimable']:
        scores=primary.set_index(['train_condition','test_condition']).macro_f1_mean
        original=scores.loc[('Original','Original')]
        normalized=scores.loc[('Normalized','Normalized')]
        paraphrase=scores.loc[('Paraphrase','Paraphrase')]
        generalization_verdict=(f'{"נמדד שיפור מספרי" if normalized>original else "לא נמדד שיפור מספרי"} '
            f'בהשוואה המשותפת: Original→Original={original:.4f}, Normalized→Normalized={normalized:.4f}, '
            f'הפרש={normalized-original:+.4f}. הבדל זה כפוף לסינון אוטומטי ולמגבלות המדגם; לא נקבעה מובהקות.')
        advantage_verdict=(f'{"נמדד יתרון מספרי" if normalized>paraphrase else "לא נמדד יתרון מספרי"} '
            f'מול Paraphrase→Paraphrase={paraphrase:.4f}; Normalized−Paraphrase={normalized-paraphrase:+.4f}. '
            'אין להסיק ממנו לבדו שהוסר Author Style.')
    accepted_cf=cf[cf.passed_semantic_preservation_screen & ~cf.after_normalization]
    verdict={
        'baseline_macro_f1_mean':float(baseline.macro_f1.mean()),
        'baseline_macro_f1_sd':float(baseline.macro_f1.std()),
        'baseline_accuracy_mean':float(baseline.accuracy.mean()),
        'primary_comparison_estimable':bool(info['primary_comparison_estimable']),
        'matched_rows':info['matched_rows'],'matched_test_rows':info['matched_test_rows'],
        'author_probe_aggregates':pa.to_dict('records'),
        'counterfactual_aggregates':cs.to_dict('records'),
        'counterfactual_consistency':consistency_summary.to_dict('records'),
        'matched_counterfactual_source_texts':int(matched_cf.row_id.nunique()) if len(matched_cf) else 0,
        'auto_screened_style_flip_rate':float(accepted_cf.label_flip.mean()) if len(accepted_cf) else None,
        'auto_screened_style_source_texts':int(accepted_cf.row_id.nunique()),
        'primary_retraining_results':primary.to_dict('records'),
        'descriptive_retraining_results':descriptive.to_dict('records'),
        'causality_established':False,'human_semantic_validation_performed':False,
        'independent_new_narrative_gold_for_stance_control':False,
        'identity_unit':'source account, not confirmed human writer',
        'lora_dora_justified_by_this_run':False,'prompting_sufficiency':'not established'}
    (out/'verdict.json').write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cf_verdict=(f'בגרסאות שעברו סינון אוטומטי לפני נרמול נמדד flip rate של '
                f'{accepted_cf.label_flip.mean():.4f} על {accepted_cf.row_id.nunique()} טקסטי מקור; '
                'זו רגישות נצפית תחת סינון אוטומטי, ללא אישור אנושי לשינוי סגנון בלבד.'
                if len(accepted_cf) else 'לא שרדו גרסאות סגנון מאומתות אוטומטית שמאפשרות לאמוד רגישות סגנונית.')
    paired_seed_rows=[]
    for scope,g in m.groupby('scope'):
        diagonal=g[g.train_condition.eq(g.test_condition)]
        pivot=diagonal.pivot(index='seed',columns='train_condition',values='macro_f1')
        if {'Original','Paraphrase','Normalized'}.issubset(pivot.columns):
            for s,row in pivot.iterrows():
                paired_seed_rows.append({'scope':scope,'seed':s,
                    'normalized_minus_original':row.Normalized-row.Original,
                    'paraphrase_minus_original':row.Paraphrase-row.Original,
                    'normalized_minus_paraphrase':row.Normalized-row.Paraphrase})
    pd.DataFrame(paired_seed_rows,columns=['scope','seed','normalized_minus_original',
        'paraphrase_minus_original','normalized_minus_paraphrase']).to_csv(out/'paired_seed_comparisons.csv',index=False,encoding='utf-8-sig')
    fixed = m[m.scope.eq('fixed_all_generated_descriptive')].groupby('test_condition').agg(
        macro_f1_mean=('macro_f1','mean'), macro_f1_sd=('macro_f1','std'),
        flip_rate=('label_flip_rate','mean'), correct_to_incorrect=('correct_to_incorrect','mean'),
        incorrect_to_correct=('incorrect_to_correct','mean'),
        true_probability_delta=('true_probability_delta','mean')).reset_index()
    fixed.to_csv(out/'fixed_classifier_summary.csv', index=False, encoding='utf-8-sig')
    fixed_matched=m[m.scope.eq('fixed_matched_paraphrase_normalized')].groupby('test_condition').agg(
        macro_f1_mean=('macro_f1','mean'),macro_f1_sd=('macro_f1','std'),n_test=('n','first'),
        label_flip_rate=('label_flip_rate','mean'),correct_to_incorrect=('correct_to_incorrect','mean'),
        incorrect_to_correct=('incorrect_to_correct','mean'),true_probability_delta=('true_probability_delta','mean')).reset_index()
    fixed_matched.to_csv(out/'fixed_classifier_matched_summary.csv',index=False,encoding='utf-8-sig')
    cols = ['train_condition','test_condition','macro_f1_mean','macro_f1_std','accuracy_mean']
    bm, bs = baseline.macro_f1.mean(), baseline.macro_f1.std()
    am, ast = baseline.accuracy.mean(), baseline.accuracy.std()
    recalls = baseline.filter(like='recall_').mean().rename_axis('Narrative').reset_index(name='Recall')
    recalls.Narrative = recalls.Narrative.str.removeprefix('recall_')
    original_n = len(load('split_definitions.csv'))
    cohort_counts=json.loads((out/'retraining_cohort_status.json').read_text(encoding='utf-8'))
    matched_counts=cohort_counts['matched_automated_pass']['counts']
    totals={k:sum(value) for k,value in matched_counts.items()}
    baseline_accounting=pd.DataFrame([
        {'comparison':'Full original baseline','train':168,'validation':84,'test':84,'Original Macro-F1':bm},
        {'comparison':'Frozen full-trained model on accepted C/D texts','train':168,'validation':84,
         'test':info['matched_test_rows'],'Original Macro-F1':float(fixed_matched.loc[fixed_matched.test_condition.eq('Original'),'macro_f1_mean'].iloc[0]) if len(fixed_matched) else np.nan},
        {'comparison':'Matched retraining: same source rows for O/P/N','train':totals['train'],'validation':totals['val'],
         'test':totals['test'],'Original Macro-F1':original if info['primary_comparison_estimable'] else np.nan}])
    primary_seed=m[m.scope.eq('retrain_matched_automated_pass') & m.train_condition.eq(m.test_condition)].pivot(index='seed',columns='train_condition',values='macro_f1')
    overview=[]
    if info['primary_comparison_estimable']:
        overview.append(f'בהשוואת האימון מחדש על אותן רשומות, Original→Original={original:.4f}, '
            f'Normalized→Normalized={normalized:.4f}, Paraphrase→Paraphrase={paraphrase:.4f}. '
            f'Normalized−Original={normalized-original:+.4f}; Normalized−Paraphrase={normalized-paraphrase:+.4f}. '
            f'הנרמול היה נמוך מהמקור ב־{int((primary_seed.Normalized<primary_seed.Original).sum())} מתוך {len(primary_seed)} seeds, '
            f'וגבוה מפרפרזה ב־{int((primary_seed.Normalized>primary_seed.Paraphrase).sum())} מתוך {len(primary_seed)} seeds.')
        overview.append(f'כאשר טקסטי הבדיקה נשארים Original: Original→Original={original:.4f}, '
            f'Paraphrase→Original={scores.loc[("Paraphrase","Original")]:.4f}, '
            f'Normalized→Original={scores.loc[("Normalized","Original")]:.4f}. '
            'זהו שינוי קטן במדגם קטן; לא נקבעה מובהקות, והיתרון האפשרי אינו עקבי בין כל מדדי הביצוע והתנאים.')
    overview.append(f'לאחר סינון נשארו {totals["train"]} דוגמאות אימון, {totals["val"]} אימות ו־{totals["test"]} בדיקה, '
        'עם ייצוג לא אחיד למחלקות. אין להשוות את ציון המקור בקבוצה זו ישירות ל־baseline המלא: זו קבוצת אימון ובדיקה שונה.')
    if len(matched_cf):
        overview.append(f'ב־Counterfactual המזווג שעבר סינון בשני השלבים נשארו {matched_cf.row_id.nunique()} טקסטי מקור; '
            f'שיעור flip לפני נרמול={matched_cf.loc[~matched_cf.after_normalization,"label_flip"].mean():.4f}, '
            f'ואחריו={matched_cf.loc[matched_cf.after_normalization,"label_flip"].mean():.4f}. '
            'לא הודגם שיפור ביציבות; המדגם קטן ואינו שולל shortcut שלא הופעל בהתערבות הזו.')
    verdict['overall_harmful_shortcut_support']='Insufficient evidence in this pilot; not evidence of absence.'
    verdict['primary_normalized_minus_original']=float(normalized-original) if info['primary_comparison_estimable'] else None
    verdict['primary_normalized_minus_paraphrase']=float(normalized-paraphrase) if info['primary_comparison_estimable'] else None
    verdict['matched_training_validation_test_counts']=totals
    (out/'verdict.json').write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sections = [
        '# ניסוי Author Style: דוח תוצאות בפועל',
        '## תקציר התוצאות',
        '\n\n'.join(overview),
        'מקורות המספרים: [תוצאות לפי תנאי](metrics_aggregated.csv), '
        '[הרכב קבוצות האימון והבדיקה](retraining_cohort_status.json), '
        '[בדיקת זיהוי כותב](author_probe_aggregated.csv), '
        '[עקביות Counterfactual](counterfactual_consistency_summary.csv).',
        '**המסקנה בפיילוט הזה: אין תמיכה מספקת בטענה שנרמול הסגנון מסיר shortcut מזיק ומשפר הכללה.** '
        'הירידה בזיהוי כותב במאפייני פני שטח בקבוצה המסוננת זהה לירידה בפרפרזה רגילה, וב־embedding לא נמדדה ירידה. '
        'נמצא יתרון ממוצע קטן של Normalized על Paraphrase במבחן N→N מול P→P, אך לא שיפור מול Original→Original. '
        'זו אינה הוכחה שאין shortcut: המדגם קטן, הסינון אוטומטי ותוויות המקור אינן gold סמנטי עצמאי.',
        '## 1. מה בוצע',
        f'בוצע פיילוט חישובי מקומי: {original_n} טקסטים שנדגמו מראש, {x.author.nunique()} מזהי כותבים/חשבונות, '
        f'{len(x)} טקסטים לאחר ביקורת דמיון סמנטי של המקור. החלוקה היא 14 חשבונות אימון, 7 חשבונות אימות ו־7 חשבונות בדיקה; '
        '12 טקסטים לכל כותב לפני סינונים, ובכל קבוצת בדיקה כותב אחד מכל נרטיב. נבחרו טקסטים באנגלית באורך 20–65 מילים. '
        'זהו תת־מדגם מהדאטה הקיים, ולא הרצה על כל הפרויקט.',
        'נשמרו החלוקה, מזהי הרשומות וחתימות קובצי המקור. בוצעה ביקורת כפילויות כללית לפני הדגימה, '
        'וכן בדיקת דמיון סמנטי בין החלוקות לפני אימון וביקורת כפילויות שנוצרו בעקבות שכתוב. '
        'קבוצות דומות הוצאו באופן סימטרי. ספי הדמיון הם הגדרה תפעולית; הם אינם הוכחה שאין אף פרפרזה סמויה.',
        '**יחידת הזהות היא חשבון מקור:** ה־split מפריד מזהי חשבונות לאחר איחוד הבדלי אותיות רישיות ו־@. '
        'אין בדאטה זיהוי מלא של הכותב האנושי לכל פרסום, ורבים מהחשבונות הם ארגונים. לכן זהו account-disjoint proxy '
        'ל־author-disjoint; לא ניתן להבטיח שאותו עורך אנושי לא כתב עבור שני חשבונות.',
        'נעשה שימוש במקודד ובארכיטקטורת SBERT-only הקיימים: MiniLM קפוא, ראש MLP עם 128 יחידות ו־dropout 0.3. '
        'ראש הסיווג אומן מחדש על כותבי האימון בלבד. בכל תנאי נשמרו אותם פרמטרים, 20 epochs ושלושה seeds: 42, 7, 123. '
        'בחירת checkpoint התבססה רק על Macro-F1 של כותבי האימות. תחזיות ה־checkpoint הישן נשמרו בנפרד כנתון תיאורי '
        'שאינו author-disjoint. קובצי המקור והמודל המקורי לא הוחלפו.',
        'נוצרו Original, Formatting באמצעות הפונקציה הקיימת, Paraphrase המשמר סגנון לפי ההנחיה, '
        'ו־Normalized לסגנון כתוב אחיד. השכתובים נעשו ב־Qwen2.5-0.5B-Instruct מקומי, בגרסת GGUF Q8_0 רשמית מקובעת, '
        'באמצעות llama.cpp ובפענוח דטרמיניסטי. המשקלים מכומתים, וכל הפלטים לניתוח נוצרו באותו מנוע. '
        'זהו מודל קטן שנבחר למשאבי CPU; אין כאן API מסחרי או אימון LoRA. שם הכותב ותווית הנרטיב לא נשלחו כמידע נלווה. '
        'ישויות שהופיעו בטקסט עצמו נשארו בטקסט.',
        'מקורות הכלים: [כרטיס מודל Qwen הרשמי](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF), '
        '[תיעוד שרת llama.cpp](https://github.com/ggml-org/llama.cpp/blob/b11887/tools/server/README.md). '
        'גרסאות וחתימות המשקלים והמנוע שנעשה בהם שימוש בפועל מתועדות ב־llama_runtime_manifest.json.',
        'בוצעו סינון באמצעות דמיון MPNet במקודד נפרד ממקודד מסווג הנרטיבים, הסקה דו־כיוונית במודל DeBERTa NLI, חילוץ ישויות ב־BERT NER, '
        'ובדיקות שמרניות של מספרים, שלילה, ודאות, ייחוס ומילות מסגור. אין כאן תיוג אנושי עצמאי של שימור עמדה ומסגור; '
        'עבר/נפסל פירושו עבר/נפסל בסינון האוטומטי בלבד. לא נבחר שכתוב על סמך תחזית מסווג הנרטיבים.',
        'בוצעו מבחן מסווג קבוע, אימון מחדש בשלוש זרועות ומטריצת בדיקות ביניהן, זיהוי כותב שהותאם מחדש בכל ייצוג, '
        'ארבעה יעדי סגנון זהים לכל טקסט בקבוצת הנגד, נרמול נוסף של כל יעד, וניסיון לשינוי עמדה כביקורת חיובית. '
        'במטריצת האימון נשמרה אותה קבוצת רשומות בכל התנאים. אם הסינון הסיר מחלקה מאימון/אימות/בדיקה, '
        'השוואת שבע המחלקות בקבוצה המסוננת סומנה כבלתי ניתנת לאמידה.',
        '## 2. מה התקבל',
        f'Baseline על כותבים שלא נראו: Macro-F1 **{bm:.4f} ± {bs:.4f}**, Accuracy **{am:.4f} ± {ast:.4f}**. '
        'סטיית התקן משקפת שונות בין seeds באותה חלוקת כותבים, ולא אי־ודאות לגבי אוכלוסיית הכותבים.',
        table(recalls),
        '### מדוע יש שלושה ציוני Original שונים?',table(baseline_accounting),
        'הבדלים בין שורות הטבלה נובעים גם מכמות דוגמאות האימון ומהרכב קבוצת הבדיקה; הם אינם אומדן להשפעת נרמול. '
        'את השפעת התנאי משווים בתוך אותה שורה וקבוצה בלבד.',
        '### תקינות השכתובים', table(failures),
        'canonical_word_change_fraction משווה רצף מילים לאחר הסרת קישורים, אזכורים, אותיות רישיות וסימני פיסוק; '
        'raw_change_fraction משווה מחרוזות ללא ניקוי. אף אחד מהמדדים אינו הוכחה לנרמול סגנון מוצלח. '
        'גם העתקה של המקור יכולה לעבור סינון משמעות בלי לבצע את ההתערבות הרצויה.',
        f'לקבוצה המשותפת שבה Paraphrase ו־Normalized עברו את הסינון ונשמרה הפרדת כפילויות נכנסו '
        f'**{info["matched_rows"]}** טקסטים, מהם **{info["matched_test_rows"]}** בבדיקה. '
        f'השוואה מלאה עם נציגות לכל שבע המחלקות בכל החלוקות: **{info["primary_comparison_estimable"]}**.',
        f'בהשוואת המסווג הקבוע על כל ארבע הזרועות נדרשת גם קבלה של Formatting; נשארו '
        f'{info["fixed_four_way_matched_test_rows"]} טקסטי בדיקה. ההשוואה המרכזית C מול D משתמשת בקבוצה המשותפת C/D.',
        '### מסווג קבוע: קבוצת C/D המשותפת שעברה סינון אוטומטי',table(fixed_matched),
        '### מסווג קבוע: כל הפלטים, כולל שכתובים שנפסלו', table(fixed),
        'השינוי בהסתברות הוא שינוי ממוצע בהסתברות תווית המקור. Flip אינו מוכיח שינוי סגנון בלבד כאשר השכתוב נפסל.',
        '### אימון מחדש: הקבוצה המשותפת שעברה סינון', table(primary[cols]),
        '### אימון מחדש: תוצאות תיאוריות הכוללות שכתובים שנפסלו', table(descriptive[cols]),
        'אין לפרש שיפור בקבוצה התיאורית כתועלת מהסרת סגנון: שינוי תוכן, עמדה או מילות מפתח יכול להסביר אותו.',
        '### זיהוי כותב', table(pa),
        'הממוצעים חושבו בשקלול שווה של קבוצות הנרטיב. בכל קבוצה אומן מסווג כותבים חדש על אותם כותבים ועל טקסטים נפרדים '
        'לכל אחד מהייצוגים; זו אינה העברה ממסווג שאומן על Original. המבחן בתוך נרטיב מצמצם את השפעת תווית הנרטיב, '
        'אך נושא, ישויות ותוכן אישי עדיין עלולים לשמש לזיהוי. לכן ירידה ביכולת הזיהוי אינה הוכחה שהוסר דווקא סגנון.',
        'ה־probe הוא LogisticRegression לינארי עם StandardScaler המותאם לנתוני האימון בלבד בכל תנאי. '
        'ירידה בדיוק של probe לינארי אינה הוכחה שמידע הכותב נמחק מכל ייצוג אפשרי או שלא ניתן לחלץ אותו במסווג חזק יותר.',
        'הכינוי Style-preserving Paraphrase מתאר את ההנחיה למחולל, ולא תוצאה מאומתת של שימור סגנון אישי. '
        'surface_style_measurements.csv מכיל מדדי אורך, פיסוק ואותיות רישיות לכל ארבע הזרועות; '
        'הם אינם מכסים את כל ממדי הסגנון. נדרשת בדיקה אנושית גם לכך שזרוע הביקורת אכן משמרת סגנון ושהנרמול אכן מאחד אותו.',
        'גם אי־ירידה בזיהוי כותב מתוך embedding אינה מוכיחה שנשמר הסגנון: ישויות ונושאים שנשמרו כדין יכולים לזהות חשבון. '
        'התאמה לפי אותה תווית נרטיב אינה התאמה לפי אותו אירוע או אותו תוכן.',
        '### Counterfactual style', table(cs),
        table(consistency_summary),
        'narrative_consistency_rate הוא שיעור קבוצות המקור שבהן כל ארבעת יעדי הסגנון קיבלו אותה תחזית. '
        'original_plus_variants_consistency_rate דורש גם התאמה לתחזית על טקסט המקור. מספר הקבוצות כולל seeds ואינו מספר טקסטים בלתי תלויים.',
        f'מספר טקסטי מקור עם כל ארבעת היעדים שעברו סינון גם לפני וגם אחרי הנרמול: '
        f'**{matched_cf.row_id.nunique() if len(matched_cf) else 0}**. '
        'קובץ counterfactual_consistency.csv מציג עקביות לכל טקסט, seed ושלב. שיעורי flip בשורות שונות של הטבלה '
        'אינם השוואה מזווגת אם קבוצות הקבלה שונות; ההשוואה המשותפת שמורה בקובץ counterfactual_matched_before_after.csv.',
        f'ביקורת שינוי עמדה: נוצרו {contrast.row_id.nunique()} טקסטים; שיעור שינוי התחזית בממוצע על פני seeds היה '
        f'{contrast.label_flip.mean():.4f}. לא נקבעה תווית נרטיב חדשה באופן עצמאי ולא אושר אנושית שהעמדה אכן הוחלפה. '
        'לכן זו בדיקת תגובתיות לניסיון שינוי, ולא הוכחה לרגישות נכונה לשינוי נרטיב. אין לחשב accuracy מול התווית הישנה.',
        '## 3. מה ניתן להסיק',
        'ההרצה מודדת התנהגות בפועל של הצינור, וכוללת ביקורת לעצם השכתוב באמצעות LLM. '
        'תוצאות הפיילוט מאפשרות לזהות בעיות שימור משמעות ולתאר רגישות לטרנספורמציות. '
        'רק השוואה מזווגת בין שכתובים תקינים יכולה לתמוך בפרשנות סגנונית, וגם אז נדרשת בדיקה אנושית של העמדה והמסגור.',
        'בפיילוט לכל חשבון יש תווית מקור נרטיבית אחת. לכן הקשר בין חשבון לתווית מובנה בדאטה. '
        'קורלציה זו לבדה אינה מוכיחה כשל בזיהוי הנרטיב של הטקסט; לטענה כזו נדרש תיוג סמנטי שאינו נקבע לפי זהות המקור.',
        '## 4. מה לא ניתן להסיק',
        'לא הוכחה סיבתיות. אין בסיס להמיר שינוי בתחזית על שכתוב בעל תוכן שונה לראיה על Author Style. '
        'Confidence גבוה יותר אינו בהכרח שיפור; נשמרו גם NLL, Brier ו־ECE. אין לטעון למובהקות בין תנאים '
        'על בסיס שלושה seeds בלבד, ואין כאן ניסוי בלתי תלוי על חלוקות רבות של כותבים.',
        'היעדר שיפור אינו מוכיח שהמודל אינו משתמש ב־shortcut. אם המחולל לא שינה בפועל את הסגנון, '
        'או לא הפחית את מידע הכותב בלי לפגוע בתוכן, ההתערבות אינה מבחן מספק להשערה.',
        '## 5. מגבלות',
        'התוויות הן שיוך נרטיבי של חשבונות, ולא gold ברמת כל טקסט; חשבון אינו תמיד אדם יחיד; '
        'נבדקה אנגלית בלבד; המדגם קטן וקצר; נבדק כותב אחד לכל מחלקה בבדיקה; הכותבים כבר נחקרו בעבר בפרויקט; '
        'המחולל קטן; אין אימות אנושי; סינון לקסיקלי עלול לפסול פרפרזה תקינה או להחמיץ שינוי סוכנות ומסגור; '
        'NLI ו־similarity הם כלי סינון ולא הוכחת שימור משמעות. ירידה בזיהוי כותב יכולה לנבוע גם מאובדן תוכן.',
        'נשמר human_review_blind_queue.csv לבדיקת זוגות מקור–שכתוב ללא תנאי, שם כותב, תווית או תחזית מסווג. '
        'מפתח נפרד נמצא ב־human_review_key.csv. העמודות למילוי ריקות: **לא בוצע תיוג אנושי**. '
        'זו דגימת ביקורת משכבת לפי תנאי, נרטיב ותוצאת סינון; היא אינה מדגם מקרי לאמידת שיעור השימור באוכלוסייה.',
        '## 6. Verdict',
        '• **רגישות ל־Author Style:** שינויי תחזיות נמדדו, אך ייחוסם לסגנון בלבד מותנה בשימור משמעות ועמדה; '
        'הסינון האוטומטי לבדו אינו מספיק לקביעה סיבתית. '+cf_verdict,
        '• **ירידה בזיהוי כותב:** המספרים נמדדו במסווגים שהותאמו מחדש ומוצגים בטבלה. '
        'יש לפרש הבדל בקבוצה המסוננת בנפרד מהבדל הכולל שכתובים שנפסלו. '+probe_verdict,
        '• **שיפור על unseen authors מעבר לפרפרזה:** '
        + generalization_verdict+' '+advantage_verdict,
        '• **LoRA/DoRA:** אין כרגע הצדקה מחקרית למעבר על סמך פיילוט זה. גם לא הוכח שה־prompting הנוכחי מספיק. '
        'הצעד הבא הוא מחולל איכותי יותר ואימות אנושי עיוור של שכתובים, לפני הגדלת המדגם ואימון נוסף.',
        '## קבצים ושחזור',
        'ראו README.md, config.json, prompts.json ו־generator_revision.json. split_definitions.csv ו־author_splits.csv '
        'מכילים את החלוקה; text_variants.csv מכיל את ארבע הגרסאות; generated_rewrites.jsonl מכיל גם את ביקורות הנגד; '
        'rewrite_validation.csv כולל ציון, החלטה וסיבות פסילה לכל שכתוב; metrics_summary.csv כולל תוצאות לכל seed; '
        'per_author_metrics.csv כולל תוצאות לכל כותב; checkpoints/ מכיל רק את ראשי המודלים החדשים. '
        'לא נדרס המודל המקורי. משקלי המחולל והמנוע המקומיים ב־runtime_llama/ ומשקלי ניסיונות ההיתכנות ב־runtime_generator/ מוחרגים מ־Git.'
    ]
    (out/'final_research_report_he.md').write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4))
    ax.bar(recalls.Narrative,recalls.Recall);ax.set_ylim(0,1);ax.set_ylabel('Recall')
    ax.set_title('Author-disjoint baseline: mean recall across 3 seeds');ax.tick_params(axis='x',rotation=25)
    fig.tight_layout();fig.savefig(out/'baseline_recall.png',dpi=160);plt.close(fig)
    selected=primary if len(primary) else descriptive
    if len(selected):
        order=['Original','Paraphrase','Normalized']
        values=selected.pivot(index='train_condition',columns='test_condition',values='macro_f1_mean').reindex(index=order,columns=order)
        fig,ax=plt.subplots(figsize=(6,5));im=ax.imshow(values.to_numpy(),vmin=0,vmax=1,cmap='Blues')
        ax.set_xticks(range(3),order);ax.set_yticks(range(3),order);ax.set_xlabel('Test texts');ax.set_ylabel('Training texts')
        ax.set_title('Automated-pass matched cohort' if len(primary) else 'Unvalidated cohort: descriptive only')
        for i in range(3):
            for j in range(3):ax.text(j,i,f'{values.iloc[i,j]:.3f}',ha='center',va='center')
        fig.colorbar(im,ax=ax,label='Macro-F1');fig.tight_layout();fig.savefig(out/'retraining_matrix.png',dpi=160);plt.close(fig)
    for representation in pa.representation.unique():
        for cohort in pa.cohort.unique():
            d=pa[(pa.representation==representation)&pa.cohort.eq(cohort)]
            if not len(d):continue
            label='unvalidated cohort' if cohort=='all_generated_descriptive' else 'automated-pass matched cohort'
            fig,ax=plt.subplots(figsize=(7,4));ax.bar(d.condition,d.accuracy_mean)
            ax.axhline(d.uniform_chance_accuracy.mean(),color='gray',linestyle='--',label='Uniform chance')
            ax.set_ylim(0,1);ax.set_ylabel('Author accuracy: mean across narrative groups')
            ax.set_title(f'{representation}: {label}\n{int(d.n_test.iloc[0])} test texts; {int(d.narrative_groups.iloc[0])} narrative groups',fontsize=10);ax.legend()
            prefix='author_probe_' if cohort=='all_generated_descriptive' else 'author_probe_matched_'
            fig.tight_layout();fig.savefig(out/f'{prefix}{representation}.png',dpi=160);plt.close(fig)


if __name__=='__main__':
    build(Path(__file__).resolve().parents[2]/'artifacts/experiments/author_style_controlled_20261026')

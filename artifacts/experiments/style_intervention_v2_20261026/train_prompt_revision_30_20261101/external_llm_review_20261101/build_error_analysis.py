"""Reporting-only qualitative error analysis of frozen train texts and review.

Annotations are assistant-authored hypotheses, not human labels or new external
review ratings. This script never imports/runs model, training or filtering code.
"""
from pathlib import Path
import ast
import collections
import csv
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
RUN = OUT.parent
STUDY = RUN.parent
ROOT = STUDY.parents[2]
MARKER = '## Focused guard error analysis — 2026-11-01'
TYPES = ['certainty_change', 'attribution_change', 'quote_change', 'stance_or_framing_change',
         'factual_change', 'entity_change', 'number_change', 'negation_change',
         'causal_relation_change', 'temporal_change', 'omission', 'addition', 'other']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def save(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def table(headers, rows):
    def cell(v):
        return str(v).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join('| ' + ' | '.join(map(cell, row)) + ' |'
                     for row in [headers, ['---'] * len(headers), *rows])


def main():
    sources = [OUT / x for x in ['external_review_joined.csv', 'summary.json',
        'NEW_NORMALIZED_EXTERNAL_LLM_REVIEW_30_20261101.csv', 'import_review.py',
        'discrepancy_classification_30.csv', 'build_error_analysis.py', 'error_analysis_annotations.json']]
    sources += [p for p in STUDY.rglob('*') if p.is_file() and OUT not in p.parents
                and not {'runtime', '__pycache__'}.intersection(p.parts)
                and p.suffix in {'.csv', '.json', '.jsonl', '.txt', '.py'}]
    code = ROOT / 'experiments/author_generalization/author_style_controlled.py'
    validator = ROOT / 'artifacts/experiments/verified_human_style_followup_20261026/experiment.py'
    sources += [code, validator, validator.parent / 'author_splits.csv', validator.parent / 'split_definitions.csv']
    before = {p: sha(p) for p in sources}
    raw = read(OUT / 'external_review_joined.csv')
    annotations = json.loads((OUT / 'error_analysis_annotations.json').read_text(encoding='utf-8'))['cases']
    lookup = {r['id']: r for r in annotations}
    assert len(raw) == len(annotations) == len(lookup) == 30
    assert set(lookup) == {r['ID'] for r in raw} and all(r['split'] == 'train' for r in raw)
    constants = {}
    for n in ast.parse(code.read_text(encoding='utf-8')).body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in {'CERT', 'ATTR', 'FRAME'}:
            constants[n.targets[0].id] = ast.literal_eval(n.value)
    def lexical(t):
        words = set(re.findall(r"\b[a-z]+(?:['’][a-z]+)*\b", t.lower().replace('’', "'")))
        return {**{k: sorted(words & v) for k, v in constants.items()},
                'digit_strings': sorted(set(re.findall(r'\b\d+(?:[.,]\d+)*\b', t))),
                'negation_tokens': re.findall(r"\b(?:no|not|never|neither|nor|without|cannot)\b|n['’]t\b", t.casefold()),
                'explicit_future_boolean': bool(re.search(r"\b(?:will|shall)\b|['’]ll\b|\b(?:won|shan)['’]t\b", t.casefold())),
                'quoted_contents': sorted(' '.join((a or b).casefold().split()) for a, b in re.findall(r'"([^"\n]+)"|“([^”\n]+)”', t))}
    rows, issues = [], []
    for base in raw:
        a = lookup[base['ID']]
        flags = base['New_rejection_reasons'].split('|') if base['New_rejection_reasons'] else []
        category = base['discrepancy_class_relative_to_llm']
        for i in a['issues']:
            # 'other' holds discourse/lexical nuances outside the requested taxonomy.
            i['types'] = ['other' if t == 'lexical_nuance' else t for t in i['types']]
            assert set(i['types']) <= set(TYPES)
            assert i['o'] in base['Original'], (base['ID'], i['o'])
            assert i['n'] in base['New_Normalized'], (base['ID'], i['n'])
            assert set(i['guards']) <= set(flags), (base['ID'], i)
            assert (i['catch'] == 'missed') == (not i['guards'])
            issues.append(dict(ID=base['ID'], external_class=category,
                external_meaning_preserved=base['external_meaning_preserved'],
                error_types='|'.join(i['types']), original_excerpt=i['o'], new_excerpt=i['n'],
                change=i['change'], relevant_rejecting_guards='|'.join(i['guards']),
                detection_alignment=i['catch'], likely_source=a['candidate_source'],
                analysis_origin='Assistant qualitative analysis; not human validation'))
        o = a.get('o', a['issues'][0]['o'] if a['issues'] else '')
        n = a.get('n', a['issues'][0]['n'] if a['issues'] else '')
        assert o in base['Original'] and n in base['New_Normalized'], base['ID']
        kinds = sorted({t for i in a['issues'] for t in i['types']})
        relevant = sorted({g for i in a['issues'] for g in i['guards']})
        original_diag, new_diag = lexical(base['Original']), lexical(base['New_Normalized'])
        screen = json.loads(base['new_validation_json'])
        # Reproduce existing lexical gates for explanation only. Do not recalculate acceptance.
        calculated = dict(certainty=original_diag['CERT'] == new_diag['CERT'],
            attribution=bool(original_diag['ATTR']) == bool(new_diag['ATTR']),
            framing_anchors=original_diag['FRAME'] == new_diag['FRAME'],
            numbers=original_diag['digit_strings'] == new_diag['digit_strings'],
            negation=len(original_diag['negation_tokens']) == len(new_diag['negation_tokens']),
            future_tense=original_diag['explicit_future_boolean'] == new_diag['explicit_future_boolean'],
            quotations=original_diag['quoted_contents'] == new_diag['quoted_contents'])
        assert all(str(v).lower() == str(screen['guard_' + k]).lower() for k, v in calculated.items()), base['ID']
        rows.append(dict(ID=base['ID'], split='train', external_class=category,
            external_meaning_preserved=base['external_meaning_preserved'],
            external_semantic_drift=base['external_semantic_drift'],
            external_stance_preserved=base['external_stance_preserved'],
            external_style_change_valid=base['external_style_change_valid'],
            external_notes=base['external_notes'], borderline_separate=base['external_meaning_preserved'] == 'Borderline',
            automatic_pass=base['New_automatic_pass'], rejecting_guards='|'.join(flags),
            error_types='|'.join(kinds), relevant_rejecting_guards='|'.join(relevant),
            guard_relevance=a['guard_relevance'], original_excerpt=o, new_excerpt=n,
            issue_evidence_json=json.dumps(a['issues'], ensure_ascii=False),
            analysis=a['analysis'], fp_mechanism='|'.join(a['fp_kind']),
            why_external_review_accepts=(base['external_notes'] if category == 'False Positive' else ''),
            borderline_nuances='|'.join(a['borderline_kind']), future_action=a['future_action'],
            future_guard_decision=('documentation_only_for_now; targeted review before proposing a new guard'
                if base['ID'] in {'creators:421279', 'creators:2e34435c6ccf', 'creators:218236'} else
                'candidate_scoped_guard_study; not a validated or deployed guard'
                if a['issues'] else 'diagnose existing guard or targeted review; no new guard justified from this case alone'),
            reviewer_disagreement_risk=a['reviewer_disagreement'], likely_source=a['candidate_source'],
            original_lexical_diagnostic_json=json.dumps(original_diag, ensure_ascii=False),
            new_lexical_diagnostic_json=json.dumps(new_diag, ensure_ascii=False),
            automatic_checks_json=base['new_validation_json'],
            analysis_origin='Assistant qualitative error analysis; not a new External LLM Review or human judgment',
            human_verified=False))
    counts = dict(collections.Counter(r['external_class'] for r in rows))
    assert counts == {'False Positive': 5, 'True Negative': 5, 'True Positive': 19, 'False Negative': 1}
    assert sum(r['borderline_separate'] for r in rows) == 15
    save('ERROR_ANALYSIS_30.csv', rows)
    save('ERROR_ANALYSIS_ISSUES.csv', issues)
    save('ERROR_ANALYSIS_BORDERLINE_15.csv', [r for r in rows if r['borderline_separate']])
    fp_mechanisms = []
    for mechanism in ['technical false positive', 'formatting variation', 'lexical variation',
                      'overly strict threshold', 'guard logic issue', 'other']:
        selected = [r for r in rows if r['external_class'] == 'False Positive'
                    and mechanism in r['fp_mechanism'].split('|')]
        fp_mechanisms.append(dict(mechanism=mechanism, count=len(selected),
                                  examples='|'.join(r['ID'] for r in selected)))
    save('ERROR_ANALYSIS_FP_MECHANISMS.csv', fp_mechanisms)
    # Main type counts are only the 20 externally flagged risk cases, not new reclassifications.
    types = []
    for t in TYPES:
        relevant_issues = [i for i in issues if t in i['error_types'].split('|')]
        ids = {i['ID'] for i in relevant_issues}
        caught = {i['ID'] for i in relevant_issues if i['detection_alignment'] != 'missed'}
        missed = ids - caught
        sources_t = collections.Counter(i['likely_source'] for i in relevant_issues)
        types.append(dict(error_type=t, count=len(ids), examples='|'.join(sorted(ids)),
            caught_by_guard=len(caught), missed_by_guard=len(missed),
            likely_source='|'.join(sorted(sources_t)) or 'ambiguous',
            unit='unique externally flagged source IDs per type; overlapping categories',
            direct_aligned_ids='|'.join(sorted({i['ID'] for i in relevant_issues if i['detection_alignment'] == 'caught'})),
            partial_aligned_ids='|'.join(sorted({i['ID'] for i in relevant_issues if i['detection_alignment'] == 'partial'}))))
    save('ERROR_ANALYSIS_BY_TYPE.csv', types)
    guard_rows = []
    for g in sorted({g for r in rows for g in r['rejecting_guards'].split('|') if g}):
        flagged = [r for r in rows if g in r['rejecting_guards'].split('|')]
        aligned = {i['ID'] for i in issues if g in i['relevant_rejecting_guards'].split('|')}
        direct = {i['ID'] for i in issues if g not in {'bidirectional_nli', 'similarity'}
                  and g in i['relevant_rejecting_guards'].split('|') and i['detection_alignment'] == 'caught'}
        guard_rows.append(dict(guard=g, rejected_rows=len(flagged),
            external_TP=sum(r['external_class'] == 'True Positive' for r in flagged),
            external_FP=sum(r['external_class'] == 'False Positive' for r in flagged),
            analyst_relevant_or_partial_rows=len(aligned), analyst_direct_rows=len(direct),
            no_alignment_in_external_risk_coding_ids='|'.join(r['ID'] for r in flagged if r['ID'] not in aligned),
            caution='Alignment counts only the 20 external-risk cases; additional FP/TN concerns are separate. Not causal validation or guard precision.'))
    save('ERROR_ANALYSIS_BY_GUARD.csv', guard_rows)
    summary_data = dict(external_class_counts=counts, borderline_count=15,
        externally_flagged_risk_cases=20, type_counts=types, guard_analysis=guard_rows,
        reviewer_disagreement_risk_ids=[r['ID'] for r in rows if r['reviewer_disagreement_risk']],
        taxonomy_scope='20 external drift-risk rows; FP/TN additional risks documented separately, never relabelled',
        semantic_drift_is_not_human_verified=True, no_training=True, no_filter_changes=True)
    (OUT / 'ERROR_ANALYSIS_COUNTS.json').write_text(json.dumps(summary_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    generate_report(rows, issues, types, guard_rows)
    changed = [str(p) for p, digest in before.items() if sha(p) != digest]
    assert not changed, changed
    audit = dict(protected_input_sha256={str(p.relative_to(ROOT)): h for p, h in before.items()},
        changed_protected_inputs=changed, rows=30, borderline_rows=15,
        verbatim_excerpt_checks=True, existing_lexical_guard_diagnostics_reproduced=True,
        external_ratings_and_classifications_unchanged=True, analysis_origin='Assistant authored; not human validation',
        no_models_called=True, no_training=True, no_test_evaluation=True)
    (OUT / 'ERROR_ANALYSIS_AUDIT.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(classes=counts, types={x['error_type']: x['count'] for x in types}, protected=len(before))))


def generate_report(rows, issues, types, guards):
    ranked = sorted(types, key=lambda r: -r['count'])
    table_types = table(['error_type', 'count', 'examples', 'caught_by_guard', 'missed_by_guard', 'likely_source'],
        [[r[k] for k in ['error_type', 'count', 'examples', 'caught_by_guard', 'missed_by_guard', 'likely_source']] for r in ranked])
    text = '''# Error Analysis — External LLM Review — New Normalized

30 דוגמאות train בלבד; 2026-11-01. זהו ניתוח איכותני חדש של הסוכן על בסיס הטקסטים, הקוד והציונים השמורים — לא Human Validation, לא סבב External LLM Review נוסף ולא אימות עובדתי של המאמרים. הכרעות המקור נשארו 19 TP, ‏5 FP, ‏5 TN ו־1 FN ביחס ל־LLM. ‏15 מקרי Borderline נשמרים בנפרד (14 TP ו־1 FN); כולם נושאים גם semantic_drift=Yes בקובץ שסופק. אין לשנות את דירוגם לפי הניתוח הזה.

## מה נמצא ולמה הסיווג לבדו אינו מספיק

**פסילת רשומה אינה הוכחה שה־guard זיהה את השגיאה הסמנטית.** למשל 116358 הוא TP ברמת הרשומה אך נפסל רק בשל צורת מספר שקולה; 298495 נפסל בלי לזהות ישירות את החלפת strangers ב־anonymous sources; 416436 נפסל בשל פסיק בתוך ציטוט בעוד השמטת העליונות המוסרית והכלכלית לא נתפסה ישירות.

נמצאו גם סיכונים שלא הוזכרו בדירוגים חיוביים של ה־LLM: ב־421951 יש חשד להיפוך תפקיד מ־fight your wars ל־face in battle; ב־421024 הושמטו lamentable והטענה המפורשת על חשיפת איברים/תחתונים; ב־212505 most הפך ל־many ו־sharply הושמט; ב־459e183c1d0d net-worth eligibility הפך ל־assets; ב־224770 last week הפך ל־recently. אלה תצפיות הסוכן המחייבות בדיקה ממוקדת, **לא תיוגים אנושיים ולא שינוי של ה־FP/TN החיצוניים**. גם 120669 כולל ניואנס founding president/founding father, בלי להחזיר את טעות Obama/Washington שתוקנה.

## סוגי שגיאות — הסיכום המבוקש

הטבלה מתייחסת רק ל־20 הרשומות שסומנו כסיכון ב־LLM, לא למועמדי הסיכון החדשים ב־FP/TN. count = מספר IDs ייחודיים עם הקטגוריה; קטגוריות חופפות ואין לסכום אותן ל־20. caught_by_guard = קיימת פסילה רלוונטית או רלוונטית חלקית לפי הניתוח; missed_by_guard = אין פסילה כזו. אם שני ניואנסים מאותה קטגוריה שונים באותו ID, זיהוי אחד מספיק לספירת caught ולכן זו אינה טענת כיסוי מלא. NLI/similarity הם אותות כלליים בלבד ולא מסבירים איזה span גרם לציון. קובץ ה־issues שומר caught/partial/missed לכל שינוי בנפרד; טבלת הסוגים כוללת IDs של זיהוי ישיר לעומת חלקי.

likely_source הוא השערה אבחונית, לא ניסוי סיבתי: prompt-induced פירושו סיכון שנוצר בפלט השכתוב, בלי לקבוע אם מקורו ב־prompt, במודל, בכימות או בפענוח. guard-too-weak פירושו כיסוי חסר במקרה שנבדק. לא נבדק prompt חלופי או סף חלופי. number_change/negation_change/causal_relation_change יכולים להישאר אפס: שינוי טוקן מספר/שלילה אינו בהכרח שינוי ערך/קוטביות/סיבתיות. temporal_change כולל less than a decade; אין צורך להמציא קטגוריה מספרית נוספת.

'''
    text += table_types + '\n\n## 19 True Positives — ראיות ורלוונטיות הדגל\n\n'
    for r in rows:
        if r['external_class'] != 'True Positive':
            continue
        text += f"### {r['ID']} — {r['external_meaning_preserved']}\n\n"
        text += f"דגלי פסילה: `{r['rejecting_guards']}`. קטגוריות: `{r['error_types']}`.\n\n"
        for i in json.loads(r['issue_evidence_json']):
            text += f"- `{i['o']}` → `{i['n']}`: {i['change']} סוגים: {', '.join(i['types'])}; alignment={i['catch']}; guards={','.join(i['guards']) or 'none'}.\n"
        text += '\n' + r['analysis'] + ' ' + r['guard_relevance'] + '\n\nהמלצה עתידית בלבד: ' + r['future_action'] + '\n\n'
    text += '## 5 False Positives — מה טכני ומה עדיין דורש בדיקה\n\n'
    text += 'סיווג מנגנון FP נשמר בנפרד מטקסונומיית semantic drift. לא נמצא מקרה שבו ניתן לייחס את הפסילה לסף similarity/NLI קשיח מדי: חמשת ה־FP החיצוניים נפסלו רק ב־guards לקסיקליים/מספריים. אין מכאן הצדקה להקלה בספים.\n\n'
    for r in rows:
        if r['external_class'] != 'False Positive':
            continue
        text += f"### {r['ID']}\n\nפסילה: `{r['rejecting_guards']}`; מנגנון: {r['fp_mechanism']}.\n\n"
        text += f"`{r['original_excerpt']}` → `{r['new_excerpt']}`.\n\nהכרעת ה־LLM: {r['why_external_review_accepts']}\n\n"
        text += r['analysis'] + ' ' + r['guard_relevance'] + '\n\n'
        if r['reviewer_disagreement_risk']:
            text += 'סיכון נפרד שלא הוכרע: ' + r['reviewer_disagreement_risk'] + '\n\n'
        text += 'המלצה עתידית בלבד: ' + r['future_action'] + '\n\n'
    fn = next(r for r in rows if r['external_class'] == 'False Negative')
    screen = json.loads(fn['automatic_checks_json'])
    text += f'''## False Negative — creators:423315

`riots`→`protests` משנה event characterization, framing, lexical polarity ו־stance intensity; התיאור אינו שקול במדויק גם אם האירוע נשאר מזוהה. `going to lose`→`destined to lose` מוסיף גוון הכרחי/פטליסטי של certainty. זו עדיין הכרעת Borderline של הבודק, לא No חדש.

CERT אינו מכיל אף אחד מהביטויים האלו, FRAME אינו מכיל riots/protests, ובדיקת עתיד מחפשת will/shall/ll ולא going to/destined. שוויון ישויות, מספרים ושלילות אינו בודק אפיון אירוע או inevitability. ציוני similarity={float(screen['semantic_similarity']):.4f}, NLI forward={float(screen['entailment_forward']):.4f}, reverse={float(screen['entailment_reverse']):.4f} עברו בספים הקיימים; אין לייחס להם הבחנת framing שלא נמדדה. מועמדים למחקר עתידי: השוואת אפיון אירוע/קוטביות בהקשר ו־claim-scoped certainty/inevitability. הוספת מילים לרשימה לבדה אינה פתרון מוכח.

## 15 Borderline — נשמרים כקבוצה חופפת, לא הכרעה בינארית

'''
    text += table(['ID', 'סיווג קיים', 'מה השתנה', 'סוג הניואנס', 'האם הדגל רלוונטי', 'guard חדש או תיעוד'],
        [[r['ID'], r['external_class'], '; '.join(i['change'] for i in json.loads(r['issue_evidence_json'])),
          r['borderline_nuances'], r['guard_relevance'], r['future_guard_decision'] + '; ' + r['future_action']] for r in rows if r['borderline_separate']])
    text += '\n\n## 5 True Negatives — ביקורת עצמית על מקור ההשוואה\n\n'
    text += table(['ID', 'מה תומך באישור', 'סיכון חדש לבדיקה, בלי שינוי תווית'],
        [[r['ID'], r['analysis'], r['reviewer_disagreement_risk'] or 'No additional concern identified in this focused review; not human verified.']
         for r in rows if r['external_class'] == 'True Negative'])
    text += '\n\n## אילו guards עובדים, ואילו אותות מטעים\n\n'
    text += 'ספירות הרלוונטיות כאן מתייחסות רק לקידוד 20 סיכוני ה־LLM. סיכונים נוספים שזוהו ב־FP/TN נשארים בנפרד; אפס בעמודה זו אינו הוכחה שדגל על FP הוא בלתי רלוונטי (למשל will/can ב־0105f26ef9f1).\n\n'
    text += table(['guard', 'פסילות', 'TP חיצוני', 'FP חיצוני', 'רלוונטי/חלקי בסיכוני LLM', 'ישיר בסיכוני LLM'],
        [[g[k] for k in ['guard', 'rejected_rows', 'external_TP', 'external_FP', 'analyst_relevant_or_partial_rows', 'analyst_direct_rows']] for g in guards])
    text += '''

- **Quotations:** מזהה ישירות שינוי/מחיקת תוכן ב־417181, ‏114783, ‏8b0d99b23d03 ו־418904. ב־423545 וב־416436 הוא מתריע רק על פסיק בתוך הציטוט, ולא על השינוי הרטורי המרכזי. דרישת verbatim עדיין הופכת זאת להפרת חוזה טקסטואלית; אין להתייחס אליה אוטומטית כ־semantic drift. הקוד מנרמל case/רווחים וממיין ציטוטים, ולכן גם אינו בדיקת בתים או סדר מלאה.
- **NLI:** אות סיכון רחב בכמה החלפות טענה/השמטות. אינו מאמת את שימור ה־stance, אינו מסביר את span השגיאה, ומפספס את 423315 ואת factual strangers/anonymous ב־298495. אין כאן ניסוי שתומך בשינוי סף.
- **Framing anchors:** מספק אות ממוקד ב־418827 בעקבות אובדן murder. כיסוי לקסיקלי מוגבל: אינו מזהה riots/protests, hack/figure או superiority/virtues.
- **Numbers:** שלוש פסילות על ייצוגים שקולים ברמת הערך: 212505 (10/ten), ‏114783 (9/11/September 11), ‏116358 (5 1/2/five and a half). האחרון TP רק בגלל סיכון אחר. יש לשמר יחידה, תאריך ו־scope בעת מחקר על נרמול, לא רק למחוק ספרות.
- **Certainty/future:** exact token set/נוכחות will מייצרים FP ב־120177, ‏418620 ו־459e183c1d0d; ב־0105f26ef9f1 might/may עשוי להיות שקול אך will/can הוא סיכון מודלי אמיתי לבדיקה. CERT מפספס likely/destined/aimed at. הוא מסמן correctly סיכון ב־probably→may ובתוספת could של 97c9d6b9ac1b, אך אינו מבין scope כמו could not avoid.
- **Negation/attribution:** not surprising/unsurprising, can't/lack capability ו־said/declared מייצרים שינוי ספירה/רשימה ללא היפוך משמעות הכרחי. attribution הוא boolean על קיום מילת ייחוס בכל הטקסט: ב־417181 אפילו United States מספק states. אינו יישור של מי טוען מה. אין לייחס לו זיהוי ישיר של strangers→anonymous sources.
- **Entities:** תופס השמטת House/Senate ב־216128; ראשי תיבות ושמות חלופיים ב־417181 עלולים להיות כשל שימור מילולי בלי שינוי זהות. NER אינו בודק תפקידי נושא/מושא, חברות/ברית, או asset/net worth.

## המלצות נפרדות — אינן שינוי מיושם

### Prompt issues

- לחקור בעתיד שימור טענות לפי actor–predicate–object–time–modality–attribution, ובפרט הבדל בין אפקט לכוונה, בעל הציפייה, יחסי חברות/ברית ו־assets/net worth. לא לשנות first person כשהדבר יוצר טענה על קבוצה.
- להגן על spans מצוטטים, טענות והשוואות מפורשות, comparators כגון less than, quantifiers כגון most/only, עוצמת הערכה ומטאפורות פוליטיות. אין להוסיף כלי עבודה או פרשנות לפתגם.
- לשמור היפותזות אלו לניסוי train חדש בלבד, אם יאושר; לא הוכח שהוראות prompt נוספות יפתרו את כשלי המודל הקטן.

### Guard issues

- לתכנן בעתיד אבחון שקילות ערכים מספריים/תאריכים ושקילות ביטויי שלילה/חובה/עתיד; להפריד דיווח על הפרת literal fidelity מסיכון סמנטי.
- לחקור יישור טענה, תפקידי משתתפים, שייכות ייחוס, scope מודלי ואפיון אירוע/קוטביות. לא להסתפק במילון מילות רגש רחב יותר.
- להעריך כל guard מול שגיאה ממוקדת, לא מול פסילת רשומה בלבד; להפריד טעות מספרית טכנית ב־TP מסיבה סמנטית אחרת. NLI דורש הערכה ממוקדת, לא כוונון סף על סמך 30 הדוגמאות.
- לבקש בדיקה אנושית ממוקדת גם ל־FP/TN שה־LLM אישר למרות עדות טקסטואלית לסיכון. אין להגדיר את ה־LLM כ־gold לצורך קביעת precision/recall של guards.

### No-action cases

- אין צורך לתקן את ערך הזמן ב־10→ten או 5 1/2→five and a half, את not surprising→unsurprising, או את have to→must כשלעצמם. אין בכך אישור של יתר הרשומה או היתר לשנות את guard כעת.
- אין צורך לפתוח מחדש את תיקון Obama/Washington ב־120669; ב־419062 לא זוהה כשל נוסף בניתוח הממוקד. לשמור כדוגמאות חיוביות אבחוניות, בלי להציגן כמאומתות אנושית.
- אין לשנות כעת split/test, labels, human-review fields, prompt, filtering, thresholds או training code. אין למחוק ספי NLI או להקל דרישת ציטוט מילולי כדי להגדיל N.

## מגבלות ושחזור

זהו מדגם אבחוני מכוון של 30 טקסטי train, ללא סוקר אדם וללא הכרעה עצמאית בעובדות העולם. רלוונטיות guard ו־likely_source הן הערכות הסוכן. הראיות הן substrings מדויקים שנבדקים בתוכנית; טוקני CERT/ATTR/FRAME, מספרים, שלילות וציטוטים מחושבים מחדש לצורכי הסבר בלבד ומושווים לדגלים השמורים. לא הורץ מודל שופט, לא נוצרו שכתובים ולא בוצעו training/test evaluation.

קלט הניתוח: `error_analysis_annotations.json` לצד הטקסטים/דירוגים השמורים. לשחזור הדוחות בלבד, מתיקיית הרפו:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/external_llm_review_20261101/build_error_analysis.py
```

התוצרים: [כל 30 הרשומות](ERROR_ANALYSIS_30.csv), [ראיות לכל שינוי](ERROR_ANALYSIS_ISSUES.csv), [15 מקרי Borderline](ERROR_ANALYSIS_BORDERLINE_15.csv), [סוגי שגיאה](ERROR_ANALYSIS_BY_TYPE.csv), [ניתוח guards](ERROR_ANALYSIS_BY_GUARD.csv), [מנגנוני FP](ERROR_ANALYSIS_FP_MECHANISMS.csv), [ספירות](ERROR_ANALYSIS_COUNTS.json), [בדיקת תקינות](ERROR_ANALYSIS_AUDIT.json). ספירת הקטגוריות ניתנת לשחזור מן ההערות, אך אינה הערכת שכיחות באוכלוסייה. הרצה חוזרת אינה משחזרת שיפוט אנושי; היא משחזרת את החישוב על ההערות האיכותניות הקפואות.
'''
    (OUT / 'ERROR_ANALYSIS_SUMMARY_HE.md').write_text(text, encoding='utf-8')
    top = ', '.join(f"{r['error_type']} ({r['count']})" for r in ranked[:3])
    section = f'''{MARKER}

בוצע ניתוח איכותני של הסוכן על אותם 30 טקסטי train, ללא שופט נוסף או אימות אנושי. נשמרו דירוגי External LLM Review — New Normalized: ‏19 TP / ‏5 FP / ‏5 TN / ‏1 FN ו־15 Borderline נפרדים (קבוצה חופפת). סוגי הסיכון השכיחים ב־20 המקרים שהבודק סימן הם {top}; קטגוריות חופפות וספירות אלו הן קידוד איכותני, לא תיוגי אדם.

ההבחנה המרכזית: TP ברמת הרשומה אינו הוכחה שה־guard זיהה את הכשל. ב־116358 הדגל היחיד הוא מספר שקול במילים; ב־298495 השינוי העובדתי אינו מזוהה ישירות; ב־416436 דגל הציטוט נובע מפסיק ולא מהשמטת מסגור. מספרים/ביטויי חובה/עתיד ותחליפים לקסיקליים מייצרים דגלים טכניים; ציטוטים שעברו שינוי תוכן ו־murder ב־418827 מספקים דוגמאות לאותות רלוונטיים. ב־423315 חסר כיסוי לאפיון riots/protests ולגוון ההכרח ב־destined.

נרשמו בנפרד גם סיכונים שלא הוזכרו בדירוגי Yes, ובהם fight your wars→face in battle ב־421951, השמטות ב־421024, most→many ב־212505 ו־net worth→assets ב־459e183c1d0d. אלו מועמדים לבדיקה נוספת, לא שינוי הכרעות ה־LLM. אין לראות בו gold או להציג את ספירות ה־FP/FN כשיעורי טעות מאומתים.

המלצות לעתיד בלבד: שימור טענות, תפקידים, scope מודלי, אפיון אירוע וציטוטים; אבחון שקילות מספרים/ביטויי שלילה וחובה; בדיקה ממוקדת של אי־הסכמות מול סוקר אדם. לא שונו prompt, guards, ספים, filtering, split, labels, human-review fields או קוד אימון; לא בוצעו retraining או test evaluation. עוצרים לפני החלטה על ניסוי חדש.
'''
    section_path = OUT / 'ERROR_ANALYSIS_CENTRAL_SECTION_HE.md'
    section_path.write_text(section, encoding='utf-8')
    apply_doc_summary()


def apply_doc_summary():
    section = (OUT / 'ERROR_ANALYSIS_CENTRAL_SECTION_HE.md').read_text(encoding='utf-8')
    targets = [ROOT / 'CURRENT_STATE.md', STUDY / 'EXPERIMENT_GUIDE_HE.md', STUDY / 'FINAL_REPORT_HE.md']
    for p in targets:
        prefix = ('artifacts/experiments/style_intervention_v2_20261026/' if p.parent == ROOT else '')
        link = prefix + 'train_prompt_revision_30_20261101/external_llm_review_20261101/ERROR_ANALYSIS_SUMMARY_HE.md'
        text = p.read_text(encoding='utf-8').split(MARKER, 1)[0].rstrip()
        # Keep the one-page state document compact; detailed summary belongs in experiment docs.
        content = section if p.name != 'CURRENT_STATE.md' else f'''{MARKER}

הניתוח האיכותני מבחין בין פסילת רשומה לזיהוי השגיאה: חלק מה־TP נתפסו רק בדגל טכני שאינו מסביר את הסיכון הסמנטי. ציטוטים/מסגור מפורש מספקים אותות רלוונטיים; כיסוי אפיון אירוע, תפקידי משתתפים ו־certainty scope חלש. זוהו גם סיכונים במקרים שה־LLM אישר, בלי לשנות את דירוגיו או את 15 מקרי ה־Borderline. זהו ניתוח הסוכן, לא Human Validation. ההמלצות עתידיות בלבד; כל הרכיבים הקפואים נשמרו ולא בוצע אימון או test evaluation.
'''
        p.write_text(text + '\n\n' + content + f'\n[Error analysis — ראיות, ספירות והמלצות]({link})\n', encoding='utf-8')


if __name__ == '__main__':
    main()

"""Saved-output comparison and review packaging; no semantic judge or model calls."""
from pathlib import Path
import collections
import hashlib
import json
import math
import re

from run import OUT, STUDY, ROOT, V2, PREVIOUS, load_v2, unchanged


def table(headers, rows):
    def cell(v):
        return str(v).replace('|', '\\|').replace('\n', '<br>')
    return '\n'.join('| ' + ' | '.join(map(cell, r)) + ' |' for r in [headers, ['---'] * len(headers), *rows])


def quoted(t):
    return [a or b for a, b in re.findall(r'"([^"\n]+)"|“([^”\n]+)”', t)]


def main():
    m = load_v2()
    protected_n = unchanged(m)
    helper = m.imported_style_module()
    engine = helper.load_engine()
    np = engine.np
    old = {r['ID']: r for r in m.records(OUT / 'frozen_comparison_inputs.csv')}
    cohort = m.records(OUT / 'analysis_cohort.csv')
    generated = {r['row_id']: r for r in [json.loads(s) for s in (OUT / 'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]}
    validation = {r['row_id']: r for r in m.records(OUT / 'rewrite_validation.csv')}
    assert len(old) == len(generated) == len(validation) == len(cohort) == 30
    scaling = json.loads((STUDY / 'style_feature_scaling.json').read_text(encoding='utf-8'))
    names = json.loads((PREVIOUS / 'style_feature_definitions.json').read_text(encoding='utf-8'))['names']
    assert names == scaling['names'] and len(names) == 66
    scale = np.array(scaling['scale'])
    rows, metrics, explicit, request_checks = [], [], [], []
    prompt = (OUT / 'prompt.txt').read_text(encoding='utf-8')
    for record in cohort:
        rid = record['row_id']
        o = old[rid]
        v3 = generated[rid]
        assert record['split'] == 'train' and record['text'] == o['Original'] == v3['original']
        assert record['narrative_name'] == o['proposed_narrative']
        payload = dict(messages=[dict(role='system', content=prompt), dict(role='user', content=record['text'])],
            temperature=0, seed=20261026, max_tokens=320, repeat_penalty=1., top_k=1, top_p=1., min_p=0., cache_prompt=True)
        matches = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest() == v3['request_sha256']
        assert matches
        request_checks.append(dict(ID=rid, original_only_request_hash_matches=True))
        row = dict(ID=rid, Author=record['author_name'], split='train', proposed_narrative=record['narrative_name'],
                   Original=record['text'], New_v2=o['New_Normalized'], New_v3=v3['rewrite'])
        original_features = np.array(engine.style_features(record['text']))
        for version, text, screen in [('v2', row['New_v2'], json.loads(o['new_validation_json'])), ('v3', row['New_v3'], validation[rid])]:
            style = helper.style_metrics(record['text'], text)
            features = np.array(engine.style_features(text))
            style['explicit_style_mean_abs_standardized_change'] = float(np.mean(np.abs(features - original_features) / scale))
            metrics.append(dict(ID=rid, version=version, **style))
            for name, a, b in zip(names, original_features, features):
                explicit.append(dict(ID=rid, version=version, feature=name, original=float(a), rewrite=float(b), delta=float(b - a)))
            row[version + '_preservation_pass'] = str(screen['passed']).lower() == 'true'
            row[version + '_rejection_reasons'] = screen['rejection_reasons']
            row[version + '_substantial_style'] = style['substantial_style_change']
            row[version + '_exact_copy'] = style['exact_copy']
            row[version + '_both_automatic'] = row[version + '_preservation_pass'] and style['substantial_style_change']
            row[version + '_quotes_verbatim_preserved'] = sorted(quoted(record['text'])) == sorted(quoted(text))
            row[version + '_quotes_verbatim_same_order'] = quoted(record['text']) == quoted(text)
            row[version + '_automatic_checks_json'] = json.dumps(screen, ensure_ascii=False)
            row[version + '_style_metrics_json'] = json.dumps(style, ensure_ascii=False)
        assert row['v2_preservation_pass'] == (o['New_automatic_pass'] == 'True')
        assert row['v2_substantial_style'] == (o['New_style_proxy_substantial'] == 'True')
        rows.append(row)
    m.write_csv('comparison_v2_v3_30.csv', rows)
    m.write_csv('style_metrics_v2_v3.csv', metrics)
    m.write_csv('explicit_style_changes_v2_v3.csv', explicit)
    saved_v2_style = {r['ID']: r for r in m.records(V2 / 'style_metrics_old_new.csv') if r['version'] == 'New'}
    for measurement in metrics:
        if measurement['version'] != 'v2':
            continue
        prior = saved_v2_style[measurement['ID']]
        for k, value in measurement.items():
            if k in {'ID', 'version'}:
                continue
            if isinstance(value, bool):
                assert prior[k] == str(value), (measurement['ID'], k)
            elif isinstance(value, (int, float)):
                assert math.isclose(float(prior[k]), value, rel_tol=1e-10, abs_tol=1e-10), (measurement['ID'], k)
            else:
                assert prior[k] == str(value), (measurement['ID'], k)
    v2_events = [json.loads(s) for s in (V2 / 'audit_trail.jsonl').read_text(encoding='utf-8').splitlines()]
    v3_events = [json.loads(s) for s in (OUT / 'audit_trail.jsonl').read_text(encoding='utf-8').splitlines()]
    v2_gen = next(e for e in v2_events if e['stage'] == 'generate')
    v3_gen = next(e for e in v3_events if e['stage'] == 'generate')
    assert v2_gen['model_sha256'] == v3_gen['model_sha256']
    assert v2_gen['runtime_sha256'] == v3_gen['runtime_sha256']
    m.dump('implementation_manifest.json', dict(
        generator_model_and_runtime_match_v2=True, v2_style_metrics_recomputed_identically=True,
        report_code_sha256=m.sha(Path(__file__)), orchestration_code_sha256=m.sha(OUT / 'run.py'),
        inherited_code_sha256=m.sha(V2 / 'run.py'),
        effective_decoding=dict(temperature=0, seed=20261026, max_tokens=320, repeat_penalty=1., top_k=1, top_p=1., min_p=0., cache_prompt=True),
        inherited_manifest_note='The nested generator manifest contains predecessor defaults; effective max_tokens=320 is in protocol and reconstructed request hashes.'))
    m.dump('request_integrity_audit.json', dict(n=30, all_passed=True, checks=request_checks))
    totals = {v: dict(automatic_pass=sum(r[v + '_preservation_pass'] for r in rows),
        substantial_style_proxy=sum(r[v + '_substantial_style'] for r in rows),
        both=sum(r[v + '_both_automatic'] for r in rows), exact_copies=sum(r[v + '_exact_copy'] for r in rows)) for v in ['v2', 'v3']}
    assert list(totals['v2'].values()) == [6, 24, 6, 0]
    changes = []
    for r in rows:
        a = set(r['v2_rejection_reasons'].split('|')) - {''}
        b = set(r['v3_rejection_reasons'].split('|')) - {''}
        changes.append(dict(ID=r['ID'], removed_flags='|'.join(sorted(a - b)), added_flags='|'.join(sorted(b - a)),
            v2_pass=r['v2_preservation_pass'], v3_pass=r['v3_preservation_pass'],
            v3_style=r['v3_substantial_style'], not_semantic_adjudication=True))
    m.write_csv('automatic_flag_changes_v2_v3.csv', changes)
    # Span probes describe literal evidence only, never adjudicate semantic equivalence.
    annotations = json.loads((V2 / 'external_llm_review_20261101/error_analysis_annotations.json').read_text(encoding='utf-8'))['cases']
    by_id = {r['ID']: r for r in rows}
    probes = []
    extra = [
        ('creators:423315', 'George Floyd riots', 'George Floyd protests', 'event characterization'),
        ('creators:423315', 'going to lose', 'destined to lose', 'certainty in context'),
        ('creators:212505', 'most media pundits', 'many media analysts', 'quantifier'),
        ('creators:421951', "That's who you want to fight your wars.", 'These were the men you wanted to face in battle.', 'participant role'),
        ('creators:421024', 'lamentable even at nightclubs', 'even at nightclubs', 'evaluative omission'),
        ('creators:459e183c1d0d', 'worth more than $1 billion', 'with more than $1 billion in assets', 'eligibility criterion')]
    candidates = [(a['id'], i['o'], i['n'], i['change']) for a in annotations for i in a['issues']] + extra
    for rid, original_span, v2_span, risk in candidates:
        r = by_id[rid]
        assert original_span in r['Original'] and v2_span in r['New_v2']
        restored = original_span in r['New_v3']
        persists = v2_span in r['New_v3']
        status = ('original_span_restored_v2_span_absent' if restored and not persists else
                  'both_spans_present_or_overlapping' if restored and persists else
                  'v2_span_still_present' if persists else 'different_form_requires_external_review')
        probes.append(dict(ID=rid, prior_risk=risk, original_span=original_span, v2_problem_span=v2_span,
            original_span_present_in_v3=restored, v2_span_present_in_v3=persists, literal_probe_status=status,
            v3_automatic_pass=r['v3_preservation_pass'], v3_style=r['v3_substantial_style'],
            final_semantic_verdict='Pending separate external review; literal probes are not adjudication'))
    m.write_csv('focused_span_checks.csv', probes)
    # Named, transparent textual diagnostics; these are not an LLM's semantic verdicts.
    specs = [
        ('creators:417181', 'funding_rank', 'most generous funder', r'\b(?:primary financier|major funder)\b'),
        ('creators:417181', 'ironic_fighting_quote', '"fighting"', r'\bfighting\b'),
        ('creators:8b0d99b23d03', 'Fitzgerald_verbatim', 'The rich are different from you and me.', r'The rich are distinct'),
        ('creators:8b0d99b23d03', 'countries_metaphor', 'two countries', r'two (?:distinct )?regions'),
        ('creators:423545', 'insult_intensity', 'right-wing hack', r'right-wing figure'),
        ('creators:423545', 'bomb_metaphor', 'bomb maker', r'\bcreator\b'),
        ('creators:298495', 'sender_property', 'strangers', r'anonymous sources'),
        ('creators:418904', 'quoted_celebrate', "We didn't celebrate the Fourth of July,", r"We didn't mark the Fourth of July,"),
        ('creators:423315', 'event_characterization', 'George Floyd riots', r'George Floyd protests'),
        ('creators:423315', 'inevitability', 'going to lose', r'destined to lose'),
        ('creators:418904', 'new_branded_word', 'Black backs whipped bloody', r'\bbranded\b'),
        ('creators:418904', 'new_specific_surrender_day', 'as was their habit', r'typically surrendered on this day'),
        ('creators:417181', 'new_pseudonymous_word', 'fictitious entities', r'\bpseudonymous\b'),
        ('creators:8b0d99b23d03', 'Saturday_retention', 'on Saturday', r'(?!)'),
        ('creators:8b0d99b23d03', 'Sunday_retention', 'on Sunday', r'(?!)'),
        ('creators:120669', 'Obama_Washington_reference', 'his past Thanksgiving addresses', r"President Washington's Thanksgiving addresses"),
        ('creators:421951', 'participant_role', 'fight your wars', r'(?:wanted to|should) face in battle'),
        ('creators:212505', 'quantifier', 'most media pundits', r'many media (?:analysts|pundits)'),
        ('creators:459e183c1d0d', 'net_worth_eligibility', 'worth more than $1 billion', r'with more than \$1 billion in assets')]
    spotchecks = []
    for rid, probe, original_anchor, risk_pattern in specs:
        r = by_id[rid]
        assert original_anchor in r['Original']
        spotchecks.append(dict(ID=rid, diagnostic=probe, original_anchor=original_anchor,
            prior_risk_pattern=risk_pattern, v2_anchor_present=original_anchor in r['New_v2'],
            v3_anchor_present=original_anchor in r['New_v3'],
            v2_risk_pattern_present=bool(re.search(risk_pattern, r['New_v2'])),
            v3_risk_pattern_present=bool(re.search(risk_pattern, r['New_v3'])),
            v3_pass=r['v3_preservation_pass'], v3_style=r['v3_substantial_style'],
            limitation='Literal pattern/anchor observation only; no final semantic adjudication'))
    m.write_csv('targeted_textual_spotchecks.csv', spotchecks)
    risk_counts = collections.Counter(reason for r in rows for reason in r['v3_rejection_reasons'].split('|') if reason)
    summary = dict(n=30, scope='Same TRAIN-only diagnostic sources; not unseen-author evidence', totals=totals,
        v3_both_ids=[r['ID'] for r in rows if r['v3_both_automatic']],
        automatic_pass_gained_ids=[r['ID'] for r in rows if r['v3_preservation_pass'] and not r['v2_preservation_pass']],
        automatic_pass_lost_ids=[r['ID'] for r in rows if r['v2_preservation_pass'] and not r['v3_preservation_pass']],
        v3_rejection_counts=dict(risk_counts), v3_truncated=sum(r['truncated'] for r in generated.values()),
        v3_verbatim_quote_failures=[r['ID'] for r in rows if not r['v3_quotes_verbatim_preserved']],
        span_probe_counts=dict(collections.Counter(p['literal_probe_status'] for p in probes)),
        preliminary_literal_repairs=[p for p in probes if p['literal_probe_status'] == 'original_span_restored_v2_span_absent'],
        new_textual_risk_patterns=[p for p in spotchecks if not p['v2_risk_pattern_present'] and p['v3_risk_pattern_present']],
        original_anchors_lost_since_v2=[p for p in spotchecks if p['v2_anchor_present'] and not p['v3_anchor_present']],
        no_training=True, no_test_evaluation=True, external_llm_review='Pending, not performed', human_validation='Pending, not performed')
    m.dump('summary.json', summary)
    comparison_table = table(['ID', 'Original', 'New v2', 'New v3', 'v2 preservation', 'v3 preservation', 'v2 style', 'v3 style'],
        [[r[k] for k in ['ID', 'Original', 'New_v2', 'New_v3', 'v2_preservation_pass', 'v3_preservation_pass', 'v2_substantial_style', 'v3_substantial_style']] for r in rows])
    (OUT / 'COMPARISON_V2_V3_30.md').write_text('# Same 30 TRAIN originals — New Normalized v2 versus v3\n\nAutomatic flags/proxies only; not verified meaning or style.\n\n' + comparison_table + '\n', encoding='utf-8')
    package = ['# Review package — 30 TRAIN examples, v2 versus v3', '',
        'This diagnostic package exposes prior rewrites, automatic scores and style metrics. It is not blind. For a separate less-cued external review, use REVIEW_PACKAGE_BLIND_30.md, which contains only ID, Original and v3. No new external/human review has been filled. Existing v2 judgments must not transfer to v3.', '']
    blind = ['# New Normalized v3 — independent review input', '',
        '30 supplied text pairs. No reviewer judgments have been filled. Assess each Original against New Normalized v3; record reviewer/model, prompt and date separately. This is not Human Validation.', '']
    for idx, r in enumerate(rows, 1):
        package += [f"## {idx:02d} — {r['ID']}", '', '### Original', '', r['Original'], '', '### New v2', '', r['New_v2'], '', '### New v3', '', r['New_v3'], '']
        a, b = json.loads(r['v2_automatic_checks_json']), json.loads(r['v3_automatic_checks_json'])
        package += ['### Automatic checks — not human validation', '', table(['Field', 'v2', 'v3'], [[k, a.get(k, ''), b.get(k, '')] for k in dict.fromkeys([*a, *b])]), '']
        a, b = json.loads(r['v2_style_metrics_json']), json.loads(r['v3_style_metrics_json'])
        package += ['### Style metrics — operational proxies', '', table(['Metric', 'v2', 'v3'], [[k, a[k], b[k]] for k in a]), '']
        blind += [f"## {idx:02d} — {r['ID']}", '', '### Original', '', r['Original'], '', '### New Normalized v3', '', r['New_v3'], '']
    (OUT / 'REVIEW_PACKAGE_30.md').write_text('\n'.join(package), encoding='utf-8')
    (OUT / 'REVIEW_PACKAGE_BLIND_30.md').write_text('\n'.join(blind), encoding='utf-8')
    focused = ['creators:417181', 'creators:8b0d99b23d03', 'creators:423545', 'creators:298495', 'creators:418904', 'creators:423315']
    text = '''# Prompt Revision v3 — אותם 30 מקורות train בלבד

## תכנון מבוקר

ה־prompt של v2 נשמר בשלמותו ונוספה הרחבת הגנות ממוקדת: אפיון אירוע, עוצמה רטורית, ודאות בהקשר, תפקידי משתתפים, כמתים, ציטוטים verbatim, מטאפורות וללא פרשנות מומצאת. הקלט למודל כולל Original בלבד, לצד הוראות ה־prompt; בלי גרסאות קודמות, תוויות, כותבים, מדדים או דירוגי review. הדוגמאות בהרחבת ה־prompt הן הגנות שהתבקשו מתוך ניתוח שגיאות train, ולכן זהו ניסוי פיתוח על מקרים מוכרים ולא מבחן בלתי תלוי.

אותו Qwen2.5-3B-Instruct Q4_K_M קפוא, runtime, ארבעה slots, temperature=0, seed=20261026, max_tokens=320, repeat_penalty=1, top_k=1, top_p=1, min_p=0 ו־cache_prompt=True. מועמד יחיד לכל מקור; אין בחירה על פי ציונים ואין ניסיונות חוזרים לשיפור פלט. אותו קוד validator ואותם מודלי MPNet/NER/DeBERTa, ספי similarity≥0.85 ו־NLI≥0.6, בדיקות אורך/קטיעה ואותם מדדי style ו־66 מאפיינים מפורשים. לא הותאמו guards כדי לקבל מספרים במילים או חלופות לקסיקליות.

## תוצאות אוטומטיות בלבד

'''
    text += table(['Metric', 'v2', 'v3'], [[k, totals['v2'][k], totals['v3'][k]] for k in ['automatic_pass', 'substantial_style_proxy', 'both', 'exact_copies']])
    text += '\n\nמעבר בדיקות אינו הוכחה ל־semantic-safe, ו־substantial style הוא proxy. רק בדיקה חיצונית נפרדת יכולה לספק דירוגים חדשים; אין כאן ספירות No/Borderline עבור v3. לא נמדדו generalization, Macro-F1 או Author Identification חדשים.\n\n'
    text += f"נוספו {len(summary['automatic_pass_gained_ids'])} מעברים אוטומטיים לעומת v2: {', '.join(summary['automatic_pass_gained_ids'])}. אבד מעבר קודם ב־{', '.join(summary['automatic_pass_lost_ids']) or 'none'}. אין להציג את ההפרש נטו כתיקון של כל שגיאות ה־review.\n\n"
    text += 'שחזורים מילוליים נקודתיים מתוך ה־error analysis, ללא הכרעה על כל הרשומה: ' + '; '.join(p['ID'] + ': ' + p['original_span'] for p in summary['preliminary_literal_repairs']) + '. בכל המקרים האלה proxy הסגנון עדיין substantial.\n\n'
    text += f"קטיעות פלט: {summary['v3_truncated']}; הפרות דיאגנוסטיקת תוכן ציטוט verbatim: {len(summary['v3_verbatim_quote_failures'])}. כשל זה נרשם בנפרד ואינו משנה את guard הציטוטים הקיים.\n\n"
    text += '## הדוגמאות המרכזיות — בדיקות spans ראשוניות בלבד\n\n'
    text += table(['ID', 'תכונה', 'ביטוי מקור ב־v3', 'תבנית סיכון ב־v2', 'תבנית סיכון ב־v3', 'v3 pass', 'v3 style'],
        [[p[k] for k in ['ID', 'diagnostic', 'v3_anchor_present', 'v2_risk_pattern_present', 'v3_risk_pattern_present', 'v3_pass', 'v3_style']] for p in spotchecks])
    text += '\n\nהתבניות והביטויים מפורטים ב־[targeted_textual_spotchecks.csv](targeted_textual_spotchecks.csv). הן מסמנות תופעות טקסטואליות, לא פוסקות אם המשמעות נשמרה. היעלמות תבנית בעייתית בלי שחזור ביטוי המקור מחייבת בדיקה חיצונית.\n\n'
    text += 'ממצאים מילוליים לבדיקת ההמשך: ב־423545 ניתן לבדוק אם right-wing hack הוחזר, בלי להסיק שכל המטאפורה או דרגת הוודאות שוחזרו. ב־423315 יש לבדוק בנפרד riots/protests ו־going to/destined; ב־298495 את strangers/anonymous sources; וב־8b0d99b23d03 וב־418904 את הציטוטים עצמם. הופעה חדשה של branded, pseudonymous או typically surrendered on this day, אובדן Saturday/Sunday, או החזרת President Washington\'s Thanksgiving addresses במקום הכינוי his, מסומנים כחשדות חדשים לבדיקה בלבד. אין כאן שיפוט LLM חיצוני או הכרעת semantic drift סופית.\n\n'
    text += table(['ID', 'סיכון קודם', 'Original span', 'v2 span', 'תצפית מילולית ב־v3', 'v3 pass', 'v3 style'],
        [[p[k] for k in ['ID', 'prior_risk', 'original_span', 'v2_problem_span', 'literal_probe_status', 'v3_automatic_pass', 'v3_style']] for p in probes if p['ID'] in focused])
    text += '\n\noriginal_span_restored_v2_span_absent מציין שחזור מילולי של הביטוי שנפגע, לא פתרון סמנטי סופי. v2_span_still_present מציין שהביטוי הבעייתי עדיין מופיע; different_form_requires_external_review אינו אישור או פסילה. למקרי Borderline הקודמים ולסיכוני ה־FP/TN ראו [כל בדיקות ה־spans](focused_span_checks.csv).\n\n'
    text += '## דגלים שנפתרו או נוספו — לא הכרעת drift\n\n'
    text += table(['ID', 'Removed flags', 'Added flags', 'v2 pass', 'v3 pass', 'v3 style'], [[c[k] for k in ['ID', 'removed_flags', 'added_flags', 'v2_pass', 'v3_pass', 'v3_style']] for c in changes])
    text += '\n\n' + table(['v3 rejection reason', 'N (overlapping)'], sorted(risk_counts.items()))
    text += '''

## מה נפתר ומה עדיין לא ידוע

הסיכום נשען על spans ודגלים בלבד. אין לייחס שיפור סמנטי סופי להסרת דגל, או drift חדש להוספת דגל. קטעי Original/v2/v3 בשלמותם מופיעים בטבלת ההשוואה ובחבילת הבדיקה; תוכן חדש, omission או שינויי scope שאינם ב־spans המוגדרים מראש יכולים להישאר גם אחרי שחזור ביטוי. יש לעיין בהם בבדיקה החיצונית הבאה, בלי לשנות את ה־prompt שוב לפי התוצאות כאן.

## תוצרים ושחזור

- [כל 30 ההשוואות](COMPARISON_V2_V3_30.md) ו־[CSV](comparison_v2_v3_30.csv).
- [כל תוצאות ה־guards](rewrite_validation.csv), [מדדי style](style_metrics_v2_v3.csv), [66 מאפיינים לשתי הגרסאות](explicit_style_changes_v2_v3.csv).
- [חבילת הבדיקה המלאה](REVIEW_PACKAGE_30.md); היא מכילה ציונים ולכן אינה עיוורת.
- [חבילה ללא ציונים/גרסה קודמת/שמות כותבים](REVIEW_PACKAGE_BLIND_30.md) לשלב החיצוני הנפרד.
- [ה־prompt](prompt_v3.txt), [תוספות לעומת v2](prompt_delta.diff), [פרוטוקול](protocol.json), [סיכום](summary.json), [תקינות קלטים](integrity_audit.json), [בקשות Original-only](request_integrity_audit.json).

לא נכתבו דירוגי External LLM Review, לא בוצע Human Validation, לא הוזנו שדות human-review, לא בוצעו threshold tuning, guard changes, retraining, LoRA או test evaluation. כל הגרסאות והביקורות הקודמות נשמרו. עוצרים לפני בדיקה חיצונית נוספת.
'''
    (OUT / 'REPORT_HE.md').write_text(text, encoding='utf-8')
    unchanged(m)
    review = m.records(OUT / 'rewrite_human_review.csv')
    human_fields = ['facts_preserved', 'stance_preserved', 'framing_preserved', 'negation_preserved', 'certainty_preserved',
                    'attribution_preserved', 'entities_preserved', 'style_changed', 'acceptable', 'notes']
    assert all(not r[k] for r in review for k in human_fields)
    m.dump('integrity_audit.json', dict(passed=True, protected_files=protected_n, changed_files=[], n=30,
        same_originals=True, train_only=True, no_split_or_label_changes=True, all_old_versions_preserved=True,
        no_existing_human_review_fields_changed=True, new_review_fields_blank=True,
        unchanged_guard_code=True, same_style_definition_and_scaling=True, original_only_requests=True,
        no_training=True, no_test_evaluation=True, no_external_review=True))
    m.event('report_v3', n=30, summary_sha256=m.sha(OUT / 'summary.json'), protected_files_unchanged=protected_n)
    print(json.dumps(totals), flush=True)


if __name__ == '__main__':
    main()

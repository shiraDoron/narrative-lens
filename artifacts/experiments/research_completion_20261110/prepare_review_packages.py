"""Create independent and QC-assisted review views; never fill human answers."""

from collections import Counter
import difflib
import json
import re
import shutil

from common import HERE, COMPLETION, FOLLOW, RUN, candidates, dump, ensure_new_outputs, read, save, style_checks, style_scores, text_sha, verify
from bundle import make_pair_package

OUTPUTS = [
    'HUMAN_STYLE_REVIEW_105.md', 'HUMAN_STYLE_REVIEW_105.csv',
    'HUMAN_STYLE_REVIEW_105_QC_ASSISTED.md', 'PAIRED_QC_INTAKE_210.csv',
    'HUMAN_PARAPHRASE_REVIEW_105.md', 'NARRATIVE_LABEL_VALIDATION_105.md',
    'NARRATIVE_LABEL_VALIDATION_105.csv', 'NARRATIVE_LABEL_VALIDATION_43_VALIDATION.md',
    'NARRATIVE_LABEL_VALIDATION_43_VALIDATION.csv', 'COMPARISON_75_READABLE.md',
    'QC_FAILURE_TRIAGE_150.csv', 'REVIEW_PACKAGE_MANIFEST.json',
]


def edit_examples(original, rewrite):
    before, after = original.split(), rewrite.split()
    differences = []
    for tag, start, end, other_start, other_end in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag != 'equal':
            differences.append({'before': ' '.join(before[start:end]), 'after': ' '.join(after[other_start:other_end])})
    return json.dumps(differences[:4], ensure_ascii=False)


def quantifier_surface_counts(text):
    # Descriptive hints, never a new guard or acceptance threshold; no scope inference.
    vocabulary = {'all', 'every', 'each', 'most', 'many', 'some', 'few', 'only', 'both', 'none', 'everyone', 'always', 'never'}
    return Counter(word for word in re.findall(r'\b\w+\b', text.casefold()) if word in vocabulary)


def prepare():
    ensure_new_outputs(OUTPUTS)
    rows = candidates()
    checks = style_checks()
    scores = style_scores()
    make_pair_package(rows, HERE / 'HUMAN_STYLE_REVIEW_105', expected=105)
    blind_text = (HERE / 'HUMAN_STYLE_REVIEW_105.md').read_text(encoding='utf-8')
    assisted = blind_text.replace(
        '# בדיקת שימור ושינוי סגנון — חבילה עצמאית',
        '# סקירת שכתוב סגנוני — חבילה בסיוע QC (אינה עיוורת)', 1,
    )
    assisted = assisted.replace('\n\n', '\n\nסימוני הסיכון בהמשך אוטומטיים בלבד; אינם הכרעת אדם. קריאת קובץ זה מבטלת עיוורון ל־QC. מומלץ לבצע תחילה סקירה באמצעות הגרסה העצמאית.\n\n', 1)
    for row in rows:
        result = checks[row['ID']]
        flags = result['rejection_reasons'].replace('|', ', ') or 'אין דגלי פסילה; עדיין נדרשת הכרעת אדם'
        if scores[row['ID']]['substantial_style_change'] != 'True':
            flags += '; style proxy below existing substantial rule — לבדיקה אנושית, לא הכרעה'
        header = '## ' + row['ID']
        assisted = assisted.replace(header + '\n', header + '\n\n**סימני סיכון אוטומטיים בלבד:** ' + flags + '\n', 1)
    (HERE / 'HUMAN_STYLE_REVIEW_105_QC_ASSISTED.md').write_text(assisted, encoding='utf-8')

    pair_intake = []
    paraphrase_md = ['# סקירה אנושית עצמאית — 105 פרפרזות', '',
                     'למלא את PAIRED_QC_INTAKE_210.csv בשורות Paraphrase. כאן מוצגים רק זוגות המקור/פרפרזה, ללא מחבר, תוויות, ציונים או דגלים. אין לשנות טקסטים. Yes / No / Borderline; פרטי סוקר ותאריך חובה.', '']
    for row in rows:
        for variant in ['Style', 'Paraphrase']:
            pair_intake.append(dict(
                ID=row['ID'], variant=variant, Original=row['Original'], Rewrite=row[variant],
                source_sha256=text_sha(row['Original']), rewrite_sha256=text_sha(row[variant]),
                meaning='', stance='', style_change='', semantic_drift='',
                reviewer_type='', reviewer_id='', review_date='', notes='',
            ))
        paraphrase_md += [f"## {row['ID']}", '', '### Original', '', row['Original'], '',
                          '### Paraphrase', '', row['Paraphrase'], '',
                          '| field | answer |', '|---|---|',
                          '| meaning | |', '| stance | |', '| semantic_drift | |', '| notes | |', '']
    save(HERE / 'PAIRED_QC_INTAKE_210.csv', pair_intake)
    (HERE / 'HUMAN_PARAPHRASE_REVIEW_105.md').write_text('\n'.join(paraphrase_md), encoding='utf-8')

    for suffix in ['md', 'csv']:
        shutil.copyfile(COMPLETION / f'NARRATIVE_LABEL_VALIDATION_105.{suffix}', HERE / f'NARRATIVE_LABEL_VALIDATION_105.{suffix}')
    guide = (COMPLETION / 'LABEL_GUIDE_HE.md').read_text(encoding='utf-8')
    validation = [row for row in read(FOLLOW / 'analysis_cohort.csv') if row['split'] == 'val']
    assert len(validation) == 43
    intake = [dict(ID=row['row_id'], Original=row['text'], proposed_label=row['narrative_name'],
                  human_label='', proposed_label_correct='', evidence_span='', human_notes='',
                  reviewer_type='', reviewer_id='', review_date='') for row in validation]
    save(HERE / 'NARRATIVE_LABEL_VALIDATION_43_VALIDATION.csv', intake)
    label_md = ['# אימות תוויות — 43 מקורות validation בלבד', '', guide, '',
                'המקורות הם validation המקורי בלבד, ללא שכתוב או שינוי split. אין כאן test.', '']
    for row in intake:
        label_md += [f"## {row['ID']}", '', row['Original'], '',
                     f"**תווית מוצעת בלבד, לא gold:** {row['proposed_label']}", '',
                     '| field | answer |', '|---|---|']
        label_md += [f'| {field} | |' for field in ['human_label', 'proposed_label_correct', 'evidence_span', 'human_notes', 'reviewer_type', 'reviewer_id', 'review_date']]
        label_md.append('')
    (HERE / 'NARRATIVE_LABEL_VALIDATION_43_VALIDATION.md').write_text('\n'.join(label_md), encoding='utf-8')

    comparison = read(RUN / 'QC_COMPARISON_BY_ID_75.csv')
    readable = ['# השוואה לקריאה — כל 75 המקורות החדשים', '',
                'זהו דוח ניתוח עם QC, לא חבילה עיוורת ולא אימות אנושי. הטקסטים מוצגים כפי שהתקבלו.', '']
    triage = []
    categories = {
        'bidirectional_nli': 'semantic_risk', 'similarity': 'semantic_risk',
        'certainty': 'certainty_risk', 'future_tense': 'temporal_or_modality_risk',
        'numbers': 'number_risk', 'entities': 'entity_risk', 'quotations': 'quote_fidelity_risk',
        'attribution': 'attribution_risk', 'framing_anchors': 'framing_or_intensity_risk',
        'negation': 'negation_scope_review',
    }
    for row in comparison:
        readable += [f"## {row['ID']}", '', '### Original', '', row['Original'], '',
                     '### Style Rewrite', '', row['Style_Rewrite'], '', '### Paraphrase', '', row['Paraphrase'], '',
                     '**דגלי Style:** ' + (row['Style_rejection_reasons'].replace('|', ', ') or 'אין'), '',
                     '**דגלי Paraphrase:** ' + (row['Paraphrase_rejection_reasons'].replace('|', ', ') or 'אין'), '']
        for method, text_key in [('Style', 'Style_Rewrite'), ('Paraphrase', 'Paraphrase')]:
            reasons = list(filter(None, row[method + '_rejection_reasons'].split('|')))
            risks = sorted({categories.get(reason, 'technical_or_completeness_risk') for reason in reasons})
            if row[method + '_substantial_style_change'] != 'True':
                risks.append('style_proxy_below_rule')
            original_counts = quantifier_surface_counts(row['Original'])
            rewrite_counts = quantifier_surface_counts(row[text_key])
            triage.append(dict(
                ID=row['ID'], method=method, automatic_pass=row[method + '_passed'],
                failed_guards='|'.join(reasons), risk_categories='|'.join(risks),
                semantic_drift_status='not adjudicated', rhetorical_intensity_status='not independently measured',
                quantifier_surface_difference=original_counts != rewrite_counts,
                quantifiers_original=json.dumps(original_counts, ensure_ascii=False, sort_keys=True),
                quantifiers_rewrite=json.dumps(rewrite_counts, ensure_ascii=False, sort_keys=True),
                quantifier_hint_is_not_a_guard=True,
                edit_examples=edit_examples(row['Original'], row[text_key]),
                Original=row['Original'], Rewrite=row[text_key],
            ))
    (HERE / 'COMPARISON_75_READABLE.md').write_text('\n'.join(readable), encoding='utf-8')
    save(HERE / 'QC_FAILURE_TRIAGE_150.csv', triage)
    dump(HERE / 'REVIEW_PACKAGE_MANIFEST.json', dict(
        style_pairs=105, paraphrase_pairs=105, source_labels_train=105, source_labels_validation=43,
        human_answers_filled=0, ratings_inferred_from_llm=False, test_texts_exported=0,
        assisted_review_is_blind=False, independent_review_contains_qc=False,
        quantifier_hints_are_descriptive_not_new_guards=True,
    ))
    verify()


if __name__ == '__main__':
    prepare()

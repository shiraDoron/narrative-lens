"""Descriptive AI+existing-QC grouping only; this never approves scientific data."""

from collections import Counter

from contract import HERE, RESEARCH, candidates, read, save, dump, sha, assert_frozen
from common import style_checks, style_scores


def report():
    assert_frozen()
    ai_path = RESEARCH / 'ai_review_audit_105_20261110/AI_REVIEW_ALL_105.csv'
    ai = {row['ID']: row for row in read(ai_path)}
    checks, styles = style_checks(), style_scores()
    records = []
    for source in candidates():
        rid = source['ID']
        review = ai[rid]
        if review['Original'] != source['Original'] or review['Style_Rewrite'] != source['Style']:
            raise ValueError('AI review text binding mismatch')
        ratings = [review[key] for key in ['ai_meaning_preserved', 'ai_narrative_preserved', 'ai_style_change_valid']]
        semantic_concern = any(review[key] == 'No' for key in ['ai_meaning_preserved', 'ai_narrative_preserved'])
        automatic_pass = checks[rid]['passed'] == 'True'
        substantial = styles[rid]['substantial_style_change'] == 'True'
        if semantic_concern:
            group = 'ai_substantial_semantic_concern'
        elif ratings == ['Yes', 'Yes', 'Yes'] and automatic_pass and substantial:
            group = 'all_available_ai_and_automatic_checks_passed'
        else:
            group = 'borderline_or_unresolved_quality'
        records.append(dict(
            ID=rid, source_split='train', quality_group=group,
            ai_meaning=ratings[0], ai_narrative=ratings[1], ai_style=ratings[2],
            automatic_preservation_pass=automatic_pass, substantial_style_proxy=substantial,
            failed_guards=checks[rid]['rejection_reasons'], ai_risk_types=review['ai_risk_types'],
            ai_notes=review['ai_notes'], human_validation_status='pending',
            scientifically_accepted=False, cohort=source['style_protocol_cohort'],
        ))
    counts = dict(Counter(row['quality_group'] for row in records))
    save(HERE / 'QUALITY_GROUPS_105.csv', records)
    dump(HERE / 'QUALITY_SUMMARY.json', dict(
        n=105, groups=counts, human_validated=0, scientific_acceptance_applied=False,
        ai_source_sha256=sha(ai_path), original_guards_and_thresholds_unchanged=True,
        grouping_not_used_for_training=True,
    ))
    lines = ['# איכות105 הזוגות — מידע לפיתוח, לא אישור אימון', '',
             'כל105 נשמרים. הקבוצות הבאות משלבות את סקירת ה־AI עם ה־guards ומדד הסגנון הקיימים, ללא שינוי ספים:', '',
             '| קבוצה | מספר | פירוש |', '|---|---:|---|',
             f"| עברו את כל בדיקות ה־AI והבדיקות האוטומטיות הזמינות | {counts.get('all_available_ai_and_automatic_checks_passed',0)} | שלושה Yes ב־AI, מעבר guards ו־substantial style; אימות אדם עדיין חסר |",
             f"| גבוליים / איכות לא פתורה | {counts.get('borderline_or_unresolved_quality',0)} | Borderline ב־AI, כשל אוטומטי או style לא מספיק; אינו בהכרח drift |",
             f"| חשש מהותי סמנטי לפי AI | {counts.get('ai_substantial_semantic_concern',0)} | Meaning או Narrative=No ב־AI; לא הכרעת אדם |", '',
             'זו קבוצת דיווח תיאורית, לא שינוי לכלל הקבלה הקפוא. גם הקבוצה הראשונה אינה “עברה את כל דרישות המחקר”: חסרים human labels ו־human pair QC. תוצאות AI אינן מועתקות לשדות האדם או ל־gold. קובץ QUALITY_GROUPS_105.csv מפרט כל ID, דגלים ונימוק.', '',
             'לפרפרזות נדרש QC אנושי נפרד. סקירת105 ה־AI עוסקת ב־Style בלבד; אין להסיק ממנה אישור לפרפרזות. המדיניות המדעית נבנית רק מחוזה QC האנושי הקיים, עם fallback סימטרי ו־secondary common accepted.', '',
             'שלושים שכתובים ישנים ו־75 חדשים הם cohorts שונים של יצירה. grouping אינו benchmark של גנרטורים, אינו זיהוי shortcut ואינו תוצאת הכללה.']
    (HERE / 'QUALITY_REPORT_HE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(counts)


if __name__ == '__main__':
    report()

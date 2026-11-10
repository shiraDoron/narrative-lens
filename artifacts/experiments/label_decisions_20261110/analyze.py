"""Read-only construct audit and hypothetical attrition, not a new labeling pass."""
from collections import Counter
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'artifacts/experiments/research_completion_20261110'))
from common import FOLLOW, read, save, sha, text_sha, verify

AI = ROOT / 'artifacts/experiments/ai_preliminary_intake_20261110/raw/LABELS_148_AI_PRELIMINARY.csv'
PAIRS = ROOT / 'artifacts/experiments/ai_preliminary_intake_20261110/raw/PAIRS_210_AI_DIAGNOSTIC.csv'
FORMS = ROOT / 'artifacts/experiments/human_validation_handoff_20261110/forms'
GROUPS = {
    'insufficient_ideological_anchor': ('עוגן אידאולוגי חסר בקטע',
        'תיאור היסטורי/ספרותי או אנקדוטה; רגש/נושא אינם מזהים מחנה באופן ייחודי. מועמד לדיון על insufficient evidence, לא תווית אדם.',
        '0b4c49505392 421951 208496 8b0d99b23d03'),
    'shared_value_not_unique': ('ערך משותף שאינו מבחין לבדו',
        'שוויון בפני חוק, חיסכון, שותפות או התנגדות לקניית קולות אינם בלעדיים למחנה; יש לבדוק את המסגור המקומי ולא להשלים זהות כותב.',
        '423153 92de8fae2e8e 415612 424229'),
    'intra_camp_criticism': ('ביקורת פנים־מחנאית',
        'ביקורת על מפלגה/מועמד מאותו מחנה אפשרי אינה ראיה אוטומטית למחנה היריב; יש לזהות את עקרון הביקורת.',
        '417479 419420 420217'),
    'reported_position_scope': ('הפרדה בין דובר, ייחוס ואימוץ עמדה',
        'חלק מהעמדות מיוחסות לאחר; ההכרעה תלויה בשאלה מה המספר מאמץ או מגנה. אין לתייג על סמך הציטוט בלבד.',
        '120669 424146 421241 401668 423930'),
    'policy_cues_need_codebook': ('רמזי מדיניות/אידאולוגיה — תלות ב-codebook',
        'קיימים רמזים שעשויים לתמוך בהצעה לפי ההגדרות; Unclear באבחון החדש אינו מוכיח שאין די ראיות. נדרשת הכרעת אדם עקבית על נימוק ועמדה, לא נושא בלבד.',
        '217678 419965 421024 117645 120177 212505 218236 417610 418022 418620 421853 422331 459e183c1d0d 418554 f7e6a21fe1ee 421101'),
    'satire_and_metaphor': ('סאטירה ומטאפורה',
        'קשר בין הלעג לבין עקרון פוליטי דורש קריאה; חלק מהקטעים דווקא מכילים רמזים חזקים. אין לפרש חריפות כשמאל/ימין או עמימות מכונה כעמימות ודאית.',
        '3fd01161cd76 420909 417456 420447 423635 423915 403504'),
    'context_or_excerpt_dependency': ('קטע חלקי/תלות בהקשר',
        'רמזים דיאקטיים, תחילת סיפור או הערכה שאינה מפורשת במלואה מגבילים פרשנות. אין להשלים מאמר שלם או ביוגרפיה כחלק מהתיוג הנוכחי.',
        '416232 421279 422298 8cc716b411c9 421849 7b85c8cb96fd'),
}


def sources():
    verify()
    rows = read(AI)
    annotations = {r['row_id']: r for r in read(FOLLOW / 'text_annotations.csv')}
    return rows, annotations


def categorized():
    rows, annotations = sources()
    ambiguous = [r for r in rows if r['ai_candidate_label'] == 'Unclear']
    manual = {}
    for category, (name, explanation, ids) in GROUPS.items():
        for suffix in ids.split():
            identity = 'creators:' + suffix
            assert identity not in manual
            manual[identity] = category, name, explanation
    missing = {r['ID'] for r in ambiguous} - set(manual)
    # Remaining inspected cases share target-based criticism/praise, rather
    # than a new inferred label. Their exact IDs are persisted in the output.
    target_name = 'עמדה כלפי יעד אינה אידאולוגיה מלאה'
    target_reason = 'הקטע מביע שבח/גינוי כלפי אדם, מוסד או פעולה; אין לזהות אוטומטית יחס ליעד עם אידאולוגיה כוללת. האדם יבדוק אם קיימת גם הצדקה מבחינה בטקסט.'
    for identity in missing:
        manual[identity] = 'target_vs_ideology', target_name, target_reason
    assert set(manual) == {r['ID'] for r in ambiguous}
    output = []
    for row in ambiguous:
        category, name, reason = manual[row['ID']]
        text = row['Original']
        # A literal context excerpt, not automatically evidence for a label.
        excerpt = text[:min(len(text), 240)]
        output.append(dict(ID=row['ID'], split=row['split'], author=annotations[row['ID']]['author'],
                           proposed_label=row['proposed_label'], Original=text, source_sha256=row['source_sha256'],
                           primary_ambiguity_category=category, category_he=name, rationale=reason,
                           context_excerpt=excerpt, excerpt_is_label_evidence=False,
                           no_unique_content_anchor_candidate=category == 'insufficient_ideological_anchor',
                           is_human_annotation=False, label_changed=False))
    return output


def scenarios():
    rows, annotations = sources()
    unclear = {r['ID'] for r in rows if r['ai_candidate_label'] == 'Unclear'}
    narrow = {r['ID'] for r in categorized() if r['no_unique_content_anchor_candidate']}
    definitions = [('unchanged_frozen_cohort', set()), ('exclude_all_67_hypothetical', unclear),
                   ('exclude_train_43_only', {r['ID'] for r in rows if r['split'] == 'train' and r['ID'] in unclear}),
                   ('exclude_validation_24_only', {r['ID'] for r in rows if r['split'] == 'validation' and r['ID'] in unclear}),
                   ('exclude_4_anchor_candidates_only', narrow)]
    summary, authors = [], []
    for scenario, removed in definitions:
        kept = [r for r in rows if r['ID'] not in removed]
        by_split = {s: [r for r in kept if r['split'] == s] for s in ('train', 'validation')}
        train, val = by_split['train'], by_split['validation']
        n = len(train)
        summary.append(dict(scenario=scenario, train_sources=n, validation_sources=len(val),
                            train_Left=sum(r['proposed_label'] == 'Left-wing' for r in train),
                            train_Right=sum(r['proposed_label'] == 'Right-wing' for r in train),
                            validation_Left=sum(r['proposed_label'] == 'Left-wing' for r in val),
                            validation_Right=sum(r['proposed_label'] == 'Right-wing' for r in val),
                            train_authors=len({annotations[r['ID']]['author'] for r in train}),
                            validation_authors=len({annotations[r['ID']]['author'] for r in val}),
                            A=n, B=n, C=n, D=2*n, E=2*n,
                            formula_updates_if_new_protocol_approved=20*math.ceil(n/16),
                            existing_105_runtime_updates=140,
                            new_protocol_required=bool(removed), applied=False))
        for split in ('train', 'validation'):
            for author in sorted({annotations[r['ID']]['author'] for r in rows if r['split'] == split}):
                group = [r for r in by_split[split] if annotations[r['ID']]['author'] == author]
                authors.append(dict(scenario=scenario, split=split, author=author, retained=len(group),
                                    Left=sum(r['proposed_label']=='Left-wing' for r in group),
                                    Right=sum(r['proposed_label']=='Right-wing' for r in group)))
    return summary, authors


def main():
    cases = categorized()
    save(HERE / 'AMBIGUITY_REASONS_67.csv', cases)
    summary, authors = scenarios()
    save(HERE / 'SCENARIOS.csv', summary)
    save(HERE / 'SCENARIOS_BY_AUTHOR.csv', authors)
    counts = Counter(r['category_he'] for r in cases)
    lines = ['# 67 תוויות Unclear — מיון סיבות, לא תיוג מחדש', '',
             'המיון הוא ניתוח מבנה המשימה בידי ChatGPT/Codex, לא עוד סבב ציוני AI, '
             'לא הכרעת אדם ולא קביעה שהתוויות שגויות. קטגוריה ראשית אחת לכל ID; '
             'כמה מקורות עמימות יכולים לחפוף. חלק מה-Unclear מכילים רמזי codebook חזקים.', '',
             '| סיבה ראשית | מספר |', '|---|---:|']
    lines += [f'| {name} | {count} |' for name, count in counts.items()]
    lines += ['', '| ID | split | סיבה | קטע הקשר מדויק (אינו בהכרח ראיה לתווית) | משמעות לבדיקה |', '|---|---|---|---|---|']
    for row in cases:
        lines.append('| ' + ' | '.join(str(row[k]).replace('|', '&#124;').replace('\n', '<br>')
                                       for k in ('ID', 'split', 'category_he', 'context_excerpt', 'rationale')) + ' |')
    (HERE / 'AMBIGUITY_ANALYSIS_HE.md').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    a = next(r for r in read(PAIRS) if r['ID']=='creators:0105f26ef9f1' and r['variant']=='Paraphrase')
    b = next(r for r in read(FORMS/'PAIRS_210.csv') if r['ID']==a['ID'] and r['variant']==a['variant'])
    hash_audit = dict(ID=a['ID'], variant=a['variant'], supplied_hash=a['rewrite_sha256'],
                      canonical_text_sha256=text_sha(b['Rewrite']), received_text_sha256=text_sha(a['Rewrite']),
                      received_crlf_count=a['Rewrite'].count('\r\n'), canonical_crlf_count=b['Rewrite'].count('\r\n'),
                      equal_only_after_documented_crlf_to_lf_comparison=a['Rewrite'].replace('\r\n','\n')==b['Rewrite'],
                      normalization_applied_to_data=False)
    (HERE / 'NEWLINE_DIAGNOSTIC.json').write_text(json.dumps(hash_audit,indent=2)+'\n',encoding='utf-8',newline='\n')
    inputs = [AI, PAIRS, FORMS/'PAIRS_210.csv', FORMS/'LABELS_148.csv', FOLLOW/'text_annotations.csv',
              FOLLOW/'assemble_annotations.py', FOLLOW/'annotation_method.json', ROOT/'MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md']
    manifest = dict(ambiguity_counts=dict(counts), scenario_count=len(summary),
                    no_data_changed=True, test_evaluated=False,
                    source_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs})
    (HERE / 'PROVENANCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(counts),ensure_ascii=False))
    print(json.dumps(summary,ensure_ascii=False))


if __name__ == '__main__':
    main()

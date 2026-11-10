"""Rebuild the focused AI audit from manual findings and existing scores only.

No inference, generation, training, label import, or acceptance operation exists here.
Lexical diagnostics execute only selected pure functions from frozen source ASTs.
"""
import ast
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import ROOT, candidates, read, save, style_checks, style_scores, verify
from findings import findings

GROUPS = ROOT / 'artifacts/experiments/main_training_runtime_20261110/QUALITY_GROUPS_105.csv'
REVIEWS = HERE.parent / 'ai_review_audit_105_20261110/AI_REVIEW_ALL_105.csv'
GUARD_SOURCE = ROOT / 'artifacts/experiments/verified_human_style_followup_20261026/experiment.py'
BASE_SOURCE = ROOT / 'experiments/author_generalization/author_style_controlled.py'
NAMES = {
    'ai_identified_difference': 'הבדל סמנטי מזוהה בקריאת AI',
    'unresolved_semantic_risk': 'סיכון סמנטי שלא הוכרע גם בקריאה חוזרת',
    'qc_signal_only': 'דגל QC ללא הבדל משמעות מזוהה בקריאת AI',
    'style_limited': 'משמעות ללא שינוי מזוהה; סגנון מוגבל',
    'quote_fidelity_only': 'נאמנות ציטוט בלבד, ללא drift מזוהה',
    'style_proxy_disagreement': 'פער בין proxy לסגנון בקריאה',
    'prior_reservation_resolved': 'הסתייגות AI קודמת לא נתמכת בקריאת ההקשר',
}


def pure_functions(path, names):
    """Compile only named functions; never import the model-bearing module."""
    tree = ast.parse(path.read_text(encoding='utf-8'))
    nodes = [node for node in ast.walk(tree)
             if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != set(names) or len(nodes) != len(names):
        raise ValueError('Missing or ambiguous frozen helper functions')
    scope = {'re': re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)
    return scope


def lexical_diagnostics(original, rewrite):
    funcs = pure_functions(GUARD_SOURCE, {'neg', 'future', 'quotations'})
    words = pure_functions(BASE_SOURCE, {'words'})['words']
    tree = ast.parse(BASE_SOURCE.read_text(encoding='utf-8'))
    lexicons = {node.targets[0].id: ast.literal_eval(node.value)
                for node in tree.body if isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in {'CERT', 'ATTR', 'FRAME'}}
    pair = {}
    for name in ('neg', 'future', 'quotations'):
        pair[name] = [funcs[name](original), funcs[name](rewrite)]
    for name, lexicon in lexicons.items():
        pair[name] = [sorted(words(text) & lexicon) for text in (original, rewrite)]
    pair['numbers'] = [sorted(set(re.findall(r'\b\d+(?:[.,]\d+)*\b', text)))
                       for text in (original, rewrite)]
    flags = {
        'negation': len(pair['neg'][0]) == len(pair['neg'][1]),
        'certainty': pair['CERT'][0] == pair['CERT'][1],
        'attribution': bool(pair['ATTR'][0]) == bool(pair['ATTR'][1]),
        'framing_anchors': pair['FRAME'][0] == pair['FRAME'][1],
        'future_tense': pair['future'][0] == pair['future'][1],
        'quotations': pair['quotations'][0] == pair['quotations'][1],
        'numbers': pair['numbers'][0] == pair['numbers'][1],
    }
    return pair, flags


def build_rows():
    verify()
    canonical = {row['ID']: row for row in candidates()}
    old = {row['ID']: row for row in read(REVIEWS)}
    scores, metrics, manual = style_checks(), style_scores(), findings()
    selected = [row for row in read(GROUPS)
                if row['quality_group'] != 'all_available_ai_and_automatic_checks_passed']
    assert len(selected) == 64 and {r['ID'] for r in selected} == set(manual)
    output = []
    for group in selected:
        identity = group['ID']
        prior, source, qc = old[identity], canonical[identity], scores[identity]
        original, rewrite = prior['Original'], prior['Style_Rewrite']
        assert (original, rewrite) == (source['Original'], source['Style'])
        detail, flags = lexical_diagnostics(original, rewrite)
        for key, value in flags.items():
            assert str(value) == qc['guard_' + key], (identity, key, value, qc['guard_' + key])
        changed = [f'{tag}: {" ".join(a[i:j])} → {" ".join(b[k:l])}'
                   for a, b in [(original.split(), rewrite.split())]
                   for tag, i, j, k, l in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
                   if tag != 'equal']
        row = {'ID': identity, 'prior_quality_group': group['quality_group'],
               'Original': original, 'Style_Rewrite': rewrite,
               'prior_ai_meaning': group['ai_meaning'], 'prior_ai_narrative': group['ai_narrative'],
               'prior_ai_style': group['ai_style'], 'prior_ai_notes': prior['ai_notes'],
               'automatic_preservation_pass': qc['passed'], 'failed_guards': qc['rejection_reasons'],
               'semantic_similarity': qc['semantic_similarity'],
               'entailment_forward': qc['entailment_forward'], 'entailment_reverse': qc['entailment_reverse'],
               'original_entities': qc['original_entities'], 'rewrite_entities': qc['rewrite_entities'],
               'substantial_style_proxy': group['substantial_style_proxy'],
               'style_metrics_json': json.dumps(metrics[identity], ensure_ascii=False),
               'lexical_guard_diagnostics_json': json.dumps(detail, ensure_ascii=False),
               'exact_word_diff_json': json.dumps(changed, ensure_ascii=False),
               **manual[identity], 'second_reading_completed': True,
               'reviewer': 'ChatGPT/Codex; exact model revision unknown',
               'review_date': '2026-11-10', 'review_type': 'QC-assisted AI critique, same-assistant second reading',
               'blind_review': False, 'is_human_review': False, 'changes_acceptance': False}
        output.append(row)
    return output


def main():
    rows = build_rows()
    save(HERE / 'FOCUSED_QUALITY_REVIEW_64.csv', rows)
    index = ['# טבלת ממצאים לפי ID', '',
             'ביקורת AI בלבד, לא החלטת קבלה. טקסטים וציונים מלאים ב-CASE_ANALYSIS_64_HE.md וב-CSV.', '',
             '| ID | קבוצה קודמת | הבדל | ממצא | המשך מומלץ |', '|---|---|---|---|---|']
    for row in rows:
        cells = [row[key].replace('|', '&#124;').replace('\n', ' ')
                 for key in ('ID', 'prior_quality_group', 'contrast', 'finding', 'recommendation')]
        index.append('| ' + ' | '.join(cells) + ' |')
    (HERE / 'CASE_TABLE_64_HE.md').write_text('\n'.join(index) + '\n', encoding='utf-8')
    counts = Counter(row['disposition'] for row in rows)
    lines = ['# ביקורת איכות ממוקדת — 64 זוגות train', '',
             'ביקורת AI של ChatGPT/Codex (גרסת מודל מדויקת לא ידועה), 10.11.2026. '
             'הביקורת אינה עיוורת ואינה אימות אנושי. הקריאה החוזרת בוצעה בידי אותו עוזר; '
             'אין כאן agreement בין סוקרים עצמאיים. 57+7 הם קבוצות הבחירה הקודמות, לא תוצאות חדשות.', '',
             'הטקסטים, דירוגי AI קודמים וציוני QC נשמרו. האבחון הלקסיקלי שוחזר מהקוד הקפוא '
             'והושווה לכל הדגלים השמורים; NLI/NER לא הורצו מחדש. כמתים, scope, ייחוס ועוצמה '
             'נבדקו בקריאה של המשפטים המלאים, לא מתוך רשימת מילים בלבד.', '']
    for row in rows:
        lines += [f"## {row['ID']}", '', '| Original | Style Rewrite |', '|---|---|',
                  f"| {row['Original'].replace('|', '&#124;')} | {row['Style_Rewrite'].replace('|', '&#124;')} |", '',
                  f"**קודם:** {row['prior_quality_group']}; Meaning={row['prior_ai_meaning']}; "
                  f"Narrative={row['prior_ai_narrative']}; Style={row['prior_ai_style']}.", '',
                  f"**נימוק AI קודם:** {row['prior_ai_notes']}", '',
                  f"**QC שמור:** passed={row['automatic_preservation_pass']}; "
                  f"failed={row['failed_guards'] or 'none'}; similarity={row['semantic_similarity']}; "
                  f"NLI forward/reverse={row['entailment_forward']}/{row['entailment_reverse']}; "
                  f"style substantial={row['substantial_style_proxy']}.", '',
                  f"**הבדל ממוקד:** {row['contrast']}", '',
                  f"**ממצא וקשר לדגלים:** {row['finding']}", '',
                  f"**קריאה חוזרת:** {row['second_reading']}", '',
                  f"**סיווג אנליטי:** {NAMES[row['disposition']]}", '',
                  f"**המשך מומלץ:** {row['recommendation']}", '',
                  '<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>', '',
                  '```json', json.dumps(json.loads(row['lexical_guard_diagnostics_json']), ensure_ascii=False, indent=2),
                  '```', '', '</details>', '']
    (HERE / 'CASE_ANALYSIS_64_HE.md').write_text('\n'.join(lines), encoding='utf-8')
    table = '\n'.join(f'| {NAMES[key]} | {counts[key]} |' for key in NAMES)
    unresolved = [r['ID'] for r in rows if r['disposition'] == 'unresolved_semantic_risk']
    identified = [r['ID'] for r in rows if r['disposition'] == 'ai_identified_difference']
    summary = f'''# סיכום ביקורת איכות ממוקדת — 64 זוגות

## מה נבדק

כל 57 הזוגות בקבוצת borderline_or_unresolved_quality וכל 7 הזוגות בקבוצת ai_substantial_semantic_concern. לא נבחרו רק הצלחות. 41 הזוגות האחרים לא נבדקו מחדש בשלב זה; גם הם אינם מאומתים אנושית. כל זוג נבדק מול המקור, השכתוב, ציוני QC והנימוקים הקודמים, ולאחר מכן נקרא שוב. זהו ניתוח AI מסייע QC של ChatGPT/Codex, לא Claude, לא סקירה עיוורת ולא Human Validation. [טבלה לפי ID](CASE_TABLE_64_HE.md), [ניתוח זוגות מלא](CASE_ANALYSIS_64_HE.md), [CSV מפורט](FOCUSED_QUALITY_REVIEW_64.csv).

## תוצאות אנליטיות, לא החלטות קבלה

| קטגוריה ראשית, בלעדית | מספר |
|---|---:|
{table}
| סך הכול | 64 |

הסיווג הראשי מונע ספירה כפולה: במקרה עם סיכון סמנטי וגם חריגת ציטוט מופיע רק הסיכון הסמנטי בטבלה. פירוט הדגלים וכל הממצאים המשניים נמצא ב-CSV ובדוח המלא. “ללא הבדל מזוהה” אינו הוכחה לשימור. “סיכון” אינו הוכחה ל-drift. גם סטייה מפיסוק ציטוט אינה מוכיחה שינוי טענה, אך היא הפרת דרישת verbatim ואינה false positive חוזי.

**{len(identified)} הבדלים מזוהים בקריאת AI:** {', '.join(identified)}.

**{len(unresolved)} סיכונים שלא הוכרעו גם בקריאה חוזרת:** {', '.join(unresolved)}.

יש אפוא {len(identified) + len(unresolved)} מקרים עם הבדל או סיכון סמנטי שעדיין דורשים הכרעה אנושית; בנוסף יש שאלות סגנון ונאמנות ציטוט המפורטות בנפרד. אין להסיק שהאחרים התקבלו לאימון.

## הממצאים המרכזיים

- כמתים ומודאליות: No one→Few people ו-will→can הם הבדלים ממשיים בנוסח; may→could אינו מוכיח הבדל כזה. גם don't have to→not supposed to משנה נורמה, אף ש-QC לא אבחן זאת במדויק.
- ייחוס ו-scope: 424146 מוסיף בעל אחר לאפיון; 420909 מוסיף תהייה של המספר עצמו. attribution Boolean יכול להישאר זהה כשהבעלים משתנים.
- זמן ויחסים: 0b4c49505392 מצמיד אותם תאריך ומקום לפעולה אחרת. זהות ישויות ומספרים אינה מספיקה. ב-11db638844f4 ה-No הקודם נחרץ מדי: before מול not since הוא סיכון שלא הוכרע, ולא סתירה מוכחת.
- השמטה ועוצמה: 421279 משמיט מאמץ מרבי ויום/לילה. העמדה הכללית נשארת אך היקף האשמה נחלש; נדרש אדם. מטאפורות, תכלית מול תוצאה, if/when והדגשת only נשארו בחלקם גבוליים.
- כשלים לקסיקליים: not long after→shortly after, didn't want→unwilling, must→requires, murder→murdering, ו-backshift will→would יכולים לשמר משמעות. United States מפעיל בטעות את מילת הייחוס states. אלו מגבלות אותות, לא היתר לשנות guards בדיעבד.
- NLI אינו שופט: ב-417661 נומינליזציה משמרת את רשימת המעשים בקריאת AI למרות פער NLI חריף. similarity נמוך אינו מסביר לבדו איזה claim השתנה.
- סגנון: קטעים כמעט מועתקים עדיין בעייתיים להתערבות גם כשהמשמעות נשמרת. ב-222877 וב-415758 ניכר שינוי ארגון שאינו עובר proxy; הסף חושב לפי הכלל הקיים ולא כוונן.

## בדיקה חוזרת ושינויי מסקנה מקומיים

ההערכות הישנות לא שונו. בניתוח החדש הסתייגויות 417181, 209914 ו-114783 אינן נתמכות די הצורך בקריאת ההקשר; ב-422791, 420447 ו-415881 נותר בעיקר אות לקסיקלי; 423153 נשאר חריגת fidelity. מנגד 421279 מצדיק חשש מפורש להשמטת עוצמה. 11db638844f4 הועבר אנליטית מ-No קודם לסיכון לא מוכרע. אלו אינם תיוגי אדם חדשים, ואינם שינוי של קבוצות האיכות המקוריות 57/7.

## Left/Right ומוכנות לאימון

הנחיות הבסיס כבר מפרידות בין עמדה של המספר, ציטוט ועמדה מוצעת. נוספה הבהרה למקרים עמומים ב-[LABEL_AMBIGUITY_ADDENDUM_HE.md](LABEL_AMBIGUITY_ADDENDUM_HE.md), בלי שינוי המחלקות. נדרשים evidence מדויק, זהות אדם ותאריך; Unclear/Mixed/Other אינם מומרים אוטומטית ל-Left/Right.

התשתית הטכנית כבר עברה smoke test, אך לפי TRAINER_READINESS.json אין עדיין רשומות אדם מאומתות המיובאות ל-gate: 0 תוויות ו-0 QC זוגות. החסמים נשארים: 105 תוויות train ו-43 validation הניתנות לייחוס לאדם; 210 הכרעות אדם לזוגות Style/Paraphrase והכרעת מחלוקות; חתימת freeze של הפרוטוקול וה-provenance. אין למלא חסרים על סמך AI. סגירת חלק מהסתייגויות AI אינה מסירה חסמים אלה.

## שחזור

משורש הרפו: `python artifacts/experiments/research_completion_20261110/focused_quality_64_20261110/build_analysis.py`

בדיקות: `python -m unittest discover -s artifacts/experiments/research_completion_20261110/focused_quality_64_20261110 -p test_analysis.py`

findings.py הוא ledger ידני של קריאת AI; הסקריפט משחזר חיבורים, דגלים לקסיקליים ודוחות, לא שיפוט סמנטי באמצעות מודל. scores קיימים נצרכים כפי שנשמרו. לא נוצרו שכתובים, לא הורצו מודלים, לא שונו מקורות/ספים/הכרעות אדם ולא נעשה שימוש ב-Test.
'''
    (HERE / 'SUMMARY_HE.md').write_text(summary, encoding='utf-8')
    dependencies = [GROUPS, REVIEWS, GUARD_SOURCE, BASE_SOURCE, HERE / 'findings.py']
    # Bind every data dependency read by style_checks/style_scores/candidates.
    from common import CHAT, RUN, CANDIDATE
    dependencies += [CHAT / 'rewrite_validation.csv', CHAT / 'style_metrics_v2_v3_chatgpt.csv',
                     RUN / 'automatic_qc/rewrite_validation.csv', RUN / 'automatic_qc/style_metrics.csv',
                     CANDIDATE / 'CANDIDATE_ID_MAP_105.csv']
    manifest = {'date': '2026-11-10', 'reviewer': 'ChatGPT/Codex; exact revision unknown',
                'selection': 'exact previous 57 unresolved + 7 concern, train only',
                'counts': dict(counts), 'is_human_review': False, 'new_model_inference': False,
                'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in dependencies}}
    (HERE / 'PROVENANCE.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(counts), ensure_ascii=False))


if __name__ == '__main__':
    main()

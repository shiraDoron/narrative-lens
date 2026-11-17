"""Final two-rater handoff only. Preserve the348-source collection and frozen protocol."""
import csv
import hashlib
import json
from pathlib import Path
import random
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COLLECTION = HERE.parent / 'train_collection_v2_20261117'


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def save(path, rows, fields=None):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def verify_collection():
    manifest = json.loads((COLLECTION / 'MANIFEST.json').read_text(encoding='utf-8'))
    for name, digest in manifest['output_sha256'].items():
        if sha(COLLECTION / name) != digest:
            raise ValueError('Immutable collection changed: '+name)
    for name, digest in manifest['protected_inputs_sha256'].items():
        if sha(ROOT / name) != digest:
            raise ValueError('Protected input changed: '+name)
    return manifest


def prepare():
    if (HERE / 'HANDOFF_MANIFEST.json').exists():
        raise ValueError('Handoff already exists; preserve completed forms and create a new version')
    verify_collection()
    candidates = read(COLLECTION / 'CANDIDATES.csv')
    old_key = {r['ID']: r for r in read(COLLECTION / 'PRIVATE_REVIEW_KEY.csv')}
    assert len(candidates) == len(old_key) == 348
    assert len({r['ID'] for r in candidates}) == len({r['article_group'] for r in candidates}) == 348
    priority = [r for r in candidates if r['priority_political_review'] == 'True']
    remainder = [r for r in candidates if r['priority_political_review'] != 'True']
    assert len(priority) == 122 and len(remainder) == 226
    orders = []
    for role, seed in [('A', 2026111708), ('B', 2026111709)]:
        rng = random.Random(seed)
        first, later = list(priority), list(remainder)
        rng.shuffle(first)
        rng.shuffle(later)
        ordered = first+later
        orders.append([r['ID'] for r in ordered])
        folder = HERE / ('reviewer_'+role)
        folder.mkdir(exist_ok=True)
        forms = [dict(review_id=old_key[r['ID']]['review_id'], Original=r['Original'], label='', evidence_span='',
                      reason='', confidence='', reviewer_type='', reviewer_id='', review_date='', assistance_used='') for r in ordered]
        save(folder / 'REVIEW.csv', forms)
        for start in range(0, len(forms), 25):
            lines = ['# תיוג עצמאי של Original', '', 'ממלאים את REVIEW.csv בלבד. אפשרויות: Left / Right / Unclear. יש לקרוא את START_HE.md. אין לשתף תשובות עם הסוקר האחר.', '']
            for row in forms[start:start+25]:
                lines += [f"## {row['review_id']}", '', row['Original'], '', '| שדה | תשובה |', '|---|---|',
                          '| Left / Right / Unclear | |', '| ראיה מדויקת | |', '| נימוק / סיבת Unclear | |', '']
            (folder / f'BOOKLET_{start//25+1:02}.md').write_text('\n'.join(lines), encoding='utf-8')
        (folder / 'START_HE.md').write_text(
            f'# לסוקר/ת {role} — מתחילים כאן\n\n'
            'בחבילה348 קטעים. יש לתייג את REVIEW.csv בעותק נפרד. החוברות לקריאה בלבד. '
            'עובדים לפי הסדר שניתן, במנות של25 ובקצב מתאים. אפשר להחזיר CSV חלקי; אין חובה להשלים הכול בבת אחת.\n\n'
            'Left / Right / Unclear לפי העמדה המאומצת בקטע בלבד. אין להסיק מזהות אדם, '
            'שם פוליטיקאי או עמדת דובר מצוטט. אי־ודאות, ערבוב, אירוניה לא פתורה, הקשר חסר '
            'או מסגור מחוץ לציר הם סיבות תקפות ל־Unclear. אין לכפות בינארי.\n\n'
            'Left: מסגור פרוגרסיבי/שמאלי מאומץ, כגון שוויון וזכויות עובדים או התנגדות לריכוז כוח ועושר. '
            'Right: מסגור שמרני/ימני מאומץ, כגון שוק חופשי, הפחתת התערבות המדינה או עמדה חברתית־מסורתית פוליטית. '
            'ביקורת על מפלגה, אזכור דת או עמדה לגבי ישראל אינם מספיקים לבדם.\n\n'
            'אין לערוך את Original או המזהה. לכל דירוג ממלאים label, evidence_span (ציטוט מדויק לתווית בינארית), '
            'reason, confidence=1/2/3, reviewer_type=human, reviewer_id קבוע, review_date=YYYY-MM-DD '
            'ו־assistance_used=none אם אין סיוע. ל־Unclear נדרש נימוק; אפשר להשאיר ראיה ריקה.\n\n'
            'התיוג העצמאי מתבצע בלי הצעות/דירוגי AI ובלי תשובות הסוקר האחר. אין להשתמש ב־AI לקבלת החלטות '
            'התיוג. אם נעשה סיוע אחר יש לדווח עליו; רשומות מסייעות יועברו לבדיקה ולא ייספרו אוטומטית כעצמאיות. '
            'מתייגים עמדה, לא אמיתות עובדות ולא הסכמה אישית עם הדעה.\n\n'
            'רק לאחר קבלת שני העותקים ייחשפו אי־הסכמות לאדג׳ודיקטור נפרד. '
            'אל תחליפו תשובות או קבצים לפני סיום התיוג העצמאי.\n', encoding='utf-8')
        archive = HERE / f'REVIEWER_{role}_ONLY.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as out:
            for path in sorted(folder.iterdir()):
                info = zipfile.ZipInfo(path.name, date_time=(2026, 11, 17, 12, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                out.writestr(info, path.read_bytes())
    assert orders[0] != orders[1]
    key_rows = []
    for r in candidates:
        key_rows.append(dict(review_id=old_key[r['ID']]['review_id'], ID=r['ID'], article_group=r['article_group'],
                             source_sha256=r['source_sha256'], author=r['author'], source_url=r['source_url'],
                             priority_block=r['priority_political_review']))
    save(HERE / 'COORDINATOR_PRIVATE_KEY.csv', key_rows)
    fields = ['review_id', 'source_sha256', 'review_A_record_sha256', 'review_B_record_sha256',
              'final_label', 'evidence_span', 'rationale', 'reviewer_type', 'adjudicator_id', 'review_date', 'assistance_used']
    save(HERE / 'ADJUDICATION_TEMPLATE.csv', [dict.fromkeys(fields, '') | dict(review_id=r['review_id'], source_sha256=r['source_sha256']) for r in key_rows], fields)
    dump(HERE / 'HANDOFF_MANIFEST.json', dict(
        candidate_sources=348, first_block=122, second_block=226, target_verified_train=200,
        selection='same immutable candidates and review IDs; separate fixed random permutations within each of the two blocks',
        source_manifest_sha256=sha(COLLECTION / 'MANIFEST.json'),
        source_csv_sha256=sha(COLLECTION / 'CANDIDATES.csv'),
        output_sha256={str(p.relative_to(HERE)): sha(p) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'HANDOFF_MANIFEST.json'},
        human_labels_filled=0, no_training=True, no_test_evaluation=True))


if __name__ == '__main__':
    prepare()

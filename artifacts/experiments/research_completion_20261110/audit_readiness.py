"""Read-only development readiness gate. Exit2 is expected while human gates block.

No ML imports, fitting, prediction, generation, or test-dependent selection.
"""

import argparse
from collections import Counter
import importlib.util
import json
import math

from common import HERE, ROOT, PREP, FOLLOW, RUN, CANDIDATE, candidates, dump, read, save, sha, text_sha, verify


def load_preparation():
    spec = importlib.util.spec_from_file_location('readiness_frozen_prepare', PREP / 'prepare.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_candidates(rows):
    if len(rows) != 105 or len({row['ID'] for row in rows}) != 105:
        raise ValueError('Expected exact105 unique train IDs')
    for row in rows:
        if row['split'] != 'train':
            raise ValueError('Non-train source in candidate views')
        for variant, flag in [('Original', 'original_present'), ('Paraphrase', 'paraphrase_present'), ('Style', 'style_present')]:
            if not row[variant] or row[flag] != 'True':
                raise ValueError('Text/availability inconsistency: ' + row['ID'] + '/' + variant)
        if row['training_ready'] != 'False':
            raise ValueError('Candidate has been marked approved without human gates')


def check_disjoint(assignments):
    groups = {split: {row['author'] for row in assignments if row['split'] == split} for split in ['train', 'val', 'test']}
    if len({row['author'] for row in assignments}) != len(assignments):
        raise ValueError('Duplicate author assignment')
    if groups['train'] & groups['val'] or groups['train'] & groups['test'] or groups['val'] & groups['test']:
        raise ValueError('Author overlap across frozen splits')
    return groups


def audit():
    verify()
    rows = candidates()
    check_candidates(rows)
    assignments = read(FOLLOW / 'author_splits.csv')
    groups = check_disjoint(assignments)
    split_by_author = {row['author']: row['split'] for row in assignments}
    cohort = read(FOLLOW / 'analysis_cohort.csv')
    assert all(split_by_author[row['author']] == row['split'] for row in cohort)
    assert all(row['author'] in groups['train'] for row in rows)
    assert {row['ID'] for row in rows} == {row['row_id'] for row in cohort if row['split'] == 'train'}
    collision_counts = {}
    annotations = read(FOLLOW / 'text_annotations.csv')
    for field in ['text_sha256', 'article_snapshot_sha256']:
        seen = {}
        for record in annotations:
            seen.setdefault(record[field], set()).add(split_by_author[record['author']])
        collision_counts[field] = sum(len(splits) > 1 for splits in seen.values())
        assert not collision_counts[field]
    prep = load_preparation()
    budget = []
    views = {}
    for arm, variants in prep.ARMS.items():
        view = read(CANDIDATE / f'DRAFT_ARM_{arm}.csv')
        expected = [(row['ID'], variant, row[variant], row['label']) for row in rows for variant in variants]
        actual = [(row['ID'], row['variant'], row['text'], row['label']) for row in view]
        assert actual == expected
        views[arm] = view
        for seed in prep.SEEDS:
            config = json.loads((CANDIDATE / f'CONFIG_{arm}_seed{seed}.json').read_text())
            assert config['n_sources'] == 105 and config['n_examples'] == len(view)
            assert config['optimizer_updates'] == 20 * math.ceil(105 / 16) == 140
            assert config['processed_examples'] == config['optimizer_updates'] * config['batch_size'] == 2240
            assert config['label_space'] == ['Right-wing', 'Left-wing']
            assert len(config['output_label_order']) == 7
            assert config['output_label_order'][5:] == config['label_space']
            assert not config['training_ready']
            schedule = read(CANDIDATE / config['schedule'])
            regenerated = [{key: str(value) for key, value in record.items()} for record in prep.schedules(view, seed, 140)]
            assert schedule == regenerated
            for record in schedule:
                selected = view[int(record['view_index'])]
                assert record['ID'] == selected['ID'] and record['variant'] == selected['variant']
            budget.append(dict(arm=arm, seed=seed, n_sources=105, n_rows=len(view), updates=140,
                               processed_examples=2240, scheduled_word_count=sum(len(view[int(record['view_index'])]['text'].split()) for record in schedule),
                               training_ready=False))
    for seed in prep.SEEDS:
        d = read(CANDIDATE / f'SCHEDULE_D_seed{seed}.csv')
        e = read(CANDIDATE / f'SCHEDULE_E_seed{seed}.csv')
        assert [(row['ID'], row['view_index']) for row in d] == [(row['ID'], row['view_index']) for row in e]
        configs = [json.loads((CANDIDATE / f'CONFIG_{arm}_seed{seed}.json').read_text()) for arm in prep.ARMS]
        for key in ['encoder', 'head', 'optimizer', 'lr', 'batch_size', 'optimizer_updates', 'processed_examples', 'checkpoint_rule']:
            assert len({json.dumps(config[key], sort_keys=True) for config in configs}) == 1
    save(HERE / 'TRAINING_BUDGET_AUDIT.csv', budget)
    save(HERE / 'INPUT_BINDINGS_105.csv', [dict(
        ID=row['ID'], author=row['author'], split=row['split'], proposed_label=row['label'],
        source_sha256=text_sha(row['Original']), paraphrase_sha256=text_sha(row['Paraphrase']),
        style_sha256=text_sha(row['Style']), style_protocol_cohort=row['style_protocol_cohort'],
        label_status='machine proposal, not gold',
    ) for row in rows])
    human_imports = ROOT / 'artifacts/experiments/data_completion_20261109/human_imports'
    attributable_imports = list(human_imports.glob('*/IMPORT_MANIFEST.json')) if human_imports.exists() else []
    # Do not infer gold from nonblank cells, AI reviews, or aggregate declarations.
    human_status = dict(attributable_import_manifests=len(attributable_imports),
                        source_labels_train=0, source_labels_validation=0, style_pairs=0, paraphrase_pairs=0)
    if attributable_imports:
        raise ValueError('Human imports now exist: audit/adjudicate their exact coverage before updating this readiness snapshot')
    blockers = [
        '105 train source labels require attributable human validation; proposals are not gold',
        '43 validation source labels require attributable human validation',
        '105 Style pair judgments and105 Paraphrase pair judgments are missing; auto pass does not substitute',
        'Resolve disagreements/Borderline and apply the preregistered shared-ID symmetric fallback before training approval',
        'Legacy30 generator model/prompt remain unknown; document the mixed-protocol interpretation before scientific training',
        'No approved end-to-end A-E trainer/evaluation bridge yet; historical evaluate()/train() must not be used as a drop-in',
    ]
    report = dict(
        audit_date='2026-11-10', training_ready=False, sources=105,
        originals=105, paraphrases=105, style_rewrites=105, missing_styles=0,
        style_protocol_counts=dict(Counter(row['style_protocol_cohort'] for row in rows)),
        proposed_label_counts=dict(Counter(row['label'] for row in rows)),
        author_split_counts={key: len(value) for key, value in groups.items()},
        author_disjoint=True, cross_split_exact_hash_collisions=collision_counts,
        near_duplicate_caution='Only inherited train202 near-duplicate audit; no new semantic scan of frozen test',
        configs_checked=25, schedules_checked=25, fixed_updates=140, processed_examples=2240,
        tokens_and_flops_equal=False, initialization_equal_in_configs_not_execution_verified=True,
        human_status=human_status, blockers=blockers,
        task='text-level Left/Right; historical seven-output head retained only for protocol compatibility',
        test_texts_exported=0, test_predictions=0, training_runs=0,
        candidate_map_sha256=sha(CANDIDATE / 'CANDIDATE_ID_MAP_105.csv'),
    )
    dump(HERE / 'READINESS.json', report)
    lines = ['# מוכנות לאימון — 10.11.2026', '', '**מצב: נתונים זמינים, אימון מדעי חסום.** אין אימון או הערכת test.', '',
             '## הושלם ונבדק', '',
             '- 105 IDs ייחודיים; Original, Paraphrase ו־Style זמינים לכולם. 30 שכתובים ישנים ו־75 חדשים נשמרים כ־cohorts נפרדים.',
             '- הצעות התוויות נשארו55 Left /50 Right; הן אינן gold.',
             '- כותבים נפרדים:9 train /4 validation /6 test. אין overlap או exact text/article-hash collision בין splits. אין בכך הבטחה שאין דמיון סמנטי או חפיפת אירועים.',
             '- טיוטות A–C:105 שורות; D–E:210 שורות. אותם מקורות ותוויות, בלי סינון נפרד לזרוע.',
             '- 25 configs ו־25 schedules שוחזרו בדיוק. בכל זרוע/seed:140 עדכונים, batch16,2240 דוגמאות מעובדות; D/E זהים במיפוי source/index.',
             '- אותם encoder/head/optimizer/seeds/config rules; זה אינו אימות של initialization או checkpoint בהתנהגות trainer שטרם אושר.',
             '- מספר המילים המעובדות נמדד ב־TRAINING_BUDGET_AUDIT.csv; תקציב דוגמאות שווה אינו FLOPs/tokens זהים.',
             '- QC מלא ל־75 החדשים ולפרפרזותיהם קיים; legacy30 נשמר ללא rerun. חבילות אדם ריקות לכל105 ולתוויות train/validation.', '',
             '## חסמי אימון', '']
    lines += [f'{number}. {blocker}' for number, blocker in enumerate(blockers, 1)]
    lines += ['', '## זהירות בקוד ההיסטורי', '',
              'הפקודה check_readiness.py בחבילת main_training_preparation היא snapshot היסטורי של common30 וממשיכה לדווח75 missing. אין להריץ prepare.py כדי לדרוס טפסים; הדוח הנוכחי מחובר ל־candidate105 ומתעד missing=0 בלי לעקוף את שערי האדם.', '',
              'ה־trainer ההיסטורי בוחר checkpoint לפי validation ופונקציות evaluate ההיסטוריות כוללות test וסינון automatic-all-arms. הן אינן מימוש של תקציב A–E הנוכחי וכלל ה־human symmetric fallback. אין להפעיל אותן כאילו היו הניסוי החדש. הקוד והפרוטוקול ההיסטוריים נשארו ללא שינוי.', '',
              'המשימה הנוכחית היא Left/Right ברמת טקסט. ראש7 נשמר מטעמי תאימות בלבד; Macro-F1 ראשי צריך להשתמש בשתי התוויות הפעילות, ולדווח inactive-output rate. אין לבצע renormalization שקט לשתיים או להציג זאת כרפליקציה של שבעת הנרטיבים ההיסטוריים.', '',
              '## שער ובדיקות', '',
              '`python artifacts/experiments/research_completion_20261110/audit_readiness.py` מחזיר exit2 כל עוד החסמים קיימים. זהו fail-closed צפוי, לא כשל QC ולא הרשאה לאימון. אין לו מסלול שמפעיל trainer.', '',
              'חוסר provenance ב־legacy30 ואי־חשיפת decoding ב־UI מתועדים בנפרד. ל־75 החדשים GPT-6 /9.11.2026 לפי המשתמשת; exact revision/parameters/finish_reason אינם ידועים. אין להמציא אותם או להרחיב את ההצהרה ל־30 הישנים.', '',
              'ה־test ההיסטורי כבר שימש בעבר. החלטה אם נדרש holdout חדש היא החלטה מחקרית עתידית עם המנחה; לא פותחים test כדי להחליט כעת.']
    (HERE / 'READINESS_HE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    verify()
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    result = audit()
    print(json.dumps(result, ensure_ascii=True, indent=2))
    raise SystemExit(2 if not result['training_ready'] else 0)

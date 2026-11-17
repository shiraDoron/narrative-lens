"""Draft index schedules only: no labels, text encoding, optimizer or training."""
from collections import Counter
import hashlib
import json
import random

from prepare import HERE, dump, read, save


def schedule(ids, variants, seed, updates=260, batch=16):
    if len(ids) != 200 or len(set(ids)) != 200 or not variants:
        raise ValueError('Draft200 schedule requires200 distinct source IDs and variants')
    rng = random.Random(seed)
    result = []
    while len(result) < updates * batch:
        cycle = [(rid, slot) for rid in ids for slot in range(len(variants))]
        rng.shuffle(cycle)
        result.extend(cycle)
    return result[:updates * batch]


def main():
    target = HERE / 'DRAFT_SCHEDULE_AUDIT.csv'
    if target.exists():
        raise ValueError('Do not overwrite a draft audit; use a new version')
    config = json.loads((HERE / 'DRAFT_CONFIG.json').read_text(encoding='utf-8'))
    ids = sorted(r['ID'] for r in read(HERE / 'PROVISIONAL_200.csv'))
    rows = []
    for seed in config['seeds']:
        double_reference = None
        for arm, variants in config['arms'].items():
            entries = schedule(ids, variants, seed)
            if len(variants) == 2:
                if double_reference is None:
                    double_reference = entries
                assert double_reference == entries
            counts = Counter(entries)
            sources = Counter(rid for rid, slot in entries)
            row = dict(arm=arm, seed=seed, draft_only=True, updates=260, batch=16, processed_examples=len(entries),
                       unique_sources=len(sources), unique_source_slots=len(counts),
                       min_source_exposure=min(sources.values()), max_source_exposure=max(sources.values()),
                       min_source_slot_exposure=min(counts.values()), max_source_slot_exposure=max(counts.values()),
                       schedule_sha256=hashlib.sha256(json.dumps(entries).encode()).hexdigest())
            rows.append(row)
    save(target, rows)
    dump(HERE / 'SCHEDULE_BINDINGS.json', dict(draft_only=True, no_training=True,
         algorithm='Python random.Random(seed), shuffled source/slot cycles, full batches; common index schedules across equal-size arms',
         missing_rewrites_and_human_labels_are_not_generated_by_schedules=True,
         total_updates=sum(r['updates'] for r in rows), total_processed_examples=sum(r['processed_examples'] for r in rows)))


if __name__ == '__main__':
    main()

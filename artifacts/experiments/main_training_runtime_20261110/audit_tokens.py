"""Token counts for draft train variants + validation Originals; no embeddings/model inference."""

import hashlib
import json
import os

from contract import HERE, CANDIDATE, ARMS, SEEDS, candidates, validation_sources, read, save, dump, schedule, assert_frozen


def audit():
    assert_frozen()
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    from transformers import AutoTokenizer
    revision = '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2', revision=revision, local_files_only=True)
    smoke = json.loads((HERE / 'smoke_runtime/SMOKE_RESULT.json').read_text())
    vocabulary_hash = hashlib.sha256(json.dumps(tokenizer.get_vocab(), sort_keys=True).encode()).hexdigest()
    if vocabulary_hash != smoke['encoder_identity']['tokenizer_vocabulary_sha256']:
        raise ValueError('Audit tokenizer differs from actual production smoke tokenizer')
    limit = smoke['encoder_identity']['max_seq_length']
    records = [dict(ID=row['ID'], variant=variant, split='train', text=row[variant])
               for row in candidates() for variant in ['Original', 'Paraphrase', 'Style']]
    records += [dict(ID=row['ID'], variant='Original', split='validation', text=row['Original']) for row in validation_sources()]
    encoded = tokenizer([row['text'] for row in records], truncation=False, add_special_tokens=True)['input_ids']
    audit_rows = [dict(ID=row['ID'], variant=row['variant'], split=row['split'], tokens_before_truncation=len(tokens),
                       tokens_at_frozen_limit=min(limit, len(tokens)), truncated=len(tokens) > limit,
                       text_sha256=hashlib.sha256(row['text'].encode()).hexdigest())
                  for row, tokens in zip(records, encoded)]
    save(HERE / 'INPUT_TOKEN_AUDIT_358.csv', audit_rows)
    token_by_pair = {(row['ID'], row['variant']): row['tokens_at_frozen_limit'] for row in audit_rows if row['split'] == 'train'}
    budgets = []
    for arm in ARMS:
        view = read(CANDIDATE / f'DRAFT_ARM_{arm}.csv')
        for seed in SEEDS:
            plan = schedule(view, seed, 140)
            budgets.append(dict(arm=arm, seed=seed, updates=140, processed_examples=2240,
                                draft_scheduled_tokens=sum(token_by_pair[row['ID'], row['variant']] for row in plan),
                                human_policy_not_yet_applied=True))
    save(HERE / 'DRAFT_TOKEN_BUDGET_25.csv', budgets)
    dump(HERE / 'TOKEN_AUDIT_SUMMARY.json', dict(
        n=358, train_rows=315, validation_original_rows=43, test_rows=0,
        encoder_max_seq_length=limit, tokenizer_revision=revision, tokenizer_vocabulary_sha256=vocabulary_hash,
        max_input_tokens=max(row['tokens_before_truncation'] for row in audit_rows),
        truncated=sum(row['truncated'] for row in audit_rows),
        classifier_predictions=False, thresholds_changed=False, draft_only=True,
    ))
    print('Token audit completed; no model predictions, training or test inputs.')


if __name__ == '__main__':
    audit()

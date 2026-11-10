"""Train-only technical smoke: synthetic targets, two updates/arm, no quality metrics."""

import json
import argparse
from pathlib import Path

from contract import HERE, LABELS, ARMS, candidates, dump, save, assert_frozen
from data import source_audit
from trainer import load_backend, encode_texts, encoder_identity, state_digest, train_head


def smoke(destination=None):
    assert_frozen()
    sources_audit = source_audit()
    destination = destination or HERE / 'smoke_runtime'
    if (destination / 'SMOKE_RESULT.json').exists():
        raise ValueError('Smoke result exists; preserve it; use a fresh checkout for repetition')
    rows = sorted(candidates(), key=lambda row: row['ID'])[:4]
    source_ids = [row['ID'] for row in rows]
    backend, encoder = load_backend()
    identity = encoder_identity(encoder)
    encoder_before = state_digest(encoder.state_dict())
    views = {
        arm: [dict(ID=row['ID'], variant=variant, text=row[variant], label=LABELS[5 + index % 2])
              for index, row in enumerate(rows) for variant in variants]
        for arm, variants in ARMS.items()
    }
    lookup, token_audit = encode_texts(backend, encoder, [row['text'] for view in views.values() for row in view])
    destination.mkdir(exist_ok=True)
    save(destination / 'tokenization_audit.csv', token_audit)
    records = []
    for arm, view in views.items():
        out = destination / arm
        out.mkdir(exist_ok=True)
        _, result, _ = train_head(backend, view, lookup, seed=42, updates=2, out=out,
                                  mode='technical_smoke', encoder_identity=identity)
        records.append(dict(arm=arm, **result))
    if len({row['initial_head_sha256'] for row in records}) != 1:
        raise ValueError('Smoke arms did not share identical initialization')
    encoder_after = state_digest(encoder.state_dict())
    if encoder_before != encoder_after or any(parameter.grad is not None for parameter in encoder.parameters()):
        raise ValueError('Frozen encoder was changed by smoke')
    report = dict(
        status='passed', date='2026-11-10', scientific_result=False,
        source_ids=source_ids, source_split='train', n_sources=4,
        targets='Synthetic alternating indices5/6 for engineering only; machine proposals ignored; not gold',
        arms=records, common_initialization_verified=True, encoder_unchanged=True,
        encoder_gradients_absent=True, validation_inputs=0, test_inputs=0,
        forward_backward_checkpoint_reload_verified=True,
        tokenization_inputs=len(token_audit), truncations=sum(row['truncated'] for row in token_audit),
        encoder_identity=identity, source_audit=sources_audit,
        no_accuracy_or_f1_computed=True, optimizer='Adam', lr=.001, batch_size=16,
        note='Two updates/arm instead of scientific140; no result here supports any research hypothesis',
    )
    dump(destination / 'SMOKE_RESULT.json', report)
    assert_frozen()
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    smoke(parser.parse_args().output_dir)

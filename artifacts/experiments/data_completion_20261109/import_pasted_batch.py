"""Preserve a pasted batch and extract CSV without changing any rewrite text."""

import argparse
import csv
import io
import json
import shutil
from pathlib import Path

from bundle import HERE, VERSION, read, sha, verify


def import_batch(source: Path, batch_number: int) -> Path:
    verify()
    expected_path = HERE / 'chatgpt_batches' / f'BATCH_{batch_number:02d}_15.csv'
    expected = read(expected_path)
    pasted = source.read_bytes().decode('utf-8-sig')
    lines = pasted.splitlines(keepends=True)
    fenced = bool(lines and lines[0].strip() in ('```', '```csv'))
    if fenced:
        if lines[-1].strip() != '```':
            raise ValueError('Unclosed Markdown fence')
        payload = ''.join(lines[1:-1])
    else:
        payload = pasted

    reader = csv.DictReader(io.StringIO(payload, newline=''), strict=True)
    rows = list(reader)
    if reader.fieldnames != ['id', 'chatgpt_style_rewrite']:
        raise ValueError('Unexpected CSV columns')
    if [row['id'] for row in rows] != [row['id'] for row in expected]:
        raise ValueError('IDs must match the entire batch in supplied order')
    if any(None in row or not row['chatgpt_style_rewrite'].strip() for row in rows):
        raise ValueError('Malformed row or empty rewrite')

    destination = HERE / 'received_batches' / f'batch_{batch_number:02d}'
    if destination.exists():
        raise ValueError('Batch already received; no overwrite')
    destination.mkdir(parents=True)
    shutil.copyfile(source, destination / 'RAW_PASTED_TEXT.txt')
    csv_path = destination / f'BATCH_{batch_number:02d}_OUTPUT.csv'
    csv_path.write_bytes(payload.encode('utf-8'))
    receipt = {
        'protocol_version_expected': VERSION,
        'batch': batch_number,
        'rows': len(rows),
        'raw_sha256': sha(destination / 'RAW_PASTED_TEXT.txt'),
        'csv_sha256': sha(csv_path),
        'input_batch_sha256': sha(expected_path),
        'markdown_fences_removed': fenced,
        'rewrite_text_edited': False,
        'id_order_matches': True,
        'actual_model_and_generation_date': None,
        'generation_metadata_status': 'not supplied; do not infer from receipt',
        'semantic_qc_executed': False,
        'human_validation_complete': False,
        'full75_import_complete': False,
    }
    (destination / 'RECEIPT.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    verify()
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--batch', type=int, choices=range(1, 6), required=True)
    arguments = parser.parse_args()
    print(import_batch(arguments.source, arguments.batch))

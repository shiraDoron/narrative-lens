"""Paths and read-only bindings for the development completion audit."""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMPLETION = ROOT / 'artifacts/experiments/data_completion_20261109'
sys.path.insert(0, str(COMPLETION))
from bundle import CHAT, FOLLOW, PREP, dump, legacy, mapping, read, save, sha, text_sha, verify

RUN = COMPLETION / 'runs/extension_v1_run01'
CANDIDATE = RUN / 'candidate_105'


def candidates():
    verify()
    from import_review import registry
    received = registry('pairs105', 'extension_v1_run01')
    rows = read(CANDIDATE / 'CANDIDATE_ID_MAP_105.csv')
    if len(rows) != 105 or len({row['ID'] for row in rows}) != 105:
        raise ValueError('Expected exact105 candidate sources')
    for row in rows:
        if row['Original'] != received[row['ID']]['Original'] or row['Style'] != received[row['ID']]['Style']:
            raise ValueError('Candidate binding mismatch: ' + row['ID'])
    return rows


def style_checks():
    old = {row['row_id']: row for row in read(CHAT / 'rewrite_validation.csv')}
    new = {row['row_id']: row for row in read(RUN / 'automatic_qc/rewrite_validation.csv')}
    if set(old) & set(new) or len(old) != 30 or len(new) != 75:
        raise ValueError('Wrong legacy/extension QC coverage')
    return {**old, **new}


def style_scores():
    old = {row['ID']: row for row in read(CHAT / 'style_metrics_v2_v3_chatgpt.csv') if row['version'] == 'ChatGPT'}
    new = {row['ID']: row for row in read(RUN / 'automatic_qc/style_metrics.csv')}
    if set(old) & set(new) or len(old) != 30 or len(new) != 75:
        raise ValueError('Wrong legacy/extension style coverage')
    return {**old, **new}


def ensure_new_outputs(names):
    """Do not regenerate a handoff over forms the user may already have edited."""
    existing = [name for name in names if (HERE / name).exists()]
    if existing:
        raise ValueError('Outputs already exist; preserve answers: ' + ', '.join(existing))

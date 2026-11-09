"""Pure evaluation helpers for the frozen protocol; no models or dataset loading.

Seven output probabilities are retained. Only Left/Right are gold task labels.
These helpers are infrastructure, not an approved A-E trainer or scientific run.
"""

import math

OUTPUT_LABELS = ('Zionist', 'Resistance', 'Western', 'Russian', 'Ukrainian', 'Right-wing', 'Left-wing')
ACTIVE = ('Right-wing', 'Left-wing')
ARMS = ('A', 'B', 'C', 'D', 'E')


def classification_metrics(gold, probabilities):
    if not gold or len(gold) != len(probabilities):
        raise ValueError('Nonempty matching gold/probability rows required')
    if any(label not in ACTIVE for label in gold):
        raise ValueError('Current task requires Left/Right gold, not historical seven-narrative labels')
    predictions = []
    for row in probabilities:
        if len(row) != 7 or any(not math.isfinite(value) or value < 0 or value > 1 for value in row):
            raise ValueError('Expected seven finite probabilities in [0,1]')
        if not math.isclose(sum(row), 1, abs_tol=1e-5):
            raise ValueError('Probabilities must sum to1; do not silently renormalize')
        predictions.append(OUTPUT_LABELS[max(range(7), key=row.__getitem__)])
    per_class = {}
    for label in ACTIVE:
        tp = sum(actual == label and predicted == label for actual, predicted in zip(gold, predictions))
        fp = sum(actual != label and predicted == label for actual, predicted in zip(gold, predictions))
        fn = sum(actual == label and predicted != label for actual, predicted in zip(gold, predictions))
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        per_class[label] = dict(precision=precision, recall=recall,
                               f1=2 * precision * recall / (precision + recall) if precision + recall else 0,
                               support=gold.count(label))
    return dict(
        n=len(gold), accuracy=sum(a == b for a, b in zip(gold, predictions)) / len(gold),
        macro_f1=sum(values['f1'] for values in per_class.values()) / 2,
        inactive_output_rate=sum(label not in ACTIVE for label in predictions) / len(gold),
        per_class=per_class,
    )


def aligned_arm_metrics(records):
    """Reject missing/duplicate/misaligned predictions before any contrast is computed."""
    groups = {}
    labels_by_id = {}
    for row in records:
        if row['arm'] not in ARMS:
            raise ValueError('Unknown arm')
        group = groups.setdefault((row['seed'], row['arm']), {})
        if row['ID'] in group:
            raise ValueError('Duplicate prediction ID')
        group[row['ID']] = row
        if row['ID'] in labels_by_id and labels_by_id[row['ID']] != row['gold']:
            raise ValueError('Inconsistent gold across conditions/seeds')
        labels_by_id[row['ID']] = row['gold']
    seeds = {seed for seed, arm in groups}
    if not seeds:
        raise ValueError('No predictions')
    expected = set(labels_by_id)
    result = {}
    for seed in seeds:
        for arm in ARMS:
            group = groups.get((seed, arm), {})
            if set(group) != expected:
                raise ValueError('All seeds/arms must contain the same evaluation IDs')
            ordered = [group[rid] for rid in sorted(expected)]
            result[seed, arm] = classification_metrics(
                [row['gold'] for row in ordered], [row['probabilities'] for row in ordered]
            )
    return result

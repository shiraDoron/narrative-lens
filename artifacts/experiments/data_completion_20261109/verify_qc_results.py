"""Check persisted QC coverage, guard accounting, paired summary, and source integrity."""

import argparse
import json

from automatic_qc import binding
from bundle import dump, read, verify
from compare_qc_75 import is_true


def check(run):
    verify()
    directory, received, identity = binding(run)
    expected = {row['ID'] for row in received}
    paired = read(directory / 'QC_COMPARISON_BY_ID_75.csv')
    assert len(paired) == 75 and {row['ID'] for row in paired} == expected
    summary = {row['method']: row for row in read(directory / 'QC_METHOD_SUMMARY.csv')}
    assert set(summary) == {'Style', 'Paraphrase'}
    for method in summary:
        counts = dict(preservation_pass=0, substantial_style=0, both=0, exact_copies=0)
        for row in paired:
            prefix = method + '_'
            failed = {key.removeprefix(prefix + 'guard_') for key in row
                      if key.startswith(prefix + 'guard_') and not is_true(row[key])}
            reasons = set(filter(None, row[prefix + 'rejection_reasons'].split('|')))
            assert failed == reasons
            preservation = is_true(row[prefix + 'passed'])
            assert preservation == (not failed)
            substantial = is_true(row[prefix + 'substantial_style_change'])
            counts['preservation_pass'] += preservation
            counts['substantial_style'] += substantial
            counts['both'] += preservation and substantial
            counts['exact_copies'] += is_true(row[prefix + 'exact_copy'])
        assert int(summary[method]['n']) == 75
        assert all(counts[key] == int(summary[method][key]) for key in counts)
    manifest = json.loads((directory / 'QC_RUN_MANIFEST.json').read_text())
    assert manifest['validator'] == identity
    assert not manifest['narrative_classifier_run'] and not manifest['test_evaluation']
    verify()
    result = dict(
        n_pairs=75, n_method_evaluations=150, same_id_coverage=True,
        guard_accounting_consistent=True, summary_recomputed_from_pairs=True,
        frozen_sources_unchanged=True, narrative_classifier_or_test_inference=False,
    )
    dump(directory / 'QC_RESULT_VERIFICATION.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    check(parser.parse_args().run)

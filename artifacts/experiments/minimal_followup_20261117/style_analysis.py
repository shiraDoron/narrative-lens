"""Reuse frozen66-feature surface representation/scaling, without fitting a model."""
import ast
import collections
import json
import re
from types import SimpleNamespace

import numpy as np

from prepare import HERE, ROOT, dump, save, sha


def load_features():
    base_path = ROOT / 'experiments/author_generalization/author_style_controlled.py'
    extended_path = ROOT / 'artifacts/experiments/verified_human_style_followup_20261026/experiment.py'
    base_tree = ast.parse(base_path.read_text(encoding='utf-8-sig'))
    base_fn = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'style_features')
    wordcount_fn = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'wordcount')
    scope = {'np': np, 're': re}
    exec(compile(ast.Module(body=[wordcount_fn, base_fn], type_ignores=[]), str(base_path), 'exec'), scope)
    extended_tree = ast.parse(extended_path.read_text(encoding='utf-8-sig'))
    extended_fn = next(n for n in extended_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'style_features')
    words = next(n for n in extended_tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'FUNCTION_WORDS' for t in n.targets))
    extended_scope = {'np': np, 're': re, 'collections': collections,
                      'base': SimpleNamespace(style_features=scope['style_features'], wordcount=scope['wordcount'])}
    exec(compile(ast.Module(body=[words, extended_fn], type_ignores=[]), str(extended_path), 'exec'), extended_scope)
    return extended_scope['style_features'], [base_path, extended_path]


def main():
    if (HERE / 'SURFACE_STYLE_66.csv').exists():
        raise ValueError('Do not overwrite measured results')
    feature, paths = load_features()
    scale_path = ROOT / 'artifacts/experiments/style_intervention_v2_20261026/style_feature_scaling.json'
    scaling = json.loads(scale_path.read_text(encoding='utf-8'))
    scale = np.array(scaling['scale'])
    assert len(scale) == 66 and np.all(scale > 0)
    variants = [json.loads(s) for s in (HERE / 'generated_rewrites.jsonl').read_text(encoding='utf-8').splitlines()]
    measured = []
    for r in variants:
        a, b = np.array(feature(r['original'])), np.array(feature(r['rewrite']))
        assert len(a) == len(b) == 66
        measured.append(dict(ID=r['row_id'], method=r['condition'],
                             standardized_mean_abs_change=float(np.mean(np.abs(b-a)/scale)),
                             **{name+'_delta': float(delta) for name, delta in zip(scaling['names'], b-a)}))
    save(HERE / 'SURFACE_STYLE_66.csv', measured)
    summary = {}
    for method in sorted({r['method'] for r in measured}):
        values = [r['standardized_mean_abs_change'] for r in measured if r['method'] == method]
        summary[method] = dict(n=len(values), standardized_mean_abs_change=float(np.mean(values)),
                               median=float(np.median(values)), nonzero_pairs=sum(v > 0 for v in values))
    dump(HERE / 'SURFACE_STYLE_SUMMARY.json', dict(methods=summary, scaling_fit_scope=scaling['fit_scope'],
         new_scaling_fit=False, inference='descriptive surface differences only; no author classifier or causal/generalization inference',
         code_scaling_sha256={str(p.relative_to(ROOT)): sha(p) for p in paths + [scale_path]}))


if __name__ == '__main__':
    main()

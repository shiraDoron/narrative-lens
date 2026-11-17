"""Run unchanged historical semantic screen on prepared TRAIN pilot only, offline."""
import importlib.util
import json
import os

from prepare import HERE, ROOT, STUDY, read, sha


def main():
    manifest = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
    for name, digest in manifest['output_sha256'].items():
        assert sha(HERE / name) == digest, f'Prepared output changed: {name}'
    assert all(r['split'] == 'train' for r in read(HERE / 'analysis_cohort.csv'))
    assert len(read(HERE / 'analysis_cohort.csv')) == 9
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    spec = importlib.util.spec_from_file_location('minimal_frozen_style', STUDY)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.OUT = HERE
    engine = helper.load_engine()
    assert engine.OUT == HERE and engine.base.OUT == HERE
    engine.validate()  # Never call evaluate(), probe(), train() or historical main().
    paths = [STUDY, ROOT / 'artifacts/experiments/verified_human_style_followup_20261026/experiment.py',
             ROOT / 'experiments/author_generalization/author_style_controlled.py']
    (HERE / 'SCREEN_BINDINGS.json').write_text(json.dumps({str(p.relative_to(ROOT)): sha(p) for p in paths}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

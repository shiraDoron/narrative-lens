"""Run the unchanged semantic screen, restricted to nine TRAIN sources."""
import importlib.util
import json
import os

from prepare import HERE, ROOT, previous, read, sha


def main():
    manifest = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
    for path, digest in manifest['source_sha256'].items():
        assert sha(ROOT / path) == digest, path
    for path, digest in manifest['output_sha256'].items():
        assert sha(HERE / path) == digest, path
    cohort = read(HERE / 'analysis_cohort.csv')
    assert len(cohort) == 9 and all(r['split'] == 'train' for r in cohort)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    spec = importlib.util.spec_from_file_location('minimal_followup_frozen_style', previous.STUDY)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.OUT = HERE
    engine = helper.load_engine()
    assert engine.OUT == HERE and engine.base.OUT == HERE
    engine.validate()
    dump = previous.dump
    paths = [previous.STUDY, ROOT / 'artifacts/experiments/verified_human_style_followup_20261026/experiment.py',
             ROOT / 'experiments/author_generalization/author_style_controlled.py']
    dump(HERE / 'SCREEN_BINDINGS.json', {str(p.relative_to(ROOT)): sha(p) for p in paths})


if __name__ == '__main__':
    main()

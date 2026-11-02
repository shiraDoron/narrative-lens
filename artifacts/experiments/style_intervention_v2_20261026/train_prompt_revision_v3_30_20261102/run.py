"""Prompt-only v3: same 30 TRAIN originals, generator, decoding and guard code.

No training, test evaluation, human validation, external judge or output selection.
"""
from pathlib import Path
import argparse
import collections
import difflib
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

OUT = Path(__file__).resolve().parent
STUDY = OUT.parent
ROOT = STUDY.parents[2]
V2 = STUDY / 'train_prompt_revision_30_20261101'
PREVIOUS = ROOT / 'artifacts/experiments/verified_human_style_followup_20261026'

ADDENDUM = '''

Additional targeted preservation safeguards (v3):

Preserve event characterization and political framing. Do not change riots to protests, murder to damage, or bullying to aggressive behavior. A politically loaded event label must retain its meaning, evaluative force and polarity.

Preserve rhetorical intensity exactly. Neither soften nor intensify insults, accusations, praise, criticism or rhetorical stance. An insult must not become a neutral description; an accusation must not become mild criticism. Preserve the force of comparisons such as moral and economic superiority, not just generic approval.

Preserve certainty in context, attached to the same claim. Do not change may to will, likely to a factual assertion, going to lose to destined to lose, allegedly to an unqualified claim, or claims to a factual statement. Keep the original certainty/uncertainty expressions and their scope. Distinguish predictions, possibilities, intentions, obligations and actual effects.

Preserve participant roles and attribution: the same subject must perform the same action on the same object, and the same person must say, believe, allege, quote or be accused of the same thing. Fighting someone's wars is not facing those people in battle. Preserve personal versus collective experience; do not replace I with we when that adds a group claim. Do not replace a personal friend with a political ally, or net worth with assets.

Preserve quantifiers and limits exactly: all, some, many, few, most, only, approximately, allegedly one-time, less than, and similar expressions. Do not drop, replace, strengthen or weaken a quantifier, degree word or comparison. Preserve numbers, dates and numerical expressions as written, including 10 rather than ten and 5 1/2 rather than five and a half; this preserves the same content without changing representation.

Preserve all text inside quotation marks verbatim, including words, punctuation and capitalization. Do not move punctuation into or out of the quoted content. Do not paraphrase direct quotations, quote fragments or quoted titles. Changing quotation order is safe only if attribution and discourse relations remain identical.

Preserve metaphorical claims that contribute to stance or framing. Two countries inside America's borders must not become two regions. Preserve the political force and logical content of a metaphor rather than replacing it with a weaker neutral claim.

No invented interpretation: do not add explanations, motives, instruments or implications not stated in the original. Did not build their muscles at a wellness club does not license embodying the hard work of the American workforce. Do not turn strangers into anonymous sources or invent bulldozers from an axe metaphor. Do not omit a claim while replacing it with a new evaluation.

These safeguards do not permit a near-copy as the default. Still substantially change the author's stylistic signature through safe sentence restructuring, clause order, sentence-length distribution, syntax, active/passive voice, discourse markers, punctuation outside quotations, conversational markers and non-evaluative idioms. Change first-person phrasing only when the experiencer and claim stay the same. Avoid synonym-only rewriting. If a politically meaningful expression cannot safely change, keep that expression and restructure the surrounding syntax instead.

The goal remains: different author style, same content and stance. Return only the rewritten text.'''


def load_v2():
    spec = importlib.util.spec_from_file_location('frozen_v2_prompt_run', V2 / 'run.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.OUT = OUT  # Output redirect only; all generator/validation code is inherited unchanged.
    return m


def unchanged(m):
    protected = m.read('protected_inputs_sha256.json')
    bad = [name for name, h in protected.items() if m.sha(ROOT / name) != h]
    assert not bad, bad
    return len(protected)


def prepare():
    m = load_v2()
    if (OUT / 'protocol.json').exists():
        unchanged(m)
        return
    cohort = m.records(V2 / 'analysis_cohort.csv')
    comparison = m.records(V2 / 'comparison_30.csv')
    ids = {r['ID']: r for r in comparison}
    assert len(cohort) == len(ids) == 30
    assert all(r['split'] == 'train' and r['text'] == ids[r['row_id']]['Original'] for r in cohort)
    m.write_csv('analysis_cohort.csv', cohort)
    m.write_csv('frozen_comparison_inputs.csv', comparison)
    baseline = (V2 / 'prompt.txt').read_text(encoding='utf-8')
    prompt = baseline + ADDENDUM
    (OUT / 'prompt_v3.txt').write_text(prompt, encoding='utf-8')
    (OUT / 'prompt.txt').write_text(prompt, encoding='utf-8')
    (OUT / 'prompt_delta.diff').write_text(''.join(difflib.unified_diff(baseline.splitlines(True), prompt.splitlines(True), fromfile='v2/prompt.txt', tofile='v3/prompt_v3.txt')), encoding='utf-8')
    m.dump('generator_manifest.json', json.loads((V2 / 'generator_manifest.json').read_text(encoding='utf-8')))
    protocol = json.loads((V2 / 'protocol.json').read_text(encoding='utf-8'))
    protocol.update(created_at_utc=m.now(), version='New Normalized v3',
        comparison='New Normalized v2 versus v3 on identical 30 TRAIN sources',
        parent_protocol_sha256=m.sha(V2 / 'protocol.json'),
        parent_prompt_sha256=m.sha(V2 / 'prompt.txt'), prompt_sha256=m.sha(OUT / 'prompt.txt'),
        sole_intended_intervention='Append targeted preservation instructions to unchanged v2 prompt',
        original_only_inputs=True, external_llm_review_performed=False,
        prompt_retains_entire_v2_prefix=prompt.startswith(baseline),
        max_tokens=320, attempts_per_text=1, candidate_selection=False)
    m.dump('protocol.json', protocol)
    guarded = [STUDY / 'study.py', PREVIOUS / 'experiment.py', ROOT / 'experiments/author_generalization/author_style_controlled.py', V2 / 'run.py']
    m.dump('unchanged_guard_code_sha256.json', {str(p.relative_to(ROOT)): m.sha(p) for p in guarded})
    protected = {str(p.relative_to(ROOT)): m.sha(p) for p in STUDY.rglob('*')
                 if p.is_file() and OUT not in p.parents and not {'__pycache__', 'runtime'}.intersection(p.parts)}
    for p in guarded + [PREVIOUS / 'author_splits.csv', PREVIOUS / 'split_definitions.csv', PREVIOUS / 'style_feature_definitions.json']:
        protected[str(p.relative_to(ROOT))] = m.sha(p)
    m.dump('protected_inputs_sha256.json', protected)
    m.event('prepare_v3', n=30, source='Original only', no_test=True, protected_files=len(protected))
    print('Prepared 30 TRAIN originals; unchanged v2 prompt plus v3 safeguards.', flush=True)


def generate():
    m = load_v2()
    unchanged(m)
    m.generate()
    unchanged(m)


def validate():
    m = load_v2()
    unchanged(m)
    m.validate()
    prior = json.loads((V2 / 'validation_method.json').read_text(encoding='utf-8'))
    current = m.read('validation_method.json')
    keys = ['ner_revision', 'nli_revision', 'semantic_revision', 'classifier_token_limit', 'semantic_token_limit', 'nli_pair_token_limit']
    assert all(prior[k] == current[k] for k in keys)
    m.dump('validator_identity_audit.json', dict(same_model_revisions_and_token_limits=True,
        unchanged_source_files=m.read('unchanged_guard_code_sha256.json'),
        semantic_threshold=.85, nli_threshold=.6, no_threshold_or_filter_changes=True))
    unchanged(m)


def report():
    from report_v3 import main
    main()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', required=True, choices=['prepare', 'generate', 'validate', 'report', 'all'])
    stage = parser.parse_args().stage
    if stage == 'all':
        for step in ['prepare', 'generate', 'validate', 'report']:
            subprocess.run([sys.executable, '-u', str(Path(__file__)), '--stage', step], check=True)
    else:
        globals()[stage]()

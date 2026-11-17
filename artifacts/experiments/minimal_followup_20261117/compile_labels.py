"""Keep AI evidence screening separate from unfilled human annotation forms."""
from collections import Counter

from prepare import HERE, PREVIOUS, dump, read, save, text_sha


def main():
    target = HERE / 'AI_LABEL_SCREEN.csv'
    if target.exists():
        raise ValueError('Preserve prior AI decisions; use a new version')
    import csv
    with (HERE / 'AI_SCREEN_NOTES.tsv').open(encoding='utf-8-sig', newline='') as stream:
        notes = list(csv.DictReader(stream, delimiter='\t'))
    forms = read(HERE / 'LABEL_97_BLIND.csv')
    assert len(notes) == 97 and {r['review_id'] for r in notes} == {r['review_id'] for r in forms}
    note_by_id = {r['review_id']: r for r in notes}
    key = {r['review_id']: r for r in read(HERE / 'LABEL_97_PRIVATE_KEY.csv')}
    results = []
    for form in forms:
        note = note_by_id[form['review_id']]
        assert note['evidence_span'] in form['Original'], form['review_id']
        assert note['category'] in ('insufficient', 'research')
        results.append(dict(review_id=form['review_id'], Original=form['Original'], ai_label='Unclear',
                            ai_evidence_status=note['category'], evidence_span=note['evidence_span'],
                            rationale_he=note['rationale_he'], reviewer_type='ai', reviewer_id='Codex_current_conversation',
                            review_date='2026-11-17', human_validated=False,
                            source_sha256=text_sha(form['Original']), source_label_changed=False))
    save(target, results)
    counts = Counter(r['ai_evidence_status'] for r in results)
    nominated = [r for r in results if key[r['review_id']]['old_provisional200'] == 'True']
    pool = read(PREVIOUS / 'TRAIN_POOL_202.csv')
    dump(HERE / 'LABEL_SCREEN_SUMMARY.json', dict(
        additional97=dict(n=97, ai_unambiguous_binary_candidates=0, insufficient=counts['insufficient'], research_decision=counts['research']),
        provisional200=dict(existing_binary_proposals=105, nominated_additional=len(nominated),
                            additional_unambiguous_binary_candidates=0,
                            additional_insufficient=sum(r['ai_evidence_status'] == 'insufficient' for r in nominated),
                            additional_research_decision=sum(r['ai_evidence_status'] == 'research' for r in nominated)),
        reserve_sources=2, total_train_pool=len(pool), new_human_gold_labels=0,
        interpretation='Conservative text-only AI screen cannot establish95 additional binary sources. Existing105 proposals remain unvalidated; not105 confirmed eligible texts.',
        original_source_labels_overwritten=False, author_identity_not_used=True,
        criterion='Require an adopted ideological framing in this excerpt; mere actor/party, faith, topic, geopolitical side or reported quote insufficient',
        limitations=['not independent human review', 'research group may include genuine Left/Right after construct/irony/attribution adjudication',
                     'apply any clarified construct consistently to old105 too; do not loosen only to reach200',
                     'no factual verification or author inference']
    ))


if __name__ == '__main__':
    main()

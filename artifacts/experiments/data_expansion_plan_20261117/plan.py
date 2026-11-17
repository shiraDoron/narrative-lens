"""Planning arithmetic and Train-only leakage screens; never training schedules."""
import itertools
import math
import re

from inventory import HERE, FOLLOW, V1, dump, read, save, text_sha


def shingles(text):
    words = re.findall(r'\w+', text.casefold())
    return {tuple(words[i:i+5]) for i in range(max(0, len(words)-4))}


def main():
    if (HERE / 'WORKLOAD_SCENARIOS.csv').exists():
        raise ValueError('Keep planning estimates versioned')
    scenarios = []
    for accepted_core, accepted_local in [(105, 0), (105, 14), (95, 14), (90, 0)]:
        deficit = 200-accepted_core-accepted_local
        for yield_rate in (.4, .6, .8):
            scenarios.append(dict(accepted_core_assumption=accepted_core, accepted_local_assumption=accepted_local,
                                  deficit=deficit, assumed_yield=yield_rate,
                                  candidate_articles_to_screen=math.ceil(deficit/yield_rate),
                                  empirical_yield=False, optimizer_budget_changed=False))
    save(HERE / 'WORKLOAD_SCENARIOS.csv', scenarios)
    workload = [
        dict(task='setup sampling/QA and prepare reviewed candidate package', unit_count=1, low_minutes_per_unit=180, high_minutes_per_unit=300),
        dict(task='existing105 labels, two independent raters', unit_count=210, low_minutes_per_unit=2, high_minutes_per_unit=3),
        dict(task='160 candidate articles: retrieval/byline/window triage, local plus external', unit_count=160, low_minutes_per_unit=3, high_minutes_per_unit=5),
        dict(task='160 new candidate labels, two independent raters', unit_count=320, low_minutes_per_unit=2, high_minutes_per_unit=3),
        dict(task='adjudication on assumed25 percent of265 sources', unit_count=67, low_minutes_per_unit=3, high_minutes_per_unit=5),
        dict(task='deduplication, source/author/period/topic audit and immutable handoff', unit_count=1, low_minutes_per_unit=180, high_minutes_per_unit=300),
    ]
    for row in workload:
        row['low_person_hours'] = row['unit_count']*row['low_minutes_per_unit']/60
        row['high_person_hours'] = row['unit_count']*row['high_minutes_per_unit']/60
    save(HERE / 'PERSON_HOUR_ESTIMATES.csv', workload)
    selected = read(HERE / 'AI_CANDIDATES_14.csv')
    old_train = read(V1 / 'TRAIN_POOL_202.csv')
    all_source_hashes = {r['text_sha256'] for r in read(FOLLOW / 'text_annotations.csv')}
    assert all(text_sha(r['Original']) == r['source_sha256'] for r in selected)
    exact = [r['candidate_id'] for r in selected if r['source_sha256'] in all_source_hashes]
    assert not exact
    near = []
    for a, b in itertools.combinations(selected, 2):
        sa, sb = shingles(a['Original']), shingles(b['Original'])
        j = len(sa & sb)/max(1, len(sa | sb))
        if j >= .8:
            near.append(dict(candidate=a['candidate_id'], other=b['candidate_id'], jaccard=j))
    for a in selected:
        for b in old_train:
            sa, sb = shingles(a['Original']), shingles(b['Original'])
            j = len(sa & sb)/max(1, len(sa | sb))
            if j >= .8:
                near.append(dict(candidate=a['candidate_id'], other=b['ID'], jaccard=j))
    dump(HERE / 'CANDIDATE_ISOLATION_AUDIT.json', dict(exact_match_existing_all_split_source_hashes=exact,
         train_only_near_duplicates_jaccard_ge_08=near, threshold_role='duplicate triage only, not a rewrite/style acceptance threshold',
         heldout_text_used=False, heldout_predictions=False,
         limitation='Hash/URL and TRAIN lexical screens do not exclude held-out semantic/syndicated/event overlap; steward review required'))
    dump(HERE / 'COLLECTION_PLAN_PROPOSED.json', dict(
         status='proposal_only_not_a_frozen_protocol_amendment', target_human_accepted_train_sources=200,
         existing105_human_accepted_status='unknown', newly_human_accepted_in_this_session=0,
         initial_gap_assuming_old105_accept=95, conditional_gap_if_local14_also_accept=81,
         first_calibration_batch=dict(candidate_articles=45, per_existing_train_author=5,
                                       composition='local additional article candidates first, public new articles to fill author coverage; no writer-implied labels'),
         eligibility_yield='measure real source eligibility after independent human ratings and adjudication; planning40/60/80 percent are not observed',
         collection_rule='single explicit named byline; same nine Train authors; one standalone contiguous35–100 word excerpt per parent article; keep all attempts/reasons; no held-out selection',
         alternate_excerpt_rule='new source ID and paragraph offsets; same parent group; existing unclear excerpt retained and never relabeled; requires explicit future sampling amendment',
         priority='Creators public same-genre archives around observed author-specific dates; other official same-author text essays only as separately audited domain cohorts',
         access='no401/403 bypass; honor access limitations; no guaranteed yield or invented unseen URL inventory',
         stop_rule='200 independently accepted unique article groups under approved sampling plan; do not stop at200 machine suggestions',
         human_label_options=['Left', 'Right', 'Unclear'], labels_from_author=False,
         time_estimate_person_hours=dict(low=sum(r['low_person_hours'] for r in workload), high=sum(r['high_person_hours'] for r in workload)),
         time_estimate_scope='data preparation and labels only; excludes rewrite generation/pairQC, training and held-out evaluation',
         minimal_prompt_development='stopped; possible control only; retain all negative results',
         training_protocol_changed=False, training_updates_changed=False, train_run=False, test_run=False))


if __name__ == '__main__':
    main()

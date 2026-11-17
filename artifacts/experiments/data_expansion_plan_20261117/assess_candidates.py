"""Illustrative text-grounded AI shortlist, never human gold or training intake."""
import re
import random

from inventory import HERE, ROOT, V2, dump, normalized_url, paragraphs, read, save, text_sha

# Identified after reading local text windows without using author identity as a label.
SELECTION = [
 ('article:b9c757558f2d5173:p14-15', 'Right', 'Amnesty is not the answer.', 'התנגדות לחנינה והדגשת גבולות וריבונות כעמדה מאומצת.'),
 ('article:55b7075a8751b9b5:p8-9', 'Right', 'Markets, not people, do that.', 'העדפת מנגנון שוק והתנגדות להשקעה ממשלתית, גם כשהשלטון רפובליקני.'),
 ('article:98811a164e66e9d5:p14-15', 'Right', 'everyone, not just the rich, will be poorer for it.', 'התנגדות למס עושר על בסיס פגיעה כלכלית כללית.'),
 ('article:12e14ba6de1fa64c:p13-14', 'Right', 'allowing innovation and competition to deliver results', 'העדפת תחרות וחדשנות על פני מנדטים והגנות בחקיקה.'),
 ('article:d0edaaeed0246baf:p10-11', 'Right', 'A project that moves forward due only to government intervention is a loser that the taxpayer is buying.', 'טיעון מפורש נגד השקעת המדינה ובעד הקצאת הון בשוק.'),
 ('article:0bbde86956884082:p5-6', 'Right', "The state shouldn't interfere.", 'עמדה מפורשת נגד סבסוד והתערבות המדינה בבחירות משפחתיות.'),
 ('article:dbdb16b080cf2b25:p8-9', 'Right', "All Americans' savings should be safe from such confiscation", 'מסגור מס עושר כהחרמת רכוש שיש להגן מפניה.'),
 ('article:2e55319b58af3d34:p7-8', 'Left', 'how your all-white neighborhood reflects your commitment to racial equality.', 'ביקורת מאומצת על הפרדה חברתית מתוך מחויבות לשוויון גזעי.'),
 ('article:43c0d2a12a1f4082:p19-21', 'Left', 'we need male allies to support our rightful place in representative democracy.', 'קריאה מאומצת לשותפות ולייצוג פוליטי של נשים; טעונה בדיקת אדם לפי ההגדרה.'),
 ('article:2f784c732746eda0:p19-20', 'Right', 'without turning to socialism.', 'שלילת צורך בסוציאליזם מתוך טיעון על הישגים כלכליים, ולא מתוך שם הכותב.'),
 ('article:ef662bddbfc967e0:p4-5', 'Left', "They shouldn't be rounded up. They should be made legal.", 'המלצה מפורשת להסדרת מעמד מהגרים ולא למעצרם.'),
 ('article:0d8baad1257f0973:p1-3', 'Right', "It's Democratic economic and social ideas that have destabilized France.", 'ביקורת מאומצת על רווחה, איגודים ושכר מינימום מתוך מסגור אנטי־מדינת רווחה.'),
 ('article:6dfe8d0ce7c4d067:p2-3', 'Right', 'What it has never generated once is a workable legislative proposal.', 'ביקורת מאומצת על תוכנית בריאות ממשלתית אוניברסלית של השמאל.'),
 ('article:73e4203962ba7e7d:p17-18', 'Right', "welfare's incentives undercut work and family formation and discourage self-sufficiency.", 'מסגור שמרני מפורש של רווחה כמעודדת תלות ופוגעת בעבודה ובמשפחה.'),
]
DEFERRED = {
 'L005': 'debt/tax discussion in inspected windows does not alone settle the adopted binary framing',
 'L012': 'possible body-signature/byline conflict; do not count until authorship resolved',
 'L021': 'satirical narrator; independent irony/stance adjudication required',
 'L053': 'no new self-contained binary window selected in this targeted pass',
 'L075': 'religious criticism and quoted context require construct/attribution adjudication',
 'L079': 'geopolitical framing is not automatically US Left/Right',
 'L087': 'targeted poverty benefits versus fiscal retrenchment requires construct adjudication',
 'L089': 'crime/reporting critique in inspected windows is not sufficient for binary stance',
}


def main():
    if (HERE / 'AI_CANDIDATES_14.csv').exists():
        raise ValueError('Keep prior shortlist; use a new version')
    bank = {r['candidate_id']: r for r in read(HERE / 'LOCAL_WINDOW_BANK.csv')}
    candidates, reviews, keys = [], [], []
    for cid, label, evidence, reason in SELECTION:
        row = bank[cid]
        assert evidence in row['Original'] and row['split'] == 'train'
        assert row['role'] != 'existing105_do_not_replace'
        assert not re.search(r'Photo credit:|Every Tuesday at|is a nationally syndicated columnist', row['Original'])
        candidates.append(dict(**row, ai_proposed_label=label, evidence_span=evidence, ai_reason_he=reason,
                               reviewer_type='ai', human_validated=False, corpus_label_changed=False))
    assert len({r['article_group'] for r in candidates}) == 14
    save(HERE / 'AI_CANDIDATES_14.csv', candidates)
    shuffled = list(candidates)
    random.Random(2026111703).shuffle(shuffled)
    for i, row in enumerate(shuffled):
        blind = f'C{i+1:03}'
        reviews.append(dict(review_id=blind, Original=row['Original'], label='', evidence_span='', reason='',
                            confidence='', reviewer_type='', reviewer_id='', review_date='', assistance_used=''))
        keys.append(dict(review_id=blind, candidate_id=row['candidate_id'], article_group=row['article_group'],
                         author=row['author'], source_url=row['source_url'], source_sha256=text_sha(row['Original']),
                         old_ID=row['old_ID'], role=row['role'], ai_proposed_label=row['ai_proposed_label']))
    save(HERE / 'CANDIDATE_HUMAN_BLIND_14.csv', reviews)
    save(HERE / 'CANDIDATE_PRIVATE_KEY_14.csv', keys)
    pages = ['# בדיקת מועמדים מקוריים — ללא שכתוב', '', 'Left / Right / Unclear. הצעות AI, זהות כותב ומקור אינן מוצגות. אין להעביר את המפתח למתייג לפני סיום.', '']
    for row in reviews:
        pages += [f"## {row['review_id']}", '', row['Original'], '', '| שדה | תשובה |', '|---|---|',
                  '| Left / Right / Unclear | |', '| ראיה מדויקת ונימוק | |', '| סוקר / תאריך / סיוע | |', '']
    (HERE / 'CANDIDATE_REVIEW_14_HE.md').write_text('\n'.join(pages), encoding='utf-8')
    old_key = {r['review_id']: r for r in read(V2 / 'LABEL_97_PRIVATE_KEY.csv')}
    save(HERE / 'DEFERRED_TARGETED_SOURCES.csv', [dict(old_blind_id=k, old_ID=old_key[k]['ID'], reason=v,
         decision='not accepted or excluded from corpus; no new candidate selected in this developmental pass') for k, v in DEFERRED.items()])
    # Conservative alias grouping: same slug with optional publisher hash suffix is not a new article.
    articles = read(HERE / 'TRAIN_ARTICLE_INVENTORY.csv')
    strip_suffix = lambda u: re.sub(r'-[0-9a-f]{5,8}$', '', normalized_url(u))
    aliases = []
    for target in read(HERE / 'UNRETRIEVED_ARCHIVE_TARGETS.csv'):
        matches = [r for r in articles if strip_suffix(r['source_url']) == strip_suffix(target['source_url'])]
        aliases.append(dict(archive_url=target['source_url'], matched_cached_urls='|'.join(r['source_url'] for r in matches),
                            status='probable publisher URL alias; not additional sample' if matches else 'unresolved',
                            counted_as_new=False))
    save(HERE / 'ARCHIVE_ALIAS_AUDIT.csv', aliases)
    # Look for explicit biographical signatures conflicting with the publisher's named byline.
    # A flag is a stewardship question, never automatic authorship reassignment.
    conflicts = []
    for row in articles:
        _, ps = paragraphs((ROOT / row['source_snapshot']).read_text(encoding='utf-8'))
        for p in ps[-4:]:
            for name in ('John Stossel', 'Tom Margenau'):
                surname = name.split()[-1]
                if (name in p or surname in p) and re.search(r'posts a new video|author of|Social Security|column|email|visit', p, re.I):
                    if surname.lower() not in row['author']:
                        conflicts.append(dict(article_group=row['article_group'], old_ID=row['old_ID'],
                                              recorded_author=row['author'], source_url=row['source_url'],
                                              body_signature_evidence=p, potential_other_writer=name,
                                              role=row['role'], decision='resolve before future inclusion; no source reassignment performed'))
    if conflicts:
        save(HERE / 'AUTHORSHIP_REVIEW_FLAGS.csv', conflicts)
    dump(HERE / 'CANDIDATE_SUMMARY.json', dict(
         selected_candidates=14, unique_article_groups=14, ai_label_counts={label: sum(r['ai_proposed_label'] == label for r in candidates) for label in ('Left', 'Right')},
         recovered_previously_unrepresented_articles=sum(r['role'] == 'unrepresented_cached_article' for r in candidates),
         alternate_excerpts_from_noncore_articles=sum(r['role'] == 'alternate_excerpt_of_unclear_article' for r in candidates),
         human_accepted_new=0, all_candidates_require_human_review=True,
         conditional_core105_plus14=119, conditional_remaining_after_all119_accepted=81,
         original_additional_gap_if105_all_accepted=95,
         formula='remaining = max(0,200 - human_accepted_existing105 - human_accepted_distinct_additional_articles)',
         bank_windows_not_independent_samples=True, yield_not_estimated_from_purposive_shortlist=True,
         deferred_targeted_source_groups=len(DEFERRED),
         nominal_archive_new_urls=len(aliases), probable_aliases=sum(r['status'].startswith('probable') for r in aliases),
         confirmed_novel_archive_articles=0,
         authorship_flagged_article_groups=len({r['article_group'] for r in conflicts}),
         no_historical_labels_splits_or_budget_changed=True))


if __name__ == '__main__':
    main()

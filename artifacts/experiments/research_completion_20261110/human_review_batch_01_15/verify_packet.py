"""Verify rendered Markdown pairs and empty answers before human handoff."""

import html
import json
import re

from build_packet import HERE, RUN, read, sha, text_sha, verify


def check():
    verify()
    packet = HERE / 'REVIEW_15_HE.md'
    manifest = json.loads((HERE / 'SELECTION_MANIFEST.json').read_text(encoding='utf-8'))
    text = packet.read_text(encoding='utf-8')
    canonical = {row['ID']: row for row in read(RUN / 'received_rewrites_75.csv')}
    pattern = r'## זוג \d+ — (creators:[^\n]+)\n\n\| Original \| Style Rewrite \|\n\|---\|---\|\n\| (.*?) \| (.*?) \|\n'
    pairs = re.findall(pattern, text)
    assert len(pairs) == len({rid for rid, _, _ in pairs}) == 15
    assert [rid for rid, _, _ in pairs] == [row['ID'] for row in manifest['rows']]
    for (rid, original, rewrite), receipt in zip(pairs, manifest['rows']):
        original = html.unescape(original.replace('<br>', '\n'))
        rewrite = html.unescape(rewrite.replace('<br>', '\n'))
        assert original == canonical[rid]['Original']
        assert rewrite == canonical[rid]['ChatGPT_Style_Rewrite']
        assert text_sha(original) == receipt['source_sha256']
        assert text_sha(rewrite) == receipt['rewrite_sha256']
    for field in ['Meaning Preserved', 'Narrative Preserved', 'Style Change Valid', 'הערות וביטויים תומכים']:
        assert text.count('| ' + field + ' | |') == 15
    assert sha(packet) == manifest['packet_sha256']
    assert manifest['qc_assisted_not_blind'] and not manifest['human_decisions_filled']
    for path in [packet, HERE / 'LEFT_RIGHT_LABELING_GUIDE_HE.md']:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            assert (path.parent / target).exists()
    print('Verified15 exact text pairs,45 empty judgment fields,15 empty notes, selection hashes and local links.')


if __name__ == '__main__':
    check()

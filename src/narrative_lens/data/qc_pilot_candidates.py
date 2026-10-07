"""
Per-author QC report for the Phase 1 pilot candidates (Dataset V2).

Reads data/candidates/v2_pilot/pilot_authors_raw.csv (produced by
build_v2_pilot_dataset.py) and, for each candidate author, reports:
  - raw count, usable count after basic cleaning (min length, non-empty)
  - exact duplicate count
  - near-duplicate clusters (via text_dedup.find_near_duplicate_clusters, threshold=0.7)
  - date range, avg text length
  - vocabulary overlap (Jaccard on top-100 words) with the EXISTING accounts already in the
    same narrative in data/raw/*.csv - a rough proxy for "does this author actually add
    new diversity, or just repeat existing accounts' framing/vocabulary"
  - PASS/FAIL against the quality gate: >=75 usable unique texts, no excessive duplication
    (near-dup clusters covering <30% of usable texts)

Does NOT write anywhere - read-only report to stdout. Run this AFTER
build_v2_pilot_dataset.py has produced real scraped data.
"""

import re
from collections import Counter

import pandas as pd

from narrative_lens.data.text_dedup import find_near_duplicate_clusters, normalize_for_exact

PILOT_PATH = "data/candidates/v2_pilot/pilot_authors_raw.csv"
MIN_USABLE_FOR_PASS = 75
MAX_NEAR_DUP_RATIO = 0.30
MIN_TEXT_LEN = 15

WORD_RE = re.compile(r"[a-zA-Z]{3,}")
STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "have", "has", "are", "was",
    "will", "our", "you", "your", "not", "but", "all", "who", "its", "their", "they",
}


def top_words(texts, n=100):
    counter = Counter()
    for t in texts:
        counter.update(w.lower() for w in WORD_RE.findall(t) if w.lower() not in STOPWORDS)
    return set(w for w, _ in counter.most_common(n))


def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    pilot = pd.read_csv(PILOT_PATH)

    tw = pd.read_csv("data/raw/twitter_natural_dataset.csv")
    tg = pd.read_csv("data/raw/telegram_natural_dataset.csv")
    existing = pd.concat([tw, tg], ignore_index=True)

    for (narrative, author), group in pilot.groupby(["narrative", "author"]):
        texts_raw = group["text"].dropna().astype(str).tolist()
        raw_count = len(texts_raw)

        exact_seen = set()
        usable = []
        exact_dupes = 0
        for t in texts_raw:
            norm = normalize_for_exact(t)
            if len(t.strip()) < MIN_TEXT_LEN:
                continue
            if norm in exact_seen:
                exact_dupes += 1
                continue
            exact_seen.add(norm)
            usable.append(t)

        usable_count = len(usable)
        clusters, _ = find_near_duplicate_clusters(usable, threshold=0.7) if usable else ({}, 0)
        near_dup_members = sum(len(m) - 1 for m in clusters.values())  # extra copies beyond 1 rep
        near_dup_ratio = near_dup_members / usable_count if usable_count else 0.0
        usable_unique = usable_count - near_dup_members

        dates = pd.to_datetime(group["timestamp"], errors="coerce", utc=True).dropna()
        date_range = (dates.min(), dates.max()) if len(dates) else (None, None)
        avg_len = sum(len(t) for t in usable) / usable_count if usable_count else 0

        candidate_vocab = top_words(usable)
        existing_narr_texts = existing[existing["narrative_name"] == narrative]["text"].dropna().astype(str).tolist()
        existing_vocab = top_words(existing_narr_texts)
        overlap = jaccard(candidate_vocab, existing_vocab)

        passed = usable_unique >= MIN_USABLE_FOR_PASS and near_dup_ratio <= MAX_NEAR_DUP_RATIO

        print(f"\n=== {narrative} / @{author} ===")
        print(f"  raw={raw_count} usable_after_cleaning={usable_count} exact_dupes={exact_dupes}")
        print(f"  near_dup_clusters={len(clusters)} near_dup_extra_copies={near_dup_members} "
              f"near_dup_ratio={near_dup_ratio:.2f}")
        print(f"  usable_unique={usable_unique}")
        print(f"  date_range={date_range}")
        print(f"  avg_text_len={avg_len:.0f}")
        print(f"  vocab_overlap_with_existing_{narrative}_accounts={overlap:.2f}")
        print(f"  QUALITY GATE: {'PASS' if passed else 'FAIL'} "
              f"(need usable_unique>={MIN_USABLE_FOR_PASS} and near_dup_ratio<={MAX_NEAR_DUP_RATIO})")


if __name__ == "__main__":
    main()

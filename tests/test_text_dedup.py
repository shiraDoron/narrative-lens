"""Tests for narrative_lens.data.text_dedup - near-duplicate detection via MinHash/LSH.
Uses small in-memory text lists only (no files, no ML models) - must stay fast."""

from narrative_lens.data.text_dedup import deduplicate_texts, get_shingles, jaccard, normalize_for_exact


def test_deduplicate_texts_keeps_first_of_near_duplicate_cluster():
    texts = [
        "The government announced new sanctions today against several officials",
        "The government announced new sanctions today against several officials.",
        "Completely unrelated text about a totally different subject matter here",
    ]
    kept_indices, cluster_summaries = deduplicate_texts(texts)

    assert kept_indices == [0, 2]
    assert len(cluster_summaries) == 1
    assert cluster_summaries[0]["kept_index"] == 0
    assert cluster_summaries[0]["dropped_indices"] == [1]
    assert cluster_summaries[0]["size"] == 2


def test_deduplicate_texts_keeps_all_distinct_texts():
    texts = [
        "First distinct sentence about elections and voting rights",
        "Second distinct sentence about climate change policy",
        "Third distinct sentence about economic sanctions on trade",
    ]
    kept_indices, cluster_summaries = deduplicate_texts(texts)

    assert kept_indices == [0, 1, 2]
    assert cluster_summaries == []


def test_deduplicate_texts_empty_input():
    kept_indices, cluster_summaries = deduplicate_texts([])
    assert kept_indices == []
    assert cluster_summaries == []


def test_jaccard_identical_sets():
    assert jaccard({("a", "b")}, {("a", "b")}) == 1.0


def test_jaccard_disjoint_sets():
    assert jaccard({("a", "b")}, {("c", "d")}) == 0.0


def test_jaccard_both_empty():
    assert jaccard(set(), set()) == 1.0


def test_get_shingles_short_text_returns_single_tuple():
    shingles = get_shingles("hello world", k=3)
    assert shingles == {("hello", "world")}


def test_get_shingles_empty_text():
    assert get_shingles("", k=3) == set()


def test_normalize_for_exact_collapses_whitespace_and_case():
    assert normalize_for_exact("  Hello   World  \n") == "hello world"

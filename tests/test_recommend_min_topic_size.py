"""Tests for narrative_lens.train_topics.recommend_min_topic_size() - pure function of
corpus_size, no BERTopic model instantiation/training involved."""

import pytest

from narrative_lens.train_topics import recommend_min_topic_size


def test_recommend_min_topic_size_at_1000_is_validated_constant():
    assert recommend_min_topic_size(1_000) == 10


def test_recommend_min_topic_size_at_anchor_16000_is_validated_constant():
    assert recommend_min_topic_size(16_000) == 10


def test_recommend_min_topic_size_below_anchor_is_flat_10():
    for corpus_size in (1, 100, 4_000, 8_000, 12_000, 16_062):
        assert recommend_min_topic_size(corpus_size) == 10


def test_recommend_min_topic_size_extrapolates_above_anchor():
    assert recommend_min_topic_size(100_000) == 19
    assert recommend_min_topic_size(1_000_000) == 31


def test_recommend_min_topic_size_is_monotonic_non_decreasing():
    sizes = [1_000, 16_062, 50_000, 100_000, 500_000, 1_000_000, 10_000_000]
    values = [recommend_min_topic_size(s) for s in sizes]
    assert values == sorted(values)


def test_recommend_min_topic_size_never_exceeds_ceiling():
    assert recommend_min_topic_size(10 ** 12) <= 100


def test_recommend_min_topic_size_rejects_non_positive():
    with pytest.raises(ValueError):
        recommend_min_topic_size(0)
    with pytest.raises(ValueError):
        recommend_min_topic_size(-5)

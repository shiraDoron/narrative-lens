"""Tests for the soft topic-distribution normalization logic in
narrative_lens.topic_modeling.stance.TopicAnalysisPipeline.get_topic_distribution().

Deliberately avoids loading any real BERTopic model (no train_topics.build_and_save_topics(),
no BERTopic.load()) - instead builds a bare TopicAnalysisPipeline instance (bypassing
__init__) and stubs out topic_model.approximate_distribution()/get_topic_label() so only the
pure normalization/sorting/top-n logic under test actually runs. Keeps this test fast and
independent of any saved model file on disk."""

from narrative_lens.topic_modeling.stance import TopicAnalysisPipeline


class _FakeBertopicModel:
    def __init__(self, scores):
        self._scores = scores

    def approximate_distribution(self, texts):
        return [self._scores], None

    def get_topic(self, topic_id):
        return [(f"word{topic_id}", 1.0)]


def _make_pipeline(scores):
    pipeline = TopicAnalysisPipeline.__new__(TopicAnalysisPipeline)
    pipeline.use_cleaned_preprocessing = False
    pipeline.llm_labels = {}
    pipeline.topic_model = _FakeBertopicModel(scores)
    return pipeline


def test_get_topic_distribution_normalizes_to_sum_one():
    pipeline = _make_pipeline([0.2, 0.0, 0.6, 0.0, 0.2])
    result = pipeline.get_topic_distribution("some text", top_n=3)

    assert len(result) == 3
    total = sum(item["score"] for item in result)
    assert abs(total - 1.0) < 1e-9


def test_get_topic_distribution_sorted_descending_by_score():
    pipeline = _make_pipeline([0.1, 0.5, 0.0, 0.3])
    result = pipeline.get_topic_distribution("some text", top_n=3)

    scores = [item["score"] for item in result]
    assert scores == sorted(scores, reverse=True)
    assert result[0]["topic_id"] == 1  # index of the largest raw score (0.5)


def test_get_topic_distribution_respects_top_n():
    pipeline = _make_pipeline([0.1, 0.2, 0.3, 0.4, 0.5])
    result = pipeline.get_topic_distribution("some text", top_n=2)
    assert len(result) == 2


def test_get_topic_distribution_empty_when_all_zero_scores():
    pipeline = _make_pipeline([0.0, 0.0, 0.0])
    result = pipeline.get_topic_distribution("some text", top_n=3)
    assert result == []


def test_get_topic_distribution_includes_label():
    pipeline = _make_pipeline([0.0, 1.0])
    result = pipeline.get_topic_distribution("some text", top_n=1)
    assert result[0]["label"] == "word1"

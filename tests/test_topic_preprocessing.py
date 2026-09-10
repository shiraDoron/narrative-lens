"""Tests for narrative_lens.topic_modeling.topic_preprocessing - pure string functions,
no ML models involved, must stay fast."""

from narrative_lens.topic_modeling.topic_preprocessing import (
    build_multiword_label,
    clean_text_for_topic_model,
    has_enough_content,
)


def test_clean_text_removes_urls():
    text = "Check this out https://example.com/path and www.example.org for more info."
    cleaned = clean_text_for_topic_model(text)
    assert "https://" not in cleaned
    assert "example.com" not in cleaned
    assert "example.org" not in cleaned


def test_clean_text_removes_bare_shortlink():
    text = "Read more at bit.ly/4bngYSJ right now"
    cleaned = clean_text_for_topic_model(text)
    assert "bit.ly" not in cleaned
    assert "bit" not in cleaned.split()


def test_clean_text_removes_mentions():
    text = "@SomeAccount said something interesting"
    cleaned = clean_text_for_topic_model(text)
    assert "@SomeAccount" not in cleaned
    assert "@" not in cleaned


def test_clean_text_splits_camelcase_hashtag():
    text = "Support #StandWithUkraine today"
    cleaned = clean_text_for_topic_model(text)
    assert "#" not in cleaned
    assert "Stand" in cleaned
    assert "With" in cleaned
    assert "Ukraine" in cleaned


def test_clean_text_is_idempotent():
    text = "Support #StandWithUkraine, see https://example.com and @account"
    once = clean_text_for_topic_model(text)
    twice = clean_text_for_topic_model(once)
    assert once == twice


def test_has_enough_content_true_for_real_sentence():
    cleaned = clean_text_for_topic_model("This is a normal sentence with real words")
    assert has_enough_content(cleaned)


def test_has_enough_content_false_for_url_only_text():
    cleaned = clean_text_for_topic_model("https://example.com/path")
    assert not has_enough_content(cleaned)


def test_has_enough_content_false_for_mentions_and_hashtags_only():
    cleaned = clean_text_for_topic_model("@a @b #c")
    assert not has_enough_content(cleaned)


def test_build_multiword_label_deduplicates_shared_words():
    topic_words = [("gaza ceasefire", 0.9), ("gaza humanitarian", 0.5), ("aid convoy", 0.2)]
    label = build_multiword_label(topic_words, top_n_words=3)
    assert label == "gaza ceasefire humanitarian"


def test_build_multiword_label_empty_input():
    assert build_multiword_label([]) == ""
    assert build_multiword_label(None) == ""


def test_build_multiword_label_respects_top_n_words():
    topic_words = [("one two three four", 0.9)]
    label = build_multiword_label(topic_words, top_n_words=2)
    assert label == "one two"

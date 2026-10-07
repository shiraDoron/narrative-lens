"""Tests for narrative_lens.features.style_normalization.normalize_style - pure text-level
style/formatting normalization (no models, no files) - must stay fast."""

from narrative_lens.features.style_normalization import normalize_style


def test_url_replaced_with_placeholder():
    text = "Check this out https://example.com/path?x=1 now"
    assert normalize_style(text) == "Check this out [URL] now"


def test_bare_shortlink_replaced_with_placeholder():
    text = "Link: bit.ly/4bngYSJ see more"
    assert normalize_style(text) == "Link: [URL] see more"


def test_mention_replaced_with_placeholder():
    text = "Thanks @SomeUser for sharing"
    assert normalize_style(text) == "Thanks [USER] for sharing"


def test_hashtag_split_camel_case_and_hash_removed():
    text = "Join us #StandWithUkraine today"
    assert normalize_style(text) == "Join us Stand With Ukraine today"


def test_hashtag_lowercase_preserved_without_hash():
    text = "trending #maga now"
    assert normalize_style(text) == "trending maga now"


def test_repeated_punctuation_collapsed():
    assert normalize_style("Really!!!") == "Really!"
    assert normalize_style("Why????") == "Why?"
    assert normalize_style("Wait.....") == "Wait..."


def test_word_elongation_collapsed():
    assert normalize_style("soooo good") == "soo good"


def test_whitespace_and_newlines_collapsed():
    text = "Line one\n\n\nLine   two"
    assert normalize_style(text) == "Line one Line two"


def test_named_entities_preserved():
    text = "Trump met NATO officials in Israel"
    assert normalize_style(text) == text


def test_empty_and_non_string_input():
    assert normalize_style("") == ""
    assert normalize_style(None) is None


def test_emoji_removed():
    text = "Great news \U0001F600 today"
    assert normalize_style(text) == "Great news today"

"""
Shared text-cleaning for the BERTopic soft-clustering pipeline (`models/saved_topic_model_soft_v2`).

This module is the SINGLE source of truth for the preprocessing applied:
  1. Before FITTING BERTopic (`train_topics.py`'s `build_and_save_topics()`), and
  2. Before SCORING new text against the fitted model at inference time
     (`stance.py`'s `TopicAnalysisPipeline.process_text()` / `.get_topic_distribution()`,
     when `model_path` points at `saved_topic_model_soft_v2`).

Why this matters (train/inference consistency): the soft_v2 model's `CountVectorizer` vocabulary
was fit on CLEANED text (URLs/@mentions removed, #hashtags split into real words). If raw,
uncleaned text is scored at inference time, tokens like "#EnergyFrontiers" arrive as a single
token that was NEVER in the fit-time vocabulary (the fit-time text had "Energy Frontiers" as two
separate tokens) - sklearn silently treats it as out-of-vocabulary (no error, just lost signal).
Importing `clean_text_for_topic_model` from this one module in both places guarantees the exact
same transformation runs on both sides.

IMPORTANT: this preprocessing is ONLY valid for `saved_topic_model_soft_v2` (and any future
re-fits that adopt it). The PINNED legacy model `models/saved_topic_model` was fit WITHOUT this
cleaning, and the existing classification checkpoints (`best_narrative_model_hybrid.pth`,
`best_model_hybrid_architecture.pth`) depend on that exact (uncleaned) behavior via
`TopicStanceLayer`'s `topic_id`-indexed embedding - do NOT apply this cleaning when using the
legacy model path (see `stance.py`'s `TopicAnalysisPipeline.__init__` for how this is gated).
"""

import re

# Found empirically (analyze_soft_topic_quality.py, calibration run): raw @mentions/#hashtags
# sometimes become entire spurious BERTopic topics on their own (e.g. a repeated channel
# signature like "@DDGeopolitics | Socials | Donate | Advertising" produced a topic literally
# labeled "ddgeopolitics") - these are source/channel artifacts, not narrative content.
URL_RE = re.compile(r"https?://\S+|www\.\S+")
# Found empirically (Experiment C review, 2026-08-31): bare (scheme-less) link-shortener URLs
# like "bit.ly/4bngYSJ" or "tinyurl.com/5xj483ws" are NOT matched by URL_RE above (no
# "https://"/"www." prefix), so they survive cleaning and leak into the BERTopic vectorizer as
# literal tokens "bit"/"ly" - confirmed to have contaminated a large topic's top representation
# ("bit ly telephone conversation..."). Explicit domain list (not a fully generic
# word.tld/path pattern, to avoid false-positive stripping of unrelated abbreviation-like text
# e.g. "U.S./European") covering the shorteners actually observed in data/raw/*.csv.
_SHORTLINK_DOMAINS = r"(?:bit\.ly|tinyurl\.com|t\.co|ow\.ly|buff\.ly|dlvr\.it|goo\.gl|is\.gd|rebrand\.ly)"
BARE_SHORTLINK_RE = re.compile(rf"\b{_SHORTLINK_DOMAINS}/\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
# Minimum number of real (2+ letter, alphabetic) word tokens required AFTER cleaning for a
# text to still be considered to have meaningful content (e.g. used by train_topics.py to drop
# texts that were pure URLs/mentions/hashtags - nothing left - from the BERTopic fit).
MIN_WORDS_AFTER_CLEAN = 3
_ALPHA_WORD_RE = re.compile(r"[A-Za-z]{2,}")


def _split_camel_case(word):
    """'StandWithUkraine' -> 'Stand With Ukraine' - so hashtag text still contributes real,
    separate word tokens to the topic model instead of one unsplittable blob token."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", word)


def clean_text_for_topic_model(text):
    """Removes URLs and @mentions entirely (no narrative-content value, high risk of turning
    into a source/channel-identity topic instead of a real one); strips the '#' from hashtags
    while splitting camelCase so the underlying words (often genuinely on-topic, e.g.
    "StandWithUkraine") remain in the text as real tokens. Idempotent: cleaning already-clean
    text is a safe no-op (no more URLs/mentions/hashtags left to remove/split)."""
    text = str(text)
    text = URL_RE.sub(" ", text)
    text = BARE_SHORTLINK_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = HASHTAG_RE.sub(lambda m: " " + _split_camel_case(m.group(1)) + " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_enough_content(cleaned_text, min_words=MIN_WORDS_AFTER_CLEAN):
    """True if cleaned_text has >= min_words real alphabetic word-tokens (2+ letters). Used to
    drop near-empty texts (pure URLs/mentions/hashtags) from the BERTopic fit."""
    return len(_ALPHA_WORD_RE.findall(cleaned_text)) >= min_words


def build_multiword_label(topic_words, top_n_words=3):
    """Builds a human-readable multi-word topic label from BERTopic's ranked representation
    words/phrases (e.g. `topic_model.get_topic(topic_id)` -> `[(word_or_phrase, score), ...]`,
    already sorted best-first).

    Why this exists (not just `" ".join(w for w, _ in topic_words[:top_n_words])`): when
    `representation_model` returns overlapping n-gram phrases that share a word (e.g. a
    MaximalMarginalRelevance representation returning "gaza ceasefire" then "gaza humanitarian"
    for the same topic), naively joining the top-N raw phrases produces a repetitive, less
    readable label like "gaza ceasefire gaza humanitarian". Instead, this splits each ranked
    phrase into individual word tokens and keeps only each token's FIRST occurrence
    (case-insensitive) across the ranked list, stopping once `top_n_words` unique tokens have
    been collected - e.g. the same input instead yields "gaza ceasefire humanitarian".

    Returns "" if `topic_words` is empty/None (caller decides the fallback, e.g. "לא זוהה")."""
    if not topic_words:
        return ""
    seen = set()
    unique_tokens = []
    for phrase, _ in topic_words:
        if not phrase:
            continue
        for token in str(phrase).split():
            key = token.lower()
            if key in seen:
                continue
            seen.add(key)
            unique_tokens.append(token)
            if len(unique_tokens) >= top_n_words:
                break
        if len(unique_tokens) >= top_n_words:
            break
    return " ".join(unique_tokens)

"""Style/formatting-only text normalization - Section 28 intervention experiment.

Context: EXPERIMENTS.md Section 27 showed that author identity is strongly recoverable from
purely stylistic/formatting features (URL/mention/hashtag usage, punctuation habits, whitespace
habits, word-elongation, etc.) even WITHIN a single fixed narrative. This module implements the
causal intervention: a deterministic, author-blind text transform that neutralizes ONLY
stylistic/technical/formatting signal, while explicitly preserving semantic content.

What this function DOES:
  - Replaces URLs (both scheme-prefixed and known bare link-shorteners) with the literal
    placeholder "[URL]".
  - Replaces @mentions with the literal placeholder "[USER]".
  - Strips the '#' marker from hashtags and splits camelCase so the underlying words survive
    as ordinary text (e.g. "#StandWithUkraine" -> "Stand With Ukraine") - this neutralizes the
    "I use hashtags" formatting habit while keeping the semantic words (which may be real
    entities/topics) fully intact.
  - Removes emoji / pictographic symbols (pure decoration, carries no semantic word content).
  - Collapses repeated punctuation runs ("!!!", "???", ".....") to a single canonical form.
  - Collapses word-elongation (3+ repeated letters, e.g. "soooo") down to 2 repeats.
  - Collapses excessive whitespace/newlines down to single spaces.

What this function explicitly does NOT do (by design, per the experiment's scope):
  - Does NOT remove or alter named entities (people/places/organizations are untouched -
    only the '#'/@ /URL wrapper around tokens is affected, never the words themselves).
  - Does NOT paraphrase or change semantic wording in any way.
  - Does NOT use author identity/source anywhere in the transform (pure function of the text).
  - Does NOT truncate or otherwise normalize text length (explicitly out of scope for this
    first intervention - see EXPERIMENTS.md Section 28 for why truncation is deferred).

Reuses the same URL/mention/hashtag regexes and camelCase splitter already established and
validated in `topic_preprocessing.py` (BERTopic's own text-cleaning module) for consistency -
only the substitution behavior differs (placeholders here, vs. full removal there).
"""
import re

from narrative_lens.topic_modeling.topic_preprocessing import (
    BARE_SHORTLINK_RE,
    HASHTAG_RE,
    MENTION_RE,
    URL_RE,
    _split_camel_case,
)

# Common emoji / pictographic / symbol blocks (decoration only, no semantic word content).
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # misc symbols & pictographs, emoticons, transport, supplemental
    "\U00002600-\U000027BF"  # misc symbols, dingbats
    "\U0001F1E6-\U0001F1FF"  # regional indicator symbols (flag letters)
    "\U00002190-\U000021FF"  # arrows
    "\U0000FE0F"             # variation selector-16
    "\U0000200D"             # zero-width joiner
    "]+"
)

REPEATED_EXCLAIM_RE = re.compile(r"!{2,}")
REPEATED_QUESTION_RE = re.compile(r"\?{2,}")
REPEATED_DOTS_RE = re.compile(r"\.{2,}")
# 3+ repeated letters (word elongation, e.g. "soooo") -> collapse to 2 ("soo"). Restricted to
# ASCII letters only so digits/punctuation runs (already handled above) are left alone.
REPEATED_LETTER_RE = re.compile(r"([A-Za-z])\1{2,}")
WHITESPACE_RE = re.compile(r"\s+")


def _hashtag_sub(match):
    return _split_camel_case(match.group(1))


def normalize_style(text):
    """Applies the full style/formatting-only normalization pipeline to a single text.
    Deterministic, stateless, uses nothing about the text's author/source. Safe to call on
    already-normalized text (idempotent in practice - no step re-introduces a pattern that an
    earlier step would match)."""
    if not isinstance(text, str) or not text:
        return text

    t = text
    t = BARE_SHORTLINK_RE.sub("[URL]", t)
    t = URL_RE.sub("[URL]", t)
    t = MENTION_RE.sub("[USER]", t)
    t = HASHTAG_RE.sub(_hashtag_sub, t)
    t = EMOJI_RE.sub("", t)
    t = REPEATED_EXCLAIM_RE.sub("!", t)
    t = REPEATED_QUESTION_RE.sub("?", t)
    t = REPEATED_DOTS_RE.sub("...", t)
    t = REPEATED_LETTER_RE.sub(r"\1\1", t)
    t = WHITESPACE_RE.sub(" ", t).strip()
    return t

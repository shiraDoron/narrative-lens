"""
Verifies that the SAME text-cleaning is used for BERTopic training (train_topics.py) and for
inference (stance.py's TopicAnalysisPipeline), and that the pinned legacy model's behavior is
completely unaffected by this change.

Checks performed:
1. Direct function-level check: `topic_preprocessing.clean_text_for_topic_model()` (the exact
   function train_topics.py calls before BERTopic.fit()) produces the expected cleaned text for
   texts containing a URL, an @mention, and a #hashtag.
2. Inference-side consistency: TopicAnalysisPipeline(model_path=TOPIC_MODEL_PATH_SOFT) internally
   applies the SAME clean_text_for_topic_model() before scoring. We verify this by feeding (a) the
   raw text and (b) the already-cleaned text (clean_text_for_topic_model applied once by us) into
   the pipeline - since the cleaning is idempotent (re-cleaning already-clean text is a no-op), both
   must produce IDENTICAL topic_id + topic_distribution results. If (a) and (b) ever diverged, it
   would mean the pipeline's internal cleaning is NOT equivalent to the shared function.
3. Legacy-model safety: TopicAnalysisPipeline() (default, TOPIC_MODEL_PATH_LEGACY) must have
   use_cleaned_preprocessing == False, and must return the EXACT SAME topic_id for a fixed sample
   sentence as it did before this change was made (regression check against a hardcoded known-good
   value recorded in an earlier session).

Run: `python src/verify_preprocessing_consistency.py` from repo root.
"""

import sys

from config import TOPIC_MODEL_PATH_LEGACY, TOPIC_MODEL_PATH_SOFT
from stance import TopicAnalysisPipeline
from topic_preprocessing import clean_text_for_topic_model

SAMPLE_TEXTS = [
    "Saudi Arabia sovereignty stuff  🔴 @DDGeopolitics | Socials | Donate | Advertising",
    "Good morning! Have a productive week and #StandWithUkraine   : 47th Artillery Brigade",
    "Read more: https://t.co/xervJmjQL8 and also check @SomeHandle for #BreakingNews updates",
]

# Recorded in an earlier session against models/saved_topic_model (legacy) BEFORE this change -
# must stay exactly this value, proving the legacy model's assignment is unaffected.
LEGACY_REGRESSION_TEXT = "Russia launched missile strikes on Ukrainian energy infrastructure."
LEGACY_REGRESSION_EXPECTED_TOPIC_ID = 347


def check_clean_function():
    print("=== 1. clean_text_for_topic_model() sanity ===")
    ok = True
    for text in SAMPLE_TEXTS:
        cleaned = clean_text_for_topic_model(text)
        has_url = "http" in cleaned
        has_mention = "@" in cleaned
        has_hashtag = "#" in cleaned
        status = "OK" if not (has_url or has_mention or has_hashtag) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"[{status}] {text!r}\n      -> {cleaned!r}")
    return ok


def check_inference_consistency():
    print("\n=== 2. Train/inference preprocessing consistency (soft_v2 model) ===")
    pipeline = TopicAnalysisPipeline(model_path=TOPIC_MODEL_PATH_SOFT)
    assert pipeline.use_cleaned_preprocessing is True, (
        "Expected use_cleaned_preprocessing=True for the soft_v2 model path"
    )
    ok = True
    for text in SAMPLE_TEXTS:
        pre_cleaned = clean_text_for_topic_model(text)
        result_raw = pipeline.process_text_with_distribution(text)
        result_pre_cleaned = pipeline.process_text_with_distribution(pre_cleaned)
        same_topic = result_raw["topic_id"] == result_pre_cleaned["topic_id"]
        same_distribution = result_raw["topic_distribution"] == result_pre_cleaned["topic_distribution"]
        status = "OK" if (same_topic and same_distribution) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"[{status}] {text!r}")
        print(f"      raw           -> topic_id={result_raw['topic_id']}, "
              f"dist={result_raw['topic_distribution']}")
        print(f"      pre-cleaned   -> topic_id={result_pre_cleaned['topic_id']}, "
              f"dist={result_pre_cleaned['topic_distribution']}")
    return ok


def check_legacy_unaffected():
    print("\n=== 3. Legacy model (saved_topic_model) unaffected ===")
    pipeline = TopicAnalysisPipeline()  # default = TOPIC_MODEL_PATH_LEGACY
    assert pipeline.model_path == TOPIC_MODEL_PATH_LEGACY
    ok = True
    if pipeline.use_cleaned_preprocessing is not False:
        print("[FAIL] use_cleaned_preprocessing should be False for the legacy model path")
        ok = False
    else:
        print("[OK] use_cleaned_preprocessing == False for the legacy model path")

    topic_id = pipeline.process_text(LEGACY_REGRESSION_TEXT)
    status = "OK" if topic_id == LEGACY_REGRESSION_EXPECTED_TOPIC_ID else "FAIL"
    if status == "FAIL":
        ok = False
    print(f"[{status}] legacy topic_id for regression sentence = {topic_id} "
          f"(expected {LEGACY_REGRESSION_EXPECTED_TOPIC_ID})")
    return ok


def main():
    results = {
        "clean_function": check_clean_function(),
        "inference_consistency": check_inference_consistency(),
        "legacy_unaffected": check_legacy_unaffected(),
    }
    print("\n=== SUMMARY ===")
    all_ok = True
    for name, ok in results.items():
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        all_ok = all_ok and ok
    if not all_ok:
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()

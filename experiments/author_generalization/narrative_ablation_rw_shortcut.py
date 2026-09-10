"""
Right-wing "Shortcut" Forensic Analysis (follow-up to narrative_ablation_loao.py)
==================================================================================
For the two held-out authors that showed severe misrouting to "Right-wing" in
EXPERIMENTS.md section 18 (MariaZakharova, BernieSanders), this script asks: WHY does the
classifier route their unseen content to "Right-wing"? It compares the entities/words/hard-topic
ids that appear in each author's test rows that got MISCLASSIFIED as Right-wing against the
entities/words/hard-topic ids that appear in Right-wing's OWN training examples - if there is
heavy overlap, that is evidence the model latched onto a superficial lexical/entity "shortcut"
(spurious cue correlated with Right-wing in training) rather than genuine narrative content.

Variant used for identifying "misclassified as Right-wing" rows: 'sbert_all_engineered'
(SBERT + NER + SRL + Emotion + Hard-Topic + Reliability) - the closest ablation variant to the
production fusion.HybridNarrativeDetector's engineered-feature set, so the forensic finding is
most relevant to the model actually used in this project. Its checkpoint was already trained
and saved by narrative_ablation_loao.py - this script only loads it for inference, it does not
retrain anything.

Reuses (unmodified, read-only): train.load_raw_data/split_leave_one_author/evaluate,
narrative_ablation_loao.build_or_load_cache/AblationDetector/VARIANTS/CHECKPOINT_DIR/
RIGHT_WING_IDX, ner.EntityAnalysisPipeline, analyze_agendas.clean_text/tokenize (word-frequency
convention already established for this project's agenda analysis).

Run (from repo root, after all 3 narrative_ablation_loao.py --author runs have completed):
    python experiments/author_generalization/narrative_ablation_rw_shortcut.py
"""
import json
import os
import sys
from collections import Counter

import torch
from bertopic import BERTopic

# narrative_topic_compare.py is a sibling experiment script (not part of the installable
# narrative_lens package) living in experiments/feature_ablation/ - add just that folder to
# sys.path. Everything else below is imported from the installed `narrative_lens` package
# (pip install -e ., see pyproject.toml) instead of a sys.path hack.
_SIBLING_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "feature_ablation"))
if _SIBLING_DIR not in sys.path:
    sys.path.insert(0, _SIBLING_DIR)

from narrative_lens.train import load_raw_data, split_leave_one_author, evaluate
from narrative_ablation_loao import (
    build_or_load_cache, AblationDetector, VARIANTS, CHECKPOINT_DIR, RIGHT_WING_IDX,
)
from narrative_topic_compare import BERTOPIC_MODEL_PATH, BERTOPIC_EMBEDDING_MODEL_NAME
from narrative_lens.features.ner import EntityAnalysisPipeline
from narrative_lens.features.analyze_agendas import clean_text, tokenize

AUTHORS_TO_ANALYZE = ("MariaZakharova", "BernieSanders")
VARIANT_NAME = "sbert_all_engineered"
RW_TRAIN_SAMPLE_SIZE = 500  # cap on Right-wing's own training examples used as the reference set
TOP_K = 25

REPORT_DIR = "reports/results/narrative_ablation_loao"
OUT_FILE = os.path.join(REPORT_DIR, "rw_shortcut_forensic.json")


def get_variant_predictions(author):
    """Loads the already-trained 'sbert_all_engineered' checkpoint for `author` and returns
    (test_texts, test_true, test_pred) - test rows aligned by position with the raw
    train/val/test split (same split_leave_one_author(df, author), same random_state=42)."""
    cache = build_or_load_cache(author)
    meta = cache["_meta"]
    arms = VARIANTS[VARIANT_NAME]
    detector = AblationDetector(
        arms, meta["ner_vocab_size"], meta["srl_vocab_size"], meta["bertopic_vec_size"], meta["sbert_dim"],
    )
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{VARIANT_NAME}_{author}.pth")
    if not os.path.exists(checkpoint_file):
        raise FileNotFoundError(
            f"'{checkpoint_file}' not found - run narrative_ablation_loao.py --author {author} first."
        )
    detector.load_state_dict(torch.load(checkpoint_file))

    _, _, test_true, test_pred = evaluate(detector, cache["test"])

    df = load_raw_data()
    _, _, test_data = split_leave_one_author(df, author)
    test_texts = test_data["text"].astype(str).str.slice(0, 3000).tolist()
    assert len(test_texts) == len(test_true), f"length mismatch for author={author}"
    return test_texts, test_true, test_pred, cache


def collect_misclassified_as_rw(author):
    """Returns list of raw text for this author's test rows where the model predicted
    Right-wing but the true narrative was something else."""
    test_texts, test_true, test_pred, _ = get_variant_predictions(author)
    misclassified = [
        text for text, true_idx, pred_idx in zip(test_texts, test_true, test_pred)
        if pred_idx == RIGHT_WING_IDX and true_idx != RIGHT_WING_IDX
    ]
    return misclassified


def collect_right_wing_training_sample(reference_author="MariaZakharova"):
    """Right-wing's own training examples (any of the 3 authors' train splits works - none of
    IDF/MariaZakharova/BernieSanders' own narrative is 'Right-wing', so the Right-wing rows in
    every train split are effectively the same underlying data)."""
    df = load_raw_data()
    train_data, _, _ = split_leave_one_author(df, reference_author)
    rw_rows = train_data[train_data["narrative_name"] == "Right-wing"]
    texts = rw_rows["text"].astype(str).str.slice(0, 3000).tolist()
    if len(texts) > RW_TRAIN_SAMPLE_SIZE:
        texts = texts[:RW_TRAIN_SAMPLE_SIZE]
    return texts


def entity_counts(entity_pipeline, texts):
    counter = Counter()
    for text in texts:
        for ent in entity_pipeline.extract_raw_entities(text):
            name = ent["text"].strip().lower()
            if name:
                counter[name] += 1
    return counter


def word_counts(texts):
    counter = Counter()
    for text in texts:
        counter.update(tokenize(clean_text(text)))
    return counter


def hard_topic_counts(texts, bertopic_model):
    from narrative_lens.topic_modeling.topic_preprocessing import clean_text_for_topic_model
    cleaned = [clean_text_for_topic_model(t) for t in texts]
    safe = [t if t.strip() else "empty" for t in cleaned]
    hard_topics, _ = bertopic_model.transform(safe)
    return Counter(int(t) for t in hard_topics)


def top_overlap(counter_a, counter_b, top_k=TOP_K):
    """Returns the items among counter_a's top_k most common that also appear in counter_b,
    with both counts, sorted by counter_a's frequency descending."""
    top_a = [item for item, _ in counter_a.most_common(top_k)]
    overlap = [(item, counter_a[item], counter_b.get(item, 0)) for item in top_a if item in counter_b]
    return overlap


def topic_words_label(bertopic_model, topic_id, top_n=5):
    words = bertopic_model.get_topic(topic_id)
    if not words:
        return ""
    return ", ".join(w for w, _ in words[:top_n])


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    print("Loading BERTopic model for hard-topic-id lookups...")
    bertopic_model = BERTopic.load(BERTOPIC_MODEL_PATH, embedding_model=BERTOPIC_EMBEDDING_MODEL_NAME)

    print("Loading NER pipeline (dslim/bert-base-NER)...")
    entity_pipeline = EntityAnalysisPipeline()

    print("Collecting Right-wing's own training examples (reference set)...")
    rw_train_texts = collect_right_wing_training_sample()
    print(f"  -> {len(rw_train_texts)} Right-wing training examples.")
    rw_entities = entity_counts(entity_pipeline, rw_train_texts)
    rw_words = word_counts(rw_train_texts)
    rw_topics = hard_topic_counts(rw_train_texts, bertopic_model)

    results = {}
    for author in AUTHORS_TO_ANALYZE:
        print(f"\n=== Author '{author}' ===")
        misclassified_texts = collect_misclassified_as_rw(author)
        print(f"  -> {len(misclassified_texts)} test rows misclassified as Right-wing "
              f"(variant='{VARIANT_NAME}').")
        if not misclassified_texts:
            results[author] = {"n_misclassified_as_right_wing": 0}
            continue

        mis_entities = entity_counts(entity_pipeline, misclassified_texts)
        mis_words = word_counts(misclassified_texts)
        mis_topics = hard_topic_counts(misclassified_texts, bertopic_model)

        entity_overlap = top_overlap(mis_entities, rw_entities)
        word_overlap = top_overlap(mis_words, rw_words)
        topic_overlap = top_overlap(mis_topics, rw_topics)

        print(f"  Top overlapping entities (misclassified count / Right-wing-training count): "
              f"{entity_overlap[:10]}")
        print(f"  Top overlapping words: {word_overlap[:10]}")
        print(f"  Top overlapping hard-topic ids: "
              f"{[(t, topic_words_label(bertopic_model, t), c1, c2) for t, c1, c2 in topic_overlap[:5]]}")

        results[author] = {
            "n_misclassified_as_right_wing": len(misclassified_texts),
            "top_entities_misclassified": mis_entities.most_common(TOP_K),
            "top_words_misclassified": mis_words.most_common(TOP_K),
            "top_hard_topics_misclassified": mis_topics.most_common(TOP_K),
            "entity_overlap_with_rw_training": entity_overlap,
            "word_overlap_with_rw_training": word_overlap,
            "hard_topic_overlap_with_rw_training": [
                (t, topic_words_label(bertopic_model, t), c1, c2) for t, c1, c2 in topic_overlap
            ],
        }

    results["_right_wing_training_reference"] = {
        "n_examples": len(rw_train_texts),
        "top_entities": rw_entities.most_common(TOP_K),
        "top_words": rw_words.most_common(TOP_K),
        "top_hard_topics": [(t, topic_words_label(bertopic_model, t), c) for t, c in rw_topics.most_common(TOP_K)],
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved forensic analysis to '{OUT_FILE}'.")


if __name__ == "__main__":
    main()

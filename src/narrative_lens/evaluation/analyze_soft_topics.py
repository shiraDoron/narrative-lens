"""
Small demo/analysis script for the new soft (multi-topic) BERTopic scoring added to
`TopicAnalysisPipeline` in stance.py (see `get_topic_distribution`/
`process_text_with_distribution`).

Does NOT touch the classification pipeline (fusion.py/train.py) or the hard `topic_id`
logic used there - this is a read-only inspection tool over a handful of example texts,
showing for each: the dominant (hard) topic, the top-N soft topics with their normalized
scores, and a human-readable label per topic (LLM-refined label if available, else the
raw BERTopic top word).

Requires the loaded BERTopic model to have been saved with `save_ctfidf=True` (see
train_topics.py) - otherwise `approximate_distribution()` raises NotFittedError and
topic_distribution will be empty for every example (dominant topic_id still works either
way, since it only needs `.transform()`). By default this script loads
`config.TOPIC_MODEL_PATH_SOFT` (`models/saved_topic_model_soft_v2`) - the separate,
versioned re-fit that supports soft/multi-topic scoring - NOT the pinned legacy
`models/saved_topic_model` that the existing classification checkpoints depend on.
Use `--model-path` to point at a different saved model.

Run (from repo root): `python -m narrative_lens.evaluation.analyze_soft_topics --n-examples 10`
"""
import argparse
import os

import pandas as pd

from narrative_lens.config import TOPIC_MODEL_PATH_SOFT
from narrative_lens.topic_modeling.stance import TopicAnalysisPipeline

RAW_DATASETS = [
    "data/raw/twitter_natural_dataset.csv",
    "data/raw/telegram_natural_dataset.csv",
    "data/raw/gemini_natural_dataset.csv",
    "data/raw/gpt_natural_dataset.csv",
]

REPORT_DIR = "reports/results/profiler_prototype"


def load_example_texts(n_examples=10, seed=42):
    """Loads all 4 natural datasets and samples n_examples texts across all narratives
    (not stratified per-narrative - this is just a quick illustrative demo, not a
    calibration sample)."""
    frames = []
    for path in RAW_DATASETS:
        if os.path.exists(path):
            df = pd.read_csv(path)
            frames.append(df[["text", "narrative_name"]])
        else:
            print(f"WARNING: dataset not found, skipping: {path}")

    full = pd.concat(frames, ignore_index=True).dropna(subset=["text", "narrative_name"])
    sample = full.sample(n=min(n_examples, len(full)), random_state=seed).reset_index(drop=True)
    return sample


def analyze(n_examples=10, top_n=3, model_path=TOPIC_MODEL_PATH_SOFT,
            out_csv=os.path.join(REPORT_DIR, "soft_topic_examples.csv")):
    examples = load_example_texts(n_examples=n_examples)

    pipeline = TopicAnalysisPipeline(model_path=model_path)

    rows = []
    print(f"\n--- Soft topic distribution demo ({len(examples)} example texts) ---\n")
    for _, row in examples.iterrows():
        text = row["text"]
        narrative = row["narrative_name"]

        result = pipeline.process_text_with_distribution(text, top_n=top_n)
        dominant_id = result["topic_id"]
        dominant_label = pipeline.get_topic_label(dominant_id)
        distribution = result["topic_distribution"]

        print(f"Narrative: {narrative}")
        print(f"Text: {text[:200]}{'...' if len(text) > 200 else ''}")
        print(f"Dominant topic (hard, backward-compatible): {dominant_id} - \"{dominant_label}\"")
        if distribution:
            print(f"Top {top_n} soft topics:")
            for item in distribution:
                print(f"  - topic_{item['topic_id']} (\"{item['label']}\"): {item['score']:.2f}")
        else:
            print("  (no soft topic distribution available - see NotFittedError note "
                  "in the module docstring if this is unexpected)")
        print()

        rows.append({
            "narrative_name": narrative,
            "text": text,
            "dominant_topic_id": dominant_id,
            "dominant_topic_label": dominant_label,
            "soft_topic_distribution": "; ".join(
                f"topic_{item['topic_id']} ({item['label']}): {item['score']:.2f}"
                for item in distribution
            ) if distribution else "(none)",
        })

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    pd.DataFrame(rows).to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"Saved {len(rows)} rows to {out_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-examples", type=int, default=10,
                        help="Number of example texts to sample and analyze (default 10).")
    parser.add_argument("--top-n", type=int, default=3,
                        help="Number of top soft topics to show per text (default 3).")
    parser.add_argument("--model-path", type=str, default=TOPIC_MODEL_PATH_SOFT,
                        help=f"Path to a saved BERTopic model (default: {TOPIC_MODEL_PATH_SOFT}, "
                             f"the soft-clustering-capable version).")
    args = parser.parse_args()

    analyze(n_examples=args.n_examples, top_n=args.top_n, model_path=args.model_path)

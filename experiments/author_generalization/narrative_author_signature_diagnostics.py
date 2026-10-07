"""
Narrative Classification — Author Signature Diagnostics (Decision Tree, direct author-ID test)
================================================================================================
Follow-up to narrative_unseen_author_error_diagnostics.py / narrative_unseen_author_domain_
shift_diagnostics.py (EXPERIMENTS.md Section 26, both closed as negative results: neither could
predict WHICH test examples a LOAO model would get wrong). This script asks a more direct
question instead of trying to predict errors: **does the text itself carry an author-specific
style/content signature at all**, independent of any trained narrative classifier? If a shallow,
interpretable Decision Tree can recover author identity from textual features alone - especially
within a single fixed narrative - that is direct evidence that author-specific signal exists in
the feature space the real classifiers consume, which could explain unseen-author degradation
even though Section 26 could not pin down *which* examples it affects.

IMPORTANT — this is a different question from Experiments 25/26 and does NOT use their
exclusion list: IDF/MariaZakharova/BernieSanders were only excluded there because THOSE
experiments tested narrative-classifier generalization (a held-out author must never have been
used to pick a policy). This script never trains or touches a narrative classifier, so all 3 are
included as ordinary real authors here.

Target: `author` (author_source). NEVER used as a feature - only textual/engineered features
below, none of which encode author/source/platform identity directly.

Features (none are author identity/metadata):
  Style/lexical (regex + analyze_agendas.tokenize, cheap, no model inference):
    text_length, word_count, sentence_count, avg_sentence_length, punctuation_rate,
    exclamation_rate, question_rate, uppercase_ratio, hashtag_count, mention_count, url_count,
    avg_word_length, stopword_rate, type_token_ratio, unique_token_count.
  Entity counts/types (reused from the corpus-wide raw-entities cache built in Experiment 24 -
    data/cache/cached_raw_entities_by_text.pt - no new NER inference):
    entity_count_total, entity_count_PER, entity_count_ORG, entity_count_LOC,
    entity_count_MISC, entity_density.
  Topic (BERTopic Soft Topic Distribution, same model as Experiments 18-26 -
    models/experiments/soft_v2_baseline_seeded):
    soft_topic_max_prob, soft_topic_entropy.
  Semantic representation (frozen SBERT sentence-transformers/all-MiniLM-L6-v2 embedding,
    reduced via PCA fit on this script's own dataset - unsupervised, no author label used in the
    fit - top 5 components only, so a shallow tree can use it):
    sbert_pca_1 .. sbert_pca_5.

Eligible authors: real (non-synthetic) authors with >=100 examples (MIN_EXAMPLES_PER_AUTHOR) -
same order of magnitude as Experiment 25's own threshold, gives every included narrative
multiple (5-9) authors with ~100-400 examples each - enough for a meaningful per-narrative
multi-class CV.

### Experiment A — global author prediction (all narratives pooled)
Decision Tree predicts `author` from the features above, across ALL eligible authors/narratives
pooled together. Compared against a majority-author baseline and a random/chance baseline
(1/n_authors). NOTE: in this pooled setting, narrative itself is informative about author (most
authors write in only one narrative) even though narrative is never used as a feature directly -
some of the engineered features (soft-topic, entities) are themselves correlated with narrative/
topic. This makes Experiment A, on its own, a WEAK test of "author style" specifically (success
here could just mean "the features can tell narratives/topics apart, and authors are a proxy for
that"). Experiment B below is the stronger, decisive test.

### Experiment B — within-narrative author prediction (the decisive test)
Same Decision Tree / same features, but run SEPARATELY within each narrative that has >= 2
eligible authors (narrative is therefore held perfectly constant). If a Decision Tree can still
recover author identity here, success cannot be explained by narrative/topic acting as a proxy -
this is the direct evidence the user asked for.

### Methodology (both experiments)
- Evaluation is ALWAYS on held-out texts: StratifiedKFold (5-fold, shuffled, seed=42) with
  cross_val_predict to obtain genuine out-of-fold predictions for every example; accuracy/
  macro-F1/confusion matrix are computed from these out-of-fold predictions, NEVER from a
  model's own training-set accuracy.
- Tried at several max_depth values (Experiment A: 5/10/15/unlimited, since ~47 classes need more
  splits than a 3-5 deep tree can offer; Experiment B: 3/4/5, kept small/interpretable since each
  narrative only has 5-9 classes). The depth with the best out-of-fold macro-F1 is then re-fit on
  ALL data (standard practice) purely for interpretation (feature importance / tree rules) - that
  full-data fit's own accuracy is NOT reported as a generalization metric anywhere.
- No further feature engineering is attempted if results are negative (one pass, as agreed).

Run (from repo root):
    python experiments/author_generalization/narrative_author_signature_diagnostics.py
"""
import json
import os
import re
import string

import numpy as np
import pandas as pd
import torch
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
import matplotlib.pyplot as plt

from narrative_lens.train import load_raw_data, is_synthetic_author
from narrative_lens.features.analyze_agendas import tokenize, STOPWORDS
from narrative_lens.topic_modeling.topic_preprocessing import clean_text_for_topic_model

RAW_ENTITIES_CACHE_FILE = "data/cache/cached_raw_entities_by_text.pt"
BERTOPIC_MODEL_PATH = "models/experiments/soft_v2_baseline_seeded"
BERTOPIC_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SOFT_TOP_N = 5

MIN_EXAMPLES_PER_AUTHOR = 100
SEED = 42
N_PCA_COMPONENTS = 5

REPORT_DIR = "artifacts/experiments/narrative_author_signature_diagnostics"
DATASET_FILE = os.path.join(REPORT_DIR, "diagnostic_dataset.csv")
SUMMARY_FILE = os.path.join(REPORT_DIR, "summary.json")

STYLE_FEATURES = [
    "text_length", "word_count", "sentence_count", "avg_sentence_length", "punctuation_rate",
    "exclamation_rate", "question_rate", "uppercase_ratio", "hashtag_count", "mention_count",
    "url_count", "avg_word_length", "stopword_rate", "type_token_ratio", "unique_token_count",
]
ENTITY_FEATURES = [
    "entity_count_total", "entity_count_PER", "entity_count_ORG", "entity_count_LOC",
    "entity_count_MISC", "entity_density",
]
TOPIC_FEATURES = ["soft_topic_max_prob", "soft_topic_entropy"]
SEMANTIC_FEATURES = [f"sbert_pca_{i + 1}" for i in range(N_PCA_COMPONENTS)]
ALL_FEATURES = STYLE_FEATURES + ENTITY_FEATURES + TOPIC_FEATURES + SEMANTIC_FEATURES

PUNCT_SET = set(string.punctuation)
WORD_SPLIT_RE = re.compile(r"\b\w+\b")


def style_lexical_features(text):
    words = WORD_SPLIT_RE.findall(text)
    n_words = len(words) if words else 1
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    n_sentences = len(sentences) if sentences else 1
    letters = [c for c in text if c.isalpha()]
    content_tokens = tokenize(text)
    stopword_hits = sum(1 for w in words if w.lower() in STOPWORDS)
    return {
        "text_length": len(text),
        "word_count": len(words),
        "sentence_count": n_sentences,
        "avg_sentence_length": len(words) / n_sentences,
        "punctuation_rate": (sum(1 for c in text if c in PUNCT_SET) / len(text)) if text else 0.0,
        "exclamation_rate": (text.count("!") / len(text)) if text else 0.0,
        "question_rate": (text.count("?") / len(text)) if text else 0.0,
        "uppercase_ratio": (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0.0,
        "hashtag_count": len(re.findall(r"#\w+", text)),
        "mention_count": len(re.findall(r"@\w+", text)),
        "url_count": len(re.findall(r"https?://\S+|www\.\S+", text)),
        "avg_word_length": (sum(len(w) for w in words) / n_words),
        "stopword_rate": (stopword_hits / n_words),
        "type_token_ratio": (len(set(content_tokens)) / len(content_tokens)) if content_tokens else 0.0,
        "unique_token_count": len(set(content_tokens)),
    }


def entity_count_features(text, raw_entities_by_text, word_count):
    entities = raw_entities_by_text.get(text) or []
    by_type = {"PER": 0, "ORG": 0, "LOC": 0, "MISC": 0}
    for e in entities:
        group = e.get("entity_group")
        if group in by_type:
            by_type[group] += 1
    total = len(entities)
    return {
        "entity_count_total": total,
        "entity_count_PER": by_type["PER"],
        "entity_count_ORG": by_type["ORG"],
        "entity_count_LOC": by_type["LOC"],
        "entity_count_MISC": by_type["MISC"],
        "entity_density": total / max(word_count, 1),
    }


def build_or_load_raw_entities_cache():
    if not os.path.exists(RAW_ENTITIES_CACHE_FILE):
        raise FileNotFoundError(
            f"'{RAW_ENTITIES_CACHE_FILE}' not found - expected it to already exist from "
            f"Experiment 24 (corpus-wide, author-independent raw-entities cache)."
        )
    print(f"Loading existing raw-entities cache '{RAW_ENTITIES_CACHE_FILE}'...")
    return torch.load(RAW_ENTITIES_CACHE_FILE, weights_only=False)["raw_entities_by_text"]


def soft_topic_summary_features(texts, bertopic_model, num_bertopic_topics):
    """Returns (max_prob, entropy) per text from BERTopic's re-normalized top-5
    approximate_distribution() - same construction as Experiments 18-26, just summarized to 2
    scalars instead of kept as a dense per-topic vector (so a shallow tree can use it)."""
    cleaned_texts = [clean_text_for_topic_model(t) for t in texts]
    safe_texts = [t if t.strip() else "empty" for t in cleaned_texts]

    print(f"  Running BERTopic .approximate_distribution() on {len(safe_texts)} texts...")
    soft_dists, _ = bertopic_model.approximate_distribution(safe_texts)

    max_probs, entropies = [], []
    for scores in soft_dists:
        nonzero = [s for s in scores if s > 0]
        if not nonzero:
            max_probs.append(0.0)
            entropies.append(0.0)
            continue
        nonzero.sort(reverse=True)
        top = nonzero[:SOFT_TOP_N]
        total = sum(top)
        probs = [s / total for s in top] if total > 0 else top
        max_probs.append(max(probs))
        entropies.append(float(-sum(p * np.log(p) for p in probs if p > 0)))
    return max_probs, entropies


def build_dataset():
    if os.path.exists(DATASET_FILE):
        print(f"Found existing diagnostic dataset '{DATASET_FILE}'. Loading (skipping feature "
              f"extraction)...")
        return pd.read_csv(DATASET_FILE)

    df = load_raw_data()
    df = df[~df["author_source"].apply(is_synthetic_author)].copy()
    df["text"] = df["text"].astype(str).str.slice(0, 3000)

    counts = df["author_source"].value_counts()
    eligible_authors = counts[counts >= MIN_EXAMPLES_PER_AUTHOR].index.tolist()
    df = df[df["author_source"].isin(eligible_authors)].reset_index(drop=True)
    print(f"{len(eligible_authors)} real authors with >= {MIN_EXAMPLES_PER_AUTHOR} examples "
          f"-> {len(df)} total rows.")

    texts = df["text"].tolist()

    print("Computing style/lexical features...")
    style_rows = [style_lexical_features(t) for t in texts]

    print("Loading raw-entities cache + computing entity-count features...")
    raw_entities_by_text = build_or_load_raw_entities_cache()
    entity_rows = [entity_count_features(t, raw_entities_by_text, s["word_count"])
                   for t, s in zip(texts, style_rows)]

    print("Loading SBERT model + encoding texts (for PCA-reduced semantic features)...")
    sbert_model = SentenceTransformer(BERTOPIC_EMBEDDING_MODEL_NAME)
    embeddings = sbert_model.encode(texts, show_progress_bar=True, batch_size=64)
    pca = PCA(n_components=N_PCA_COMPONENTS, random_state=SEED)
    pca_components = pca.fit_transform(embeddings)
    print(f"  PCA explained variance ratio (top {N_PCA_COMPONENTS}): "
          f"{np.round(pca.explained_variance_ratio_, 3)}")

    print("Loading BERTopic model + computing soft-topic summary features...")
    bertopic_model = BERTopic.load(BERTOPIC_MODEL_PATH, embedding_model=BERTOPIC_EMBEDDING_MODEL_NAME)
    num_bertopic_topics = len([t for t in bertopic_model.get_topics().keys() if t != -1])
    max_probs, entropies = soft_topic_summary_features(texts, bertopic_model, num_bertopic_topics)

    dataset = pd.DataFrame(style_rows)
    entity_df = pd.DataFrame(entity_rows)
    dataset = pd.concat([dataset, entity_df], axis=1)
    dataset["soft_topic_max_prob"] = max_probs
    dataset["soft_topic_entropy"] = entropies
    for i in range(N_PCA_COMPONENTS):
        dataset[f"sbert_pca_{i + 1}"] = pca_components[:, i]
    dataset["author"] = df["author_source"].values
    dataset["narrative_name"] = df["narrative_name"].values

    os.makedirs(REPORT_DIR, exist_ok=True)
    dataset.to_csv(DATASET_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved diagnostic dataset ({len(dataset)} rows, {len(eligible_authors)} authors) to "
          f"'{DATASET_FILE}'.")
    return dataset


def run_cv_experiment(dataset, feature_cols, depths, report_prefix, scope_label):
    X = dataset[feature_cols].fillna(0.0)
    y = dataset["author"].astype(str)
    n_classes = y.nunique()
    n_examples = len(dataset)

    majority_baseline = y.value_counts().iloc[0] / n_examples
    chance_baseline = 1.0 / n_classes
    print(f"\n=== Experiment [{scope_label}] - n_authors={n_classes}, n_examples={n_examples} ===")
    print(f"Majority-author baseline: {majority_baseline * 100:.1f}% | "
          f"Random/chance baseline: {chance_baseline * 100:.1f}%")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    depth_results = {}
    best_depth, best_macro_f1, best_oof_pred = None, -1.0, None
    for depth in depths:
        clf = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=25,
                                      class_weight="balanced", random_state=SEED)
        oof_pred = cross_val_predict(clf, X, y, cv=skf)
        acc = accuracy_score(y, oof_pred)
        macro_f1 = f1_score(y, oof_pred, average="macro")
        depth_label = "unlimited" if depth is None else depth
        print(f"  max_depth={depth_label}: OOF accuracy={acc * 100:.1f}% | OOF macro-F1={macro_f1 * 100:.1f}%")
        depth_results[str(depth_label)] = {"accuracy": float(acc), "macro_f1": float(macro_f1)}
        if macro_f1 > best_macro_f1:
            best_depth, best_macro_f1, best_oof_pred = depth, macro_f1, oof_pred

    # Full-data fit at the best depth, for interpretation ONLY (feature importance/tree rules)
    # - this fit's own accuracy is never reported as a generalization metric.
    clf = DecisionTreeClassifier(max_depth=best_depth, min_samples_leaf=25,
                                  class_weight="balanced", random_state=SEED)
    clf.fit(X, y)

    importance_df = pd.DataFrame({
        "feature": feature_cols, "importance": clf.feature_importances_,
    }).sort_values("importance", ascending=False)
    importance_df.to_csv(f"{report_prefix}_feature_importance.csv", index=False, encoding="utf-8-sig")

    # export_text's own max_depth caps how many levels of the already-fit tree get printed, not
    # how the tree was built - pass a large cap when best_depth is None (unlimited) rather than
    # None itself (export_text does `depth <= max_depth + 1` internally and breaks on None).
    export_text_depth = best_depth if best_depth is not None else 50
    with open(f"{report_prefix}_tree_rules.txt", "w", encoding="utf-8") as f:
        f.write(export_text(clf, feature_names=feature_cols, max_depth=export_text_depth))

    classes_sorted = sorted(y.unique().tolist())
    conf_df = pd.DataFrame(
        pd.crosstab(y, pd.Series(best_oof_pred, index=y.index), rownames=["true_author"],
                    colnames=["predicted_author"]).reindex(index=classes_sorted, columns=classes_sorted, fill_value=0)
    )
    conf_df.to_csv(f"{report_prefix}_confusion_matrix.csv", encoding="utf-8-sig")

    try:
        fig_w = max(14, n_classes * 0.4)
        plt.figure(figsize=(fig_w, 12))
        plot_tree(clf, feature_names=feature_cols, class_names=classes_sorted,
                  filled=True, rounded=True, fontsize=5, max_depth=3)
        plt.tight_layout()
        plt.savefig(f"{report_prefix}_tree.png", dpi=150)
        plt.close()
    except Exception as e:  # pragma: no cover - plotting is best-effort only
        print(f"  [warn] tree plot failed ({e}), continuing without it.")

    best_depth_label = "unlimited" if best_depth is None else best_depth
    beats_both_baselines = (depth_results[str(best_depth_label)]["accuracy"] > majority_baseline and
                             depth_results[str(best_depth_label)]["accuracy"] > chance_baseline)
    return {
        "scope": scope_label,
        "n_authors": int(n_classes),
        "n_examples": int(n_examples),
        "majority_baseline": float(majority_baseline),
        "chance_baseline": float(chance_baseline),
        "depth_results": depth_results,
        "best_depth": best_depth_label,
        "best_depth_beats_both_baselines": bool(beats_both_baselines),
        "top_features": importance_df.head(5)["feature"].tolist(),
    }


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    dataset = build_dataset()

    # ---- Experiment A: global (all narratives pooled) ----
    result_a = run_cv_experiment(
        dataset, ALL_FEATURES, depths=(5, 10, 15, None),
        report_prefix=os.path.join(REPORT_DIR, "experiment_a_global"),
        scope_label="Experiment A - global author prediction (all narratives pooled)",
    )

    # ---- Experiment B: within each narrative with >= 2 eligible authors ----
    results_b = []
    for narrative in sorted(dataset["narrative_name"].unique()):
        subset = dataset[dataset["narrative_name"] == narrative].reset_index(drop=True)
        if subset["author"].nunique() < 2:
            print(f"\n[skip] narrative '{narrative}' has < 2 eligible authors, skipping Experiment B.")
            continue
        result = run_cv_experiment(
            subset, ALL_FEATURES, depths=(3, 4, 5),
            report_prefix=os.path.join(REPORT_DIR, f"experiment_b_{narrative}"),
            scope_label=f"Experiment B - within-narrative author prediction ({narrative})",
        )
        results_b.append(result)

    any_b_beats_baseline = any(r["best_depth_beats_both_baselines"] for r in results_b)
    summary = {
        "seed": SEED,
        "min_examples_per_author": MIN_EXAMPLES_PER_AUTHOR,
        "n_features": len(ALL_FEATURES),
        "features": ALL_FEATURES,
        "experiment_a": result_a,
        "experiment_b_by_narrative": results_b,
        "experiment_a_beats_both_baselines": result_a["best_depth_beats_both_baselines"],
        "any_experiment_b_narrative_beats_both_baselines": any_b_beats_baseline,
    }
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved run summary to '{SUMMARY_FILE}'.")


if __name__ == "__main__":
    main()

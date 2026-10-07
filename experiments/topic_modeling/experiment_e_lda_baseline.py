"""Experiment E: a fully SEPARATE classic-LDA baseline, compared against BERTopic Hard and
BERTopic Soft (the existing `models/experiments/soft_v2_baseline_seeded` model - the final
selected baseline from Experiments A/A2/B/C) on the same corpus and the same underlying cleaned
text, using the metrics the user explicitly asked for: Topic Coherence, Topic Diversity,
Interpretability, seed-stability, document-topic distribution shape, and coverage/outliers where
applicable.

Explicitly NOT a replacement for BERTopic - this is a benchmark data point only. Nothing in
`fusion.py`/`train.py`/any checkpoint/`models/saved_topic_model`/`models/saved_topic_model_soft_v2`
is touched. The LDA model itself is a brand-new artifact saved under its own path
(`models/experiments/lda_baseline/`), never read by any other part of the codebase.

Methodology
-----------
1. Corpus: reuses `load_deduplicated_training_texts()` (train_topics.py) - the SAME 16,062
   cleaned+deduplicated texts BERTopic's soft_v2_baseline_seeded was fit on. Guarantees the LDA
   vs BERTopic comparison is on identical documents, not just "a similar corpus".
2. Tokenization (LDA-specific, classic bag-of-words - unrelated to BERTopic's own vectorizer):
   lowercase, alphabetic tokens only, length >= 3, sklearn's English stop word list removed.
   A single shared `gensim.corpora.Dictionary` (no_below=5, no_above=0.5, keep_n=10000) is built
   from this tokenization and used for BOTH (a) fitting LDA itself and (b) computing coherence
   for BERTopic's own topics (see step 4) - so coherence numbers are computed the same way for
   both methods, not confounded by different vocabularies.
3. Choosing K (number of LDA topics) - PRINCIPLED, not copied from BERTopic's topic count:
   a coherence sweep over K in {50, 100, 150, 200} (u_mass coherence, gensim's `CoherenceModel`,
   which only needs the SAME training corpus - no external reference corpus/window-cooccurrence
   computation needed, unlike c_v - keeping this tractable on a CPU-only machine). The K with the
   highest (least-negative) mean u_mass coherence across its own topics is selected as the final
   LDA baseline's topic count. A single-process `gensim.models.LdaModel` is used throughout -
   calibrated directly on this machine: `LdaMulticore` (multi-worker) was tried first, but on
   Windows each `LdaMulticore` fit re-spawns a fresh worker pool ("spawn", not "fork") that
   re-imports and re-pickles the full corpus per worker; measured at ~158s for a tiny K=50/
   passes=1/iterations=20 fit, vs ~2s for the same config single-process, and ~8s single-process
   for the far larger K=200/passes=3/iterations=50 - the corpus (16,062 docs, ~7,500-word
   vocabulary after filtering) is simply too small for multi-process gensim LDA to pay off on
   this OS; single-process is both simpler and dramatically faster here.
4. Topic Coherence (u_mass, same CoherenceModel/dictionary/corpus as step 3) is computed for
   BOTH the final LDA model's topics AND BERTopic Hard's topics (top-10 words per non-outlier
   topic from `topic_model.get_topic(tid)`, restricted to single-word terms that exist in the
   shared dictionary - BERTopic's MMR-diversified representation occasionally returns multi-word
   phrases which have no single vocabulary entry; these are decomposed to their first token or
   dropped if still OOV, and the drop count is reported for transparency).
5. Topic Diversity = (# unique words among each topic's top-10) / (10 * n_topics) - the standard,
   framework-agnostic definition - computed directly from each method's own top word lists
   (no dictionary filtering involved here, unlike coherence).
6. Interpretability: a manual qualitative read of the final LDA model's own top-10 topics
   (printed to the console/report), following the same "does the top word list look topically
   coherent to a human, or is it a noisy word-salad" standard already used qualitatively for
   BERTopic in Experiments A-C's manual reviews.
7. Seed-stability: refits the FINAL LDA (same chosen K) with a second random_state (7) and
   measures topic alignment via a document-membership BEST-Jaccard match (same conceptual
   approach as Experiment D2's document-membership topic mapping, adapted for LDA: each doc's
   dominant topic per model defines a topic->docset mapping; each seed-42 topic is matched to
   its highest-Jaccard-overlap seed-7 topic, not an exact match, since LDA topic boundaries are
   inherently soft/different across random inits) plus a secondary top-10-word Jaccard, for a
   second, content-based corroborating signal.
8. Document-topic distribution + coverage/outliers: computed on the SAME 280-text deterministic
   stratified sample used throughout this project's soft-quality analysis
   (`analyze_soft_topic_quality.load_stratified_sample(seed=42)`), for a like-for-like comparison
   against the already-existing BERTopic Hard/Soft numbers in
   `artifacts/experiments/profiler_prototype/soft_topic_quality_summary.json` (baseline run). LDA's own
   per-document topic distribution (`gensim`'s `get_document_topics`) yields, for each doc: the
   top-1 topic's probability (analogous to BERTopic's soft top1 score) and Shannon entropy of the
   full K-way distribution (LDA-specific - BERTopic's soft distribution is sparse/truncated to
   the texts' matched topics only, not comparable to entropy directly, so entropy is reported for
   LDA only, with commentary). LDA has NO outlier concept (unlike HDBSCAN) - every document
   always receives a full distribution over all K topics - this structural difference is called
   out explicitly rather than forcing an artificial "outlier %" number for LDA.
9. Runtime: wall-clock time for the coherence sweep, the final model fit (x2 seeds), and
   per-document inference on the 280-text sample are all measured directly. BERTopic's OWN
   training-time is NOT re-measured in this script (re-fitting soft_v2_baseline_seeded is out of
   scope / would be wasteful duplicate work) - only BERTopic's INFERENCE time on the same
   280-text sample is measured here (reusing the already-saved model), for an apples-to-apples
   inference-side runtime comparison; training-time comparison is explicitly left as "not
   measured, out of scope" rather than guessed.

Run (from repo root): python experiments/topic_modeling/experiment_e_lda_baseline.py
"""
import json
import os
import re
import time

import numpy as np
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# NOTE: `BERTopic` (and transitively torch/sentence-transformers) is deliberately NOT imported at
# module level to keep this module lightweight to import - it is imported lazily instead, inside
# `compute_bertopic_hard_metrics()`, the only place that needs it.
from narrative_lens.evaluation.analyze_soft_topic_quality import load_stratified_sample
from narrative_lens.train_topics import load_deduplicated_training_texts

REPORT_DIR = "artifacts/experiments/profiler_prototype"
LDA_MODEL_DIR = "models/experiments/lda_baseline"
BERTOPIC_BASELINE_PATH = "models/experiments/soft_v2_baseline_seeded"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

K_SWEEP = [50, 100, 150, 200]
LDA_PASSES = 5
LDA_ITERATIONS = 100
TOP_N_WORDS = 10
DICT_NO_BELOW = 5
DICT_NO_ABOVE = 0.5
DICT_KEEP_N = 10_000
SEED_A = 42
SEED_B = 7

_TOKEN_RE = re.compile(r"[a-z]+")


def tokenize(text):
    """Classic bag-of-words tokenization for LDA: lowercase, alphabetic-only tokens, length>=3,
    sklearn's English stop word list removed. Independent of BERTopic's own vectorizer/tokenizer
    (BERTopic uses its own CountVectorizer defaults) - this is LDA's own preprocessing step."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if len(t) >= 3 and t not in ENGLISH_STOP_WORDS]


def build_dictionary_and_corpus(tokenized_docs):
    dictionary = Dictionary(tokenized_docs)
    dictionary.filter_extremes(no_below=DICT_NO_BELOW, no_above=DICT_NO_ABOVE, keep_n=DICT_KEEP_N)
    corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]
    return dictionary, corpus


def fit_lda(corpus, dictionary, num_topics, random_state, passes=LDA_PASSES, iterations=LDA_ITERATIONS):
    return LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        passes=passes,
        iterations=iterations,
        random_state=random_state,
        eval_every=None,
    )


def lda_topic_words(lda_model, num_topics, top_n=TOP_N_WORDS):
    return [
        [w for w, _ in lda_model.show_topic(tid, topn=top_n)]
        for tid in range(num_topics)
    ]


def compute_coherence(topics_words, tokenized_docs, dictionary, corpus):
    """u_mass coherence over an arbitrary list of top-word lists - works for both LDA's own
    topics AND (separately, by the caller) BERTopic's topics, as long as every word is present
    in `dictionary`. u_mass needs no external reference corpus (unlike c_v), only `corpus`."""
    cm = CoherenceModel(
        topics=topics_words, texts=tokenized_docs, corpus=corpus, dictionary=dictionary,
        coherence="u_mass",
    )
    return cm.get_coherence(), cm.get_coherence_per_topic()


def topic_diversity(topics_words):
    all_words = [w for topic in topics_words for w in topic]
    if not all_words:
        return None
    return len(set(all_words)) / len(all_words)


def run_k_sweep(tokenized_docs, dictionary, corpus):
    print(f"=== שלב 1: coherence sweep על K={K_SWEEP} (u_mass) ===")
    sweep_results = []
    for k in K_SWEEP:
        t0 = time.time()
        model = fit_lda(corpus, dictionary, num_topics=k, random_state=SEED_A)
        fit_seconds = time.time() - t0
        words = lda_topic_words(model, k)
        mean_coh, _ = compute_coherence(words, tokenized_docs, dictionary, corpus)
        div = topic_diversity(words)
        print(f"  K={k}: u_mass_coherence={mean_coh:.4f}  diversity={div:.3f}  fit_time={fit_seconds:.1f}s")
        sweep_results.append({
            "k": k, "u_mass_coherence": mean_coh, "topic_diversity": div, "fit_seconds": fit_seconds,
        })
    best = max(sweep_results, key=lambda r: r["u_mass_coherence"])
    print(f"  -> נבחר K={best['k']} (u_mass coherence הגבוה ביותר: {best['u_mass_coherence']:.4f})")
    return sweep_results, best["k"]


def doc_membership_by_argmax(lda_model, corpus, num_topics):
    """Maps each doc to its single dominant (argmax-probability) topic - the LDA analogue of
    BERTopic's hard topic_id - used to build topic->docset sets for the seed-stability check."""
    doc_topics = [None] * len(corpus)
    topic_docs = {tid: set() for tid in range(num_topics)}
    for i, bow in enumerate(corpus):
        dist = lda_model.get_document_topics(bow, minimum_probability=0.0)
        top_tid = max(dist, key=lambda x: x[1])[0]
        doc_topics[i] = top_tid
        topic_docs[top_tid].add(i)
    return doc_topics, topic_docs


def seed_stability_check(corpus, dictionary, chosen_k, tokenized_docs):
    print(f"\n=== שלב 2: seed-stability check (K={chosen_k}, seeds {SEED_A} vs {SEED_B}) ===")
    t0 = time.time()
    model_a = fit_lda(corpus, dictionary, chosen_k, random_state=SEED_A)
    fit_seconds_a = time.time() - t0
    t0 = time.time()
    model_b = fit_lda(corpus, dictionary, chosen_k, random_state=SEED_B)
    fit_seconds_b = time.time() - t0

    _, topic_docs_a = doc_membership_by_argmax(model_a, corpus, chosen_k)
    _, topic_docs_b = doc_membership_by_argmax(model_b, corpus, chosen_k)

    def best_jaccard_match(docset, other_topic_docs):
        best_j, best_tid = 0.0, None
        for tid, other_docset in other_topic_docs.items():
            union = len(docset | other_docset)
            inter = len(docset & other_docset)
            j = inter / union if union else 0.0
            if j > best_j:
                best_j, best_tid = j, tid
        return best_j, best_tid

    doc_jaccards = []
    for tid, docset in topic_docs_a.items():
        if not docset:
            continue
        j, _ = best_jaccard_match(docset, topic_docs_b)
        doc_jaccards.append(j)

    words_a = lda_topic_words(model_a, chosen_k)
    words_b = lda_topic_words(model_b, chosen_k)
    word_jaccards = []
    for wa in words_a:
        sa = set(wa)
        best_j = max((len(sa & set(wb)) / len(sa | set(wb)) for wb in words_b), default=0.0)
        word_jaccards.append(best_j)

    result = {
        "chosen_k": chosen_k,
        "seed_a": SEED_A, "seed_b": SEED_B,
        "fit_seconds_seed_a": fit_seconds_a, "fit_seconds_seed_b": fit_seconds_b,
        "doc_membership_best_jaccard_mean": float(np.mean(doc_jaccards)),
        "doc_membership_best_jaccard_median": float(np.median(doc_jaccards)),
        "top_words_best_jaccard_mean": float(np.mean(word_jaccards)),
        "top_words_best_jaccard_median": float(np.median(word_jaccards)),
    }
    print(f"  doc-membership best-Jaccard: mean={result['doc_membership_best_jaccard_mean']:.3f} "
          f"median={result['doc_membership_best_jaccard_median']:.3f}")
    print(f"  top-10-word best-Jaccard: mean={result['top_words_best_jaccard_mean']:.3f} "
          f"median={result['top_words_best_jaccard_median']:.3f}")
    return result, model_a


def compute_final_lda_metrics(model_a, corpus, dictionary, tokenized_docs, chosen_k):
    words = lda_topic_words(model_a, chosen_k)
    mean_coh, per_topic_coh = compute_coherence(words, tokenized_docs, dictionary, corpus)
    div = topic_diversity(words)
    return {
        "chosen_k": chosen_k,
        "u_mass_coherence_mean": mean_coh,
        "u_mass_coherence_per_topic": per_topic_coh,
        "topic_diversity": div,
        "top_words_per_topic": {int(tid): w for tid, w in enumerate(words)},
    }


def compute_lda_doc_distribution(model_a, dictionary, sample_texts, chosen_k):
    """Document-topic distribution stats on the SAME 280-text stratified sample used for
    BERTopic's soft-quality analysis - top1 probability stats + Shannon entropy (LDA-specific,
    since every doc gets a full K-way distribution, unlike BERTopic's sparse soft output)."""
    t0 = time.time()
    top1_probs, entropies = [], []
    for text in sample_texts:
        bow = dictionary.doc2bow(tokenize(text))
        dist = model_a.get_document_topics(bow, minimum_probability=0.0)
        probs = np.array([p for _, p in dist], dtype=float)
        probs = probs / probs.sum() if probs.sum() > 0 else probs
        top1_probs.append(float(probs.max()) if probs.size else 0.0)
        nz = probs[probs > 0]
        entropies.append(float(-(nz * np.log(nz)).sum()) if nz.size else 0.0)
    inference_seconds = time.time() - t0
    top1_arr, ent_arr = np.array(top1_probs), np.array(entropies)
    max_entropy = float(np.log(chosen_k))
    return {
        "n_texts": len(sample_texts),
        "inference_seconds": inference_seconds,
        "top1_prob_mean": float(top1_arr.mean()), "top1_prob_median": float(np.median(top1_arr)),
        "top1_prob_min": float(top1_arr.min()), "top1_prob_max": float(top1_arr.max()),
        "entropy_mean": float(ent_arr.mean()), "entropy_median": float(np.median(ent_arr)),
        "max_possible_entropy": max_entropy,
        "normalized_entropy_mean": float(ent_arr.mean() / max_entropy) if max_entropy > 0 else None,
        "pct_no_dominant_topic_top1_lt_0.3": float(100 * (top1_arr < 0.3).mean()),
    }


def compute_bertopic_hard_metrics(dictionary, tokenized_docs, corpus, sample_texts):
    from bertopic import BERTopic  # lazy import - see module-level NOTE above `LdaMulticore` usage

    print("\n=== שלב 4: מדדי BERTopic Hard (coherence/diversity/outliers/inference-time) ===")
    t0 = time.time()
    model = BERTopic.load(BERTOPIC_BASELINE_PATH, embedding_model=EMBEDDING_MODEL_NAME)
    load_seconds = time.time() - t0

    topic_ids = [tid for tid in model.get_topics().keys() if tid != -1]
    raw_top_words = {tid: [w for w, _ in model.get_topic(tid)][:TOP_N_WORDS] for tid in topic_ids}

    # Filter to single-word terms present in the shared dictionary (see module docstring step 4).
    filtered_words, n_dropped_words, n_topics_all_dropped = [], 0, 0
    for tid, words in raw_top_words.items():
        kept = []
        for w in words:
            token = w.split()[0].lower() if " " in w else w.lower()
            if token in dictionary.token2id:
                kept.append(token)
            else:
                n_dropped_words += 1
        if kept:
            filtered_words.append(kept)
        else:
            n_topics_all_dropped += 1

    mean_coh, _ = compute_coherence(filtered_words, tokenized_docs, dictionary, corpus)
    div = topic_diversity([raw_top_words[tid] for tid in topic_ids])

    full_hard_topics = np.array(model.topics_)
    outlier_pct_full_corpus = float(100 * (full_hard_topics == -1).mean())

    t0 = time.time()
    _ = model.transform(sample_texts)
    inference_seconds = time.time() - t0

    result = {
        "n_topics": len(topic_ids),
        "u_mass_coherence_mean_on_filtered_words": mean_coh,
        "n_words_dropped_oov_or_multiword": n_dropped_words,
        "n_topics_fully_dropped_from_coherence": n_topics_all_dropped,
        "topic_diversity_raw_top_words": div,
        "outlier_pct_full_training_corpus": outlier_pct_full_corpus,
        "load_seconds": load_seconds,
        "inference_seconds_280_sample": inference_seconds,
    }
    print(f"  n_topics={result['n_topics']}  u_mass_coherence(filtered)={mean_coh:.4f}  "
          f"diversity(raw)={div:.3f}  outlier%={outlier_pct_full_corpus:.2f}  "
          f"(dropped {n_dropped_words} OOV/multiword words, {n_topics_all_dropped} topics fully dropped)")
    return result


def load_existing_bertopic_soft_summary():
    """Reuses the already-computed soft-distribution summary for soft_v2_baseline_seeded
    (Experiments A-D2 all reuse this same file/methodology) rather than re-running the expensive
    approximate_distribution() step redundantly in this script."""
    path = os.path.join(REPORT_DIR, "soft_topic_quality_summary.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(LDA_MODEL_DIR, exist_ok=True)

    print("טוען קורפוס (16,062 טקסטים, זהה ל-soft_v2_baseline_seeded)...")
    texts_list = load_deduplicated_training_texts(verbose=False)
    tokenized_docs = [tokenize(t) for t in texts_list]
    dictionary, corpus = build_dictionary_and_corpus(tokenized_docs)
    print(f"  מילון: {len(dictionary)} מילים ייחודיות (אחרי סינון no_below={DICT_NO_BELOW}, "
          f"no_above={DICT_NO_ABOVE}, keep_n={DICT_KEEP_N})")

    sweep_results, chosen_k = run_k_sweep(tokenized_docs, dictionary, corpus)

    stability_result, model_a = seed_stability_check(corpus, dictionary, chosen_k, tokenized_docs)

    print(f"\n=== שלב 3: מדדים סופיים ל-LDA (K={chosen_k}) ===")
    final_lda_metrics = compute_final_lda_metrics(model_a, corpus, dictionary, tokenized_docs, chosen_k)
    print(f"  u_mass coherence={final_lda_metrics['u_mass_coherence_mean']:.4f}  "
          f"diversity={final_lda_metrics['topic_diversity']:.3f}")
    print("  --- 10 topics ראשונים (עבור interpretability - קריאה ידנית) ---")
    for tid in range(min(10, chosen_k)):
        print(f"    [{tid}] {', '.join(final_lda_metrics['top_words_per_topic'][tid])}")

    sample_df = load_stratified_sample(n_per_narrative=40, seed=42)
    sample_texts = sample_df["text"].tolist()
    lda_doc_dist = compute_lda_doc_distribution(model_a, dictionary, sample_texts, chosen_k)
    print(f"\n=== שלב 5: document-topic distribution (LDA, 280-sample) ===")
    print(f"  top1_prob: mean={lda_doc_dist['top1_prob_mean']:.3f} median={lda_doc_dist['top1_prob_median']:.3f}")
    print(f"  normalized entropy: mean={lda_doc_dist['normalized_entropy_mean']:.3f} "
          f"(0=fully concentrated, 1=uniform over all K={chosen_k} topics)")
    print(f"  % no dominant topic (top1<0.3): {lda_doc_dist['pct_no_dominant_topic_top1_lt_0.3']:.1f}%")

    bertopic_hard_metrics = compute_bertopic_hard_metrics(dictionary, tokenized_docs, corpus, sample_texts)
    bertopic_soft_summary = load_existing_bertopic_soft_summary()

    model_a.save(os.path.join(LDA_MODEL_DIR, f"lda_k{chosen_k}_seed{SEED_A}"))
    dictionary.save(os.path.join(LDA_MODEL_DIR, "dictionary.gensim"))

    output = {
        "corpus_size": len(texts_list),
        "vocab_size": len(dictionary),
        "k_sweep": sweep_results,
        "chosen_k": chosen_k,
        "final_lda_metrics": {k: v for k, v in final_lda_metrics.items() if k != "top_words_per_topic"},
        "final_lda_top_words_per_topic": final_lda_metrics["top_words_per_topic"],
        "seed_stability": stability_result,
        "lda_doc_topic_distribution_280_sample": lda_doc_dist,
        "bertopic_hard_metrics": bertopic_hard_metrics,
        "bertopic_soft_summary_reused_from_baseline": bertopic_soft_summary,
    }
    out_path = os.path.join(REPORT_DIR, "expE_lda_baseline.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nתוצאות מלאות נשמרו ל-{out_path}")
    print(f"מודל LDA נשמר ל-{LDA_MODEL_DIR} (נפרד לגמרי, לא נגיש לשום קוד אחר).")
    print("\nExperiment E הושלם. לא נגעו ב-fusion.py / train.py / checkpoints / "
          "saved_topic_model_soft_v2 / saved_topic_model.")


if __name__ == "__main__":
    main()

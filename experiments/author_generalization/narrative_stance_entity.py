"""
Narrative Classification — Stance-Aware Entity Representation (Experiment 22)
==============================================================================
PHASE 1 ONLY: entity-targeted stance extraction + a manual-review validation sample.
Does NOT run LOAO training and does NOT touch the classification models - per an explicit
gate: the target-conditioned stance signal must be shown (on a hand-reviewed sample) to be
reasonably accurate BEFORE any feature/model work happens. See EXPERIMENTS.md section 22 for
the full write-up once the gate is passed.

Research question: can entity identity remain useful for narrative classification when
conditioned on the author's stance TOWARD that entity, rather than used as an identity-only
feature (as in section 21's plain entity masking)?

--- Why not the existing "Stance" module (stance.py / TopicStanceLayer) ---
Audited first (see chat). `TopicAnalysisPipeline.process_text()` takes a whole text and
returns only a hard BERTopic topic_id - no entity information in or out, and no stance/
sentiment value at all (the class name is legacy; fusion.py explicitly discards any
stance-like value: "topic_id = features['stance']  # deliberately ignore stance_label").
Not usable for entity-targeted stance in any configuration.

--- Why not entity_role_tagger.py (evaluation/) ---
This IS entity-mention-targeted (assigns hero/victim/aggressor/betrayer/savior per mention),
but its own gold-calibration results (reports/results/profiler_prototype/eval_entity_role_*)
show only 12/167 (~7%) judged "correct" by a human annotator, with F1=0.0 for hero/aggressor/
betrayer. Not reliable enough to reuse as a pseudo-label source.

--- Why not generic sentence-level sentiment ---
A sentence can be net-positive/negative while an individual entity mentioned in it is treated
neutrally (or oppositely) - context sentiment is not necessarily attitude-toward-THIS-entity.
Kept only as a conceptual fallback, not used here.

--- Candidate method actually used: pretrained target-dependent (ABSA) sentiment ---
yangheng/deberta-v3-base-absa-v1.1 (DeBERTa-v3 + PyABSA's FAST-LCF-BERT training; SemEval-2014/
2016 + MAMS, ~1M downloads) takes (context, target) pairs directly:
    classifier(sentence, text_pair="food") -> {"Positive": .., "Negative": .., "Neutral": ..}
This is a genuine target-conditioned pretrained sentiment classifier (not a supervised stance
model trained on THIS project's data, and not zero-shot/NLI pseudo-labeling) - the strongest
"already exists, don't build something complicated" option available. Documented explicitly
here as an off-the-shelf heuristic being validated against a hand-labeled sample, not as a
ground-truth stance model.

--- Representation built here (masking, same spirit as section 21) ---
Each entity mention -> (entity_group, predicted_stance) -> a single placeholder token that
keeps entity TYPE + attitude but removes entity IDENTITY, e.g.:
    "Trump is destroying American democracy" -> "[PERSON:NEG] is destroying American democracy"
Local context = the spaCy sentence containing the mention (en_core_web_trf, already a project
dependency - used here ONLY for sentence boundaries, not for entity_role_tagger's rule-based
role logic).

--- Phase 1 outputs (this script) ---
1. reports/results/narrative_stance_entity/validation_sample.csv: ~150-200 entity mentions,
   balanced across the 3 LOAO authors (IDF, MariaZakharova, BernieSanders - same accounts/
   same split_leave_one_author test sets as sections 19-21). Columns are ordered so the
   annotator-facing ones come first (author, context, target_entity, entity_type,
   predicted_stance, gold_stance, error_category, annotator_notes), with raw ABSA
   scores/metadata pushed to the end. gold_stance/error_category/annotator_notes are left
   BLANK for a human to fill in by hand - see STANCE_ANNOTATION_GUIDE.md (saved alongside the
   CSV) for label definitions and edge-case rules (quotation/negation/sarcasm/reported
   speech/action-vs-entity/multiple-entities/short-context/entity-boundary/entity-type).
   error_category allowed values: see ERROR_CATEGORIES below.
2. reports/results/narrative_stance_entity/STANCE_ANNOTATION_GUIDE.md: the annotation
   instructions (label definitions + edge-case rules) referenced above.
3. --show-qualitative: prints a handful of examples per author to the console for a first
   qualitative look (ASCII-safe printing) before/alongside the manual annotation pass.

Run:
    python experiments/author_generalization/narrative_stance_entity.py --build-sample
    python experiments/author_generalization/narrative_stance_entity.py --show-qualitative

Next step (NOT this script, NOT yet run): after gold_stance is filled in by hand, compute
accuracy/agreement + error-category breakdown against reports/results/narrative_stance_entity/
validation_sample.csv, and only if that signal is judged strong enough, build the full 7-variant
LOAO comparison (sbert_only / sbert_ner / sbert_masked / sbert_soft_topic /
sbert_masked_soft_topic / sbert_stance_masked / sbert_stance_masked_soft_topic).
"""
import argparse
import os

import pandas as pd
import torch
import spacy
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import pipeline as hf_pipeline

from narrative_lens.train import load_raw_data, split_leave_one_author
from narrative_lens.features.ner import EntityAnalysisPipeline, reconstruct_fragmented_entities

AUTHORS = ("IDF", "MariaZakharova", "BernieSanders")
SEED = 42  # matches split_leave_one_author's own fixed random_state=42 (sections 19-21)

TARGET_MENTIONS_PER_AUTHOR = 60   # ~180 total, within the requested 150-200 range
MAX_MENTIONS_PER_TEXT = 2         # avoid a handful of texts dominating the sample
MAX_TEXT_CHARS = 3000             # matches load_raw_data()/section 21 text-length convention

ABSA_MODEL_NAME = "yangheng/deberta-v3-base-absa-v1.1"
STANCE_LABEL_MAP = {"Positive": "positive", "Negative": "negative", "Neutral": "neutral"}
MASK_STANCE_SUFFIX = {"positive": "POS", "negative": "NEG", "neutral": "NEU"}
ENTITY_TYPE_TOKENS = {"PER": "PERSON", "ORG": "ORG", "LOC": "LOCATION", "MISC": "MISC"}

ERROR_CATEGORIES = (
    "none", "negation", "quotation", "sarcasm", "wrong_entity_boundary",
    "wrong_entity_type", "insufficient_context", "multiple_entities",
    "reported_speech", "action_vs_entity", "other",
)

REPORT_DIR = "reports/results/narrative_stance_entity"
VALIDATION_SAMPLE_FILE = os.path.join(REPORT_DIR, "validation_sample.csv")
ANNOTATION_GUIDE_FILE = os.path.join(REPORT_DIR, "STANCE_ANNOTATION_GUIDE.md")
PILOT_SAMPLE_FILE = os.path.join(REPORT_DIR, "pilot_sample_30.csv")

PILOT_ANNOTATED_FILE = os.path.join(REPORT_DIR, "pilot_sample_30_annotated.csv")
CONTEXT_EXPERIMENT_FILE = os.path.join(REPORT_DIR, "context_width_experiment.csv")

PILOT_SIZE_PER_AUTHOR = 10
STANCE_CLASSES = ("positive", "negative", "neutral")
# Mentions flagged as suspicious during the initial qualitative look (see chat) - forced into
# the pilot regardless of the class-balancing logic below.
REQUIRED_PILOT_IDS = ("IDF_011", "IDF_023", "IDF_024", "MariaZakharova_039")

# Root-cause bucket per error_category, per the user's requested 3-way split: did the ABSA
# model reason wrong given adequate input (absa_prediction_error), was the local context too
# short to expose the real stance (insufficient_context), or was the entity span/type itself
# wrong going into the ABSA call (ner_entity_error)?
ERROR_BUCKET_MAP = {
    "wrong_entity_boundary": "ner_entity_error",
    "wrong_entity_type": "ner_entity_error",
    "insufficient_context": "insufficient_context",
    "negation": "absa_prediction_error",
    "quotation": "absa_prediction_error",
    "sarcasm": "absa_prediction_error",
    "multiple_entities": "absa_prediction_error",
    "reported_speech": "absa_prediction_error",
    "action_vs_entity": "absa_prediction_error",
    "other": "absa_prediction_error",
}

# --- Mini-benchmark candidates (Experiment 22 gate did NOT pass for the ABSA model above -
# see chat: 60% sentence / 66.7% full-post, both below the 70-75% bar, full-post also
# introduced a new failure mode). These 3 are tried on the SAME 30 gold pilot rows, same
# target entity, before any decision to keep tuning ABSA or pivot away from it entirely. ---

# Candidate A: a real target-dependent stance model (text, target) -> FAVOR/AGAINST/NONE,
# trained on SemEval-2016 Task 6. id2label confirmed from the model's config.json.
SEMEVAL_STANCE_MODEL = "krishnagarg09/stance-detection-semeval2016"
SEMEVAL_LABEL_MAP = {"FAVOR": "positive", "AGAINST": "negative", "NONE": "neutral"}

# Candidate B: NOT a supervised stance model - a generic NLI/zero-shot classifier repurposed
# via explicit target-conditioned hypotheses (documented here, not a ground-truth stance
# model). Entailment score across the 3 hypotheses picks the label.
NLI_MODEL = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
NLI_HYPOTHESIS_TEMPLATES = {
    "positive": "The author supports {target}.",
    "negative": "The author opposes {target}.",
    "neutral": "The author expresses no clear attitude toward {target}.",
}

# Candidate C: a real stance model, but PRO/CON only (IBM ArgKP-2023, topic-vs-argument) -
# has NO neutral class. Per model card usage: predicted_class==1 -> PRO, ==0 -> CON.
# Abstention-to-neutral rule below is a FIXED, PRE-DECLARED margin on |P(PRO)-P(CON)|,
# chosen before looking at any gold label in this pilot (not tuned against our data - see
# predict_procon_stance() docstring for the exact rule used).
PROCON_STANCE_MODEL = "NLP-Debater-Project/debertav3-stance-detection"
PROCON_ABSTENTION_MARGIN = 0.15

STANCE_METHOD_BENCHMARK_FILE = os.path.join(REPORT_DIR, "stance_method_benchmark.csv")

_nlp = None
_absa_classifier = None
_ner_pipeline = None
_semeval_classifier = None
_nli_classifier = None
_procon_tokenizer = None
_procon_model = None


def get_nlp():
    """Lazy-loaded spaCy parser, reused ONLY for sentence-boundary detection here (not for
    entity_role_tagger.py's rule-based role logic)."""
    global _nlp
    if _nlp is None:
        print("Loading spaCy en_core_web_trf (sentence boundaries only)...")
        _nlp = spacy.load("en_core_web_trf")
    return _nlp


def get_absa_classifier():
    global _absa_classifier
    if _absa_classifier is None:
        print(f"Loading target-dependent ABSA classifier '{ABSA_MODEL_NAME}'...")
        _absa_classifier = hf_pipeline("text-classification", model=ABSA_MODEL_NAME, top_k=None)
    return _absa_classifier


def get_ner_pipeline():
    global _ner_pipeline
    if _ner_pipeline is None:
        _ner_pipeline = EntityAnalysisPipeline()
    return _ner_pipeline


def get_local_context(text, start, end):
    """Sentence-level local context: the spaCy sentence spanning [start, end). Falls back to
    the full text if no sentence boundary matches (e.g. offset misalignment on odd
    whitespace/emoji) - documented fallback, not a silent failure."""
    doc = get_nlp()(text)
    for sent in doc.sents:
        if sent.start_char <= start and end <= sent.end_char:
            return sent.text
    return text


def predict_entity_stance(local_context, entity_text):
    """Target-conditioned sentiment via yangheng/deberta-v3-base-absa-v1.1: entity_text is
    passed as text_pair (the aspect/target), so the prediction is conditioned on that
    specific target, not just generic sentence sentiment. Returns (stance_label, scores)."""
    absa = get_absa_classifier()
    result = absa(local_context, text_pair=entity_text)[0]
    scores = {r["label"]: float(r["score"]) for r in result}
    best_label = max(scores, key=scores.get)
    return STANCE_LABEL_MAP.get(best_label, "neutral"), scores


def get_semeval_classifier():
    global _semeval_classifier
    if _semeval_classifier is None:
        print(f"Loading SemEval-2016 stance classifier '{SEMEVAL_STANCE_MODEL}'...")
        _semeval_classifier = hf_pipeline("text-classification", model=SEMEVAL_STANCE_MODEL, top_k=None)
    return _semeval_classifier


def predict_semeval_stance(context_text, entity_text):
    """Candidate A: krishnagarg09/stance-detection-semeval2016, a real (text, target) ->
    FAVOR/AGAINST/NONE stance model (not sentiment). Mapped FAVOR->positive,
    AGAINST->negative, NONE->neutral."""
    clf = get_semeval_classifier()
    result = clf(context_text, text_pair=entity_text)[0]
    scores = {r["label"]: float(r["score"]) for r in result}
    best_label = max(scores, key=scores.get)
    return SEMEVAL_LABEL_MAP.get(best_label, "neutral"), scores


def get_nli_classifier():
    global _nli_classifier
    if _nli_classifier is None:
        print(f"Loading NLI zero-shot classifier '{NLI_MODEL}'...")
        _nli_classifier = hf_pipeline("zero-shot-classification", model=NLI_MODEL)
    return _nli_classifier


def predict_nli_stance(context_text, entity_text):
    """Candidate B: NOT a supervised stance model - a generic NLI model repurposed via 3
    explicit hypotheses ('the author supports/opposes/has no clear attitude toward TARGET'),
    picking whichever hypothesis has the highest entailment score. Documented explicitly as a
    zero-shot heuristic, not our own trained stance signal."""
    clf = get_nli_classifier()
    hyps = [
        NLI_HYPOTHESIS_TEMPLATES["positive"].format(target=entity_text),
        NLI_HYPOTHESIS_TEMPLATES["negative"].format(target=entity_text),
        NLI_HYPOTHESIS_TEMPLATES["neutral"].format(target=entity_text),
    ]
    hyp_to_stance = {hyps[0]: "positive", hyps[1]: "negative", hyps[2]: "neutral"}
    result = clf(context_text, hyps, hypothesis_template="{}", multi_label=False)
    scores = {hyp_to_stance[label]: score for label, score in zip(result["labels"], result["scores"])}
    best_label = max(scores, key=scores.get)
    return best_label, scores


def get_procon_model():
    global _procon_tokenizer, _procon_model
    if _procon_model is None:
        print(f"Loading PRO/CON stance classifier '{PROCON_STANCE_MODEL}'...")
        _procon_tokenizer = AutoTokenizer.from_pretrained(PROCON_STANCE_MODEL)
        _procon_model = AutoModelForSequenceClassification.from_pretrained(PROCON_STANCE_MODEL)
        _procon_model.eval()
    return _procon_tokenizer, _procon_model


def predict_procon_stance(context_text, entity_text):
    """Candidate C: NLP-Debater-Project/debertav3-stance-detection, a real PRO/CON stance
    model (IBM ArgKP-2023 topic-vs-argument), trained WITHOUT a neutral class. Per the model
    card's own usage example, predicted_class==1 -> PRO, ==0 -> CON (no id2label in
    config.json, so this mapping is hardcoded from the documented example, not guessed).
    Abstention rule (benchmark-only, NOT part of the model): if |P(PRO)-P(CON)| <
    PROCON_ABSTENTION_MARGIN (=0.15, fixed before looking at any gold label here) ->
    label 'neutral'; otherwise take the higher of PRO/CON. This margin was picked a priori
    as "close to a 50/50 split" and never adjusted against this pilot's gold labels, to avoid
    threshold leakage."""
    tokenizer, model = get_procon_model()
    text = f"Topic: {entity_text} [SEP] Argument: {context_text}"
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        probs = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)[0]
    p_con, p_pro = float(probs[0]), float(probs[1])
    if abs(p_pro - p_con) < PROCON_ABSTENTION_MARGIN:
        return "neutral", {"CON": p_con, "PRO": p_pro}
    return ("positive" if p_pro > p_con else "negative"), {"CON": p_con, "PRO": p_pro}


def build_masked_example(text, start, end, entity_group, stance_label):
    """Entity IDENTITY removed, entity TYPE + predicted ATTITUDE kept, e.g.
    "Trump is destroying American democracy" -> "[PERSON:NEG] is destroying American democracy"."""
    token = f"[{ENTITY_TYPE_TOKENS.get(entity_group, 'ENTITY')}:{MASK_STANCE_SUFFIX[stance_label]}]"
    return text[:start] + token + text[end:]


def collect_author_mentions(author, target_count=TARGET_MENTIONS_PER_AUTHOR):
    df = load_raw_data()
    _, _, test_data = split_leave_one_author(df, author)
    ner = get_ner_pipeline()
    mentions = []
    for row_idx, row in test_data.iterrows():
        if len(mentions) >= target_count:
            break
        text = str(row["text"])[:MAX_TEXT_CHARS]
        raw_entities = ner.extract_raw_entities(text)
        raw_entities = reconstruct_fragmented_entities(raw_entities, text)
        if not raw_entities:
            continue
        raw_entities = sorted(raw_entities, key=lambda e: e["start"])[:MAX_MENTIONS_PER_TEXT]
        for ent in raw_entities:
            context = get_local_context(text, ent["start"], ent["end"])
            stance_label, scores = predict_entity_stance(context, ent["text"])
            masked_example = build_masked_example(text, ent["start"], ent["end"], ent["entity_group"], stance_label)
            mentions.append({
                # Column order deliberately matches STANCE_ANNOTATION_GUIDE.md: the columns an
                # annotator needs to look at come first, scores/metadata are pushed to the end.
                "mention_id": f"{author}_{len(mentions) + 1:03d}",
                "author": author,
                "context": context,
                "target_entity": ent["text"],
                "entity_type": ent["entity_group"],
                "predicted_stance": stance_label,
                "gold_stance": "",       # fill by hand: positive / negative / neutral
                "error_category": "",    # fill using ERROR_CATEGORIES (default 'none' if correct)
                "annotator_notes": "",
                "narrative_name": row["narrative_name"],
                "row_index": int(row_idx),
                "original_text": text,
                "pos_score": round(scores.get("Positive", 0.0), 4),
                "neu_score": round(scores.get("Neutral", 0.0), 4),
                "neg_score": round(scores.get("Negative", 0.0), 4),
                "masked_example": masked_example,
            })
            if len(mentions) >= target_count:
                break
    return mentions


def build_validation_sample():
    os.makedirs(REPORT_DIR, exist_ok=True)
    all_mentions = []
    for author in AUTHORS:
        print(f"\n=== Collecting entity-stance mentions for {author} ===")
        mentions = collect_author_mentions(author)
        print(f"  collected {len(mentions)} mention(s)")
        all_mentions.extend(mentions)

    result_df = pd.DataFrame(all_mentions)
    result_df.to_csv(VALIDATION_SAMPLE_FILE, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(result_df)} mentions to {VALIDATION_SAMPLE_FILE}")
    print(f"See {ANNOTATION_GUIDE_FILE} for label definitions + edge-case rules before "
          "filling in 'gold_stance' (positive/negative/neutral) and 'error_category' "
          f"(one of: {ERROR_CATEGORIES}).")
    return result_df


def _safe_print(line):
    print(line.encode("ascii", errors="replace").decode("ascii"))


def show_qualitative(n_per_author=10):
    if not os.path.exists(VALIDATION_SAMPLE_FILE):
        raise SystemExit(f"{VALIDATION_SAMPLE_FILE} not found - run --build-sample first.")
    sample_df = pd.read_csv(VALIDATION_SAMPLE_FILE, keep_default_na=False)
    for author in AUTHORS:
        subset = sample_df[sample_df["author"] == author].head(n_per_author)
        _safe_print(f"\n=== {author} ({len(subset)} shown) ===")
        for _, r in subset.iterrows():
            _safe_print(
                f"[{r['mention_id']}] entity='{r['target_entity']}' ({r['entity_type']}) -> "
                f"{r['predicted_stance']} (pos={r['pos_score']} neu={r['neu_score']} neg={r['neg_score']})"
            )
            _safe_print(f"  context: {r['context']}")
            _safe_print(f"  masked : {r['masked_example']}")


def show_representative(n_per_label=5):
    """Prints n_per_label examples for EACH predicted_stance value (positive/negative/
    neutral), pre-annotation - purely so a reviewer can sanity-check the label definition
    being used before starting the manual pass. Does NOT touch gold_stance."""
    if not os.path.exists(VALIDATION_SAMPLE_FILE):
        raise SystemExit(f"{VALIDATION_SAMPLE_FILE} not found - run --build-sample first.")
    sample_df = pd.read_csv(VALIDATION_SAMPLE_FILE, keep_default_na=False)
    for label in ("positive", "negative", "neutral"):
        subset = sample_df[sample_df["predicted_stance"] == label].head(n_per_label)
        _safe_print(f"\n=== predicted_stance = {label} ({len(subset)} shown) ===")
        for _, r in subset.iterrows():
            _safe_print(
                f"[{r['mention_id']}] author={r['author']} entity='{r['target_entity']}' "
                f"({r['entity_type']}) (pos={r['pos_score']} neu={r['neu_score']} neg={r['neg_score']})"
            )
            _safe_print(f"  context: {r['context']}")


def build_pilot_sample(n_per_author=PILOT_SIZE_PER_AUTHOR, required_ids=REQUIRED_PILOT_IDS):
    """Selects a 30-mention pilot (10/author) from the already-built validation_sample.csv -
    does NOT change any predicted_stance value and does NOT fill gold_stance. required_ids
    are force-included (the suspicious cases flagged during the initial qualitative look);
    remaining slots per author are chosen to balance predicted_stance as evenly as possible
    (target ~n_per_author/3 per class), falling back to whatever's available if a class is
    short. Selection within a class is the first N rows in the original (deterministic)
    order - no randomness, so re-running reproduces the same pilot."""
    if not os.path.exists(VALIDATION_SAMPLE_FILE):
        raise SystemExit(f"{VALIDATION_SAMPLE_FILE} not found - run --build-sample first.")
    full_df = pd.read_csv(VALIDATION_SAMPLE_FILE, keep_default_na=False)

    base, extra = divmod(n_per_author, len(STANCE_CLASSES))
    target_per_class = {c: base + (1 if i < extra else 0) for i, c in enumerate(STANCE_CLASSES)}

    pilot_parts = []
    for author in AUTHORS:
        author_df = full_df[full_df["author"] == author]
        forced = author_df[author_df["mention_id"].isin(required_ids)]
        pool = author_df[~author_df["mention_id"].isin(forced["mention_id"])]

        forced_counts = forced["predicted_stance"].value_counts().to_dict()
        needed_per_class = {c: max(target_per_class[c] - forced_counts.get(c, 0), 0) for c in STANCE_CLASSES}

        chosen = [forced]
        for cls in STANCE_CLASSES:
            n_take = needed_per_class[cls]
            if n_take <= 0:
                continue
            take = pool[pool["predicted_stance"] == cls].head(n_take)
            chosen.append(take)
            pool = pool.drop(take.index)

        author_pilot = pd.concat(chosen)
        shortfall = n_per_author - len(author_pilot)
        if shortfall > 0:
            author_pilot = pd.concat([author_pilot, pool.head(shortfall)])
        pilot_parts.append(author_pilot.head(n_per_author))

    pilot_df = pd.concat(pilot_parts).reset_index(drop=True)
    pilot_df.to_csv(PILOT_SAMPLE_FILE, index=False, encoding="utf-8-sig")

    print(f"Saved {len(pilot_df)} mentions to {PILOT_SAMPLE_FILE}")
    for author in AUTHORS:
        counts = pilot_df[pilot_df["author"] == author]["predicted_stance"].value_counts().to_dict()
        print(f"  {author}: {counts}")
    missing_required = set(required_ids) - set(pilot_df["mention_id"])
    if missing_required:
        print(f"  WARNING: required id(s) not found in validation_sample.csv: {missing_required}")
    return pilot_df


def analyze_pilot():
    """Computes accuracy/confusion-matrix/error-category metrics against the pilot's
    gold_stance column - run this ONLY after gold_stance has been filled in by hand.
    Reads PILOT_ANNOTATED_FILE (a hand-labeled copy), NOT the blank PILOT_SAMPLE_FILE."""
    if not os.path.exists(PILOT_ANNOTATED_FILE):
        raise SystemExit(f"{PILOT_ANNOTATED_FILE} not found - save your annotated pilot there first.")
    pilot_df = pd.read_csv(PILOT_ANNOTATED_FILE, keep_default_na=False)
    pilot_df["gold_stance"] = pilot_df["gold_stance"].str.strip().str.lower()

    unlabeled = pilot_df[pilot_df["gold_stance"] == ""]
    labeled = pilot_df[pilot_df["gold_stance"] != ""]
    if unlabeled.shape[0] > 0:
        print(f"WARNING: {len(unlabeled)} row(s) still missing gold_stance - excluded below.")
    if labeled.empty:
        raise SystemExit("No gold_stance values filled in yet - nothing to analyze.")

    is_correct = labeled["predicted_stance"] == labeled["gold_stance"]

    print(f"\n1. Overall accuracy: {is_correct.mean():.3f} ({is_correct.sum()}/{len(labeled)})")

    print("\n2. Confusion matrix (rows=gold, cols=predicted):")
    print(pd.crosstab(labeled["gold_stance"], labeled["predicted_stance"], dropna=False))

    print("\n3. Accuracy by author:")
    for author, grp in labeled.groupby("author"):
        acc = (grp["predicted_stance"] == grp["gold_stance"]).mean()
        print(f"   {author}: {acc:.3f} ({(grp['predicted_stance'] == grp['gold_stance']).sum()}/{len(grp)})")

    print("\n4. Accuracy by predicted class (precision given that prediction):")
    for cls, grp in labeled.groupby("predicted_stance"):
        acc = (grp["predicted_stance"] == grp["gold_stance"]).mean()
        print(f"   predicted={cls}: {acc:.3f} ({(grp['predicted_stance'] == grp['gold_stance']).sum()}/{len(grp)})")

    print("\n5. Error-category breakdown (rows where predicted != gold):")
    errors = labeled[~is_correct]
    if len(errors) > 0:
        print(errors["error_category"].replace("", "(blank)").value_counts().to_string())
    else:
        print("   no errors")

    print("\n6. Negative-SENTENCE-sentiment vs negative-ENTITY-stance check:")
    pred_neg = labeled[labeled["predicted_stance"] == "negative"]
    over_neg = pred_neg[pred_neg["gold_stance"] != "negative"]
    print(f"   predicted=negative but gold!=negative: {len(over_neg)}/{len(pred_neg)} of predicted-negative rows")
    if len(over_neg) > 0:
        print(over_neg[["mention_id", "author", "target_entity", "gold_stance", "error_category"]].to_string(index=False))
    action_vs_entity_n = (labeled["error_category"] == "action_vs_entity").sum()
    print(f"   error_category='action_vs_entity' count (all labeled rows): {action_vs_entity_n}")

    print("\n7. Root-cause buckets of the errors "
          "(ABSA reasoning error vs insufficient context vs NER/entity extraction error):")
    if len(errors) > 0:
        buckets = errors["error_category"].map(ERROR_BUCKET_MAP)
        n_errors = len(errors)
        counts = buckets.value_counts()
        for bucket, n in counts.items():
            print(f"   {bucket}: {n}/{n_errors} of errors ({n / len(labeled):.1%} of all {len(labeled)} pilot rows)")
        print("\n   ...broken down by author:")
        for author, grp in errors.groupby("author"):
            grp_buckets = grp["error_category"].map(ERROR_BUCKET_MAP).value_counts().to_dict()
            print(f"   {author} ({len(grp)} error(s)): {grp_buckets}")
        print("\n   ...mention_ids per bucket:")
        for bucket in ("ner_entity_error", "insufficient_context", "absa_prediction_error"):
            ids = errors[buckets == bucket]["mention_id"].tolist()
            print(f"   {bucket}: {ids}")
    else:
        print("   no errors")
    return labeled


def build_context_variants(original_text, context_sentence, entity_text):
    """Builds the 3 context-width variants for the SAME target entity: current sentence only
    (the existing 'context' column), current + previous/next sentence, and the full post.
    Sentence boundaries reuse the same spaCy parse as get_local_context(); the current
    sentence is located by matching 'context_sentence' back into original_text (since the
    pilot CSV stores strings, not char offsets)."""
    ctx_stripped = context_sentence.strip()
    doc = get_nlp()(original_text)
    sents = list(doc.sents)

    target_idx = None
    for i, sent in enumerate(sents):
        if ctx_stripped and (ctx_stripped in sent.text or sent.text.strip() in ctx_stripped):
            target_idx = i
            break
    if target_idx is None:
        pos = original_text.find(ctx_stripped)
        if pos != -1:
            for i, sent in enumerate(sents):
                if sent.start_char <= pos < sent.end_char:
                    target_idx = i
                    break

    if target_idx is None:
        window_text = context_sentence  # couldn't locate sentence index - fall back, don't crash
    else:
        lo, hi = max(target_idx - 1, 0), min(target_idx + 1, len(sents) - 1)
        window_text = " ".join(s.text.strip() for s in sents[lo:hi + 1])

    return {
        "sentence": context_sentence,
        "window": window_text,
        "full": original_text,
    }


def run_context_width_experiment():
    """Pilot-only experiment (NOT training): for each of the 30 hand-labeled mentions, keeps
    the SAME target_entity fixed and re-runs the ABSA classifier with 3 context widths
    (current sentence / +-1 sentence window / full post), then compares accuracy against
    gold_stance for each. Purpose: decide whether widening context (cheap, no model swap)
    fixes the insufficient_context failure mode before considering a different stance method."""
    if not os.path.exists(PILOT_ANNOTATED_FILE):
        raise SystemExit(f"{PILOT_ANNOTATED_FILE} not found - save your annotated pilot there first.")
    pilot_df = pd.read_csv(PILOT_ANNOTATED_FILE, keep_default_na=False)
    pilot_df["gold_stance"] = pilot_df["gold_stance"].str.strip().str.lower()
    labeled = pilot_df[pilot_df["gold_stance"] != ""].copy()
    if labeled.empty:
        raise SystemExit("No gold_stance values filled in yet - nothing to run the experiment on.")

    rows_out = []
    for _, r in labeled.iterrows():
        entity = r["target_entity"]
        variants = build_context_variants(r["original_text"], r["context"], entity)
        pred_window, _ = predict_entity_stance(variants["window"], entity)
        pred_full, _ = predict_entity_stance(variants["full"][:MAX_TEXT_CHARS], entity)
        rows_out.append({
            "mention_id": r["mention_id"],
            "author": r["author"],
            "target_entity": entity,
            "gold_stance": r["gold_stance"],
            "error_category": r["error_category"],
            "pred_sentence": r["predicted_stance"],  # reuse - identical context, no need to recompute
            "correct_sentence": r["predicted_stance"] == r["gold_stance"],
            "pred_window": pred_window,
            "correct_window": pred_window == r["gold_stance"],
            "pred_full": pred_full,
            "correct_full": pred_full == r["gold_stance"],
        })

    out_df = pd.DataFrame(rows_out)
    os.makedirs(REPORT_DIR, exist_ok=True)
    out_df.to_csv(CONTEXT_EXPERIMENT_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved per-row comparison to {CONTEXT_EXPERIMENT_FILE}\n")

    print("Overall accuracy by context-width strategy:")
    for strategy in ("sentence", "window", "full"):
        col = f"correct_{strategy}"
        print(f"   {strategy:8s}: {out_df[col].mean():.3f} ({out_df[col].sum()}/{len(out_df)})")

    print("\nAccuracy by author x strategy:")
    for author, grp in out_df.groupby("author"):
        parts = ", ".join(f"{s}={grp[f'correct_{s}'].mean():.2f}" for s in ("sentence", "window", "full"))
        print(f"   {author}: {parts}")

    print("\nRows flipped WRONG -> RIGHT by widening context:")
    flips = out_df[~out_df["correct_sentence"] & (out_df["correct_window"] | out_df["correct_full"])]
    if len(flips) > 0:
        print(flips[["mention_id", "author", "gold_stance", "pred_sentence", "pred_window",
                      "pred_full", "error_category"]].to_string(index=False))
    else:
        print("   none")

    print("\nRows flipped RIGHT -> WRONG by widening context (new failure modes introduced):")
    regressions = out_df[out_df["correct_sentence"] & (~out_df["correct_window"] | ~out_df["correct_full"])]
    if len(regressions) > 0:
        print(regressions[["mention_id", "author", "gold_stance", "pred_sentence", "pred_window",
                            "pred_full", "error_category"]].to_string(index=False))
    else:
        print("   none")
    return out_df


FLAGGED_MENTION_IDS = (
    "IDF_023", "IDF_024", "BernieSanders_002", "BernieSanders_005", "BernieSanders_007",
    "MariaZakharova_039",
)


def _print_method_report(name, df):
    """Prints the full per-method report block requested for the mini-benchmark: overall
    accuracy, accuracy by author, accuracy by gold class, confusion matrix, neutral
    false-prediction count, and the two named failure-mode categories."""
    col = f"pred_{name}"
    is_correct = df[col] == df["gold_stance"]
    print(f"\n{'=' * 70}\n{name}\n{'=' * 70}")
    print(f"Overall accuracy: {is_correct.mean():.3f} ({is_correct.sum()}/{len(df)})")

    print("Accuracy by author:")
    for author, grp in df.groupby("author"):
        acc = (grp[col] == grp["gold_stance"]).mean()
        print(f"   {author}: {acc:.3f} ({(grp[col] == grp['gold_stance']).sum()}/{len(grp)})")

    print("Accuracy by gold class (recall per class):")
    for cls, grp in df.groupby("gold_stance"):
        acc = (grp[col] == grp["gold_stance"]).mean()
        print(f"   gold={cls}: {acc:.3f} ({(grp[col] == grp['gold_stance']).sum()}/{len(grp)})")

    print("Confusion matrix (rows=gold, cols=predicted):")
    print(pd.crosstab(df["gold_stance"], df[col], dropna=False))

    neutral_false = df[(df[col] == "neutral") & (df["gold_stance"] != "neutral")]
    print(f"Neutral false predictions (predicted neutral, gold != neutral): {len(neutral_false)}/{len(df)}")

    gold_neutral = df["gold_stance"] == "neutral"
    pred_neutral = df[col] == "neutral"
    tp = int((gold_neutral & pred_neutral).sum())
    neutral_precision = tp / pred_neutral.sum() if pred_neutral.sum() else float("nan")
    neutral_recall = tp / gold_neutral.sum() if gold_neutral.sum() else float("nan")
    print(f"Neutral precision: {neutral_precision:.3f} ({tp}/{pred_neutral.sum()})   "
          f"Neutral recall: {neutral_recall:.3f} ({tp}/{gold_neutral.sum()})")

    action_vs_entity_rows = df[df["error_category"] == "action_vs_entity"]
    n_fixed = (action_vs_entity_rows[col] == action_vs_entity_rows["gold_stance"]).sum()
    print(f"action_vs_entity rows correct: {n_fixed}/{len(action_vs_entity_rows)} "
          f"({action_vs_entity_rows['mention_id'].tolist()})")

    insuff_rows = df[df["error_category"] == "insufficient_context"]
    n_fixed_insuff = (insuff_rows[col] == insuff_rows["gold_stance"]).sum()
    print(f"insufficient_context rows correct: {n_fixed_insuff}/{len(insuff_rows)} "
          f"({insuff_rows['mention_id'].tolist()})")

    # Attribute each error to NER/entity-boundary upstream issues vs the stance model itself,
    # using the same ERROR_BUCKET_MAP used in analyze_pilot() - so a low accuracy number isn't
    # blamed on the stance model when the root cause is actually a bad entity span/type.
    wrong = df[df[col] != df["gold_stance"]].copy()
    wrong["bucket"] = wrong["error_category"].map(ERROR_BUCKET_MAP).fillna("absa_prediction_error")
    n_ner_caused = int((wrong["bucket"] == "ner_entity_error").sum())
    print(f"Of {len(wrong)} errors: {n_ner_caused} are NER/entity-boundary-caused "
          f"(not the stance model's fault), {len(wrong) - n_ner_caused} are stance-model errors.")

    flagged = df[df["mention_id"].isin(FLAGGED_MENTION_IDS)]
    print("Specifically flagged mention_ids (gold / predicted):")
    for _, r in flagged.iterrows():
        mark = "OK" if r[col] == r["gold_stance"] else "WRONG"
        print(f"   {r['mention_id']:20s} gold={r['gold_stance']:8s} pred={r[col]:8s} [{mark}]")


def run_stance_method_benchmark():
    """Mini-benchmark on the SAME 30 hand-labeled pilot rows (target entity fixed) comparing
    5 stance-extraction methods BEFORE deciding whether Experiment 22 has any usable signal:
      1. absa_sentence - the already-tested ABSA model, current-sentence context (baseline).
      2. absa_full     - same ABSA model, full-post context (reused from
                         context_width_experiment.csv if present, else recomputed).
      3. semeval       - Candidate A: krishnagarg09/stance-detection-semeval2016.
      4. nli           - Candidate B: zero-shot NLI w/ explicit target hypotheses.
      5. procon        - Candidate C: NLP-Debater-Project PRO/CON model + fixed abstention rule.
    NOT training. Saves the per-row comparison to STANCE_METHOD_BENCHMARK_FILE."""
    if not os.path.exists(PILOT_ANNOTATED_FILE):
        raise SystemExit(f"{PILOT_ANNOTATED_FILE} not found - save your annotated pilot there first.")
    pilot_df = pd.read_csv(PILOT_ANNOTATED_FILE, keep_default_na=False)
    pilot_df["gold_stance"] = pilot_df["gold_stance"].str.strip().str.lower()
    labeled = pilot_df[pilot_df["gold_stance"] != ""].copy()
    if labeled.empty:
        raise SystemExit("No gold_stance values filled in yet - nothing to benchmark.")

    absa_full_by_id = {}
    if os.path.exists(CONTEXT_EXPERIMENT_FILE):
        ctx_df = pd.read_csv(CONTEXT_EXPERIMENT_FILE, keep_default_na=False)
        absa_full_by_id = dict(zip(ctx_df["mention_id"], ctx_df["pred_full"]))

    rows_out = []
    for _, r in labeled.iterrows():
        entity = r["target_entity"]
        sentence_ctx = r["context"]
        full_ctx = str(r["original_text"])[:MAX_TEXT_CHARS]

        pred_absa_full = absa_full_by_id.get(r["mention_id"])
        if pred_absa_full is None:
            pred_absa_full, _ = predict_entity_stance(full_ctx, entity)
        pred_semeval, _ = predict_semeval_stance(sentence_ctx, entity)
        pred_nli, _ = predict_nli_stance(sentence_ctx, entity)
        pred_procon, _ = predict_procon_stance(sentence_ctx, entity)

        rows_out.append({
            "mention_id": r["mention_id"],
            "author": r["author"],
            "target_entity": entity,
            "context": sentence_ctx,
            "gold_stance": r["gold_stance"],
            "error_category": r["error_category"],
            "pred_absa_sentence": r["predicted_stance"],
            "pred_absa_full": pred_absa_full,
            "pred_semeval": pred_semeval,
            "pred_nli": pred_nli,
            "pred_procon": pred_procon,
        })

    out_df = pd.DataFrame(rows_out)
    os.makedirs(REPORT_DIR, exist_ok=True)
    out_df.to_csv(STANCE_METHOD_BENCHMARK_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved per-row comparison to {STANCE_METHOD_BENCHMARK_FILE}")

    method_names = ("absa_sentence", "absa_full", "semeval", "nli", "procon")
    for name in method_names:
        _print_method_report(name, out_df)

    print(f"\n{'=' * 70}\nFIXED vs REGRESSED relative to absa_sentence baseline\n{'=' * 70}")
    baseline_correct = out_df["pred_absa_sentence"] == out_df["gold_stance"]
    for name in method_names[1:]:
        col = f"pred_{name}"
        method_correct = out_df[col] == out_df["gold_stance"]
        fixed = out_df[~baseline_correct & method_correct]
        regressed = out_df[baseline_correct & ~method_correct]
        print(f"\n{name}: fixed {len(fixed)} baseline errors, introduced {len(regressed)} new errors")
        if len(fixed) > 0:
            print("  FIXED:", fixed[["mention_id", "gold_stance", "pred_absa_sentence", col]].to_dict("records"))
        if len(regressed) > 0:
            print("  REGRESSED:", regressed[["mention_id", "gold_stance", "pred_absa_sentence", col]].to_dict("records"))

    print(f"\n{'=' * 70}\nTARGET-SENSITIVITY CHECK\n"
          f"(same sentence, >=2 distinct targets - does each method vary its prediction the way "
          f"gold does, or output the same label regardless of target - i.e. sentence-sentiment "
          f"in disguise?)\n{'=' * 70}")
    for ctx_text, grp in out_df.groupby("context"):
        if grp["target_entity"].nunique() < 2:
            continue
        print(f"\nContext: {ctx_text!r}")
        print(f"  gold labels differ across targets: {grp['gold_stance'].nunique() > 1}")
        cols = ["mention_id", "target_entity", "gold_stance"] + [f"pred_{n}" for n in method_names]
        print(grp[cols].to_string(index=False))
        for name in method_names:
            col = f"pred_{name}"
            print(f"  {name}: distinct predictions across targets = {grp[col].nunique()} "
                  f"(gold has {grp['gold_stance'].nunique()} distinct values)")

    print(f"\n{'=' * 70}\nGATE SUMMARY (need 70-75%+, reasonable across all 3 authors, no new "
          f"systematic failure mode)\n{'=' * 70}")
    for name in method_names:
        col = f"pred_{name}"
        overall = (out_df[col] == out_df["gold_stance"]).mean()
        by_author = {a: (g[col] == g["gold_stance"]).mean() for a, g in out_df.groupby("author")}
        min_author = min(by_author.values())
        print(f"   {name:14s} overall={overall:.3f}  by_author={ {k: round(v, 2) for k, v in by_author.items()} }  "
              f"min_author={min_author:.2f}")
    return out_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-sample", action="store_true")
    parser.add_argument("--show-qualitative", action="store_true")
    parser.add_argument("--show-representative", action="store_true")
    parser.add_argument("--build-pilot", action="store_true")
    parser.add_argument("--analyze-pilot", action="store_true")
    parser.add_argument("--context-experiment", action="store_true")
    parser.add_argument("--stance-benchmark", action="store_true")
    args = parser.parse_args()

    ran_something = False
    if args.build_sample:
        build_validation_sample()
        ran_something = True
    if args.show_qualitative:
        show_qualitative()
        ran_something = True
    if args.show_representative:
        show_representative()
        ran_something = True
    if args.build_pilot:
        build_pilot_sample()
        ran_something = True
    if args.analyze_pilot:
        analyze_pilot()
        ran_something = True
    if args.context_experiment:
        run_context_width_experiment()
        ran_something = True
    if args.stance_benchmark:
        run_stance_method_benchmark()
        ran_something = True
    if not ran_something:
        parser.print_help()

# Narrative list
NARRATIVES = [
    "Zionist", "Resistance", "Western",
    "Russian", "Ukrainian",
    "Right-wing", "Left-wing"
]

# Dimensions
NUM_NARRATIVES = len(NARRATIVES)    # number of narratives
NUM_TOPICS = 500                    # maximum number of topics
NUM_EMOTIONS = 6                    # number of emotions

# Hyperparameters
LEARNING_RATE = 0.001   # step size
BATCH_SIZE = 16         # batch size
EPOCHS = 20             # number of iterations over the data

# Narrative-to-index mapping
NARRATIVE_TO_IDX = {name: i for i, name in enumerate(NARRATIVES)}
IDX_TO_NARRATIVE = {i: name for i, name in enumerate(NARRATIVES)}

# --- Model selection for training (train.py) ---
# Can be overridden via --model on the command line. Options:
#   "baseline_fusion" - the existing NarrativeDetector (fusion.py), unchanged
#   "sbert_only"       - Baseline 1: frozen SBERT embedding -> MLP only
#   "hybrid"           - HybridNarrativeDetector: SBERT + all engineered features
MODEL_TYPE = "baseline_fusion"
MODEL_TYPES = ("baseline_fusion", "sbert_only", "hybrid")

# --- Train/Validation/Test split ratios ---
# Shared across all three model types (same random_state, same split logic) to
# ensure a fair research comparison - every model is trained/evaluated on the exact same samples.
VAL_SIZE = 0.15
TEST_SIZE = 0.15

# --- BERTopic model versions (see stance.py's TopicAnalysisPipeline) ---
# TOPIC_MODEL_PATH_LEGACY: the PINNED, frozen BERTopic model that the already-trained
#   classification checkpoints (models/best_narrative_model_hybrid.pth [baseline_fusion],
#   models/best_model_hybrid_architecture.pth [hybrid]) were trained against, via
#   TopicStanceLayer's nn.Embedding indexed directly by topic_id. Saved WITHOUT
#   save_ctfidf=True (no fitted vectorizer_model/c_tf_idf_), so approximate_distribution()
#   (soft/multi-topic scoring) does NOT work on this version - only the hard topic_id from
#   .transform() is available. Do NOT overwrite this path / do NOT re-run train_topics.py
#   pointed at this path - it must stay byte-identical to what those checkpoints saw during
#   training (git commit bb44b09), or their learned topic_id -> narrative associations
#   silently become meaningless. Default for TopicAnalysisPipeline(), used unchanged by
#   fusion.py's NarrativeDetector/HybridNarrativeDetector (backward compatible).
# TOPIC_MODEL_PATH_SOFT: a SEPARATE, newer BERTopic re-fit (same 4 datasets), saved WITH
#   save_ctfidf=True, so it DOES support approximate_distribution() / soft multi-topic
#   scoring (see stance.py's get_topic_distribution/process_text_with_distribution and
#   analyze_soft_topics.py). Topic ids in this version are NOT comparable to
#   TOPIC_MODEL_PATH_LEGACY's ids (BERTopic topic numbering is not stable across re-fits) -
#   this version is not yet used by any classification checkpoint. train_topics.py's
#   default local-save target is this path, so future re-fits never clobber the legacy
#   pinned model above.
TOPIC_MODEL_PATH_LEGACY = "models/saved_topic_model"
TOPIC_MODEL_PATH_SOFT = "models/saved_topic_model_soft_v2"
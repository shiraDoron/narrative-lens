NARRATIVES = [
    "Zionist", "Resistance", "Western",
    "Russian", "Ukrainian",
    "Right-wing", "Left-wing"
]

# Dimensions
NUM_NARRATIVES = len(NARRATIVES)
NUM_TOPICS = 500
NUM_EMOTIONS = 6

# Hyperparameters
LEARNING_RATE = 0.001
BATCH_SIZE = 16
EPOCHS = 20

NARRATIVE_TO_IDX = {name: i for i, name in enumerate(NARRATIVES)}
IDX_TO_NARRATIVE = {i: name for i, name in enumerate(NARRATIVES)}

# Model selection for training (--model overrides this; same options as MODEL_TYPES).
MODEL_TYPE = "baseline_fusion"
MODEL_TYPES = ("baseline_fusion", "sbert_only", "hybrid")

# Split ratios shared by all model types, so every model sees identical samples.
VAL_SIZE = 0.15
TEST_SIZE = 0.15

# BERTopic model versions (see stance.py's TopicAnalysisPipeline):
# LEGACY is the pinned model the trained checkpoints depend on (topic_id-indexed
# embeddings). It must stay byte-identical: no re-fit onto this path, no overwrite.
# It has no fitted ctfidf, so only hard topic_id works here, not soft scoring.
# SOFT is a separate re-fit with ctfidf saved, so soft scoring works; its topic ids
# are not comparable to LEGACY's, no checkpoint uses it yet, and re-fits target it.
TOPIC_MODEL_PATH_LEGACY = "models/saved_topic_model"
TOPIC_MODEL_PATH_SOFT = "models/saved_topic_model_soft_v2"
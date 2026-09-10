"""Tests for narrative_lens.train_topics's CLI: importing the module and running --help must
NEVER trigger a real BERTopic fit (see train_topics.py's own `if __name__ == "__main__":` guard
and `_parse_args()`). Process-level checks use subprocess (to genuinely exercise `python -m
narrative_lens.train_topics`); argparse value-parsing is checked directly (fast, no subprocess)."""

import subprocess
import sys

from narrative_lens.train_topics import _parse_args

# Only ever printed once build_and_save_topics() actually starts running - their absence in
# stdout is the load-bearing assertion that no training happened.
_TRAINING_STARTED_MARKERS = ("בונה אשכולות נושאים", "טוען את קבצי הנתונים")


def test_import_does_not_start_training():
    result = subprocess.run(
        [sys.executable, "-c", "import narrative_lens.train_topics"],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stderr
    for marker in _TRAINING_STARTED_MARKERS:
        assert marker not in result.stdout


def test_help_prints_usage_and_exits_without_training():
    result = subprocess.run(
        [sys.executable, "-m", "narrative_lens.train_topics", "--help"],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout
    for marker in _TRAINING_STARTED_MARKERS:
        assert marker not in result.stdout


def test_parse_args_defaults_preserve_original_behavior(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["train_topics.py"])
    args = _parse_args()
    assert args.config is None
    assert args.seed is None
    assert args.min_topic_size is None
    assert args.embedding_model is None
    assert args.output_path is None


def test_parse_args_reads_seed_and_min_topic_size(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["train_topics.py", "--seed", "7", "--min-topic-size", "15"])
    args = _parse_args()
    assert args.seed == 7
    assert args.min_topic_size == 15


def test_parse_args_config_file_supplies_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["train_topics.py", "--config", "configs/topic_model.yaml"])
    args = _parse_args()
    assert args.seed == 42
    assert args.min_topic_size == 10
    assert args.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"


def test_parse_args_cli_flag_overrides_config_file(monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["train_topics.py", "--config", "configs/topic_model.yaml", "--seed", "99"],
    )
    args = _parse_args()
    assert args.seed == 99            # explicit CLI flag wins over the config file
    assert args.min_topic_size == 10  # still comes from the config file

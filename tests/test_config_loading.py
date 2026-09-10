"""Tests for narrative_lens.utils.config_loader.load_config() and basic sanity checks on
narrative_lens.config's constants. No heavy model loading (no transformers/BERTopic/torch
checkpoints) - just YAML parsing and constant consistency."""

import pytest

from narrative_lens import config
from narrative_lens.utils.config_loader import load_config


def test_load_config_returns_empty_dict_for_none():
    assert load_config(None) == {}


def test_load_config_loads_default_yaml():
    cfg = load_config("configs/default.yaml")
    assert cfg["model"] == "baseline_fusion"
    assert cfg["seed"] == 42
    assert cfg["epochs"] == 20


def test_load_config_raises_for_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("configs/this_file_does_not_exist.yaml")


def test_config_narratives_and_num_narratives_consistent():
    assert config.NUM_NARRATIVES == len(config.NARRATIVES)


def test_config_model_type_is_a_valid_model_type():
    assert config.MODEL_TYPE in config.MODEL_TYPES

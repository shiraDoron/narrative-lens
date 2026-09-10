"""Minimal YAML config loader for the configs/ directory.

Intentionally tiny: reads a YAML file into a plain dict, nothing more. No schema validation, no
merging/inheritance beyond a single optional base file - this project's configs/ are small and
flat (see configs/README.md), so a heavier config framework is not warranted.
"""
from __future__ import annotations

import os

import yaml


def load_config(path: str | None) -> dict:
    """Loads a YAML config file into a dict.

    Returns an empty dict if `path` is None (so callers can do
    `parser.add_argument(..., default=config.get("key", existing_default))` unconditionally,
    without a separate "was --config given" branch).

    Raises FileNotFoundError with a clear message if `path` is given but does not exist, so a
    typo in --config fails loudly instead of silently falling back to defaults.
    """
    if path is None:
        return {}
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}

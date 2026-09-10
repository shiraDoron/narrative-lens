"""Centralized RNG seeding for reproducibility.

Seeds Python's `random`, NumPy, and PyTorch's global RNG state (CPU and CUDA if available). This
is independent of - and does NOT replace - the hardcoded `random_state=42` already used at every
`train_test_split()` call site in `train.py`'s split functions (that logic is deliberately left
untouched; it is extensively validated as leak-free, see `verify_no_leakage()`). This module only
adds determinism for things that previously had NONE at all: model weight initialization and
DataLoader/batch shuffling order.
"""
from __future__ import annotations

import random

import numpy as np
import torch


def set_all_seeds(seed: int = 42) -> None:
    """Seeds Python's `random`, NumPy, and PyTorch (CPU + CUDA) global RNGs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

"""Reproducibility metadata: capture the git commit hash and write a per-run metadata JSON
alongside a run's outputs, so every result can later be traced back to the exact code version,
config, seed, and command-line arguments that produced it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def get_git_commit_hash() -> str:
    """Returns the current git commit hash (short + dirty-flag suffix), or "unknown" if this is
    not a git checkout / git is unavailable (e.g. a plain source download)."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown"

    try:
        dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
        ).decode().strip())
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        dirty = False

    return f"{commit}-dirty" if dirty else commit


def write_run_metadata(output_path: str, **fields) -> None:
    """Writes a JSON file at `output_path` (parent directories created if needed) capturing:
    - `git_commit`: output of get_git_commit_hash()
    - `timestamp_utc`: ISO-8601 UTC timestamp of when this was written
    - `python_version`: sys.version
    - any additional `**fields` the caller passes (e.g. config path, seed, CLI args, dataset
      paths, resulting metrics, output model/checkpoint path).
    """
    metadata = {
        "git_commit": get_git_commit_hash(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        **fields,
    }
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)

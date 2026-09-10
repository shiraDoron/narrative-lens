"""Tests for narrative_lens.train's leakage-safety checks (verify_no_leakage) and the
Leave-One-Author-Out split (split_leave_one_author). Uses tiny synthetic DataFrames only -
no real dataset loading, no model training."""

import pandas as pd
import pytest

from narrative_lens.train import split_leave_one_author, verify_no_leakage


def _make_synthetic_df():
    rows = []
    authors = ["AccountA", "AccountB", "AccountC", "AccountD"]
    narratives = ["Western", "Russian", "Ukrainian", "Zionist"]
    for author, narrative in zip(authors, narratives):
        for i in range(15):
            rows.append({
                "text": f"{author} sample text number {i}",
                "author_source": author,
                "narrative_name": narrative,
            })
    return pd.DataFrame(rows)


def test_verify_no_leakage_passes_when_disjoint():
    train_data = pd.DataFrame({"author_source": ["A", "A", "B"]})
    val_data = pd.DataFrame({"author_source": ["A", "B"]})
    test_data = pd.DataFrame({"author_source": ["C", "C"]})
    verify_no_leakage(train_data, val_data, test_data, key_col="author_source")  # should not raise


def test_verify_no_leakage_raises_on_overlap():
    train_data = pd.DataFrame({"author_source": ["A", "C"]})
    val_data = pd.DataFrame({"author_source": ["B"]})
    test_data = pd.DataFrame({"author_source": ["C", "D"]})
    with pytest.raises(AssertionError):
        verify_no_leakage(train_data, val_data, test_data, key_col="author_source")


def test_split_leave_one_author_isolates_held_out_author():
    df = _make_synthetic_df()
    train_data, val_data, test_data = split_leave_one_author(df, held_out_author="AccountA")

    assert set(test_data["author_source"].unique()) == {"AccountA"}
    assert "AccountA" not in set(train_data["author_source"].unique())
    assert "AccountA" not in set(val_data["author_source"].unique())
    # No leakage between test and train/val (re-verified explicitly, mirroring the function's
    # own internal call to verify_no_leakage).
    verify_no_leakage(train_data, val_data, test_data, key_col="author_source")


def test_split_leave_one_author_rejects_synthetic_author():
    df = _make_synthetic_df()
    with pytest.raises(ValueError):
        split_leave_one_author(df, held_out_author="whatever_synthetic")


def test_split_leave_one_author_rejects_unknown_author():
    df = _make_synthetic_df()
    with pytest.raises(ValueError):
        split_leave_one_author(df, held_out_author="NotARealAccount")

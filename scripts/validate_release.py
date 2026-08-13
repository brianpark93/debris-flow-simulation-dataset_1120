"""Validate the released data, metadata, and benchmark split."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "simulation_summary_github.csv"
DICTIONARY_PATH = ROOT / "metadata" / "data_dictionary.csv"
SPLIT_PATH = ROOT / "metadata" / "benchmark_split.csv"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    dictionary = pd.read_csv(DICTIONARY_PATH)
    split = pd.read_csv(SPLIT_PATH)

    expected_columns = dictionary["column"].tolist()
    assert dictionary["column"].is_unique, "Dictionary contains duplicate column definitions."
    assert set(df.columns) == set(expected_columns), "Dataset schema differs from dictionary."
    assert len(df) == 1119, f"Expected 1,119 rows, found {len(df):,}."
    assert not df.isna().any().any(), "Dataset contains missing values."
    assert not df.duplicated().any(), "Dataset contains duplicate rows."
    assert np.isfinite(df.to_numpy(dtype=float)).all(), "Dataset contains non-finite values."

    assert len(split) == len(df), "Split does not cover every row exactly once."
    assert split["row_index"].tolist() == list(range(len(df)))
    assert split["record_id"].is_unique
    assert set(split["split"]) == {"train", "test"}
    assert (split["split"] == "train").sum() == 895
    assert (split["split"] == "test").sum() == 224
    assert split.loc[split["split"] == "test", "cv_fold"].isna().all()
    train_folds = split.loc[split["split"] == "train", "cv_fold"].dropna().astype(int)
    assert set(train_folds) == set(range(5))

    print("Release validation passed:")
    print(f"  rows: {len(df):,}")
    print(f"  columns: {df.shape[1]}")
    print("  missing values: 0")
    print("  duplicate rows: 0")
    print("  split: 895 train / 224 test")


if __name__ == "__main__":
    main()

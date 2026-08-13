"""Generate the fixed benchmark split and descriptive statistics."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, train_test_split


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "simulation_summary_github.csv"
METADATA_DIR = ROOT / "metadata"
SPLIT_PATH = METADATA_DIR / "benchmark_split.csv"
STATS_PATH = METADATA_DIR / "dataset_statistics.csv"
SEED = 42
TEST_SIZE = 0.20


def generated_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(DATA_PATH)
    indices = np.arange(len(df))
    train_idx, test_idx = train_test_split(
        indices, test_size=TEST_SIZE, random_state=SEED, shuffle=True
    )

    split = pd.DataFrame(
        {
            "row_index": indices,
            "record_id": [f"DFTT-{i + 1:04d}" for i in indices],
            "split": "train",
            "cv_fold": pd.Series([pd.NA] * len(df), dtype="Int64"),
        }
    )
    split.loc[test_idx, "split"] = "test"

    kfold = KFold(n_splits=5, shuffle=True, random_state=SEED)
    for fold, (_, validation_positions) in enumerate(kfold.split(train_idx)):
        split.loc[train_idx[validation_positions], "cv_fold"] = fold

    stats = (
        df.describe(percentiles=[0.25, 0.5, 0.75])
        .T.reset_index(names="column")
        .rename(columns={"50%": "median"})
    )
    stats["missing"] = df.isna().sum().reindex(stats["column"]).to_numpy()
    return split, stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="Fail if committed metadata is stale."
    )
    args = parser.parse_args()
    split, stats = generated_tables()

    if args.check:
        expected_split = pd.read_csv(SPLIT_PATH, dtype={"cv_fold": "Int64"})
        expected_stats = pd.read_csv(STATS_PATH)
        pd.testing.assert_frame_equal(expected_split, split, check_dtype=False)
        pd.testing.assert_frame_equal(
            expected_stats, stats, check_dtype=False, rtol=1e-12, atol=1e-12
        )
        print("Committed metadata matches the generator.")
        return

    METADATA_DIR.mkdir(exist_ok=True)
    split.to_csv(SPLIT_PATH, index=False)
    stats.to_csv(STATS_PATH, index=False)
    print(f"Wrote {SPLIT_PATH.relative_to(ROOT)}")
    print(f"Wrote {STATS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

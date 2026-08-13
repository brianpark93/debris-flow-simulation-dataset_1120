"""Run reproducible baselines on the fixed train–test split."""

from __future__ import annotations

import os
from pathlib import Path

# Limit native linear-algebra libraries before importing NumPy/scikit-learn.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "simulation_summary_github.csv"
SPLIT_PATH = ROOT / "metadata" / "benchmark_split.csv"
RESULTS_DIR = ROOT / "results"
RESULTS_PATH = RESULTS_DIR / "baseline_metrics.csv"
SEED = 42

PRE_EVENT = ["volume_m3", "slope_deg", "potential_energy_MJ"]
IMPACT = [
    "impact_duration_s",
    "sleout_energy_max_J",
    "rcforce_force_max_N",
    "rcforce_impulse_Ns",
]
TARGETS = ["plastic_energy_MJ_front", "plastic_energy_MJ_rear"]
TASKS = {
    "pre_event": PRE_EVENT,
    "descriptor_assisted": PRE_EVENT + IMPACT,
}


def models() -> dict[str, object]:
    return {
        "Linear": make_pipeline(StandardScaler(), LinearRegression()),
        "RandomForest": RandomForestRegressor(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            random_state=SEED,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=250,
            learning_rate=0.05,
            max_depth=3,
            random_state=SEED,
        ),
        "SVR": make_pipeline(StandardScaler(), SVR(C=10.0, epsilon=0.1, kernel="rbf")),
        "MLP": make_pipeline(
            StandardScaler(),
            MLPRegressor(
                hidden_layer_sizes=(128, 128, 64),
                activation="relu",
                solver="adam",
                alpha=1e-4,
                batch_size=32,
                learning_rate_init=1e-3,
                max_iter=4000,
                random_state=SEED,
            ),
        ),
    }


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    split = pd.read_csv(SPLIT_PATH)
    train_mask = split["split"].eq("train").to_numpy()
    test_mask = split["split"].eq("test").to_numpy()
    rows: list[dict[str, object]] = []

    for task_name, features in TASKS.items():
        x_train = df.loc[train_mask, features]
        x_test = df.loc[test_mask, features]
        for target in TARGETS:
            y_train = df.loc[train_mask, target]
            y_test = df.loc[test_mask, target]
            for model_name, model in models().items():
                model.fit(x_train, y_train)
                prediction = model.predict(x_test)
                rows.append(
                    {
                        "task": task_name,
                        "model": model_name,
                        "target": target,
                        "n_train": int(train_mask.sum()),
                        "n_test": int(test_mask.sum()),
                        "n_features": len(features),
                        "r2": r2_score(y_test, prediction),
                        "mae_MJ": mean_absolute_error(y_test, prediction),
                        "rmse_MJ": np.sqrt(mean_squared_error(y_test, prediction)),
                        "seed": SEED,
                    }
                )

    results = pd.DataFrame(rows).sort_values(["task", "target", "model"])
    RESULTS_DIR.mkdir(exist_ok=True)
    results.to_csv(RESULTS_PATH, index=False, float_format="%.10f")
    print(results.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
    print(f"\nWrote {RESULTS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

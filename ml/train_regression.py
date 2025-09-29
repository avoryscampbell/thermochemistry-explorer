# ml/train_regression.py
"""
Train a regression model to predict ΔG (or another continuous target)
from reaction strings.

Usage:
    python -m ml.train_regression data/processed/delta_g.csv \
        --target-column delta_g \
        --out models/delta_g_rf.pkl \
        --cv 5 --test-size 0.2

Assumptions:
- CSV has a 'reaction' column and a numeric target column (default: 'delta_g').
- Features are generated from ml.features.vectorize(reactions).
- Model factory and save/load helpers live in ml.models.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold, cross_val_score, train_test_split

from .features import vectorize
from .models import make_regressor, save_model


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Train a regression model to predict ΔG (or another numeric target) from reaction strings."
    )
    p.add_argument(
        "csv_path",
        type=str,
        help="Path to input CSV with columns: reaction,<target>",
    )
    p.add_argument(
        "--target-column",
        type=str,
        default="delta_g",
        help="Name of the numeric target column in the CSV (default: delta_g).",
    )
    p.add_argument(
        "--out",
        type=str,
        default="models/delta_g_rf.pkl",
        help="Where to save the trained model (default: models/delta_g_rf.pkl).",
    )
    p.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Holdout fraction for the train/test split (default: 0.2).",
    )
    p.add_argument(
        "--cv",
        type=int,
        default=5,
        help="Number of CV folds for cross-validation MAE (default: 5).",
    )
    p.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    return p.parse_args()


def _load_dataset(csv_path: Path, target_col: str) -> Tuple[list[str], np.ndarray]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Basic schema checks
    if "reaction" not in df.columns:
        raise KeyError("CSV must contain a 'reaction' column.")
    if target_col not in df.columns:
        raise KeyError(f"CSV must contain the target column '{target_col}'.")

    # Drop rows with missing values in the required columns
    df = df.dropna(subset=["reaction", target_col])

    # Ensure numeric target
    try:
        y = pd.to_numeric(df[target_col], errors="raise").to_numpy()
    except Exception as e:
        raise ValueError(
            f"Target column '{target_col}' must be numeric. "
            f"Consider cleaning the CSV. Original error: {e}"
        )

    reactions = df["reaction"].astype(str).tolist()
    return reactions, y


def main() -> None:
    args = _parse_args()

    csv_path = Path(args.csv_path)
    out_path = Path(args.out)

    print("=== Training Regression Model ===")
    print(f"CSV:            {csv_path}")
    print(f"Target column:  {args.target_column}")
    print(f"Output model:   {out_path}")
    print(f"Test size:      {args.test_size}")
    print(f"CV folds:       {args.cv}")
    print(f"Random state:   {args.random_state}")

    # 1) Load data
    reactions, y = _load_dataset(csv_path, args.target_column)

    if len(reactions) < 5:
        print(
            f"[warn] Very small dataset ({len(reactions)} rows). "
            "Results will be unstable; consider adding more rows."
        )

    # 2) Vectorize features
    X, feature_names = vectorize(reactions)
    print(f"Samples: {X.shape[0]}  Features: {X.shape[1]}")

    # 3) Cross-validation MAE (negative scores in sklearn -> take abs)
    cv = max(2, int(args.cv))
    kf = KFold(n_splits=cv, shuffle=True, random_state=args.random_state)
    model_for_cv = make_regressor()
    cv_scores = cross_val_score(
        model_for_cv, X, y, cv=kf, scoring="neg_mean_absolute_error", n_jobs=None
    )
    cv_mae = np.abs(cv_scores)
    print(f"CV MAE per fold (kJ/mol): {np.round(cv_mae, 3).tolist()}")
    print(f"CV MAE mean ± std (kJ/mol): {cv_mae.mean():.3f} ± {cv_mae.std():.3f}")

    # 4) Train/test split report
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )
    model = make_regressor()
    model.fit(X_tr, y_tr)
    y_pred = model.predict(X_te)
    test_mae = mean_absolute_error(y_te, y_pred)
    print(f"Holdout Test MAE (kJ/mol): {test_mae:.3f}")

    # 5) Save model
    save_model(model, out_path)
    print(f"[ok] Model saved → {out_path}")

    # 6) Optionally, save a tiny model card alongside the artifact
    try:
        card_path = out_path.with_suffix(".json")
        import json  # local import to avoid hard dependency at module level

        card = {
            "artifact": str(out_path),
            "target": args.target_column,
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "features": feature_names,
            "cv_folds": cv,
            "cv_mae_mean": float(cv_mae.mean()),
            "cv_mae_std": float(cv_mae.std()),
            "test_mae": float(test_mae),
            "random_state": args.random_state,
        }
        card_path.parent.mkdir(parents=True, exist_ok=True)
        with card_path.open("w") as f:
            json.dump(card, f, indent=2)
        print(f"[ok] Model card saved → {card_path}")
    except Exception as e:
        print(f"[warn] Could not write model card: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[error] {exc}")
        sys.exit(1)


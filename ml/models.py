# ml/models.py
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import joblib
from pathlib import Path
from typing import Any

def make_regressor() -> RandomForestRegressor:
    return RandomForestRegressor(n_estimators=300, random_state=42)

def make_classifier() -> RandomForestClassifier:
    return RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42)

def save_model(model: Any, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)

def load_model(path: str | Path) -> Any:
    return joblib.load(path)


# ml/infer.py
from .features import vectorize
from .models import load_model

def predict_delta_g(model_path: str, reaction: str) -> float:
    model = load_model(model_path)
    X, _ = vectorize([reaction])
    return float(model.predict(X)[0])

def predict_spontaneous(model_path: str, reaction: str) -> bool:
    model = load_model(model_path)
    X, _ = vectorize([reaction])
    return bool(model.predict(X)[0])


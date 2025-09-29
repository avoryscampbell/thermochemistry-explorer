# ml/train_classifier.py
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from .features import vectorize
from .models import make_classifier, save_model

def train(csv_path: str, out_path: str = "models/spont_rf.pkl"):
    df = pd.read_csv(csv_path)  # expects: reaction, label (1 if ΔG<0 else 0)
    X, _ = vectorize(df["reaction"].tolist())
    y = df["label"].astype(int).values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = make_classifier().fit(Xtr, ytr)
    f1 = f1_score(yte, model.predict(Xte))
    print(f"Spontaneity RF F1: {f1:.3f}")
    save_model(model, out_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m ml.train_classifier data/processed/spont.csv")
        sys.exit(1)
    train(sys.argv[1])


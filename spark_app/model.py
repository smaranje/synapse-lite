"""
Dummy helper functions that imitate a real ML workflow
so the streaming job can run end-to-end without a
trained model or SHAP installed.
"""

import random
from typing import List, Tuple

# ------------------------------------------------------------------ #
# 1. “Load” a model (stub)
# ------------------------------------------------------------------ #
def load_model(path: str | None = None):
    """
    Pretends to load a trained model from `path`.
    You can later swap this for joblib / pickle.
    """
    print(f"[model] Dummy model loaded from {path or '<memory>'}")
    return None                      # placeholder “model” object


# ------------------------------------------------------------------ #
# 2. Pre-process a Pandas DataFrame -> (X, feature_names)
# ------------------------------------------------------------------ #
def preprocess_features(pdf) -> Tuple[list[list[float]], List[str]]:
    """
    Very small feature set for the demo:
      • feature_amount
      • feature_tx_count_daily
    Converts the DataFrame rows to a plain Python list of lists.
    """
    feat_names = ["feature_amount", "feature_tx_count_daily"]

    # Guarantee the columns exist; fall back to 0
    for col in feat_names:
        if col not in pdf.columns:
            pdf[col] = 0.0

    X = pdf[feat_names].values.tolist()
    return X, feat_names


# ------------------------------------------------------------------ #
# 3. Explain a prediction (stub SHAP-style output)
# ------------------------------------------------------------------ #
def explain_prediction(
    model, X: list[list[float]], feature_names: List[str]
) -> list[list[float]]:
    """
    Returns a list of “SHAP values” (random numbers)
    matching the shape of X.
    """
    shap_vals: list[list[float]] = []
    for _ in X:
        shap_vals.append([random.uniform(-0.2, 0.2) for _ in feature_names])
    return shap_vals


# ------------------------------------------------------------------ #
# 4. Convenience single-row scoring helpers (optional)
# ------------------------------------------------------------------ #
def predict_fraud_score(features: dict) -> float:
    """
    Simple heuristic:
      – low amount + many daily tx → high score
    """
    amt   = float(features.get("feature_amount", 0))
    freq  = int(features.get("feature_tx_count_daily", 0))

    if amt < 50 and freq > 50:
        return random.uniform(0.85, 0.99)
    if amt < 200 and freq > 20:
        return random.uniform(0.60, 0.80)
    return random.uniform(0.01, 0.40)

"""
Light-weight stand-ins for a real ML model & SHAP explainer.
They expose every symbol referenced by streaming_app.py so the
Spark job will start cleanly.
"""

from __future__ import annotations
import random
from typing import List, Tuple, Any

# ------------------------------------------------------------------ #
# 1. “Load” / “load_dummy” model
# ------------------------------------------------------------------ #
def load_model(path: str | None = None) -> Any:
    """
    Pretends to load a trained model from disk.
    Replace with pickle / joblib in production.
    """
    print(f"[model] dummy model loaded from {path or '<memory>'}")
    return None                      # placeholder object

# ― export under the old alias too
def load_dummy_model(path: str | None = None) -> Any:        # noqa: N802
    return load_model(path)


# ------------------------------------------------------------------ #
# 2. Basic Pandas-to-matrix pre-processing
# ------------------------------------------------------------------ #
def preprocess_features(pdf) -> Tuple[list[list[float]], List[str]]:
    """
    Very small feature set for demo purposes.
    Ensures that required columns exist before export to list-of-lists.
    """
    feature_names = ["feature_amount", "feature_tx_count_daily"]

    for col in feature_names:
        if col not in pdf.columns:
            pdf[col] = 0.0

    X = pdf[feature_names].values.tolist()
    return X, feature_names


# ------------------------------------------------------------------ #
# 3. Dummy prediction helpers
# ------------------------------------------------------------------ #
def predict_fraud_score(features: dict) -> float:
    """
    Simple heuristic:
        – low amount  + many daily tx  ➜ high fraud score
    """
    amount = float(features.get("feature_amount", 0))
    freq   = int(features.get("feature_tx_count_daily", 0))

    if amount < 50 and freq > 50:
        return random.uniform(0.85, 0.99)
    if amount < 200 and freq > 20:
        return random.uniform(0.60, 0.80)
    return random.uniform(0.01, 0.40)


# ------------------------------------------------------------------ #
# 4. SHAP-style explanations  (row-by-row)
# ------------------------------------------------------------------ #
def get_shap_explanation(                       # noqa: N802
    features: dict,
    prediction_score: float | None = None,
) -> list[dict]:
    """
    Creates a tiny list of feature-contribution dicts.
    """
    explanation: list[dict] = [
        {
            "feature":      "TransactionAmount",
            "value":        features.get("feature_amount", 0),
            "contribution": random.uniform(0.2, 0.5),
        }
    ]

    if prediction_score is None:
        prediction_score = predict_fraud_score(features)

    if prediction_score > 0.8:
        explanation.append({
            "feature":      "SuspiciousFrequency",
            "value":        features.get("feature_tx_count_daily", 0),
            "contribution": random.uniform(0.1, 0.3),
        })
        explanation.append({
            "feature":      "AccountPairAnomaly",
            "value":        True,
            "contribution": random.uniform(0.1, 0.2),
        })
    elif prediction_score > 0.5:
        explanation.append({
            "feature":      "TxnTypeMatch",
            "value":        features.get("transaction_type", "transfer"),
            "contribution": random.uniform(0.05, 0.15),
        })

    # keep only the top-3 by absolute contribution
    return sorted(
        explanation,
        key=lambda x: abs(x["contribution"]),
        reverse=True
    )[:3]


# ------------------------------------------------------------------ #
# 5. Matrix-level explainer (kept for older code paths)
# ------------------------------------------------------------------ #
def explain_prediction(         # same signature streaming_app once used
    model,
    X: list[list[float]],
    feature_names: List[str],
) -> list[list[float]]:
    """
    Produces a 2-D list of random SHAP-like values that
    has the same shape as `X`.
    """
    return [
        [random.uniform(-0.2, 0.2) for _ in feature_names]
        for _ in X
    ]

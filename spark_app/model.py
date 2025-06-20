# spark_app/model.py
import random
import json

# This file would contain your trained ML model and SHAP explainer
# For this initial demo, we'll use simple dummy functions.

# --- Dummy ML Model Prediction ---
def predict_fraud_score(features):
    """
    Simulates an ML model predicting a fraud score.
    In a real scenario, this would load a trained model (e.g., from scikit-learn, XGBoost)
    and perform inference based on input features.
    """
    # Simple rule: if amount is very low and frequency is high, return high score
    amount = features.get('feature_amount', 0)
    tx_count_daily = features.get('feature_tx_count_daily', 0)

    if amount < 50 and tx_count_daily > 50:
        return random.uniform(0.85, 0.99) # High fraud probability
    elif amount < 200 and tx_count_daily > 20:
        return random.uniform(0.6, 0.8) # Medium probability
    else:
        return random.uniform(0.01, 0.4) # Low probability for normal transactions

# --- Dummy SHAP Explainer ---
def get_shap_explanation(features, prediction_score):
    """
    Simulates SHAP explanation for a prediction.
    In a real scenario, this would use the SHAP library (e.g., shap.TreeExplainer)
    to calculate feature contributions for a given prediction.
    """
    explanation = []
    # Always include transaction amount as a significant feature
    explanation.append({"feature": "TransactionAmount", "value": features.get('feature_amount', 0), "contribution": random.uniform(0.2, 0.5)})

    if prediction_score > 0.8:
        explanation.append({"feature": "SuspiciousFrequency", "value": features.get('feature_tx_count_daily', 0), "contribution": random.uniform(0.1, 0.3)})
        explanation.append({"feature": "AccountPairAnomaly", "value": "True", "contribution": random.uniform(0.1, 0.2)})
    elif prediction_score > 0.5:
        explanation.append({"feature": "TxnTypeMatch", "value": features.get('transaction_type', 'transfer'), "contribution": random.uniform(0.05, 0.15)})

    # Sort by contribution and return top 3
    explanation_sorted = sorted(explanation, key=lambda x: x['contribution'], reverse=True)[:3]
    return explanation_sorted

# Function to load a dummy model (if needed by streaming_app, currently not used directly)
def load_dummy_model():
    """
    Placeholder function to simulate loading a pre-trained model.
    """
    print("Dummy ML Model loaded successfully.")
    return "DummyModelObject" # Return a placeholder
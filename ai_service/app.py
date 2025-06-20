# ai_service/app.py
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# This is a placeholder/stub for LLM interaction.
# In a real application, you'd load a small local LLM (e.g., using Hugging Face transformers)
# or make an API call to a larger model.

def generate_sar_draft_llm_stub(alert_data):
    """
    Stubs the LLM's SAR draft generation.
    It constructs a simple narrative based on the provided alert data.
    """
    transaction_id = alert_data.get("transaction_id", "N/A")
    sender = alert_data.get("sender_account", "N/A")
    receiver = alert_data.get("receiver_account", "N/A")
    amount = alert_data.get("amount", "N/A")
    ml_score = alert_data.get("ml_fraud_score", "N/A")
    is_smurfing = alert_data.get("is_smurfing_rule", False)
    shap_features = alert_data.get("shap_features", [])

    narrative = f"SAR Draft for Transaction ID: {transaction_id}\n\n"
    narrative += f"On {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert_data.get('alert_timestamp', 0) / 1000))}, a suspicious transaction occurred.\n"
    narrative += f"Sender Account: {sender}, Receiver Account: {receiver}, Amount: ${amount}\n"
    narrative += f"ML Fraud Score: {ml_score:.2f}\n"

    if is_smurfing:
        narrative += "Rule-based 'smurfing' pattern detected, indicating potentially structured transactions.\n"
    else:
        narrative += "No explicit smurfing rule detected, primary flag from ML model.\n"

    if shap_features:
        narrative += "\nKey features driving this alert:\n"
        for feature in shap_features:
            narrative += f"- {feature['feature']}: {feature['value']} (Contribution: {feature['contribution']:.2f})\n"
    else:
        narrative += "\nNo specific SHAP features provided for this alert.\n"

    narrative += "\nFurther investigation is recommended to determine the legitimacy of this activity."

    return narrative

@app.route('/generate-sar', methods=['POST'])
def generate_sar():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input, JSON data required"}), 400

    sar_draft = generate_sar_draft_llm_stub(data)
    return jsonify({"sar_draft": sar_draft})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Flask LLM Stub"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True for dev, remove in prod
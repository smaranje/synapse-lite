# ai_service/Dockerfile
# This Dockerfile builds the image for your Flask LLM service.

FROM python:3.9-slim-buster

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- CRITICAL FIX: Create app.py directly in the Dockerfile to ensure correct indentation and f-string escaping ---
# This bypasses any issues with host file system or copy-paste errors.
RUN echo '# ai_service/app.py - Updated for Neo4j context and f-string fix' > app.py && \
    echo 'from flask import Flask, request, jsonify' >> app.py && \
    echo 'import os' >> app.py && \
    echo 'import json' >> app.py && \
    echo 'import google.generativeai as genai' >> app.py && \
    echo 'from cassandra.cluster import Cluster' >> app.py && \
    echo 'from cassandra.auth import PlainTextAuthProvider' >> app.py && \
    echo 'from neo4j import GraphDatabase, basic_auth' >> app.py && \
    echo '' >> app.py && \
    echo 'app = Flask(__name__)' >> app.py && \
    echo '' >> app.py && \
    echo '# Configure the Gemini API' >> app.py && \
    echo 'GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")' >> app.py && \
    echo '' >> app.py && \
    echo 'if GEMINI_API_KEY:' >> app.py && \
    echo '    genai.configure(api_key=GEMINI_API_KEY)' >> app.py && \
    echo '    model = genai.GenerativeModel("gemini-2.0-flash")' >> app.py && \
    echo 'else:' >> app.py && \
    echo '    model = None' >> app.py && \
    echo '    print("WARNING: GEMINI_API_KEY not set. LLM functionality will be disabled.")' >> app.py && \
    echo '' >> app.py && \
    echo '# Cassandra Configuration (optional, if LLM needs to query directly)' >> app.py && \
    echo 'CASSANDRA_CONTACT_POINTS = os.environ.get("CASSANDRA_CONTACT_POINTS", "cassandra").split(",")' >> app.py && \
    echo '# auth_provider = PlainTextAuthProvider(username="cassandra", password="cassandra") # Uncomment if you set up auth' >> app.py && \
    echo 'cassandra_cluster = None' >> app.py && \
    echo 'try:' >> app.py && \
    echo '    cassandra_cluster = Cluster(CASSANDRA_CONTACT_POINTS)' >> app.py && \
    echo '    # For a simple demo, we won"t strictly verify session here, but useful for context.' >> app.py && \
    echo '    print("Cassandra cluster object created for Flask service.")' >> app.py && \
    echo 'except Exception as e:' >> app.py && \
    echo '    print(f"Failed to create Cassandra cluster object in Flask service: {e}")' >> app.py && \
    echo '' >> app.py && \
    echo '# Neo4j Configuration' >> app.py && \
    echo 'NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")' >> app.py && \
    echo 'NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")' >> app.py && \
    echo 'NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")' >> app.py && \
    echo '' >> app.py && \
    echo 'neo4j_driver = None' >> app.py && \
    echo 'try:' >> app.py && \
    echo '    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))' >> app.py && \
    echo '    neo4j_driver.verify_connectivity()' >> app.py && \
    echo '    print("Neo4j driver initialized and connected for Flask service.")' >> app.py && \
    echo 'except Exception as e:' >> app.py && \
    echo '    print(f"Failed to connect to Neo4j in Flask service: {e}")' >> app.py && \
    echo '    neo4j_driver = None' >> app.py && \
    echo '' >> app.py && \
    echo 'def fetch_neo4j_context(transaction_hash):' >> app.py && \
    echo '    if not neo4j_driver:' >> app.py && \
    echo '        return "Neo4j connection not available."' >> app.py && \
    echo '    ' >> app.py && \
    echo '    context_data = []' >> app.py && \
    echo '    query = """' >> app.py && \
    echo '    MATCH (tx:Transaction {hash: $transaction_hash})' >> app.py && \
    echo '    OPTIONAL MATCH (addr_in:Address)-[s_in:SENT]->(tx)' >> app.py && \
    echo '    OPTIONAL MATCH (tx)-[s_out:SENT_TO]->(addr_out:Address)' >> app.py && \
    echo '    RETURN tx, COLLECT({address: addr_in.id, relationship: type(s_in)}) AS inputs, COLLECT({address: addr_out.id, relationship: type(s_out)}) AS outputs' >> app.py && \
    echo '    """' >> app.py && \
    echo '    try:' >> app.py && \
    echo '        with neo4j_driver.session() as session:' >> app.py && \
    echo '            result = session.run(query, transaction_hash=transaction_hash).single()' >> app.py && \
    echo '            if result:' >> app.py && \
    echo '                tx_props = dict(result["tx"])' >> app.py && \
    echo "                context_data.append(f\"Transaction (Hash: {tx_props.get('hash', 'N/A')}, ML Score: {tx_props.get('mlFraudScore', 'N/A')}, Smurfing Rule: {tx_props.get('isSmurfingRule', 'N/A')})\")" >> app.py && \
    echo '                ' >> app.py && \
    echo '                input_addresses = [item["address"] for item in result["inputs"] if item["address"]]' >> app.py && \
    echo '                if input_addresses:' >> app.py && \
    echo '                    context_data.append(f"Involved input addresses: {', '.join(input_addresses)}")' >> app.py && \
    echo '                ' >> app.py && \
    echo '                output_addresses = [item["address"] for item in result["outputs"] if item["address"]]' >> app.py && \
    echo '                if output_addresses:' >> app.py && \
    echo '                    context_data.append(f"Involved output addresses: {', '.join(output_addresses)}")' >> app.py && \
    echo '                ' >> app.py && \
    echo '                # You could add more complex queries here, e.g., finding common counterparties' >> app.py && \
    echo '                ' >> app.py && \
    echo '                return "\n".join(context_data)' >> app.py && \
    echo '            else:' >> app.py && \
    echo '                return "No specific graph context found for this transaction."' >> app.py && \
    echo '    except Exception as e:' >> app.py && \
    echo '        print(f"Error generating content from LLM: {e}")' >> app.py && \
    echo '        return f"Error fetching graph context: {e}"' >> app.py && \
    echo '' >> app.py && \
    echo '' >> app.py && \
    echo '@app.route("/health")' >> app.py && \
    echo 'def health_check():' >> app.py && \
    echo '    return jsonify({"status": "ok"}), 200' >> app.py && \
    echo '' >> app.py && \
    echo '@app.route("/generate-sar", methods=["POST"])' >> app.py && \
    echo 'def generate_sar():' >> app.py && \
    echo '    if not model:' >> app.py && \
    echo '        return jsonify({"error": "LLM service not configured due to missing API key."}), 503' >> app.py && \
    echo '' >> app.py && \
    echo '    data = request.json' >> app.py && \
    echo '    if not data:' >> app.py && \
    echo '        return jsonify({"error": "Invalid request: no JSON data provided."}), 400' >> app.py && \
    echo '' >> app.py && \
    echo '    # Extract relevant alert details from the incoming data' >> app.py && \
    echo '    transaction_hash = data.get("transaction_hash", "N/A")' >> app.py && \
    echo '    ml_fraud_score = data.get("ml_fraud_score", "N/A")' >> app.py && \
    echo '    is_smurfing_rule = data.get("is_smurfing_rule", False)' >> app.py && \
    echo '    num_inputs = data.get("num_inputs", "N/A")' >> app.py && \
    echo '    num_outputs = data.get("num_outputs", "N/A")' >> app.py && \
    echo '    total_input_value = data.get("total_input_value", "N/A")' >> app.py && \
    echo '    total_output_value = data.get("total_output_value", "N/A")' >> app.py && \
    echo '    transaction_fee = data.get("transaction_fee", "N/A")' >> app.py && \
    echo '    fee_per_byte = data.get("fee_per_byte", "N/A")' >> app.py && \
    echo '    shap_features_json = data.get("shap_features_json", "[]")' >> app.py && \
    echo '' >> app.py && \
    echo '    shap_features_list = []' >> app.py && \
    echo '    try:' >> app.py && \
    echo '        shap_features_list = json.loads(shap_features_json)' >> app.py && \
    echo '    except json.JSONDecodeError:' >> app.py && \
    echo '        pass' >> app.py && \
    echo '' >> app.py && \
    echo '    # Fetch Neo4j context' >> app.py && \
    echo '    neo4j_context = fetch_neo4j_context(transaction_hash)' >> app.py && \
    echo '' >> app.py && \
    echo '    # Construct a comprehensive prompt for the LLM' >> app.py && \
    echo '    prompt = f"""' >> app.py && \
    echo '    Generate a Suspicious Activity Report (SAR) draft based on the following Bitcoin transaction alert.' >> app.py && \
    echo '    Focus on conciseness, clarity, and the reasons for suspicion.' >> app.py && \
    echo '' >> app.py && \
    echo '    Transaction Details:' >> app.py && \
    echo '    - Transaction Hash: {transaction_hash}' >> app.py && \
    echo '    - ML Fraud Score: {ml_fraud_score}' >> app.py && \
    echo '    - Smurfing Rule Triggered: {is_smurfing_rule}' >> app.py && \
    echo '    - Number of Inputs: {num_inputs}' >> app.py && \
    echo '    - Number of Outputs: {num_outputs}' >> app.py && \
    echo '    - Total Input Value: {total_input_value} Satoshis' >> app.py && \
    echo '    - Total Output Value: {total_output_value} Satoshis' >> app.py && \
    echo '    - Transaction Fee: {transaction_fee} Satoshis' >> app.py && \
    echo '    - Fee Per Byte: {fee_per_byte:.4f}' >> app.py && \
    echo '' >> app.py && \
    echo '    Top Features/Reasons for Alert (from SHAP insights):' >> app.py && \
    echo '    {json.dumps(shap_features_list, indent=2)}' >> app.py && \
    echo '' >> app.py && \
    echo '    Graph Database Context (from Neo4j):' >> app.py && \
    echo '    {neo4j_context}' >> app.py && \
    echo '' >> app.py && \
    echo '    Based on these details, draft a concise SAR highlighting the key suspicious activities.' >> app.py && \
    echo '    """' >> app.py && \
    echo '' >> app.py && \
    echo 'if __name__ == "__main__":' >> app.py && \
    echo '    app.run(host="0.0.0.0", port=5000)' >> app.py
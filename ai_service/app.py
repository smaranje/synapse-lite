    # ai_service/app.py - Updated for Neo4j context
    from flask import Flask, request, jsonify
    import os
    import json
    import google.generativeai as genai
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    from neo4j import GraphDatabase, basic_auth

    app = Flask(__name__)

    # Configure the Gemini API
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
    else:
        model = None
        print("WARNING: GEMINI_API_KEY not set. LLM functionality will be disabled.")

    # Cassandra Configuration (optional, if LLM needs to query directly)
    CASSANDRA_CONTACT_POINTS = os.environ.get('CASSANDRA_CONTACT_POINTS', 'cassandra').split(',')
    # auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra') # Uncomment if you set up auth
    cassandra_cluster = None
    try:
        cassandra_cluster = Cluster(CASSANDRA_CONTACT_POINTS)
        # For a simple demo, we won't strictly verify session here, but useful for context.
        print("Cassandra cluster object created for Flask service.")
    except Exception as e:
        print(f"Failed to create Cassandra cluster object in Flask service: {e}")

    # Neo4j Configuration
    NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
    NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')

    neo4j_driver = None
    try:
        neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))
        neo4j_driver.verify_connectivity()
        print("Neo4j driver initialized and connected for Flask service.")
    except Exception as e:
        print(f"Failed to connect to Neo4j in Flask service: {e}")
        neo4j_driver = None

    def fetch_neo4j_context(transaction_hash):
        if not neo4j_driver:
            return "Neo4j connection not available."
        
        context_data = []
        query = """
        MATCH (tx:Transaction {hash: $transaction_hash})
        OPTIONAL MATCH (addr_in:Address)-[s_in:SENT]->(tx)
        OPTIONAL MATCH (tx)-[s_out:SENT_TO]->(addr_out:Address)
        RETURN tx, COLLECT({address: addr_in.id, relationship: type(s_in)}) AS inputs, COLLECT({address: addr_out.id, relationship: type(s_out)}) AS outputs
        """
        try:
            with neo4j_driver.session() as session:
                result = session.run(query, transaction_hash=transaction_hash).single()
                if result:
                    tx_props = dict(result["tx"])
                    context_data.append(f"Transaction (Hash: {tx_props.get('hash', 'N/A')}, ML Score: {tx_props.get('mlFraudScore', 'N/A')}, Smurfing Rule: {tx_props.get('isSmurfingRule', 'N/A')})")
                    
                    input_addresses = [item['address'] for item in result["inputs"] if item['address']]
                    if input_addresses:
                        context_data.append(f"Involved input addresses: {', '.join(input_addresses)}")
                    
                    output_addresses = [item['address'] for item in result["outputs"] if item['address']]
                    if output_addresses:
                        context_data.append(f"Involved output addresses: {', '.join(output_addresses)}")
                    
                    # You could add more complex queries here, e.g., finding common counterparties
                    
                    return "\n".join(context_data)
                else:
                    return "No specific graph context found for this transaction."
        except Exception as e:
            print(f"Error fetching Neo4j context for {transaction_hash}: {e}")
            return f"Error fetching graph context: {e}"


    @app.route('/generate-sar', methods=['POST'])
    def generate_sar():
        if not model:
            return jsonify({"error": "LLM service not configured due to missing API key."}), 503

        data = request.json
        if not data:
            return jsonify({"error": "Invalid request: no JSON data provided."}), 400

        # Extract relevant alert details from the incoming data
        transaction_hash = data.get("transaction_hash", "N/A")
        ml_fraud_score = data.get("ml_fraud_score", "N/A")
        is_smurfing_rule = data.get("is_smurfing_rule", False)
        num_inputs = data.get("num_inputs", "N/A")
        num_outputs = data.get("num_outputs", "N/A")
        total_input_value = data.get("total_input_value", "N/A")
        total_output_value = data.get("total_output_value", "N/A")
        transaction_fee = data.get("transaction_fee", "N/A")
        fee_per_byte = data.get("fee_per_byte", "N/A")
        shap_features_json = data.get("shap_features_json", "[]")

        shap_features_list = []
        try:
            shap_features_list = json.loads(shap_features_json)
        except json.JSONDecodeError:
            pass

        # Fetch Neo4j context
        neo4j_context = fetch_neo4j_context(transaction_hash)

        # Construct a comprehensive prompt for the LLM
        prompt = f"""
        Generate a Suspicious Activity Report (SAR) draft based on the following Bitcoin transaction alert.
        Focus on conciseness, clarity, and the reasons for suspicion.

        Transaction Details:
        - Transaction Hash: {transaction_hash}
        - ML Fraud Score: {ml_fraud_score}
        - Smurfing Rule Triggered: {is_smurfing_rule}
        - Number of Inputs: {num_inputs}
        - Number of Outputs: {num_outputs}
        - Total Input Value: {total_input_value} Satoshis
        - Total Output Value: {total_output_value} Satoshis
        - Transaction Fee: {transaction_fee} Satoshis
        - Fee Per Byte: {fee_per_byte:.4f}

        Top Features/Reasons for Alert (from SHAP insights):
        {json.dumps(shap_features_list, indent=2)}

        Graph Database Context (from Neo4j):
        {neo4j_context}

        Based on these details, draft a concise SAR highlighting the key suspicious activities.
        """

        try:
            # Call the Gemini API
            response = model.generate_content(prompt)
            sar_draft = response.text
            return jsonify({"sar_draft": sar_draft})
        except Exception as e:
            print(f"Error generating content from LLM: {e}")
            return jsonify({"error": f"Failed to generate SAR draft from LLM: {e}"}), 500

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
    
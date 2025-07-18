# ai_service/app_optimized.py - Optimized LLM Service with Batch Processing
import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from neo4j import GraphDatabase
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.warning("GEMINI_API_KEY not set. LLM features will be disabled.")
    model = None

# Neo4j configuration with connection pooling
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')

# Initialize Neo4j driver with connection pool
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    max_connection_pool_size=50
)

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=10)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "llm-service-optimized"}), 200

@lru_cache(maxsize=1000)
def get_transaction_context(transaction_hash):
    """Get transaction context from Neo4j with caching"""
    query = """
    MATCH (t:Transaction {hash: $transaction_hash})
    OPTIONAL MATCH (sender:Address)-[:SENT]->(t)
    OPTIONAL MATCH (t)-[:SENT_TO]->(receiver:Address)
    RETURN t, collect(DISTINCT sender.id) as senders, collect(DISTINCT receiver.id) as receivers
    """
    
    with driver.session() as session:
        result = session.run(query, transaction_hash=transaction_hash).single()
        if result and result['t']:
            return {
                'transaction': dict(result['t']),
                'senders': result['senders'],
                'receivers': result['receivers']
            }
    return None

def generate_sar_for_transaction(alert_data, context=None):
    """Generate SAR for a single transaction"""
    if not model:
        return {
            "transaction_hash": alert_data.get("transaction_hash"),
            "sar_draft": "LLM service not configured",
            "risk_score": 0.0,
            "analysis": "No analysis available"
        }
    
    try:
        # Create prompt
        prompt = f"""
        Analyze this Bitcoin transaction for suspicious activity:
        
        Transaction Hash: {alert_data.get('transaction_hash')}
        Number of Inputs: {alert_data.get('num_inputs')}
        Number of Outputs: {alert_data.get('num_outputs')}
        Total Input Value: {alert_data.get('total_input_value')} satoshis
        Total Output Value: {alert_data.get('total_output_value')} satoshis
        Transaction Fee: {alert_data.get('transaction_fee')} satoshis
        Fee per Byte: {alert_data.get('fee_per_byte')} sat/byte
        
        {f"Senders: {', '.join(context['senders'][:5])}" if context and context['senders'] else ""}
        {f"Receivers: {', '.join(context['receivers'][:5])}" if context and context['receivers'] else ""}
        
        Provide:
        1. Risk assessment (0.0-1.0)
        2. Brief analysis (2-3 sentences)
        3. SAR draft if suspicious (or "No SAR required" if not)
        
        Format as JSON: {"risk_score": 0.0, "analysis": "", "sar_draft": ""}
        """
        
        response = model.generate_content(prompt)
        
        # Parse response
        try:
            result = json.loads(response.text)
            return {
                "transaction_hash": alert_data.get("transaction_hash"),
                "risk_score": float(result.get("risk_score", 0.0)),
                "analysis": result.get("analysis", ""),
                "sar_draft": result.get("sar_draft", "")
            }
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                "transaction_hash": alert_data.get("transaction_hash"),
                "risk_score": 0.5,
                "analysis": "Analysis completed",
                "sar_draft": response.text[:500]
            }
            
    except Exception as e:
        logger.error(f"Error generating SAR: {str(e)}")
        return {
            "transaction_hash": alert_data.get("transaction_hash"),
            "risk_score": 0.0,
            "analysis": f"Error: {str(e)}",
            "sar_draft": "Error generating SAR"
        }

@app.route('/generate-sar', methods=['POST'])
def generate_sar():
    """Single transaction SAR generation endpoint (backward compatible)"""
    alert_data = request.json
    
    if not alert_data:
        return jsonify({"error": "No data provided"}), 400
    
    # Get transaction context
    tx_hash = alert_data.get("transaction_hash")
    context = get_transaction_context(tx_hash) if tx_hash else None
    
    # Generate SAR
    result = generate_sar_for_transaction(alert_data, context)
    
    # Store result in Neo4j
    if tx_hash:
        store_sar_result(tx_hash, result)
    
    return jsonify(result), 200

@app.route('/generate-sar/batch', methods=['POST'])
def generate_sar_batch():
    """Batch SAR generation endpoint for multiple transactions"""
    data = request.json
    
    if not data or 'transactions' not in data:
        return jsonify({"error": "No transactions provided"}), 400
    
    transactions = data['transactions']
    logger.info(f"Processing batch of {len(transactions)} transactions")
    
    # Process transactions in parallel
    futures = []
    for tx_data in transactions:
        future = executor.submit(process_single_transaction, tx_data)
        futures.append(future)
    
    # Collect results
    results = []
    for future in as_completed(futures):
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")
    
    # Batch store results in Neo4j
    if results:
        batch_store_sar_results(results)
    
    return jsonify({"results": results}), 200

def process_single_transaction(tx_data):
    """Process a single transaction for batch processing"""
    tx_hash = tx_data.get("transaction_hash")
    context = get_transaction_context(tx_hash) if tx_hash else None
    return generate_sar_for_transaction(tx_data, context)

def store_sar_result(transaction_hash, result):
    """Store SAR result for a single transaction"""
    query = """
    MATCH (t:Transaction {hash: $transaction_hash})
    SET t.llmAnalysis = $analysis,
        t.riskScore = $risk_score,
        t.sarDraft = $sar_draft,
        t.analysisTimestamp = datetime()
    """
    
    try:
        with driver.session() as session:
            session.run(
                query,
                transaction_hash=transaction_hash,
                analysis=result.get("analysis", ""),
                risk_score=result.get("risk_score", 0.0),
                sar_draft=result.get("sar_draft", "")
            )
    except Exception as e:
        logger.error(f"Error storing SAR result: {str(e)}")

def batch_store_sar_results(results):
    """Batch store SAR results in Neo4j"""
    query = """
    UNWIND $results as result
    MATCH (t:Transaction {hash: result.transaction_hash})
    SET t.llmAnalysis = result.analysis,
        t.riskScore = result.risk_score,
        t.sarDraft = result.sar_draft,
        t.analysisTimestamp = datetime()
    """
    
    try:
        with driver.session() as session:
            session.run(query, results=results)
            logger.info(f"Stored {len(results)} SAR results in Neo4j")
    except Exception as e:
        logger.error(f"Error batch storing SAR results: {str(e)}")

@app.route('/analyze-network', methods=['POST'])
def analyze_network():
    """Analyze transaction network for patterns"""
    data = request.json
    address = data.get('address')
    depth = data.get('depth', 2)
    
    if not address:
        return jsonify({"error": "No address provided"}), 400
    
    # Get network data from Neo4j
    network_query = """
    MATCH path = (a:Address {id: $address})-[:SENT|SENT_TO*1..$depth]-(connected)
    RETURN path LIMIT 100
    """
    
    paths = []
    with driver.session() as session:
        result = session.run(network_query, address=address, depth=depth)
        for record in result:
            paths.append(record['path'])
    
    if not paths:
        return jsonify({"analysis": "No network activity found"}), 200
    
    # Analyze with LLM
    if model:
        prompt = f"""
        Analyze this Bitcoin address network:
        Address: {address}
        Connected paths: {len(paths)}
        Network depth: {depth}
        
        Identify any suspicious patterns or behaviors.
        """
        
        try:
            response = model.generate_content(prompt)
            return jsonify({"analysis": response.text}), 200
        except Exception as e:
            logger.error(f"Error in network analysis: {str(e)}")
    
    return jsonify({"analysis": f"Found {len(paths)} connected paths"}), 200

@app.teardown_appcontext
def close_driver(error):
    """Close Neo4j driver on app teardown"""
    if driver:
        driver.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
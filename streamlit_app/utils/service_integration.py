"""
Service Integration Module for Synapse-Lite Fraud Detection System
Handles connections to Neo4j, Kafka, and Flask LLM Service
"""

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from neo4j import GraphDatabase
from kafka import KafkaConsumer, KafkaProducer
import streamlit as st

class Neo4jConnection:
    """Handles Neo4j database connections and queries"""
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            return True
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {str(e)}")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def get_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """Fetch recent transactions from Neo4j"""
        if not self.driver:
            return []
        
        query = """
        MATCH (t:Transaction)
        RETURN t
        ORDER BY t.timestamp DESC
        LIMIT $limit
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                transactions = []
                for record in result:
                    tx = record["t"]
                    transactions.append({
                        'hash': tx.get('hash'),
                        'timestamp': datetime.fromisoformat(tx.get('timestamp', datetime.now().isoformat())),
                        'total_value_btc': float(tx.get('total_value', 0)),
                        'total_value_usd': float(tx.get('total_value', 0)) * 45000,
                        'fee': float(tx.get('fee', 0)),
                        'num_inputs': int(tx.get('num_inputs', 0)),
                        'num_outputs': int(tx.get('num_outputs', 0)),
                        'ml_score': float(tx.get('ml_score', 0)),
                        'is_smurfing_rule': bool(tx.get('is_smurfing', False)),
                        'risk_level': tx.get('risk_level', 'Low')
                    })
                return transactions
        except Exception as e:
            st.error(f"Error fetching transactions: {str(e)}")
            return []
    
    def get_alerts(self) -> List[Dict]:
        """Fetch alerts from Neo4j"""
        if not self.driver:
            return []
        
        query = """
        MATCH (a:Alert)-[:TRIGGERED_BY]->(t:Transaction)
        RETURN a, t
        ORDER BY a.timestamp DESC
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                alerts = []
                for record in result:
                    alert = record["a"]
                    tx = record["t"]
                    alerts.append({
                        'alert_id': alert.get('id'),
                        'transaction_hash': tx.get('hash'),
                        'risk_level': alert.get('risk_level'),
                        'timestamp': datetime.fromisoformat(alert.get('timestamp', datetime.now().isoformat())),
                        'ml_score': float(tx.get('ml_score', 0)),
                        'is_smurfing': bool(tx.get('is_smurfing', False)),
                        'total_value_btc': float(tx.get('total_value', 0)),
                        'total_value_usd': float(tx.get('total_value', 0)) * 45000,
                        'num_inputs': int(tx.get('num_inputs', 0)),
                        'num_outputs': int(tx.get('num_outputs', 0)),
                        'fee': float(tx.get('fee', 0)),
                        'description': alert.get('description', 'Suspicious activity detected'),
                        'status': alert.get('status', 'Open')
                    })
                return alerts
        except Exception as e:
            st.error(f"Error fetching alerts: {str(e)}")
            return []
    
    def get_analytics_data(self) -> Dict:
        """Fetch analytics data from Neo4j"""
        if not self.driver:
            return {}
        
        analytics = {}
        
        # Get transaction statistics
        stats_query = """
        MATCH (t:Transaction)
        RETURN 
            COUNT(t) as total_transactions,
            AVG(t.ml_score) as avg_risk_score,
            SUM(t.total_value) as total_volume,
            AVG(t.total_value) as avg_transaction_size
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(stats_query)
                record = result.single()
                if record:
                    analytics['total_transactions'] = record['total_transactions']
                    analytics['avg_risk_score'] = float(record['avg_risk_score'] or 0)
                    analytics['total_volume'] = float(record['total_volume'] or 0)
                    analytics['avg_transaction_size'] = float(record['avg_transaction_size'] or 0)
                
                # Get risk distribution
                risk_query = """
                MATCH (t:Transaction)
                RETURN t.risk_level as risk_level, COUNT(t) as count
                """
                result = session.run(risk_query)
                risk_distribution = {}
                for record in result:
                    risk_distribution[record['risk_level']] = record['count']
                analytics['risk_distribution'] = risk_distribution
                
                return analytics
        except Exception as e:
            st.error(f"Error fetching analytics: {str(e)}")
            return {}

class KafkaConnection:
    """Handles Kafka connections for real-time data streaming"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BROKER", "kafka:9092")
        self.topic = os.getenv("KAFKA_TOPIC", "transactions")
        self.consumer = None
        self.producer = None
    
    def create_consumer(self, group_id: str = "streamlit-dashboard"):
        """Create Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            return True
        except Exception as e:
            st.error(f"Failed to create Kafka consumer: {str(e)}")
            return False
    
    def create_producer(self):
        """Create Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            return True
        except Exception as e:
            st.error(f"Failed to create Kafka producer: {str(e)}")
            return False
    
    def consume_messages(self, max_messages: int = 10) -> List[Dict]:
        """Consume messages from Kafka"""
        if not self.consumer:
            return []
        
        messages = []
        try:
            # Set timeout to avoid blocking
            records = self.consumer.poll(timeout_ms=1000, max_records=max_messages)
            
            for topic_partition, msgs in records.items():
                for msg in msgs:
                    messages.append(msg.value)
            
            return messages
        except Exception as e:
            st.error(f"Error consuming Kafka messages: {str(e)}")
            return []
    
    def close(self):
        """Close Kafka connections"""
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()

class LLMServiceConnection:
    """Handles connections to the Flask LLM Service (Gemini API)"""
    
    def __init__(self):
        self.base_url = os.getenv("LLM_SERVICE_URL", "http://flask-llm-service:5000")
    
    def generate_sar(self, transaction_data: Dict) -> str:
        """Generate SAR using the LLM service"""
        try:
            response = requests.post(
                f"{self.base_url}/generate-sar",
                json={'transaction_data': transaction_data},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('sar_text', 'Error generating SAR')
            else:
                return f"Error: Unable to generate SAR (Status: {response.status_code})"
        except requests.exceptions.Timeout:
            return "Error: SAR generation timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "Error: Unable to connect to LLM service. Please check if the service is running."
        except Exception as e:
            return f"Error generating SAR: {str(e)}"
    
    def check_health(self) -> bool:
        """Check if LLM service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

# Create singleton instances
@st.cache_resource
def get_neo4j_connection():
    """Get or create Neo4j connection"""
    conn = Neo4jConnection()
    conn.connect()
    return conn

@st.cache_resource
def get_kafka_connection():
    """Get or create Kafka connection"""
    return KafkaConnection()

@st.cache_resource
def get_llm_connection():
    """Get or create LLM service connection"""
    return LLMServiceConnection()
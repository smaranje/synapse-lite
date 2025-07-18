# streamlit_app/utils/service_integration_optimized.py
import os
import json
import requests
import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
from datetime import datetime, timedelta
import time
from functools import lru_cache
from typing import Dict, List, Any, Optional
import redis
import pickle

# Redis configuration for caching
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_TTL = int(os.environ.get('REDIS_TTL', 300))  # 5 minutes default

class CacheManager:
    """Manages caching with Redis"""
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=False
            )
            self.redis_client.ping()
        except Exception as e:
            print(f"Redis not available, falling back to in-memory cache: {e}")
            self.redis_client = None
            self.memory_cache = {}
    
    def get(self, key: str) -> Any:
        """Get value from cache"""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                return pickle.loads(value) if value else None
            except Exception:
                return None
        else:
            return self.memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = REDIS_TTL):
        """Set value in cache"""
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, pickle.dumps(value))
            except Exception:
                pass
        else:
            self.memory_cache[key] = value
    
    def delete(self, key: str):
        """Delete value from cache"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception:
                pass
        else:
            self.memory_cache.pop(key, None)

# Initialize cache manager
cache_manager = CacheManager()

class Neo4jServiceOptimized:
    """Optimized Neo4j service with connection pooling and caching"""
    def __init__(self, uri, username, password):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self.connect()
    
    def connect(self):
        """Initialize connection with pooling"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_pool_size=50,
                connection_acquisition_timeout=30.0
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {str(e)}")
            return False
    
    def is_connected(self):
        """Check if connected to Neo4j"""
        if not self.driver:
            return False
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except:
            return False
    
    def get_recent_transactions(self, limit=100):
        """Get recent transactions with caching"""
        cache_key = f"recent_transactions_{limit}"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        query = """
        MATCH (t:Transaction)
        RETURN t
        ORDER BY t.timestamp DESC
        LIMIT $limit
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                transactions = [dict(record['t']) for record in result]
                
                # Cache the result
                cache_manager.set(cache_key, transactions, ttl=60)  # Cache for 1 minute
                return transactions
        except Exception as e:
            st.error(f"Failed to fetch transactions: {str(e)}")
            return []
    
    def get_transaction_by_hash(self, tx_hash):
        """Get transaction by hash with caching"""
        cache_key = f"transaction_{tx_hash}"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        query = """
        MATCH (t:Transaction {hash: $hash})
        OPTIONAL MATCH (sender:Address)-[:SENT]->(t)
        OPTIONAL MATCH (t)-[:SENT_TO]->(receiver:Address)
        RETURN t, 
               collect(DISTINCT sender.id) as senders,
               collect(DISTINCT receiver.id) as receivers
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, hash=tx_hash).single()
                if result:
                    transaction_data = {
                        'transaction': dict(result['t']),
                        'senders': result['senders'],
                        'receivers': result['receivers']
                    }
                    # Cache the result
                    cache_manager.set(cache_key, transaction_data, ttl=300)  # Cache for 5 minutes
                    return transaction_data
                return None
        except Exception as e:
            st.error(f"Failed to fetch transaction: {str(e)}")
            return None
    
    def get_statistics(self):
        """Get database statistics with caching"""
        cache_key = "database_statistics"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        stats_query = """
        MATCH (t:Transaction)
        WITH count(t) as total_transactions,
             avg(t.fee) as avg_fee,
             max(t.timestamp) as latest_timestamp
        MATCH (a:Address)
        WITH total_transactions, avg_fee, latest_timestamp, count(a) as total_addresses
        RETURN {
            total_transactions: total_transactions,
            total_addresses: total_addresses,
            avg_fee: avg_fee,
            latest_timestamp: latest_timestamp
        } as stats
        """
        
        risk_query = """
        MATCH (t:Transaction)
        WHERE t.riskScore > 0
        RETURN t.riskScore as risk_score, count(t) as count
        ORDER BY risk_score DESC
        """
        
        try:
            with self.driver.session() as session:
                # Get general statistics
                stats_result = session.run(stats_query).single()
                stats = stats_result['stats'] if stats_result else {}
                
                # Get risk distribution
                risk_result = session.run(risk_query)
                risk_distribution = [
                    {'risk_score': record['risk_score'], 'count': record['count']}
                    for record in risk_result
                ]
                
                result = {
                    'stats': stats,
                    'risk_distribution': risk_distribution
                }
                
                # Cache the result
                cache_manager.set(cache_key, result, ttl=120)  # Cache for 2 minutes
                return result
        except Exception as e:
            st.error(f"Failed to fetch statistics: {str(e)}")
            return {'stats': {}, 'risk_distribution': []}
    
    def search_transactions(self, search_term):
        """Search transactions by hash or address"""
        query = """
        MATCH (t:Transaction)
        WHERE t.hash CONTAINS $search_term
        RETURN t
        LIMIT 50
        UNION
        MATCH (a:Address {id: $search_term})-[:SENT|SENT_TO]-(t:Transaction)
        RETURN t
        LIMIT 50
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, search_term=search_term)
                return [dict(record['t']) for record in result]
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return []
    
    def get_address_analytics(self, address_id):
        """Get analytics for a specific address with caching"""
        cache_key = f"address_analytics_{address_id}"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        query = """
        MATCH (a:Address {id: $address_id})
        OPTIONAL MATCH (a)-[:SENT]->(sent_tx:Transaction)
        OPTIONAL MATCH (received_tx:Transaction)-[:SENT_TO]->(a)
        WITH a,
             count(DISTINCT sent_tx) as sent_count,
             count(DISTINCT received_tx) as received_count,
             sum(sent_tx.totalOutputValue) as total_sent,
             sum(received_tx.totalOutputValue) as total_received
        RETURN {
            address: a.id,
            sent_count: sent_count,
            received_count: received_count,
            total_sent: total_sent,
            total_received: total_received,
            balance: total_received - total_sent
        } as analytics
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, address_id=address_id).single()
                if result:
                    analytics = result['analytics']
                    # Cache the result
                    cache_manager.set(cache_key, analytics, ttl=180)  # Cache for 3 minutes
                    return analytics
                return None
        except Exception as e:
            st.error(f"Failed to fetch address analytics: {str(e)}")
            return None
    
    def close(self):
        """Close the driver connection"""
        if self.driver:
            self.driver.close()

class LLMServiceOptimized:
    """Optimized LLM service with batch support"""
    def __init__(self, base_url):
        self.base_url = base_url
        self.batch_endpoint = f"{base_url}/generate-sar/batch"
        self.single_endpoint = f"{base_url}/generate-sar"
    
    def is_connected(self):
        """Check if LLM service is available"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def analyze_transaction(self, transaction_data):
        """Analyze a single transaction"""
        try:
            response = requests.post(
                self.single_endpoint,
                json=transaction_data,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"LLM analysis failed: {str(e)}")
            return None
    
    def analyze_transactions_batch(self, transactions_list):
        """Analyze multiple transactions in batch"""
        try:
            response = requests.post(
                self.batch_endpoint,
                json={"transactions": transactions_list},
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get('results', [])
            return []
        except Exception as e:
            st.error(f"Batch LLM analysis failed: {str(e)}")
            return []

# Initialize services with environment variables
@st.cache_resource
def get_neo4j_service():
    """Get cached Neo4j service instance"""
    return Neo4jServiceOptimized(
        uri=os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
        username=os.environ.get('NEO4J_USERNAME', 'neo4j'),
        password=os.environ.get('NEO4J_PASSWORD', 'password')
    )

@st.cache_resource
def get_llm_service():
    """Get cached LLM service instance"""
    return LLMServiceOptimized(
        base_url=os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000')
    )

def invalidate_cache(pattern=None):
    """Invalidate cache entries"""
    if pattern:
        # Invalidate specific pattern
        if cache_manager.redis_client:
            for key in cache_manager.redis_client.scan_iter(match=pattern):
                cache_manager.delete(key)
        else:
            # For in-memory cache, clear matching keys
            keys_to_delete = [k for k in cache_manager.memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                cache_manager.delete(key)
    else:
        # Clear all cache
        if cache_manager.redis_client:
            cache_manager.redis_client.flushall()
        else:
            cache_manager.memory_cache.clear()
# data/producer_app_robust.py - Robust Kafka Producer with Circuit Breaker and Retry Logic
import os
import time
import json
import random
import sys
import logging
from typing import Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError, ConnectionError
import signal
import threading
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment Variables
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
PRODUCER_RATE = float(os.environ.get('PRODUCER_RATE', '1.0'))  # Messages per second
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '20'))
RETRY_BACKOFF = float(os.environ.get('RETRY_BACKOFF', '2.0'))
CIRCUIT_BREAKER_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_THRESHOLD', '5'))

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD
    timeout: int = 30  # seconds
    reset_timeout: int = 60  # seconds

class CircuitBreaker:
    """Circuit breaker pattern implementation for Kafka connection"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker moving to HALF_OPEN state")
                else:
                    raise Exception("Circuit breaker is OPEN - failing fast")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.config.reset_timeout
    
    def _on_success(self):
        """Called when operation succeeds"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker reset to CLOSED state")
    
    def _on_failure(self):
        """Called when operation fails"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if (self.state == CircuitState.CLOSED and 
            self.failure_count >= self.config.failure_threshold):
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

class RobustKafkaProducer:
    """Robust Kafka producer with retry logic and circuit breaker"""
    
    def __init__(self, broker: str, topic: str):
        self.broker = broker
        self.topic = topic
        self.producer: Optional[KafkaProducer] = None
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
        self.is_running = True
        self.stats = {
            'messages_sent': 0,
            'messages_failed': 0,
            'reconnections': 0,
            'circuit_breaker_opens': 0
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.is_running = False
    
    def _create_producer(self) -> KafkaProducer:
        """Create a new Kafka producer with optimal settings"""
        return KafkaProducer(
            bootstrap_servers=self.broker.split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1),
            retries=3,
            retry_backoff_ms=1000,
            request_timeout_ms=30000,
            metadata_max_age_ms=30000,
            max_block_ms=10000,
            batch_size=16384,
            linger_ms=100,
            compression_type='lz4',
            acks='all'  # Wait for all replicas
        )
    
    def _connect_with_retry(self) -> bool:
        """Attempt to connect to Kafka with exponential backoff"""
        retry_count = 0
        backoff = 1.0
        
        while retry_count < MAX_RETRIES and self.is_running:
            try:
                logger.info(f"Attempting to connect to Kafka at {self.broker} (attempt {retry_count + 1}/{MAX_RETRIES})")
                
                # Test connection by creating producer and checking broker metadata
                test_producer = self._create_producer()
                
                # Verify broker connectivity
                metadata = test_producer.list_topics(timeout=10)
                logger.info(f"Successfully connected to Kafka. Available topics: {list(metadata.topics)}")
                
                # Verify topic exists or can be created
                if self.topic not in metadata.topics:
                    logger.warning(f"Topic '{self.topic}' not found in available topics")
                
                self.producer = test_producer
                self.stats['reconnections'] += 1
                return True
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Failed to connect to Kafka (attempt {retry_count}/{MAX_RETRIES}): {e}")
                
                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying in {backoff:.1f} seconds...")
                    time.sleep(backoff)
                    backoff = min(backoff * RETRY_BACKOFF, 30.0)  # Cap at 30 seconds
        
        logger.error(f"Failed to connect to Kafka after {MAX_RETRIES} attempts")
        return False
    
    def _send_message_with_circuit_breaker(self, data: Dict[Any, Any]) -> bool:
        """Send message using circuit breaker pattern"""
        try:
            future = self.circuit_breaker.call(
                self.producer.send,
                self.topic,
                value=data
            )
            
            # Wait for send confirmation
            record_metadata = future.get(timeout=10)
            logger.debug(f"Message sent to topic '{record_metadata.topic}', "
                        f"partition {record_metadata.partition}, offset {record_metadata.offset}")
            
            self.stats['messages_sent'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.stats['messages_failed'] += 1
            
            # Check if we need to reconnect
            if isinstance(e, (ConnectionError, KafkaTimeoutError)):
                logger.warning("Connection error detected, will attempt to reconnect")
                self._close_producer()
            
            return False
    
    def _close_producer(self):
        """Safely close the producer"""
        if self.producer:
            try:
                self.producer.close(timeout=10)
            except Exception as e:
                logger.warning(f"Error closing producer: {e}")
            finally:
                self.producer = None
    
    def _ensure_connected(self) -> bool:
        """Ensure we have a valid Kafka connection"""
        if self.producer is None:
            return self._connect_with_retry()
        return True
    
    def _generate_transaction_data(self) -> Dict[str, Any]:
        """Generate realistic Bitcoin transaction data"""
        tx_hash = ''.join(random.choices('0123456789abcdef', k=64))
        vin_sz = random.randint(1, 5)
        vout_sz = random.randint(1, 5)
        size = random.randint(200, 1000)
        fee = random.randint(1000, 50000)
        current_time = int(time.time())
        
        # Generate realistic Bitcoin addresses
        def generate_address():
            return ''.join(random.choices('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz', k=34))
        
        # Generate inputs
        inputs_list = []
        for _ in range(vin_sz):
            inputs_list.append({
                "prev_out": {
                    "addr": generate_address(),
                    "value": random.randint(100000, 100000000)  # Satoshis
                },
                "scriptSig": ''.join(random.choices('0123456789abcdef', k=random.randint(20, 100))),
                "sequence": random.randint(0, 4294967295)
            })
        
        # Generate outputs
        outputs_list = []
        total_input_value = sum(inp["prev_out"]["value"] for inp in inputs_list)
        remaining_value = total_input_value - fee
        
        for i in range(vout_sz):
            if i == vout_sz - 1:  # Last output gets remaining value
                value = max(remaining_value, 0)
            else:
                value = random.randint(1000, remaining_value // 2) if remaining_value > 0 else 0
                remaining_value -= value
            
            outputs_list.append({
                "addr": generate_address(),
                "value": value,
                "script": ''.join(random.choices('0123456789abcdef', k=random.randint(20, 50))),
                "spent": False
            })
        
        return {
            "hash": tx_hash,
            "ver": 1,
            "vin_sz": vin_sz,
            "vout_sz": vout_sz,
            "size": size,
            "weight": size * 4,  # Approximation for SegWit
            "fee": fee,
            "relayed_by": "0.0.0.0",
            "lock_time": 0,
            "tx_index": random.randint(1, 1000000),
            "double_spend": False,
            "time": current_time,
            "block_height": random.randint(800000, 820000),  # Recent block heights
            "inputs": json.dumps(inputs_list),
            "out": json.dumps(outputs_list)
        }
    
    def _log_stats(self):
        """Log current statistics"""
        logger.info(f"📊 Data Generator Stats - Sent: {self.stats['messages_sent']}, "
                   f"Failed: {self.stats['messages_failed']}, "
                   f"Reconnections: {self.stats['reconnections']}")
        if self.stats['messages_sent'] > 0:
            logger.info(f"✅ Data is flowing! Last transaction sent successfully.")
    
    def run(self):
        """Main producer loop"""
        logger.info(f"🚀 Starting data generator - Producing {PRODUCER_RATE} transaction/sec")
        logger.info(f"📡 Target: {self.broker} -> Topic: {self.topic}")
        
        # Initial connection
        if not self._connect_with_retry():
            logger.error("❌ Failed to establish initial Kafka connection")
            sys.exit(1)
        
        logger.info("✅ Data generator ready! Starting to produce transactions...")
        
        message_interval = 1.0 / PRODUCER_RATE if PRODUCER_RATE > 0 else 1.0
        last_stats_time = time.time()
        
        try:
            while self.is_running:
                start_time = time.time()
                
                # Ensure we have a connection
                if not self._ensure_connected():
                    logger.error("Unable to maintain Kafka connection")
                    time.sleep(5)
                    continue
                
                # Generate and send transaction data
                try:
                    transaction_data = self._generate_transaction_data()
                    success = self._send_message_with_circuit_breaker(transaction_data)
                    
                    if not success:
                        logger.warning("Failed to send message, continuing...")
                
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}")
                    self.stats['messages_failed'] += 1
                
                # Log stats every 30 seconds
                if time.time() - last_stats_time > 30:
                    self._log_stats()
                    last_stats_time = time.time()
                
                # Rate limiting
                elapsed = time.time() - start_time
                sleep_time = max(0, message_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        self._log_stats()
        self._close_producer()
        logger.info("Shutdown complete")

def main():
    """Main entry point"""
    logger.info("=== Robust Kafka Producer Starting ===")
    logger.info(f"Configuration:")
    logger.info(f"  Kafka Broker: {KAFKA_BROKER}")
    logger.info(f"  Topic: {KAFKA_TOPIC}")
    logger.info(f"  Rate: {PRODUCER_RATE} messages/second")
    logger.info(f"  Max Retries: {MAX_RETRIES}")
    logger.info(f"  Circuit Breaker Threshold: {CIRCUIT_BREAKER_THRESHOLD}")
    
    producer = RobustKafkaProducer(KAFKA_BROKER, KAFKA_TOPIC)
    
    try:
        producer.run()
    except Exception as e:
        logger.error(f"Fatal error in producer: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
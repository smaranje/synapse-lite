# data/bitcoin_mempool_consumer.py
# This script connects to the Blockchain.com WebSocket API to stream
# real-time Bitcoin mempool (unconfirmed) transactions and publishes them to Kafka.

import websocket # Library for WebSocket client
import json      # For JSON parsing and serialization
import time      # For sleep and timestamping
import os        # For environment variables
from kafka import KafkaProducer # Kafka Python client

# --- Configuration ---
# Kafka broker address: 'kafka' is the service name in docker-compose.yml,
# Docker's internal DNS resolves this to the Kafka container's IP.
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
# Kafka topic to publish transaction data to. This should match what Spark consumes.
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')

# Blockchain.com WebSocket API endpoint for unconfirmed transactions
WEBSOCKET_URL = "wss://ws.blockchain.info/inv"

# --- Kafka Producer Setup ---
# Initialize Kafka Producer to send messages to the configured broker.
# value_serializer: Converts Python dictionaries to JSON strings encoded as UTF-8 bytes,
# which is the format Kafka expects for JSON messages.
# api_version: Specifies the Kafka API version for compatibility.
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
    print(f"Kafka Producer connected to {KAFKA_BROKER} for topic {KAFKA_TOPIC}")
except Exception as e:
    print(f"ERROR: Could not connect to Kafka Producer: {e}")
    # Exit if Kafka connection fails, as we cannot send data without it.
    exit(1)

# --- WebSocket Callbacks ---
# This function is called when a message is received from the WebSocket.
def on_message(ws, message):
    try:
        data = json.loads(message)
        # Check if the message contains unconfirmed transaction data.
        # Blockchain.com's 'inv' stream sends transaction data in 'x' field.
        if data.get('op') == 'utx' and 'x' in data:
            transaction_details = data['x']

            # --- ADDED FOR DEBUGGING: Print the transaction details to see its structure ---
            # IMPORTANT: Remove this line after you've captured a sample JSON output
            # to avoid excessive logging in your production-like demo.
            print(json.dumps(transaction_details, indent=2))
            # -----------------------------------------------------------------------------

            # Add a processing timestamp for tracking within the pipeline
            transaction_details['producer_timestamp_ms'] = int(time.time() * 1000)

            # Send the parsed transaction details to Kafka.
            # The 'future' object allows waiting for acknowledgment, though for high-volume
            # streams, you might send asynchronously and handle failures differently.
            future = producer.send(KAFKA_TOPIC, value=transaction_details)
            record_metadata = future.get(timeout=10) # Block for 10 seconds to ensure send

            # Optional: Print confirmation of sent message.
            # print(f"Sent Bitcoin transaction {transaction_details.get('hash', 'N/A')} to Kafka.")
        elif data.get('op') == 'pong':
            # Handle pong messages if needed to keep connection alive, or ignore.
            pass
        # Add more 'elif' for other message types you might want to handle,
        # e.g., 'block' for new blocks being mined.
    except json.JSONDecodeError as e:
        print(f"WARNING: Could not decode JSON message: {e} - Message: {message[:100]}...")
    except Exception as e:
        print(f"ERROR: An error occurred processing WebSocket message: {e}")

# This function is called if a WebSocket error occurs.
def on_error(ws, error):
    print(f"WebSocket Error: {error}")

# This function is called when the WebSocket connection is closed.
def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket Closed: Status Code: {close_status_code}, Message: {close_msg}")
    # Attempt to reconnect after a delay, especially for a data generator service.
    print("Attempting to reconnect to WebSocket in 5 seconds...")
    time.sleep(5)
    start_websocket_stream() # Call the function to re-establish connection

# This function is called when the WebSocket connection is successfully opened.
def on_open(ws):
    print("WebSocket connection opened. Subscribing to unconfirmed transactions...")
    # Subscribe to unconfirmed transactions (mempool).
    # The 'op': 'unconfirmed_sub' operation subscribes to new unconfirmed transactions.
    ws.send(json.dumps({"op": "unconfirmed_sub"}))
    # You could also subscribe to new blocks: ws.send(json.dumps({"op":"blocks_sub"}))

# --- Main WebSocket Connection Logic ---
def start_websocket_stream():
    # Create a WebSocketApp instance with the defined callbacks.
    # The 'run_forever()' method will keep the connection alive, handling messages
    # and automatic re-connection attempts based on on_close logic.
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    # This loop ensures that if the connection closes (e.g., network issue),
    # the on_close callback will trigger a reconnection attempt.
    while True:
        try:
            ws.run_forever(ping_interval=30, ping_timeout=10) # Send pings to keep connection alive
        except Exception as e:
            print(f"Main WebSocket loop error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# --- Entry Point ---
if __name__ == "__main__":
    print(f"Starting Bitcoin Mempool Consumer, connecting to {WEBSOCKET_URL}...")
    # This ensures the 'websocket-client' library is installed.
    # This check is primarily for local testing; Dockerfile handles installation.
    try:
        import websocket
    except ImportError:
        print("Please install 'websocket-client' library: pip install websocket-client")
        exit(1)

    start_websocket_stream()
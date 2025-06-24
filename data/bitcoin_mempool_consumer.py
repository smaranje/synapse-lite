# data/bitcoin_mempool_consumer.py
import json
import time
import random

# Extended list of more realistic-looking addresses
PREFIXES = ["1", "3", "bc1q", "bc1p"]
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def generate_bitcoin_address():
    prefix = random.choice(PREFIXES)
    # Generate 26-42 random characters for the rest of the address
    suffix_length = random.randint(26, 42)
    suffix = ''.join(random.choice(CHARS) for _ in range(suffix_length))
    return prefix + suffix

def generate_synthetic_transaction():
    tx_hash = ''.join(random.choices('0123456789abcdef', k=64))
    tx_size = random.randint(200, 1000) # bytes
    tx_weight = tx_size * 4 # roughly 4x size
    tx_fee = random.randint(1000, 50000) # satoshis

    num_inputs = random.choices([1, 2, 3, 5, 10, 20], weights=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02], k=1)[0]
    num_outputs = random.choices([1, 2, 3, 5, 10, 20, 30], weights=[0.5, 0.2, 0.1, 0.08, 0.05, 0.04, 0.03], k=1)[0]

    vin = []
    total_input_value = 0
    for _ in range(num_inputs):
        sender_addr = generate_bitcoin_address()
        input_value = random.randint(100000, 100000000) # Larger value for inputs
        total_input_value += input_value
        vin.append({
            "txid": ''.join(random.choices('0123456789abcdef', k=64)),
            "vout": random.randint(0, 5),
            "scriptSig": {"asm": "...", "hex": "..."},
            "sequence": 4294967295,
            "witness": [],
            "value": float(input_value), # Use float for value
            "prev_out": {
                "spent": False,
                "tx_index": random.randint(1, 100000),
                "type": 0,
                "addr": sender_addr,
                "value": input_value,
                "n": random.randint(0, 5),
                "script": "..."
            }
        })

    vout = []
    total_output_value = 0
    for _ in range(num_outputs):
        receiver_addr = generate_bitcoin_address()
        output_value = random.randint(10000, 50000000) # Smaller value for outputs
        total_output_value += output_value
        vout.append({
            "value": output_value,
            "n": random.randint(0, num_outputs - 1),
            "scriptPubKey": {
                "asm": "...",
                "hex": "...",
                "reqSigs": 1,
                "type": "pubkeyhash",
                "addresses": [receiver_addr]
            }
        })

    # Adjust output values to account for fee and balance inputs/outputs
    # This is a simplification; real Bitcoin transactions are more complex.
    # For now, let's assume the transaction fee is implicitly handled by the difference.
    # To ensure total_input_value >= total_output_value + transaction_fee:
    # If total_output_value is too high, scale it down or increase inputs.
    # For simplicity of synthetic data, ensure total_input_value is large enough.
    # Here, we'll make total_output_value slightly less than total_input_value
    # and the difference will be the transaction_fee.
    total_output_value = total_input_value - tx_fee
    if total_output_value < 0: # Prevent negative output value
        total_output_value = 0
        tx_fee = total_input_value # All input becomes fee

    # Redistribute total_output_value among actual outputs
    if vout:
        remaining_value = total_output_value
        for i in range(len(vout)):
            if i == len(vout) - 1: # Last output takes the rest
                vout[i]['value'] = remaining_value
            else:
                share = random.randint(1, remaining_value // (len(vout) - i) + 1) if (len(vout) - i) > 0 else 0
                vout[i]['value'] = share
                remaining_value -= share
            if vout[i]['value'] < 0: vout[i]['value'] = 0 # Ensure no negative values

    current_time = int(time.time())

    transaction = {
        "hash": tx_hash,
        "size": tx_size,
        "weight": tx_weight,
        "fee": tx_fee,
        "vin": vin,
        "vout": vout,
        "locktime": 0,
        "ver": 1,
        "relayed_by": "0.0.0.0",
        "time": current_time,
        "block_height": 0, # Placeholder, as it's mempool data
        "double_spend": False,
        "rbf": True,
        "total_input_value": float(total_input_value),
        "total_output_value": float(total_output_value),
        "transaction_fee": float(tx_fee),
        "fee_per_byte": float(tx_fee / tx_size if tx_size > 0 else 0),
        "num_inputs": num_inputs,
        "num_outputs": num_outputs
    }
    return json.dumps(transaction)

if __name__ == "__main__":
    while True:
        transaction_json = generate_synthetic_transaction()
        print(transaction_json, flush=True) # Print to stdout, which Kafka producer consumes
        time.sleep(random.uniform(0.5, 2.0)) # Generate transactions every 0.5 to 2 seconds

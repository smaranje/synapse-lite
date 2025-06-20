# spark_app/fraud_rules.py

def detect_smurfing_rule(transaction):
    """
    A simple rule-based detector for smurfing patterns.
    In a real Neo4j integration, this would involve graph traversals.
    For this demo, we'll just use dummy logic based on amount and account names.
    """
    amount_threshold = 100.0
    transfer_type = "transfer"
    smurfing_keyword = "SMURF"

    if (transaction.get("transaction_type") == transfer_type and
        transaction.get("amount") < amount_threshold):
        sender = transaction.get("sender_account", "")
        receiver = transaction.get("receiver_account", "")
        if smurfing_keyword in sender or smurfing_keyword in receiver:
            return True
    return False

# You can add more rules here
def detect_high_value_transfer(transaction):
    if transaction.get("amount", 0) > 10000:
        return True
    return False

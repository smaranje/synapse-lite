"""
Rule-based fraud detectors used by streaming_app.py
"""

# ------------------------------------------------------------------ #
# 1. Smurfing (structuring) rule
# ------------------------------------------------------------------ #
def detect_smurfing_rule(tx: dict) -> bool:
    """
    Flags transfers < 100 USD where either account
    contains the string “SMURF”.
    """
    if tx.get("transaction_type") != "transfer":
        return False

    amount   = float(tx.get("amount", 0))
    if amount >= 100:
        return False

    sender   = str(tx.get("sender_account", "")).upper()
    receiver = str(tx.get("receiver_account", "")).upper()
    return "SMURF" in sender or "SMURF" in receiver

# ------------------------------------------------------------------ #
# 2. High-value wire rule (example of a second rule)
# ------------------------------------------------------------------ #
def detect_high_value_transfer(tx: dict) -> bool:
    """
    Flags any transaction > 10 000 USD.
    """
    return float(tx.get("amount", 0)) > 10_000

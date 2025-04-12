import time
import subprocess
import json
import uuid
from prettytable import PrettyTable

CHAIN_NAME = "scam-chain"
COIN_NAME = "ScamCoin 7.0"
DISTRIBUTE_AMOUNT = 100000  # amount to distribute to each address
SUSPICION_WINDOW = 30  # seconds for single transaction suspicion window
THRESHOLD_AMOUNT = 50000  # Threshold for suspicious transaction
TIME_THRESHOLD = 300  # 5 minutes threshold for detecting more than 3 transactions
TRANSACTION_THRESHOLD = 3  # If more than 3 transactions within 5 minutes

# Maintain an array to store transaction information
transactions_data = []
sender_mapping = {}  # Mapping from random sender ID to actual address

def run_cli_command(*args):
    """Run multichain-cli commands and return JSON output."""
    command = ["multichain-cli", CHAIN_NAME] + list(args)
    result = subprocess.run(command, stdout=subprocess.PIPE)
    try:
        return json.loads(result.stdout.decode())
    except json.JSONDecodeError:
        return result.stdout.decode()

# Constants
ADDRESS_COUNT = 5
INITIAL_ISSUE_AMOUNT = 500000  # amount for issuing

# Step 1: Get all wallet addresses
print("Fetching existing addresses...")
addresses_response = run_cli_command("listaddresses")

# Extract only the addresses from the response
addresses = [entry["address"] for entry in addresses_response]

print("Addresses fetched:")
print(addresses)

# Step 2: Issue ScamCoin to the first address
print(f"Issuing {INITIAL_ISSUE_AMOUNT} {COIN_NAME} to {addresses[0]}...")
issue_result = run_cli_command("issue", addresses[0], COIN_NAME, str(INITIAL_ISSUE_AMOUNT), "1.0")
print("Issue TXID:", issue_result)

# Wait for confirmation
time.sleep(3)

# Step 3: Distribute 100k ScamCoin to each of the remaining addresses from the first address
print("Distributing tokens to other addresses...")
for addr in addresses[1:]:
    # We are sending the coin from the first address (addresses[0])
    sender = addresses[0]

    # Generate a random sender ID (this will anonymize the sender)
    sender_id = str(uuid.uuid4())

    # Map the random sender ID to the actual address
    sender_mapping[sender_id] = sender

    # Send the token to the recipient address
    tx = run_cli_command("sendassetfrom", sender, addr, COIN_NAME, str(DISTRIBUTE_AMOUNT))

    # Store transaction details with the anonymized sender ID
    transactions_data.append({
        "from": sender_id,  # Store the random sender ID
        "to": addr,
        "amount": DISTRIBUTE_AMOUNT,
        "asset": COIN_NAME,
        "time": time.time(),  # Current timestamp
        "txid": tx
    })
    time.sleep(1)  # simulate a slight delay between transfers

print("Distribution complete.")

print("\n🔍 Detecting suspicious transactions...\n")

# Check transactions for amounts greater than the threshold and within the suspicion window
suspicious_transactions = []

for tx in transactions_data:
    # Only consider transactions with amount greater than the threshold
    if tx["amount"] > THRESHOLD_AMOUNT:
        for record in transactions_data:
            # Skip the current transaction when comparing to others
            if tx == record:
                continue  # Skip the current transaction itself
            
            # If the transaction happens within the suspicion window (e.g., 5 seconds)
            if tx["from"] == record["from"] and abs(tx["time"] - record["time"]) <= SUSPICION_WINDOW:
                suspicious_transactions.append(tx)

# Detect if more than 3 transactions happen within 5 minutes
suspicious_multiple_transactions = []

# Group transactions by anonymized sender ID and check the frequency of transactions
for addr in set(tx["from"] for tx in transactions_data):  # Loop through unique anonymized sender IDs
    # Filter transactions by this anonymized sender ID
    sender_transactions = [tx for tx in transactions_data if tx["from"] == addr]
    
    # Sort the transactions by time
    sender_transactions.sort(key=lambda x: x["time"])

    # Check for more than 3 transactions within 5 minutes
    for i in range(len(sender_transactions) - TRANSACTION_THRESHOLD + 1):
        time_diff = sender_transactions[i + TRANSACTION_THRESHOLD - 1]["time"] - sender_transactions[i]["time"]
        if time_diff <= TIME_THRESHOLD:
            suspicious_multiple_transactions.append(addr)
            break

# Display suspicious transactions
suspicious_table = PrettyTable(["From (Anonymized)", "To", "Amount", "Asset", "Time", "TxID"])

for tx in suspicious_transactions:
    suspicious_table.add_row([tx["from"], tx["to"], tx["amount"], tx["asset"], tx["time"], tx["txid"]])

if suspicious_transactions:
    print("Suspicious Transactions Detected:")
    print(suspicious_table)
else:
    print("No suspicious transactions detected.")

# Display warning if more than 3 transactions have been made by the same anonymized sender ID within 5 minutes
if suspicious_multiple_transactions:
    print("\n🚩 Warning: More than 3 transactions made by the following anonymized sender IDs within 5 minutes:")
    for addr in suspicious_multiple_transactions:
        # The sender ID is anonymized, so we just display the random ID
        print(f"- {addr}")
else:
    print("\nNo multiple transactions detected within 5 minutes.")

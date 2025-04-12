import subprocess
import json
import time
from prettytable import PrettyTable

import time
import subprocess
import json
from prettytable import PrettyTable

CHAIN_NAME = "scam-chain"

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
COIN_NAME = "ScamCoin 4.0"
DISTRIBUTE_AMOUNT = 100000  # amount to distribute to each address
SUSPICION_WINDOW = 30  # seconds for single transaction suspicion window
THRESHOLD_AMOUNT = 50000  # Threshold for suspicious transaction
TIME_THRESHOLD = 300  # 5 minutes threshold for detecting more than 3 transactions
TRANSACTION_THRESHOLD = 3  # If more than 3 transactions within 5 minutes

# Maintain an array to store transaction information
transactions_data = []

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

# Step 3: Distribute 100k ScamCoin to each of the remaining addresses
print("Distributing tokens to other addresses...")
for addr in addresses[1:]:
    tx = run_cli_command("sendassetfrom", addresses[0], addr, COIN_NAME, str(DISTRIBUTE_AMOUNT))
    transactions_data.append({
        "from": addresses[0],
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
            # If the transaction happens within the suspicion window (e.g., 5 seconds)
            if tx["to"] == record["to"] and abs(tx["time"] - record["time"]) <= SUSPICION_WINDOW:
                suspicious_transactions.append(tx)

# Detect if more than 3 transactions happen within 5 minutes
suspicious_multiple_transactions = []

# Group transactions by sender address and check the frequency of transactions
for addr in set(tx["from"] for tx in transactions_data):  # Loop through unique senders
    # Filter transactions by this address
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
suspicious_table = PrettyTable(["From", "To", "Amount", "Asset", "Time", "TxID"])

for tx in suspicious_transactions:
    suspicious_table.add_row([tx["from"], tx["to"], tx["amount"], tx["asset"], tx["time"], tx["txid"]])

if suspicious_transactions:
    print("Suspicious Transactions Detected:")
    print(suspicious_table)
else:
    print("No suspicious transactions detected.")

# Display warning if more than 3 transactions have been made by the same address within 5 minutes
if suspicious_multiple_transactions:
    print("\n🚩 Warning: More than 3 transactions made by the following addresses within 5 minutes:")
    for addr in suspicious_multiple_transactions:
        print(f"- {addr}")
else:
    print("\nNo multiple transactions detected within 5 minutes.")


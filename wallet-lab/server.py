from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)
MULTICHAIN_RPC = "http://127.0.0.1:7360"
MULTICHAIN_AUTH = ("multichainrpc", "811ru13gB2N6oxrnm3vktGQUovxoeWRoHwiWLoUcPaJA")
FULL_LEDGER_FILE = "full_ledger.txt"
GLOBAL_LEDGER_FILE = "global_ledger.txt"

# Function to append transaction to a file
def save_transaction(filename, transaction):
    with open(filename, "a") as file:
        file.write(json.dumps(transaction) + "\n")

# Create a transaction on MultiChain
@app.route("/transaction", methods=["POST"])
def create_transaction():
    data = request.json
    required_fields = ["sender", "receiver", "asset", "amount"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400
    
    transaction = {
        "method": "sendassetfrom",
        "params": [data["sender"], data["receiver"], data["asset"], data["amount"]]
    }
    response = requests.post(MULTICHAIN_RPC, auth=MULTICHAIN_AUTH, json=transaction)
    
    if response.status_code == 200:
        tx_id = response.json().get("result")
        transaction_data = {
            "id": tx_id,
            "sender": data["sender"],
            "receiver": data["receiver"],
            "asset": data["asset"],
            "amount": data["amount"],
            "timestamp": datetime.utcnow().isoformat()
        }
        save_transaction(FULL_LEDGER_FILE, transaction_data)
        save_transaction(GLOBAL_LEDGER_FILE, {k: transaction_data[k] for k in ["id", "sender", "receiver", "asset", "amount", "timestamp"]})
        return jsonify({"message": "Transaction added successfully.", "transaction": transaction_data})
    else:
        return jsonify({"error": "Transaction failed."}), 500

# Get full ledger (Admin only)
@app.route("/full-ledger", methods=["GET"])
def get_full_ledger():
    with open(FULL_LEDGER_FILE, "r") as file:
        transactions = [json.loads(line) for line in file]
    return jsonify(transactions)

# Get global ledger summary
@app.route("/global-ledger", methods=["GET"])
def get_global_ledger():
    with open(GLOBAL_LEDGER_FILE, "r") as file:
        transactions = [json.loads(line) for line in file]
    return jsonify(transactions)

if __name__ == "__main__":
    app.run(port=5000)

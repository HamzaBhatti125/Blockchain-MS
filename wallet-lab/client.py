import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
CLIENT_LEDGER_FILE = "client_ledger.txt"
SERVER_URL = "http://localhost:5000"

# Function to append transaction to a file
def save_transaction(transaction):
    with open(CLIENT_LEDGER_FILE, "a") as file:
        file.write(json.dumps(transaction) + "\n")

# Send transaction request to Full Node
@app.route("/send", methods=["POST"])
def send_transaction():
    data = request.json
    try:
        response = requests.post(f"{SERVER_URL}/transaction", json=data)
        if response.status_code == 200:
            save_transaction(response.json()["transaction"])
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Transaction failed."}), 500

# Get transactions relevant to this client
@app.route("/transactions", methods=["GET"])
def get_client_transactions():
    with open(CLIENT_LEDGER_FILE, "r") as file:
        transactions = [json.loads(line) for line in file]
    return jsonify(transactions)

if __name__ == "__main__":
    app.run(port=5001)

import hashlib
import time
import socket
import threading
import json
import os

# Global flag to stop other servers once a winner is found
winner_found = threading.Event()
ledger_lock = threading.Lock()
num_servers = 3
barrier = threading.Barrier(num_servers)
# Ensure ledger.json is read from the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
ledger_file = os.path.join(script_dir, "ledger.json")


# Load ledger data
try:
    with open(ledger_file, "r") as f:
        ledger = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    ledger = {"clients": [], "transactions": []}  # Initialize empty ledger structure

# Proof of Work function
def proof_of_work(data, difficulty=2):
    nonce = 0
    prefix = '0' * (difficulty * 2)
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start_timestamp = time.time()
    
    while not winner_found.is_set():
        text = f"{data}{nonce}".encode()
        hash_value = hashlib.sha256(text).hexdigest()
        
        if hash_value.startswith(prefix):
            end_timestamp = time.time()
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            time_taken = round(end_timestamp - start_timestamp, 4)
            return nonce, hash_value, start_time, end_time, time_taken
        
        nonce += 1
    return None, None, None, None, None

# Verify transaction and register new client if needed
def verify_transaction(transaction):
    try:
        transaction_data = json.loads(transaction)
        client_id = transaction_data.get("clientId")
        message = transaction_data.get("message")

        if not client_id or not message:
            return False, None

        with ledger_lock:

            # Correctly access "clients" inside the ledger dictionary
            valid_client = any(entry.get("clientId") == client_id for entry in ledger.get("clients", []))

        return valid_client, message
    except json.JSONDecodeError:
        return False, None


# Server function
def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", port))
    server.listen(1)
    print(f"Server started on port {port}")

    while True:
        conn, addr = server.accept()
        message = conn.recv(1024).decode()
        print(f"Received transaction '{message}' on port {port}")

        valid, transaction_message = verify_transaction(message)
        if not valid:
            conn.sendall("❌ Invalid or Unauthorized Transaction".encode())
            conn.close()
            continue

        barrier.wait()
        
        nonce, final_hash, start_time, end_time, time_taken = proof_of_work(transaction_message, difficulty=2)
        
        if nonce is not None:
            winner_found.set()
            with ledger_lock:
                ledger["transactions"].append({
                    "server": port,
                    "transaction": transaction_message,
                    "nonce": nonce,
                    "hash": final_hash,
                    "timestamp": end_time
                })
                with open(ledger_file, "w") as f:
                    json.dump(ledger, f, indent=4)

            response = (f"\U0001F3C6 Winner Found on {port}\n"
                        f"➡ Start Time: {start_time}\n"
                        f"➡ End Time: {end_time}\n"
                        f"➡ Computational Time: {time_taken} seconds\n"
                        f"➡ Nonce: {nonce}\n"
                        f"➡ Hash: {final_hash}")
            conn.sendall(response.encode())
        else:
            conn.sendall("⏹ Mining Stopped (Another Server Won)".encode())
        
        conn.close()

# Start server threads
server_ports = [5000, 5001, 5002]
for port in server_ports:
    threading.Thread(target=start_server, args=(port,), daemon=True).start()

# Client function to send transaction
def send_transaction(client_id, message):
    transaction_data = json.dumps({"clientId": client_id, "message": message})
    responses = []
    threads = []

    def client_thread(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(("localhost", port))
            client.sendall(transaction_data.encode())
            response = client.recv(1024).decode()
            responses.append(response)

    for port in server_ports:
        t = threading.Thread(target=client_thread, args=(port,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n" + "=" * 50)
    for response in responses:
        print(response)
        print("-" * 50)

# Example Usage
time.sleep(1)
client_id = "12345"  # If not in ledger.json, it will be added dynamically
transaction_message = "Hello"
send_transaction(client_id, transaction_message)

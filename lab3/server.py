import hashlib
import time
import socket
import threading

# Proof of Work function
def proof_of_work(data, difficulty=2):
    """
    A simple Proof of Work function that finds a nonce
    such that the hash has `difficulty` leading zero pairs.
    
    :param data: The transaction data or block data to be hashed
    :param difficulty: Number of leading zero pairs (e.g., difficulty=2 means "0000" at the start)
    :return: (nonce, hash_value, start_time, end_time, time_taken)
    """
    nonce = 0
    prefix = '0' * (difficulty * 2)  # Two zeros per difficulty level
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # Start timestamp
    start_timestamp = time.time()
    
    while True:
        text = f"{data}{nonce}".encode()
        hash_value = hashlib.sha256(text).hexdigest()
        
        if hash_value.startswith(prefix):
            end_timestamp = time.time()
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # End timestamp
            time_taken = round(end_timestamp - start_timestamp, 4)
            return nonce, hash_value, start_time, end_time, time_taken  # Return results
        
        nonce += 1  # Increment nonce and retry

# Barrier to synchronize all servers
num_servers = 3
barrier = threading.Barrier(num_servers)

# Server function
def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", port))
    server.listen(1)
    print(f"Server started on port {port}")

    while True:
        conn, addr = server.accept()
        message = conn.recv(1024).decode()
        print(f"Received message '{message}' on port {port}")

        # Wait for all nodes before starting PoW
        barrier.wait()
        
        # Run Proof of Work
        nonce, final_hash, start_time, end_time, time_taken = proof_of_work(message, difficulty=2)
        
        # Prepare response
        response = (f"✅ PoW Completed on {port}\n"
                    f"➡ Start Time: {start_time}\n"
                    f"➡ End Time: {end_time}\n"
                    f"➡ Computational Time: {time_taken} seconds\n"
                    f"➡ Nonce: {nonce}\n"
                    f"➡ Hash: {final_hash}")
        
        conn.sendall(response.encode())
        conn.close()

# Create server threads for ports 5000, 5001, and 5002
server_ports = [5000, 5001, 5002]
for port in server_ports:
    threading.Thread(target=start_server, args=(port,), daemon=True).start()

# Client function to send message to all servers and receive PoW results
def send_message_to_servers(message):
    responses = []
    threads = []

    def client_thread(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(("localhost", port))
            client.sendall(message.encode())
            response = client.recv(1024).decode()
            responses.append(response)

    # Start client threads
    for port in server_ports:
        t = threading.Thread(target=client_thread, args=(port,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Print all responses together
    print("\n" + "=" * 50)
    for response in responses:
        print(response)
        print("-" * 50)

# Example Usage (send message to all servers)
time.sleep(1)  # Allow servers to start properly
message = "Shahbaz"
send_message_to_servers(message)

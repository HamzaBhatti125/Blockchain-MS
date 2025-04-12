import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
import json
import binascii
from statistics import mean
from prettytable import PrettyTable  # pip install prettytable

from blockchain.multichain_api import MultichainAPI
from config.config import MULTICHAIN_NODES

results_lock = threading.Lock()
metrics = []  # Global to store results for table

def send_requests(node_name, request_count, delay_ms, stream_name, key, data_hex, round_num):
    main_node_config = MULTICHAIN_NODES['main_node']
    api = MultichainAPI(main_node_config['url'], main_node_config['user'], main_node_config['password'])

    access_times = []

    def worker(i):
        start_time = time.time()
        try:
            result = api.publish_to_blockchain(stream_name, f"{key}_{node_name}_{i}", data_hex)
            end_time = time.time()
            elapsed = (end_time - start_time) * 1000  # ms
            access_times.append(elapsed)
            print(f"✓ {node_name} sent request {i+1}: {result} [{elapsed:.2f} ms]")
        except Exception as e:
            end_time = time.time()
            elapsed = (end_time - start_time) * 1000
            access_times.append(elapsed)
            print(f"⚠ {node_name} failed request {i+1}: {e} [{elapsed:.2f} ms]")

    threads = []
    for i in range(request_count):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(delay_ms / 1000.0)  # Delay between requests

    for t in threads:
        t.join()

    with results_lock:
        metrics.append({
            "round": round_num,
            "node": node_name,
            "requests": request_count,
            "access_time": mean(access_times) if access_times else 0.0,
            "response_time": mean(access_times)  # assuming equal for now
        })


def run_round(round_num, request_count, delay_ms):
    stream_name = "contract-stream"
    base_data = {
        "round": round_num,
        "status": "test-request"
    }
    data_json = json.dumps(base_data)
    data_hex = binascii.hexlify(data_json.encode()).decode()

    print(f"\n🚀 Starting Round {round_num} with {request_count} requests per node, delay: {delay_ms}ms")

    threads = []
    for node_name in ['NodeA', 'NodeB', 'NodeC']:
        t = threading.Thread(target=send_requests, args=(
            node_name, request_count, delay_ms, stream_name, "testkey", data_hex, round_num
        ))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"✅ Completed Round {round_num}\n")


def print_summary_table():
    table = PrettyTable()
    table.field_names = ["Round", "Node", "No. of Requests", "Avg Access Time (ms)", "Avg Response Time (ms)"]

    for m in metrics:
        table.add_row([
            m["round"], m["node"], m["requests"],
            f"{m['access_time']:.2f}", f"{m['response_time']:.2f}"
        ])

    print("\n📊 Performance Summary Table:")
    print(table)


if __name__ == "__main__":
    run_round(round_num=1, request_count=100, delay_ms=600)
    run_round(round_num=2, request_count=200, delay_ms=120)
    # run_round(round_num=3, request_count=..., delay_ms=90)  # Optional

    print_summary_table()

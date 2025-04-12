import threading
from blockchain.multichain_api import MultichainAPI
from config.config import MULTICHAIN_NODES

def publish_to_node(name, node_config, stream_name, key, hex_data):
    try:
        api = MultichainAPI(node_config['url'], node_config['user'], node_config['password'])
        result = api.publish_to_blockchain(stream_name, key, hex_data)
        print(f"✓ Published to {name} at {node_config['url']}: {result}")
    except Exception as e:
        print(f"⚠ Failed to publish to {name}: {e}")

def replicate_contract_to_other_nodes(stream_name, key, hex_data):
    other_nodes = {k: v for k, v in MULTICHAIN_NODES.items() if k != 'main_node'}

    threads = []
    for name, node in other_nodes.items():
        thread = threading.Thread(target=publish_to_node, args=(name, node, stream_name, key, hex_data))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

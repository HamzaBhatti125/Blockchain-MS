from blockchain.multichain_api import MultichainAPI
from config.config import MULTICHAIN_RPC_URL, MULTICHAIN_RPC_USER, MULTICHAIN_RPC_PASSWORD

def publish_to_blockchain(message, signature):
    # Interact with Multichain and publish the message
    multichain_api = MultichainAPI(MULTICHAIN_RPC_URL, MULTICHAIN_RPC_USER, MULTICHAIN_RPC_PASSWORD)
    result = multichain_api.publish_to_blockchain(message, signature)
    return result

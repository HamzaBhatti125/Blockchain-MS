from web3 import Web3
from solcx import compile_source
from config.config import CONTRACT_ADDRESS

def deploy_contract(contract_source_code):
    # You will need to compile the smart contract source code and interact with the Ethereum network
    # This example uses Web3.py to deploy contracts
    
    web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    web3.eth.default_account = web3.eth.accounts[0]
    
    # compiled_contract = compile_source(contract_source_code)  # You'll need to compile your contract
    
    # contract = web3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])

    compiled_sol = compile_source(contract_source_code)
    contract_id, contract_interface = compiled_sol.popitem()

    contract = web3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
    )
    
    tx_hash = contract.constructor().transact()
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contract deployed at address: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

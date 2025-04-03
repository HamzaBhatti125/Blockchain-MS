from blockchain.smart_contract import deploy_contract

with open("contracts/SmartContract.sol", "r") as file:
    contract_source_code = file.read()

contract_address = deploy_contract(contract_source_code)
print(f"Deployed contract at: {contract_address}")

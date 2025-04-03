import os
from openai_api.prompt_generator import get_generated_contract
from blockchain.smart_contract import deploy_contract

def deploy_smart_contract(fare, route_id, occupancy):
    smart_contract_code = get_generated_contract(fare, route_id, occupancy)
    return deploy_contract(smart_contract_code)

def save_contract_to_file(contract_code: str, filename: str = "contracts/Contract.sol"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(contract_code)

def load_contract_from_file(filename: str = "contracts/Contract.sol") -> str:
    with open(filename, "r") as f:
        return f.read()
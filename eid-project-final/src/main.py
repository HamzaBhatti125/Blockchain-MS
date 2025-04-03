import json
import binascii
from solcx import install_solc, set_solc_version
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from fare_prediction import predict_fare
from openai_api.prompt_generator import get_generated_contract
from blockchain.smart_contract import deploy_contract
from train_model import train_and_save_model
from blockchain.multichain_api import MultichainAPI
from config.config import MULTICHAIN_RPC_URL, MULTICHAIN_RPC_USER, MULTICHAIN_RPC_PASSWORD
from smart_contract_deployment import save_contract_to_file, load_contract_from_file

def main():
    train_and_save_model()
    # Sample input data
    input_data = {
        'x1_hour': 8, 'x2_passenger_count': 85, 'x3_vehicle_count': 3, 'x4_weather_condition': 1,
        'x5_day_type': 0, 'occupancy_rate': 0.48, 'dayofweek': 1
    }

    # Step 1: Predict the fare using the trained model
    fare = predict_fare(input_data)
    print(f"Predicted fare: {fare}")

    # Step 2: Generate a smart contract based on the predicted fare
    route_id = "route_123"
    occupancy = 107

    # # Install the latest version of solc (replace with the specific version you need)
    # solcx.install_solc("0.8.19")  # Replace with the desired version

    install_solc('0.8.20')  # Or any version your contract needs
    set_solc_version('0.8.20')

    smart_contract_code = get_generated_contract(fare, route_id, occupancy)

    # Save the generated contract to a file
    save_contract_to_file(smart_contract_code)
    
    # Load the contract from the file (if needed)
    smart_contract_code = load_contract_from_file()

    # Step 3: Deploy the generated smart contract on Multichain
    deployed_contract_address = deploy_contract(smart_contract_code)
    
    # Step 4: Send the contract address to the blockchain (if necessary)
    multichain_api = MultichainAPI(MULTICHAIN_RPC_URL, MULTICHAIN_RPC_USER, MULTICHAIN_RPC_PASSWORD)
    message = {
        "contract_address": deployed_contract_address,
        "fare": fare,
        "route_id": route_id,
    }

    # Convert message to JSON format
    data = json.dumps(message)  # The data is the serialized message in JSON format
    message_hex = binascii.hexlify(data.encode('utf-8')).decode('utf-8')


    
    # Publish the message to the blockchain (e.g., vehicle node publishing contract details)
    result = multichain_api.publish_to_blockchain("contract-stream", deployed_contract_address,message_hex)

    print(f"Message with contract address published to blockchain: {result}")

    subscription = multichain_api.list_stream_items("contract-stream", deployed_contract_address)
    print(f"Subscription result: {subscription}")

if __name__ == "__main__":
    main()

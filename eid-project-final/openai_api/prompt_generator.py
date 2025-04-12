from dotenv import load_dotenv
import os
import time
import cohere
# from openai import OpenAI, APIError, RateLimitError

load_dotenv()

co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))
# client = OpenAI(api_key=OPENAI_API_KEY)


def generate_prompt(fare, route_id, occupancy):
   prompt = """
    Generate a simple Solidity smart contract for Multichain that adjusts the fare dynamically for route {route_id}:

    - Current Occupancy: {occupancy} passengers
    - Predicted Fare: {fare}

    Contract Requirements:

    - Implement a function to adjust the fare based on the number of passengers (occupancy).
    - Include a function for administrators to manually adjust the fare.
    - Use a constant for precision (such as 10^18) for converting decimal values into wei.
    - Implement all logic in native Solidity without using external libraries or complex security mechanisms.
    - The contract should be simple, easy to understand, and focused on the functionality of dynamic fare adjustment.
    - The adjustFare function should increase the fare when occupancy is high and decrease it when occupancy is low.
    - Include a function to set the predicted fare, converted from a decimal number (e.g., 0.3027901777605441 ETH) to wei.
    - Include a function to adjust the fare dynamically based on occupancy, increasing it by a fixed amount for every 100 passengers.
    """
   
   return prompt

def get_generated_contract(fare, route_id, occupancy, retries=5):
    prompt = generate_prompt(fare, route_id, occupancy)

    # for i in range(retries):
    #     try:
    #         # response = client.chat.completions.create(
    #         #     model="gpt-3.5-turbo",
    #         #     messages=[
    #         #         {"role": "system", "content": "You are a smart contract generator for blockchain applications."},
    #         #         {"role": "user", "content": prompt}
    #         #     ],
    #         #     temperature=0.7,
    #         #     max_tokens=800
    #         # )
    #         # return response.choices[0].message.content
        
    #         response = client.chat.completions.create(
    #               model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "user", "content": prompt}
    #         ],
    #         max_tokens=800
    #         )
    #         print(response.headers)  # <--- This may show your limit info (on some responses)

    #     except RateLimitError as e:
    #         wait = 2 ** i
    #         print(f"⚠️ Rate limit hit. Retrying in {wait} seconds... {e}")
    #         time.sleep(wait)
    #     except APIError as e:
    #         print(f"🚨 API error occurred: {e}")
    #         break
    #     except Exception as e:
    #         print(f"❌ Unexpected error: {e}")
    #         break

    # raise Exception("❌ Failed to generate contract after multiple retries.")

    response = co.chat(
    model="command-a-03-2025", 
    messages=[{"role": "user", "content": prompt}]
)

    # Extract the smart contract code (text) from the response content
    response_content = response.message.content[0].text
    
    # Return only the code part (Solidity contract)
    start_index = response_content.find("```solidity") + len("```solidity")
    end_index = response_content.find("```", start_index)

    # Extract the code without the "```solidity" block
    smart_contract_code = response_content[start_index:end_index].strip()

    
    return smart_contract_code
import subprocess
import rsa
import json
import base64
import binascii
import uuid
import random

# Caesar Cipher for blinding
def caesar_encrypt(text, shift=3):
    return ''.join(chr(ord(c) + shift) for c in text)

def caesar_decrypt(text, shift=3):
    return ''.join(chr(ord(c) - shift) for c in text)

# RSA Key Generation
def generate_key_pair():
    return rsa.newkeys(2048)

# Signing & Verification
def sign_message(message, private_key):
    return base64.b64encode(rsa.sign(message.encode(), private_key, 'SHA-256')).decode()

def verify_signature(message, signature, public_key):
    try:
        rsa.verify(message.encode(), base64.b64decode(signature), public_key)
        return True
    except rsa.VerificationError:
        return False

# Multichain Helpers
def multichain_cmd(*args):
    cmd = ['multichain-cli', 'network-chain'] + list(args)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error: {result.stderr.strip()}")
    return result.stdout.strip()

def publish_to_stream(stream, key, json_data):
    data = json.dumps(json_data)  # The data is the serialized message in JSON format
    message_hex = binascii.hexlify(data.encode('utf-8')).decode('utf-8')
    return multichain_cmd('publish', stream, key, message_hex)

def read_from_stream(stream, key):
    output = multichain_cmd('liststreamkeyitems', stream, key)
    items = json.loads(output)
    return json.loads(bytes.fromhex(items[0]['data']).decode())

def get_multichain_addresses():
    output = multichain_cmd('getaddresses')
    return json.loads(output)


# === DEMO ===
if __name__ == "__main__":
    # Key pairs
    pubA, privA = generate_key_pair()
    pubB, privB = generate_key_pair()
    pubSigner, privSigner = generate_key_pair()

   # Fetch the first three addresses
    addresses = get_multichain_addresses()
    alice_address = addresses[0]
    bob_address = addresses[1]
    signer_address = addresses[2]
    print("Alice Address:", alice_address)
    print("Bob Address:", bob_address)
    print("Signer Address:", signer_address)

    # Convert Public Keys to strings
    pubSigner_str = pubSigner

    # Step 1: Encrypt and sign
    original_message = f"Send 50 coins from {alice_address} to {bob_address}"
    blinded_message = caesar_encrypt(original_message)
    signature = sign_message(blinded_message, privSigner)

    # Step 2: Publish to Signer's stream
    tx_data = {
        "from": signer_address,
        "to": alice_address,
        "blindedMessage": blinded_message,
        "signature": signature,
    }

    

    random_key = f"tx-{uuid.uuid4().hex[:8]}"

    try:
        txid_signer = publish_to_stream("signer-stream", random_key, tx_data)
        print("Published to Signer Stream:", txid_signer)
    except Exception as e:
        print("Multichain Publish Error:", e)
        exit()

    # Step 3: Read & verify the signed message from Signer Stream
    try:
        tx = read_from_stream("signer-stream", random_key)
        # Load the public key from the string
        pubSigner_loaded = pubSigner
        
        is_valid = verify_signature(tx['blindedMessage'], tx['signature'], pubSigner_loaded)
        decrypted = caesar_decrypt(tx['blindedMessage'])

        print("Decrypted Message:", decrypted)
        print("Signature Verified:", is_valid)

        if not is_valid:
            raise ValueError("Invalid signature. Transaction cannot proceed.")

        # Step 4: Alice publishes the signed message to her stream
        tx_data_alice = {
            "from": alice_address,
            "to": bob_address,
            "blindedMessage": tx['blindedMessage'],
            "signature": tx['signature']
        }

        random_key_alice = f"tx-{uuid.uuid4().hex[:8]}"

        try:
            txid_alice = publish_to_stream("alice-stream", random_key_alice, tx_data_alice)
            print("Published to Alice Stream:", txid_alice)
        except Exception as e:
            print("Error publishing to Alice Stream:", e)
            exit()

        # Step 5: Read & verify the signed message from Alice's Stream
        tx_alice = read_from_stream("alice-stream", random_key_alice)
        is_valid_alice = verify_signature(tx_alice['blindedMessage'], tx_alice['signature'], pubSigner_loaded)
        decrypted_alice = caesar_decrypt(tx_alice['blindedMessage'])

        print("Decrypted Message from Alice:", decrypted_alice)
        print("Signature Verified from Alice Stream:", is_valid_alice)

        if not is_valid_alice:
            raise ValueError("Invalid signature from Alice's stream. Transaction cannot proceed.")

        # Step 6: Instead of transferring coin, publish "Coin transferred" message to Bob's stream
        tx_data_bob = {
            "from": alice_address,
            "to": bob_address,
            "message": "Coin transferred"
        }

        random_key_bob = f"tx-{uuid.uuid4().hex[:8]}"
        try:
            txid_bob = publish_to_stream("bob-stream", random_key_bob, tx_data_bob)
            print("Published to Bob Stream: Coin transferred message", txid_bob)
        except Exception as e:
            print("Error publishing to Bob Stream:", e)
            exit()

    except Exception as e:
        print("Error during the process:", e)

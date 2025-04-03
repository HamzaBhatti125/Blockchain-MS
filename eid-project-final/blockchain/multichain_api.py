import requests

class MultichainAPI:
    def __init__(self, rpc_url, rpc_user, rpc_password):
        self.rpc_url = rpc_url
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password

    def _send_request(self, method, params=None):
        headers = {'Content-Type': 'application/json'}
        data = {
            "method": method,
            "params": params if params else [],
            "jsonrpc": "2.0",
            "id": 1
        }
        response = requests.post(self.rpc_url, json=data, headers=headers, auth=(self.rpc_user, self.rpc_password))
        return response.json()

    def publish_to_blockchain(self, stream_identifier, key, data, options=None):
    # Constructing the parameters based on the expected API format
        params = [stream_identifier, key, data, options] if options else [stream_identifier, key, data]
        return self._send_request("publish", params)
    
    def list_stream_items(self, stream_identifier, key):
        params = [stream_identifier, key]
        return self._send_request("liststreamkeyitems", params)

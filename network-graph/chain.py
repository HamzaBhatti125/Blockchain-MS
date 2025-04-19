import subprocess
import networkx as nx
import matplotlib.pyplot as plt
import json

chain_name = "network-chain"

def get_new_address(chain_name):
    cmd = ['multichain-cli', chain_name, 'getnewaddress']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()


def get_created_address(chain_name):
    cmd = ['multichain-cli', chain_name, 'getaddresses']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout.strip())  # Parse the string to a Python list
    else:
        print("Error getting addresses:", result.stderr.strip())
        return []

def send_tokens(chain_name, from_addr, to_addr, amount):
    cmd = ['multichain-cli', chain_name, 'sendfrom', from_addr, to_addr, str(amount)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

# Step 1: Generate 10 addresses
addresses = get_created_address(chain_name)
print(f"Addresses: {addresses}")

# Step 2: Connect first address to the others in a graph
G = nx.DiGraph()
G.add_nodes_from(addresses)
edges = [(addresses[0], addr) for addr in addresses[1:]]
G.add_edges_from(edges)

# Step 3: Send small transactions (optional, uncomment to execute)
# for addr in addresses[1:]:
#     tx = send_tokens(chain_name, addresses[0], addr, 0.01)
#     print(f"Sent 0.01 from {addresses[0]} to {addr}: {tx}")

# Step 4: Visualize
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=8, arrows=True)
# plt.title("Multichain Address Graph (Node 0 → Others)")
# plt.show()
plt.savefig("multichain_graph.png", bbox_inches='tight')
print("Graph saved as multichain_graph.png")

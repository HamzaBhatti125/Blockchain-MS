const axios = require("axios");
const { loadLedger } = require("./helper");

const SERVERS = [
  "http://localhost:3001",
  "http://localhost:3002",
  "http://localhost:3003",
];
const clientHash = "abc123"; // Simulated client hash
const message = "Hello, servers!";

// Ensure client exists in ledger
const ledger = loadLedger();
if (!ledger.clients[clientHash]) {
  ledger.clients[clientHash] = true;
  console.log("Client registered in ledger.");
}

// Function to broadcast message and collect verification
async function broadcastMessage() {
  let approvals = 0;

  for (const server of SERVERS) {
    try {
      const response = await axios.post(`${server}/verify`, { clientHash });
      if (response.data.verified) {
        console.log(`${response.data.server} verified client.`);
        approvals++;
      } else {
        console.log(`${response.data.server} rejected client.`);
      }
    } catch (error) {
      console.log(`Failed to reach ${server}`);
    }
  }

  // Send verification results to Server1
  axios
    .post("http://localhost:3001/verify-results", {
      clientHash,
      approvals,
      noOfServers: SERVERS.length,
      msgToWrite: message,
    })
    .then((response) => console.log(response.data.message))
    .catch((err) =>
      console.log("Error sending verification results to Server1", err)
    );
}

// Start the broadcast process
broadcastMessage();

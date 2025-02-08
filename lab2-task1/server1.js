const express = require("express");
const axios = require("axios");
const { addMessageToLedger } = require("./helper");
const { verifyClient } = require("./helper");

const app = express();
app.use(express.json());

const SERVER_NAME = process.env.SERVER_NAME || "Server1";

// Endpoint to verify client and send results to Server1
app.post("/verify", async (req, res) => {
  const { clientHash } = req.body;
  const isValid = verifyClient(clientHash);

  res.json({ server: SERVER_NAME, verified: isValid });
});

// Endpoint to receive verification results
app.post("/verify-results", (req, res) => {
  const { clientHash, approvals, noOfServers, msgToWrite } = req.body;

  if (approvals > noOfServers / 2) {
    addMessageToLedger(clientHash, msgToWrite);
    console.log("Consensus reached! Message added to ledger.");
    res.json({ success: true, message: "Message added to ledger." });
  } else {
    console.log("Consensus failed. Message rejected.");
    res.json({ success: false, message: "Consensus failed." });
  }
});

// Start server
const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Server1 running on port ${PORT}`);
});

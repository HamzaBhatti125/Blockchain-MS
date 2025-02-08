const express = require("express");
const axios = require("axios");
const { verifyClient } = require("./helper");

const app = express();
app.use(express.json());

const SERVER_NAME = process.env.SERVER_NAME || "Verification Server";
const SERVER1_URL = "http://localhost:3001/verify-results";

// Endpoint to verify client and send results to Server1
app.post("/verify", async (req, res) => {
  const { clientHash } = req.body;
  const isValid = verifyClient(clientHash);

  // Send verification result to Server1
  //   try {
  //     await axios.post(SERVER1_URL, { clientHash, approvals: isValid ? 1 : 0 });
  //   } catch (error) {
  //     console.log("Failed to send verification result to Server1");
  //   }

  res.json({ server: SERVER_NAME, verified: isValid });
});

// Start server
const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`${SERVER_NAME} running on port ${PORT}`);
});

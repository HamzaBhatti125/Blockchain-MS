const axios = require("axios");

const SERVER_URL = "http://localhost:3000";

// Function to send data to the server
async function sendData(key, value) {
  try {
    const response = await axios.post(`${SERVER_URL}/store`, { key, value });
    console.log("✅ Data stored successfully:", response.data);
  } catch (error) {
    console.error(
      "❌ Error storing data:",
      error.response?.data || error.message
    );
  }
}

// Function to check ledger integrity
async function verifyLedger() {
  try {
    const response = await axios.get(`${SERVER_URL}/verify`);
    console.log(response.data.message);
  } catch (error) {
    console.error(
      "❌ Ledger integrity check failed:",
      error.response?.data || error.message
    );
  }
}

// Function to attempt tampering (will not affect actual ledger)
async function attemptTampering() {
  try {
    const response = await axios.post(`${SERVER_URL}/tamper`);
    console.log(response.data.message);
  } catch (error) {
    console.error(
      "🚨 Tampering alert!:",
      error.response?.data || error.message
    );
  }
}

// Run tests
async function run() {
  console.log("\n🔹 Storing valid data...");
  await sendData("user1", "balance: 500");
  await sendData("user2", "balance: 1000");

  console.log("\n🔹 Checking ledger integrity...");
  await verifyLedger();

  console.log("\n🔹 Attempting tampering...");
  await attemptTampering();

  console.log("\n🔹 Verifying ledger again...");
  await verifyLedger();
}

run();

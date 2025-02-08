const axios = require("axios");
const crypto = require("crypto");
const { ec } = require("elliptic");

const EC = new ec("secp256k1");

// Generate client A's key pair
const clientAKeyPair = EC.genKeyPair();
const clientAPublicKey = clientAKeyPair.getPublic("hex");

// Generate client B's key pair (attacker)
const clientBKeyPair = EC.genKeyPair();
const clientBPublicKey = clientBKeyPair.getPublic("hex");

console.log("🔹 Client A Public Key:", clientAPublicKey);
console.log("🔹 Client B Public Key:", clientBPublicKey);

// Secret key for encryption (must match between client & server)
const secretKey = "secure_shared_secret";

// Function to encrypt data
function encryptData(data, secretKey) {
  const cipher = crypto.createCipher("aes-256-cbc", secretKey);
  let encrypted = cipher.update(JSON.stringify(data), "utf8", "hex");
  encrypted += cipher.final("hex");
  return encrypted;
}

// Function to decrypt data
function decryptData(encryptedData, secretKey) {
  const decipher = crypto.createDecipher("aes-256-cbc", secretKey);
  let decrypted = decipher.update(encryptedData, "hex", "utf8");
  decrypted += decipher.final("utf8");
  return JSON.parse(decrypted);
}

// Generate a unique coin ID
const coinId = crypto.randomBytes(16).toString("hex");

// Client A signs the coin
const signatureA = clientAKeyPair.sign(coinId).toDER("hex");

// Create the coin
const coin = {
  coinId,
  owner: clientAPublicKey,
  signature: signatureA,
};

console.log("🔹 Created Coin:", coin);

// Encrypt coin data
const encryptedCoin = encryptData(coin, secretKey);

// Function to send the transaction
async function sendTransaction(client, description) {
  try {
    const response = await axios.post("http://localhost:3000/transfer", {
      encryptedCoin,
      secretKey,
    });

    // Decrypt server response
    const updatedCoin = decryptData(response.data.encryptedCoin, secretKey);

    console.log(`\n✅ ${description} Success!`);
    console.log(updatedCoin);
  } catch (error) {
    console.error(
      `❌ ${description} Failed:`,
      error.response?.data || error.message
    );
  }
}

// Execute double-spend attack
(async () => {
  await sendTransaction(clientAKeyPair, "Client A Transfer");
  await sendTransaction(clientBKeyPair, "Client B Double-Spend Attempt");
})();

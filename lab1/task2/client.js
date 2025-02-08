const axios = require("axios");
const crypto = require("crypto");
const { ec } = require("elliptic");

const EC = new ec("secp256k1");

// Generate client key pair
const clientKeyPair = EC.genKeyPair();
const clientPublicKey = clientKeyPair.getPublic("hex");

console.log("🔹 Client Public Key:", clientPublicKey);

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

// Function to create and send a coin
async function createAndSendCoin() {
  // Generate a unique coin ID
  const coinId = crypto.randomBytes(16).toString("hex");

  // Sign the coin with the client's private key
  const signature = clientKeyPair.sign(coinId).toDER("hex");

  // Coin data
  const coin = {
    coinId,
    owner: clientPublicKey,
    signature,
  };

  console.log("🔹 Created Coin:", coin);

  // Encrypt coin data
  const encryptedCoin = encryptData(coin, secretKey);

  // Send to server
  try {
    const response = await axios.post("http://localhost:3000/transfer", {
      encryptedCoin,
      secretKey,
    });

    // Decrypt server response
    const updatedCoin = decryptData(response.data.encryptedCoin, secretKey);

    console.log("\n✅ Coin Ownership Transferred!");
    console.log(updatedCoin);
  } catch (error) {
    console.error(
      "❌ Error transferring coin:",
      error.response?.data || error.message
    );
  }
}

// Execute
createAndSendCoin();

const express = require("express");
const crypto = require("crypto");
const { ec } = require("elliptic");

const app = express();
app.use(express.json());

const EC = new ec("secp256k1");

// Generate server's key pair
const serverKeyPair = EC.genKeyPair();
const serverPublicKey = serverKeyPair.getPublic("hex");

console.log("🔹 Server Public Key:", serverPublicKey);

// Track spent coins
const spentCoins = new Set();

// Function to decrypt data
function decryptData(encryptedData, secretKey) {
  const decipher = crypto.createDecipher("aes-256-cbc", secretKey);
  let decrypted = decipher.update(encryptedData, "hex", "utf8");
  decrypted += decipher.final("utf8");
  return JSON.parse(decrypted);
}

// Function to encrypt data
function encryptData(data, secretKey) {
  const cipher = crypto.createCipher("aes-256-cbc", secretKey);
  let encrypted = cipher.update(JSON.stringify(data), "utf8", "hex");
  encrypted += cipher.final("hex");
  return encrypted;
}

// API to receive encrypted coin and change ownership
app.post("/transfer", (req, res) => {
  try {
    const { encryptedCoin, secretKey } = req.body;

    // Decrypt incoming coin data
    const coin = decryptData(encryptedCoin, secretKey);

    console.log("🔹 Received Coin:", coin);

    // Check if the coin was already spent
    if (spentCoins.has(coin.coinId)) {
      return res.status(400).json({ message: "❌ Double Spending Detected!" });
    }

    // Verify client's signature
    const clientKey = EC.keyFromPublic(coin.owner, "hex");
    const isValid = clientKey.verify(coin.coinId, coin.signature);

    if (!isValid) {
      return res
        .status(400)
        .json({ message: "❌ Invalid Signature! Tampering detected." });
    }

    console.log("✅ Signature Verified!");

    // Mark coin as spent
    spentCoins.add(coin.coinId);

    // Remove client signature & re-sign with server
    delete coin.signature;
    coin.owner = serverPublicKey;

    const serverSignature = serverKeyPair.sign(coin.coinId).toDER("hex");
    coin.signature = serverSignature;

    console.log("🔹 New Ownership Applied:", coin);

    // Encrypt the updated coin
    const encryptedResponse = encryptData(coin, secretKey);
    res.json({ encryptedCoin: encryptedResponse });
  } catch (error) {
    console.error("❌ Error processing transaction:", error.message);
    res.status(500).json({ message: "Server error" });
  }
});

// Start server
app.listen(3000, () => {
  console.log("🚀 Server running on port 3000");
});

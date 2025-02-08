const express = require("express");
const fs = require("fs");
const crypto = require("crypto");

const app = express();
const PORT = 3000;
const LEDGER_FILE = "ledger.json";

app.use(express.json());

// Read ledger file or initialize it
let ledger = [];
if (fs.existsSync(LEDGER_FILE)) {
  try {
    const data = fs.readFileSync(LEDGER_FILE, "utf8").trim();
    ledger = data ? JSON.parse(data) : [];
  } catch (error) {
    console.error("Error reading ledger.json. Resetting ledger.");
    ledger = [];
  }
}

// Function to compute SHA-256 hash
function hashData(data) {
  return crypto.createHash("sha256").update(data).digest("hex");
}

// Function to validate ledger integrity
function isLedgerValid() {
  for (let i = 1; i < ledger.length; i++) {
    const computedHash = hashData(
      ledger[i - 1].hash + `${ledger[i].key}:${ledger[i].value}`
    );
    if (computedHash !== ledger[i].hash) {
      return false;
    }
  }
  return true;
}

// Add new message to ledger (Only if the ledger is valid)
app.post("/store", (req, res) => {
  if (!isLedgerValid()) {
    return res
      .status(400)
      .json({ error: "⚠️ Tampering detected! Cannot add new data." });
  }

  const { key, value } = req.body;
  if (!key || !value) {
    return res.status(400).json({ error: "Key and value are required" });
  }

  const message = `${key}:${value}`;
  const prevHash =
    ledger.length > 0 ? ledger[ledger.length - 1].hash : "GENESIS";
  const newHash = hashData(prevHash + message);

  const entry = { prevHash, hash: newHash, key, value };
  ledger.push(entry);

  fs.writeFileSync(LEDGER_FILE, JSON.stringify(ledger, null, 2));

  res.json({ success: true, entry });
});

// Verify Ledger Integrity
app.get("/verify", (req, res) => {
  if (isLedgerValid()) {
    return res.json({ message: "✅ Ledger is valid!" });
  }
  return res
    .status(400)
    .json({ error: "⚠️ Tampering detected! Ledger integrity compromised." });
});

// Attempted tampering without modifying ledger
app.post("/tamper", (req, res) => {
  if (ledger.length < 2) {
    return res.status(400).json({ error: "Not enough data to tamper" });
  }

  // Simulate an unauthorized modification (without saving)
  const tempLedger = JSON.parse(JSON.stringify(ledger)); // Deep copy
  tempLedger[1].value = "TamperedData"; // Modify second entry

  // Check if tampering is detected
  if (!isLedgerValid(tempLedger)) {
    return res
      .status(400)
      .json({ error: "⚠️ Tampering detected! Ledger remains unchanged." });
  }

  res.json({ message: "Tampering went undetected (should not happen)!" });
});

app.get("/msg", (req, res) => {
  res.send("Hello World!");
});

// Start Server
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

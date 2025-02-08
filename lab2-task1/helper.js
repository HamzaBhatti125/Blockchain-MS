const fs = require("fs");

// Shared ledger file
const ledgerFile = "ledger.json";

// Initialize ledger if not exists
if (!fs.existsSync(ledgerFile)) {
  fs.writeFileSync(
    ledgerFile,
    JSON.stringify({ clients: {}, messages: [] }, null, 2)
  );
}

// Load ledger
function loadLedger() {
  return JSON.parse(fs.readFileSync(ledgerFile, "utf8"));
}

// Save ledger
function saveLedger(ledger) {
  fs.writeFileSync(ledgerFile, JSON.stringify(ledger, null, 2));
}

// Verify client
function verifyClient(clientHash) {
  const ledger = loadLedger();
  return ledger.clients[clientHash] !== undefined;
}

// Add message to ledger
function addMessageToLedger(clientHash, message) {
  const ledger = loadLedger();
  ledger.messages.push({
    clientHash,
    message,
    timestamp: new Date().toISOString(),
  });
  saveLedger(ledger);
}

module.exports = { loadLedger, saveLedger, verifyClient, addMessageToLedger };

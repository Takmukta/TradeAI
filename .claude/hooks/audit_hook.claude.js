// Audit Hook — logs all agent events to the audit trail
// Invoked at the start/end of each agent step

const fs = require("fs");
const path = require("path");

const AUDIT_LOG = path.join(__dirname, "../../../logs/audit.jsonl");

function auditLog(event, data = {}) {
  const entry = JSON.stringify({ timestamp: new Date().toISOString(), event, ...data });
  fs.appendFileSync(AUDIT_LOG, entry + "\n");
}

module.exports = { auditLog };

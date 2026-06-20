// Security Hook — sanitizes inputs to prevent injection attacks

const DANGEROUS_CHARS = /[<>\"';&|`$\\{}]/g;

function sanitize(value, maxLen = 500) {
  if (typeof value !== "string") return value;
  return value.replace(DANGEROUS_CHARS, "").slice(0, maxLen).trim();
}

function sanitizeObject(obj) {
  if (typeof obj !== "object" || obj === null) return sanitize(String(obj));
  return Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [sanitize(k), sanitize(String(v))])
  );
}

module.exports = { sanitize, sanitizeObject };

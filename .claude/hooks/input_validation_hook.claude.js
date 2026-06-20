// Input Validation Hook — validates and sanitizes ticker inputs before processing

const VALID_TICKER = /^[A-Z]{1,5}$/;

function validateTickers(tickers) {
  if (!Array.isArray(tickers) || tickers.length === 0) {
    throw new Error("At least one ticker is required");
  }
  if (tickers.length > 2) {
    throw new Error("Maximum 2 tickers allowed");
  }
  return tickers.map((t) => {
    const clean = String(t).trim().toUpperCase();
    if (!VALID_TICKER.test(clean)) {
      throw new Error(`Invalid ticker symbol: ${t}`);
    }
    return clean;
  });
}

module.exports = { validateTickers };

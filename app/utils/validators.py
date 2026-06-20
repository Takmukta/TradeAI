import re
from typing import List
from app.utils.ticker_normalizer import get_valid_ticker

# After normalization a ticker must be 1-10 uppercase letters (hyphen allowed for e.g. BRK-B)
VALID_TICKER_RE = re.compile(r"^[A-Z]{1,10}(-[A-Z]{1})?$")


def validate_tickers(raw: List[str]) -> List[str]:
    if not raw:
        raise ValueError("At least one ticker is required")
    if len(raw) > 2:
        raise ValueError("Maximum 2 tickers allowed")
    normalized = []
    for t in raw:
        resolved = get_valid_ticker(t)
        if not VALID_TICKER_RE.match(resolved):
            raise ValueError(f"'{t}' could not be resolved to a valid ticker symbol")
        normalized.append(resolved)
    return normalized


def sanitize_string(value: str, max_length: int = 500) -> str:
    value = value.strip()
    value = re.sub(r"[<>\"';&|`$\\]", "", value)
    return value[:max_length]

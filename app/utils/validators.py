import re
from typing import List


VALID_TICKER_RE = re.compile(r"^[A-Z]{1,10}$")


def validate_tickers(raw: List[str]) -> List[str]:
    if not raw:
        raise ValueError("At least one ticker is required")
    if len(raw) > 2:
        raise ValueError("Maximum 2 tickers allowed")
    cleaned = []
    for t in raw:
        t = t.strip().upper()
        if not VALID_TICKER_RE.match(t):
            raise ValueError(f"'{t}' is not a valid ticker symbol")
        cleaned.append(t)
    return cleaned


def sanitize_string(value: str, max_length: int = 500) -> str:
    value = value.strip()
    value = re.sub(r"[<>\"';&|`$\\]", "", value)
    return value[:max_length]

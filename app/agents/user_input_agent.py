from typing import List
from app.utils.validators import validate_tickers
from app.utils.logger import get_logger, audit_log

logger = get_logger(__name__)


class UserInputAgent:
    """Validates and sanitizes user-provided stock tickers."""

    def run(self, raw_tickers: List[str]) -> List[str]:
        logger.info(f"UserInputAgent received: {raw_tickers}")
        tickers = validate_tickers(raw_tickers)
        audit_log("user_input_validated", {"tickers": tickers})
        logger.info(f"Validated tickers: {tickers}")
        return tickers

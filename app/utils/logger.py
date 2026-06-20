import logging
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)
        fh = logging.FileHandler(LOG_DIR / "tradeai.log")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


def audit_log(event: str, data: dict) -> None:
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": event, **data}
    audit_path = LOG_DIR / "audit.jsonl"
    with open(audit_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

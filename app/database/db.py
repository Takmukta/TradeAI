import json
from pathlib import Path
from datetime import datetime
from typing import Any

DB_PATH = Path(__file__).parent.parent.parent / "data"
DB_PATH.mkdir(exist_ok=True)
STORE_FILE = DB_PATH / "kv_store.json"


def _load() -> dict:
    if STORE_FILE.exists():
        with open(STORE_FILE) as f:
            return json.load(f)
    return {}


def _save(store: dict) -> None:
    with open(STORE_FILE, "w") as f:
        json.dump(store, f, indent=2, default=str)


def kv_set(key: str, value: Any) -> None:
    store = _load()
    store[key] = {"value": value, "updated_at": datetime.utcnow().isoformat()}
    _save(store)


def kv_get(key: str) -> Any:
    store = _load()
    entry = store.get(key)
    return entry["value"] if entry else None


def kv_delete(key: str) -> None:
    store = _load()
    store.pop(key, None)
    _save(store)

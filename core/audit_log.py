import json
import os
import time
from typing import Any, Dict


class AuditLogger:
    def __init__(self, path: str = "mission_logs/audit.jsonl"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path

    def write(self, event_type: str, payload: Dict[str, Any]) -> None:
        record = {
            "ts": time.time(),
            "event": event_type,
            "payload": payload,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

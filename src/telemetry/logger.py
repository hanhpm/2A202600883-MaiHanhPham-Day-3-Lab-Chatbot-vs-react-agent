import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class JSONLLogger:
    """Logger that writes events to JSONL (JSON Lines) format."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"agent_telemetry_{timestamp}.jsonl"

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event as a JSON line.
        Format: {"timestamp": "...", "event_type": "...", "data": {...}}
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
        }

        try:
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error writing to log: {e}")

    def read_logs(self) -> list[Dict[str, Any]]:
        """Read all logged events from the JSONL file."""
        logs = []
        if not self.log_file.exists():
            return logs

        try:
            with self.log_file.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception as e:
            print(f"Error reading logs: {e}")

        return logs

    def get_log_file_path(self) -> str:
        """Get the path to the current log file."""
        return str(self.log_file)


# Global logger instance
logger = JSONLLogger()

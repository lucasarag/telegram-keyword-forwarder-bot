from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
import pathlib
import asyncio

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = DATA_DIR / "config.json"
LOGS_PATH = DATA_DIR / "logs.jsonl"

@dataclass
class AppConfig:
    keywords: List[str] = field(default_factory=list)
    chat_id: Optional[int | str] = None

    @classmethod
    def load(cls) -> "AppConfig":
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return cls(**data)
        cfg = cls()
        cfg.save()
        return cfg

    def save(self) -> None:
        CONFIG_PATH.write_text(json.dumps({
            "keywords": self.keywords,
            "chat_id": self.chat_id,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

class LogBus:
    """Simple async pub/sub for log lines."""
    def __init__(self) -> None:
        self._subs: List[asyncio.Queue[str]] = []

    def subscribe(self) -> asyncio.Queue[str]:
        q: asyncio.Queue[str] = asyncio.Queue()
        self._subs.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[str]) -> None:
        if q in self._subs:
            self._subs.remove(q)

    async def publish(self, line: str) -> None:
        LOGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOGS_PATH.open("a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")
        for q in list(self._subs):
            await q.put(line)

CONFIG = AppConfig.load()
LOGS = LogBus()

# runtime, preenchido pelo telegram_service
RUNTIME: Dict[str, Any] = {
    "session_id": None,
    "is_logged": False,
}

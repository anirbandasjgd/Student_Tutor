"""Persist chat sessions to disk as JSON."""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from config import CHATS_DIR


def _ensure_dir() -> None:
    os.makedirs(CHATS_DIR, exist_ok=True)


def _path(session_id: str) -> str:
    return os.path.join(CHATS_DIR, f"{session_id}.json")


def new_session_id() -> str:
    return str(uuid.uuid4())


def save_session(
    session_id: str,
    subject: str,
    messages: list[dict[str, str]],
    essay_grade: Optional[int] = None,
) -> None:
    _ensure_dir()
    title = _derive_title(messages)
    payload = {
        "session_id": session_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "subject": subject,
        "essay_grade": essay_grade,
        "messages": messages,
        "title": title,
    }
    with open(_path(session_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_session(session_id: str) -> Optional[dict[str, Any]]:
    p = _path(session_id)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def list_sessions() -> list[dict[str, Any]]:
    _ensure_dir()
    out: list[dict[str, Any]] = []
    for name in os.listdir(CHATS_DIR):
        if not name.endswith(".json"):
            continue
        session_id = name[:-5]
        data = load_session(session_id)
        if data:
            out.append(
                {
                    "session_id": session_id,
                    "title": data.get("title", "Chat"),
                    "updated_at": data.get("updated_at", ""),
                    "subject": data.get("subject", ""),
                }
            )
    out.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    return out


def _derive_title(messages: list[dict[str, str]], max_len: int = 48) -> str:
    for m in messages:
        if m.get("role") == "user":
            text = (m.get("content") or "").strip().replace("\n", " ")
            if text:
                return text[:max_len] + ("…" if len(text) > max_len else "")
    return "New chat"

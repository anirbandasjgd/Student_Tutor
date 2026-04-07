"""Persist chat sessions to disk as JSON, scoped per student."""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from config import CHATS_DIR

STUDENTS_SUBDIR = "students"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _student_chats_dir(student_storage_key: str) -> str:
    return os.path.join(CHATS_DIR, STUDENTS_SUBDIR, student_storage_key)


def _path(session_id: str, student_storage_key: str) -> str:
    return os.path.join(_student_chats_dir(student_storage_key), f"{session_id}.json")


def new_session_id() -> str:
    return str(uuid.uuid4())


def save_session(
    session_id: str,
    student_storage_key: str,
    student_name: str,
    subject: str,
    messages: list[dict[str, str]],
    essay_grade: Optional[int] = None,
) -> None:
    d = _student_chats_dir(student_storage_key)
    _ensure_dir(d)
    title = _derive_title(messages)
    payload = {
        "session_id": session_id,
        "student_name": student_name.strip(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "subject": subject,
        "essay_grade": essay_grade,
        "messages": messages,
        "title": title,
    }
    with open(_path(session_id, student_storage_key), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_session(
    session_id: str, student_storage_key: str
) -> Optional[dict[str, Any]]:
    p = _path(session_id, student_storage_key)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def list_student_sessions(student_storage_key: str) -> list[dict[str, Any]]:
    d = _student_chats_dir(student_storage_key)
    if not os.path.isdir(d):
        return []
    out: list[dict[str, Any]] = []
    for name in os.listdir(d):
        if not name.endswith(".json"):
            continue
        sid = name[:-5]
        data = load_session(sid, student_storage_key)
        if data:
            out.append(
                {
                    "session_id": sid,
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

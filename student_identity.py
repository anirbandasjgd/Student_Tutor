"""Map student display name to a private storage key (per-student chat isolation)."""

from __future__ import annotations

import hashlib
from typing import Optional


def student_storage_key(name: str) -> Optional[str]:
    """
    Return a stable, filesystem-safe key for this exact name string.
    Two different students with the same spelling share a key—use a unique
    name or add an ID in the name if that matters for your deployment.
    """
    n = (name or "").strip()
    if not n:
        return None
    return hashlib.sha256(n.encode("utf-8")).hexdigest()

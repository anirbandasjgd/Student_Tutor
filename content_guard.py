"""Content checks for user and assistant messages (OpenAI Moderation API)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from openai import OpenAI

# Moderation input length limit (characters); trim very long pastes.
MAX_MODERATION_INPUT_CHARS = 32000

# OpenAI Python SDK uses snake_case for category fields (see ModerationCategories).
_CATEGORY_LABELS = (
    ("sexual", "sexual content"),
    ("sexual_minors", "content involving minors"),
    ("hate", "hateful content"),
    ("hate_threatening", "threatening language"),
    ("harassment", "harassment or abuse"),
    ("harassment_threatening", "threatening harassment"),
    ("violence", "violence"),
    ("violence_graphic", "graphic violence"),
    ("self_harm", "self-harm"),
    ("self_harm_intent", "self-harm"),
    ("self_harm_instructions", "self-harm instructions"),
    ("illicit", "disallowed content"),
    ("illicit_violent", "violent illicit content"),
)


def _labels_for_categories(categories) -> list[str]:
    labels: list[str] = []
    for attr, label in _CATEGORY_LABELS:
        if hasattr(categories, attr) and bool(getattr(categories, attr)):
            labels.append(label)
    return labels


def moderation_block_reason(client: OpenAI, text: str) -> Optional[str]:
    """
    Run OpenAI moderation on `text`.

    Returns None if the content is allowed, or a short user-facing message if it
    should be blocked (vulgarity, sexual content, harassment, violence, etc.).
    On API failure, returns None (fail-open) so outages do not lock users out.
    """
    if not text or not text.strip():
        return None
    chunk = text[:MAX_MODERATION_INPUT_CHARS]
    try:
        resp = client.moderations.create(
            model="omni-moderation-latest",
            input=chunk,
        )
    except Exception:
        try:
            resp = client.moderations.create(input=chunk)
        except Exception:
            return None
    if not resp.results:
        return None
    result = resp.results[0]
    if not result.flagged:
        return None

    labels = _labels_for_categories(result.categories)
    if labels:
        kinds = ", ".join(labels)
        return (
            f"This cannot be shown because it may involve: {kinds}. "
            "This tutor is for school-appropriate questions only—please rephrase respectfully."
        )
    return (
        "This cannot be shown because it may violate content guidelines. "
        "Please keep language and topics appropriate for a school setting."
    )


def safe_assistant_reply(client: OpenAI, reply: str) -> str:
    """
    If the model reply fails moderation, return a safe replacement string.
    Otherwise return `reply` unchanged.
    """
    reason = moderation_block_reason(client, reply)
    if reason is None:
        return reply
    return (
        "_The assistant’s reply was withheld because it did not pass safety checks. "
        "Try rephrasing your question or ask your teacher for help._"
    )

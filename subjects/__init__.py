"""Subject modules: Science, Math, English, General knowledge, Essay."""

from typing import Any, Optional

from . import english, essay, general_knowledge, math, science

SUBJECT_KEYS = ("Science", "Math", "English", "General knowledge", "Essay")

_MODULE_MAP: dict[str, Any] = {
    "Science": science,
    "Math": math,
    "English": english,
    "General knowledge": general_knowledge,
    "Essay": essay,
}


def get_module(subject: str):
    if subject not in _MODULE_MAP:
        raise ValueError(f"Unknown subject: {subject}")
    return _MODULE_MAP[subject]


def get_system_message(subject: str, essay_grade: Optional[int] = None) -> str:
    mod = get_module(subject)
    base = mod.SYSTEM_MESSAGE
    if subject == "Essay" and essay_grade is not None:
        return (
            base
            + f"\n\nThe student has indicated they are in grade {essay_grade}. "
            "Use this grade for complexity of feedback."
        )
    return base


def get_max_tokens(subject: str) -> int:
    return get_module(subject).MAX_TOKENS

"""
Student Tutor — Streamlit chatbot for Science, Math, English, General knowledge, and Essay.
Run from this directory: streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from typing import Any

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from openai import OpenAI

import chat_storage
from config import DEFAULT_MODEL
from subjects import SUBJECT_KEYS, get_max_tokens, get_system_message
from subjects import essay as essay_subject


def _effective_api_key() -> str:
    """Sidebar key (if non-empty) takes precedence over OPENAI_API_KEY in the environment."""
    from_ui = (st.session_state.get("user_openai_key") or "").strip()
    if from_ui:
        return from_ui
    return (os.getenv("OPENAI_API_KEY") or "").strip()


def _openai_client():
    key = _effective_api_key()
    return OpenAI(api_key=key) if key else None

CHAT_INPUT_PLACEHOLDERS = {
    "Science": "Ask me any Science related questions",
    "Math": "Ask me any Math related questions",
    "English": "Ask me any English Grammer related questions",
    "General knowledge": "Ask about any topic outside Science, Math, or English",
    "Essay": "Paste your essay for evaluation",
}


def _extract_assistant_text(message) -> str:
    """Normalize message.content (str, None, or list of content parts) to plain text."""
    raw = getattr(message, "content", None)
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts: list[str] = []
        for block in raw:
            if isinstance(block, dict):
                if block.get("type") == "text" and "text" in block:
                    parts.append(str(block["text"]))
                elif "text" in block:
                    parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts).strip()
    return str(raw).strip()


_SUBJECT_FILE_FOR_HINT = {
    "Science": "science",
    "Math": "math",
    "English": "english",
    "General knowledge": "general_knowledge",
    "Essay": "essay",
}


def _call_model(
    client: OpenAI,
    messages: list[dict[str, str]],
    model: str,
    max_tokens: int,
    *,
    subject_key: str = "Math",
) -> str:
    if not client:
        raise RuntimeError("OpenAI client is not configured.")
    kwargs: dict[str, Any] = {"model": model, "messages": messages}
    effort = os.getenv("OPENAI_REASONING_EFFORT", "").strip()
    if effort:
        kwargs["reasoning_effort"] = effort

    try:
        resp = client.chat.completions.create(**kwargs, max_tokens=max_tokens)
    except Exception as e:
        err = str(e).lower()
        if any(
            s in err
            for s in ("max_tokens", "max_completion_tokens", "unsupported_parameter")
        ):
            resp = client.chat.completions.create(
                **kwargs, max_completion_tokens=max_tokens
            )
        elif "reasoning_effort" in err and "reasoning_effort" in kwargs:
            kwargs.pop("reasoning_effort", None)
            resp = client.chat.completions.create(**kwargs, max_tokens=max_tokens)
        else:
            raise

    choice = resp.choices[0]
    msg = choice.message
    text = _extract_assistant_text(msg)

    refusal = getattr(msg, "refusal", None)
    if refusal:
        return f"The model declined to answer: {refusal}"

    if text:
        return text

    finish = getattr(choice, "finish_reason", None) or ""
    usage = getattr(resp, "usage", None)
    detail = ""
    if usage is not None:
        ctd = getattr(usage, "completion_tokens_details", None)
        if ctd is not None:
            rt = getattr(ctd, "reasoning_tokens", None)
            if rt is not None:
                detail = f" (reasoning_tokens≈{rt})"

    sub_file = _SUBJECT_FILE_FOR_HINT.get(subject_key, "math")

    if finish == "length":
        return (
            "**No visible reply:** the output budget ran out before the model wrote an answer. "
            "This often happens with **reasoning models** (reasoning uses the same token limit). "
            f"Try raising `MAX_TOKENS` in `subjects/{sub_file}.py`, "
            "or set `OPENAI_REASONING_EFFORT=low` in `.env` if your model supports it, then reload."
        )

    return (
        "**No visible reply** from the model "
        f"(finish_reason={finish!r}{detail}). "
        "Try a higher `MAX_TOKENS` for this subject, set `OPENAI_REASONING_EFFORT=low` in `.env`, "
        "or switch `OPENAI_MODEL` to a non-reasoning chat model."
    )


def _init_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = chat_storage.new_session_id()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "subject" not in st.session_state:
        st.session_state.subject = "Science"
    if "essay_grade" not in st.session_state:
        st.session_state.essay_grade = None
    if "user_openai_key" not in st.session_state:
        st.session_state.user_openai_key = ""


def _persist() -> None:
    chat_storage.save_session(
        st.session_state.session_id,
        st.session_state.subject,
        st.session_state.messages,
        essay_grade=st.session_state.essay_grade
        if st.session_state.subject == "Essay"
        else None,
    )


def _start_new_chat() -> None:
    st.session_state.session_id = chat_storage.new_session_id()
    st.session_state.messages = []
    st.session_state.essay_grade = None


def main() -> None:
    st.set_page_config(page_title="Student Tutor", page_icon="📚", layout="wide")
    _init_state()

    st.title("Student Tutor")
    st.caption(
        "Ask questions in Science, Math, English, General knowledge, or get essay feedback."
    )

    with st.sidebar:
        st.subheader("OpenAI API key")
        st.text_input(
            "Paste your API key",
            type="password",
            placeholder="sk-…",
            help="Stored only in this browser session. Leave empty to use OPENAI_API_KEY from your .env file.",
            key="user_openai_key",
        )
        st.caption(
            "Get a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)."
        )

        st.divider()

        st.subheader("Subject")
        subject = st.radio(
            "Choose topic",
            SUBJECT_KEYS,
            index=SUBJECT_KEYS.index(st.session_state.subject)
            if st.session_state.subject in SUBJECT_KEYS
            else 0,
            key="subject_radio",
        )
        if subject != st.session_state.subject:
            st.session_state.subject = subject
            st.session_state.messages = []
            st.session_state.session_id = chat_storage.new_session_id()
            st.session_state.essay_grade = None
            st.rerun()

        if st.session_state.subject == "Essay":
            st.subheader("Essay options")
            grade_options = ["Not set (assistant will ask)"] + [
                f"Grade {g}" for g in range(1, 13)
            ]
            current = st.session_state.essay_grade
            default_idx = 0
            if current is not None and 1 <= current <= 12:
                default_idx = current
            idx = st.selectbox(
                "Your grade (optional)",
                range(len(grade_options)),
                format_func=lambda i: grade_options[i],
                index=default_idx,
                key="essay_grade_select",
            )
            st.session_state.essay_grade = None if idx == 0 else idx

        st.divider()
        if st.button("New chat", use_container_width=True):
            _start_new_chat()
            st.rerun()

        st.subheader("Saved chats")
        sessions = chat_storage.list_sessions()
        grouped: defaultdict[str, list] = defaultdict(list)
        for s in sessions:
            subj = (s.get("subject") or "Science").strip()
            if subj not in SUBJECT_KEYS:
                subj = "Other"
            grouped[subj].append(s)

        group_order = list(SUBJECT_KEYS)
        if grouped.get("Other"):
            group_order.append("Other")

        for subj in group_order:
            subs = grouped.get(subj, [])
            if not subs:
                continue
            with st.expander(
                f"{subj} ({len(subs)})",
                expanded=(subj == st.session_state.subject),
            ):
                for s in subs:
                    label = (s.get("title") or "Chat")[:40]
                    if st.button(
                        label,
                        key=f"load_{s['session_id']}",
                        use_container_width=True,
                    ):
                        data = chat_storage.load_session(s["session_id"])
                        if data:
                            st.session_state.session_id = data["session_id"]
                            st.session_state.messages = data.get("messages", [])
                            st.session_state.subject = data.get("subject", "Science")
                            st.session_state.essay_grade = data.get("essay_grade")
                            st.rerun()

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    client = _openai_client()

    if not _effective_api_key():
        st.error(
            "Add your OpenAI API key in the sidebar, or set `OPENAI_API_KEY` in a `.env` file (see `.env.example`)."
        )

    system_msg = get_system_message(
        st.session_state.subject,
        essay_grade=st.session_state.essay_grade
        if st.session_state.subject == "Essay"
        else None,
    )
    max_tokens = get_max_tokens(st.session_state.subject)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    _ph = CHAT_INPUT_PLACEHOLDERS.get(
        st.session_state.subject, CHAT_INPUT_PLACEHOLDERS["Science"]
    )
    if prompt := st.chat_input(placeholder=_ph):
        if st.session_state.subject == "Essay":
            wc = essay_subject.count_words(prompt)
            if not essay_subject.essay_within_limit(prompt):
                st.warning(
                    f"This message is {wc} words. Essays must be **{essay_subject.MAX_ESSAY_WORDS} words or fewer**. "
                    "Shorten your text and send again."
                )
                st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})

        if not client:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "_Cannot reply: add your API key in the sidebar or set `OPENAI_API_KEY` in `.env`._",
                }
            )
            _persist()
            st.rerun()

        api_messages = (
            [{"role": "system", "content": system_msg}]
            + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        )
        try:
            reply = _call_model(
                client,
                api_messages,
                model,
                max_tokens,
                subject_key=st.session_state.subject,
            )
        except Exception as e:
            reply = f"Error calling the model: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        _persist()
        st.rerun()


if __name__ == "__main__":
    main()

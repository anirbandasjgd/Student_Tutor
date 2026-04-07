"""App configuration loaded from environment."""

import os

from dotenv import load_dotenv

load_dotenv()

# Specified model for all OpenAI interactions; override via OPENAI_MODEL if needed.
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHATS_DIR = os.path.join(DATA_DIR, "chats")

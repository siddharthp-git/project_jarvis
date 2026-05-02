"""
Global configuration for Project Jarvis.
Loads environment variables from .env (and .env.local / keys.env overrides).
"""
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
    for candidate in (Path(".env.local"), Path("keys.env")):
        if candidate.exists():
            load_dotenv(dotenv_path=candidate, override=True)
except Exception:
    pass


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@dataclass(frozen=True)
class Settings:
    # ─── Ollama / LLM ──────────────────────────────────────────────
    ollama_url: str
    model: str
    max_tool_rounds: int
    conversation_history_limit: int
    timeout: int
    wake_word: str

    # ─── Web Search ────────────────────────────────────────────────
    tavily_api_key: str

    # ─── News ──────────────────────────────────────────────────────
    news_api_key: str

    # ─── Gmail SMTP ────────────────────────────────────────────────
    gmail_address: str
    gmail_app_pass: str

    # ─── Amadeus Flights ───────────────────────────────────────────
    amadeus_api_key: str
    amadeus_api_secret: str
    amadeus_env: str

    # ─── AviationStack Flights ─────────────────────────────────────
    aviationstack_api_key: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        ollama_url=_get("OLLAMA_URL", "http://localhost:11434/api/chat"),
        model=_get("MODEL", "gemma4:e2b"),
        max_tool_rounds=int(_get("MAX_TOOL_ROUNDS", "5")),
        conversation_history_limit=int(_get("CONVERSATION_HISTORY_LIMIT", "30")),
        timeout=int(_get("TIMEOUT", "180")),
        wake_word=_get("WAKE_WORD", "hello"),

        tavily_api_key=_get("TAVILY_API_KEY", ""),
        news_api_key=_get("NEWS_API_KEY", ""),

        gmail_address=_get("GMAIL_ADDRESS", ""),
        gmail_app_pass=_get("GMAIL_APP_PASS", ""),

        amadeus_api_key=_get("AMADEUS_API_KEY", ""),
        amadeus_api_secret=_get("AMADEUS_API_SECRET", ""),
        amadeus_env=_get("AMADEUS_ENV", "test"),

        aviationstack_api_key=_get("AVIATIONSTACK_API_KEY", ""),
    )


# ─── Backwards-compatible module-level constants ────────────────────
# Other tools (weather, news, etc.) still do `import config; config.TAVILY_API_KEY`
# so we expose the same names they already use.
_s = get_settings()
OLLAMA_URL               = _s.ollama_url
MODEL                    = _s.model
MAX_TOOL_ROUNDS          = _s.max_tool_rounds
CONVERSATION_HISTORY_LIMIT = _s.conversation_history_limit
TIMEOUT                  = _s.timeout
WAKE_WORD                = _s.wake_word
TAVILY_API_KEY           = _s.tavily_api_key
NEWS_API_KEY             = _s.news_api_key
GMAIL_ADDRESS            = _s.gmail_address
GMAIL_APP_PASS           = _s.gmail_app_pass
AMADEUS_API_KEY          = _s.amadeus_api_key
AMADEUS_API_SECRET       = _s.amadeus_api_secret
AMADEUS_ENV              = _s.amadeus_env
AVIATIONSTACK_API_KEY   = _s.aviationstack_api_key

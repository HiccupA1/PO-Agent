import os
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


def _backend_env_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".env"


def _read_backend_env() -> tuple[bool, dict[str, str]]:
    env_path = _backend_env_path()
    if not env_path.exists():
        return False, {}
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return True, values


def _env_value(env_values: dict[str, str], key: str, default: str = "") -> str:
    if key in env_values:
        return env_values[key]
    return os.getenv(key, default)


def _env_int(env_values: dict[str, str], key: str, default: int) -> int:
    raw_value = _env_value(env_values, key, str(default))
    try:
        return int(raw_value)
    except ValueError:
        return default


ENV_FILE_DETECTED, ENV_FILE_VALUES = _read_backend_env()


@dataclass(frozen=True)
class Settings:
    app_name: str = "PO Agent API"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    llm_mode: str = field(default_factory=lambda: _env_value(ENV_FILE_VALUES, "LLM_MODE", "mock"))
    llm_provider: str = field(default_factory=lambda: _env_value(ENV_FILE_VALUES, "LLM_PROVIDER", "mock"))
    llm_api_key: str = field(default_factory=lambda: _env_value(ENV_FILE_VALUES, "LLM_API_KEY", ""))
    llm_base_url: str = field(default_factory=lambda: _env_value(ENV_FILE_VALUES, "LLM_BASE_URL", ""))
    llm_model: str = field(default_factory=lambda: _env_value(ENV_FILE_VALUES, "LLM_MODEL", ""))
    llm_timeout_seconds: int = field(default_factory=lambda: _env_int(ENV_FILE_VALUES, "LLM_TIMEOUT_SECONDS", 30))
    gemini_api_key: str = field(default_factory=lambda: _env_value(ENV_FILE_VALUES, "GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: _env_value(ENV_FILE_VALUES, "GEMINI_MODEL", "gemini-3.5-flash"))
    gemini_timeout_seconds: int = field(default_factory=lambda: _env_int(ENV_FILE_VALUES, "GEMINI_TIMEOUT_SECONDS", 120))
    env_file_detected: bool = field(default_factory=lambda: ENV_FILE_DETECTED)


def get_settings() -> Settings:
    env_file_detected, env_values = _read_backend_env()
    settings = Settings(
        llm_mode=_env_value(env_values, "LLM_MODE", "mock"),
        llm_provider=_env_value(env_values, "LLM_PROVIDER", "mock"),
        llm_api_key=_env_value(env_values, "LLM_API_KEY", ""),
        llm_base_url=_env_value(env_values, "LLM_BASE_URL", ""),
        llm_model=_env_value(env_values, "LLM_MODEL", ""),
        llm_timeout_seconds=_env_int(env_values, "LLM_TIMEOUT_SECONDS", 30),
        gemini_api_key=_env_value(env_values, "GEMINI_API_KEY", ""),
        gemini_model=_env_value(env_values, "GEMINI_MODEL", "gemini-3.5-flash"),
        gemini_timeout_seconds=_env_int(env_values, "GEMINI_TIMEOUT_SECONDS", 120),
        env_file_detected=env_file_detected,
    )
    logger.info(
        "Loaded PO Agent config: env_file_detected=%s provider=%s model=%s timeout=%s api_key_present=%s",
        settings.env_file_detected,
        settings.llm_provider,
        settings.gemini_model if settings.llm_provider == "gemini" else settings.llm_model,
        settings.gemini_timeout_seconds if settings.llm_provider == "gemini" else settings.llm_timeout_seconds,
        bool(settings.gemini_api_key if settings.llm_provider == "gemini" else settings.llm_api_key),
    )
    return settings


settings = get_settings()

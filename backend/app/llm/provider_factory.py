from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.llm.base import LLMConfigurationError, LLMProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider


@dataclass(frozen=True)
class ProviderSelection:
    provider: LLMProvider
    mode_requested: str
    mode_used: str
    provider_name: str
    model: str | None
    timeout_seconds: int | None
    provider_configured: bool
    fallback_used: bool
    fallback_reason: str | None = None


def select_provider(runtime_mode: str | None = None) -> ProviderSelection:
    settings = get_settings()
    mode_requested = (runtime_mode or settings.llm_mode or "mock").lower()
    if mode_requested not in {"mock", "llm"}:
        mode_requested = "mock"

    if mode_requested == "mock":
        return ProviderSelection(
            provider=MockLLMProvider(),
            mode_requested="mock",
            mode_used="mock",
            provider_name="mock",
            model=None,
            timeout_seconds=None,
            provider_configured=True,
            fallback_used=False,
        )

    provider_name = (settings.llm_provider or "openai_compatible").lower()
    try:
        if provider_name == "mock":
            return ProviderSelection(
                provider=MockLLMProvider(),
                mode_requested="llm",
                mode_used="mock",
                provider_name="mock",
                model=None,
                timeout_seconds=None,
                provider_configured=True,
                fallback_used=True,
                fallback_reason="LLM_PROVIDER=mock",
            )
        if provider_name == "openai_compatible":
            provider = OpenAICompatibleProvider(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
                model=settings.llm_model,
                timeout_seconds=settings.llm_timeout_seconds,
            )
            return ProviderSelection(
                provider=provider,
                mode_requested="llm",
                mode_used="llm",
                provider_name=provider.provider_name,
                model=settings.llm_model,
                timeout_seconds=settings.llm_timeout_seconds,
                provider_configured=True,
                fallback_used=False,
            )
        if provider_name == "gemini":
            provider = GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
                timeout_seconds=settings.gemini_timeout_seconds,
            )
            return ProviderSelection(
                provider=provider,
                mode_requested="llm",
                mode_used="llm",
                provider_name=provider.provider_name,
                model=provider.model,
                timeout_seconds=provider.timeout_seconds,
                provider_configured=True,
                fallback_used=False,
            )
        raise LLMConfigurationError(f"Unsupported LLM_PROVIDER: {provider_name}")
    except LLMConfigurationError as exc:
        return ProviderSelection(
            provider=MockLLMProvider(),
            mode_requested="llm",
            mode_used="mock",
            provider_name=provider_name,
            model=_model_for_provider(provider_name, settings),
            timeout_seconds=_timeout_for_provider(provider_name, settings),
            provider_configured=False,
            fallback_used=True,
            fallback_reason=str(exc),
        )


def get_llm_status() -> dict[str, object]:
    settings = get_settings()
    selection = select_provider()
    provider_name = (settings.llm_provider or "mock").lower()
    configured = _is_provider_configured(provider_name, settings)
    message = "Mock mode is active. No API key is required."
    if settings.llm_mode == "llm" and provider_name == "gemini" and configured:
        message = "Gemini provider configured."
    elif settings.llm_mode == "llm" and provider_name == "gemini":
        message = "GEMINI_API_KEY missing. Agent will fallback to mock mode."
    elif settings.llm_mode == "llm" and not configured:
        message = "LLM_API_KEY or LLM_BASE_URL missing. Agent will fallback to mock mode."
    elif settings.llm_mode == "llm":
        message = "LLM-assisted mode is configured."
    return {
        "mode": settings.llm_mode or "mock",
        "provider": provider_name,
        "model": _model_for_provider(provider_name, settings),
        "timeout_seconds": _timeout_for_provider(provider_name, settings),
        "available": selection.mode_used == "llm" or selection.mode_requested == "mock",
        "configured": configured,
        "env_file_detected": settings.env_file_detected,
        "provider_configured": configured,
        "fallback_used": selection.fallback_used,
        "fallback_reason": selection.fallback_reason,
        "message": message,
    }


def get_safe_debug_config() -> dict[str, object]:
    settings = get_settings()
    return {
        "env_file_detected": settings.env_file_detected,
        "llm_mode": settings.llm_mode,
        "llm_provider": settings.llm_provider,
        "gemini_model": settings.gemini_model,
        "gemini_timeout_seconds": settings.gemini_timeout_seconds,
        "gemini_api_key_present": bool(settings.gemini_api_key),
    }


def _is_provider_configured(provider_name: str, settings: Settings) -> bool:
    if provider_name == "mock":
        return True
    if provider_name == "gemini":
        return bool(settings.gemini_api_key)
    if provider_name == "openai_compatible":
        return bool(settings.llm_api_key and settings.llm_base_url and settings.llm_model)
    return False


def _model_for_provider(provider_name: str, settings: Settings) -> str:
    if provider_name == "gemini":
        return settings.gemini_model or "gemini-3.5-flash"
    if provider_name == "openai_compatible":
        return settings.llm_model
    return ""


def _timeout_for_provider(provider_name: str, settings: Settings) -> int | None:
    if provider_name == "gemini":
        return settings.gemini_timeout_seconds
    if provider_name == "openai_compatible":
        return settings.llm_timeout_seconds
    return None

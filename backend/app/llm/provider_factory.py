from dataclasses import dataclass

from app.core.config import settings
from app.llm.base import LLMConfigurationError, LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider


@dataclass(frozen=True)
class ProviderSelection:
    provider: LLMProvider
    mode_requested: str
    mode_used: str
    provider_name: str
    fallback_used: bool
    fallback_reason: str | None = None


def select_provider(runtime_mode: str | None = None) -> ProviderSelection:
    mode_requested = (runtime_mode or settings.llm_mode or "mock").lower()
    if mode_requested not in {"mock", "llm"}:
        mode_requested = "mock"

    if mode_requested == "mock":
        return ProviderSelection(
            provider=MockLLMProvider(),
            mode_requested="mock",
            mode_used="mock",
            provider_name="mock",
            fallback_used=False,
        )

    provider_name = (settings.llm_provider or "openai_compatible").lower()
    if provider_name == "mock":
        provider_name = "openai_compatible"
    try:
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
                fallback_used=False,
            )
        raise LLMConfigurationError(f"Unsupported LLM_PROVIDER: {provider_name}")
    except LLMConfigurationError as exc:
        return ProviderSelection(
            provider=MockLLMProvider(),
            mode_requested="llm",
            mode_used="mock",
            provider_name="mock",
            fallback_used=True,
            fallback_reason=str(exc),
        )


def get_llm_status() -> dict[str, object]:
    selection = select_provider()
    configured = bool(settings.llm_api_key and settings.llm_base_url and settings.llm_model)
    message = "Mock mode is active. No API key is required."
    if settings.llm_mode == "llm" and not configured:
        message = "LLM_API_KEY or LLM_BASE_URL missing. Agent will fallback to mock mode."
    elif settings.llm_mode == "llm" and configured:
        message = "LLM-assisted mode is configured."
    return {
        "mode": settings.llm_mode or "mock",
        "provider": settings.llm_provider or "mock",
        "model": settings.llm_model,
        "available": selection.mode_used == "llm" or selection.mode_requested == "mock",
        "fallback_used": selection.fallback_used,
        "fallback_reason": selection.fallback_reason,
        "message": message,
    }

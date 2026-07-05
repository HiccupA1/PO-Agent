from abc import ABC, abstractmethod
from typing import Any


class LLMProviderError(Exception):
    pass


class LLMConfigurationError(LLMProviderError):
    pass


class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    def generate_structured_output(
        self,
        task: str,
        system_prompt: str,
        user_input: str,
        context: dict[str, Any],
        expected_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Return a structured dictionary matching the expected schema."""

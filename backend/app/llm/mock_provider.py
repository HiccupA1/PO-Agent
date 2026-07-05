from typing import Any

from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    provider_name = "mock"

    def generate_structured_output(
        self,
        task: str,
        system_prompt: str,
        user_input: str,
        context: dict[str, Any],
        expected_schema: dict[str, Any],
    ) -> dict[str, Any]:
        mock_output = context.get("mock_output", {})
        return mock_output if isinstance(mock_output, dict) else {}

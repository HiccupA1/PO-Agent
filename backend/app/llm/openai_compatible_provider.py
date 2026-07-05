import json
import urllib.request
from typing import Any

from app.llm.base import LLMConfigurationError, LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    provider_name = "openai_compatible"

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: int,
    ) -> None:
        if not api_key:
            raise LLMConfigurationError("LLM_API_KEY missing")
        if not base_url:
            raise LLMConfigurationError("LLM_BASE_URL missing")
        if not model:
            raise LLMConfigurationError("LLM_MODEL missing")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate_structured_output(
        self,
        task: str,
        system_prompt: str,
        user_input: str,
        context: dict[str, Any],
        expected_schema: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": task,
                            "input": user_input,
                            "context": context,
                            "expected_schema": expected_schema,
                        },
                        indent=2,
                    ),
                },
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
        content = raw_response["choices"][0]["message"]["content"]
        return json.loads(content)

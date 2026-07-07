import json
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.llm.base import LLMConfigurationError, LLMProvider, LLMProviderError


class GeminiProvider(LLMProvider):
    provider_name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.5-flash",
        timeout_seconds: int = 120,
    ) -> None:
        if not api_key:
            raise LLMConfigurationError("GEMINI_API_KEY missing")
        self.api_key = api_key
        self.model = model or "gemini-3.5-flash"
        self.timeout_seconds = timeout_seconds
        self.last_attempt_count = 0

    def generate_structured_output(
        self,
        task: str,
        system_prompt: str,
        user_input: str,
        context: dict[str, Any],
        expected_schema: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = (
            f"{system_prompt}\n\n"
            "Generate a fresh, context-aware PO assistant response based on the user input and supplied context. "
            "Do not copy deterministic templates. "
            "Return ONLY valid JSON. Do not include markdown fences, prose, or explanations outside JSON. "
            "Follow the expected schema. Use only supplied context and tool results. "
            "Set human_review_required true when assumptions or ambiguity exist.\n\n"
            f"Task: {task}\n"
            f"User input: {user_input}\n"
            f"Context and tool results:\n{json.dumps(context, indent=2)}\n"
            f"Expected schema:\n{json.dumps(expected_schema, indent=2)}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        encoded_model = urllib.parse.quote(self.model, safe="")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{encoded_model}:generateContent?key={urllib.parse.quote(self.api_key)}"
        )
        raw_response = self._post_with_retries(url, payload)

        try:
            text = raw_response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError("Gemini response did not contain text output") from exc

        cleaned = self._strip_json_fences(text)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(f"Gemini output was not valid JSON: {exc.msg}") from exc
        if not isinstance(parsed, dict):
            raise LLMProviderError("Gemini output JSON was not an object")
        return parsed

    def _strip_json_fences(self, value: str) -> str:
        text = value.strip()
        fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            return fenced.group(1).strip()
        return text

    def _post_with_retries(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        request_body = json.dumps(payload).encode("utf-8")
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            self.last_attempt_count = attempt
            request = urllib.request.Request(
                url,
                data=request_body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="ignore")
                if exc.code in {401, 403}:
                    raise LLMProviderError("Gemini authentication failed") from exc
                if exc.code < 500 or attempt == max_attempts:
                    raise LLMProviderError(f"Gemini request failed: HTTP {exc.code} {detail[:200]}") from exc
            except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
                if attempt == max_attempts:
                    raise LLMProviderError(
                        f"Gemini request timed out or network failed after {attempt} attempt(s): {exc}"
                    ) from exc
            except Exception as exc:
                raise LLMProviderError(f"Gemini request failed: {exc}") from exc

            time.sleep(0.5 * attempt)

        raise LLMProviderError("Gemini request failed after retry attempts")

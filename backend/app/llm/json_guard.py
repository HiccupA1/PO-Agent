import json
from typing import Any


def safe_parse_json(raw_value: Any) -> tuple[dict[str, Any] | None, str | None]:
    if isinstance(raw_value, dict):
        return raw_value, None
    if not isinstance(raw_value, str):
        return None, "Provider output was not JSON text or object."
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        return None, f"Malformed JSON: {exc.msg}"
    if not isinstance(parsed, dict):
        return None, "Provider output JSON was not an object."
    return parsed, None


def validate_required_keys(payload: dict[str, Any], required_keys: list[str]) -> tuple[bool, str | None]:
    missing = [key for key in required_keys if key not in payload]
    if missing:
        return False, f"Provider output missing required key(s): {', '.join(missing)}"
    return True, None


def fallback_to_mock_output(mock_output: dict[str, Any], reason: str) -> tuple[dict[str, Any], str]:
    return mock_output, reason

from abc import ABC, abstractmethod
from typing import Any


class MCPTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, payload: dict[str, Any]) -> Any:
        """Run the mock tool with a simple dictionary payload."""

from abc import ABC, abstractmethod
from typing import Any


class MCPBaseTool(ABC):
    tool_name: str
    display_name: str
    description: str
    input_schema: dict[str, str]
    output_schema: dict[str, str]

    @abstractmethod
    def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Execute a mock MCP-style tool with structured input."""

    def manifest(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "display_name": self.display_name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }

    @property
    def name(self) -> str:
        return self.tool_name

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.execute(payload)


MCPTool = MCPBaseTool

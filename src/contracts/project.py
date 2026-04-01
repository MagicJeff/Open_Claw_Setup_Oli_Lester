from abc import ABC, abstractmethod
from typing import Any


class BaseProject(ABC):
    """Public-safe version of the project interface used by OpenClaw."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def get_tools(self) -> list[dict]:
        """Return the tool declarations exposed by this project."""
        raise NotImplementedError

    @abstractmethod
    async def dispatch_tool(self, tool_name: str, args: dict) -> Any:
        """Execute a tool call for this project."""
        raise NotImplementedError

    def get_system_context(self) -> str:
        """Optional project-specific context for the orchestrator."""
        return ""

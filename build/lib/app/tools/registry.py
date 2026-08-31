from typing import Callable, Type
from pydantic import BaseModel
from app.permissions.checks import check_permission
from app.permissions.roles import UserRole

class Tool(BaseModel):
    """Describes a single tool the agent can use."""

    model_config = {"arbitrary_types_allowed": True}

    name: str
    description: str
    input_schema: Type[BaseModel]
    handler: Callable[[BaseModel], object]

class ToolRegistry:
    """Holds all registered tools and lets us register or look them up."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"A tool named '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"No tool named '{name}' is registered.")
        return self._tools[name]

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def run(self, tool_name: str, role: UserRole, input_data: BaseModel) -> object:
        """Run a tool by name, but only after checking that 
        the given role is permitted to use it."""

        check_permission(role, tool_name)
        tool = self.get(tool_name)
        return tool.handler(input_data)
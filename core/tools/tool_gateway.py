import logging

from core.permissions.permission_service import (
    PermissionService,
)
from core.tools.tool_registry import (
    ToolRegistry,
)


class ToolGateway:
    def __init__(self):
        self.logger = logging.getLogger(
            "shaz.tool_gateway"
        )

        self.registry = ToolRegistry()
        self.permissions = PermissionService()

    def register(
        self,
        name,
        description,
        action,
        function,
    ):
        self.registry.register(
            name=name,
            description=description,
            action=action,
            function=function,
        )

        self.logger.info(
            "Tool registered: %s | action=%s",
            name,
            action,
        )

    async def execute(
        self,
        tool_name,
        **kwargs,
    ):
        tool = self.registry.get(
            tool_name
        )

        if tool is None:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        permission = (
            self.permissions.check(
                tool.action
            )
        )

        if permission == "blocked":
            raise PermissionError(
                f"Tool blocked: {tool_name}"
            )

        if permission == "confirm":
            raise PermissionError(
                f"Confirmation required for: "
                f"{tool_name}"
            )

        self.logger.info(
            "Tool execution started: %s",
            tool_name,
        )

        result = await tool.function(
            **kwargs
        )

        self.logger.info(
            "Tool execution completed: %s",
            tool_name,
        )

        return result

    def list_tools(self):
        return self.registry.list_tools()

    def describe_tools(self):
        return self.registry.describe_tools()

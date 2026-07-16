from core.tools.tool_definition import (
    ToolDefinition,
)


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(
        self,
        name,
        description,
        action,
        function,
    ):
        tool = ToolDefinition(
            name=name,
            description=description,
            action=action,
            function=function,
        )

        self.tools[name] = tool

    def get(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(
            self.tools.keys()
        )

    def describe_tools(self):
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "action": tool.action,
            }
            for tool in self.tools.values()
        ]

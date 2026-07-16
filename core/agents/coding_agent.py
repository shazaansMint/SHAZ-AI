from core.agents.base import Agent
from core.models.model_gateway import ModelGateway


class CodingAgent(Agent):
    def __init__(self):
        self.gateway = ModelGateway()

    def name(self):
        return "coding"

    def can_handle(self, message):
        return True

    async def run(self, message, context=None):
        context = context or {}
        identity = context.get("identity", "")
        memory = context.get("memory", "")

        response = await self.gateway.generate(
            [
                {
                    "role": "system",
                    "content": identity,
                },
                {
                    "role": "system",
                    "content": (
                        "You are SHAZ's coding agent. "
                        "You are an expert software engineer. "
                        "Help Shaz write, understand, debug, "
                        "and improve code. "
                        "Be practical and explain things clearly."
                    ),
                },
                {
                    "role": "system",
                    "content": f"Known SHAZ memory:\n{memory}",
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            model="coding",
        )

        return {
            "agent": self.name(),
            "response": response["message"]["content"],
        }

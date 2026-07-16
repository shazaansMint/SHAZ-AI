from core.agents.base import Agent
from core.models.model_gateway import ModelGateway


class ConversationAgent(Agent):
    def __init__(self):
        self.gateway = ModelGateway()

    def name(self):
        return "conversation"

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
                        "You are SHAZ, Shaz's personal AI system. "
                        "You are direct, natural, honest, and collaborative. "
                        "You are not a generic chatbot. "
                        "You are being built to become Shaz's personal "
                        "AI companion and digital co-founder."
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
            model="fast-chat",
        )

        return {
            "agent": self.name(),
            "response": response["message"]["content"],
        }

from core.router.intent_router import IntentRouter
from core.agents.manager import AgentManager


class SHAZCoordinator:
    def __init__(self):
        self.router = IntentRouter()
        self.agent_manager = AgentManager()

    async def process(self, message):
        intent = self.router.route(message)

        result = await self.agent_manager.run(
            intent,
            message,
        )

        return {
            "intent": intent,
            "result": result,
        }

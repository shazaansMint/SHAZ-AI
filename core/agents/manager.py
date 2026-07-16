from core.agents.conversation_agent import ConversationAgent
from core.agents.coding_agent import CodingAgent


class AgentManager:
    def __init__(self):
        self.agents = [
            ConversationAgent(),
            CodingAgent(),
        ]

    def find_agent(self, intent):
        for agent in self.agents:
            if agent.name() == intent:
                return agent

        return None

    async def run(
        self,
        intent,
        message,
        context=None,
    ):
        agent = self.find_agent(intent)

        if agent is None:
            agent = self.find_agent("conversation")

        return await agent.run(
            message,
            context,
        )

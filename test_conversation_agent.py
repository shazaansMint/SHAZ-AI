import asyncio

from core.agents.conversation_agent import ConversationAgent


async def main():
    agent = ConversationAgent()

    result = await agent.run(
        "What is SHAZ?"
    )

    print(result)


asyncio.run(main())

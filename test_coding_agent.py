import asyncio

from core.agents.coding_agent import CodingAgent


async def main():
    agent = CodingAgent()

    result = await agent.run(
        "Explain what a Python function is in two sentences."
    )

    print(result)


asyncio.run(main())

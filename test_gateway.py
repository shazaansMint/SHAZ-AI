import asyncio

from core.models.model_gateway import ModelGateway


async def test_policy(
    gateway,
    policy,
):
    response = await gateway.generate(
        [
            {
                "role": "user",
                "content": (
                    "Reply with exactly one word: "
                    "CONNECTED"
                ),
            }
        ],
        model=policy,
    )

    print(
        f"{policy} -> "
        f"{response['message']['content']}"
    )


async def main():
    gateway = ModelGateway()

    await test_policy(
        gateway,
        "fast-chat",
    )

    await test_policy(
        gateway,
        "coding",
    )

    await test_policy(
        gateway,
        "reasoning",
    )


asyncio.run(main())

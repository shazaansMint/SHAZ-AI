import asyncio

from core.coordinator import SHAZCoordinator


class SHAZ:
    def __init__(self):
        self.coordinator = SHAZCoordinator()

    async def talk(self, message):
        return await self.coordinator.process(message)


async def main():
    shaz = SHAZ()

    print()
    print("=================================")
    print("        SHAZ IS ONLINE")
    print("=================================")
    print()
    print("Qwen3 8B connected.")
    print("Type 'exit' to shut down SHAZ.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print()
                print("SHAZ: Shutting down.")
                break

            result = await shaz.talk(user_input)
            response = result["result"]["response"]

            print()
            print(f"SHAZ: {response}")
            print()

        except KeyboardInterrupt:
            print()
            print("SHAZ: Shutting down.")
            break

        except Exception as error:
            print()
            print(f"SHAZ Error: {error}")
            print()


if __name__ == "__main__":
    asyncio.run(main())

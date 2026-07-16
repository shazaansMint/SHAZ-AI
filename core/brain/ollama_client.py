from ollama import Client


class OllamaBrain:
    def __init__(self, model="qwen3:8b"):
        self.model = model
        self.client = Client(host="http://localhost:11434")

    def chat(self, messages):
        response = self.client.chat(
            model=self.model,
            messages=messages,
        )

        return response["message"]["content"]

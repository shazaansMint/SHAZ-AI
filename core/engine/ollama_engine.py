from core.engine.base import Engine
from core.brain.ollama_client import OllamaBrain


class OllamaEngine(Engine):
    def __init__(self):
        self.brain = OllamaBrain()

    def chat(self, messages):
        return self.brain.chat(messages)

    def name(self):
        return "ollama"

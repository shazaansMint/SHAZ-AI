from abc import ABC, abstractmethod


class Engine(ABC):
    @abstractmethod
    def chat(self, messages):
        pass

    @abstractmethod
    def name(self):
        pass

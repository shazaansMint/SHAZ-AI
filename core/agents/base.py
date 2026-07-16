from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def can_handle(self, message):
        pass

    @abstractmethod
    def run(self, message, context=None):
        pass

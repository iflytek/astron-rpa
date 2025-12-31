from abc import ABC, abstractmethod


class ISmartCore(ABC):
    @staticmethod
    @abstractmethod
    def print(msg: str = "") -> str:
        pass

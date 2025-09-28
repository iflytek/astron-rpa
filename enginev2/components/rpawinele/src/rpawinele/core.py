from abc import ABC, abstractmethod
from typing import Union

from astronverse.actionlib.types import WinPick


class IWinEleCore(ABC):
    @staticmethod
    @abstractmethod
    def find(pick: WinPick, wait_time: float = 10.0) -> Union["Locator", list["Locator"]]:
        pass

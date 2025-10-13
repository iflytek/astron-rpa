from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Token:
    type: str = None  # TokenType
    value: dict = None


@dataclass
class Node(ABC):
    # 标识
    token: Token = None

    @abstractmethod
    def display(self, svc, tab_num):
        pass


@dataclass
class InputParam:
    types: str
    key: str
    value: Any
    need_eval: bool
    special: str = None

    def show(self, is_func_param: bool = True):
        code = self.value
        if not self.need_eval:
            code = "\"{}\"".format(self.value)
        if self.special:
            code = "{}({})".format(self.special, code)
        if self.key:
            if is_func_param:
                code = "{}={}".format(self.key, code)
            else:
                code = "{} = {}".format(self.key, code)
        return code

    def show_value(self):
        code = self.value
        if not self.need_eval:
            code = "\"{}\"".format(self.value)
        if self.special:
            code = "{}({})".format(self.special, code)
        return code


@dataclass
class OutputParam:
    types: str
    value: str

    def show(self):
        return self.value


class IParam(ABC):

    @abstractmethod
    def parse_param(self, i: dict) -> InputParam:
        pass

    @abstractmethod
    def parse_condition_input(self, token: Token) -> InputParam:
        pass

    @abstractmethod
    def parse_input(self, token: Token) -> Dict[str, InputParam]:
        pass

    @abstractmethod
    def parse_output(self, token: Token) -> List[OutputParam]:
        pass

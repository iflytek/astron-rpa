from typing import Optional
from astronverse.executor.flow.syntax import Token
from astronverse.executor.flow.syntax.token import TokenType
from astronverse.executor.error import BaseException, MISSING_REQUIRED_KEY_ERROR_FORMAT


class Lexer:
    """词法分析，主要是将flow转换成token, 并过滤flow没用的信息"""

    def __init__(self, flow_list: list):
        self.flow_list: list = flow_list  # list dict
        self.position: int = 0
        self.read_position: int = 0
        self.flow: dict = {}

        self.read_flow()  # 初始化

    @staticmethod
    def flow_to_token(flow_json: dict) -> Optional[Token]:
        """将flow转换成token"""

        token_type = flow_json.get("key", "")

        if not token_type:
            raise BaseException(MISSING_REQUIRED_KEY_ERROR_FORMAT.format(flow_json), f"missing key {flow_json}")
        return Token(type=token_type, value=flow_json)

    def read_flow(self):
        """词法分析核心"""

        if self.read_position >= len(self.flow_list):
            self.flow = None
        else:
            self.flow = self.flow_list[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def next_token(self) -> Token:
        """词法分析nex_token"""

        if self.flow is None:
            token = Token(TokenType.EOF.value)
        else:
            token = self.flow_to_token(self.flow)
        self.read_flow()
        return token

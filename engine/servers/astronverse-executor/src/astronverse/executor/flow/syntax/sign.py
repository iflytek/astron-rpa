from dataclasses import dataclass
from enum import Enum
from typing import Any


class SignType(Enum):
    Break = "Break"
    Continue = "Continue"
    Return = "Return"
    # Raise = "Raise"  # 使用python内部raise机制


@dataclass
class Sign:
    type: SignType
    value: Any


# 信号， 避免重复new
BreakSign = Sign(type=SignType.Break, value=None)
ContinueSign = Sign(type=SignType.Continue, value=None)

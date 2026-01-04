"""
Astronverse CUA - Computer Use Agent
使用视觉大模型操作电脑的原子能力组件
"""

import importlib.metadata
from astronverse.cua.computer_use import ComputerUseAgent
from astronverse.cua.action_parser import (
    parse_action_to_structure_output,
    parsing_response_to_pyautogui_code,
)

# 尝试导入包装类（如果可用）
try:
    from astronverse.cua.computer_use import ComputerUse

    __all__ = [
        "ComputerUseAgent",
        "ComputerUse",
        "parse_action_to_structure_output",
        "parsing_response_to_pyautogui_code",
    ]
except ImportError:
    __all__ = [
        "ComputerUseAgent",
        "parse_action_to_structure_output",
        "parsing_response_to_pyautogui_code",
    ]

try:
    __version__ = importlib.metadata.version("astronverse-cua")
except importlib.metadata.PackageNotFoundError:
    __version__ = "1.0.1"  # fallback

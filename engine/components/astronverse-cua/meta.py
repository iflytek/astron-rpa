"""
元数据生成脚本
用于生成原子能力的元数据配置
"""

from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.baseline.config.config import load_config

# 尝试导入ComputerUse类（如果可用）
try:
    from astronverse.cua.computer_use import ComputerUse

    HAS_COMPUTER_USE = True
except ImportError:
    HAS_COMPUTER_USE = False
    print("警告: 无法导入ComputerUse类，可能缺少依赖")


def get_version():
    """获取版本号"""
    pyproject_data = load_config("pyproject.toml")
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    if HAS_COMPUTER_USE:
        atomicMg.register(ComputerUse, version=get_version())
        atomicMg.meta()
    else:
        print("错误: 无法注册ComputerUse类")

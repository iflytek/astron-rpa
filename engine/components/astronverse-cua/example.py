"""
示例：如何使用ComputerUseAgent

使用方法:
1. 先安装包: pip install -e .  (在组件目录下)
2. 设置环境变量: export ARK_API_KEY="your_api_key"  (Windows: set ARK_API_KEY=your_api_key)
3. 运行脚本: python example.py [指令]

示例:
    python example.py "打开计算器并计算 123 + 456"
"""

import os
import sys
from pathlib import Path

# 尝试导入，如果失败则添加路径（用于开发环境）
try:
    from astronverse.cua.computer_use import ComputerUseAgent
except ImportError:
    # 如果包未安装，尝试添加 src 目录到路径（用于开发测试）
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path.parent))
        from astronverse.cua.computer_use import ComputerUseAgent

        print("[提示] 使用开发模式，建议运行 'pip install -e .' 安装包")
    else:
        raise ImportError(
            "无法导入 astronverse.cua。请先安装包：\n  cd engine/components/astronverse-cua\n  pip install -e ."
        )


def main():
    """示例主函数"""
    # 从命令行参数或默认值获取指令
    if len(sys.argv) > 1:
        instruction = " ".join(sys.argv[1:])
    else:
        instruction = "打开计算器并计算 123 + 456"

    # 检查 API Key
    api_key = os.getenv("ARK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("错误: 未设置 API Key")
        print("=" * 60)
        print("请设置环境变量:")
        print("  Linux/Mac: export ARK_API_KEY='your_api_key'")
        print("  Windows:   set ARK_API_KEY=your_api_key")
        print("=" * 60)
        sys.exit(1)

    try:
        # 创建Agent（API Key从环境变量读取）
        print(f"[初始化] 创建 ComputerUseAgent...")
        agent = ComputerUseAgent(
            api_key=api_key,
            model="doubao-1-5-ui-tars-250428",
            language="Chinese",
            max_steps=20,
        )

        # 运行任务
        print(f"[任务] 执行指令: {instruction}")
        result = agent.run(instruction)

        # 打印结果
        print("\n" + "=" * 60)
        print("执行结果:")
        print(f"  成功: {result['success']}")
        print(f"  步数: {result['steps']}")
        print(f"  有效动作步数: {result['action_steps']}")
        print(f"  耗时: {result['duration']:.2f}秒")
        if result.get("error"):
            print(f"  错误: {result['error']}")
        print(f"  截图目录: {agent.screenshot_dir}")
        print("=" * 60)

    except ValueError as e:
        print(f"\n[错误] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[中断] 用户手动停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n[错误] 执行失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

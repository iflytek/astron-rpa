# Astronverse CUA - 计算机使用代理

使用视觉大模型操作电脑的原子能力组件。通过调用视觉大模型（如豆包、Qwen等）分析屏幕截图，自动执行鼠标点击、键盘输入、拖拽等操作，实现GUI自动化任务。

## 功能特性

- 🤖 **视觉理解**: 使用视觉大模型理解屏幕内容
- 🖱️ **鼠标操作**: 支持点击、双击、右键、拖拽等操作
- ⌨️ **键盘操作**: 支持输入文本、快捷键等操作
- 📸 **智能截图**: 自动截图并标记操作位置
- 🔄 **循环执行**: 自动循环执行直到任务完成
- 🎯 **动作解析**: 智能解析模型输出的动作指令

## 安装

```bash
pip install astronverse-cua
```

或者从源码安装：

```bash
git clone <repository-url>
cd astronverse-cua
pip install -e .
```

## 快速开始

### 基本使用

```python
from astronverse.cua.computer_use import ComputerUseAgent

# 创建Agent（使用豆包模型）
agent = ComputerUseAgent(
    api_key="your_api_key",  # 或设置环境变量 ARK_API_KEY
    model="doubao-1-5-ui-tars-250428",
    language="Chinese",
    max_steps=20
)

# 运行任务
result = agent.run("帮我打开计算器并计算 123 + 456")

# 查看结果
if result['success']:
    print(f"任务完成！共执行 {result['steps']} 步")
else:
    print(f"任务失败: {result.get('error', '未知错误')}")
```

### 使用环境变量

```bash
export ARK_API_KEY="your_api_key"
python your_script.py
```

## 支持的操作

- `click(point='<point>x y</point>')` - 单击
- `left_double(point='<point>x y</point>')` - 双击
- `right_single(point='<point>x y</point>')` - 右键点击
- `drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')` - 拖拽
- `hotkey(key='ctrl c')` - 快捷键
- `type(content='xxx')` - 输入文本
- `scroll(point='<point>x y</point>', direction='down')` - 滚动
- `wait()` - 等待
- `finished(content='xxx')` - 任务完成

## 配置参数

- `api_key`: API密钥（必需）
- `model`: 模型ID（默认: "doubao-1-5-ui-tars-250428"）
- `language`: 交互语言（默认: "Chinese"）
- `max_steps`: 最大执行步数（默认: 20）
- `screenshot_dir`: 截图保存目录（可选）
- `temperature`: 模型温度参数（默认: 0.0）

## 项目结构

```
astronverse-cua/
├── src/
│   └── astronverse/
│       └── cua/
│           ├── __init__.py
│           ├── action_parser.py      # 动作解析模块
│           └── computer_use.py      # 主要的ComputerUseAgent类
├── pyproject.toml
├── config.yaml
├── meta.py
└── README.md
```

## 依赖项

- `pyautogui`: GUI自动化操作
- `pillow`: 图像处理
- `openai`: OpenAI兼容API（可选，用于其他模型）
- `pyperclip`: 剪贴板操作（用于文本输入）

## 许可证

Apache License 2.0

## 贡献

欢迎提交Issue和Pull Request！

## 集成到RPA系统

CUA组件已设计为可以嵌入到RPA软件中，通过前端界面调用。

### 集成步骤

1. **在前端使用**：
   - 在流程编排界面中找到 "ComputerUseAgent" 或 "计算机使用代理"
   - 拖拽到流程中
   - 配置参数（至少需要 `instruction`）
   - 运行流程

### 输出参数

组件返回以下输出参数，可在后续节点中使用：
- `success` (Bool): 任务是否成功完成
- `steps` (Int): 总执行步数
- `action_steps` (Int): 有效动作步数
- `duration` (Float): 执行耗时（秒）
- `screenshots` (List): 截图文件路径列表
- `error` (Str, 可选): 错误信息（如果失败）

**独立使用时**：
```python
agent = ComputerUseAgent(api_key="your_api_key")
```

## 测试

运行集成测试：

```bash
# 方法1: 先安装组件（推荐）
pip install -e .
python example.py
```

```
# 方法2: 在RPA项目根目录运行
# 从项目根目录运行，系统会自动找到依赖
如果遇到 `No module named 'astronverse'` 错误：
1. 运行 `pip install -e .` 安装组件
2. 或在完整的RPA项目环境中运行
```
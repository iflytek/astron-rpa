# Astronverse CUA - Computer Use Agent

A computer use agent component that uses vision LLMs to operate computers. By calling vision LLMs (such as Doubao, Qwen, etc.) to analyze screen screenshots, it automatically performs mouse clicks, keyboard input, drag-and-drop operations, and other actions to achieve GUI automation tasks.

## Features

- 🤖 **Vision Understanding**: Uses vision LLMs to understand screen content
- 🖱️ **Mouse Operations**: Supports click, double-click, right-click, drag-and-drop, etc.
- ⌨️ **Keyboard Operations**: Supports text input, hotkeys, etc.
- 📸 **Smart Screenshots**: Automatically captures screenshots and marks operation positions
- 🔄 **Loop Execution**: Automatically loops until the task is completed
- 🎯 **Action Parsing**: Intelligently parses action instructions from model output
- 📡 **Real-time Streaming**: Real-time streaming output of model responses to frontend

## Installation

```bash
pip install astronverse-cua
```

Or install from source:

```bash
git clone <repository-url>
cd astronverse-cua
pip install -e .
```

## Quick Start

### Basic Usage

```python
from astronverse.cua.computer_use import ComputerUseAgent

# Create Agent (using Doubao model)
agent = ComputerUseAgent(
    api_key="your_api_key",  # or set environment variable ARK_API_KEY
    model="doubao-1-5-ui-tars-250428",
    language="Chinese",
    max_steps=20
)

# Run task
result = agent.run("Open calculator and calculate 123 + 456")

# Check result
if result['success']:
    print(f"Task completed! Total steps: {result['steps']}")
else:
    print(f"Task failed: {result.get('error', 'Unknown error')}")
```

### Using Environment Variables

```bash
export ARK_API_KEY="your_api_key"
python your_script.py
```

## Supported Actions

- `click(point='<point>x y</point>')` - Single click
- `left_double(point='<point>x y</point>')` - Double click
- `right_single(point='<point>x y</point>')` - Right click
- `drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')` - Drag
- `hotkey(key='ctrl c')` - Hotkey
- `type(content='xxx')` - Type text
- `scroll(point='<point>x y</point>', direction='down')` - Scroll
- `wait()` - Wait
- `finished(content='xxx')` - Task completed

## Configuration Parameters

- `api_key`: API key (required)
- `model`: Model ID (default: "doubao-1-5-ui-tars-250428")
- `language`: Interaction language (default: "Chinese")
- `max_steps`: Maximum execution steps (default: 20)
- `screenshot_dir`: Screenshot save directory (optional)
- `temperature`: Model temperature parameter (default: 0.0)
- `enable_stream_output`: Enable real-time streaming output (default: True)

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

## Dependencies

- `pyautogui`: GUI automation operations
- `pillow`: Image processing
- `openai`: OpenAI-compatible API (optional, for other models)
- `pyperclip`: Clipboard operations (for text input)

## Integration with RPA System

The CUA component is designed to be embedded in the RPA software and can be called through the frontend interface.

### Integration Steps

1. **Install the component**:
   ```bash
   cd engine/components/astronverse-cua
   pip install -e .
   ```

2. **Generate metadata**:
   ```bash
   python meta.py
   ```

3. **Restart RPA system**: The system will automatically load the newly registered atomic capability

4. **Use in frontend**:
   - Find "ComputerUseAgent" or "计算机使用代理" in the process orchestration interface
   - Drag it into the process
   - Configure parameters (at least `instruction` is required)
   - Run the process

### Output Parameters

The component returns the following output parameters that can be used in subsequent nodes:
- `success` (Bool): Whether the task completed successfully
- `steps` (Int): Total execution steps
- `action_steps` (Int): Valid action steps
- `duration` (Float): Execution duration (seconds)
- `screenshots` (List): List of screenshot file paths
- `error` (Str, optional): Error message (if failed)

### Real-time Streaming Output

CUA component supports real-time streaming output of model responses. The frontend can display model return content in real-time through the RPA system's logging system.

**When used in RPA process**:
- Automatically obtains process context (`__process_id__` and `__line__`)
- Automatically enables real-time streaming output
- Displays model responses in real-time in the execution log window:
  ```
  [CUA模型响应] [模型响应开始]
  [CUA模型响应] Thought: I need to analyze screen content...
  [CUA模型响应] Action: click(point='<point>100 200</point>')
  [CUA模型响应] [模型响应结束]
  ```

**When used standalone**:
```python
agent = ComputerUseAgent(
    api_key="your_api_key",
    enable_stream_output=True,  # Enable streaming output (default True)
    process_id="test_process",   # Process ID (optional)
    line=1,                      # Line number (optional)
)
```

### Troubleshooting

**Component not appearing in frontend**:
1. Run `python meta.py` to generate metadata
2. Check if `meta.json` file exists
3. Restart RPA system

**Error "API Key not provided"**:
1. Set environment variable `ARK_API_KEY`
2. Or provide `api_key` directly in component parameters

**No real-time output in frontend**:
1. Ensure `enable_stream_output=True`
2. When used in RPA process, system automatically injects context parameters
3. Check if execution log window is open

## License

Apache License 2.0

## Contributing

Welcome to submit Issues and Pull Requests!

## Testing

Run integration tests:

```bash
# Method 1: Install component first (recommended)
pip install -e .
python example.py

# Method 2: Run from RPA project root
# Run from project root, system will automatically find dependencies
```

If you encounter `No module named 'astronverse'` error:
1. Run `pip install -e .` to install the component
2. Or run in a complete RPA project environment
3. See [Testing Guide](README_TESTING.md) for details

## Related Links

- [Astronverse RPA Platform](https://github.com/your-org/astron-rpa)


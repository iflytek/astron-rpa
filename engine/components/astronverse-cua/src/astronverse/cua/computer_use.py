"""
Computer Use Agent - 使用视觉大模型操作电脑
实现完整的自动化流程：用户指令 → 截图 → 模型分析 → 执行操作 → 循环直到任务完成
"""

import os
import time
import tempfile
import base64
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from datetime import datetime

import pyautogui
from PIL import Image, ImageDraw
from openai import OpenAI
# from volcenginesdkarkruntime import Ark

from astronverse.cua.action_parser import (
    parse_action_to_structure_output,
    parsing_response_to_pyautogui_code,
)

# 尝试导入actionlib（如果可用）
try:
    from astronverse.actionlib.atomic import atomicMg
    from astronverse.actionlib.report import report
    from astronverse.actionlib import ReportType, ReportCode, ReportCodeStatus

    HAS_ACTIONLIB = True
except ImportError:
    HAS_ACTIONLIB = False
    # 定义占位符，避免运行时错误
    report = None
    ReportType = None
    ReportCode = None
    ReportCodeStatus = None

# 设置PyAutoGUI安全设置
pyautogui.FAILSAFE = False  # 鼠标移到左上角会触发异常停止
pyautogui.PAUSE = 0.5  # 每个操作之间暂停0.5秒


# 电脑 GUI 任务场景的提示词模板
COMPUTER_USE_PROMPT = """You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.

## Output Format
```
Thought: ...
Action: ...
```

## Action Space
click(point='<point>x1 y1</point>')
left_double(point='<point>x1 y1</point>')
right_single(point='<point>x1 y1</point>')
drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')
hotkey(key='ctrl c') # Split keys with a space and use lowercase. Also, do not use more than 3 keys in one hotkey action.
type(content='xxx') # Use escape characters \\', \\\", and \\n in content part to ensure we can parse the content in normal python string format. If you want to submit your input, use \\n at the end of content. 
scroll(point='<point>x1 y1</point>', direction='down or up or right or left') # Show more information on the `direction` side.
wait() #Sleep for 5s and take a screenshot to check for any changes.
finished(content='xxx') # Use escape characters \\', \\", and \\n in content part to ensure we can parse the content in normal python string format.

## Note
- Use {language} in `Thought` part.
- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.

## User Instruction
{instruction}
"""


class ComputerUseAgent:
    """计算机使用代理类 - 使用视觉大模型操作电脑"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "doubao-1-5-ui-tars-250428",
        language: str = "Chinese",
        max_steps: int = 20,
        screenshot_dir: Optional[str] = None,
        temperature: float = 0.0,
        provider: str = "doubao",  # "doubao" or "openai"
        enable_stream_output: bool = True,  # 是否启用实时流式输出
        process_id: Optional[str] = None,  # 流程ID，用于日志输出
        line: Optional[int] = None,  # 当前行号，用于日志输出
    ):
        """
        初始化Agent

        Args:
            api_key: API密钥，如果不提供则从环境变量读取（ARK_API_KEY 或 OPENAI_API_KEY）
            model: 使用的模型ID
            language: 交互语言
            max_steps: 最大执行步数
            screenshot_dir: 截图保存目录，默认使用临时目录
            temperature: 模型温度参数
            provider: 模型提供商，"doubao" 或 "openai"
        """
        self.api_key = api_key or os.getenv("ARK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key未提供，请设置环境变量ARK_API_KEY/OPENAI_API_KEY或传入api_key参数")

        self.provider = provider
        if provider == "doubao":
            # self.client = Ark(api_key=self.api_key)
            self.client = OpenAI(api_key=self.api_key, base_url="https://ark.cn-beijing.volces.com/api/v3")
        elif provider == "openai":
            self.client = OpenAI(api_key=self.api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        else:
            raise ValueError(f"不支持的provider: {provider}")

        self.model = model
        self.language = language
        self.max_steps = max_steps
        self.temperature = temperature

        # 设置截图目录
        if screenshot_dir:
            self.screenshot_dir = Path(screenshot_dir)
        else:
            self.screenshot_dir = Path(tempfile.mkdtemp(prefix="cua_agent_"))
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # 历史记录
        self.action_history: List[Dict] = []
        self.screenshots: List[str] = []
        # 保存对话历史：(assistant响应, (base64_image, image_format) 或 None)
        self.conversation_history: List[Tuple[str, Optional[Tuple[str, str]]]] = []
        self.pending_response: Optional[str] = None  # 待保存的响应（等待下一步的截图）
        self.instruction: Optional[str] = None  # 保存用户指令

        # 保存上一次点击的坐标，用于在下一次截图上标记
        self.last_click_coords: Optional[Tuple[int, int]] = None

        # 屏幕尺寸缓存，避免每次都打开Image文件
        self.screen_width = None
        self.screen_height = None
        self.max_screenshots = 5

        # 连续无action计数器，用于追踪连续没有action的步骤数
        self.consecutive_no_action = 0

        # 连续相同action追踪
        self.last_action = None  # 保存上一次的action
        self.consecutive_same_action = 1  # 连续相同action的次数

        # 实时输出相关
        self.enable_stream_output = enable_stream_output
        self.process_id = process_id
        self.line = line

        print(f"[初始化] 截图保存目录: {self.screenshot_dir}")

    def take_screenshot(self) -> Tuple[str, str]:
        """
        截取当前屏幕，并在截图上标记上一次点击的位置（如果有）

        Returns:
            Tuple[截图文件路径, Base64编码的图片]
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.screenshot_dir / f"screenshot_{timestamp}.png"

        # 使用pyautogui截图
        screenshot = pyautogui.screenshot()
        screenshot.save(str(screenshot_path))

        # 第一次截图时保存屏幕尺寸，避免后续每次都打开Image文件
        if self.screen_width is None or self.screen_height is None:
            self.screen_width, self.screen_height = screenshot.size
            print(f"[初始化] 保存屏幕尺寸: {self.screen_width}x{self.screen_height}")

        # 如果有上一次点击坐标，在截图上标记
        final_screenshot_path = str(screenshot_path)
        if self.last_click_coords:
            x, y = self.last_click_coords
            final_screenshot_path = self._mark_click_on_image(str(screenshot_path), x, y)

        # 编码为Base64（使用标记后的图片）
        with open(final_screenshot_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        return final_screenshot_path, base64_image

    def _mark_click_on_image(self, image_path: str, x: int, y: int, radius: int = 20) -> str:
        """
        在截图上绘制红色圆点标记，表示上一次点击的位置

        Args:
            image_path: 截图文件路径
            x: 点击的X坐标（屏幕坐标）
            y: 点击的Y坐标（屏幕坐标）
            radius: 标记圆点半径（像素）

        Returns:
            标记后的图片路径
        """
        try:
            # 打开图片
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)

            # 绘制红色实心圆点
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill="red", outline="white", width=3)

            # 绘制外圈
            draw.ellipse([x - radius - 10, y - radius - 10, x + radius + 10, y + radius + 10], outline="red", width=3)

            # 绘制十字准线
            line_length = radius + 15
            draw.line([x - line_length, y, x + line_length, y], fill="red", width=2)
            draw.line([x, y - line_length, x, y + line_length], fill="red", width=2)

            # 保存标记后的图片
            marked_path = str(Path(image_path).parent / f"marked_{Path(image_path).name}")
            img.save(marked_path)

            return marked_path
        except Exception as e:
            return image_path  # 如果出错，返回原始路径

    def _extract_click_coordinates(
        self, action: Dict, image_height: int, image_width: int
    ) -> Optional[Tuple[int, int]]:
        """
        从动作中提取点击坐标

        Args:
            action: 动作字典
            image_height: 截图高度
            image_width: 截图宽度

        Returns:
            屏幕坐标 (x, y)，如果不是点击操作则返回None
        """
        action_type = action.get("action_type", "")
        action_inputs = action.get("action_inputs", {})

        # 检查是否是点击类操作
        click_actions = ["click", "left_single", "left_double", "right_single"]
        if action_type not in click_actions:
            return None

        # 提取坐标
        start_box = action_inputs.get("start_box")
        if not start_box:
            return None

        try:
            # 解析坐标（相对坐标）
            start_box = eval(str(start_box))
            if len(start_box) == 4:
                x1, y1, x2, y2 = start_box
            elif len(start_box) == 2:
                x1, y1 = start_box
                x2 = x1
                y2 = y1
            else:
                return None

            # 转换为屏幕绝对坐标
            x = round(float((x1 + x2) / 2) * image_width)
            y = round(float((y1 + y2) / 2) * image_height)

            return (x, y)
        except Exception as e:
            print(f"[警告] 无法解析坐标: {e}")
            return None

    def build_messages(self, instruction: str, screenshot_path: str, base64_image: str) -> List[Dict]:
        """
        构建发送给模型的消息（包含完整对话历史）

        Args:
            instruction: 用户指令
            screenshot_path: 截图路径
            base64_image: Base64编码的图片
        """
        # 保存指令（用于后续步骤）
        if not self.instruction:
            self.instruction = instruction

        # 获取图片格式
        image_format = Path(screenshot_path).suffix[1:] or "png"

        # 构建系统提示词
        system_prompt = COMPUTER_USE_PROMPT.format(instruction=self.instruction, language=self.language)

        messages: List[Dict] = []

        # 第一步：只有system_prompt和第一张截图
        if not self.conversation_history:
            messages = [
                {"role": "user", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/{image_format};base64,{base64_image}"}}
                    ],
                },
            ]
        else:
            # 后续步骤：按照格式添加历史对话
            messages.append({"role": "user", "content": system_prompt})

            # 添加历史对话：assistant响应 + 对应的截图（交替）
            for assistant_response, screenshot_info in self.conversation_history:
                # 添加assistant的响应
                messages.append({"role": "assistant", "content": assistant_response})

                # 如果截图信息存在，添加对应的截图（user消息）
                if screenshot_info is not None:
                    msg_image, msg_format = screenshot_info
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/{msg_format};base64,{msg_image}"},
                                }
                            ],
                        }
                    )

            # 添加当前截图
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/{image_format};base64,{base64_image}"}}
                    ],
                }
            )

        return messages

    def inference(self, messages: List[Dict], stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        调用模型进行推理

        Args:
            messages: 消息列表
            stream_callback: 流式输出回调函数，接收(content: str)参数，用于实时输出模型响应

        Returns:
            模型响应文本
        """
        if self.provider == "doubao":
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=self.temperature, stream=True
            )

            # 流式响应拼接
            full_response = ""
            print("\n[模型响应]")

            # 如果提供了回调函数，实时输出
            if stream_callback:
                stream_callback("[模型响应开始]\n")

            for chunk in response:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        content = delta.content
                        full_response += content
                        print(content, end="", flush=True)

                        # 实时回调输出
                        if stream_callback:
                            stream_callback(content)

            print("\n")

            # 如果提供了回调函数，通知结束
            if stream_callback:
                stream_callback("\n[模型响应结束]\n")

            return full_response
        else:  # openai
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=True if stream_callback else False,
            )

            if stream_callback:
                # OpenAI流式输出
                full_response = ""
                stream_callback("[模型响应开始]\n")
                for chunk in response:
                    if hasattr(chunk, "choices") and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            content = delta.content
                            full_response += content
                            stream_callback(content)
                stream_callback("\n[模型响应结束]\n")
                return full_response
            else:
                return response.choices[0].message.content

    def _limit_screenshots_in_history(self) -> None:
        """
        限制对话历史中的截图数量，最多保留max_screenshots-1个截图
        """
        screenshots_count = sum(1 for _, screenshot_info in self.conversation_history if screenshot_info is not None)

        max_screenshots_in_history = self.max_screenshots - 1
        if screenshots_count >= max_screenshots_in_history:
            for i, (assistant_response, screenshot_info) in enumerate(self.conversation_history):
                if screenshot_info is not None:
                    self.conversation_history[i] = (assistant_response, None)
                    remaining_count = screenshots_count - 1
                    break

    def execute_action(self, action, image_height, image_width) -> bool:
        """
        执行动作，并保存点击坐标用于下一次截图的标记

        Args:
            action: 动作字典或动作列表
            image_height: 截图高度
            image_width: 截图宽度

        Returns:
            是否执行成功（任务完成）
        """
        try:
            # 处理action可能是列表的情况
            action_to_process = action
            if isinstance(action, list) and len(action) > 0:
                action_to_process = action[0]  # 取第一个action用于提取坐标
            elif isinstance(action, list) and len(action) == 0:
                return False

            # 在执行前提取点击坐标（如果是点击操作）
            if isinstance(action_to_process, dict):
                click_coords = self._extract_click_coordinates(action_to_process, image_height, image_width)
                if click_coords:
                    self.last_click_coords = click_coords

            py_code = parsing_response_to_pyautogui_code(action, image_height, image_width)

            if py_code == "DONE":
                return True

            # 创建执行环境
            exec_globals = {"pyautogui": pyautogui, "time": time, "pyperclip": None}

            # 尝试导入pyperclip（用于type动作的粘贴）
            try:
                import pyperclip

                exec_globals["pyperclip"] = pyperclip
            except ImportError:
                print("[警告] pyperclip未安装，type动作可能使用write方式")

            # 执行代码
            exec(py_code, exec_globals)

            # 等待操作完成
            time.sleep(0.5)

            return False  # 未完成，继续循环

        except Exception as e:
            print(f"[错误] 执行动作时出错: {e}")
            import traceback

            traceback.print_exc()
            return False

    def run(self, instruction: str) -> Dict:
        """
        运行自动化任务

        Args:
            instruction: 用户指令

        Returns:
            执行结果字典
        """
        print(f"\n{'=' * 60}")
        print(f"[任务开始] {instruction}")
        print(f"{'=' * 60}\n")

        step = 0
        action_step = 0
        start_time = time.time()

        try:
            while step < self.max_steps:
                step += 1
                print(f"\n[步骤 {step}/{self.max_steps}]")
                print("-" * 60)

                # 1. 截图（执行动作后的新状态）
                screenshot_path, base64_image = self.take_screenshot()
                self.screenshots.append(screenshot_path)

                # 如果有待保存的响应，现在保存（因为有了新的截图）
                if self.pending_response:
                    # 在添加新历史前，先清理旧的截图以限制数量
                    self._limit_screenshots_in_history()

                    image_format = Path(screenshot_path).suffix[1:] or "png"
                    self.conversation_history.append(
                        (
                            self.pending_response,  # 上一步的响应
                            (base64_image, image_format),  # 当前步骤的截图（执行动作后的新状态）
                        )
                    )
                    self.pending_response = None

                # 2. 构建消息并调用模型
                print("模型分析中...")
                messages = self.build_messages(instruction, screenshot_path, base64_image)

                # 创建流式输出回调函数
                def stream_callback(content: str):
                    """实时输出模型响应的回调函数"""
                    if self.enable_stream_output and HAS_ACTIONLIB and report and self.process_id:
                        # 使用report模块输出实时日志，前端可以通过WebSocket接收
                        report.info(
                            ReportCode(
                                log_type=ReportType.User,
                                process_id=self.process_id,
                                line=self.line or 0,
                                status=ReportCodeStatus.RES,
                                msg_str=f"[CUA模型响应] {content}",
                            )
                        )

                response = self.inference(
                    messages, stream_callback=stream_callback if self.enable_stream_output else None
                )

                # 保存响应，等待下一步的截图再一起保存到历史
                self.pending_response = response

                # 3. 解析响应
                # 直接使用缓存的屏幕尺寸，避免每次都打开Image文件
                image_width, image_height = self.screen_width, self.screen_height
                model_type = "doubao" if self.provider == "doubao" else "qwen25vl"
                action = parse_action_to_structure_output(
                    response, 1000, image_height, image_width, model_type=model_type
                )
                if not action:
                    # 更新连续无action计数器
                    self.consecutive_no_action += 1

                    # 如果连续两次无action，清空历史会话，只保留最开始的system_prompt
                    if self.consecutive_no_action >= 3:
                        self.conversation_history.clear()
                        self.pending_response = None
                        self.consecutive_no_action = 0

                    continue
                else:
                    # 有有效动作，重置连续无action计数器
                    self.consecutive_no_action = 0
                    action_step += 1

                    # 检查连续相同action
                    current_action_key = (action[0].get("action_type"), action[0].get("action_inputs"))
                    if current_action_key == self.last_action:
                        self.consecutive_same_action += 1

                        if self.consecutive_same_action >= 3:
                            self.conversation_history.clear()
                            self.pending_response = None
                            self.consecutive_same_action = 1
                            self.consecutive_no_action = 0
                            self.last_action = None
                            continue
                    else:
                        self.consecutive_same_action = 1
                        self.last_action = current_action_key

                # 4. 执行动作
                print("执行动作...")

                is_finished = self.execute_action(action, image_height, image_width)

                if is_finished:
                    print("\n" + "=" * 60)
                    print("[任务成功完成]")
                    print(f"总步骤数: {step}")
                    print(f"总耗时: {time.time() - start_time:.2f}秒")
                    print("=" * 60)
                    return {
                        "success": True,
                        "steps": step,
                        "action_steps": action_step,
                        "duration": time.time() - start_time,
                        "screenshots": self.screenshots,
                    }

                # 等待界面响应
                print("等待界面响应...")
                time.sleep(1)

            # 达到最大步数
            print("\n" + "=" * 60)
            print("[任务未完成] 已达到最大步数限制")
            print(f"总步骤数: {step}")
            print(f"总耗时: {time.time() - start_time:.2f}秒")
            print("=" * 60)
            return {
                "success": False,
                "steps": step,
                "action_steps": action_step,
                "duration": time.time() - start_time,
                "screenshots": self.screenshots,
                "error": "达到最大步数限制",
            }

        except KeyboardInterrupt:
            print("\n\n[任务中断] 用户手动停止")
            return {
                "success": False,
                "steps": step,
                "action_steps": action_step,
                "duration": time.time() - start_time,
                "screenshots": self.screenshots,
                "error": "用户中断",
            }
        except Exception as e:
            print(f"\n\n[任务失败] 发生错误: {e}")
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "steps": step,
                "action_steps": action_step,
                "duration": time.time() - start_time,
                "screenshots": self.screenshots,
                "error": str(e),
            }


# 为了兼容原子能力注册系统，创建一个包装类
if HAS_ACTIONLIB:

    class ComputerUse:
        """Computer Use Agent包装类，用于原子能力注册"""

        @staticmethod
        @atomicMg.atomic(
            "ComputerUseAgent",
            inputList=[
                atomicMg.param("instruction", types="Str"),
                atomicMg.param("api_key", types="Str", required=False),
                atomicMg.param("model", types="Str", required=False),
                atomicMg.param("language", types="Str", required=False),
                atomicMg.param("max_steps", types="Int", required=False),
                atomicMg.param("screenshot_dir", types="Str", required=False),
                atomicMg.param("temperature", types="Float", required=False),
                atomicMg.param("provider", types="Str", required=False),
            ],
            outputList=[
                atomicMg.param("success", types="Bool"),
                atomicMg.param("steps", types="Int"),
                atomicMg.param("action_steps", types="Int"),
                atomicMg.param("duration", types="Float"),
                atomicMg.param("screenshots", types="List"),
                atomicMg.param("error", types="Str", required=False),
            ],
        )
        def run(
            instruction: str,
            api_key: Optional[str] = None,
            model: str = "doubao-1-5-ui-tars-250428",
            language: str = "Chinese",
            max_steps: int = 20,
            screenshot_dir: Optional[str] = None,
            temperature: float = 0.0,
            provider: str = "doubao",
            enable_stream_output: bool = True,
            **kwargs,  # 接收RPA系统注入的上下文参数，如__process_id__, __line__等
        ):
            """
            运行计算机使用代理任务

            Args:
                instruction: 用户指令
                api_key: API密钥
                model: 模型ID
                language: 交互语言
                max_steps: 最大执行步数
                screenshot_dir: 截图保存目录
                temperature: 模型温度参数
                provider: 模型提供商

            Returns:
                执行结果，包含success, steps, action_steps, duration, screenshots, error等字段
            """
            # 从kwargs中提取RPA系统注入的上下文参数
            process_id = kwargs.get("__process_id__") or kwargs.get("process_id")
            line = kwargs.get("__line__") or kwargs.get("line")

            agent = ComputerUseAgent(
                api_key=api_key,
                model=model,
                language=language,
                max_steps=max_steps,
                screenshot_dir=screenshot_dir,
                temperature=temperature,
                provider=provider,
                enable_stream_output=enable_stream_output,
                process_id=process_id,
                line=line,
            )
            result = agent.run(instruction)

            # 返回结果，确保所有输出参数都有值
            return {
                "success": result.get("success", False),
                "steps": result.get("steps", 0),
                "action_steps": result.get("action_steps", 0),
                "duration": result.get("duration", 0.0),
                "screenshots": result.get("screenshots", []),
                "error": result.get("error", ""),
            }

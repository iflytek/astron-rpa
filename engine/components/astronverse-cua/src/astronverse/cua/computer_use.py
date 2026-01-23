"""
Computer Use Agent - 使用视觉大模型操作电脑
实现完整的自动化流程：用户指令 → 截图 → 模型分析 → 执行操作 → 循环直到任务完成
"""

import base64
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pyautogui
import pyperclip
import requests
from astronverse.actionlib.atomic import atomicMg
from astronverse.baseline.logger.logger import logger
from astronverse.cua.action_parser import (
    parse_action_to_structure_output,
    parsing_response_to_pyautogui_code,
)
from astronverse.cua.custom_action_screen import CustomActionScreen
from PIL import Image, ImageDraw

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
- Use Chinese in `Thought` part.
- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.

## User Instruction
{instruction}
"""

API_URL = "http://127.0.0.1:{}/api/rpa-ai-service/cua/chat".format(
    atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
)


class ComputerUseAgent:
    """计算机使用代理类 - 使用视觉大模型操作电脑"""

    def __init__(
        self,
        max_steps: int = 20,
        temperature: float = 0.0,
    ):
        """
        初始化Agent

        Args:
            max_steps: 最大执行步数
            temperature: 模型温度参数
        """

        self.max_steps = max_steps
        self.temperature = temperature

        # 设置截图目录
        self.screenshot_dir = Path(tempfile.mkdtemp(prefix="cua_agent_"))
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # 历史记录
        self.action_history: list[dict] = []
        self.screenshots: list[str] = []
        # 保存对话历史：(assistant响应, (base64_image, image_format) 或 None)
        self.conversation_history: list[tuple[str, Optional[tuple[str, str]]]] = []
        self.pending_response: Optional[str] = None  # 待保存的响应（等待下一步的截图）
        self.instruction: Optional[str] = None  # 保存用户指令

        # 保存上一次点击的坐标，用于在下一次截图上标记
        self.last_click_coords: Optional[tuple[int, int]] = None

        # 屏幕尺寸缓存，避免每次都打开Image文件
        self.screen_width = None
        self.screen_height = None
        self.max_screenshots = 5

        # 连续无action计数器，用于追踪连续没有action的步骤数
        self.consecutive_no_action = 0

        # 连续相同action追踪
        self.last_action = None  # 保存上一次的action
        self.consecutive_same_action = 1  # 连续相同action的次数

        logger.info(f"[初始化] 截图保存目录: {self.screenshot_dir}")

    def take_screenshot(self) -> tuple[str, str]:
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
            logger.info(f"[初始化] 保存屏幕尺寸: {self.screen_width}x{self.screen_height}")

        # 如果有上一次点击坐标，在截图上标记
        final_screenshot_path = str(screenshot_path)
        if self.last_click_coords:
            x, y = self.last_click_coords
            final_screenshot_path = self.mark_click_on_image(str(screenshot_path), x, y)

        # 编码为Base64（使用标记后的图片）
        with open(final_screenshot_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        return final_screenshot_path, base64_image

    @staticmethod
    def mark_click_on_image(image_path: str, x: int, y: int, radius: int = 20) -> str:
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

    @staticmethod
    def extract_click_coordinates(action: dict, image_height: int, image_width: int) -> Optional[tuple[int, int]]:
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
            logger.info(f"[警告] 无法解析坐标: {e}")
            return None

    def build_messages(self, instruction: str, screenshot_path: str, base64_image: str) -> list[dict]:
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
        system_prompt = COMPUTER_USE_PROMPT.format(instruction=self.instruction)

        messages: list[dict] = []

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

    def inference(self, messages: list[dict] = None) -> str:
        """
        调用模型进行推理

        Args:
            messages: 消息列表

        Returns:
            模型响应文本
        """

        try:
            # 发送 API 请求
            response = requests.post(API_URL, data=json.dumps(messages, ensure_ascii=False))
            response.raise_for_status()  # 检查请求是否成功

            # 返回模型生成的回复
            response_json = response.json()

            # 兼容两种响应格式
            if "data" in response_json and "choices" in response_json["data"]:
                # 新格式
                return response_json["data"]["choices"][0]["message"]["content"]
            elif "choices" in response_json:
                # 原格式
                return response_json["choices"][0]["message"]["content"]
            else:
                raise ValueError("未知的响应格式")

        except requests.exceptions.RequestException as e:
            logger.info(f"请求错误: {e}")
            return None
        except KeyError:
            logger.info("响应格式不正确")
            return None

    def limit_screenshots_in_history(self) -> None:
        """
        限制对话历史中的截图数量，最多保留max_screenshots-1个截图
        """
        screenshots_count = sum(1 for _, screenshot_info in self.conversation_history if screenshot_info is not None)

        max_screenshots_in_history = self.max_screenshots - 1
        if screenshots_count >= max_screenshots_in_history:
            for i, (assistant_response, screenshot_info) in enumerate(self.conversation_history):
                if screenshot_info is not None:
                    self.conversation_history[i] = (assistant_response, None)
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
                click_coords = self.extract_click_coordinates(action_to_process, image_height, image_width)
                if click_coords:
                    self.last_click_coords = click_coords

            py_code = parsing_response_to_pyautogui_code(action, image_height, image_width)

            if py_code == "DONE":
                return True

            # 创建执行环境
            exec_globals = {"pyautogui": pyautogui, "time": time, "pyperclip": pyperclip}

            # 执行代码
            exec(py_code, exec_globals)

            # 等待操作完成
            time.sleep(0.5)

            return False  # 未完成，继续循环

        except Exception as e:
            logger.info(f"[错误] 执行动作时出错: {e}")
            import traceback

            traceback.logger.info_exc()
            return False

    def run(self, instruction: str) -> dict:
        """
        运行自动化任务

        Args:
            instruction: 用户指令

        Returns:
            执行结果字典
        """
        logger.info(f"{'=' * 60}")
        logger.info(f"[任务开始] {instruction}")
        logger.info(f"{'=' * 60}\n")

        step = 0
        action_step = 0
        start_time = time.time()

        # 设置PyAutoGUI安全设置
        current_failsafe = pyautogui.FAILSAFE
        current_pause = pyautogui.PAUSE
        pyautogui.FAILSAFE = False  # 鼠标移到左上角会触发异常停止
        pyautogui.PAUSE = 0.5  # 每个操作之间暂停0.5秒

        try:
            while step < self.max_steps:
                step += 1
                logger.info(f"[步骤 {step}/{self.max_steps}]")
                logger.info("-" * 60)

                # 1. 截图（执行动作后的新状态）
                screenshot_path, base64_image = self.take_screenshot()
                self.screenshots.append(screenshot_path)

                # 如果有待保存的响应，现在保存（因为有了新的截图）
                if self.pending_response:
                    # 在添加新历史前，先清理旧的截图以限制数量
                    self.limit_screenshots_in_history()

                    image_format = Path(screenshot_path).suffix[1:] or "png"
                    self.conversation_history.append(
                        (
                            self.pending_response,  # 上一步的响应
                            (base64_image, image_format),  # 当前步骤的截图（执行动作后的新状态）
                        )
                    )
                    self.pending_response = None

                # 2. 构建消息并调用模型
                logger.info("模型分析中...")
                messages = self.build_messages(instruction, screenshot_path, base64_image)

                response = self.inference(messages)
                logger.info(response)

                # 保存响应，等待下一步的截图再一起保存到历史
                self.pending_response = response

                # 3. 解析响应
                # 直接使用缓存的屏幕尺寸，避免每次都打开Image文件
                image_width, image_height = self.screen_width, self.screen_height
                action = parse_action_to_structure_output(
                    response, 1000, image_height, image_width, model_type="doubao"
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
                logger.info("执行动作...")

                is_finished = self.execute_action(action, image_height, image_width)

                if is_finished:
                    logger.info("=" * 60)
                    logger.info("[任务成功完成]")
                    logger.info(f"总步骤数: {step}")
                    logger.info(f"总耗时: {time.time() - start_time:.2f}秒")
                    logger.info("=" * 60)
                    return {
                        "success": True,
                        "steps": step,
                        "duration": time.time() - start_time,
                        "screenshots": self.screenshot_dir,
                    }

                # 等待界面响应
                logger.info("等待界面响应...")
                time.sleep(1)
            # 达到最大步数
            logger.info("=" * 60)
            logger.info("[任务未完成] 已达到最大步数限制")
            logger.info(f"总步骤数: {step}")
            logger.info(f"总耗时: {time.time() - start_time:.2f}秒")
            logger.info("=" * 60)
            return {
                "success": False,
                "steps": step,
                "duration": time.time() - start_time,
                "screenshots": self.screenshot_dir,
                "error": "达到最大步数限制",
            }
        except KeyboardInterrupt:
            logger.info("\n\n[任务中断] 用户手动停止")
            return {
                "success": False,
                "steps": step,
                "duration": time.time() - start_time,
                "screenshots": self.screenshot_dir,
                "error": "用户中断",
            }
        except Exception as e:
            logger.info(f"\n\n[任务失败] 发生错误: {e}")
            return {
                "success": False,
                "steps": step,
                "duration": time.time() - start_time,
                "screenshots": self.screenshot_dir,
                "error": str(e),
            }
        finally:
            # 设置PyAutoGUI安全设置
            pyautogui.FAILSAFE = current_failsafe  # 鼠标移到左上角会触发异常停止
            pyautogui.PAUSE = current_pause  # 每个操作之间暂停0.5秒


class ComputerUse:
    """Computer Use Agent包装类，用于原子能力注册"""

    @staticmethod
    @atomicMg.atomic(
        "ComputerUse",
        inputList=[
            atomicMg.param("instruction", types="Str"),
            atomicMg.param("max_steps", types="Int", required=False),
            atomicMg.param("temperature", types="Float", required=False),
        ],
        outputList=[
            atomicMg.param("computer_use_res", types="Dict"),
        ],
    )
    def run(
        instruction: str,
        max_steps: int = 20,
        temperature: float = 0.0,
    ):
        """
        运行计算机使用代理任务

        Args:
            instruction: 用户指令
            max_steps: 最大执行步数
            temperature: 模型温度参数

        Returns:
            执行结果，包含success, steps, action_steps, duration, screenshots, error等字段
        """

        agent = ComputerUseAgent(
            max_steps=max_steps,
            temperature=temperature,
        )
        result = agent.run(instruction)

        # 返回结果，确保所有输出参数都有值
        return {
            "success": result.get("success", False),
            "steps": result.get("steps", 0),
            "duration": result.get("duration", 0.0),
            "screenshots": result.get("screenshots", []),
            "error": result.get("error", ""),
        }

    @staticmethod
    @atomicMg.atomic(
        "ComputerUse",
        inputList=[
            atomicMg.param("instruction", types="Str"),
            atomicMg.param("max_steps", types="Int", required=False),
            atomicMg.param("temperature", types="Float", required=False),
        ],
        outputList=[
            atomicMg.param("computer_use_res", types="Dict"),
        ],
    )
    def custom_action_screen(
        instruction: str,
        max_steps: int = 20,
        temperature: float = 0.0,
    ):
        """
        自定义AI操作屏幕

        Args:
            instruction: 用户指令
            max_steps: 最大执行步数
            temperature: 模型温度参数

        Returns:
            执行结果，包含success, steps, action_steps, duration, screenshots, error等字段
        """

        agent = CustomActionScreen(
            max_steps=max_steps,
            temperature=temperature,
        )
        result = agent.run(instruction)

        # 返回结果，确保所有输出参数都有值
        return {
            "success": result.get("success", False),
            "steps": result.get("steps", 0),
            "duration": result.get("duration", 0.0),
            "screenshots": result.get("screenshots", []),
            "error": result.get("error", ""),
            "thought": result.get("thought", ""),
            "data": result.get("data", ""),
        }

    @staticmethod
    @atomicMg.atomic(
        "ComputerUse",
        inputList=[
            atomicMg.param("instruction", types="Str", default="帮我从屏幕中提取数据，并返回 JSON 格式。"),
            atomicMg.param("max_steps", types="Int", required=False),
            atomicMg.param("temperature", types="Float", required=False),
        ],
        outputList=[
            atomicMg.param("computer_use_res", types="Dict"),
        ],
    )
    def extract_data(
        instruction: str,
        max_steps: int = 1,
        temperature: float = 0.0,
    ):
        """
        提取屏幕数据

        Args:
            instruction: 用户指令
            max_steps: 最大执行步数
            temperature: 模型温度参数

        Returns:
            执行结果，包含success, steps, action_steps, duration, screenshots, error等字段
        """

        agent = CustomActionScreen(
            max_steps=max_steps,
            temperature=temperature,
        )
        result = agent.run(instruction)

        # 返回结果，确保所有输出参数都有值
        return {
            "success": result.get("success", False),
            "steps": result.get("steps", 0),
            "duration": result.get("duration", 0.0),
            "screenshots": result.get("screenshots", []),
            "error": result.get("error", ""),
            "thought": result.get("thought", ""),
            "data": result.get("data", ""),
        }

    @staticmethod
    @atomicMg.atomic(
        "ComputerUse",
        inputList=[
            atomicMg.param("instruction", types="Str", default="帮我将 [数据内容] 填写到屏幕中的表单。数据内容："),
            atomicMg.param("max_steps", types="Int", required=False),
            atomicMg.param("temperature", types="Float", required=False),
        ],
        outputList=[
            atomicMg.param("computer_use_res", types="Dict"),
        ],
    )
    def fill_form(
        instruction: str,
        max_steps: int = 20,
        temperature: float = 0.0,
    ):
        """
        填写表单

        Args:
            instruction: 用户指令
            max_steps: 最大执行步数
            temperature: 模型温度参数

        Returns:
            执行结果，包含success, steps, action_steps, duration, screenshots, error等字段
        """

        agent = CustomActionScreen(
            max_steps=max_steps,
            temperature=temperature,
        )
        result = agent.run(instruction)

        # 返回结果，确保所有输出参数都有值
        return {
            "success": result.get("success", False),
            "steps": result.get("steps", 0),
            "duration": result.get("duration", 0.0),
            "screenshots": result.get("screenshots", []),
            "error": result.get("error", ""),
            "thought": result.get("thought", ""),
            "data": result.get("data", ""),
        }

    @staticmethod
    @atomicMg.atomic(
        "ComputerUse",
        inputList=[
            atomicMg.param("instruction", types="Str", default="帮我处理并关闭屏幕中的验证码。"),
            atomicMg.param("max_steps", types="Int", required=False),
            atomicMg.param("temperature", types="Float", required=False),
        ],
        outputList=[
            atomicMg.param("computer_use_res", types="Dict"),
        ],
    )
    def process_captcha(
        instruction: str,
        max_steps: int = 20,
        temperature: float = 0.0,
    ):
        """
        处理验证码

        Args:
            instruction: 用户指令
            max_steps: 最大执行步数
            temperature: 模型温度参数

        Returns:
            执行结果，包含success, steps, action_steps, duration, screenshots, error等字段
        """

        agent = CustomActionScreen(
            max_steps=max_steps,
            temperature=temperature,
        )
        result = agent.run(instruction)

        # 返回结果，确保所有输出参数都有值
        return {
            "success": result.get("success", False),
            "steps": result.get("steps", 0),
            "duration": result.get("duration", 0.0),
            "screenshots": result.get("screenshots", []),
            "error": result.get("error", ""),
            "thought": result.get("thought", ""),
            "data": result.get("data", ""),
        }

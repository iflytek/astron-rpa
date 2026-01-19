import ast
import copy
import os
import shutil
import threading
import time
from collections.abc import Callable
from typing import Optional

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.ai import LLMModelTypes
from astronverse.ai.api.llm import DEFAULT_MODEL, chat_normal, chat_streamable
from astronverse.ai.error import LLM_NO_RESPONSE_ERROR  # noqa: F401 (示例: 保留若后续使用)
from astronverse.ai.prompt.g_chat import prompt_generate_question
from astronverse.ai.utils.extract import FileExtractor
from astronverse.ai.utils.str import replace_keyword


def wait_with_timeout(check_done: Callable[[], bool], reset_timeout_on_activity: bool, wait_time: int):
    """
    等待对话框结果，支持用户活动检测和超时保护

    Args:
        check_done: 回调函数，返回 True 表示完成，False 表示继续等待
        reset_timeout_on_activity: 是否在检测到用户活动（鼠标移动）时重置超时计时器
        wait_time: 超时时间（秒）
    """
    from pynput.mouse import Controller as MouseController

    mouse_controller: Optional[MouseController] = None
    if reset_timeout_on_activity:
        mouse_controller = MouseController()

    last_pos = None
    start = time.time()
    while not check_done():
        if reset_timeout_on_activity and mouse_controller:
            pos = mouse_controller.position
            if pos != last_pos:
                last_pos = pos
                start = time.time()
        if time.time() - start > wait_time:
            break
        time.sleep(0.1)


class ChatAI:
    """Chat interaction utilities: single turn, multi-turn, and knowledge-based chat."""

    @staticmethod
    @atomicMg.atomic(
        "ChatAI",
        inputList=[
            atomicMg.param(
                "custom_model",
                dynamics=[
                    DynamicsItem(
                        key="$this.custom_model.show",
                        expression="return $this.model.value == '{}'".format(LLMModelTypes.CUSTOM_MODEL.value),
                    )
                ],
            )
        ],
        outputList=[atomicMg.param("single_chat_res", types="Str")],
    )
    def single_turn_chat(query: str, model: LLMModelTypes = LLMModelTypes.DS_CHAT, custom_model: str = "") -> str:
        """
        单轮对话方法
        Args:
            - query(str): 用户问题
        Return:
            `str`, 大模型生成的答案
        """
        if model == LLMModelTypes.CUSTOM_MODEL and custom_model:
            model = custom_model
        else:
            model = model.value
        return chat_normal(user_input=query, system_input="", model=model)

    @staticmethod
    @atomicMg.atomic(
        "ChatAI",
        inputList=[
            atomicMg.param(
                "custom_model",
                dynamics=[
                    DynamicsItem(
                        key="$this.custom_model.show",
                        expression="return $this.model.value == '{}'".format(LLMModelTypes.CUSTOM_MODEL.value),
                    )
                ],
            )
        ],
        outputList=[atomicMg.param("chat_res", types="Dict")],
    )
    def chat(
        is_save: bool,
        title: str,
        max_turns: int,
        model: LLMModelTypes = LLMModelTypes.DS_CHAT,
        custom_model: str = "",
    ) -> dict:
        """
        多轮对话方法
        Args:
            - is_save(bool): 用于判断是否需要保存最后的导出对话
            - title(title): 标题名称
            - max_turns(int): 最大问答的轮数
        Return:
            `dict`, 选择导出的记录
        """

        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        ws = atomicMg.cfg().get("WS", None)
        if ws:
            params = {
                "max_turns": str(max_turns),
                "is_save": str(int(is_save)),
                "title": title,
                "model": model.value,
            }
            ws.send_reply({"data": {"name": "multichat", "params": params, "height": 600}}, 600, callback_func)

        done.wait()
        if res_e:
            raise Exception(res_e)

        return res

    @staticmethod
    def _extract_file_content(file_path: str) -> str:
        """提取文件内容"""
        _, extension = os.path.splitext(file_path)

        if "pdf" in extension.lower():
            return FileExtractor.extract_pdf(file_path)
        elif "docx" in extension.lower():
            return FileExtractor.extract_docx(file_path)
        else:
            raise NotImplementedError(f"Not support file type：{extension}")

    @staticmethod
    def _generate_questions(file_content: str) -> list:
        """生成问题列表"""
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_generate_question),
            input_keys=[{"keyword": "text", "text": file_content[:18000]}],
        )
        content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")

        try:
            output = ast.literal_eval(s_content)
        except (ValueError, SyntaxError):
            output = [
                "这篇文本的主题是什么？",
                "文本中提到了哪些关键信息?",
                "文本提到了哪些具体的结果？",
            ]
        return output

    @staticmethod
    def _setup_file_cache(file_path: str) -> str:
        """设置文件缓存"""
        word_dir = os.path.join("cache", "chatData")
        cache_file = os.path.join(word_dir, os.path.basename(file_path))

        if not os.path.exists(word_dir):
            os.makedirs(word_dir)
        if os.path.exists(cache_file):
            os.remove(cache_file)
        shutil.copy2(file_path, cache_file)

        return cache_file

    @staticmethod
    @atomicMg.atomic(
        "ChatAI",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[atomicMg.param("knowledge_chat_res", types="Dict")],
    )
    def knowledge_chat(
        file_path: str,
        is_save: bool = False,
        max_turns: int = 20,
    ):
        """
        知识库问答
        Args:
            - file_path(str): 文件路径
            - is_save(bool): 用于判断是否需要保存最后的导出对话
            - max_turns(int): 最大问答的轮数

        Return:
            `dict`, 选择导出的记录
        """
        # 提取文件内容
        file_content = ChatAI._extract_file_content(file_path)

        # 生成问题
        output = ChatAI._generate_questions(file_content)

        # 设置文件缓存
        dest_file = ChatAI._setup_file_cache(file_path)

        # 拉起窗口
        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        ws = atomicMg.cfg().get("WS", None)
        if ws:
            params = {
                "max_turns": str(max_turns),
                "is_save": str(int(is_save)),
                "questions": "$-$".join(output),
                "file_path": file_path,
            }
            ws.send_reply(
                {"data": {"name": "multichat", "params": params, "content": file_content[:5000], "height": 700}},
                600,
                callback_func,
            )

        done.wait()

        # 文件清空
        if os.path.exists(dest_file):
            os.remove(dest_file)

        if res_e:
            raise Exception(res_e)
        return res

    @staticmethod
    def streamable_response(inputs: list, model: str = DEFAULT_MODEL):
        """Stream model responses accumulating content and reasoning lists.

        Args:
            inputs (list): chat message list [{'role': str, 'content': str}, ...]
            model(str): default model name
        Returns:
            tuple[list[str], list[str]]: (content tokens, reasoning tokens)
        """
        content: list[str] = []
        reason: list[str] = []
        for item in chat_streamable(inputs, model):
            # if item.get("content"):
            #     content.append(item.get("content"))
            # if item.get("reasoning_content"):
            #     reason.append(item.get("reasoning_content"))
            content.append(item)
        return content, reason

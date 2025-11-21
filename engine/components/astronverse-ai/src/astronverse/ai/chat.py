import ast
import copy
import json
import os
import shutil
import subprocess
import time

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.ai import LLMModelTypes
from astronverse.ai.api.llm import chat_normal, chat_streamable, DEFAULT_MODEL
from astronverse.ai.error import LLM_NO_RESPONSE_ERROR  # noqa: F401 (示例: 保留若后续使用)
from astronverse.ai.prompt.g_chat import prompt_generate_question
from astronverse.ai.utils.extract import FileExtractor
from astronverse.ai.utils.str import replace_keyword
from astronverse.baseline.logger.logger import logger
from astronverse.tools.tools import RpaTools


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

        # 拉起窗口
        exe_path = RpaTools.get_window_dir()
        args = [
            exe_path,
            f"--url=tauri://localhost/multichat.html?max_turns={str(max_turns)}&is_save={str(int(is_save))}&title={title}&model={model.value}",
            "--height=600",
        ]
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        # 数据输出
        save_dict = {}
        while True:
            if process.stdout is None:
                break
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if not output:
                continue
            save_str = output.strip()
            try:
                save_dict = json.loads(save_str)
            except Exception:  # 保留宽泛捕获用于健壮性日志
                logger.error("save_dict JSON parse error: %s", save_str)

        try:
            time.sleep(1)
            process.kill()
        except Exception:  # 宽泛捕获：仅做进程清理
            logger.debug("process already terminated")

        return save_dict

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
        exe_path = RpaTools.get_window_dir()
        url_params = (
            f"max_turns={str(max_turns)}&is_save={str(int(is_save))}"
            f"&questions={'$-$'.join(output)}&file_path={file_path}"
        )
        args = [
            exe_path,
            f"--url=tauri://localhost/multichat.html?{url_params}",
            f"--content={file_content[:5000]}",
            "--height=700",
        ]
        # args = [exe_path, f"--url=https://tauri.localhost/multichat.html?max_turns={str(max_turns)}&is_save={str(int(is_save))}&questions={'$-$'.join(output)}&file_path={file_path}", f"--content={file_content[:5000]}", "--height=700"]
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        # 数据输出
        save_dict = {}
        while True:
            if process.stdout is None:
                break
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if not output:
                continue

            save_str = output.strip()
            try:
                save_dict = json.loads(save_str)
            except Exception:  # 宽泛捕获：日志调试
                logger.debug("save_dict JSON parse error: %s", save_str)

        # 文件清空
        if os.path.exists(dest_file):
            os.remove(dest_file)

        # 结束子进程
        try:
            time.sleep(1)
            process.kill()
        except Exception:  # 进程可能已退出
            logger.debug("process already terminated (knowledge_chat)")

        return save_dict

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
            if item.get("content"):
                content.append(item.get("content"))
            if item.get("reasoning_content"):
                reason.append(item.get("reasoning_content"))
        return content, reason

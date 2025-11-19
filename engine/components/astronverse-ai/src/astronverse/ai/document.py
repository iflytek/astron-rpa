"""Document AI utilities for expansion and summarization prompts."""

# encoding: UTF-8

import copy

from astronverse.actionlib import AtomicLevel
from astronverse.actionlib.atomic import atomicMg

from astronverse.ai.chat import ChatAI
from astronverse.ai.prompt.g_document import (
    prompt_sentence_extend,
    prompt_sentence_reduce,
    prompt_theme_extend,
)
from astronverse.ai.utils.str import replace_keyword


class DocumentAI:
    """Provide document-oriented AI utilities: theme expansion, sentence expansion and reduction."""

    @staticmethod
    @atomicMg.atomic(
        "DocumentAI",
        inputList=[
            atomicMg.param("model", types="Str", level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("theme_expand_res", types="Str")],
    )
    def theme_expand(theme_text: str, model: str = "") -> str:
        # 生成提示词
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_theme_extend),
            input_keys=[{"keyword": "theme", "text": theme_text}],
        )

        # 向大模型发送请求
        if model:
            content, _ = ChatAI.streamable_response(inputs, model=model)
        else:
            content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")

        return s_content

    @staticmethod
    @atomicMg.atomic(
        "DocumentAI",
        inputList=[
            atomicMg.param("model", types="Str", level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("sentence_expand_res", types="Str")],
    )
    def sentence_expand(paragraph_text: str, model: str = ""):
        """
        段落扩写

        :param paragraph_text: 段落

        :return:
            `str`, 扩写结果
        """

        # 生成提示词
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_sentence_extend),
            input_keys=[{"keyword": "paragraph", "text": paragraph_text}],
        )

        # 向大模型发送请求
        if model:
            content, _ = ChatAI.streamable_response(inputs, model=model)
        else:
            content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")

        return s_content

    @staticmethod
    @atomicMg.atomic(
        "DocumentAI",
        inputList=[
            atomicMg.param("model", types="Str", level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("sentence_reduce_res", types="Str")],
    )
    def sentence_reduce(sentence_text: str, model: str = ""):
        """
        段落缩写

        :param sentence_text: 段落

        :return:
            `str`, 扩写结果
        """

        # 生成提示词
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_sentence_reduce),
            input_keys=[{"keyword": "paragraph", "text": sentence_text}],
        )

        # 向大模型发送请求
        if model:
            content, _ = ChatAI.streamable_response(inputs, model=model)
        else:
            content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")

        return s_content

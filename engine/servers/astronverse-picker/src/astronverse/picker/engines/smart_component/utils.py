from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Comment, NavigableString


class HTMLProcessor(ABC):
    """
    HTML处理器抽象基类
    为智能组件拾取流程提供HTML解析能力的开放接口
    """

    @abstractmethod
    def parse_html(self, html: str, **kwargs) -> Dict[str, Any]:
        """
        解析HTML内容，提取元素信息

        Args:
            html: HTML字符串内容
            **kwargs: 额外参数，可能包含坐标、上下文等信息

        Returns:
            解析结果字典，具体格式由实现类定义
        """
        pass


class DefaultHTMLProcessor(HTMLProcessor):
    """
    默认HTML处理器实现
    提供基础的HTML处理能力，可作为参考实现
    """

    def parse_html(self, html: str, **kwargs) -> Dict[str, Any]:
        """默认实现：返回基础结构"""

        # 这里可以实现基础的HTML解析逻辑
        # 或者抛出NotImplementedError提示需要具体实现
        return {"elements": [], "message": "请实现具体的HTML解析逻辑"}


# 单例模式的处理器管理器
class HTMLProcessorManager:
    """
    HTML处理器管理器
    支持注册和切换不同的HTML处理器实现
    """

    def __init__(self):
        self._processors: Dict[str, HTMLProcessor] = {}
        self._current_processor: Optional[HTMLProcessor] = None

        # 注册默认处理器
        self.register_processor("default", DefaultHTMLProcessor())
        self.set_current_processor("default")

    def register_processor(self, name: str, processor: HTMLProcessor) -> None:
        """
        注册HTML处理器

        Args:
            name: 处理器名称
            processor: 处理器实例
        """
        if not isinstance(processor, HTMLProcessor):
            raise TypeError("处理器必须继承自HTMLProcessor")

        self._processors[name] = processor

    def set_current_processor(self, name: str) -> None:
        """
        设置当前使用的处理器

        Args:
            name: 处理器名称
        """
        if name not in self._processors:
            raise ValueError(f"未找到名为 '{name}' 的处理器")

        self._current_processor = self._processors[name]

    def get_current_processor(self) -> HTMLProcessor:
        """获取当前处理器"""
        if self._current_processor is None:
            raise RuntimeError("未设置当前处理器")

        return self._current_processor

    def get_available_processors(self) -> List[str]:
        """获取所有可用处理器名称"""
        return list(self._processors.keys())

    def remove_processor(self, name: str) -> None:
        """移除处理器"""
        if name == "default":
            raise ValueError("不能移除默认处理器")

        if name in self._processors:
            del self._processors[name]

            # 如果移除的是当前处理器，切换到默认处理器
            if self._current_processor == self._processors.get(name):
                self.set_current_processor("default")


# 全局处理器管理器实例
html_processor_manager = HTMLProcessorManager()


# 外部拾取直接导入使用下面的函数
def parse_html(html: str = "", **kwargs) -> str:
    """
    使用当前HTML处理器解析HTML
    这是对外提供的主要接口，保持向后兼容
    """

    def is_visible(tag):
        """判断元素是否可见（粗略判断）"""
        if not tag or not hasattr(tag, "name"):
            return False
        # hidden 属性
        if tag.has_attr("hidden"):
            return False
        # style 属性中包含 display: none 或 visibility: hidden
        style = tag.get("style", "").lower()
        if "display: none" in style or "visibility: hidden" in style:
            return False
        return True

    def should_keep_tag(tag):
        """判断是否保留该标签（基于是否可交互或有定位价值）"""
        interactive_tags = {
            "input",
            "button",
            "a",
            "select",
            "textarea",
            "option",
            "label",
            "form",
            "div",
            "span",
            "ul",
            "li",
            "table",
            "tr",
            "td",
        }
        return tag.name in interactive_tags

    def should_keep_attr(attr_name):
        """保留对自动化有用的属性"""
        useful_attrs = {
            "id",
            "class",
            "name",
            "type",
            "value",
            "placeholder",
            "aria-label",
            "aria-labelledby",
            "role",
            "for",
            "href",
            "src",
            "alt",
            "title",
            "data-",  # 所有 data-* 属性
            "tabindex",
            "disabled",
            "readonly",
            "checked",
            "selected",
        }
        if attr_name.startswith("data-"):
            return True
        return attr_name in useful_attrs

    def remove_blank_text_nodes(soup):
        """移除纯空白的文本节点（包括换行、缩进等）"""
        for element in soup.descendants:
            if isinstance(element, NavigableString):
                if not element.strip():  # 如果去除空白后为空
                    element.extract()  # 从 DOM 中移除

    # 清理文本节点，去除“学生\n    ”中的换行和空格
    def clean_text_children(tag):
        children = list(tag.children)
        new_children = []
        found_text = False
        for child in children:
            if isinstance(child, NavigableString):
                text = str(child)
                stripped = text.strip()
                if stripped:
                    if not found_text:
                        # 保留第一个有效文本（如“学生”）
                        new_children.append(stripped)
                        found_text = True
                    # 如果已找到文本，后续空白一律丢弃
                else:
                    # 纯空白：只有在还没遇到有效文本时才可能保留（一般不保留）
                    pass
            else:
                # 保留标签（如 <i>），但你后面会删它
                new_children.append(child)
        tag.clear()
        tag.extend(new_children)

    soup = BeautifulSoup(html, "html.parser", multi_valued_attributes=False)

    # 1. 移除 <script>, <style>, <noscript>, <meta>, <link> 等非 UI 元素
    for tag in soup(["script", "style", "noscript", "meta", "link", "head", "title"]):
        tag.decompose()

    # 2. 移除注释（除非显式保留）
    if True:
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

    # 3. 遍历所有标签，清理属性 + 移除不可见/无用元素
    tags_to_remove = []
    for tag in soup.find_all():
        # 跳过文本节点等
        if not hasattr(tag, "name") or not tag.name:
            continue

        # 判断是否可见
        if not is_visible(tag):
            tags_to_remove.append(tag)
            continue

        # 判断是否值得保留（可交互或容器）
        if not should_keep_tag(tag):
            # 如果是纯文本容器且无有用属性，可移除
            if not tag.get("id") and not tag.get("class") and not tag.find():
                tags_to_remove.append(tag)
            continue

        # 保留有用属性，清理其他
        attrs_to_remove = []
        for attr in list(tag.attrs.keys()):
            if not should_keep_attr(attr):
                attrs_to_remove.append(attr)
        for attr in attrs_to_remove:
            del tag[attr]

    # 执行移除
    for tag in tags_to_remove:
        tag.decompose()

    # 对可能包含“文字 + 换行 + <i>”的标签进行清理

    for li in soup.find_all("li", id=True):  # 假设带 id 的 li 是选项
        clean_text_children(li)

    # 4. 移除空的容器（可选）
    for tag in soup.find_all():
        if tag.name in {"div", "span", "ul", "li", "form", "section"}:
            # 如果没有子标签、没有文本（或只有空白）、没有关键属性，则移除
            if not tag.find() and (not tag.text.strip()) and not tag.get("id") and not tag.get("class"):
                tag.decompose()

    # 最后一步：清理空白文本节点
    remove_blank_text_nodes(soup)

    # 返回紧凑 HTML
    return str(soup).replace("\n", "")

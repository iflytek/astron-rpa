"""谷歌浏览器JS构建器模块。"""

from astronverse.browser.js.base import BaseBuilder


class CodeChromeBuilder(BaseBuilder):
    """谷歌浏览器代码构建器。"""

    @staticmethod
    def eval_js_code(is_await: bool):
        # 下面这个空格必须保留
        if is_await:
            _js = """
            // 注释保留空格
            return await main()
            """
        else:
            _js = """
           // 注释保留空格
           return main()
           """
        return _js

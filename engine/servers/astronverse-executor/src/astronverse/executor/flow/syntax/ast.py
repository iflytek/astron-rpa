from dataclasses import dataclass
from astronverse.executor.flow.syntax import InputParam, OutputParam, Token, Node
from typing import List, Dict
from astronverse.executor.flow.syntax.token import TokenType
from astronverse.executor.utils.utils import str_to_list_if_possible


@dataclass
class CodeLine:
    """表示一行代码的数据结构"""

    tab_num: int = 0
    code: str = ""
    line: int = -1


@dataclass
class Program(Node):
    token: Token = None
    statements: List[Node] = None

    def display(self, svc, tab_num=0):
        statement_code_lines = []
        project_id = svc.ast_curr_info.get("__project_id__")
        mode = svc.ast_curr_info.get("__mode__")
        version = svc.ast_curr_info.get("__version__")
        process_id = svc.ast_curr_info.get("__process_id__")

        # body 块
        if self.statements:
            for statement in self.statements:
                statement_code_lines.extend(statement.display(svc, tab_num + 2))

        # import 块
        code_lines = [
            CodeLine(
                tab_num,
                "from .package import element, element_vision, module, component, gv, complex_param_parser, smart_component",
            ),
            CodeLine(tab_num, "from astronverse.actionlib.types import *"),
            CodeLine(tab_num, "from astronverse.workflowlib.consequence import consequence"),
        ]
        if self.token.value:
            import_python = svc.get_import_python(project_id, process_id)
            if import_python:
                for import_line in import_python:
                    code_lines.append(CodeLine(tab_num, import_line))

        for _ in range(2):
            code_lines.append(CodeLine(tab_num, ""))

        # main 块
        code_lines.append(CodeLine(tab_num, "def main(args):"))
        param_list = svc.storage.param_list(project_id=project_id, mode=mode, version=version, process_id=process_id)
        for p in param_list:
            param = svc.param.parse_param(
                {
                    "value": str_to_list_if_possible(p.get("varValue")),
                    "types": p.get("varType"),
                    "name": p.get("varName"),
                }
            )
            code_lines.append(
                CodeLine(
                    tab_num + 1,
                    '{} = args.get("{}", {})'.format(p.get("varName"), p.get("varName"), param.show_value()),
                )
            )
        code_lines.append(CodeLine(tab_num + 1, ""))
        code_lines.append(CodeLine(tab_num + 1, "try:"))
        code_lines.append(CodeLine(tab_num + 2, "pass"))

        code_lines.extend(statement_code_lines)

        code_lines.append(CodeLine(tab_num + 1, "finally:"))
        code_lines.append(CodeLine(tab_num + 2, "pass"))
        for p in param_list:
            if p.get("varDirection"):
                code_lines.append(CodeLine(tab_num + 2, 'args["{}"] = {}'.format(p.get("varName"), p.get("varName"))))
        code_lines.append(CodeLine(tab_num + 1, ""))
        return code_lines


@dataclass
class Block(Node):
    token: Token = None
    statements: List[Node] = None

    def display(self, svc, tab_num=0):
        code_lines = []
        if self.statements:
            for statement in self.statements:
                code_lines.extend(statement.display(svc, tab_num + 1))
        return code_lines


@dataclass
class Atomic(Node):
    token: Token = None
    __arguments__: Dict[str, InputParam] = None
    __returned__: List[OutputParam] = None

    def display(self, svc, tab_num=0):
        project_id = svc.ast_curr_info.get("__project_id__")
        process_id = svc.ast_curr_info.get("__process_id__")
        self.__arguments__ = svc.param.parse_input(self.token)
        self.__returned__ = svc.param.parse_output(self.token)

        # import 块
        import_list = self.token.value.get("src", "").split(".")
        if len(import_list) == 4:
            svc.add_import_python(project_id, process_id, "import {}.{}".format(import_list[0], import_list[1]))
        elif len(import_list) == 5:
            svc.add_import_python(
                project_id, process_id, "import {}.{}.{}".format(import_list[0], import_list[1], import_list[2])
            )

        # key特殊处理
        key = self.token.value.get("key", "")
        if key == "Smart.run_code":
            svc.add_smart_component(project_id, self.__arguments__.get("smart_component").value)

        # 检测是否需要重试包装（debug 模式下不生成重试包装代码）
        advance_info = self._extract_advance_info()
        if not svc.conf.debug_mode and advance_info["skip_err"] == "retry" and advance_info["retry_time"] > 0:
            # 添加重试所需的 import
            svc.add_import_python(project_id, process_id, "import time")
            svc.add_import_python(project_id, process_id, "import traceback")
            svc.add_import_python(project_id, process_id, "from astronverse.actionlib.report import report")
            svc.add_import_python(
                project_id, process_id, "from astronverse.actionlib import ReportCode, ReportType, ReportCodeStatus"
            )
            return self._display_with_retry(svc, tab_num, advance_info)
        else:
            return self._display_normal(svc, tab_num)

    def _extract_advance_info(self) -> dict:
        """从参数中提取高级参数信息"""
        info = {
            "skip_err": "exit",
            "retry_time": 0,
            "retry_interval": 0,
        }
        for key, param in self.__arguments__.items():
            if not param.need_eval:  # 只处理静态值
                if key == "__skip_err__":
                    info["skip_err"] = param.value
                elif key == "__retry_time__":
                    try:
                        info["retry_time"] = int(param.value)
                    except (ValueError, TypeError):
                        pass
                elif key == "__retry_interval__":
                    try:
                        info["retry_interval"] = float(param.value)
                    except (ValueError, TypeError):
                        pass
        return info

    def _display_normal(self, svc, tab_num) -> list:
        """原有的单行代码生成逻辑"""
        # debug 模式下禁用重试，将 __skip_err__ 改为 "exit"
        if svc.conf.debug_mode:
            arguments = []
            for k, param in self.__arguments__.items():
                if k == "__skip_err__":
                    arguments.append('__skip_err__="exit"')
                elif k in ("__retry_time__", "__retry_interval__"):
                    continue  # debug 模式下不传递重试相关参数
                else:
                    arguments.append(param.show())
        else:
            arguments = [i.show() for i in self.__arguments__.values()]

        if len(self.__returned__) > 0:
            code = ",".join([r.show() for r in self.__returned__]) + " = {}({})".format(
                self.token.value.get("src"), ", ".join(arguments)
            )
        else:
            code = "{}({})".format(self.token.value.get("src"), ", ".join(arguments))

        return [CodeLine(tab_num, code, self.token.value.get("__line__"))]

    def _display_with_retry(self, svc, tab_num, advance_info) -> list:
        """生成带重试包装的代码（包含 START/RETRY/ERROR 上报）"""
        code_lines = []
        line = self.token.value.get("__line__", 0)
        key = self.token.value.get("key", "")
        process_id = svc.ast_curr_info.get("__process_id__")
        uid = f"_{line}__"

        # 构建函数调用参数：修改 __skip_err__ 为 "exit"，移除 retry 相关参数，添加标记
        modified_arguments = []
        for k, param in self.__arguments__.items():
            if k == "__skip_err__":
                modified_arguments.append('__skip_err__="exit"')
            elif k in ("__retry_time__", "__retry_interval__"):
                continue  # 这些由外层处理，不传给 atomic_run
            else:
                modified_arguments.append(param.show())
        # 添加标记，告诉 atomic_run 跳过 START 上报
        modified_arguments.append("__in_external_retry__=True")

        # 生成函数调用代码
        src = self.token.value.get("src")
        if len(self.__returned__) > 0:
            returns = ",".join([r.show() for r in self.__returned__])
            func_call = f"{returns} = {src}({', '.join(modified_arguments)})"
        else:
            func_call = f"{src}({', '.join(modified_arguments)})"

        # === 生成代码 ===

        # 1. START 上报（在 try 之前，确保即使表达式错误也已上报）
        code_lines.append(
            CodeLine(
                tab_num,
                f'report.info(ReportCode(log_type=ReportType.Code, process_id="{process_id}", key="{key}", '
                f'line={line}, status=ReportCodeStatus.START, msg_str="流程 {{process}} 第 {line} 步 {{atomic}} 开始执行"))',
                0,
            )
        )

        # 2. 初始化重试计数器
        code_lines.append(CodeLine(tab_num, f"__retry_count{uid} = {advance_info['retry_time']}", 0))

        # 3. while True:
        code_lines.append(CodeLine(tab_num, "while True:", 0))

        # 4. try:
        code_lines.append(CodeLine(tab_num + 1, "try:", 0))

        # 5. 函数调用（atomic_run 会处理 delay_before/after、res_print）
        code_lines.append(CodeLine(tab_num + 2, func_call, line))

        # 6. break
        code_lines.append(CodeLine(tab_num + 2, "break", 0))

        # 7. except:
        code_lines.append(CodeLine(tab_num + 1, f"except Exception as __e{uid}:", 0))
        code_lines.append(CodeLine(tab_num + 2, f"__retry_count{uid} -= 1", 0))
        code_lines.append(CodeLine(tab_num + 2, f"if __retry_count{uid} < 0:", 0))

        # 8. 超过重试次数，上报 ERROR 并抛出
        code_lines.append(
            CodeLine(
                tab_num + 3,
                f'report.error(ReportCode(log_type=ReportType.Code, process_id="{process_id}", line={line}, '
                f'status=ReportCodeStatus.ERROR, msg_str="执行错误 " + str(__e{uid}), error_traceback=traceback.format_exc()))',
                0,
            )
        )
        code_lines.append(CodeLine(tab_num + 3, "raise", 0))

        # 9. 重试中，上报 WARNING
        code_lines.append(
            CodeLine(
                tab_num + 2,
                f'report.warning(ReportCode(log_type=ReportType.Code, process_id="{process_id}", line={line}, '
                f'status=ReportCodeStatus.SKIP, msg_str="执行重试 " + str(__e{uid}), error_traceback=traceback.format_exc()))',
                0,
            )
        )

        # 10. 重试间隔
        if advance_info["retry_interval"] > 0:
            code_lines.append(CodeLine(tab_num + 2, f"time.sleep({advance_info['retry_interval']})", 0))

        return code_lines


@dataclass
class AtomicExist(Node):
    """缝合原子能力和IF"""

    token: Token = None
    __arguments__: Dict[str, InputParam] = None

    consequence: Block = None
    conditions_and_blocks: List["IF"] = None
    alternative: Block = None

    def display(self, svc, tab_num=0):
        # 解析原子能力的参数和返回值
        project_id = svc.ast_curr_info.get("__project_id__")
        process_id = svc.ast_curr_info.get("__process_id__")
        self.__arguments__ = svc.param.parse_input(self.token)

        # import 块
        import_list = self.token.value.get("src").split(".")
        if len(import_list) == 4:
            svc.add_import_python(project_id, process_id, "import {}.{}".format(import_list[0], import_list[1]))
        elif len(import_list) == 5:
            svc.add_import_python(
                project_id, process_id, "import {}.{}.{}".format(import_list[0], import_list[1], import_list[2])
            )

        # 检测是否需要重试包装（debug 模式下不生成重试包装代码）
        advance_info = self._extract_advance_info()
        if not svc.conf.debug_mode and advance_info["skip_err"] == "retry" and advance_info["retry_time"] > 0:
            # 添加重试所需的 import
            svc.add_import_python(project_id, process_id, "import time")
            svc.add_import_python(project_id, process_id, "import traceback")
            svc.add_import_python(project_id, process_id, "from astronverse.actionlib.report import report")
            svc.add_import_python(
                project_id, process_id, "from astronverse.actionlib import ReportCode, ReportType, ReportCodeStatus"
            )
            return self._display_with_retry(svc, tab_num, advance_info)
        else:
            return self._display_normal(svc, tab_num)

    def _extract_advance_info(self) -> dict:
        """从参数中提取高级参数信息"""
        info = {
            "skip_err": "exit",
            "retry_time": 0,
            "retry_interval": 0,
        }
        for key, param in self.__arguments__.items():
            if not param.need_eval:
                if key == "__skip_err__":
                    info["skip_err"] = param.value
                elif key == "__retry_time__":
                    try:
                        info["retry_time"] = int(param.value)
                    except (ValueError, TypeError):
                        pass
                elif key == "__retry_interval__":
                    try:
                        info["retry_interval"] = float(param.value)
                    except (ValueError, TypeError):
                        pass
        return info

    def _display_normal(self, svc, tab_num) -> list:
        """原有的代码生成逻辑"""
        code_lines = []

        # debug 模式下禁用重试，将 __skip_err__ 改为 "exit"
        if svc.conf.debug_mode:
            arguments = []
            for k, param in self.__arguments__.items():
                if k == "__skip_err__":
                    arguments.append('__skip_err__="exit"')
                elif k in ("__retry_time__", "__retry_interval__"):
                    continue
                else:
                    arguments.append(param.show())
        else:
            arguments = [i.show() for i in self.__arguments__.values()]

        # if 原子能力块
        atomic_code = "if {}({}):".format(self.token.value.get("src"), ", ".join(arguments))
        code_lines.append(CodeLine(tab_num, atomic_code, self.token.value.get("__line__")))

        # if body块
        if self.consequence:
            temp = self.consequence.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        # elif 块
        if self.conditions_and_blocks:
            for i in self.conditions_and_blocks:
                code_lines.extend(i.display(svc, tab_num, True))

        # else 块
        if self.alternative:
            code_lines.append(CodeLine(tab_num, "else:"))
            temp = self.alternative.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines

    def _display_with_retry(self, svc, tab_num, advance_info) -> list:
        """生成带重试包装的代码"""
        code_lines = []
        line = self.token.value.get("__line__", 0)
        key = self.token.value.get("key", "")
        process_id = svc.ast_curr_info.get("__process_id__")
        uid = f"_{line}__"

        # 构建函数调用参数
        modified_arguments = []
        for k, param in self.__arguments__.items():
            if k == "__skip_err__":
                modified_arguments.append('__skip_err__="exit"')
            elif k in ("__retry_time__", "__retry_interval__"):
                continue
            else:
                modified_arguments.append(param.show())
        modified_arguments.append("__in_external_retry__=True")

        # 生成函数调用代码
        src = self.token.value.get("src")
        func_call = f"__exist_result{uid} = {src}({', '.join(modified_arguments)})"

        # === 生成代码 ===

        # 1. START 上报
        code_lines.append(
            CodeLine(
                tab_num,
                f'report.info(ReportCode(log_type=ReportType.Code, process_id="{process_id}", key="{key}", '
                f'line={line}, status=ReportCodeStatus.START, msg_str="流程 {{process}} 第 {line} 步 {{atomic}} 开始执行"))',
                0,
            )
        )

        # 2. 初始化重试计数器
        code_lines.append(CodeLine(tab_num, f"__retry_count{uid} = {advance_info['retry_time']}", 0))

        # 3. while True:
        code_lines.append(CodeLine(tab_num, "while True:", 0))

        # 4. try:
        code_lines.append(CodeLine(tab_num + 1, "try:", 0))

        # 5. 函数调用，结果保存到临时变量
        code_lines.append(CodeLine(tab_num + 2, func_call, line))

        # 6. break
        code_lines.append(CodeLine(tab_num + 2, "break", 0))

        # 7. except:
        code_lines.append(CodeLine(tab_num + 1, f"except Exception as __e{uid}:", 0))
        code_lines.append(CodeLine(tab_num + 2, f"__retry_count{uid} -= 1", 0))
        code_lines.append(CodeLine(tab_num + 2, f"if __retry_count{uid} < 0:", 0))

        # 8. ERROR 上报
        code_lines.append(
            CodeLine(
                tab_num + 3,
                f'report.error(ReportCode(log_type=ReportType.Code, process_id="{process_id}", line={line}, '
                f'status=ReportCodeStatus.ERROR, msg_str="执行错误 " + str(__e{uid}), error_traceback=traceback.format_exc()))',
                0,
            )
        )
        code_lines.append(CodeLine(tab_num + 3, "raise", 0))

        # 9. RETRY 上报
        code_lines.append(
            CodeLine(
                tab_num + 2,
                f'report.warning(ReportCode(log_type=ReportType.Code, process_id="{process_id}", line={line}, '
                f'status=ReportCodeStatus.SKIP, msg_str="执行重试 " + str(__e{uid}), error_traceback=traceback.format_exc()))',
                0,
            )
        )

        # 10. 重试间隔
        if advance_info["retry_interval"] > 0:
            code_lines.append(CodeLine(tab_num + 2, f"time.sleep({advance_info['retry_interval']})", 0))

        # 11. if 判断（使用临时变量）
        code_lines.append(CodeLine(tab_num, f"if __exist_result{uid}:", 0))

        # if body块
        if self.consequence:
            temp = self.consequence.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        # elif 块
        if self.conditions_and_blocks:
            for i in self.conditions_and_blocks:
                code_lines.extend(i.display(svc, tab_num, True))

        # else 块
        if self.alternative:
            code_lines.append(CodeLine(tab_num, "else:"))
            temp = self.alternative.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines


@dataclass
class AtomicFor(Node):
    token: Token = None

    body: Block = None
    __arguments__: Dict[str, InputParam] = None
    __returned__: List[OutputParam] = None

    def display(self, svc, tab_num=0):
        project_id = svc.ast_curr_info.get("__project_id__")
        process_id = svc.ast_curr_info.get("__process_id__")
        self.__arguments__ = svc.param.parse_input(self.token)
        self.__returned__ = svc.param.parse_output(self.token)

        # import 块
        import_list = self.token.value.get("src").split(".")
        if len(import_list) == 4:
            svc.add_import_python(project_id, process_id, "import {}.{}".format(import_list[0], import_list[1]))
        elif len(import_list) == 5:
            svc.add_import_python(
                project_id, process_id, "import {}.{}.{}".format(import_list[0], import_list[1], import_list[2])
            )

        # 检测是否需要重试包装（debug 模式下不生成重试包装代码）
        advance_info = self._extract_advance_info()
        if not svc.conf.debug_mode and advance_info["skip_err"] == "retry" and advance_info["retry_time"] > 0:
            # 添加重试所需的 import
            svc.add_import_python(project_id, process_id, "import time")
            svc.add_import_python(project_id, process_id, "import traceback")
            svc.add_import_python(project_id, process_id, "from astronverse.actionlib.report import report")
            svc.add_import_python(
                project_id, process_id, "from astronverse.actionlib import ReportCode, ReportType, ReportCodeStatus"
            )
            return self._display_with_retry(svc, tab_num, advance_info)
        else:
            return self._display_normal(svc, tab_num)

    def _extract_advance_info(self) -> dict:
        """从参数中提取高级参数信息"""
        info = {
            "skip_err": "exit",
            "retry_time": 0,
            "retry_interval": 0,
        }
        for key, param in self.__arguments__.items():
            if not param.need_eval:
                if key == "__skip_err__":
                    info["skip_err"] = param.value
                elif key == "__retry_time__":
                    try:
                        info["retry_time"] = int(param.value)
                    except (ValueError, TypeError):
                        pass
                elif key == "__retry_interval__":
                    try:
                        info["retry_interval"] = float(param.value)
                    except (ValueError, TypeError):
                        pass
        return info

    def _display_normal(self, svc, tab_num) -> list:
        """原有的代码生成逻辑"""
        code_lines = []

        # debug 模式下禁用重试，将 __skip_err__ 改为 "exit"
        if svc.conf.debug_mode:
            arguments = []
            for k, param in self.__arguments__.items():
                if k == "__skip_err__":
                    arguments.append('__skip_err__="exit"')
                elif k in ("__retry_time__", "__retry_interval__"):
                    continue
                else:
                    arguments.append(param.show())
        else:
            arguments = [i.show() for i in self.__arguments__.values()]

        # for 原子能力块
        atomic_code = "for {} in {}({}):".format(
            ", ".join([r.show() for r in self.__returned__]), self.token.value.get("src"), ", ".join(arguments)
        )
        code_lines.append(CodeLine(tab_num, atomic_code, self.token.value.get("__line__")))

        # for body块
        if self.body:
            temp = self.body.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))
        else:
            code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines

    def _display_with_retry(self, svc, tab_num, advance_info) -> list:
        """生成带重试包装的代码"""
        code_lines = []
        line = self.token.value.get("__line__", 0)
        key = self.token.value.get("key", "")
        process_id = svc.ast_curr_info.get("__process_id__")
        uid = f"_{line}__"

        # 构建函数调用参数
        modified_arguments = []
        for k, param in self.__arguments__.items():
            if k == "__skip_err__":
                modified_arguments.append('__skip_err__="exit"')
            elif k in ("__retry_time__", "__retry_interval__"):
                continue
            else:
                modified_arguments.append(param.show())
        modified_arguments.append("__in_external_retry__=True")

        # 生成函数调用代码
        src = self.token.value.get("src")
        func_call = f"__for_iterable{uid} = {src}({', '.join(modified_arguments)})"

        # === 生成代码 ===

        # 1. START 上报
        code_lines.append(
            CodeLine(
                tab_num,
                f'report.info(ReportCode(log_type=ReportType.Code, process_id="{process_id}", key="{key}", '
                f'line={line}, status=ReportCodeStatus.START, msg_str="流程 {{process}} 第 {line} 步 {{atomic}} 开始执行"))',
                0,
            )
        )

        # 2. 初始化重试计数器
        code_lines.append(CodeLine(tab_num, f"__retry_count{uid} = {advance_info['retry_time']}", 0))

        # 3. while True:
        code_lines.append(CodeLine(tab_num, "while True:", 0))

        # 4. try:
        code_lines.append(CodeLine(tab_num + 1, "try:", 0))

        # 5. 函数调用，结果保存到临时变量
        code_lines.append(CodeLine(tab_num + 2, func_call, line))

        # 6. break
        code_lines.append(CodeLine(tab_num + 2, "break", 0))

        # 7. except:
        code_lines.append(CodeLine(tab_num + 1, f"except Exception as __e{uid}:", 0))
        code_lines.append(CodeLine(tab_num + 2, f"__retry_count{uid} -= 1", 0))
        code_lines.append(CodeLine(tab_num + 2, f"if __retry_count{uid} < 0:", 0))

        # 8. ERROR 上报
        code_lines.append(
            CodeLine(
                tab_num + 3,
                f'report.error(ReportCode(log_type=ReportType.Code, process_id="{process_id}", line={line}, '
                f'status=ReportCodeStatus.ERROR, msg_str="执行错误 " + str(__e{uid}), error_traceback=traceback.format_exc()))',
                0,
            )
        )
        code_lines.append(CodeLine(tab_num + 3, "raise", 0))

        # 9. RETRY 上报
        code_lines.append(
            CodeLine(
                tab_num + 2,
                f'report.warning(ReportCode(log_type=ReportType.Code, process_id="{process_id}", line={line}, '
                f'status=ReportCodeStatus.SKIP, msg_str="执行重试 " + str(__e{uid}), error_traceback=traceback.format_exc()))',
                0,
            )
        )

        # 10. 重试间隔
        if advance_info["retry_interval"] > 0:
            code_lines.append(CodeLine(tab_num + 2, f"time.sleep({advance_info['retry_interval']})", 0))

        # 11. for 循环（使用临时变量）
        returns = ", ".join([r.show() for r in self.__returned__])
        code_lines.append(CodeLine(tab_num, f"for {returns} in __for_iterable{uid}:", 0))

        # for body块
        if self.body:
            temp = self.body.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))
        else:
            code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines


@dataclass
class Break(Node):
    token: Token = None

    def display(self, svc, tab_num=0):
        return [CodeLine(tab_num, "break", self.token.value.get("__line__"))]


@dataclass
class Continue(Node):
    token: Token = None

    def display(self, svc, tab_num=0):
        return [CodeLine(tab_num, "continue", self.token.value.get("__line__"))]


@dataclass
class Return(Node):
    token: Token = None

    def display(self, svc, tab_num=0):
        return [CodeLine(tab_num, "return", self.token.value.get("__line__"))]


@dataclass
class IF(Node):
    token: Token = None
    __arguments__: Dict[str, InputParam] = None

    consequence: Block = None
    conditions_and_blocks: List["IF"] = None
    alternative: Block = None

    def display(self, svc, tab_num=0, is_else_if: bool = False):
        code_lines = []
        self.__arguments__ = svc.param.parse_input(self.token)
        arguments = [i.show() for i in self.__arguments__.values()]

        # if块
        if is_else_if:
            code_lines.append(CodeLine(tab_num, "elif consequence({}):".format(", ".join(arguments))))
        else:
            code_lines.append(CodeLine(tab_num, "if consequence({}):".format(", ".join(arguments))))

        # if body块
        if self.consequence:
            temp = self.consequence.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        # elif 块
        if self.conditions_and_blocks:
            for i in self.conditions_and_blocks:
                code_lines.extend(i.display(svc, tab_num, True))

        # else 块
        if self.alternative:
            code_lines.append(CodeLine(tab_num, "else:"))
            temp = self.alternative.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines


@dataclass
class While(Node):
    token: Token = None
    __arguments__: Dict[str, InputParam] = None

    body: Block = None

    def display(self, svc, tab_num=0):
        code_lines = []
        self.__arguments__ = svc.param.parse_input(self.token)
        arguments = [i.show() for i in self.__arguments__.values()]

        # while块
        code_lines.append(CodeLine(tab_num, "while consequence({}):".format(", ".join(arguments))))

        # body块
        if self.body:
            temp = self.body.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))
        else:
            code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines


@dataclass
class Try(Node):
    token: Token = None
    body: Block = None
    catch_block: Block = None
    finally_block: Block = None

    def display(self, svc, tab_num=0):
        code_lines = [CodeLine(tab_num, "try:", self.token.value.get("__line__"))]

        # try块
        if self.body:
            temp = self.body.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))
        else:
            code_lines.append(CodeLine(tab_num + 1, "pass"))

        # except块
        if self.catch_block:
            code_lines.append(CodeLine(tab_num, "except Exception as e:"))
            temp = self.catch_block.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        # finally块
        if self.finally_block:
            code_lines.append(CodeLine(tab_num, "finally:"))
            temp = self.finally_block.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines


@dataclass
class For(Node):
    token: Token = None
    body: Block = None
    __arguments__: Dict[str, InputParam] = None
    __returned__: List[OutputParam] = None

    def display(self, svc, tab_num=0):
        code_lines = []
        self.__arguments__ = svc.param.parse_input(self.token)
        self.__returned__ = svc.param.parse_output(self.token)
        arguments = [i.show_value() for i in self.__arguments__.values()]

        # for块
        if self.token.type == TokenType.ForStep.value:
            start = arguments[0]
            end = arguments[1]
            step = arguments[2]
            if self.__returned__:
                iterator_var = self.__returned__[0].show()
                code_lines.append(
                    CodeLine(
                        tab_num,
                        'for {} in range(Int.__validate__("start", {}), Int.__validate__("end", {}), Int.__validate__("step", {})):'.format(
                            iterator_var, start, end, step
                        ),
                        self.token.value.get("__line__"),
                    )
                )
            else:
                code_lines.append(
                    CodeLine(
                        tab_num,
                        'for i in range(Int.__validate__("start", {}), Int.__validate__("end", {}), Int.__validate__("step", {})):'.format(
                            start, end, step
                        ),
                        self.token.value.get("__line__"),
                    )
                )
        elif self.token.type == TokenType.ForList.value:
            lists = arguments[0]
            if self.__returned__ and len(self.__returned__) >= 2:
                index_var = self.__returned__[0].show()
                item_var = self.__returned__[1].show()
                code_lines.append(
                    CodeLine(
                        tab_num,
                        'for {}, {} in enumerate(List.__validate__("lists", {})):'.format(index_var, item_var, lists),
                        self.token.value.get("__line__"),
                    )
                )
            else:
                code_lines.append(
                    CodeLine(
                        tab_num,
                        'for item in List.__validate__("lists", {}):'.format(lists),
                        self.token.value.get("__line__"),
                    )
                )
        elif self.token.type == TokenType.ForDict.value:
            dicts = arguments[0]
            if self.__returned__ and len(self.__returned__) >= 2:
                key_var = self.__returned__[0].show()
                value_var = self.__returned__[1].show()
                code_lines.append(
                    CodeLine(
                        tab_num,
                        'for {}, {} in dict(Dict.__validate__("dicts", {})).items():'.format(key_var, value_var, dicts),
                        self.token.value.get("__line__"),
                    )
                )
            else:
                code_lines.append(
                    CodeLine(
                        tab_num,
                        'for key, value in dict(Dict.__validate__("dicts", {})).items():'.format(dicts),
                        self.token.value.get("__line__"),
                    )
                )

        # body块
        if self.body:
            temp = self.body.display(svc, tab_num)
            if temp:
                code_lines.extend(temp)
            else:
                code_lines.append(CodeLine(tab_num + 1, "pass"))
        else:
            code_lines.append(CodeLine(tab_num + 1, "pass"))

        return code_lines

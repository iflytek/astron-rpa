from dataclasses import dataclass
from astronverse.executor.flow.syntax import InputParam, OutputParam, Token, Node
from typing import List, Dict
from astronverse.executor.flow.syntax.token import TokenType


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
                tab_num, "from .package import element, element_vision, module, component, gv, complex_param_parser"
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
                    "value": p.get("varValue"),
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
        arguments = [i.show() for i in self.__arguments__.values()]

        # import 块
        import_list = self.token.value.get("src", "").split(".")
        if len(import_list) == 4:
            svc.add_import_python(project_id, process_id, "import {}.{}".format(import_list[0], import_list[1]))
        elif len(import_list) == 5:
            svc.add_import_python(
                project_id, process_id, "import {}.{}.{}".format(import_list[0], import_list[1], import_list[2])
            )
        else:
            pass

        # 原子能力块
        if len(self.__returned__) > 0:
            code = ",".join([r.show() for r in self.__returned__]) + " = {}({})".format(
                self.token.value.get("src"), ", ".join(arguments)
            )
        else:
            code = "{}({})".format(self.token.value.get("src"), ", ".join(arguments))

        return [CodeLine(tab_num, code, self.token.value.get("__line__"))]


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
        code_lines = []
        project_id = svc.ast_curr_info.get("__project_id__")
        process_id = svc.ast_curr_info.get("__process_id__")
        self.__arguments__ = svc.param.parse_input(self.token)
        arguments = [i.show() for i in self.__arguments__.values()]

        # import 块
        import_list = self.token.value.get("src").split(".")
        svc.add_import_python(project_id, process_id, "import {}.{}".format(import_list[0], import_list[1]))

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


@dataclass
class AtomicFor(Node):
    token: Token = None

    body: Block = None
    __arguments__: Dict[str, InputParam] = None
    __returned__: List[OutputParam] = None

    def display(self, svc, tab_num=0):
        code_lines = []
        project_id = svc.ast_curr_info.get("__project_id__")
        process_id = svc.ast_curr_info.get("__process_id__")
        self.__arguments__ = svc.param.parse_input(self.token)
        self.__returned__ = svc.param.parse_output(self.token)
        arguments = [i.show() for i in self.__arguments__.values()]

        # import 块
        import_list = self.token.value.get("src").split(".")
        svc.add_import_python(project_id, process_id, "import {}.{}".format(import_list[0], import_list[1]))

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

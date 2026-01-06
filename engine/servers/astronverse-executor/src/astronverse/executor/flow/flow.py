import json
import os
from astronverse.executor.error import BaseException, SYNTAX_ERROR_FORMAT, PROCESS_ACCESS_ERROR_FORMAT
from astronverse.executor.flow.syntax.lexer import Lexer
from astronverse.executor.flow.syntax.parser import Parser
from astronverse.executor.flow.syntax.ast import CodeLine
from astronverse.executor.utils.utils import str_to_list_if_possible


class Flow:
    def __init__(self, svc):
        self.svc = svc

    def gen_component(self, path: str, project_id, mode: str, version: str):
        os.makedirs(path, exist_ok=True)
        component_list = self.svc.storage.component_list(project_id, mode, version)
        if component_list:
            for c in component_list:
                component_id = c.get("componentId")
                component_name = c.get("componentId")
                version = c.get("version")
                requirement = self._requirement_display(component_id, "", version)

                self.svc.add_component_info(
                    project_id,
                    component_id,
                    component_name,
                    version,
                    requirement,
                    "c{}.{}".format(component_id, "main.py"),
                )

                component_path = os.path.join(path, "c{}".format(component_id))
                self.gen_code(path=component_path, project_id=component_id, project_name="", mode="", version=version)

    def gen_code(
        self,
        path: str,
        project_id: str,
        project_name: str,
        mode: str,
        version: str,
        process_id: str = "",
        line=0,
        end_line=0,
    ):
        os.makedirs(path, exist_ok=True)

        # 1. 获取全局变量
        global_var = self._global_display(project_id, mode, version)
        requirement = self._requirement_display(project_id, mode, version)
        self.svc.add_project_info(
            project_id, mode, version, project_name, requirement, self.svc.conf.gateway_port, global_var
        )

        # 2. 生成流程相关数据
        process_list = self.svc.storage.process_list(project_id=project_id, mode=mode, version=version)
        if len(process_list) == 0:
            raise BaseException(PROCESS_ACCESS_ERROR_FORMAT, "工程数据异常 {}".format(project_id))

        process_index = 1
        module_index = 1
        main_process_name = False
        for process in process_list:
            name = process.get("name")
            category = process.get("resourceCategory")
            resource_id = str(process.get("resourceId", ""))

            # 生成python
            if category == "process":
                file_name = ""
                is_main_process = False
                if process_id:
                    if resource_id == str(process_id):
                        main_process_name = True
                        is_main_process = True
                        file_name = "main.py"
                else:
                    if name == self.svc.conf.main_process_name:
                        main_process_name = True
                        is_main_process = True
                        file_name = "main.py"
                if not file_name:
                    file_name = "process{}.py".format(process_index)
                process_index += 1
                if is_main_process:
                    res, map_res = self._flow_display(
                        project_id, mode, version, resource_id, name, start_line=line, end_line=end_line
                    )
                else:
                    res, map_res = self._flow_display(project_id, mode, version, resource_id, name)

                self.svc.add_process_info(project_id, resource_id, category, name, file_name)
                with open(os.path.join(path, file_name), "w", encoding="utf-8") as file:
                    file.write(res)
                    pass
                with open(os.path.join(path, file_name.replace(".py", ".map")), "w", encoding="utf-8") as file:
                    file.write(map_res)
                    pass
            elif category == "module":
                file_name = ""
                if process_id:
                    if resource_id == str(process_id):
                        file_name = "main.py"
                        main_process_name = True

                if not file_name:
                    file_name = "module{}.py".format(module_index)
                module_index += 1
                res = self._module_display(project_id, mode, version, resource_id, name)

                self.svc.add_process_info(project_id, resource_id, category, name, file_name)
                with open(os.path.join(path, file_name), "w", encoding="utf-8") as file:
                    file.write(res)
                    pass
            else:
                raise NotImplementedError()
        if not main_process_name:
            raise BaseException(PROCESS_ACCESS_ERROR_FORMAT, "工程数据异常 {}".format(project_id))

        # 2.1 生成智能组件
        smart_index = 1
        for smart_key, smart_info in self.svc.ast_globals_dict[project_id].smart_component_info.items():
            file_name = "smart{}.py".format(smart_index)
            smart_index += 1
            with open(os.path.join(path, file_name), "w", encoding="utf-8") as file:
                res = self._smart_component_display(
                    project_id, mode, version, smart_info.smart_id, smart_info.smart_version
                )
                if res:
                    self.svc.update_smart_component(project_id, smart_key, file_name, res.get("smartType"))
                    file.write(res.get("smartCode"))

        # 3. 生成project.py
        tpl_path = os.path.join(os.path.dirname(__file__), "tpl", "package.tpl")
        with open(tpl_path, "r", encoding="utf-8") as tpl_file:
            tpl_content = tpl_file.read()

        global_code = ""
        for k, v in global_var.items():
            global_code += f"gv[{k!r}] = {v}\n"
        tpl_content = tpl_content.replace("{{GLOBAL}}", global_code)
        package_py_content = tpl_content.replace("{{PACKAGE_PATH}}", repr(os.path.join(path, "package.json")))
        with open(os.path.join(path, "package.py"), "w", encoding="utf-8") as file:
            file.write(package_py_content)

        # 4. 生成package.json
        res = json.dumps(
            self.svc.ast_globals_dict[project_id],
            default=lambda o: o.__json__() if hasattr(o, "__json__") else None,
            ensure_ascii=False,
            indent=4,
        )
        with open(os.path.join(path, "package.json"), "w", encoding="utf-8") as file:
            file.write(res)

        # 5. 生成__init__.py（使目录成为包，支持相对导入）
        init_py_path = os.path.join(path, "__init__.py")
        if not os.path.exists(init_py_path):
            with open(init_py_path, "w", encoding="utf-8") as file:
                file.write("")

    def _requirement_display(self, project_id: str, mode: str, version: str):
        """
        当前包的依赖性
        """

        requirement = dict()
        res = self.svc.storage.pip_list(project_id=project_id, mode=mode, version=version)
        for i in res:
            pack_name = i.get("packageName")
            pack_version = i.get("packageVersion")
            pack_mirror = i.get("mirror")
            if pack_name not in requirement:
                requirement[pack_name] = {
                    "package_name": pack_name,
                    "package_version": pack_version,
                    "package_mirror": pack_mirror,
                }
        return requirement

    def _global_display(self, project_id: str, mode: str, version: str):
        """
        当前包的访问全局变量
        """
        global_list = self.svc.storage.global_list(project_id=project_id, mode=mode, version=version)
        global_var = {}
        for g in global_list:
            param = self.svc.param.parse_param(
                {
                    "value": str_to_list_if_possible(g.get("varValue")),
                    "types": g.get("varType"),
                    "name": g.get("varName"),
                }
            )
            global_var[g["varName"]] = param.show_value()
        return global_var

    def _module_display(self, project_id: str, mode: str, version: str, module_id: str, module_name) -> str:
        """
        模块生成 python模块
        """
        # 1. 获取配置参数
        param_list = self.svc.storage.param_list(
            project_id=project_id, mode=mode, version=version, process_id=module_id
        )

        # 2. 获取模块原始代码
        module_code = self.svc.storage.module_detail(
            project_id=project_id, mode=mode, version=version, module_id=module_id
        )

        # 3. 如果没有配置参数，直接返回原始代码
        if not param_list:
            return module_code

        # 4. 注入配置参数到 main(args) 函数中
        return self._inject_params_to_module(module_code, param_list)

    def _smart_component_display(
        self, project_id: str, mode: str, version: str, smart_id: str, smart_version: str
    ) -> str:
        return self.svc.storage.smart_component_detail(
            project_id=project_id, smart_id=smart_id, smart_version=smart_version, mode=mode, version=version
        )

    def _inject_params_to_module(self, module_code: str, param_list: list) -> str:
        """
        将配置参数注入到Python模块代码中
        在 def main(args): 函数开头添加输入参数初始化
        在函数结尾添加输出参数写回
        """
        import re

        # 分离输入参数和输出参数
        input_params = [p for p in param_list if p.get("varDirection") == 0]
        output_params = [p for p in param_list if p.get("varDirection") == 1]

        # 查找 def main(args): 的位置
        main_pattern = r"(def\s+main\s*\(\s*args\s*\)\s*(?:->.*?)?\s*:)"
        main_match = re.search(main_pattern, module_code)

        if not main_match:
            # 如果没有找到 main 函数，直接返回原始代码
            return module_code

        # 计算 main 函数体的缩进（通常是4个空格）
        indent = self.svc.conf.indentation

        # 生成输入参数初始化代码（复用 svc.param.parse_param）
        input_code_lines = []
        for p in input_params:
            var_name = p.get("varName")
            param = self.svc.param.parse_param(
                {
                    "value": str_to_list_if_possible(p.get("varValue")),
                    "types": p.get("varType"),
                    "name": var_name,
                }
            )
            input_code_lines.append(f'{indent}{var_name} = args.get("{var_name}", {param.show_value()})')

        # 生成输出参数初始化代码（输出参数也需要初始化）
        for p in output_params:
            var_name = p.get("varName")
            param = self.svc.param.parse_param(
                {
                    "value": str_to_list_if_possible(p.get("varValue")),
                    "types": p.get("varType"),
                    "name": var_name,
                }
            )
            input_code_lines.append(f'{indent}{var_name} = args.get("{var_name}", {param.show_value()})')

        if input_code_lines:
            input_code_lines.append(f"{indent}# --- 配置参数初始化结束 ---")
            input_code_lines.append("")

        # 在 main 函数定义后插入输入参数代码
        input_code = "\n".join(input_code_lines)
        main_end_pos = main_match.end()

        # 插入输入参数初始化代码
        new_code = module_code[:main_end_pos] + "\n" + input_code + module_code[main_end_pos:]

        # 如果有输出参数，需要在函数末尾写回
        if output_params:
            # 生成输出参数写回代码
            output_code_lines = [f"{indent}# --- 输出参数写回 ---"]
            for p in output_params:
                var_name = p.get("varName")
                output_code_lines.append(f'{indent}args["{var_name}"] = {var_name}')

            output_code = "\n" + "\n".join(output_code_lines)

            # 找到 return 语句或函数末尾，在其前面插入输出参数写回代码
            # 简单处理：在最后一个 return 前插入（如果有的话）
            return_pattern = r"(\n)([ \t]*)(return\b.*?)(\n|$)"
            return_matches = list(re.finditer(return_pattern, new_code))

            if return_matches:
                # 在最后一个 return 前插入
                last_return = return_matches[-1]
                insert_pos = last_return.start()
                new_code = new_code[:insert_pos] + output_code + new_code[insert_pos:]
            else:
                # 没有 return，在代码末尾添加
                new_code = new_code.rstrip() + "\n" + output_code + "\n"

        return new_code

    def _flow_display(
        self, project_id: str, mode: str, version: str, process_id: str, process_name: str, start_line=0, end_line=0
    ):
        """
        流程生成 主流程 子流程
        """

        # 1. 获取流程数据
        flow_list = self.svc.storage.process_detail(
            project_id=project_id, mode=mode, version=version, process_id=process_id
        )
        line = 0
        new_flow_list = []
        process_meta = []
        for k, v in enumerate(flow_list):
            line = line + 1
            if v.get("disabled"):
                continue
            if start_line > 0 and line < start_line:
                continue
            if end_line > 0 and line > end_line:  # noqa
                continue
            v.update(
                {
                    "__line__": line,
                    "__process_id__": process_id,
                }
            )
            if v.get("breakpoint"):
                # 流程扫描的断点
                self.svc.add_breakpoint(project_id, process_id, line)
            process_meta.append([line, v.get("id"), v.get("alias", v.get("title", "")), v.get("key")])
            new_flow_list.append(v)

        self.svc.add_process_meta(project_id, process_id, process_meta)

        # 2. 解析
        lexer = Lexer(flow_list=new_flow_list)
        parser = Parser(lexer=lexer)
        program = parser.parse_program()
        if len(parser.errors) > 0:
            raise BaseException(
                SYNTAX_ERROR_FORMAT.format(" ".join(parser.errors)), "语法错误: {}".format(parser.errors)
            )
        self.svc.ast_curr_info = {
            "__project_id__": project_id,
            "__mode__": mode,
            "__version__": version,
            "__process_id__": process_id,
            "__process_name__": process_name,
        }
        result = program.display(svc=self.svc, tab_num=0)
        code_lines = []
        map_list = []
        for i, code_line in enumerate(result):
            if isinstance(code_line, CodeLine):
                indent = str(self.svc.conf.indentation * code_line.tab_num)
                code_lines.append(indent + code_line.code)
                if code_line.line > 0:
                    map_list.append("{}:{}".format(i + 1, code_line.line))
        return "\n".join(code_lines), ",".join(map_list)

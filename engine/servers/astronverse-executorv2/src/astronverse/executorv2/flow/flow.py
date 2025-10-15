import json
import os

from astronverse.executorv2.error import BaseException, SYNTAX_ERROR_FORMAT, PROCESS_ACCESS_ERROR_FORMAT
from astronverse.executorv2.flow.svc import Svc
from astronverse.executorv2.flow.syntax.lexer import Lexer
from astronverse.executorv2.flow.syntax.parser import Parser
from astronverse.executorv2.flow.syntax.ast import CodeLine


class Flow:

    def __init__(self, svc: Svc):
        self.svc = svc

    def gen_package(self, project_id: str, mode: str, version: str):
        os.makedirs("./project", exist_ok=True)

        # 生成project.py
        res = self._global_display(project_id, mode, version)
        if res:
            with open("./project/project.py", "w", encoding="utf-8") as file:
                file.write(res)

        # 生成project.json
        project_json = {
            "project_info": None,
            "requirement": None,
        }

        # 生成project_info
        res = [v.to_project_json() for k, v in self.svc.ast_globals.items()]
        if res:
            project_json["project_info"] = res

        # 生成requirement_exit
        requirement = dict()
        res = self._requirement_display(project_id, mode, version)
        if res:
            for i in res:
                if i.get("packageName") not in requirement:
                    requirement[i.get("packageName")] = {
                        "package_name": i.get("packageName"),
                        "package_version": i.get("packageVersion"),
                        "package_mirror": i.get("mirror")
                    }
        if len(requirement) > 0:
            project_json["requirement"] = requirement
        with open("./project/project.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(project_json, ensure_ascii=False, indent=4))

    def gen_flow(self, project_id: str, mode: str, version: str):
        # 生成流程相关数据
        process_list = self.svc.storage.process_list(project_id=project_id, mode=mode, version=version)
        if len(process_list) == 0:
            raise BaseException(PROCESS_ACCESS_ERROR_FORMAT, "工程数据异常 {}".format(project_id))

        process_index = 1
        module_index = 1
        for process in process_list:
            name = process.get("name")
            category = process.get("resourceCategory")
            resource_id = process.get("resourceId")

            # 生成python
            if category == "process":
                if name == self.svc.conf.MAIN_FLOW_NAME:
                    file_name = "main"
                else:
                    file_name = "process{}".format(process_index)
                    process_index += 1
                res = self._flow_display(project_id, mode, version, resource_id, name)
            elif category == "module":
                res = self._module_display(project_id, mode, version, resource_id, name)
                file_name = "module{}".format(module_index)
                module_index += 1
            else:
                res = None
                file_name = ""
            if res:
                self.svc.set_process_info(resource_id, file_name, category, name)

                with open("./project/{}.py".format(file_name), "w", encoding="utf-8") as file:
                    file.write(res)

    def _requirement_display(self, project_id: str, mode: str, version: str):
        """
        当前包的依赖性
        """
        return self.svc.storage.pip_list(project_id=project_id, mode=mode, version=version)

    def _global_display(self, project_id: str, mode: str, version: str):
        """
        当前包的访问全局变量
        """
        global_list = self.svc.storage.global_list(project_id=project_id, mode=mode, version=version)
        param_code = ""
        for g in global_list:
            param = self.svc.param.parse_param({
                "value": g.get("varValue"),
                "types": g.get("varType"),
                "name": g.get("varName"),
            })
            param_code += "{} = {}\n".format(g.get("varName"), param.show_value())
        return param_code

    def _module_display(self, project_id: str, mode: str, version: str, module_id: str, module_name) -> str:
        """
        模块生成 python模块
        """
        # 1. 获取模块数据
        return self.svc.storage.module_detail(project_id=project_id, mode=mode, version=version, module_id=module_id)

    def _flow_display(self, project_id: str, mode: str, version: str, process_id: str, process_name: str) -> str:
        """
        流程生成 主流程 子流程
        """

        # 1. 获取流程数据
        flow_list = self.svc.storage.process_detail(project_id=project_id, mode=mode, version=version, process_id=process_id)

        line = 0
        new_flow_list = []
        for k, v in enumerate(flow_list):
            line = line + 1
            if v.get("disabled"):
                continue
            v.update({
                "__line__": line,
            })
            new_flow_list.append(v)

        # 2. 解析
        lexer = Lexer(flow_list=new_flow_list)
        parser = Parser(lexer=lexer)
        program = parser.parse_program()
        if len(parser.errors) > 0:
            raise BaseException(SYNTAX_ERROR_FORMAT.format(" ".join(parser.errors)), "语法错误: {}".format(parser.errors))
        self.svc.ast_curr_info = {
            "__project_id__": project_id,
            "__mode__": mode,
            "__version__": version,
            "__process_id__": process_id,
            "__process_name__": process_name
        }
        result = program.display(svc=self.svc, tab_num=0)
        code_lines = []
        for code_line in result:
            if isinstance(code_line, CodeLine):
                indent = self.svc.conf.INDENTATION * code_line.tab_num
                code_lines.append(indent + code_line.code)
            else:
                # 兼容旧格式
                code_lines.append(str(code_line))
        return "\n".join(code_lines)

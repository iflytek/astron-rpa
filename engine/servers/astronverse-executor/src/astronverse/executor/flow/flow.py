import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from astronverse.executor.error import *
from astronverse.executor.flow.syntax.ast import CodeLine
from astronverse.executor.flow.syntax.lexer import Lexer
from astronverse.executor.flow.syntax.parser import Parser
from astronverse.executor.utils.utils import str_to_list_if_possible


class Flow:
    """流程/模块代码生成：根据工程数据生成可执行的 Python 流程文件、模块文件及辅助文件。"""

    def __init__(self, svc):
        """保存 FlowSvc 引用。"""
        self.svc = svc
        self.max_workers = 5

    def gen_component(self, path: str, project_id: str, mode: str, version: str):
        """遍历组件列表，为每个组件生成独立目录、main 入口并注册组件信息。"""
        os.makedirs(path, exist_ok=True)
        component_list = self.svc.storage.component_list(project_id=project_id, mode=mode, version=version)
        if not component_list:
            return

        # 并发生成所有组件
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for c in component_list:
                future = executor.submit(self._gen_single_component, path, project_id, c)
                futures.append(future)

            # 等待所有组件生成完成
            for future in as_completed(futures):
                future.result()

    def _gen_single_component(self, path: str, project_id: str, component: dict):
        """生成单个组件（线程安全）"""
        component_id = component.get("componentId")
        component_name = component.get("componentId")
        version = component.get("version")
        requirement = self._get_requirements(project_id=component_id, mode="", version=version)

        # 生成组件代码
        main_params = []
        self.gen_code(
            path=os.path.join(path, f"c{component_id}"),
            project_id=component_id,
            mode="",
            version=version,
            main_params=main_params
        )

        # 注册meta信息
        self.svc.add_component_info(
            project_id=project_id,
            component_id=component_id,
            component_name=component_name,
            version=version,
            requirement=requirement,
            component_file_name=f"c{component_id}.main.py",
            component_params=main_params,
        )

    def gen_code(
            self,
            path: str,
            project_id: str,
            mode: str,
            version: str,
            process_id: str = "",
            line: int = 0,
            end_line: int = 0,
            main_params: list = None,
    ):
        """生成项目代码主入口：初始化项目信息、流程/模块文件、智能组件、辅助文件。"""
        if main_params is None:
            main_params = []
        os.makedirs(path, exist_ok=True)

        # 1. 初始化项目信息
        global_var = self._get_global_vars(project_id=project_id, mode=mode, version=version)
        requirement = self._get_requirements(project_id=project_id, mode=mode, version=version)
        project_info = self.svc.storage.project_info(project_id=project_id, mode=mode, version=version)
        self.svc.add_project_info(
            project_id=project_id,
            mode=mode,
            version=version,
            project_name=project_info.get("name", "机器人") if project_info else "机器人",
            requirement=requirement,
            gateway_port=self.svc.conf.gateway_port,
            global_var=global_var,
            project_icon=project_info.get("iconUrl", "") if project_info else ""
        )

        # 2. 生成流程和模块文件
        self._gen_flow_files(path=path, project_id=project_id, mode=mode, version=version, process_id=process_id, line=line, end_line=end_line, main_params=main_params)

        # 3. 生成智能组件
        self._gen_smart_components(path=path, project_id=project_id, mode=mode, version=version)

        # 4. 生成辅助文件
        package = path.rstrip("/").split("/")[-1]
        self._write_package_py(path=path, package=package, global_var=global_var)
        self._write_package_json(path=path, project_id=project_id)
        self._write_init_py(path=path)

    def _gen_flow_files(
            self,
            path: str,
            project_id: str,
            mode: str,
            version: str,
            process_id: str,
            line: int,
            end_line: int,
            main_params: list
    ) -> None:
        """生成流程/模块 py 及流程 .map；主入口为 main.py，未找到主入口则抛异常。"""
        resource_list = self.svc.storage.process_list(project_id=project_id, mode=mode, version=version)
        if not resource_list:
            raise BizException(PROCESS_ACCESS_ERROR_FORMAT.format(project_id), f"工程数据异常 {project_id}")

        # 并发处理所有任务
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            process_index = 1
            module_index = 1

            for item in resource_list:
                resource_id = str(item.get("resourceId", ""))
                name = item.get("name")
                category = item.get("resourceCategory")
                is_main = self._is_main_entry(resource_id=resource_id, name=name, process_id=process_id)

                # 确定文件名
                if category == "process":
                    file_name = "main.py" if is_main else f"process{process_index}.py"
                    if not is_main:
                        process_index += 1
                elif category == "module":
                    file_name = "main.py" if is_main else f"module{module_index}.py"
                    if not is_main:
                        module_index += 1
                else:
                    raise NotImplementedError(f"不支持的资源类型: {category}")

                # 立即提交任务
                config = {
                    "resource_id": resource_id,
                    "name": name,
                    "category": category,
                    "file_name": file_name,
                    "is_main": is_main,
                }
                future = executor.submit(
                    self._gen_single_flow_file,
                    path=path,
                    project_id=project_id,
                    mode=mode,
                    version=version,
                    config=config,
                    line=line if is_main else 0,
                    end_line=end_line if is_main else 0,
                )
                futures[future] = config

            # 等待所有任务完成，收集 main_params
            has_main_entry = False
            for future in as_completed(futures):
                config = futures[future]
                param_list = future.result()
                if config["is_main"] and not has_main_entry:
                    has_main_entry = True
                    main_params.extend(param_list)

        if not has_main_entry:
            raise BizException(PROCESS_ACCESS_ERROR_FORMAT.format(project_id), f"工程数据异常 {project_id}")

    def _gen_single_flow_file(
            self,
            path: str,
            project_id: str,
            mode: str,
            version: str,
            config: dict,
            line: int,
            end_line: int
    ):
        """生成单个流程/模块文件（线程安全），返回处理后的参数列表"""
        category = config["category"]
        resource_id = config["resource_id"]
        name = config["name"]
        file_name = config["file_name"]

        # 获取参数列表（网络请求）
        if category == "process":
            param_list = self.svc.storage.param_list(
                project_id=project_id, mode=mode, version=version, process_id=resource_id
            )
        else:  # module
            param_list = self.svc.storage.param_list(
                project_id=project_id, mode=mode, version=version, module_id=resource_id
            )

        # 解析参数
        for p in param_list:
            param = self.svc.param.parse_param({
                "value": str_to_list_if_possible(p.get("varValue")),
                "types": p.get("varType"),
                "name": p.get("varName"),
            })
            p["varValue"] = param.show_value()

        # 注册到 svc
        self.svc.add_process_info(
            project_id=project_id,
            process_id=resource_id,
            process_category=category,
            process_name=name,
            process_file_name=file_name,
            process_params=param_list
        )

        # 生成代码（网络请求）
        if category == "process":
            code, code_map = self._generate_flow_code(
                project_id=project_id, mode=mode, version=version, process_id=resource_id,
                process_name=name, start_line=line, end_line=end_line
            )
            self._write_file(path=path, file_name=file_name, content=code)
            self._write_file(path=path, file_name=file_name.replace(".py", ".map"), content=code_map)
        elif category == "module":
            code = self._get_module_code(project_id=project_id, mode=mode, version=version, module_id=resource_id)
            self._write_file(path=path, file_name=file_name, content=code)
        else:
            raise NotImplementedError(f"不支持的资源类型: {category}")

        return param_list  # 返回参数列表供收集 main_params

    def _gen_smart_components(self, path: str, project_id: str, mode: str, version: str) -> None:
        """拉取智能组件详情并写入 smart1.py、smart2.py ..."""
        smart_items = list(self.svc.ast_globals_dict[project_id].smart_component_info.items())

        # 并发生成所有智能组件
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for index, (smart_key, smart_info) in enumerate(smart_items, start=1):
                future = executor.submit(
                    self._gen_single_smart_component,
                    path=path,
                    project_id=project_id,
                    mode=mode,
                    version=version,
                    smart_key=smart_key,
                    smart_info=smart_info,
                    index=index
                )
                futures.append(future)

            # 等待所有智能组件生成完成
            for future in as_completed(futures):
                future.result()  # 如果有异常会在这里抛出

    def _gen_single_smart_component(
            self,
            path: str,
            project_id: str,
            mode: str,
            version: str,
            smart_key: str,
            smart_info,
            index: int
    ):
        """生成单个智能组件（线程安全）"""
        file_name = f"smart{index}.py"

        res = self.svc.storage.smart_component_detail(
            project_id=project_id,
            smart_id=smart_info.smart_id,
            smart_version=smart_info.smart_version,
            mode=mode,
            version=version
        )
        if res:
            self.svc.update_smart_component(
                project_id=project_id,
                smart_key=smart_key,
                component_file_name=file_name,
                smart_type=res.get("smartType")
            )
            self._write_file(path=path, file_name=file_name, content=res.get("smartCode"))

    def _generate_flow_code(
            self,
            project_id: str,
            mode: str,
            version: str,
            process_id: str,
            process_name: str,
            start_line: int = 0,
            end_line: int = 0
    ) -> tuple:
        """从流程数据生成 Python 源码与行号映射 (code, code_map)。"""
        flow_list = self.svc.storage.process_detail(
            project_id=project_id, mode=mode, version=version, process_id=process_id
        )

        filtered_list, process_meta = self._filter_flow_list(
            flow_list=flow_list, process_id=process_id, project_id=project_id,
            start_line=start_line, end_line=end_line
        )
        self.svc.add_process_meta(project_id=project_id, process_id=process_id, process_meta=process_meta)

        # 2. 词法分析和语法解析
        lexer = Lexer(flow_list=filtered_list)
        parser = Parser(lexer=lexer)
        program = parser.parse_program()

        if parser.errors:
            raise BizException(
                SYNTAX_ERROR_FORMAT.format(" ".join(parser.errors)),
                f"语法错误: {parser.errors}"
            )

        # 3. 生成代码
        self.svc.ast_curr_info = {
            "__project_id__": project_id,
            "__mode__": mode,
            "__version__": version,
            "__process_id__": process_id,
            "__process_name__": process_name,
        }
        result = program.display(svc=self.svc, tab_num=0)

        # 4. 构建代码和映射（生成行:流程行,...）
        code_lines = []
        map_list = []
        for i, code_line in enumerate(result):
            if isinstance(code_line, CodeLine):
                indent = str(self.svc.conf.indentation * code_line.tab_num)
                code_lines.append(indent + code_line.code)
                if code_line.line > 0:
                    map_list.append(f"{i + 1}:{code_line.line}")
        return "\n".join(code_lines), ",".join(map_list)

    def _filter_flow_list(
            self,
            flow_list: list,
            process_id: str,
            project_id: str,
            start_line: int,
            end_line: int
    ) -> tuple:
        """过滤流程节点：跳过 disabled、不在行范围内的，附加行号与断点，返回 (filtered_list, process_meta)。"""
        line = 0
        filtered_list = []
        process_meta = []

        for v in flow_list:
            line += 1

            # 跳过禁用的节点和不在范围内的行
            if v.get("disabled"):
                continue
            if start_line > 0 and line < start_line:
                continue
            if 0 < end_line < line:
                continue

            # 添加行号和流程ID信息
            v.update({"__line__": line, "__process_id__": process_id})

            # 记录断点
            if v.get("breakpoint"):
                self.svc.add_breakpoint(project_id=project_id, process_id=process_id, line=line)

            # 收集元数据
            process_meta.append([line, v.get("id"), v.get("alias", v.get("title", "")), v.get("key")])
            filtered_list.append(v)

        return filtered_list, process_meta

    def _get_requirements(self, project_id: str, mode: str, version: str) -> dict:
        """获取项目 pip 依赖列表。"""
        res = self.svc.storage.pip_list(project_id=project_id, mode=mode, version=version)
        return {
            i.get("packageName"): {
                "package_name": i.get("packageName"),
                "package_version": i.get("packageVersion"),
                "package_mirror": i.get("mirror"),
            }
            for i in res
        }

    def _get_global_vars(self, project_id: str, mode: str, version: str) -> dict:
        """获取并解析全局变量为可展示格式。"""
        global_list = self.svc.storage.global_list(project_id=project_id, mode=mode, version=version)
        global_var = {}
        for g in global_list:
            param = self.svc.param.parse_param({
                "value": str_to_list_if_possible(g.get("varValue")),
                "types": g.get("varType"),
                "name": g.get("varName"),
            })
            global_var[g["varName"]] = param.show_value()
        return global_var

    def _get_module_code(self, project_id: str, mode: str, version: str, module_id: str) -> str:
        """从存储取模块源码，兼容旧包名 rpahelper。"""
        module_code = self.svc.storage.module_detail(
            project_id=project_id, mode=mode, version=version, module_id=module_id
        )
        # 兼容老代码：替换旧的包名
        if "rpahelper" in module_code:
            module_code = module_code.replace("rpahelper", "astronverse.workflowlib")
        return module_code

    def _write_file(self, path: str, file_name: str, content: str) -> None:
        """将内容写入 path 下的 file_name。"""
        file_path = os.path.join(path, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _write_package_py(self, path: str, package: str, global_var: dict) -> None:
        """按模板生成并写入 package.py（含全局变量与 package 路径）。"""
        tpl_path = os.path.join(os.path.dirname(__file__), "tpl", "package.tpl")
        with open(tpl_path, encoding="utf-8") as f:
            tpl_content = f.read()

        global_code = "".join(f"gv[{k!r}] = {v}\n" for k, v in global_var.items())
        tpl_content = tpl_content.replace("{{GLOBAL}}", global_code)
        tpl_content = tpl_content.replace("{{PACKAGE_PATH}}", repr(os.path.join(path, "package.json")))
        package_py_content = tpl_content.replace("{{PACKAGE}}", package)

        self._write_file(path=path, file_name="package.py", content=package_py_content)

    def _write_package_json(self, path: str, project_id: str) -> None:
        """将工程全局数据序列化并写入 package.json。"""
        content = json.dumps(
            self.svc.ast_globals_dict[project_id],
            default=lambda o: o.__json__() if hasattr(o, "__json__") else None,
            ensure_ascii=False,
            indent=4,
        )
        self._write_file(path=path, file_name="package.json", content=content)

    def _write_init_py(self, path: str) -> None:
        """若不存在则写入空 __init__.py。"""
        init_py_path = os.path.join(path, "__init__.py")
        if not os.path.exists(init_py_path):
            self._write_file(path=path, file_name="__init__.py", content="")

    def _is_main_entry(self, resource_id: str, name: str, process_id: str) -> bool:
        """判断是否为主入口：有 process_id 时按 resource_id 匹配，否则按 main_process_name 与 name。"""
        if process_id:
            return resource_id == str(process_id)
        return name == self.svc.conf.main_process_name

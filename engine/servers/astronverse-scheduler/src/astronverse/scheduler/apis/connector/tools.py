import asyncio
import datetime
import json
import mimetypes
import os
import sys
from dataclasses import field
from enum import Enum
import re
import ast
import json
from typing import Dict

from astronverse.scheduler.apis.response import ResCode, res_msg
from astronverse.scheduler.core.schduler.venv import create_project_venv, get_project_venv
from astronverse.scheduler.core.svc import Svc, get_svc
from astronverse.scheduler.logger import logger
from astronverse.scheduler.utils.ai import InputType, get_factors
from astronverse.scheduler.utils.clipboard import Clipboard
from astronverse.scheduler.utils.pip import PipManager
from astronverse.scheduler.utils.subprocess import SubPopen
from astronverse.scheduler.utils.utils import EmitType, emit_to_front
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

router = APIRouter()


class FilePath(BaseModel):
    path: str


class WriteFile(BaseModel):
    path: str
    mode: str = "w"  # w 覆盖写 a 追加写
    content: str


class PythonCode(BaseModel):
    code: str


class VideoPaths(BaseModel):
    videoPaths: list


class BrowserPlugin(BaseModel):
    """
    定义安装插件参数
    """

    browser: str = "chrome"
    op: str = "install"


class BrowserType(Enum):
    CHROME = "CHROME"


class ContractFactors(Enum):
    contract_type: InputType = InputType.TEXT
    contract_path: str = ""
    contract_content: str = ""
    custom_factors: str = ""
    contract_validate: str = ""


class CheckBrowserPlugin(BaseModel):
    """
    定义检测安装插件参数
    """

    browsers: list[str] = field(default_factory=list)

    @classmethod
    @field_validator("browsers", mode="before")
    def set_default_browsers(cls, v):
        default_browser_list = [browser.value.lower() for browser in BrowserType]
        if not v:
            return default_browser_list
        assert all(item in default_browser_list for item in v), "Invalid browser type in plugins"
        return v


class PipPackages(BaseModel):
    """
    定义安装python包信息
    """

    project_id: str
    package: str = ""
    version: str = ""
    mirror: str = ""


class NotifyText(BaseModel):
    alert_type: str


class ClipboardParams(BaseModel):
    is_html: bool = False


@router.on_event("startup")
async def startup_event():
    async def startup():
        emit_to_front(
            EmitType.SYNC_CANCEL,
            msg={"route_port": get_svc().rpa_route_port, "step": 100},
        )

    task = asyncio.create_task(startup())


@router.post("/file/read")
def read_file(file_path: FilePath):
    """
    前端通用的读取文件的方法，包括日志文件
    """
    # 检查文件是否存在
    if not os.path.isfile(file_path.path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        mime_type, _ = mimetypes.guess_type(file_path.path)
        if mime_type is None:
            mime_type = "application/octet-stream"  # 默认 MIME 类型

        def file_iterator():
            with open(file_path.path, "rb") as file:
                while True:
                    chunk = file.read(1024)  # 每次读取 1024 字节
                    if not chunk:
                        break
                    yield chunk

        return StreamingResponse(file_iterator(), media_type=mime_type)
    except Exception as e:
        logger.exception("read_file error: {}".format(e))
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/file/write")
def read_write(write_file: WriteFile):
    """
    前端通用的覆盖写文件的方法
    """
    # 检查文件夹是否存在
    if not os.path.exists(os.path.dirname(write_file.path)):
        os.mkdir(os.path.dirname(write_file.path))

    # 写入文件
    try:
        with open(write_file.path, "w", encoding="utf-8") as f:
            f.write(write_file.content)
        return res_msg(code=ResCode.SUCCESS, msg="", data=None)
    except Exception as e:
        logger.exception("read_write error: {}".format(e))
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/video/play")
def video_play(video_paths: VideoPaths):
    try:
        video_paths = video_paths.videoPaths
        if not video_paths:
            return res_msg(code=ResCode.ERR, msg="videoPaths is empty", data={"exist": []})
        existing_files = [path for path in video_paths if os.path.exists(path)]
        return res_msg(code=ResCode.SUCCESS, msg="", data={"exist": existing_files})
    except Exception as e:
        logger.exception("An error occurred while checking video paths.")
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/window/auto_start/check")
def auto_start_check():
    """
    自启动探测
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"autostart": False})

    from astronverse.scheduler.utils.window import AutoStart

    return res_msg(msg="", data={"autostart": AutoStart.check()})


@router.post("/window/auto_start/enable")
def auto_start_enable(svc: Svc = Depends(get_svc)):
    """
    自动开启
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"tips": "操作异常，linux暂不支持自启动"})

    from astronverse.scheduler.utils.window import AutoStart

    exe_path = os.path.join(os.path.dirname(os.path.dirname(svc.config.conf_file)), "astron-rpa.exe").lower()
    AutoStart.enable(exe_path)
    return res_msg(msg="", data={"tips": "操作成功"})


@router.post("/window/auto_start/disable")
def auto_start_disable():
    """
    自启动关闭
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"tips": "操作异常，linux暂不支持自启动"})

    from astronverse.scheduler.utils.window import AutoStart

    AutoStart.disable()
    return res_msg(msg="", data={"tips": "操作成功"})


@router.get("/browser/plugins/get_support")
def browser_get_support():
    """
    获取插件支持的浏览器列表
    """
    try:
        from astronverse.browser_plugin.browser import ExtensionManager

        browsers = [browser.value.lower() for browser in ExtensionManager.get_support()]
        return res_msg(msg="获取成功", data={"browsers": browsers})
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="获取失败", data=None)


@router.post("/browser/plugins/install")
def browser_install(plugin_op: BrowserPlugin):
    """
    安装插件
    """
    try:
        from astronverse.browser_plugin import BrowserType
        from astronverse.browser_plugin.browser import ExtensionManager

        browser = BrowserType.init(plugin_op.browser)
        ex_manager = ExtensionManager(browser_type=browser)
        ex_manager.install()
        return res_msg(msg="安装成功", data=None)
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="安装失败", data=None)


@router.post("/browser/plugins/check_status")
def browser_check(options: CheckBrowserPlugin):
    """
    检测插件状态
    """
    try:
        from astronverse.browser_plugin import BrowserType
        from astronverse.browser_plugin.browser import ExtensionManager

        check_result = dict()
        for browser in options.browsers:
            ex_manager = ExtensionManager(browser_type=BrowserType.init(browser))
            check_result[browser.lower()] = ex_manager.check_status()
        return res_msg(msg="", data=check_result)
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="检测失败", data=None)


@router.post("/clipboard/get")
def clipboard_get(is_html: bool):
    """
    获取剪贴板内容
    """
    from astronverse.scheduler.utils.clipboard import Clipboard

    if is_html:
        content = Clipboard.paste_html_clip()
    else:
        content = Clipboard.paste_str_clip()
    return res_msg(code=ResCode.SUCCESS, msg="", data={"content": content})


@router.post("/pip/install")
def stream_sse(pck: PipPackages, svc: Svc = Depends(get_svc)):
    def sse_async_generator(pck: PipPackages):
        """
        实现前端包安装交互
        """
        sub_processes = list()
        try:
            project_id = pck.project_id
            package = pck.package
            version = pck.version
            mirror = pck.mirror
            exec_python = create_project_venv(svc, project_id)
            pck_v = package
            if version:
                pck_v += "=={}".format(version)

            def log(sub_proc):
                while True:
                    output = sub_proc.proc.stdout.readline()
                    if output == "" and not sub_proc.is_alive():
                        break
                    if not output.strip():
                        continue
                    yield "data: {}\n\n".format(json.dumps({"stdout": output}))
                    if "Successfully installed {}".format(package) in output:
                        return
                err_info = sub_proc.proc.stderr.read().strip()
                if err_info:
                    raise Exception(err_info)

            # 下载并缓存
            download_proc = SubPopen(cmd=PipManager.download_pip_cmd(package, version, mirror)).run(log=True)
            sub_processes.append(download_proc)
            for log_data in log(download_proc):
                yield log_data

            # 执行安装
            install_proc = SubPopen(cmd=PipManager.install_pip_cmd(package, version, exec_python=exec_python)).run(
                log=True
            )
            sub_processes.append(download_proc)
            for log_data in log(install_proc):
                yield log_data
        except Exception as e:
            logger.exception(e)
            err = str(e)
            data = json.dumps({"stderr": err})
            yield f"data: {data}\n\n"
        finally:
            for sub_pro in sub_processes:
                sub_pro.kill()
            yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(sse_async_generator(pck), media_type="text/event-stream")


@router.post("/package/version")
def package_version(pck: PipPackages, svc: Svc = Depends(get_svc)):
    package = pck.package
    project_id = pck.project_id
    exec_python = get_project_venv(svc, project_id)
    if os.path.exists(exec_python):
        version = PipManager.package_version(package, exec_python=exec_python)
    else:
        version = None
    return res_msg(msg="", data={"package": package, "version": version})


@router.post("/alert/test")
def notify_text(param: NotifyText, svc: Svc = Depends(get_svc)):
    from astronverse.scheduler.utils.notify_utils import NotifyUtils

    notifier = NotifyUtils(svc)
    if param.alert_type == "mail":
        if not notifier.email_setting["receiver"]:
            return res_msg(code=ResCode.ERR, msg="邮件必填", data=None)

        notifier.login_send()
        notifier.send_email("测试邮件")
    else:
        if not notifier.text_setting["receiver"]:
            return res_msg(code=ResCode.ERR, msg="手机号必填", data=None)

        notifier.send_text("test", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/send/tip")
def send_tip(tip_data: dict, svc: Svc = Depends(get_svc)):
    emit_to_front(EmitType.TIP, msg=tip_data)
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/send/alert")
def send_tip(tip_data: dict, svc: Svc = Depends(get_svc)):
    emit_to_front(EmitType.ALERT, msg=tip_data)
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/validate/contract")
def validate_contract(params: ContractFactors, svc: Svc = Depends(get_svc)):
    logger.info(f"params: {params}")
    get_factors(
        params.contract_type,
        params.contract_path,
        params.contract_content,
        params.custom_factors,
        params.contract_validate,
        svc.rpa_route_port,
    )
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/clipboard")
def get_clipboard_html(params: ClipboardParams, svc: Svc = Depends(get_svc)):
    content = ""
    if params.is_html:
        content = Clipboard.paste_html_clip()
    else:
        content = Clipboard.paste_str_clip()
    return res_msg(code=ResCode.SUCCESS, msg="", data={"content": content})


@router.post("/smart/code-to-meta")
def code_to_meta(pycode: PythonCode):
    python_code = pycode.code

    # 0. 提取安装包
    def extract_pip_packages(code: str) -> list:
        """
        解析代码中通过注释声明的pip安装包名
        :param code: 包含pip安装注释的代码字符串
        :return: 去重后的第三方包名列表
        """
        # 初始化集合（自动去重）
        package_set = set()
        # 按行分割代码
        lines = code.splitlines()

        for line in lines:
            # 去除行首尾空白字符（空格/制表符/换行符等）
            stripped_line = line.strip()
            # 筛选以"# pip install "开头的注释行
            if stripped_line.startswith("# pip install "):
                # 截取"# pip install "之后的部分并再次去除空白
                pkg_str = stripped_line[len("# pip install ") :].strip()
                # 按空格分割成包名列表（兼容多包一行的情况）
                pkg_list = pkg_str.split()
                # 添加到集合中去重
                package_set.update(pkg_list)

        # 集合转列表返回（保证结果有序，Python3.7+集合有序）
        return list(package_set)

    pip_packages = extract_pip_packages(python_code)

    # 1. 提取函数定义和 docstring
    try:
        func_pattern = re.compile(
            r"def\s+\w+\([\s\S]*?\)(?:\s*->\s*[\s\S]*?)?:\s*\n"  # 匹配def函数定义行（含参数）
            r"(?P<indent> {4}|\t)"  # 捕获函数体的缩进（4空格/制表符）
            r'(?P<docstring>["\']{3}[\s\S]*?["\']{3})',  # 匹配三引号包裹的docstring
            re.MULTILINE,
        )

        # 匹配第一个函数的docstring
        match = func_pattern.search(python_code)
        docstring = "title: 网页自动化"
        if match:
            # 步骤2：提取并清理docstring（去掉三引号、多余缩进/空白）
            docstring = match.group("docstring")
            # 去掉首尾的三引号
            docstring = docstring.strip('"""').strip("'''")
            # 去掉每行开头的缩进（保持原格式的同时清理多余空格）
            indent = match.group("indent")
            docstring_lines = [line.lstrip(indent).rstrip() for line in docstring.split("\n")]
            # 拼接并清理空行
            docstring = "\n".join([line for line in docstring_lines if line.strip()])
    except Exception as e:
        raise ValueError(f"解析 Python 代码失败: {e}")

    # 2. 解析 docstring
    lines = [line.strip() for line in docstring.split("\n") if line.strip()]

    # 提取 title
    try:
        title_match = re.match(r"^title[:：]\s*(.+)$", lines[0])
        title = title_match.group(1).strip()
    except Exception as e:
        raise ValueError("docstring 第一行应为 'title: ...'")

    # 提取 description（可能多行）
    desc_lines = []
    i = 1
    while i < len(lines) and not lines[i].startswith(("inputs:", "outputs:")):
        desc_lines.append(lines[i])
        i += 1
    description = " ".join(desc_lines).strip()
    if description.startswith("description:"):
        description = description[len("description:") :].strip()

    # 初始化输入输出列表
    input_list = []
    output_list = []

    # 辅助函数：解析参数行
    def parse_param_line(line: str):
        pattern = re.compile(
            r"^-\s*(?P<name>\w+)\s*"
            r"\((?P<type>[^)]+)\):\s*"
            r"「(?P<description>[^」]*)」"
            r"(?P<extra>(?:(?!id:|options:|eg:).)*)"
            r"(?:\s*[，,]?\s*id:\s*(?P<element_id>\d*))?"
            r"(?:[，, ]\s*options:\s*(?P<options>\[[^\]]*\]))?"
            r"(?:[，, ]\s*eg:\s*(?P<example>\S.*?))?"
            r"\s*$"
        )
        match = pattern.match(line.strip())
        if match:
            result = {k: v or "" for k, v in match.groupdict().items()}
            return result
        else:
            raise ValueError(f"无法解析参数行: {line}")

    def safe_str_to_type(value_str: str, target_type: str):
        """
        将字符串 value_str 转换为 target_type 指定的类型。

        支持的 target_type: 'str', 'int', 'float', 'bool', 'list', 'dict'
        """
        type_mapping = {
            "str": lambda x: x,  # 字符串本身
            "int": int,
            "float": float,
            "bool": lambda x: x.lower() in ("true", "1", "yes", "on"),
            "list": lambda x: (ast.literal_eval(x) if x.strip().startswith(("[",)) else [x]),
            "dict": ast.literal_eval,
            "tuple": ast.literal_eval,
        }

        if target_type not in type_mapping or target_type == "str":
            return value_str  # 不做转换
        try:
            if target_type in ("list", "dict", "tuple"):
                # 直接尝试解析，让 ast.literal_eval 报错（如果格式不对）
                result = ast.literal_eval(value_str)
                # 可选：严格校验结果类型（防止 "(42)" 被解析为 int 而不是 tuple）
                if target_type == "list" and not isinstance(result, list):
                    raise ValueError("Not a list")
                elif target_type == "dict" and not isinstance(result, dict):
                    raise ValueError("Not a dict")
                elif target_type == "tuple" and not isinstance(result, tuple):
                    raise ValueError("Not a tuple")
                return result
            else:
                return type_mapping[target_type](value_str)
        except Exception as e:
            return value_str

    # 解析 inputs
    if i < len(lines) and lines[i] == "inputs:":
        i += 1
        while i < len(lines) and not lines[i].startswith("outputs:"):
            if "None" in lines[i]:
                i += 1
                continue
            result = parse_param_line(lines[i])
            name, type_hint, chinese_name, extra, element_id, options, case = (
                result["name"],
                result["type"],
                result["description"],
                result["extra"],
                result["element_id"],
                result["options"],
                result["example"],
            )
            input_list.append(
                {
                    "name": name,
                    "type_hint": type_hint,
                    "title": chinese_name,
                    "extra_info": extra,
                    "element_id": element_id,
                    "options": options,
                    "case": case,
                }
            )
            i += 1

    # 解析 outputs
    if i < len(lines) and lines[i] == "outputs:":
        i += 1
        while i < len(lines):
            if "None" in lines[i]:
                i += 1
                continue
            result = parse_param_line(lines[i])
            name, type_hint, chinese_name, extra, options, case = (
                result["name"],
                result["type"],
                result["description"],
                result["extra"],
                result["options"],
                result["example"],
            )
            output_list.append({"name": name, "type_hint": type_hint, "title": chinese_name, "case": case})
            i += 1

    # 3. 构建 inputList 和 outputList 的最终结构
    type_map = {
        "bool": "Bool",
        "str": "Str",
        "int": "Int",
        "float": "Float",
        "list": "List",
        "tuple": "Tuple",
        "dict": "Dict",
    }

    def map_type_to_meta_type(type_str: str) -> str:
        base_type = type_str.split("[")[0].split(".")[-1]  # 支持泛型如 List[str]
        return type_map.get(base_type.lower(), "Str")

    def build_input_item(param: Dict) -> Dict:
        name = param["name"]
        type_hint = param["type_hint"]
        title = param["title"]
        element_id = param["element_id"]
        case = param["case"].strip('"')
        options = param["options"]
        item = {"types": "", "key": name, "title": title, "name": name, "required": True}
        # 特殊处理 formType
        if type_hint == "Browser":
            item["types"] = "Browser"
            item["formType"] = {"type": "INPUT_VARIABLE_PYTHON"}
            item["value"] = []
        elif type_hint == "WebPick":
            item["types"] = "WebPick"
            item["formType"] = {"type": "PICK", "params": {"use": "WebPick"}}
            item["noInput"] = True
            item["value"] = []
            if element_id is not None and element_id != "":
                item["default"] = element_id
                value = {"data": element_id, "type": "element", "value": case}
                item["value"].append(value)
        elif type_hint in type_map:
            item["formType"] = {"type": "INPUT_VARIABLE_PYTHON"}
            item["types"] = type_map[type_hint]
            item["value"] = []
            # 设置默认值
            if case is not None and case != "" and type_hint in ("list", "tuple", "dict", "int", "bool", "float"):
                item["value"].append({"type": "python", "value": safe_str_to_type(case, type_hint)})
            else:
                item["value"].append({"type": "other", "value": case})
        else:
            try:
                python_types, control_types = type_hint.split("-")
                item["types"] = map_type_to_meta_type(python_types)
            except Exception as e:
                raise ValueError(f"解析字段类型失败: {e}")
            if control_types == "file":
                item["formType"] = {"type": "INPUT_VARIABLE_PYTHON_FILE", "params": {"file_type": "file"}}
            elif control_types == "folder":
                item["formType"] = {"type": "INPUT_VARIABLE_PYTHON_FOLDER", "params": {"file_type": "folder"}}
            elif control_types == "textbox":
                item["formType"] = {"type": "INPUT_VARIABLE_PYTHON"}
            elif control_types == "checkbox":
                item["formType"] = {"type": "CHECKBOX"}
                item["options"] = [{"label": "是", "value": True}, {"label": "否", "value": False}]
            elif control_types == "select" or control_types == "multi_select":
                item["formType"] = {"type": "SELECT"}
                item["options"] = safe_str_to_type(options, "list")

            # 设置默认值
            item["value"] = []
            if case is not None and case != "":
                if python_types in ("list", "tuple", "dict", "int", "bool", "float"):
                    item["value"].append({"type": "python", "value": safe_str_to_type(case, type_hint)})
                else:
                    item["value"].append({"type": "other", "value": case})

            # 设置types
            item["types"] = map_type_to_meta_type(python_types)

        return item

    def build_output_item(param: Dict) -> Dict:
        name = param["name"]
        type_hint = param["type_hint"]
        title = param["title"]
        case = param["case"].strip('"')
        meta_type = type_hint
        if meta_type in type_map:
            meta_type = map_type_to_meta_type(type_hint)
        item = {
            "types": meta_type,
            "formType": {"type": "RESULT"},
            "key": name,
            "title": title,
            "value": [{"type": "var", "value": None}],
        }
        return item

    # 4. 构建最终 meta 结构
    meta = {
        "key": "Smart.run_code",
        "title": title,
        "version": "1.0.1",
        "src": "astronverse.smart.smart.Smart().run_code",
        "comment": description,
        "packages": [],
        "inputList": [],
        "outputList": [],
        "icon": "magic-command",
    }

    # 添加pip packages
    for package in pip_packages:
        meta["packages"].append(package)

    # 添加用户定义的输入参数
    for param in input_list:
        meta["inputList"].append(build_input_item(param))

    # 添加输出参数
    for param in output_list:
        meta["outputList"].append(build_output_item(param))

    return res_msg(code=ResCode.SUCCESS, msg="", data=meta)

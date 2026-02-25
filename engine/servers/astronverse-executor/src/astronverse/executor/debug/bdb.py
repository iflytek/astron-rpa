import bdb
import glob
import importlib
import inspect
import os
import sys
import threading
from collections import defaultdict
from collections.abc import Callable


class CustomBdb(bdb.Bdb):
    def __init__(self, project_dir: str, ext_dir: str, notify: Callable, err_handler: Callable):
        super().__init__()

        self.notify = notify
        self.err_handler = err_handler

        # 配置
        self.project_dir = os.path.abspath(project_dir)
        self.ext_dir = os.path.abspath(ext_dir)
        self.main_file = os.path.join(self.project_dir, "main.py")

        # 多文件行号映射
        self.file_map = {}
        self.file_line_maps = {}
        self.file_rev_maps = {}

        # 流程数据
        self.paused = False
        self.current_frame = None

        # 加载所有文件的映射
        self._load_all_maps()

        # 同步事件
        self._go_event = threading.Event()
        self._go_event.set()
        self._first_stop = True

        # 强制中断标志
        self._force_stop = False

    def _load_all_maps(self):
        """加载project目录下所有.py文件的.map文件"""
        py_files = glob.glob(os.path.join(self.project_dir, "*.py"))

        for py_file in py_files:
            if "package" not in py_file:
                self.file_map[py_file] = True

            map_file = py_file.replace(".py", ".map")
            if not os.path.exists(map_file):
                continue
            self.file_line_maps[py_file] = {}

            # 加载单个.map文件
            with open(map_file, encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    continue

                line_map = {}
                for pair in content.split(","):
                    if ":" in pair:
                        py_line, flow_line = pair.strip().split(":")
                        line_map[int(py_line)] = int(flow_line)

                if line_map:
                    self.file_line_maps[py_file] = line_map
                    # 根据行号映射生成反向映射
                    rev = defaultdict(list)
                    for py_line, flow_line in line_map.items():
                        rev[flow_line].append(py_line)
                    for lst in rev.values():
                        lst.sort()
                    self.file_rev_maps[py_file] = dict(rev)

    def _to_flow_line(self, filename: str, py_line: int) -> int:
        """把Python行号转成流程行号"""
        if filename not in self.file_line_maps:
            return py_line
        return self.file_line_maps.get(filename).get(py_line, None)

    def _to_py_lines(self, filename: str, flow_line: int) -> list[int]:
        """把流程行号转成Python行号列表"""
        return self.file_rev_maps.get(filename, {}).get(flow_line, [flow_line])

    def _to_project_path(self, path):
        """把绝对路径转成 project 相对路径，方便用户输入/显示"""
        try:
            return os.path.relpath(path, self.project_dir)
        except ValueError:
            return path

    def _to_abs_path(self, path):
        """把用户输入的 project 相对路径转成绝对路径"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.project_dir, path)

    def set_breakpoint(self, filename: str, flow_line: int, cond=None):
        """设置断点 - 支持多文件"""
        abs_path = self._to_abs_path(filename)
        py_lines = self._to_py_lines(abs_path, flow_line)
        for py_line in py_lines:
            self.set_break(abs_path, py_line, cond=cond)
            break

    def clear_breakpoint(self, filename: str, flow_line: int):
        """清除断点 - 支持多文件"""
        abs_path = self._to_abs_path(filename)
        for py_line in self._to_py_lines(abs_path, flow_line):
            self.clear_break(abs_path, py_line)
            break

    def cmd_start(self, g_v=None, l_v=None):
        """启动调试 - 在project目录下运行"""

        # 重置强制中断标志
        self._force_stop = False

        # 确保project目录在sys.path中
        if self.ext_dir not in sys.path:
            sys.path.insert(0, self.ext_dir)
        if self.project_dir not in sys.path:
            sys.path.insert(0, self.project_dir)

        if os.path.dirname(self.project_dir) not in sys.path:
            sys.path.insert(0, os.path.dirname(self.project_dir))
        # 切换到project目录
        original_cwd = os.getcwd()
        os.chdir(self.project_dir)

        try:
            package_name = os.path.basename(self.project_dir)
            try:
                importlib.import_module(package_name)
            except ImportError:
                pass

            # 准备执行环境
            # 合并 g_v 参数和必要的执行环境变量
            g_v_exec = {"__name__": "__main__", "__file__": self.main_file, "__package__": package_name, **(g_v or {})}
            l_v_exec = g_v_exec

            # 读取并编译main.py
            with open(self.main_file, encoding="utf-8") as f:
                source = f.read()

            # 在 source 后追加调用 main 函数的代码
            source = (
                source
                + "\n\n# 自动追加：执行完 main.py 后调用 main 函数\nif __name__ == '__main__':\n    _args = globals().get('_args', {})\n    main(_args)\n"
            )
            try:
                code = compile(source, self.main_file, "exec")
                # 运行代码
                self.run(code, g_v_exec, l_v_exec)
            except SyntaxError as e:
                self._handle_syntax_exception(e)
                raise e
            except Exception as e:
                self._handle_exception(e)
                raise e
        finally:
            os.chdir(original_cwd)

    def cmd_continue(self):
        """继续执行"""
        self.set_continue()
        self.paused = False
        self._go_event.set()

    def cmd_next(self):
        """单步执行"""
        self.set_next(self.current_frame)
        self.paused = False
        self._go_event.set()

    def cmd_force_stop(self):
        """强制中断执行"""
        self._force_stop = True
        self.paused = True
        self._go_event.set()
        # 立即停止调试器执行
        self.set_quit()

    def user_line(self, frame):
        """行断点触发"""
        # 检查是否被强制中断
        if self._force_stop:
            return

        filename = frame.f_code.co_filename
        py_line = frame.f_lineno

        if not filename.startswith(self.project_dir):
            return

        # 清掉框架初始 trace（仅第一次）
        if self._first_stop:
            self._first_stop = False
            self.set_continue()
            return

        # 检查是否是可视化文件，但当前行号不在映射表中
        if filename in self.file_line_maps:
            line_map = self.file_line_maps[filename]
            if py_line not in line_map:
                return

        self.current_frame = frame
        self.paused = True

        breaks = self.get_breaks(filename, py_line)
        reason = "breakpoint" if breaks else "step"

        project_filename = self._to_project_path(filename)
        flow_line = self._to_flow_line(filename, py_line)

        merged_vars = {}
        local_vars = frame.f_locals if hasattr(frame, "f_locals") else {}
        gv_obj = frame.f_globals.get("gv", {}) if hasattr(frame, "f_globals") else {}
        for k, v in {**gv_obj, **local_vars}.items():
            if not k.startswith("__"):
                try:
                    v_str = str(v)
                    v_type = type(v).__name__.capitalize()
                except Exception as e:
                    v_str = v
                    v_type = "Any"
                merged_vars[k] = {"value": v_str, "types": v_type}
        self.notify(reason, file=project_filename, line=flow_line, py_line=py_line, merged_vars=merged_vars)

        # 阻塞等待用户操作
        self._go_event.clear()
        self._go_event.wait()

    def _handle_syntax_exception(self, exc: SyntaxError):
        """处理异常 - 支持多文件"""

        filename = exc.filename
        py_line = exc.lineno or 0

        project_filename = self._to_project_path(filename)
        flow_line = self._to_flow_line(filename, py_line)

        self.notify(
            "syntax_exception",
            file=project_filename,
            line=flow_line,
            py_line=py_line,
            exc=exc,
            exc_msg=self.err_handler(exc),
        )

    def _handle_exception(self, exc: Exception):
        """处理异常 - 支持多文件"""
        matched = []
        tb = exc.__traceback__

        while tb:
            if tb.tb_frame.f_code.co_filename in self.file_map:
                matched.append(tb)
            tb = tb.tb_next

        if not matched:
            self.notify("exception", file="", line=0, py_line=0, exc=exc, exc_msg=self.err_handler(exc))
        else:
            tb = matched[-1]
            filename = tb.tb_frame.f_code.co_filename
            py_line = tb.tb_lineno

            self.notify(
                "exception",
                file=self._to_project_path(filename),
                line=self._to_flow_line(filename, py_line),
                py_line=py_line,
                exc=exc,
                exc_msg=self.err_handler(exc),
            )

    def find_nearest_caller(self):
        """
        在调用栈中向上查找，返回最近（最内层）匹配预定义文件列表的调用位置
        """
        frame = inspect.currentframe().f_back

        while frame:
            filename = frame.f_code.co_filename
            if filename in self.file_map:
                return self._to_project_path(filename), self._to_flow_line(filename, frame.f_lineno)
            frame = frame.f_back
        return "", 0

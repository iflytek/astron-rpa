import bdb
import json
import os
import sys
import glob
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def _notify(typ, **kw):
    """打印演示"""
    print(json.dumps({'type': typ, **kw}, ensure_ascii=False))


class Debug(bdb.Bdb):

    def __init__(self, project_dir: str):
        super().__init__()

        # 配置
        self.project_dir = os.path.abspath(project_dir)
        self.main_file = os.path.join(self.project_dir, "main.py")

        # 多文件行号映射
        self.file_line_maps = {}
        self.file_rev_maps = {}

        # 流程数据
        self.paused = False
        self.current_frame = None

        # 加载所有文件的映射
        self._load_all_maps()

    def _load_all_maps(self):
        """加载project目录下所有.py文件的.map文件"""
        py_files = glob.glob(os.path.join(self.project_dir, "*.py"))

        for py_file in py_files:
            filename = os.path.basename(py_file)
            map_file = py_file.replace('.py', '.map')

            if not os.path.exists(map_file):
                continue

            # 加载单个.map文件
            with open(map_file, encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    continue

                line_map = {}
                for pair in content.split(','):
                    if ':' in pair:
                        py_line, flow_line = pair.strip().split(':')
                        line_map[int(py_line)] = int(flow_line)

                if line_map:
                    self.file_line_maps[filename] = line_map

                    # 根据行号映射生成反向映射
                    rev = defaultdict(list)
                    for py_line, flow_line in line_map.items():
                        rev[flow_line].append(py_line)
                    for lst in rev.values():
                        lst.sort()
                    self.file_rev_maps[filename] = dict(rev)

    def _to_flow_line(self, filename: str, py_line: int) -> int:
        """把Python行号转成流程行号"""
        return self.file_line_maps.get(filename, {}).get(py_line, py_line)

    def _to_py_lines(self, filename: str, flow_line: int) -> List[int]:
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
        py_lines = self._to_py_lines(filename, flow_line)
        for py_line in py_lines:
            self.set_break(abs_path, py_line, cond=cond)
            break

    def clear_breakpoint(self, filename: str, flow_line: int):
        """清除断点 - 支持多文件"""
        abs_path = self._to_abs_path(filename)
        for py_line in self._to_py_lines(filename, flow_line):
            self.clear_break(abs_path, py_line)
            break

    def cmd_start(self, g_v=None, l_v=None):
        """启动调试 - 在project目录下运行"""
        if g_v is None:
            g_v = {'__name__': '__main__', '__file__': self.main_file}
        if l_v is None:
            l_v = g_v

        # 确保project目录在sys.path中
        if self.project_dir not in sys.path:
            sys.path.insert(0, self.project_dir)

        # 切换到project目录
        original_cwd = os.getcwd()
        os.chdir(self.project_dir)

        try:
            # 读取并编译main.py
            with open(self.main_file, encoding='utf-8') as f:
                source = f.read()
            code = compile(source, self.main_file, 'exec')

            # 运行代码
            self.run(code, g_v, l_v)
        except Exception as e:
            self._handle_exception(e)
        finally:
            os.chdir(original_cwd)

    def cmd_continue(self):
        """继续执行"""
        self.set_continue()
        self.paused = False

    def cmd_next(self):
        """单步执行"""
        self.set_next(self.current_frame)
        self.paused = False

    def user_line(self, frame):
        """行断点触发"""
        filename = frame.f_code.co_filename
        py_line = frame.f_lineno

        # 只检查project目录下的文件
        if not filename.startswith(self.project_dir):
            return
            
        breaks = self.get_breaks(filename, py_line)
        if not breaks:
            return
            
        self.current_frame = frame
        self.paused = True

        project_filename = self._to_project_path(filename)
        flow_line = self._to_flow_line(os.path.basename(filename), py_line)

        _notify('breakpoint', file=project_filename, line=flow_line, py_line=py_line, code=frame.f_code.co_name)

    def _handle_exception(self, exc: Exception):
        """处理异常 - 支持多文件"""
        tb = exc.__traceback__

        while tb.tb_next:
            tb = tb.tb_next

        filename = tb.tb_frame.f_code.co_filename
        py_line = tb.tb_lineno

        project_filename = self._to_project_path(filename)
        flow_line = self._to_flow_line(filename, py_line)

        _notify('exception', file=project_filename, line=flow_line, py_line=py_line, msg=str(exc), exc_type=type(exc).__name__)

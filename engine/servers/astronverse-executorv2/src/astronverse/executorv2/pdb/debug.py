import bdb
import json
import os
from collections import defaultdict


def _notify(typ, **kw):
    """简单 mock：把事件发回 WebSocket，或打印演示"""
    print(json.dumps({'type': typ, **kw}, ensure_ascii=False))


class Debug(bdb.Bdb):
    """
    只保留：设断点、取消断点、运行、下一步、继续、停止。
    同时支持普通 Python 与 AST 流程代码（.map 文件）。
    """

    def __init__(self, filename: str):
        super().__init__()
        self.filename = os.path.abspath(filename)
        self.map_file = self.filename.replace('.py', '.map')

        # 正向：Python 行号 -> 流程行号
        self.line_map = self._load_line_map()
        # 反向：流程行号 -> [Python 行号, ...] 升序
        self.rev_map = self._build_reverse_map()

        self.paused = False
        self.current_frame = None

    def _load_line_map(self):
        """加载 .map 文件：{py_line: flow_line}"""
        if not os.path.exists(self.map_file):
            return {}
        with open(self.map_file, encoding='utf-8') as f:
            return {int(k): int(v) for k, v in json.load(f).items()}

    def _build_reverse_map(self):
        """根据 line_map 生成反向映射：{flow_line: [py_line, ...]}"""
        rev = defaultdict(list)
        for py_line, flow_line in self.line_map.items():
            rev[flow_line].append(py_line)
        # 每条列表按 Python 行号升序
        for lst in rev.values():
            lst.sort()
        return dict(rev)

    def _to_flow_line(self, py_line: int) -> int:
        """把 Python 行号转成流程行号（单值）"""
        return self.line_map.get(py_line, py_line)

    def _to_py_lines(self, flow_line: int):
        """把流程行号转成 Python 行号列表"""
        if not self.line_map:
            return [flow_line]
        return self.rev_map.get(flow_line, [flow_line])

    def set_breakpoint(self, flow_line: int, cond=None):
        """在流程行号上设断点，内部会映射到所有对应 Python 行"""
        for py_line in self._to_py_lines(flow_line):
            self.set_break(self.filename, py_line, cond=cond)

    def clear_breakpoint(self, flow_line: int):
        """清除流程行号对应的断点"""
        for py_line in self._to_py_lines(flow_line):
            self.clear_break(self.filename, py_line)

    def run_path(self, g_v=None, l_v=None):
        if g_v is None:
            g_v = {'__name__': '__main__', '__file__': self.filename}
        if l_v is None:
            l_v = g_v
        try:
            with open(self.filename, encoding='utf-8') as f:
                source = f.read()
            code = compile(source, self.filename, 'exec')
            self.run(code, g_v, l_v)
        except Exception as e:
            self._handle_exception(e)

    def cmd_continue(self):
        self.set_continue()
        self.paused = False

    def cmd_next(self):
        self.set_next(self.current_frame)
        self.paused = False

    def user_line(self, frame):
        self.current_frame = frame
        self.paused = True
        flow_line = self._to_flow_line(frame.f_lineno)
        _notify('pause', file=self.filename, line=flow_line)

    def _handle_exception(self, exc: Exception):
        tb = exc.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        py_line = tb.tb_lineno
        flow_line = self._to_flow_line(py_line)
        _notify('exception', file=self.filename, line=flow_line, msg=str(exc))

    def is_flow(self):
        return bool(self.line_map)

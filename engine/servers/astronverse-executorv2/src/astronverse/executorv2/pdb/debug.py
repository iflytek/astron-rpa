import bdb
import json
import os
from collections import defaultdict


def _notify(typ, **kw):
    """简单 mock：把事件发回 WebSocket，或打印演示"""
    print(json.dumps({'type': typ, **kw}, ensure_ascii=False))


class Debug(bdb.Bdb):

    def __init__(self, filename: str):
        super().__init__()
        self.filename = os.path.abspath(filename)
        self.map_file = self.filename.replace('.py', '.map')

        self.line_map = self._load_line_map()
        self.rev_map = self._build_reverse_map()

        self.paused = False
        self.current_frame = None

    def _load_line_map(self):
        """加载 .map 文件"""
        if not os.path.exists(self.map_file):
            return {}
        with open(self.map_file, encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            line_map = {}
            for pair in content.split(','):
                if ':' in pair:
                    py_line, flow_line = pair.strip().split(':')
                    line_map[int(py_line)] = int(flow_line)
            return line_map

    def _build_reverse_map(self):
        """根据 .map 生成反向映射"""
        rev = defaultdict(list)
        for py_line, flow_line in self.line_map.items():
            rev[flow_line].append(py_line)
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
        """设置断点"""
        for py_line in self._to_py_lines(flow_line):
            self.set_break(self.filename, py_line, cond=cond)
            break

    def clear_breakpoint(self, flow_line: int):
        """清除断点"""
        for py_line in self._to_py_lines(flow_line):
            self.clear_break(self.filename, py_line)
            break

    def start(self, g_v=None, l_v=None):
        if g_v is None:
            g_v = {'__name__': '__main__', '__file__': self.filename}
        if l_v is None:
            l_v = g_v
        try:
            with open(self.filename, encoding='utf-8') as f:
                source = f.read()
            code = compile(source, self.filename, 'exec')
            self.run(code, g_v, l_v)
            l_v['main']() #noqa
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

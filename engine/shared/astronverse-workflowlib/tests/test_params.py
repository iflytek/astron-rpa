#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from astronverse.workflowlib.params import ComplexParamParser


def test_complex_param_parser():
    """测试复杂参数解析器"""
    source_dict = {
        "python_expr": {"rpa": "special", "value": [{"type": "python", "data": "len(user_list)"}]},
        "flow_var": {"rpa": "special", "value": [{"type": "var", "data": "current_user"}]},
        "global_var": {"rpa": "special", "value": [{"type": "g_var", "data": "api_base_url"}]},
        "mixed": {"rpa": "special", "value": [
            {"type": "var", "data": "prefix"},
            {"type": "str", "data": "_"},
            {"type": "g_var", "data": "suffix"}
        ]},

        "nested": {
            "deep": [
                {"rpa": "special", "value": [{"type": "var", "data": "deep_var"}]},
                {"rpa": "special", "value": [{"type": "other", "data": "deep_var"}]},
                {"rpa": "special", "value": [{"type": "str", "data": "deep_var"}]},
            ]
        }
    }

    # 模拟运行时变量
    user_list = ["a", "b"]
    current_user = "A()"
    prefix = "order"
    deep_var = "nested_value"
    gv = {
        "api_base_url": "https://api.example.com",
        "suffix": "_end"
    }

    _processor = ComplexParamParser()
    template = _processor.parse_params(source_dict)

    # 提供完整的变量上下文
    ctx = {
        'prefix': "order2",  # 覆盖原来的值
    }
    result = _processor.evaluate_params(template, ctx)
    print("测试结果:")
    pprint(result)


if __name__ == "__main__":
    test_complex_param_parser()

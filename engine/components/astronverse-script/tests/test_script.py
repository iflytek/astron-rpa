import unittest

from astronverse.script.script import Script


class TestScriptModule(unittest.TestCase):
    """测试Script.module原子能力"""

    def setUp(self):
        """测试前的准备工作"""

        # 创建真实的环境对象，模拟to_dict方法
        class MockEnv:
            def __init__(self, params):
                self.params = params

            def to_dict(self):
                return self.params

        self.env = MockEnv({"param1": "value1", "param2": "value2"})

    def test_module_with_main_function(self):
        """测试包含main函数的脚本执行"""
        # 准备测试数据
        test_content = """
def main(param1, param2):
    return {"result": f"{param1}_{param2}", "status": "success"}
"""

        # 调用原子能力，使用a=a,b=b的方式
        result = Script.module(content=test_content, __env__=self.env)

        # 验证结果
        expected = {"result": "value1_value2", "status": "success"}
        self.assertEqual(result, expected)

    def test_module_without_main_function(self):
        """测试不包含main函数的脚本执行"""
        # 准备测试数据
        test_content = """
# 没有main函数的脚本
x = 10
y = 20
"""

        # 调用原子能力，使用a=a,b=b的方式
        result = Script.module(content=test_content, __env__=self.env)

        # 验证结果（没有main函数时应该返回None）
        self.assertIsNone(result)

    def test_module_with_complex_script(self):
        """测试复杂脚本的执行"""
        # 准备测试数据
        test_content = """
import json

def main(param1, param2):
    # 模拟复杂的业务逻辑
    data = {
        "input": {"param1": param1, "param2": param2},
        "processed": True,
        "timestamp": "2024-01-01"
    }
    
    # 使用logger记录日志
    logger.info("处理完成")
    
    return data
"""

        # 调用原子能力，使用a=a,b=b的方式
        result = Script.module(content=test_content, __env__=self.env)

        # 验证结果
        expected = {
            "input": {"param1": "value1", "param2": "value2"},
            "processed": True,
            "timestamp": "2024-01-01",
        }
        self.assertEqual(result, expected)

    def test_module_with_error_handling(self):
        """测试脚本执行错误处理"""
        # 准备测试数据（包含错误的脚本）
        test_content = """
def main(param1, param2):
    # 故意制造一个错误
    undefined_variable + 1
    return "should not reach here"
"""

        # 验证异常被正确抛出
        with self.assertRaises(NameError):
            Script.module(content=test_content, __env__=self.env)

    def test_module_with_empty_content(self):
        """测试空内容的情况"""
        # 调用原子能力，使用a=a,b=b的方式
        result = Script.module(content="", __env__=self.env)

        # 验证结果
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

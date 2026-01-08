from unittest import TestCase
from unittest.mock import patch, MagicMock
import os
from astronverse.cua.computer_use import ComputerUse


class TestComputerUse(TestCase):
    def setUp(self):
        # 保存原始环境变量
        self.original_api_key = os.environ.get('ARK_API_KEY')
        self.original_openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        # 设置测试用API密钥
        os.environ['ARK_API_KEY'] = 'test_api_key'
    
    def tearDown(self):
        # 恢复原始环境变量
        if self.original_api_key is not None:
            os.environ['ARK_API_KEY'] = self.original_api_key
        elif 'ARK_API_KEY' in os.environ:
            del os.environ['ARK_API_KEY']
        
        if self.original_openai_api_key is not None:
            os.environ['OPENAI_API_KEY'] = self.original_openai_api_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    @patch('astronverse.cua.computer_use.ComputerUseAgent')
    def test_run_with_default_params(self, mock_agent_class):
        # 配置mock
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            'success': True,
            'steps': 5,
            'action_steps': 3,
            'duration': 10.5,
            'screenshots': ['screenshot1.png', 'screenshot2.png'],
            'error': ''
        }
        mock_agent_class.return_value = mock_agent
        
        # 执行测试
        instruction = '测试指令'
        result = ComputerUse.run(instruction)
        
        # 验证结果
        self.assertTrue(result['success'])
        self.assertEqual(result['steps'], 5)
        self.assertEqual(result['action_steps'], 3)
        self.assertEqual(result['duration'], 10.5)
        self.assertEqual(result['screenshots'], ['screenshot1.png', 'screenshot2.png'])
        self.assertEqual(result['error'], '')
        
        # 验证ComputerUseAgent被正确初始化
        mock_agent_class.assert_called_once_with(
            api_key=None,
            model='doubao-1-5-ui-tars-250428',
            language='Chinese',
            max_steps=20,
            screenshot_dir=None,
            temperature=0.0,
            provider='doubao'
        )
        
        # 验证agent.run被调用
        mock_agent.run.assert_called_once_with(instruction)
    
    @patch('astronverse.cua.computer_use.ComputerUseAgent')
    def test_run_with_custom_params(self, mock_agent_class):
        # 配置mock
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            'success': False,
            'steps': 2,
            'action_steps': 1,
            'duration': 5.2,
            'screenshots': ['screenshot1.png'],
            'error': '测试错误'
        }
        mock_agent_class.return_value = mock_agent
        
        # 执行测试
        instruction = '自定义参数测试'
        api_key = 'a3b7c93e-e998-4604-9949-dd439db686c5'
        model = 'custom-model'
        language = 'English'
        max_steps = 10
        screenshot_dir = '/tmp/screenshots'
        temperature = 0.5
        provider = 'openai'
        
        result = ComputerUse.run(
            instruction=instruction,
            api_key=api_key,
            model=model,
            language=language,
            max_steps=max_steps,
            screenshot_dir=screenshot_dir,
            temperature=temperature,
            provider=provider
        )
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertEqual(result['steps'], 2)
        self.assertEqual(result['action_steps'], 1)
        self.assertEqual(result['duration'], 5.2)
        self.assertEqual(result['screenshots'], ['screenshot1.png'])
        self.assertEqual(result['error'], '测试错误')
        
        # 验证ComputerUseAgent被正确初始化
        mock_agent_class.assert_called_once_with(
            api_key=api_key,
            model=model,
            language=language,
            max_steps=max_steps,
            screenshot_dir=screenshot_dir,
            temperature=temperature,
            provider=provider
        )
        
        # 验证agent.run被调用
        mock_agent.run.assert_called_once_with(instruction)
    
    @patch('astronverse.cua.computer_use.ComputerUseAgent')
    def test_run_with_rpa_context(self, mock_agent_class):
        # 配置mock
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            'success': True,
            'steps': 3,
            'action_steps': 2,
            'duration': 7.8,
            'screenshots': ['screenshot1.png', 'screenshot2.png', 'screenshot3.png'],
            'error': ''
        }
        mock_agent_class.return_value = mock_agent
        
        # 执行测试 - 传递RPA上下文参数
        instruction = 'RPA上下文测试'
        result = ComputerUse.run(instruction=instruction)
        
        # 验证结果
        self.assertTrue(result['success'])
        
        # 验证agent.run被调用
        mock_agent.run.assert_called_once_with(instruction)
    
    def test_run_without_api_key(self):
        # 移除环境变量
        if 'ARK_API_KEY' in os.environ:
            del os.environ['ARK_API_KEY']
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # 执行测试 - 应该引发ValueError
        with self.assertRaises(ValueError) as context:
            ComputerUse.run(instruction='测试指令', api_key=None)
        
        # 验证错误消息
        self.assertIn('API Key未提供', str(context.exception))

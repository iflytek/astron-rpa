# 🐍 Python代码质量检测手册

## 📖 概述

本手册详细说明项目中使用的Python代码质量检测工具链，包括工具介绍、使用方法、质量标准和最佳实践。基于现代Python开发标准，提供完整的代码质量保障体系。

## 🛠️ 工具链架构

### 格式化工具链
```
源代码 → isort → black → 标准化代码
```

### 质量检测链
```
代码 → flake8 → mypy → pylint → 质量报告
```

## 🎯 质量标准

| 检测维度 | 标准要求 | 检测工具 | 阈值设置 |
|---------|---------|----------|----------|
| **代码格式** | 符合Black标准 | black | 88字符行长度 |
| **Import管理** | 自动排序整理 | isort | black兼容模式 |
| **语法规范** | PEP8代码规范 | flake8 | 复杂度≤10 |
| **类型检查** | 严格类型注解 | mypy | 0 errors |
| **静态分析** | 代码质量分析 | pylint | 评分≥8.0 |

## 🔧 工具详解

### 1. 代码格式化工具

#### **Black** - "毫不妥协"的代码格式化器
```bash
# 安装 (在虚拟环境中)
python -m pip install black==24.4.2

# 手动使用
black .
black --check .  # 仅检查不修改

# 项目中集成
make fmt-python  # 包含在完整格式化流程中
```
**作用**：自动格式化Python代码，消除格式争议

**配置特点**：
- 行长度：88字符 (比PEP8的79字符稍宽)
- 支持Python 3.9, 3.10, 3.11
- 自动处理字符串引号、括号、空行等
- 与isort完美兼容

#### **isort** - Import语句排序工具
```bash
# 安装
python -m pip install isort==5.13.2

# 使用
isort .
isort --check-only .
```

**配置特点**：
- 使用black兼容配置 (`profile = "black"`)
- 多行输出模式3：垂直悬挂缩进
- 自动添加尾随逗号
- 智能识别第三方库和本地模块

### 2. 代码质量检测工具

#### **Flake8** - 语法和风格检查
```bash
# 安装
python -m pip install flake8==7.0.0

# 使用
flake8 .
make check-flake8-python  # 单独运行
```

**检测类别**：
- **E**: PEP8 错误 (Error)
- **W**: PEP8 警告 (Warning)  
- **F**: PyFlakes错误 (Fatal)
- **C**: McCabe复杂度 (Complexity)

**配置要点**：
- 最大行长度：88字符 (与black保持一致)
- 复杂度阈值：10
- 忽略与black冲突的规则：E203, W503, E501

**常见错误码**：
```
E302: expected 2 blank lines, found 1
F401: 'module' imported but unused
C901: 'function' is too complex (11)
W292: no newline at end of file
```

#### **MyPy** - 静态类型检查
```bash
# 安装
python -m pip install mypy==1.9.0

# 使用
mypy .
make check-mypy-python
```

**配置特点**：
- Python版本：3.11
- 严格模式配置：
  - `disallow_untyped_defs`: true - 禁止无类型定义函数
  - `disallow_incomplete_defs`: true - 禁止不完整类型定义
  - `check_untyped_defs`: true - 检查无类型函数体
  - `no_implicit_optional`: true - 禁止隐式Optional

**常见错误**：
```
error: Function is missing a return type annotation
error: Argument 1 has incompatible type "str"; expected "int"
error: Cannot determine type of 'variable'
```

#### **Pylint** - 综合静态分析
```bash
# 安装  
python -m pip install pylint==3.1.0

# 使用
pylint --fail-under=8.0 *.py
make check-pylint-python
```

**评分系统**：
- 满分：10.0分
- 项目要求：≥8.0分
- 扣分规则：错误(-1分)、警告(-0.25分)、重构建议(-0.25分)

**配置要点**：
- 最大行长度：88字符
- 设计约束：
  - 最大参数数量：7
  - 最大局部变量：15
  - 最大返回值：6
  - 最大分支数：12
  - 最大语句数：50

**消息类别**：
- **C**: Convention (约定)
- **R**: Refactor (重构建议)
- **W**: Warning (警告)
- **E**: Error (错误)
- **F**: Fatal (致命错误)

## 🚀 日常使用指南

### 开发工作流

#### 1. 环境初始化
```bash
# 一键安装所有Python工具
make install-tools-python

# 验证工具安装
make check-tools-python

# 查看Python项目信息
make info-python
```

#### 2. 代码开发
```bash
# 编写代码...

# 格式化代码
make fmt-python

# 质量检查
make check-python
```

#### 3. 提交前检查
```bash
# 完整检查（包含格式化）
make fmt && make check

# 或使用Git hooks自动执行（推荐）
git commit -m "feat: add new feature"  # hooks自动运行
```

### 单独工具使用

#### 格式化检查
```bash
# 检查代码格式（不修改文件）
make fmt-check-python

# 自动格式化
make fmt-python
```

#### 质量检查工具
```bash
# 语法和风格检查
make check-flake8-python

# 类型检查
make check-mypy-python

# 静态分析
make check-pylint-python

# 完整质量检查
make check-python
```

## 📊 质量报告解读

### Flake8报告
```bash
$ flake8 .
main.py:15:80: E501 line too long (89 > 88 characters)
main.py:23:1: F401 'os' imported but unused
main.py:45:1: C901 'process_data' is too complex (12)
```
**解读**：
- E501：行长度超限，需要换行或简化
- F401：导入了未使用的模块
- C901：函数复杂度过高，需要重构

### MyPy报告
```bash
$ mypy .
main.py:25: error: Function is missing a return type annotation
main.py:30: error: Argument 1 to "len" has incompatible type "Optional[str]"; expected "Sized"
```
**解读**：
- 第25行：函数缺少返回类型注解
- 第30行：传递了可能为None的值给期望非空参数的函数

### Pylint报告
```bash
$ pylint main.py
************* Module main
main.py:15:0: C0103: Constant name "user_data" doesn't conform to UPPER_CASE naming style (invalid-name)
main.py:25:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)

------------------------------------------------------------------
Your code has been rated at 7.5/10 (previous run: 6.8/10, +0.70)
```
**解读**：
- C0103：常量命名不符合规范
- R1710：函数返回语句不一致
- 当前评分：7.5/10 (低于8.0要求)

## ⚠️ 常见问题处理

### 1. 类型注解缺失
**问题**: `Function is missing a return type annotation`

**解决方案**:
```python
# ❌ 缺少类型注解
def process_data(data):
    return data.upper()

# ✅ 添加类型注解
def process_data(data: str) -> str:
    return data.upper()

# ✅ 复杂类型注解
from typing import List, Dict, Optional

def process_users(users: List[Dict[str, str]]) -> Optional[List[str]]:
    if not users:
        return None
    return [user["name"] for user in users]
```

### 2. 行长度问题
**问题**: `E501 line too long`

**解决方案**:
```python
# ❌ 行太长
result = some_very_long_function_name(argument1, argument2, argument3, argument4, argument5)

# ✅ 合理换行
result = some_very_long_function_name(
    argument1, argument2, argument3, 
    argument4, argument5
)

# ✅ 字符串换行
message = (
    "This is a very long string that needs to be broken "
    "into multiple lines for better readability"
)
```

### 3. 函数复杂度过高
**问题**: `C901 'function' is too complex`

**解决方案**:
```python
# ❌ 复杂度过高
def process_user_data(user):
    if user.age > 18:
        if user.is_active:
            if user.has_permission:
                if user.role == 'admin':
                    return handle_admin(user)
                elif user.role == 'moderator':
                    return handle_moderator(user)
                else:
                    return handle_user(user)
            else:
                return handle_inactive_user(user)
        else:
            return handle_suspended_user(user)
    else:
        return handle_underage_user(user)

# ✅ 重构后
def process_user_data(user):
    """Process user data based on their attributes."""
    if user.age <= 18:
        return handle_underage_user(user)
    
    if not user.is_active:
        return handle_suspended_user(user)
    
    if not user.has_permission:
        return handle_inactive_user(user)
    
    return _handle_active_user(user)

def _handle_active_user(user):
    """Handle active users with permissions."""
    handlers = {
        'admin': handle_admin,
        'moderator': handle_moderator,
    }
    handler = handlers.get(user.role, handle_user)
    return handler(user)
```

### 4. Import排序问题
**解决方案**：自动修复
```bash
# 自动修复import顺序
isort .

# 或者使用完整格式化
make fmt-python
```

### 5. Pylint评分低
**常见改进点**：
```python
# ❌ 问题代码
def getData(userID):
    global data
    if userID == None:
        return
    return data[userID]

# ✅ 改进后
def get_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user data by ID.
    
    Args:
        user_id: The user identifier
        
    Returns:
        User data dictionary or None if not found
    """
    if user_id is None:
        return None
    
    # Avoid global variables, use dependency injection
    return USER_DATA.get(user_id)
```

## 🎛️ 自定义配置

### pyproject.toml配置
```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_gitignore = true

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pylint.messages_control]
max-line-length = 88
good-names = ["i", "j", "k", "ex", "id", "_", "db", "pk", "ui"]
disable = [
    "C0103",  # invalid-name
    "R0903",  # too-few-public-methods  
    "C0111",  # missing-docstring
]

[tool.pylint.design]
max-args = 7
max-locals = 15
max-returns = 6
max-branches = 12
max-statements = 50
```

### setup.cfg配置
```ini
[flake8]
max-line-length = 88
extend-ignore = E203,W503,E501
max-complexity = 10
select = E,W,F,C
exclude = 
    .git,
    __pycache__,
    .venv,
    venv/,
    build/,
    dist/,
    *.egg-info/,
    .mypy_cache/,
    .pytest_cache/
```

## 📈 质量提升建议

### 1. 逐步提升标准
```bash
# 阶段1：基础质量
pylint --fail-under=6.0 *.py

# 阶段2：中等质量  
pylint --fail-under=7.0 *.py

# 阶段3：高质量
pylint --fail-under=8.0 *.py

# 阶段4：优秀质量
pylint --fail-under=9.0 *.py
```

### 2. 持续监控
```bash
# 定期生成质量报告
flake8 --format=html --htmldir=reports/flake8
pylint --output-format=json > reports/pylint.json
mypy --html-report reports/mypy
```

### 3. 团队规范
- 提交前必须通过所有质量检查
- 新代码Pylint评分必须≥8.0
- 类型注解覆盖率要求≥90%
- 复杂度控制：单函数≤10

## 🐍 Python最佳实践

### 1. 类型注解
```python
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    active: bool = True

def get_users(limit: int = 10) -> List[User]:
    """Get list of users with optional limit."""
    pass

def find_user(user_id: int) -> Optional[User]:
    """Find user by ID, return None if not found."""
    pass
```

### 2. 异常处理
```python
from typing import Optional
import logging

def safe_divide(a: float, b: float) -> Optional[float]:
    """Safely divide two numbers."""
    try:
        if b == 0:
            logging.warning("Division by zero attempted")
            return None
        return a / b
    except (TypeError, ValueError) as e:
        logging.error(f"Invalid input for division: {e}")
        return None
```

### 3. 文档字符串
```python
def calculate_tax(income: float, rate: float) -> float:
    """Calculate tax based on income and rate.
    
    Args:
        income: The income amount in currency units
        rate: Tax rate as decimal (e.g., 0.1 for 10%)
        
    Returns:
        The calculated tax amount
        
    Raises:
        ValueError: If income is negative or rate is invalid
        
    Example:
        >>> calculate_tax(10000, 0.1)
        1000.0
    """
    if income < 0:
        raise ValueError("Income cannot be negative")
    if not 0 <= rate <= 1:
        raise ValueError("Rate must be between 0 and 1")
    
    return income * rate
```

## 🔗 参考链接

- [Black文档](https://black.readthedocs.io/)
- [isort文档](https://pycqa.github.io/isort/)
- [Flake8文档](https://flake8.pycqa.org/)
- [MyPy文档](https://mypy.readthedocs.io/)
- [Pylint文档](https://pylint.pycqa.org/)
- [PEP8风格指南](https://pep8.org/)
- [Python类型注解](https://docs.python.org/3/library/typing.html)

---

💡 **记住**：好的Python代码不仅要能运行，还要易读、易维护、类型安全！

🤖 如有问题，参考 `make help` 或联系技术负责人
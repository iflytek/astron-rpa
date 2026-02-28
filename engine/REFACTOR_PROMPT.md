# BizException 重构任务提示词

## 任务目标
将指定组件中的用户可感知的`raise xxx(...)`错误尽量替换成统一的 `raise BizException(ERROR_CODE, message)`，统一项目的错误处理规范。

## 背景信息
项目使用 `BizException` 作为标准业务异常类，定义在：
- 路径：`shared/astronverse-baseline/src/astronverse/baseline/error/error.py`
- 结构：
  ```python
  class BizException(Exception):
      def __init__(self, code: ErrorCode, message: str):
          self.code = code
          self.message = message
  ```

每个组件都有自己的 `error.py` 文件，定义了该组件特定的 `ErrorCode`。

## 修改规范

### 1. 导入检查
确保组件的 `error.py` 已导入：
```python
from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _
```

### 2. 定义 ErrorCode
在组件的 `error.py` 中定义所需的错误码：
```python
# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))
INTERNAL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误"))

# 组件特定错误
SPECIFIC_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("具体错误描述"))
```

### 3. 替换规则

**场景 A：简单字符串消息**
```python
# 修改前
raise Exception("参数不能为空")

# 修改后
raise BizException(PARAM_ERROR, "参数不能为空")
```

**场景 B：格式化消息**
```python
# 修改前
raise Exception(f"找不到文件: {filename}")

# 修改后
raise BizException(ERROR_FORMAT.format(f"找不到文件: {filename}"), f"找不到文件: {filename}")
```

**场景 C：变量消息**
```python
# 修改前
raise Exception(error_msg)

# 修改后
raise BizException(ERROR_FORMAT.format(error_msg), error_msg)
```

### 4. 不需要修改的场景
- `except Exception:` 用于捕获所有异常的情况（需要具体分析）
- 测试文件中的异常（除非明确是业务逻辑测试）
- 第三方库的异常处理

## 注意事项

1. **保持消息内容不变**：只改异常类型，不改错误消息的内容(可以美化)
2. **复用已有 ErrorCode**：优先使用 error.py 中已定义的错误码
3. **合理分类**：相似的错误可以共用一个 ErrorCode（使用 format）
4. **国际化支持**：新增的 ErrorCode 消息使用 `_()` 包裹
5. **不要过度细分**：不需要为每个错误都创建独立的 ErrorCode
6. **不要过渡替换**: 一些内部错误可以不用替换成业务错误
7. **避免滥用通用错误码**：`*_FORMAT` 类型的错误码只应用于真正需要动态内容的场景
8. **正确：区分固定消息和动态消息**：动态已FROMAT结尾，不是动态的不能包含FROMAT

## 常见错误模式

### ❌ 错误：滥用通用错误码

不要用通用的 `*_FORMAT` 错误码来包装固定的错误消息：

```python
# 错误示例 1：固定消息不应使用 ERROR_FORMAT
raise BizException(ERROR_FORMAT.format("未知的响应格式"), "未知的响应格式")

# 错误示例 2：固定消息不应使用 PARAM_ERROR_FORMAT
raise BizException(PARAM_ERROR_FORMAT.format("条件异常，请输入正确的条件！"), "条件异常，请输入正确的条件！")

# 错误示例 3：固定消息不应使用 SHEET_ERROR_FORMAT
raise BizException(SHEET_ERROR_FORMAT.format("新sheet名称已存在"), "新sheet名称已存在")
```

**问题分析：**
- `*_FORMAT` 是通用错误模板，用于动态内容
- 固定的错误消息应该定义为独立的 ErrorCode
- 滥用会导致错误分类不清晰，难以追踪和处理

### ✅ 正确：区分固定消息和动态消息

**固定消息 → 定义独立的 ErrorCode：**

```python
# 在 error.py 中定义
UNKNOWN_RESPONSE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未知的响应格式"))
CONDITION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("条件异常，请输入正确的条件"))
SHEET_NAME_EXISTS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("sheet名称已存在"))

# 使用时
raise BizException(UNKNOWN_RESPONSE_ERROR, "未知的响应格式")
raise BizException(CONDITION_ERROR, "条件异常，请输入正确的条件")
raise BizException(SHEET_NAME_EXISTS_ERROR, "新sheet名称已存在")
```

**动态消息 → 使用 *_FORMAT：**

```python
# 正确使用 ERROR_FORMAT（包含动态内容）
raise BizException(ERROR_FORMAT.format(f"找不到文件: {filename}"), f"找不到文件: {filename}")

# 正确使用 PARAM_ERROR_FORMAT（包含动态参数信息）
raise BizException(PARAM_ERROR_FORMAT.format(f"参数 {param_name} 验证失败"), f"参数 {param_name} 验证失败")

# 正确使用 SHEET_ERROR_FORMAT（包含动态 sheet 名称）
raise BizException(SHEET_ERROR_FORMAT.format(f"sheet '{sheet_name}' 不存在"), f"sheet '{sheet_name}' 不存在")
```

### 判断标准

- **固定消息**：错误描述是固定的，不包含变量 → 定义独立的 ErrorCode
- **动态消息**：错误描述包含变量（文件名、参数名、数值等）→ 使用 `*_FORMAT`

### ⚠️ 重要规则：FORMAT 错误码只接收变量值

**❌ 错误：传入完整的错误描述**

```python
# 错误示例 1：传入完整的中文错误描述
raise BizException(PARAM_ERROR_FORMAT.format("custom_factors 格式错误，请检查"), "custom_factors 格式错误，请检查")

# 错误示例 2：传入包含完整描述的 f-string
raise BizException(ACTION_PARSE_ERROR_FORMAT.format(f"无法解析动作: {raw_str}"), f"无法解析动作: {raw_str}")

# 错误示例 3：传入完整的错误描述而不是变量值
raise BizException(ASPECT_RATIO_ERROR_FORMAT.format(f"绝对宽高比必须小于 {MAX_RATIO}, 实际为 {ratio}"), ...)
```

**✅ 正确：只传入变量值**

```python
# 正确示例 1：只传入变量名
# error.py: CUSTOM_FACTORS_FORMAT_ERROR = ErrorCode(BizCode.LocalErr, _("{} 格式错误，请检查"))
raise BizException(CUSTOM_FACTORS_FORMAT_ERROR.format("custom_factors"), "custom_factors 格式错误，请检查")

# 正确示例 2：只传入需要显示的变量值
# error.py: ACTION_PARSE_ERROR_FORMAT = ErrorCode(BizCode.LocalErr, _("动作解析失败: {}"))
raise BizException(ACTION_PARSE_ERROR_FORMAT.format(raw_str), f"无法解析动作: {raw_str}")

# 正确示例 3：只传入关键的变量信息
# error.py: ASPECT_RATIO_ERROR_FORMAT = ErrorCode(BizCode.LocalErr, _("图片宽高比错误: {}"))
raise BizException(ASPECT_RATIO_ERROR_FORMAT.format(f"最大={MAX_RATIO}, 实际={ratio}"), ...)
```

**核心原则：**
- `*_FORMAT` 错误码的 `format()` 方法只应接收**纯变量值**或**简短的变量信息**
- 不要在 `format()` 中传入完整的错误描述文本（尤其是中文描述）
- 错误描述应该在 ErrorCode 定义中通过 `_()` 国际化
- 如果错误消息是固定的，应该定义独立的 ErrorCode，而不是使用 `*_FORMAT`
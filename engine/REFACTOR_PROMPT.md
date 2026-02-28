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
UNKNOWN_RESPONSE_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未知的响应格式"))
CONDITION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("条件异常，请输入正确的条件"))
SHEET_NAME_EXISTS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("sheet名称已存在"))

# 使用时
raise BizException(UNKNOWN_RESPONSE_FORMAT_ERROR, "未知的响应格式")
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

## 修改策略

### 推荐方式：分批修改

由于涉及的文件较多，建议采用分批修改的方式，降低风险：

**方案 1：按组件分批（推荐）**
```
第一批：Components (组件)
- astronverse-ai
- astronverse-browser
- astronverse-excel
- astronverse-datatable
- astronverse-word

第二批：Servers (服务)
- astronverse-scheduler
- astronverse-picker
- astronverse-executor

第三批：Shared (共享)
- astronverse-actionlib
- astronverse-locator
- astronverse-browser-plugin
```

**方案 2：按错误类型分批**
```
第一批：修复 ERROR_FORMAT 滥用
第二批：修复 PARAM_ERROR_FORMAT 滥用
第三批：修复其他 *_FORMAT 滥用
```

**方案 3：先修复典型案例**
```
1. 选择 2-3 个典型文件作为示例
2. 完成修改并测试
3. 确认无问题后，再批量修改其他文件
```

### 每批修改的步骤

1. **修改 error.py**：添加新的 ErrorCode 定义
2. **修改业务代码**：替换错误的使用方式
3. **本地测试**：确保修改不影响功能
4. **提交代码**：每个组件一个 commit，便于回滚
5. **代码审查**：检查是否有遗漏或错误

### 风险控制

- ✅ 每次只修改一个组件，便于审查和测试
- ✅ 每个组件独立提交，出问题可以快速回滚
- ✅ 优先修改影响小的组件，积累经验
- ✅ 保持错误消息内容不变，只改错误类型
- ❌ 避免一次性修改所有文件
- ❌ 避免在修改过程中改变错误消息的语义


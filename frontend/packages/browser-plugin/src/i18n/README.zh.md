# 浏览器插件国际化 (i18n)

## 概览

浏览器插件现已支持以下语言的国际化：
- **英文** (en)
- **简体中文** (zh-CN)
- **阿拉伯语** (ar)

## 架构

i18n实现包含以下部分：

1. **i18n模块** (`src/i18n/index.ts`) - 核心国际化功能
2. **类型定义** (`src/i18n/types.ts`) - 消息的TypeScript类型定义
3. **语言文件** - 每种支持语言的翻译文件:
   - `src/i18n/locales/en.ts` - 英文翻译
   - `src/i18n/locales/zh-CN.ts` - 简体中文翻译
   - `src/i18n/locales/ar.ts` - 阿拉伯语翻译

## 使用方法

### 基本翻译

导入 `t` 函数并使用它获取翻译：

```typescript
import { t } from '../i18n/index'

const message = t('errors.elementNotFound')
// 返回: "Element not found" (en) / "未找到元素" (zh-CN) / "لم يتم العثور على العنصر" (ar)
```

### 带参数的翻译

对于动态内容，使用参数插值：

```typescript
const message = t('errors.elementChangedAtNode', { 
  index: '5', 
  step: 'removed' 
})
// 返回: "元素在第5节点removed处发生变动"
```

### 设置语言

语言会自动从以下来源检测：
1. 保存在 `chrome.storage.local` 中的偏好设置
2. 浏览器语言设置

手动更改语言：

```typescript
import { setLocale } from '../i18n/index'

await setLocale('en')     // 切换到英文
await setLocale('zh-CN')  // 切换到中文
await setLocale('ar')     // 切换到阿拉伯语
```

### 获取当前语言

```typescript
import { getLocale } from '../i18n/index'

const currentLocale = getLocale()
console.log(currentLocale) // 'en', 'zh-CN', 或 'ar'
```

## 消息结构

所有翻译按以下类别组织：

### 错误信息 (`errors.*`)
- 后台错误：标签页操作、元素操作、执行错误
- 内容错误：元素操作、验证错误

### 成功消息 (`success.*`)
- 操作成功消息

### HTML标签 (`tags.*`)
- HTML标签的可读名称（例如：`div` → "块元素"）

### 输入类型 (`inputTypes.*`)
- 输入类型的可读名称（例如：`text` → "输入框"）

## 添加新翻译

### 步骤1：更新类型定义

在 `src/i18n/types.ts` 中添加新键：

```typescript
export interface Messages {
  errors: {
    // ... 现有键
    myNewError: string
  }
}
```

### 步骤2：添加翻译

在所有语言文件中更新翻译：

**en.ts:**
```typescript
errors: {
  myNewError: 'My new error message',
}
```

**zh-CN.ts:**
```typescript
errors: {
  myNewError: '我的新错误信息',
}
```

**ar.ts:**
```typescript
errors: {
  myNewError: 'رسالة الخطأ الجديدة',
}
```

### 步骤3：在代码中使用

```typescript
import { t } from '../i18n/index'

const message = t('errors.myNewError')
```

## 实现细节

### Getter模式

常量和枚举已转换为使用getter模式以支持动态语言切换：

```typescript
// 之前
export enum ErrorMessage {
  ELEMENT_NOT_FOUND = '未找到元素'
}

// 之后
export const ErrorMessage = {
  get ELEMENT_NOT_FOUND() { return t('errors.elementNotFound') }
}
```

这确保了即使在运行时更改语言，也始终返回正确的翻译。

## 测试

测试不同语言：

1. 打开浏览器扩展
2. 打开浏览器控制台
3. 通过编程方式更改语言：
   ```javascript
   chrome.storage.local.set({ locale: 'en' })
   chrome.storage.local.set({ locale: 'zh-CN' })
   chrome.storage.local.set({ locale: 'ar' })
   ```
4. 重新加载扩展

## RTL支持（阿拉伯语）

为了支持阿拉伯语，可能需要额外的CSS来正确处理从右到左(RTL)的文本方向。考虑添加：

```css
[data-locale="ar"] {
  direction: rtl;
}
```

## 最佳实践

1. **永远不要硬编码面向用户的字符串** - 始终使用 `t()` 函数
2. **使用描述性的键** - 使翻译键清晰且分层
3. **保持翻译一致性** - 在所有消息中使用相似的术语
4. **测试所有语言** - 验证翻译在所有支持的语言中都能正常工作
5. **考虑文本扩展** - 某些语言（如德语或阿拉伯语）可能使用更多空间

## 已完成的改造

本次国际化改造已完成以下工作：

1. ✅ 创建了i18n工具模块和语言文件
2. ✅ 更新了 `background/constant.ts` 使用i18n
3. ✅ 更新了 `content/constant.ts` 使用i18n
4. ✅ 更新了 `content/tag.ts` 和 `content/utils.ts` 使用i18n
5. ✅ 更新了 `content/contentInject.ts` 中的硬编码文本
6. ✅ 修复了TypeScript配置以支持模块解析

## 未来改进

潜在的改进方向：
- 添加更多语言支持
- 实现每个语言环境的日期/时间格式化
- 实现每个语言环境的数字格式化
- 支持复数规则
- 添加语言选择器UI组件
- 支持动态加载语言包以减小初始包大小

## 故障排除

如果遇到导入错误，请尝试：
1. 重启VS Code的TypeScript服务器（命令面板：`TypeScript: Restart TS Server`）
2. 运行 `npm run build` 检查实际构建是否成功
3. 确保 `tsconfig.json` 中的 `moduleResolution` 设置正确

## 构建

使用以下命令构建项目：

```bash
npm run build          # 构建Chrome版本
npm run build:firefox  # 构建Firefox版本
```

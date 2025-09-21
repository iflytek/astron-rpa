# 🔍 TypeScript代码质量检测手册

## 📖 概述

本手册详细说明项目中使用的TypeScript代码质量检测工具链，包括工具介绍、使用方法、质量标准和最佳实践。基于Go和Python的成功实践，为TypeScript项目提供完整的质量保障体系。

## 🛠️ 工具链架构

### 格式化工具链
```
源代码 → prettier → 标准化代码
```

### 质量检测链
```
代码 → eslint → tsc → 质量报告
```

## 🎯 质量标准

| 检测维度 | 标准要求 | 检测工具 | 阈值设置 |
|---------|---------|----------|----------|
| **代码格式** | 符合Prettier标准 | prettier | 强制执行 |
| **代码规范** | ESLint规则检查 | eslint | 0 errors, 0 warnings |
| **类型检查** | 严格类型检查 | tsc | 0 errors |
| **Import管理** | 自动排序整理 | eslint-plugin-import | 自动修复 |
| **代码复杂度** | 圈复杂度控制 | eslint-complexity | ≤10 |
| **最佳实践** | TypeScript最佳实践 | @typescript-eslint | 强制执行 |

## 🔧 工具详解

### 1. 代码格式化工具

#### **Prettier** - 代码格式化器
```bash
# 安装
npm install --save-dev prettier

# 手动使用
npx prettier --write "src/**/*.{ts,tsx}"
npx prettier --check "src/**/*.{ts,tsx}"

# 项目中集成
make fmt-typescript  # 包含在完整格式化流程中
```
**作用**：TypeScript代码格式化器，自动格式化代码符合统一标准

**配置特点**：
- 行长度：80字符
- 缩进：2个空格
- 分号：自动添加
- 引号：单引号
- 尾随逗号：es5
- 自动格式化：TypeScript、TSX、JSON、Markdown

### 2. 代码质量检测工具

#### **ESLint** - 代码规范检查
```bash
# 安装
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin

# 使用
npx eslint "src/**/*.{ts,tsx}"
npx eslint "src/**/*.{ts,tsx}" --fix
```

**核心插件**：
- `@typescript-eslint/eslint-plugin`: TypeScript专用规则
- `eslint-plugin-import`: Import语句管理
- `eslint-plugin-prettier`: Prettier集成
- `eslint-config-prettier`: 禁用与Prettier冲突的规则

**检测类别**：
- **E**: Error（错误）
- **W**: Warning（警告）
- **I**: Info（信息）
- **C**: Complexity（复杂度）

**常见错误码**：
```
@typescript-eslint/no-explicit-any: Unexpected any. Specify a different type
@typescript-eslint/explicit-function-return-type: Missing return type annotation
@typescript-eslint/no-unused-vars: 'variable' is assigned a value but never used
complexity: Function 'functionName' has a complexity of 15
```

#### **TypeScript Compiler (tsc)** - 类型检查
```bash
# 安装
npm install --save-dev typescript

# 使用
npx tsc --noEmit  # 只检查类型，不生成文件
npx tsc --strict  # 严格模式检查
```

**配置特点**：
- TypeScript版本：5.0+
- 严格模式设置：
  - `strict`: true
  - `noImplicitAny`: true
  - `strictNullChecks`: true
  - `strictFunctionTypes`: true
  - `strictBindCallApply`: true
  - `strictPropertyInitialization`: true
  - `noImplicitReturns`: true
  - `noFallthroughCasesInSwitch`: true
  - `noUncheckedIndexedAccess`: true
  - `exactOptionalPropertyTypes`: true

**常见错误**：
```
error TS2322: Type 'string' is not assignable to type 'number'
error TS7031: Binding element 'data' implicitly has an 'any' type
error TS2531: Object is possibly 'null'
```

## 🚀 日常使用指南

### 开发工作流

#### 1. 环境初始化
```bash
# 一键安装所有TypeScript工具
make install-tools-typescript

# 验证工具安装
make check-tools-typescript
```

#### 2. 代码开发
```bash
# 编写代码...

# 格式化代码
make fmt-typescript

# 质量检查
make check-typescript
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
make fmt-check-typescript

# 自动格式化
make fmt-typescript
```

#### 代码规范检查
```bash
# 运行ESLint检查
make check-eslint-typescript

# 自动修复
npx eslint "src/**/*.{ts,tsx}" --fix
```

#### 类型检查
```bash
# 运行TypeScript类型检查
make check-tsc-typescript

# 严格模式检查
npx tsc --strict --noEmit
```

## 📊 质量报告解读

### ESLint报告
```bash
$ npx eslint "src/**/*.{ts,tsx}"
src/components/UserProfile.tsx
  15:10  error  '@typescript-eslint/no-explicit-any'  Unexpected any. Specify a different type
  23:5   error  '@typescript-eslint/explicit-function-return-type'  Missing return type annotation
  45:12  warn   'complexity'  Function 'processUserData' has a complexity of 12
```
**解读**：
- 第15行：使用了any类型，需要指定具体类型
- 第23行：函数缺少返回类型注解
- 第45行：函数复杂度过高，需要重构

### TypeScript编译报告
```bash
$ npx tsc --noEmit
src/utils/helpers.ts:25:5 - error TS2322: Type 'string' is not assignable to type 'number'
src/utils/helpers.ts:30:1 - error TS7031: Binding element 'data' implicitly has an 'any' type
```
**解读**：
- TS2322：类型不匹配，字符串不能赋值给数字类型
- TS7031：参数隐式具有any类型，需要类型注解

## ⚠️ 常见问题处理

### 1. 类型注解缺失
**问题**: `Missing return type annotation`

**解决方案**:
```typescript
// ❌ 缺少返回类型
function processData(data: string) {
  return data.toUpperCase();
}

// ✅ 添加返回类型
function processData(data: string): string {
  return data.toUpperCase();
}

// ✅ 箭头函数类型注解
const processData = (data: string): string => {
  return data.toUpperCase();
};
```

### 2. 使用any类型
**问题**: `Unexpected any. Specify a different type`

**解决方案**:
```typescript
// ❌ 使用any类型
function handleData(data: any): void {
  console.log(data);
}

// ✅ 使用泛型
function handleData<T>(data: T): void {
  console.log(data);
}

// ✅ 使用unknown类型
function handleData(data: unknown): void {
  if (typeof data === 'string') {
    console.log(data.toUpperCase());
  } else if (typeof data === 'number') {
    console.log(data.toFixed(2));
  }
}

// ✅ 使用联合类型
function handleData(data: string | number | boolean): void {
  console.log(data);
}
```

### 3. 函数复杂度过高
**问题**: `Function has a complexity of 15`

**解决方案**:
```typescript
// ❌ 复杂度过高
function processUserData(user: User): ProcessedUser {
  if (user.age > 18) {
    if (user.isActive) {
      if (user.hasPermission) {
        if (user.role === 'admin') {
          return { ...user, status: 'admin' };
        } else if (user.role === 'moderator') {
          return { ...user, status: 'moderator' };
        } else {
          return { ...user, status: 'user' };
        }
      } else {
        return { ...user, status: 'inactive' };
      }
    } else {
      return { ...user, status: 'suspended' };
    }
  } else {
    return { ...user, status: 'underage' };
  }
}

// ✅ 重构后
function processUserData(user: User): ProcessedUser {
  const status = determineUserStatus(user);
  return { ...user, status };
}

function determineUserStatus(user: User): string {
  if (user.age <= 18) return 'underage';
  if (!user.isActive) return 'suspended';
  if (!user.hasPermission) return 'inactive';
  
  return user.role === 'admin' ? 'admin' : 
         user.role === 'moderator' ? 'moderator' : 'user';
}
```

### 4. 空值检查问题
**问题**: `Object is possibly 'null'`

**解决方案**:
```typescript
// ❌ 可能为null
function processData(data: string | null): string {
  return data.toUpperCase(); // 错误：data可能为null
}

// ✅ 空值检查
function processData(data: string | null): string {
  if (data === null) {
    throw new Error('Data cannot be null');
  }
  return data.toUpperCase();
}

// ✅ 使用可选链和空值合并
function processData(data: string | null): string {
  return data?.toUpperCase() ?? '';
}

// ✅ 使用类型守卫
function processData(data: string | null): string {
  if (isValidString(data)) {
    return data.toUpperCase();
  }
  return '';
}

function isValidString(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0;
}
```

### 5. Import顺序问题
**问题**: Import顺序不规范

**解决方案**：配置ESLint自动修复
```bash
npx eslint "src/**/*.{ts,tsx}" --fix
```

## 🎛️ 自定义配置

### Package.json脚本配置
```json
{
  "scripts": {
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,js,jsx,json,md}\"",
    "lint": "eslint \"src/**/*.{ts,tsx}\"",
    "lint:fix": "eslint \"src/**/*.{ts,tsx}\" --fix",
    "type-check": "tsc --noEmit",
    "quality": "npm run format:check && npm run lint && npm run type-check"
  }
}
```

### .prettierrc配置
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

### .eslintrc.js配置
```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    project: './tsconfig.json',
  },
  plugins: [
    '@typescript-eslint',
    'import',
    'prettier'
  ],
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    '@typescript-eslint/recommended-requiring-type-checking',
    'plugin:import/errors',
    'plugin:import/warnings',
    'plugin:import/typescript',
    'prettier'
  ],
  rules: {
    // Prettier集成
    'prettier/prettier': 'error',
    
    // TypeScript严格规则
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/explicit-function-return-type': 'error',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/no-non-null-assertion': 'error',
    '@typescript-eslint/prefer-const': 'warn',
    '@typescript-eslint/no-var-requires': 'warn',
    '@typescript-eslint/strict-boolean-expressions': 'error',
    '@typescript-eslint/no-floating-promises': 'error',
    
    // 代码复杂度控制
    'complexity': ['warn', 10],
    'max-lines-per-function': ['warn', 50],
    'max-params': ['warn', 5],
    'max-depth': ['warn', 4],
    
    // Import管理
    'import/order': [
      'error',
      {
        'groups': [
          'builtin',
          'external',
          'internal',
          'parent',
          'sibling',
          'index'
        ],
        'newlines-between': 'always',
        'alphabetize': {
          'order': 'asc',
          'caseInsensitive': true
        }
      }
    ],
    
    // 最佳实践
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-alert': 'error',
    'prefer-const': 'error',
    'no-var': 'error',
    'no-unused-expressions': 'error',
    'no-duplicate-imports': 'error'
  },
  settings: {
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: './tsconfig.json',
      },
    },
  },
};
```

### tsconfig.json配置
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "removeComments": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "allowUnusedLabels": false,
    "allowUnreachableCode": false
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "build",
    "coverage"
  ]
}
```

## 📈 质量提升建议

### 1. 逐步提升标准
```bash
# 阶段1：基础质量
npx eslint "src/**/*.{ts,tsx}" --max-warnings 10

# 阶段2：中等质量  
npx eslint "src/**/*.{ts,tsx}" --max-warnings 5

# 阶段3：高质量
npx eslint "src/**/*.{ts,tsx}" --max-warnings 0
```

### 2. 持续监控
```bash
# 定期生成质量报告
npx eslint "src/**/*.{ts,tsx}" --format json > eslint-report.json
npx tsc --noEmit > typescript-report.txt
```

### 3. 团队规范
- 提交前必须通过所有质量检查
- 定期review质量报告
- 建立代码质量指标看板
- 分享最佳实践案例

## 🔗 参考链接

- [TypeScript官方文档](https://www.typescriptlang.org/docs/)
- [ESLint文档](https://eslint.org/)
- [Prettier文档](https://prettier.io/)
- [TypeScript ESLint文档](https://typescript-eslint.io/)
- [Effective TypeScript](https://effectivetypescript.com/)

---

💡 **记住**：代码质量检测不是为了限制开发，而是为了帮助我们写出更好、更可靠的TypeScript代码！

🤖 如有问题，参考 `make help` 或联系技术负责人

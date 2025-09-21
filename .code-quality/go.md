# 🔍 Go代码质量检测手册

## 📖 概述

本手册详细说明项目中使用的Go代码质量检测工具链，包括工具介绍、使用方法、质量标准和最佳实践。

## 🛠️ 工具链架构

### 格式化工具链
```
源代码 → go fmt → goimports → gofumpt → golines → 标准化代码
```

### 质量检测链
```
代码 → gocyclo → staticcheck → golangci-lint → 质量报告
```

## 🎯 质量标准

| 检测维度 | 标准要求 | 检测工具 | 阈值设置 |
|---------|---------|----------|----------|
| **代码格式** | 符合Go标准格式 | go fmt + gofumpt | 强制执行 |
| **Import管理** | 无未使用导入 | goimports | 自动清理 |
| **行长度** | 单行不超过120字符 | golines | 120字符 |
| **函数复杂度** | 圈复杂度≤10 | gocyclo | McCabe ≤ 10 |
| **静态分析** | 无潜在bug和问题 | staticcheck | 0 issues |
| **代码规范** | 遵循最佳实践 | golangci-lint | 0 issues |

## 🔧 工具详解

### 1. 代码格式化工具

#### **go fmt** - 基础格式化
```bash
# 手动使用
go fmt ./...

# 项目中集成
make fmt-go  # 包含在完整格式化流程中
```
**作用**：Go官方标准格式化，处理缩进、空格、括号等基础格式

#### **goimports** - Import管理
```bash
# 安装
go install golang.org/x/tools/cmd/goimports@latest

# 使用
goimports -w *.go  # 自动整理imports
```
**功能**：
- 自动添加缺失的import
- 移除未使用的import
- 按标准库、第三方库、本地包分组排序

#### **gofumpt** - 严格格式化
```bash
# 安装
go install mvdan.cc/gofumpt@latest

# 使用  
gofumpt -w *.go
```
**特色**：
- 比go fmt更严格的格式化规则
- 统一字符串字面量格式
- 优化复合字面量布局
- 标准化注释格式

#### **golines** - 行长度控制
```bash
# 安装
go install github.com/segmentio/golines@latest

# 使用
golines -w -m 120 *.go  # 限制120字符
```
**配置**：
- `-m 120`：最大行长度120字符
- `-w`：直接修改文件
- 智能换行，保持代码可读性

### 2. 代码质量检测工具

#### **gocyclo** - 圈复杂度检测
```bash
# 安装
go install github.com/fzipp/gocyclo/cmd/gocyclo@latest

# 使用
gocyclo -over 10 .        # 检查复杂度>10的函数
gocyclo -top 10 .         # 显示最复杂的10个函数
gocyclo -avg .            # 显示平均复杂度
```

**复杂度等级**：
- **1-4**: 简单，易于测试和维护
- **5-7**: 中等，需要注意
- **8-10**: 复杂，需要重构考虑
- **>10**: 高风险，强制重构

**示例输出**：
```
10 main myComplexFunction backend-go/main.go:15:1
```

#### **staticcheck** - 静态代码分析
```bash
# 安装（锁定版本）
go install honnef.co/go/tools/cmd/staticcheck@2025.1.1

# 使用
staticcheck ./...                    # 分析所有包
staticcheck -explain ST1008          # 解释错误码
```

**检测类别**：
- **SA**: Static analysis bugs（静态分析bug）
- **S**: Stylistic issues（代码风格）
- **ST**: Simple improvements（简单改进）
- **U**: Unused code（未使用代码）

**常见错误码**：
```
ST1008: A function's error value should be its final return value
SA1019: Using a deprecated function, variable, constant or field
S1000: Use a simple channel send/receive instead of select
U1000: Unused function
```

#### **golangci-lint** - 综合检测器
```bash
# 安装
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.3.0

# 使用
golangci-lint run ./...              # 运行所有启用的检查器
golangci-lint run --enable-all       # 启用所有检查器
golangci-lint linters                # 列出所有可用检查器
```

**默认启用的检查器**：
- **errcheck**: 检查未处理的错误
- **gosimple**: 简化代码建议
- **govet**: Go官方vet检查
- **ineffassign**: 检查无效赋值
- **staticcheck**: 集成staticcheck
- **typecheck**: 类型检查
- **unused**: 未使用代码检测

## 🚀 日常使用指南

### 开发工作流

#### 1. 环境初始化
```bash
# 一键安装所有Go工具
make install-tools-go

# 验证工具安装
make check-tools-go
```

#### 2. 代码开发
```bash
# 编写代码...

# 格式化代码
make fmt-go

# 质量检查
make check-go
```

#### 3. 提交前检查
```bash
# 完整检查（包含格式化）
make fmt && make check

# 或使用Git hooks自动执行（推荐）
git commit -m "feat: add new feature"  # hooks自动运行
```

### 单独工具使用

#### 复杂度检查
```bash
# 项目整体复杂度
make check-gocyclo

# 查看最复杂的函数
gocyclo -top 5 backend-go/
```

#### 静态分析
```bash
# 运行静态检查
make check-staticcheck  

# 解释特定错误码
make explain-staticcheck code=ST1008
```

#### 综合检查
```bash
# 运行golangci-lint
make check-golangci-lint

# 只检查特定问题类型
golangci-lint run --disable-all --enable=errcheck,gosimple
```

## 📊 质量报告解读

### 圈复杂度报告
```bash
$ gocyclo -over 5 .
8 main processUserData backend-go/user.go:25:1
6 main validateInput backend-go/validator.go:15:1
```
**解读**：
- 函数`processUserData`复杂度为8，需要考虑重构
- 函数`validateInput`复杂度为6，可接受但需关注

### Staticcheck报告
```bash
$ staticcheck ./...
main.go:15:2: SA1019: strings.Title is deprecated (staticcheck)
main.go:23:6: ST1008: error should be the last return value (staticcheck)
```
**解读**：
- SA1019：使用了废弃的API，需要替换
- ST1008：错误返回值应该放在最后

### Golangci-lint报告
```bash
$ golangci-lint run
main.go:10:2: Error return value of `fmt.Printf` is not checked (errcheck)
main.go:15:1: `unusedFunction` is unused (unused)
```
**解读**：
- errcheck：未检查fmt.Printf的错误返回值
- unused：存在未使用的函数

## ⚠️ 常见问题处理

### 1. 复杂度过高
**问题**：`gocyclo: function complexity is over 10`

**解决方案**：
```go
// ❌ 复杂度过高
func processData(data []string) error {
    for _, item := range data {
        if item != "" {
            if len(item) > 10 {
                if strings.Contains(item, "error") {
                    if !strings.HasPrefix(item, "temp") {
                        // 复杂处理逻辑...
                    }
                }
            }
        }
    }
    return nil
}

// ✅ 重构后
func processData(data []string) error {
    for _, item := range data {
        if err := processItem(item); err != nil {
            return err
        }
    }
    return nil
}

func processItem(item string) error {
    if !isValidItem(item) {
        return nil
    }
    return handleValidItem(item)
}
```

### 2. Import顺序问题
**问题**：Import顺序不规范

**解决方案**：运行`goimports`自动修复
```bash
goimports -w *.go
```

### 3. 废弃API使用
**问题**：`SA1019: using deprecated function`

**解决方案**：
```go
// ❌ 使用废弃API
import "strings"
title := strings.Title(name)

// ✅ 使用新API  
import "golang.org/x/text/cases"
import "golang.org/x/text/language"
caser := cases.Title(language.English)
title := caser.String(name)
```

### 4. 错误处理问题
**问题**：`errcheck: error return value not checked`

**解决方案**：
```go
// ❌ 未检查错误
fmt.Printf("Hello %s\n", name)

// ✅ 检查错误
if _, err := fmt.Printf("Hello %s\n", name); err != nil {
    return fmt.Errorf("failed to print: %w", err)
}

// ✅ 或明确忽略
_ = fmt.Printf("Hello %s\n", name)
```

## 🎛️ 自定义配置

### Golangci-lint配置文件
创建`.golangci.yml`：
```yaml
# .golangci.yml
run:
  timeout: 5m
  
linters-settings:
  gocyclo:
    min-complexity: 10
  staticcheck:
    checks: ["all"]
  errcheck:
    check-type-assertions: true
    
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - typecheck
    - unused
    - gocyclo
    - gofmt
    - goimports
  disable:
    - deadcode  # deprecated
    
issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - gocyclo
```

### 自定义复杂度阈值
修改`makefiles/go.mk`：
```makefile
# 将复杂度阈值从10改为8
$(GOCYCLO) -over 8 . || ...
```

## 📈 质量提升建议

### 1. 逐步提升标准
```bash
# 阶段1：基础质量
gocyclo -over 15 .

# 阶段2：中等质量  
gocyclo -over 10 .

# 阶段3：高质量
gocyclo -over 8 .
```

### 2. 持续监控
```bash
# 定期生成质量报告
gocyclo -avg . > complexity_report.txt
golangci-lint run --out-format=json > quality_report.json
```

### 3. 团队规范
- 提交前必须通过所有质量检查
- 定期review质量报告
- 建立代码质量指标看板
- 分享最佳实践案例

## 🔗 参考链接

- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Effective Go](https://golang.org/doc/effective_go.html)
- [Staticcheck文档](https://staticcheck.io/)
- [Golangci-lint文档](https://golangci-lint.run/)
- [圈复杂度理论](https://en.wikipedia.org/wiki/Cyclomatic_complexity)

---

💡 **记住**：代码质量检测不是为了限制开发，而是为了帮助我们写出更好、更可靠的代码！

🤖 如有问题，参考 `make help` 或联系技术负责人
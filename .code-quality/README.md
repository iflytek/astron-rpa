# 📋 代码质量检测文档中心

本目录集中存放所有编程语言的代码质量检测指南和最佳实践文档。

## 📁 目录结构

```
.code-quality/
├── README.md          # 本说明文件
├── go.md             # Go语言代码质量检测完整指南
├── java.md           # Java代码质量检测完整指南
├── python.md         # Python代码质量检测完整指南
└── typescript.md     # TypeScript代码质量检测完整指南
```

## 🎯 支持的语言

| 语言 | 文档 | 工具链 | 状态 |
|------|------|--------|------|
| **Go** | [`go.md`](./go.md) | gofmt + goimports + gofumpt + golines + staticcheck + golangci-lint | ✅ 完整 |
| **Java** | [`java.md`](./java.md) | spotless + checkstyle + spotbugs + pmd | ✅ 完整 |
| **Python** | [`python.md`](./python.md) | black + isort + flake8 + mypy + pylint | ✅ 完整 |
| **TypeScript** | [`typescript.md`](./typescript.md) | prettier + eslint + tsc | ✅ 完整 |

## 🚀 快速开始

### 查看特定语言的质量检测指南
```bash
# Go语言
cat .code-quality/go.md

# Java
cat .code-quality/java.md

# Python  
cat .code-quality/python.md

# TypeScript
cat .code-quality/typescript.md
```

### 运行质量检测
```bash
# 格式化所有支持的语言
make fmt

# 检查所有支持的语言
make check

# 针对特定语言
make fmt-go && make check-go
make fmt-java && make check-java
make fmt-typescript && make check-typescript
make fmt-python && make check-python
```

## 📖 文档说明

每个语言的质量检测文档都包含：

- **🛠️ 工具链架构** - 完整的工具链组成和数据流
- **🎯 质量标准** - 明确的质量检测标准和阈值
- **🔧 工具详解** - 每个工具的作用、配置和使用方法  
- **🚀 使用指南** - 日常开发工作流和最佳实践
- **📊 报告解读** - 如何理解和处理质量检测报告
- **⚠️ 问题处理** - 常见问题的解决方案和最佳实践
- **🎛️ 自定义配置** - 团队定制化配置指南

## 🔗 相关文档

- [`Makefile-readme.md`](../Makefile-readme.md) - 完整的Makefile使用指南
- [`BRANCH_MANAGEMENT.md`](../BRANCH_MANAGEMENT.md) - 分支管理和提交规范
- [`backend-go/`](../backend-go/) - Go项目示例
- [`backend-java/`](../backend-java/) - Java项目示例
- [`frontend-ts/`](../frontend-ts/) - TypeScript项目示例  
- [`backend-python/`](../backend-python/) - Python项目示例

## 💡 贡献指南

添加新语言的代码质量检测文档时，请：

1. 创建 `{language}.md` 文件
2. 遵循现有文档的结构和格式
3. 更新本README的语言支持表格
4. 在 `makefiles/{language}.mk` 中实现相应的工具集成

---

🤖 **自动化是王道** - 好的代码质量检测应该是自动的、一致的、不需要人工干预的！
# 🚀 开发工作流文档中心

本目录集中存放开发工作流相关的指南和规范，帮助团队建立统一、高效的开发流程。

## 📁 目录结构

```
.workflows/
├── README.md          # 本说明文件
└── git.md            # Git分支管理与提交规范完整指南
```

## 🎯 工作流覆盖

| 工作流 | 文档 | 主要内容 | 状态 |
|-------|------|----------|------|
| **Git工作流** | [`git.md`](./git.md) | 分支管理 + 提交规范 + Git hooks | ✅ 完整 |
| **代码审查** | *计划中* | Pull Request + Code Review流程 | 🚧 规划中 |
| **发布流程** | *计划中* | 版本管理 + 发布自动化 | 🚧 规划中 |
| **热修复流程** | *计划中* | 紧急修复 + 快速发布 | 🚧 规划中 |

## 🚀 快速开始

### Git工作流 (核心必读)
```bash
# 查看完整Git工作流指南
cat .workflows/git.md

# 一键初始化开发环境
make dev-setup

# 创建规范分支
make new-feature name=user-login
make new-bugfix name=auth-error

# 安全推送
make safe-push
```

### 核心命令速览
```bash
# 环境设置
make dev-setup              # 安装工具 + 配置Git hooks
make hooks-install           # 安装完整Git hooks
make hooks-install-basic     # 安装轻量Git hooks

# 分支管理  
make new-feature name=功能名  # 创建feature分支
make new-bugfix name=问题名   # 创建bugfix分支
make new-hotfix name=补丁名   # 创建hotfix分支
make safe-push               # 验证并推送分支

# 质量检查
make fmt                     # 格式化所有代码
make check                   # 运行所有质量检查
make check-branch            # 检查分支命名规范
```

## 📋 工作流规范

### 1. 分支命名规范
```
main                    # 主分支
develop                 # 开发集成分支  
feature/功能名          # 新功能开发
bugfix/问题名          # bug修复
hotfix/补丁名          # 紧急修复
design/设计名          # UI/UX优化
refactor/重构名        # 代码重构
test/测试名            # 测试开发
doc/文档名             # 文档更新
```

### 2. 提交消息规范
```
<type>(<scope>): <description>

支持的类型：
feat     新功能               feat: 支持手机号登录
fix      bug修复             fix: 解决token过期问题  
docs     文档更新             docs: 完善API说明
style    代码格式             style: 统一缩进格式
refactor 代码重构             refactor: 拆分用户服务
perf     性能优化             perf: 优化数据库查询
test     测试相关             test: 添加单元测试
build    构建系统             build: 升级webpack到5.0
ci       CI/CD配置           ci: 添加GitHub Actions
chore    杂项任务             chore: 更新.gitignore
revert   回滚提交             revert: 回滚commit abc123
```

### 3. 代码质量门禁
- **格式化**: 自动运行格式化工具
- **语法检查**: 通过各语言的lint工具
- **类型检查**: TypeScript/Python类型验证
- **复杂度控制**: 函数复杂度限制
- **测试覆盖**: 单元测试要求 (规划中)

## 🛡️ 自动化保护机制

### Git Hooks 自动执行
- **pre-commit**: 代码格式化 + 质量检查
- **commit-msg**: 提交消息格式验证  
- **pre-push**: 分支命名规范验证

### 质量门禁
- Go: golangci-lint + staticcheck 全通过
- Python: pylint评分≥8.0 + mypy类型检查
- TypeScript: ESLint零警告 + tsc类型检查

## 🎯 最佳实践

### 开发流程建议
1. **开始开发**: `make dev-setup` (首次) → `make new-feature name=功能名`
2. **编写代码**: 频繁commit，使用规范的commit message
3. **提交前检查**: `make fmt && make check` 确保质量
4. **推送代码**: `make safe-push` 验证并推送
5. **创建PR**: 通过GitHub界面创建Pull Request
6. **代码审查**: 团队review，修改建议
7. **合并代码**: 审查通过后合并到主分支

### 团队协作约定
- 🚫 **禁止直接推送到main/develop分支**
- ✅ **必须通过分支开发 + PR流程**
- ✅ **提交前必须通过所有质量检查**
- ✅ **使用规范的分支命名和提交消息**
- ✅ **大功能拆分为小commit，便于review**

## 🆘 常见问题

### Git工作流问题
- **提交被拒绝**: 检查提交消息格式，使用 `<type>(<scope>): <description>` 格式
- **推送被拒绝**: 检查分支命名，使用 `make new-feature name=xxx` 创建规范分支
- **质量检查失败**: 运行 `make check` 查看详细错误，修复后重新提交
- **想跳过检查**: 使用 `--no-verify` 但不推荐，或安装轻量hooks: `make hooks-install-basic`

### 分支管理问题
- **在错误分支开发**: 使用git命令迁移代码到正确分支
- **分支名不规范**: 重命名分支或创建新的规范分支
- **忘记创建分支**: 从main分支创建新的feature分支，迁移代码

## 🔗 相关文档

- [`.code-quality/`](../.code-quality/) - 代码质量检测指南
- [`Makefile-readme.md`](../Makefile-readme.md) - 完整的Makefile使用手册
- [`README.md`](../README.md) - 项目主文档

## 📈 工作流演进

### 已实现功能 ✅
- Git分支管理和命名规范
- 提交消息格式验证
- 自动代码格式化
- 多语言代码质量检查
- Git hooks自动化

### 规划功能 🚧
- Pull Request模板和规范
- 自动化测试集成
- 版本号管理和发布流程
- 代码审查checklist
- CI/CD管道集成

---

💡 **记住**: 好的工作流程是团队协作的基石，这些规范会让开发更高效、代码更可靠！

🤖 如有问题，参考具体文档或联系技术负责人
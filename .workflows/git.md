# 🚀 分支管理与提交规范指南

## 快速上手

### 1️⃣ 初始化开发环境
```bash
make dev-setup    # 一键安装工具 + 配置Git hooks
```

### 2️⃣ 创建规范分支
```bash
# 新功能开发
make new-feature name=user-login

# 修复bug  
make new-bugfix name=auth-error

# 紧急修复
make new-hotfix name=security-patch

# UI/UX优化
make new-design name=mobile-layout

# 其他类型：refactor, test, doc
```

### 3️⃣ 安全推送
```bash
make safe-push    # 验证分支名 + 推送到远程
```

## 📝 提交消息规范

### 支持的类型
```
build    构建系统/依赖变更     build: 升级webpack到5.0
chore    杂项任务             chore: 更新.gitignore  
ci       CI/CD配置           ci: 添加GitHub Actions
docs     文档更新             docs: 完善API说明
feat     新功能               feat: 支持手机号登录
fix      bug修复             fix: 解决token过期问题
perf     性能优化             perf: 优化数据库查询
refactor 代码重构             refactor: 拆分用户服务
revert   回滚提交             revert: 回滚commit abc123
style    代码格式             style: 统一缩进格式  
test     测试相关             test: 添加单元测试
```

### 格式要求
```
<type>(<scope>): <description>

✅ 正确示例：
feat: 添加用户认证功能
fix(api): 修复登录验证bug
perf(database): 优化查询性能

❌ 错误示例：  
添加新功能
Fix bug
update readme
```

## 🛡️ 自动化保护

### Git Hooks 自动执行
- **提交时**: 自动格式化 + 代码质量检查
- **推送时**: 验证分支命名规范
- **消息时**: 验证提交消息格式

### 支持的分支类型
```
main                    主分支
develop                 开发集成分支
feature/功能名           新功能开发
bugfix/问题名           bug修复  
hotfix/补丁名           紧急修复
design/设计名           UI/UX优化
refactor/重构名         代码重构
test/测试名             测试开发
doc/文档名              文档更新
```

## 🔧 常用命令

### 分支管理
```bash
make branch-help         # 查看完整帮助
make check-branch        # 检查当前分支规范
make list-remote-branches # 列出远程规范分支
```

### Git Hooks
```bash
make hooks-install       # 安装完整hooks (推荐)
make hooks-install-basic # 安装轻量hooks (快速)
make hooks-uninstall     # 卸载所有hooks
```

## ⚠️ 注意事项

1. **首次使用必须运行** `make dev-setup`
2. **分支命名** 必须使用规范格式，否则无法推送
3. **提交消息** 必须符合格式，否则无法提交
4. **代码质量** 不通过会阻止提交
5. **绕过检查** 可以使用 `--no-verify` 但不推荐

## 🆘 常见问题

**Q: 提交被拒绝怎么办？**  
A: 查看错误提示，按提示修改分支名或提交消息格式

**Q: 代码质量检查失败？**  
A: 运行 `make check` 查看详细错误，修复后重新提交

**Q: 想要快速开发，跳过检查？**  
A: 使用 `make hooks-install-basic` 安装轻量版hooks

**Q: 不小心在错误分支开发了？**  
A: 使用相关git命令迁移代码到正确分支

---

💡 **记住**: 这套规范是为了提高代码质量和团队协作效率，习惯后会大大提升开发体验！

🤖 如有问题，参考 `make help` 或联系技术负责人
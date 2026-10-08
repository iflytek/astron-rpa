# 参与贡献 AstronRPA

[English](CONTRIBUTING.md) | 简体中文

感谢你对 AstronRPA 的关注！问题反馈、功能建议、文档和代码贡献都非常欢迎。

## 反馈问题与功能建议

- 先搜索[已有 issue](https://github.com/iflytek/astron-rpa/issues)，没有再按对应的 [issue 模板](https://github.com/iflytek/astron-rpa/issues/new/choose)新建。
- 报告 bug 时请写明 AstronRPA 版本、操作系统、部署方式（Docker / 源码）和复现步骤。
- 使用问题和想法也可以发到 [GitHub Discussions](https://github.com/iflytek/astron-rpa/discussions)。
- **安全漏洞请勿在公开 issue 中提交**，请按 [SECURITY.md](SECURITY.md) 私下报告。

## 开发环境

客户端、引擎和后端服务的构建见 [BUILD_GUIDE.zh.md](BUILD_GUIDE.zh.md)，本地运行完整服务见 [docker/QUICK_START.md](docker/QUICK_START.md)。

| 目录 | 技术栈 |
|---|---|
| `engine/` | Python（uv）：组件、服务和共享库 |
| `backend/` | Java 服务（`robot-service`、`resource-service`、`rpa-auth`）和 Python 服务（`ai-service`、`openapi-service`） |
| `frontend/` | Vue / TypeScript（pnpm） |
| `docker/` | 部署配置 |

## 提交 Pull Request

1. Fork 仓库，从 `main` 创建分支（如 `fix/scheduler-timeout`）。
2. 每个 PR 只做一件事，并关联相关 issue（`Closes #123`）。
3. 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)，如 `fix(websocket-client): return after a message fails to parse`。
4. 每个提交都要签署（`git commit -s`），以确认 [Developer Certificate of Origin](https://developercertificate.org/)。
5. 按 PR 模板填写内容，包括你是如何测试的。
6. 确保 CI 通过。维护者会进行评审，请及时回复评审意见并保持分支与 `main` 同步。

## 测试要求

**新功能和 bug 修复都必须附带自动化测试。**

- 新增功能时，在所改模块的自动化测试中加入对应测试。
- 修复 bug 时，尽量补一个“没有修复就会失败”的回归测试。
- 确实无法自动化测试的改动（如纯 UI 或依赖特定硬件的行为），请在 PR 描述中说明原因和你做的手动验证。
- 评审者会在批准前检查测试；无理由降低改动代码测试覆盖的 PR 可能会被要求补测试。

测试位置与运行方式：

| 范围 | 位置 | 命令 |
|---|---|---|
| 引擎组件 / 服务 / 共享库（Python） | `engine/<分组>/<模块>/tests/` | 在模块目录执行 `uv run --with pytest pytest tests` |
| Python 后端服务 | `backend/ai-service/tests/`、`backend/openapi-service/tests/` | 在服务目录执行 `uv run --dev pytest tests` |
| Java 后端服务 | `backend/<服务>/src/test/java/` | 在服务目录执行 `mvn -B test` |
| 部署配置 | `docker/tests/` | `sh docker/tests/test-render-config.sh` 和 `sh docker/tests/test-nginx-config.sh` |

## 代码风格与静态检查

CI 会在每个 PR 上运行以下检查，推送前请先在本地执行：

- Python：`uv run --project engine --dev ruff format ./engine --check`
- Java：在 `backend/robot-service` 和 `backend/resource-service` 执行 `mvn -B -DskipTests spotless:check`（`spotless:apply` 可自动格式化）
- 前端：在 `frontend/` 执行 `pnpm run lint`（`pnpm run lint:fix` 可修复大部分问题）

新出现的编译器和 linter 警告请修复，而不是屏蔽。

## 许可证

提交贡献即表示你同意你的贡献以 [Apache License 2.0](LICENSE) 授权。

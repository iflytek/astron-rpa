# Security Policy

This project follows the [Iflytek Opensource Community Security Policy](https://github.com/iflytek/community/blob/master/SECURITY.md).

For project-specific security considerations, see below.

## Reporting a Vulnerability

**Do not report security vulnerabilities through public issues, pull requests, or discussions.**

Report privately through either channel:

- GitHub private vulnerability reporting: open the repository's **Security** tab and choose **Report a vulnerability**.
- Email: security@iflytek.com

Please include the affected component and version (or commit), steps to reproduce, the impact, and any suggested fix. If you already have a patch, attach it to the private report instead of opening a public pull request; maintainers will coordinate the fix and disclosure with you.

We will acknowledge your report within 48 hours, keep you informed while we work on a fix, and credit you in the release notes and advisory unless you prefer to remain anonymous.

## Supported Versions

Only the latest release receives security fixes. Please upgrade to the [latest release](https://github.com/iflytek/astron-rpa/releases/latest) before reporting, and mention it if the issue only reproduces on an older version.

## Security Scope

Reports in these areas are especially relevant:

| Component | Examples |
| --- | --- |
| Gateway and backend services | Authentication bypass, identity header spoofing, cross-tenant data access |
| Local scheduler and executor | Remote access to local-only endpoints, command execution |
| AI-generated automation | Model output that escapes into executed code |
| Desktop client | Renderer-to-main IPC abuse, unsafe update verification |

Self-hosted deployments are responsible for network exposure, TLS, and access control. Use HTTPS for any server address configured in clients that connect across machines.

Do not place real credentials, tokens, private keys, or personal data in examples, tests, issues, pull requests, or documentation.

---

## 安全策略（中文）

本项目遵循 [iFlytek 开源社区安全策略](https://github.com/iflytek/community/blob/master/SECURITY.md)。

**请不要通过公开的 Issue、Pull Request 或 Discussion 报告安全漏洞。** 请通过以下任一私密渠道报告：

- GitHub 私密漏洞报告：进入仓库 **Security** 页签，点击 **Report a vulnerability**。
- 邮件：security@iflytek.com

报告中请写明受影响的组件和版本（或 commit）、复现步骤、影响范围以及修复建议。已有补丁的，请附在私密报告里，不要直接提交公开 PR，维护者会与你协调修复和披露。我们会在 48 小时内确认收到，修复过程中保持沟通，并在发布说明和安全公告中致谢（如希望匿名请告知）。

仅最新发布版本接收安全修复。自行部署时，网络暴露、TLS 和访问控制由部署方负责；跨机器连接的客户端请使用 HTTPS 服务地址。

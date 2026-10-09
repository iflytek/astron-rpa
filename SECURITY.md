# Security Policy

AstronRPA follows the [iFLYTEK Open Source Community Security Policy](https://github.com/iflytek/community/blob/master/SECURITY.md). This file describes how to report a vulnerability in this repository.

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues, discussions or pull requests.**

Report privately through either channel:

- [GitHub private vulnerability reporting](https://github.com/iflytek/astron-rpa/security/advisories/new) (preferred)
- Email: [security@iflytek.com](mailto:security@iflytek.com)

Please include:

- The affected component (for example `engine`, `backend/robot-service`, `frontend`) and version or commit
- A description of the vulnerability and its impact
- Steps to reproduce or a proof of concept
- Any suggested fix or mitigation

## What to Expect

- The community security policy provides for acknowledgment within 48 hours, followed by assessment of the vulnerability and its severity.
- We keep you informed while we work on a fix and coordinate the disclosure date with you.
- Fixes are released as a new version and published as a [GitHub Security Advisory](https://github.com/iflytek/astron-rpa/security/advisories). We credit reporters unless they prefer to stay anonymous.

## Supported Versions

Security fixes are made on `main` and shipped in the next [release](https://github.com/iflytek/astron-rpa/releases). Please upgrade to the latest release to receive them.

## Security Scope

Reports in these areas are especially relevant:

| Component | Examples |
| --- | --- |
| Gateway and backend services | Authentication bypass, identity header spoofing, cross-tenant data access |
| Local scheduler and executor | Remote access to local-only endpoints, command execution |
| AI-generated automation | Model output that escapes into executed code |
| Desktop client | Renderer-to-main IPC abuse, unsafe update verification |

Self-hosted deployments are responsible for network exposure, TLS and access control. Use HTTPS for any server address configured in clients that connect across machines.

Do not place real credentials, tokens, private keys or personal data in examples, tests, issues, pull requests or documentation.

---

## 安全策略（中文）

AstronRPA 遵循 [iFLYTEK 开源社区安全策略](https://github.com/iflytek/community/blob/master/SECURITY.md)。

**请不要通过公开的 Issue、Pull Request 或 Discussion 报告安全漏洞。** 请通过以下任一私密渠道报告：

- [GitHub 私密漏洞报告](https://github.com/iflytek/astron-rpa/security/advisories/new)（推荐）
- 邮件：[security@iflytek.com](mailto:security@iflytek.com)

报告中请写明受影响的组件和版本（或 commit）、漏洞描述与影响、复现步骤或 PoC，以及修复建议。按社区安全策略，我们会在 48 小时内确认收到并评估严重程度，修复过程中保持沟通，与你协调披露时间，并在安全公告中致谢（如希望匿名请告知）。

安全修复在 `main` 上进行，并随下一个版本发布，请升级到最新版本。自行部署时，网络暴露、TLS 和访问控制由部署方负责；跨机器连接的客户端请使用 HTTPS 服务地址。

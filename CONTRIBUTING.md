# Contributing to AstronRPA

English | [简体中文](CONTRIBUTING.zh.md)

Thanks for your interest in AstronRPA! Bug reports, feature requests, documentation and code are all welcome.

## Reporting bugs and requesting features

- Search [existing issues](https://github.com/iflytek/astron-rpa/issues) first, then open a new one with the matching [issue template](https://github.com/iflytek/astron-rpa/issues/new/choose).
- For bugs, include the AstronRPA version, OS, deployment mode (Docker / source) and the steps to reproduce.
- Questions and ideas can also go to [GitHub Discussions](https://github.com/iflytek/astron-rpa/discussions).
- **Do not report security vulnerabilities in public issues.** Follow [SECURITY.md](SECURITY.md) instead.

## Development setup

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for building the client, engine and backend services, and [docker/QUICK_START.md](docker/QUICK_START.md) for running the full stack locally.

| Directory | Stack |
|---|---|
| `engine/` | Python (uv workspace): components, servers and shared libraries |
| `backend/` | Java services (`robot-service`, `resource-service`, `rpa-auth`) and Python services (`ai-service`, `openapi-service`) |
| `frontend/` | Vue / TypeScript (pnpm) |
| `docker/` | Deployment configuration |

## Submitting a pull request

1. Fork the repository and create a branch from `main` (for example `fix/scheduler-timeout`).
2. Keep each PR focused on one change, and link the related issue (`Closes #123`).
3. Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages, e.g. `fix(websocket-client): return after a message fails to parse`.
4. Sign off every commit (`git commit -s`) to certify the [Developer Certificate of Origin](https://developercertificate.org/).
5. Fill in the pull request template, including how you tested the change.
6. Make sure CI passes. A maintainer will review the PR; please respond to review comments and keep the branch up to date.

## Testing policy

**New functionality and bug fixes must come with automated tests.**

- When you add a feature, add tests for it to the automated test suite of the module you changed.
- When you fix a bug, add a regression test that fails without the fix whenever practical.
- If a change genuinely cannot be covered by an automated test (for example, UI-only or hardware-dependent behavior), explain why in the PR description and describe the manual verification you did.
- Reviewers check for tests before approving, and PRs that reduce test coverage of changed code without a reason may be asked to add tests.

Where tests live and how to run them:

| Area | Location | Command |
|---|---|---|
| Engine components / servers / shared libs (Python) | `engine/<group>/<module>/tests/` | `uv run --with pytest pytest tests` in the module directory |
| Python backend services | `backend/ai-service/tests/`, `backend/openapi-service/tests/` | `uv run --dev pytest tests` in the service directory |
| Java backend services | `backend/<service>/src/test/java/` | `mvn -B test` in the service directory |
| Deployment configuration | `docker/tests/` | `sh docker/tests/test-render-config.sh` and `sh docker/tests/test-nginx-config.sh` |

## Code style and static checks

CI runs these checks on every pull request; run them locally before pushing:

- Python: `uv run --project engine --dev ruff format ./engine --check`
- Java: `mvn -B -DskipTests spotless:check` in `backend/robot-service` and `backend/resource-service` (`spotless:apply` fixes formatting)
- Frontend: `pnpm run lint` in `frontend/` (`pnpm run lint:fix` fixes most issues)

Please fix new compiler and linter warnings instead of suppressing them.

## License

By contributing, you agree that your contributions are licensed under the [Apache License 2.0](LICENSE).

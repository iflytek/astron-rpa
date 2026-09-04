# AGENTS.md

Guidance for AI coding agents working in the **astron-rpa** (AstronRPA)
repository — an agent-ready RPA suite with out-of-the-box automation tools for
desktop applications, web systems, and business-process automation.

AstronRPA uses a **server–client** architecture: server components run via
Docker, and the client (RPA engine + desktop app) is packaged and run on the
machine that executes RPA tasks. The client toolchain is Windows-first.

## Project layout

This is a multi-language monorepo driven by a unified `Makefile` (with modular
includes under `makefiles/`).

- `backend/` — server-side microservices (deployed via Docker Compose):
  - `robot-service/`, `resource-service/`, `rpa-auth/` — Java / Spring Boot
    services (Maven; each ships `checkstyle.xml`, `pmd-ruleset.xml`,
    `spotbugs-exclude.xml`).
  - `ai-service/`, `openapi-service/` — Python services (managed with `uv`).
- `engine/` — the Python RPA execution engine (managed with `uv`, linted with
  `ruff`): `main.py`, `components/` (RPA components), `servers/`, `shared/`.
- `frontend/` — pnpm workspace monorepo (Vue 3 + TypeScript, Vitest, ESLint,
  i18n under `locales/`). Notable packages under `frontend/packages/`:
  `electron-app` (desktop client), `web-app` (web console), `browser-plugin`,
  `auth-app`, `cli`, `components`, `shared`.
- `docker/` — Docker Compose manifests for the server stack.
- `makefiles/` — modular Make components (`common.mk`, `python.mk`, `java.mk`,
  `typescript.mk`, `go.mk`, `git.mk`).
- `resources/` — packaged client resources. `docs/`, `FAQ.md`, `BUILD_GUIDE.md`
  — documentation.

## Toolchain

- **Python 3.13.x** + **uv 0.8+** — RPA engine and Python services.
- **Node.js 22+** + **pnpm 9+** — frontend workspace.
- **Java JDK 8+** + **Maven** — Java backend services.
- **Docker & Docker Compose** — server deployment.
- Windows client packaging also needs **SWIG** (Python↔C/C++ bindings, e.g.
  `pywinhook`) and **7-Zip** (deployment archives). See `BUILD_GUIDE.md`.

## Common commands

Quality and git workflow are driven by the root `Makefile` (run `make help` to
see detected projects and targets):

- `make install-tools` — install the formatting/linting toolchain.
- `make fmt` — format across languages (`fmt-python`, `fmt-java`, `fmt-ts`, …).
- `make check` (alias `make lint`) — format check + linters
  (`check-python`, `check-java`, `check-ts`, …). CI is check-only; it does not
  auto-fix.
- `make new-feature name=<short-name>` / `make new-bugfix name=<short-name>` —
  branch helpers following the project's branch strategy.

Pre-commit hooks (install with `pre-commit install`) format the engine with
ruff: `uv run --project engine --dev ruff format ./engine`.

### Run the server (Docker)

```bash
cd docker
cp .env.example .env
# configure the public HTTPS names and copy the certificate/key to docker/certs/
# see docker/HTTPS_DEPLOYMENT.md for required variables
docker compose up -d
docker compose ps
```

Gateway API: https://localhost · Casdoor auth: https://localhost:8443

### Build the client (Windows)

```bash
# full build (engine + frontend desktop app) from the repo root
./build.bat --python-exe "C:\Program Files\Python313\python.exe"
./build.bat --skip-frontend   # engine only
./build.bat --skip-engine     # frontend only
```

The packaged installer is written to `frontend/packages/electron-app/dist/`.

### Frontend (pnpm workspace, from `frontend/`)

```bash
pnpm install
pnpm dev:web         # run the web console in dev
pnpm dev:desktop     # run the desktop app in dev
pnpm build:desktop   # build the Windows desktop app
```

## Testing instructions

There is no aggregate `make test`; run tests per component:

- **Frontend**: `pnpm test` (Vitest) or `pnpm test:run` for a single run.
- **Python** (`engine`, `backend/ai-service`, `backend/openapi-service`):
  `uv run pytest` within the project where tests exist (e.g. `backend/ai-service`
  has a `tests/` directory).
- **Java** (`backend/robot-service`, `resource-service`, `rpa-auth`):
  `mvn test` within the service directory.

Run `make check` and the relevant tests before opening a PR, and add or update
tests for code you change.

## Code style

Formatting and linting are wired through `make fmt` / `make check`:

| Language        | Format / Lint                                                        |
| --------------- | -------------------------------------------------------------------- |
| Python          | `ruff` format + `ruff` check (see `engine/.ruff.toml`)               |
| Java            | Checkstyle + PMD + SpotBugs (per-service configs)                     |
| TypeScript/Vue  | ESLint (`frontend/eslint.config.mjs`); `pnpm lint` / `pnpm lint:fix` |

## PR instructions

- Create branches with the Make helpers (`make new-feature name=<…>`).
- Run `make check` and the relevant component tests before committing; make sure
  pre-commit hooks pass.
- Keep PRs focused and write clear, conventional commit messages.
- For build and deployment details, see `BUILD_GUIDE.md`.

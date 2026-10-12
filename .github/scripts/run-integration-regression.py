"""Run the bounded integration suites in clean environments; no deployed services required."""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_TESTS = [
    "test_execution_isolation.py",
    "test_execution_management.py",
    "test_external_security.py",
    "test_integration_policy.py",
    "test_mcp_auth.py",
    "test_mcp_modern.py",
    "test_schema_readiness.py",
    "test_sensitive_logging.py",
    "test_service_read.py",
    "test_workflow_control.py",
    "test_workflow_isolation.py",
    "test_workflow_schema.py",
]
ENGINE_TESTS = {
    "browser": ["test_read_context.py"],
    "database": ["test_query.py"],
    "email": ["test_receive_email.py", "test_core_imap4_receive.py"],
    "network": ["test_read.py"],
    "enterprise": ["test_shared_read.py"],
}
# Only imports needed by these unit tests. Native GUI dependencies, full component
# packaging and remote database drivers are deliberately outside this test environment.
ENGINE_DEPENDENCIES = ["python-dateutil", "pycryptodome", "keyring", "loguru", "toml", "pyyaml", "requests"]


def run(command, *, cwd, env):
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=["openapi", "engine"])
    parser.add_argument("--component", choices=ENGINE_TESTS)
    parser.add_argument("--report-dir", type=Path, required=True)
    args = parser.parse_args()
    if (args.suite == "engine") != bool(args.component):
        parser.error("--component is required only for the engine suite")
    if args.suite == "engine" and os.name != "nt":
        parser.error("Engine regression targets the Windows client; use a Windows runner")
    reports = args.report_dir.resolve()
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="astron-integration-regression-") as workspace:
        work = Path(workspace)
        env = os.environ.copy()
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", PYTHONUTF8="1")
        # Do not inherit an active local environment, plugins or pytest selection flags.
        for key in ("VIRTUAL_ENV", "PYTHONPATH", "PYTEST_ADDOPTS", "PYTEST_PLUGINS"):
            env.pop(key, None)
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        pytest_args = ["-q", "--import-mode=importlib", "-o", f"cache_dir={work / 'pytest-cache'}"]
        if args.suite == "openapi":
            project = ROOT / "backend/openapi-service"
            env.update(
                UV_PROJECT_ENVIRONMENT=str(work / "venv"),
                DATABASE_URL="mysql+aiomysql://{username}:{password}@127.0.0.1:3307/test_db",
                DATABASE_USERNAME="test_user",
                DATABASE_PASSWORD="test_password",
                REDIS_URL="redis://127.0.0.1:6380/0",
                LOG_DIR=str(work / "logs"),
                INTEGRATION_POLICY_FILE="",
            )
            run(
                ["uv", "sync", "--locked", "--project", str(project), "--python", "3.13", "--group", "dev"],
                cwd=work,
                env=env,
            )
            run(
                [
                    "uv",
                    "run",
                    "--no-sync",
                    "--project",
                    str(project),
                    "python",
                    "-m",
                    "pytest",
                    "-p",
                    "pytest_asyncio.plugin",
                    *pytest_args,
                    f"--junitxml={reports / 'openapi.xml'}",
                    *[str(project / "tests" / test) for test in OPENAPI_TESTS],
                ],
                cwd=project,
                env=env,
            )
        else:
            component = ROOT / "engine/components" / f"astronverse-{args.component}"
            sources = [
                component / "src",
                ROOT / "engine/shared/astronverse-actionlib/src",
                ROOT / "engine/shared/astronverse-baseline/src",
            ]
            dependencies = list(ENGINE_DEPENDENCIES)
            if args.component == "browser":
                sources.append(ROOT / "engine/components/astronverse-software/src")
                dependencies.extend(["psutil", "pywin32"])
            # Reuse the committed Engine versions without resolving its full GUI/EXE graph
            # or generating component-level lockfiles during a test run.
            lock = tomllib.loads((ROOT / "engine/uv.lock").read_text(encoding="utf-8"))
            versions = {package["name"]: package["version"] for package in lock["package"]}
            command = ["uv", "run", "--no-project", "--isolated", "--python", "3.13", "--with", "pytest==8.3.5"]
            for dependency in dependencies:
                command.extend(["--with", f"{dependency}=={versions[dependency]}"])
            env["PYTHONPATH"] = os.pathsep.join(str(source) for source in sources)
            run(
                [
                    *command,
                    "python",
                    "-m",
                    "pytest",
                    *pytest_args,
                    f"--junitxml={reports / f'engine-{args.component}.xml'}",
                    *[str(component / "tests" / test) for test in ENGINE_TESTS[args.component]],
                ],
                cwd=work,
                env=env,
            )


if __name__ == "__main__":
    main()

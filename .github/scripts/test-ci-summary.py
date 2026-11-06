"""Execute the actual CI summary shell against success/failure scheduling cases."""

import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/main-ci.yml"
COMPONENTS = ("engine", "frontend", "backend", "deployment", "integration")
JOBS = ("style-check", "deployment-security-test", "integration-regression")


class SummaryTest(unittest.TestCase):
    def check_summary(self, changed=(), results=None, detection="success"):
        source = WORKFLOW.read_text(encoding="utf-8")
        marker = "      - name: Generate CI Summary\n        run: |\n"
        self.assertEqual(source.count(marker), 1)
        script = "\n".join(line[10:] for line in source.split(marker)[1].splitlines())
        expected = {
            "style-check": bool(set(changed) & {"engine", "frontend", "backend"}),
            "deployment-security-test": "deployment" in changed,
            "integration-regression": "integration" in changed,
        }
        states = {job: "success" if expected[job] else "skipped" for job in JOBS}
        states.update(results or {})
        expressions = {
            **{
                f"needs.check-changes.outputs.{c}-changed": str(c in changed).lower()
                for c in COMPONENTS
            },
            **{f"needs.{job}.result": state for job, state in states.items()},
            "needs.check-changes.result": detection,
        }
        script = re.sub(r"\$\{\{\s*(.*?)\s*\}\}", lambda m: expressions[m[1]], script)
        bash = os.environ.get("ASTRON_TEST_BASH") or shutil.which("bash")
        self.assertIsNotNone(
            bash, "Bash is required to verify the actual workflow shell"
        )
        result = subprocess.run(
            [bash, "-s"],
            input=script,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
        )
        success = detection == "success" and all(
            states[j] == "success" for j in JOBS if expected[j]
        )
        self.assertEqual(
            result.returncode, 0 if success else 1, result.stdout + result.stderr
        )

    def test_path_specific_failures_cancellation_and_skips(self):
        for component in COMPONENTS:
            job = (
                JOBS[1]
                if component == "deployment"
                else JOBS[2]
                if component == "integration"
                else JOBS[0]
            )
            for state in ("success", "failure", "cancelled", "skipped"):
                with self.subTest(component=component, state=state):
                    self.check_summary((component,), {job: state})

    def test_no_changes_and_all_changes(self):
        self.check_summary()
        self.check_summary(COMPONENTS)
        for job in JOBS:
            with self.subTest(job=job):
                self.check_summary(COMPONENTS, {job: "failure"})

    def test_change_detection_failure_cannot_pass(self):
        for state in ("failure", "cancelled", "skipped"):
            with self.subTest(state=state):
                self.check_summary(detection=state)


if __name__ == "__main__":
    unittest.main()

"""Run with python3 -m unittest discover -s tests -p 'test_casdoor_credentials.py'."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "credentials", ROOT / "scripts/sync-casdoor-credentials.py"
)
CREDENTIALS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CREDENTIALS)


class CasdoorCredentialsTest(unittest.TestCase):
    def test_docker_failure_does_not_disclose_credential_output(self):
        result = subprocess.CompletedProcess(
            [], 1, "sensitive value", "sensitive value"
        )
        with patch.object(CREDENTIALS.subprocess, "run", return_value=result):
            with self.assertRaises(RuntimeError) as failure:
                CREDENTIALS.run(["docker", "compose"], ROOT)
        self.assertNotIn("sensitive value", str(failure.exception))

    def test_missing_database_credentials_leave_existing_env_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / ".env").write_text("EXISTING=preserved\n", encoding="utf-8")
            config = {
                "services": {
                    "rpa-auth": {
                        "environment": {"CASDOOR_APPLICATION_NAME": "example-app"}
                    }
                }
            }
            with (
                patch.object(
                    CREDENTIALS, "__file__", str(directory / "scripts/sync.py")
                ),
                patch("sys.argv", ["sync.py"]),
                patch.object(CREDENTIALS, "run", side_effect=[json.dumps(config), ""]),
                self.assertRaises(ValueError),
            ):
                CREDENTIALS.main()
            self.assertEqual((directory / ".env").read_text(), "EXISTING=preserved\n")
            self.assertEqual(list(directory.glob(".casdoor-env-*")), [])

    def test_bootstrap_generates_secrets_and_signing_keys(self):
        data = json.loads(
            (ROOT / "volumes/casdoor/init_data_dump.json").read_text(encoding="utf-8")
        )
        for cert in data["certs"]:
            self.assertFalse(cert.get("certificate"))
            self.assertFalse(cert.get("privateKey"))
            self.assertEqual(cert["cryptoAlgorithm"], "RS256")
            self.assertGreaterEqual(cert["bitSize"], 3072)
        for application in data["applications"]:
            self.assertFalse(application.get("clientSecret"))
            self.assertIn(application["cert"], [cert["name"] for cert in data["certs"]])

    def test_multiline_update_is_idempotent_and_preserves_other_settings(self):
        original = '# deployment\nOTHER="unchanged"\nCASDOOR_CERTIFICATE=\'old\ncertificate\'\nCASDOOR_CLIENT_SECRET="old"\n'
        values = {
            "CASDOOR_CERTIFICATE": "new\npublic certificate\n",
            "CASDOOR_CLIENT_SECRET": "new$literal",
        }
        result = CREDENTIALS.update_env(original, values)
        self.assertEqual(result, CREDENTIALS.update_env(result, values))
        self.assertIn('OTHER="unchanged"', result)
        self.assertNotIn("old", result)
        self.assertIn("CASDOOR_CLIENT_SECRET='new$literal'", result)
        self.assertIn("CASDOOR_CERTIFICATE='new\npublic certificate\n'", result)

    def test_appends_missing_values(self):
        self.assertEqual(
            CREDENTIALS.update_env("X=1", {"KEY": "value"}), "X=1\nKEY='value'\n"
        )

    def test_rejects_duplicates_without_selecting_an_arbitrary_secret(self):
        with self.assertRaises(ValueError):
            CREDENTIALS.update_env("KEY=one\nKEY=two\n", {"KEY": "new"})

    def test_rejects_values_that_could_change_dotenv_structure(self):
        for value in ["quote'", "null\x00", "carriage\rreturn"]:
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                CREDENTIALS.dotenv_value(value)


if __name__ == "__main__":
    unittest.main()

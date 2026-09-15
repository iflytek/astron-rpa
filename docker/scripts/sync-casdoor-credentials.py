#!/usr/bin/env python3
"""Copy this deployment's Casdoor application credentials to its Compose .env."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def dotenv_value(value):
    # Compose single quotes preserve PEM newlines and prevent $ interpolation.
    if "'" in value or "\x00" in value or "\r" in value:
        raise ValueError("Unsupported character in Casdoor configuration")
    return "'" + value + "'"


def update_env(content, values):
    for key, value in values.items():
        pattern = re.compile(
            r"^"
            + re.escape(key)
            + r"[ \t]*=[ \t]*(?:'[^']*'|\"(?:\\.|[^\"\\])*\"|[^\n]*)[^\n]*",
            re.MULTILINE,
        )
        replacement = key + "=" + dotenv_value(value)
        if len(pattern.findall(content)) > 1:
            raise ValueError("Duplicate configuration entry: " + key)
        if pattern.search(content):
            content = pattern.sub(lambda _: replacement, content)
        else:
            content = content.rstrip("\n") + "\n" + replacement + "\n"
    return content


def run(command, cwd, data=None):
    result = subprocess.run(
        command,
        cwd=str(cwd),
        input=data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
    )
    if result.returncode:
        # Compose config and SQL errors can contain credentials; do not echo them.
        raise RuntimeError(
            "Docker Compose operation failed; check the project and running MySQL/Casdoor services"
        )
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-name", help="Existing Compose project name, if explicitly set"
    )
    args = parser.parse_args()
    directory = Path(__file__).resolve().parents[1]
    # The supplied Compose services load docker/.env through x-env-file.
    # A different CLI --env-file would only change interpolation, not that mount.
    env_file = directory / ".env"
    if env_file.is_symlink() or not env_file.is_file():
        raise ValueError("Create a regular deployment .env file first")
    compose = ["docker", "compose", "--env-file", str(env_file)]
    if args.project_name:
        compose += ["--project-name", args.project_name]
    config = json.loads(run(compose + ["config", "--format", "json"], directory))
    environment = config["services"]["rpa-auth"]["environment"]
    application = environment.get("CASDOOR_APPLICATION_NAME")
    database = environment.get("CASDOOR_DATABASE_NAME", "casdoor")
    if not application or not re.fullmatch(r"[A-Za-z0-9_]+", database):
        raise ValueError("Invalid Casdoor application or database configuration")
    query = (
        "SELECT HEX(a.client_id),HEX(a.client_secret),HEX(c.certificate) "
        "FROM `{0}`.application a JOIN `{0}`.cert c "
        "ON c.owner='admin' AND c.name=IF(a.cert='', 'cert-built-in', a.cert) "
        "WHERE a.owner='admin' AND BINARY a.name=0x{1};"
    ).format(database, application.encode("utf-8").hex())
    rows = (
        run(
            compose
            + [
                "exec",
                "-T",
                "mysql",
                "sh",
                "-c",
                'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -u root -N --batch',
            ],
            directory,
            query,
        )
        .strip()
        .splitlines()
    )
    if len(rows) != 1 or len(rows[0].split("\t")) != 3:
        raise ValueError(
            "Application/signing certificate missing or ambiguous; wait for Casdoor initialization"
        )
    client_id, secret, certificate = (
        bytes.fromhex(x).decode("utf-8") for x in rows[0].split("\t")
    )
    if (
        not client_id
        or not secret
        or not certificate.startswith("-----BEGIN CERTIFICATE-----")
    ):
        raise ValueError("Casdoor has not generated complete application credentials")
    updated = update_env(
        env_file.read_text(encoding="utf-8"),
        {
            "CASDOOR_CLIENT_ID": client_id,
            "CASDOOR_CLIENT_SECRET": secret,
            "CASDOOR_CERTIFICATE": certificate,
        },
    )
    # Atomic replacement, restricted permissions, no credential output or backup copies.
    descriptor, temporary = tempfile.mkstemp(
        prefix=".casdoor-env-", dir=str(env_file.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            output.write(updated)
        os.chmod(temporary, 0o600)
        os.replace(temporary, env_file)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(
        "Casdoor application credentials synchronized. Recreate rpa-auth to apply them."
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        raise SystemExit(str(error)) from None

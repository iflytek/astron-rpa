"""Bounded, owner-scoped binary storage, separate from JSON execution records.

Handles are opaque and never contain a client/server path. The private SQLite
manifest and blobs must share a persistent deployment directory. This is a
single-deployment local store, not a distributed object storage implementation.
"""

import asyncio
import hashlib
import os
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID, uuid4

from app.security.workflow_authorization import WorkflowAccessError

FILE_LIMITS = {"maxFileBytes": 10 * 1024 * 1024, "maxFiles": 8, "retentionSeconds": 86400}
OWNER_QUOTA = 100 * 1024 * 1024


def deny(code):
    raise WorkflowAccessError(code, "File request could not be completed")


def file_id(value):
    try:
        if str(UUID(value)) != value:
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        deny("FILE_NOT_FOUND")
    return value


def file_name(value):
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= 160
        or value in {".", ".."}
        or value[-1:] in {".", " "}
        or re.search(r'[\\/:<>"|?*\x00-\x1f\x7f]', value)
        or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", value, re.IGNORECASE)
    ):
        deny("FILE_NAME_INVALID")
    return value


class IntegrationFileStore:
    def __init__(self, directory):
        if not directory:
            deny("FILE_TRANSFER_UNAVAILABLE")
        self.root = Path(directory).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.manifest = self.root / "manifest.sqlite3"
        with self.db() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, owner TEXT NOT NULL, "
                "execution TEXT, name TEXT NOT NULL, size INTEGER NOT NULL, sha256 TEXT, "
                "expires REAL NOT NULL, state TEXT NOT NULL, upload_key TEXT, "
                "UNIQUE(owner, upload_key))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS grants (token_hash TEXT PRIMARY KEY, file_id TEXT NOT NULL, "
                "mode TEXT NOT NULL, execution TEXT NOT NULL, expires REAL NOT NULL)"
            )
        self.manifest.chmod(0o600)

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.manifest, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def blob(self, identifier):
        path = self.root / (file_id(identifier) + ".blob")
        if path.is_symlink():
            deny("FILE_NOT_FOUND")
        return path

    @staticmethod
    def public(row):
        return {
            "fileId": row["id"],
            "fileName": row["name"],
            "size": row["size"],
            "sha256": row["sha256"],
            "expiresAt": row["expires"],
        }

    def get(self, identifier, owner=None, *, ready=True):
        file_id(identifier)
        with self.db() as db:
            row = db.execute("SELECT * FROM files WHERE id=?", (identifier,)).fetchone()
        if row is None or (owner is not None and row["owner"] != owner):
            deny("FILE_NOT_FOUND")
        if row["expires"] <= time.time():
            deny("FILE_EXPIRED")
        if ready and row["state"] != "ready":
            deny("FILE_NOT_READY")
        return dict(row)

    def reserve(self, owner, name, *, execution=None, upload_key=None, identifier=None):
        self.cleanup()
        file_name(name)
        identifier = file_id(identifier) if identifier else str(uuid4())
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            if upload_key:
                row = db.execute("SELECT * FROM files WHERE owner=? AND upload_key=?", (owner, upload_key)).fetchone()
                if row:
                    if row["name"] != name or row["execution"] != execution:
                        deny("FILE_IDEMPOTENCY_CONFLICT")
                    return dict(row)
            count, allocated = db.execute(
                "SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE owner=?", (owner,)
            ).fetchone()
            if count >= 64 or allocated + FILE_LIMITS["maxFileBytes"] > OWNER_QUOTA:
                deny("FILE_QUOTA_EXCEEDED")
            db.execute(
                "INSERT INTO files VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    identifier,
                    owner,
                    execution,
                    name,
                    FILE_LIMITS["maxFileBytes"],
                    None,
                    time.time() + FILE_LIMITS["retentionSeconds"],
                    "pending",
                    upload_key,
                ),
            )
        return self.get(identifier, owner, ready=False)

    def write(self, identifier, data):
        """Commit only whole bounded buffers; identical retries are idempotent."""
        if len(data) > FILE_LIMITS["maxFileBytes"]:
            deny("FILE_TOO_LARGE")
        checksum = hashlib.sha256(data).hexdigest()
        target = self.blob(identifier)
        temporary = self.root / (str(uuid4()) + ".part")
        try:
            with temporary.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.chmod(0o600)
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT * FROM files WHERE id=?", (identifier,)).fetchone()
                if row is None or row["expires"] <= time.time():
                    deny("FILE_EXPIRED")
                if row["state"] == "ready":
                    if row["sha256"] != checksum or row["size"] != len(data):
                        deny("FILE_IDEMPOTENCY_CONFLICT")
                else:
                    temporary.replace(target)
                    db.execute(
                        "UPDATE files SET size=?, sha256=?, state='ready' WHERE id=?",
                        (len(data), checksum, identifier),
                    )
            return self.public(self.get(identifier))
        finally:
            temporary.unlink(missing_ok=True)

    def read(self, identifier, owner=None):
        row = self.get(identifier, owner)
        try:
            with self.blob(identifier).open("rb") as stream:
                data = stream.read(FILE_LIMITS["maxFileBytes"] + 1)
        except OSError:
            deny("FILE_NOT_FOUND")
        if len(data) != row["size"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            deny("FILE_INTEGRITY_FAILED")
        return row, data

    def grant(self, identifier, owner, execution, mode, expires):
        if mode not in {"read", "write"}:
            deny("FILE_PERMISSION_DENIED")
        row = self.get(identifier, owner, ready=mode == "read")
        if mode == "write" and row["execution"] != execution:
            deny("FILE_PERMISSION_DENIED")
        token = secrets.token_urlsafe(32)
        with self.db() as db:
            db.execute(
                "INSERT INTO grants VALUES (?,?,?,?,?)",
                (hashlib.sha256(token.encode()).hexdigest(), identifier, mode, execution, expires),
            )
            db.execute("UPDATE files SET expires=MAX(expires,?) WHERE id=?", (expires, identifier))
        return token

    def authorize(self, identifier, token, mode):
        if not isinstance(token, str) or not 20 <= len(token) <= 100:
            deny("FILE_PERMISSION_DENIED")
        with self.db() as db:
            row = db.execute(
                "SELECT * FROM grants WHERE token_hash=? AND file_id=? AND mode=? AND expires>?",
                (hashlib.sha256(token.encode()).hexdigest(), file_id(identifier), mode, time.time()),
            ).fetchone()
        if row is None:
            deny("FILE_PERMISSION_DENIED")
        return dict(row)

    def revoke(self, execution):
        with self.db() as db:
            db.execute("DELETE FROM grants WHERE execution=?", (execution,))
            db.execute("DELETE FROM files WHERE execution=? AND state='pending'", (execution,))

    def delete(self, identifier, owner):
        self.get(identifier, owner, ready=False)
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM grants WHERE file_id=? AND expires>?", (identifier, time.time())).fetchone():
                deny("FILE_IN_USE")
            self.blob(identifier).unlink(missing_ok=True)
            db.execute("DELETE FROM files WHERE id=? AND owner=?", (identifier, owner))

    def cleanup(self):
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM grants WHERE expires<=?", (time.time(),))
            for row in db.execute("SELECT id FROM files WHERE expires<=?", (time.time(),)).fetchall():
                self.blob(row["id"]).unlink(missing_ok=True)
                db.execute("DELETE FROM files WHERE id=?", (row["id"],))
        # An interrupted atomic write can leave a partial file. Never remove an
        # in-flight write or anything outside this store's private directory.
        for path in self.root.glob("*.part"):
            try:
                UUID(path.stem)
                if not path.is_symlink() and path.stat().st_mtime < time.time() - 3600:
                    path.unlink(missing_ok=True)
            except (OSError, ValueError):
                continue


def store():
    from app.config import get_settings

    return IntegrationFileStore(get_settings().INTEGRATION_FILE_ROOT)


async def maintain_files():
    from app.config import get_settings
    from app.logger import get_logger

    if not get_settings().INTEGRATION_FILE_ROOT:
        return
    while True:
        try:
            await asyncio.to_thread(store().cleanup)
        except Exception:
            get_logger(__name__).warning("Integration file cleanup failed; retrying on the next interval")
        await asyncio.sleep(300)

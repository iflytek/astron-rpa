import re
from urllib.parse import urlparse

from astronverse.scheduler.config import Config

# PEP 508 distribution name; rejects URLs, VCS specs, paths, options and extras
PACKAGE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
# Version literal used after "=="; rejects spaces, "@", ";" and leading "-"
VERSION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.!+_-]*$")
PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

# Default index hosts, kept in sync with frontend PythonPackageManagement/config.ts
PIP_MIRROR_ALLOW_HOSTS = (
    "pypi.mirrors.ustc.edu.cn",
    "mirrors.aliyun.com",
    "pypi.tuna.tsinghua.edu.cn",
    "pypi.python.org",
    "pypi.org",
    "pypi.douban.com",
)


def validate_package_name(package: str) -> str:
    if not isinstance(package, str) or not PACKAGE_NAME_PATTERN.match(package):
        raise ValueError("invalid package name: {!r}".format(package))
    return package


def validate_version(version: str) -> str:
    if not version:
        return ""
    if not isinstance(version, str) or not VERSION_PATTERN.match(version):
        raise ValueError("invalid package version: {!r}".format(version))
    return version


def allowed_mirror_hosts() -> set:
    hosts = {host.lower() for host in PIP_MIRROR_ALLOW_HOSTS}
    extra = getattr(Config, "pip_mirror_allow_hosts", None) or []
    hosts.update(str(host).strip().lower() for host in extra if str(host).strip())
    return hosts


def validate_mirror(mirror: str) -> str:
    if not isinstance(mirror, str) or not mirror:
        raise ValueError("pip mirror is required")
    parsed = urlparse(mirror)
    if parsed.scheme not in ("https", "http"):
        raise ValueError("invalid pip mirror scheme: {!r}".format(mirror))
    if parsed.username or parsed.password:
        raise ValueError("pip mirror must not contain credentials")
    hostname = (parsed.hostname or "").lower()
    if hostname not in allowed_mirror_hosts():
        raise ValueError("pip mirror host is not allowed: {!r}".format(hostname))
    return mirror


def is_insecure_mirror(mirror: str) -> bool:
    return urlparse(mirror).scheme == "http"


def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str) or not PROJECT_ID_PATTERN.match(project_id):
        raise ValueError("invalid project_id: {!r}".format(project_id))
    return project_id

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import urlsplit, urlunsplit

TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

EXCLUDED_DIR_NAMES = {
    ".git",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "venv",
}

RUNTIME_DATA_PREFIXES = (
    "data/",
    "data_v2/",
    "tower/data/",
)

SENSITIVE_BASENAMES = {
    ".env",
    "id_dsa",
    "id_ed25519",
    "id_rsa",
    "users_secure.json",
}

SENSITIVE_SUFFIXES = {
    ".key",
    ".p12",
    ".pem",
    ".pfx",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_command(
    command: Sequence[str],
    *,
    cwd: Path | str | None = None,
    check: bool = False,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
        env={
            **os.environ,
            "GIT_TERMINAL_PROMPT": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )

    if check and result.returncode != 0:
        rendered = " ".join(command)
        raise RuntimeError(
            f"Command failed ({result.returncode}): {rendered}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return result


def run_git(
    repo_root: Path,
    *args: str,
    check: bool = False,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    return run_command(
        ["git", "-C", str(repo_root), *args],
        check=check,
        timeout=timeout,
    )


def find_repo_root(start: Path | str | None = None) -> Path:
    candidate = Path(start or Path.cwd()).resolve()

    if candidate.is_file():
        candidate = candidate.parent

    for path in (candidate, *candidate.parents):
        if (path / ".git").exists():
            return path

    raise RuntimeError(f"No Git repository found from: {candidate}")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
    return sha256_bytes(encoded)


def sanitize_remote_url(url: str) -> str:
    value = (url or "").strip()
    if not value:
        return value

    if "://" not in value:
        return value

    parts = urlsplit(value)
    hostname = parts.hostname or ""
    if parts.port is not None:
        hostname = f"{hostname}:{parts.port}"

    return urlunsplit(
        (
            parts.scheme,
            hostname,
            parts.path,
            parts.query,
            parts.fragment,
        )
    )


def tracked_files(repo_root: Path) -> list[str]:
    result = run_git(repo_root, "ls-files", "-z", check=True, timeout=300)
    return sorted(path for path in result.stdout.split("\0") if path)


def latest_checkpoint_dirs(repo_root: Path, limit: int = 3) -> list[Path]:
    checkpoint_root = repo_root / "integration_checkpoints"
    if not checkpoint_root.exists():
        return []

    directories = sorted(
        (path for path in checkpoint_root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
        reverse=True,
    )
    return directories[: max(0, limit)]


def is_sensitive_path(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    path = Path(normalized)
    lower_name = path.name.lower()

    if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
        return True

    if lower_name in SENSITIVE_BASENAMES:
        return True

    if lower_name.startswith(".env."):
        return True

    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        return True

    if lower_name.endswith("credentials.json"):
        return True

    if lower_name.endswith("secrets.json"):
        return True

    return False


def is_runtime_data_path(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.startswith(RUNTIME_DATA_PREFIXES)


def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True

    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False

    return b"\x00" not in sample


def parse_porcelain_paths(output: str) -> list[str]:
    paths: list[str] = []
    for raw_line in (output or "").splitlines():
        if len(raw_line) < 4:
            continue
        value = raw_line[3:].strip()
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        if value:
            paths.append(value)
    return paths


def unique_preserving_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def safe_slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return cleaned.strip("-._") or "context"

from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

from .common import (
    TEXT_SUFFIXES,
    is_probably_text,
    is_runtime_data_path,
    is_sensitive_path,
    latest_checkpoint_dirs,
    run_git,
    sha256_file,
    tracked_files,
    unique_preserving_order,
    utc_now,
    write_json,
)

RUNTIME_PATTERNS = (
    re.compile(r"\bFlask\s*\("),
    re.compile(r"\bFastAPI\s*\("),
    re.compile(r"\bBlueprint\s*\("),
    re.compile(r"\bcreate_app\b"),
    re.compile(r"\bapp\.run\s*\("),
    re.compile(r"\bgunicorn\b", re.IGNORECASE),
    re.compile(r"\bwsgi\b", re.IGNORECASE),
    re.compile(r"\basgi\b", re.IGNORECASE),
)

ENV_PATTERNS = (
    re.compile(r"os\.getenv\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"os\.environ\.get\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"os\.environ\[\s*['\"]([^'\"]+)['\"]\s*\]"),
)

TOP_LEVEL_ALWAYS_INCLUDE = {
    ".gitignore",
    "Dockerfile",
    "Procfile",
    "README.md",
    "app.py",
    "gunicorn.conf.py",
    "manage.py",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "runtime.txt",
    "setup.cfg",
    "setup.py",
    "wsgi.py",
}


def _text(relative_path: str, repo_root: Path, max_file_bytes: int) -> str | None:
    path = repo_root / relative_path
    try:
        if not path.is_file() or path.stat().st_size > max_file_bytes:
            return None
        if not is_probably_text(path):
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _recent_changed_files(repo_root: Path, commit_limit: int = 8) -> list[str]:
    result = run_git(
        repo_root,
        "log",
        f"-{commit_limit}",
        "--name-only",
        "--format=",
        timeout=300,
    )
    if result.returncode != 0:
        return []
    return unique_preserving_order(
        line.strip() for line in result.stdout.splitlines() if line.strip()
    )


def _runtime_candidates(
    repo_root: Path,
    paths: list[str],
    max_file_bytes: int,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for relative_path in paths:
        path = Path(relative_path)
        if path.suffix.lower() != ".py":
            continue
        if is_runtime_data_path(relative_path) or is_sensitive_path(relative_path):
            continue

        content = _text(relative_path, repo_root, max_file_bytes)
        if content is None:
            continue

        hits = [pattern.pattern for pattern in RUNTIME_PATTERNS if pattern.search(content)]
        if hits:
            candidates.append(
                {
                    "path": relative_path,
                    "hits": hits,
                }
            )

    return candidates


def _environment_names(
    repo_root: Path,
    paths: list[str],
    max_file_bytes: int,
) -> dict[str, list[str]]:
    results: dict[str, set[str]] = {}

    for relative_path in paths:
        if Path(relative_path).suffix.lower() != ".py":
            continue
        if is_runtime_data_path(relative_path) or is_sensitive_path(relative_path):
            continue

        content = _text(relative_path, repo_root, max_file_bytes)
        if content is None:
            continue

        names: set[str] = set()
        for pattern in ENV_PATTERNS:
            names.update(pattern.findall(content))
        if names:
            results[relative_path] = names

    return {
        path: sorted(names)
        for path, names in sorted(results.items())
    }


def _latest_checkpoint_paths(
    repo_root: Path,
    tracked_set: set[str],
    checkpoint_limit: int,
) -> list[str]:
    selected: list[str] = []
    for directory in latest_checkpoint_dirs(repo_root, checkpoint_limit):
        prefix = str(directory.relative_to(repo_root)).replace("\\", "/") + "/"
        selected.extend(path for path in tracked_set if path.startswith(prefix))
    return sorted(selected)


def _focused_candidates(
    repo_root: Path,
    paths: list[str],
    runtime_candidates: list[dict[str, Any]],
    checkpoint_limit: int,
) -> list[str]:
    tracked_set = set(paths)
    candidates: list[str] = []

    candidates.extend(path for path in paths if "/" not in path and path in TOP_LEVEL_ALWAYS_INCLUDE)
    candidates.extend(path for path in paths if path.startswith("tools/"))
    candidates.extend(_recent_changed_files(repo_root))
    candidates.extend(item["path"] for item in runtime_candidates)
    candidates.extend(_latest_checkpoint_paths(repo_root, tracked_set, checkpoint_limit))

    selected_source_names = {
        Path(path).stem
        for path in candidates
        if Path(path).suffix.lower() == ".py"
    }

    for relative_path in paths:
        path = Path(relative_path)
        if path.suffix.lower() != ".py" or not path.name.startswith("test"):
            continue

        content = _text(relative_path, repo_root, 512 * 1024)
        if content is None:
            continue

        if any(name and name in content for name in selected_source_names):
            candidates.append(relative_path)

    return [path for path in unique_preserving_order(candidates) if path in tracked_set]


def select_snapshot_paths(
    repo_root: Path,
    *,
    mode: str,
    checkpoint_limit: int,
    max_file_bytes: int,
) -> tuple[list[str], list[dict[str, Any]], dict[str, list[str]]]:
    paths = tracked_files(repo_root)
    runtime_candidates = _runtime_candidates(repo_root, paths, max_file_bytes)
    environment_names = _environment_names(repo_root, paths, max_file_bytes)

    if mode == "full":
        candidates = paths
    elif mode == "focused":
        candidates = _focused_candidates(
            repo_root,
            paths,
            runtime_candidates,
            checkpoint_limit,
        )
    else:
        raise ValueError(f"Unsupported snapshot mode: {mode}")

    return candidates, runtime_candidates, environment_names


def create_source_snapshot(
    repo_root: Path,
    destination_root: Path,
    *,
    mode: str = "focused",
    checkpoint_limit: int = 3,
    max_file_bytes: int = 512 * 1024,
    max_total_bytes: int = 40 * 1024 * 1024,
) -> dict[str, Any]:
    source_root = destination_root / "source"
    source_root.mkdir(parents=True, exist_ok=True)

    candidates, runtime_candidates, environment_names = select_snapshot_paths(
        repo_root,
        mode=mode,
        checkpoint_limit=checkpoint_limit,
        max_file_bytes=max_file_bytes,
    )

    included: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    total_bytes = 0

    for relative_path in candidates:
        source = repo_root / relative_path

        if is_sensitive_path(relative_path):
            skipped.append({"path": relative_path, "reason": "sensitive_path"})
            continue

        if is_runtime_data_path(relative_path):
            skipped.append({"path": relative_path, "reason": "runtime_data"})
            continue

        try:
            size = source.stat().st_size
        except OSError:
            skipped.append({"path": relative_path, "reason": "stat_failed"})
            continue

        if size > max_file_bytes:
            skipped.append({"path": relative_path, "reason": "file_size_limit"})
            continue

        if total_bytes + size > max_total_bytes:
            skipped.append({"path": relative_path, "reason": "total_size_limit"})
            continue

        if source.suffix.lower() not in TEXT_SUFFIXES and not is_probably_text(source):
            skipped.append({"path": relative_path, "reason": "non_text"})
            continue

        destination = source_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        total_bytes += size
        included.append(
            {
                "path": relative_path,
                "size_bytes": size,
                "sha256": sha256_file(source),
            }
        )

    write_json(destination_root / "runtime_candidates.json", runtime_candidates)
    write_json(destination_root / "environment_variable_names.json", environment_names)

    manifest = {
        "schema_version": "simplee.devkit.source_snapshot.v1",
        "generated_at": utc_now(),
        "mode": mode,
        "checkpoint_limit": checkpoint_limit,
        "max_file_bytes": max_file_bytes,
        "max_total_bytes": max_total_bytes,
        "included_file_count": len(included),
        "included_total_bytes": total_bytes,
        "runtime_candidate_count": len(runtime_candidates),
        "environment_variable_name_count": len(
            {name for names in environment_names.values() for name in names}
        ),
        "included": included,
        "skipped": skipped,
    }
    write_json(destination_root / "source_manifest.json", manifest)
    return manifest


def create_zip(context_directory: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(context_directory.rglob("*")):
            if not path.is_file():
                continue
            archive.write(path, arcname=str(path.relative_to(context_directory)))

    return zip_path


def read_latest_resume_checkpoint(repo_root: Path) -> tuple[Path | None, dict[str, Any]]:
    for directory in latest_checkpoint_dirs(repo_root, limit=20):
        candidate = directory / "resume_checkpoint.json"
        if not candidate.exists():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        return candidate, payload
    return None, {}

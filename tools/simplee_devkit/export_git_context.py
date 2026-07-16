from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import (
    parse_porcelain_paths,
    run_git,
    sanitize_remote_url,
    utc_now,
    write_json,
)


def _git_text(repo_root: Path, *args: str) -> str:
    result = run_git(repo_root, *args)
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


def _collect_remotes(repo_root: Path) -> list[dict[str, str]]:
    names = [
        value.strip()
        for value in _git_text(repo_root, "remote").splitlines()
        if value.strip()
    ]

    remotes: list[dict[str, str]] = []
    for name in names:
        raw_url = _git_text(repo_root, "config", "--get", f"remote.{name}.url")
        remotes.append(
            {
                "name": name,
                "url": sanitize_remote_url(raw_url),
            }
        )
    return remotes


def _collect_recent_commits(repo_root: Path, limit: int) -> list[dict[str, str]]:
    separator = "\x1f"
    record_separator = "\x1e"
    result = run_git(
        repo_root,
        "log",
        f"-{limit}",
        f"--format=%H{separator}%h{separator}%aI{separator}%an{separator}%s{record_separator}",
    )

    if result.returncode != 0:
        return []

    commits: list[dict[str, str]] = []
    for record in result.stdout.split(record_separator):
        record = record.strip()
        if not record:
            continue
        parts = record.split(separator)
        if len(parts) != 5:
            continue
        commits.append(
            {
                "commit": parts[0],
                "short_commit": parts[1],
                "authored_at": parts[2],
                "author": parts[3],
                "subject": parts[4],
            }
        )
    return commits


def collect_git_context(repo_root: Path, recent_commit_limit: int = 25) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    status = _git_text(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    branch = _git_text(repo_root, "branch", "--show-current")
    head = _git_text(repo_root, "rev-parse", "HEAD")
    short_head = _git_text(repo_root, "rev-parse", "--short", "HEAD")
    origin_main = _git_text(repo_root, "rev-parse", "--verify", "origin/main")
    upstream = _git_text(repo_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    upstream_head = _git_text(repo_root, "rev-parse", "--verify", "@{u}") if upstream else ""

    return {
        "schema_version": "simplee.devkit.git_context.v1",
        "generated_at": utc_now(),
        "repository_root": str(repo_root),
        "branch": branch,
        "head": head,
        "short_head": short_head,
        "origin_main": origin_main,
        "upstream": upstream,
        "upstream_head": upstream_head,
        "working_tree_clean": status == "",
        "status_porcelain": status.splitlines(),
        "changed_paths": parse_porcelain_paths(status),
        "remotes": _collect_remotes(repo_root),
        "recent_commits": _collect_recent_commits(repo_root, recent_commit_limit),
    }


def export_git_context(
    repo_root: Path,
    destination: Path,
    recent_commit_limit: int = 25,
) -> dict[str, Any]:
    payload = collect_git_context(repo_root, recent_commit_limit=recent_commit_limit)
    write_json(destination, payload)
    return payload

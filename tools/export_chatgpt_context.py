#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

TOOLS_ROOT = Path(__file__).resolve().parent
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from simplee_devkit import __version__
from simplee_devkit.common import (
    canonical_digest,
    find_repo_root,
    safe_slug,
    sha256_file,
    utc_now,
    utc_stamp,
    write_json,
)
from simplee_devkit.create_snapshot import (
    create_source_snapshot,
    create_zip,
    read_latest_resume_checkpoint,
)
from simplee_devkit.export_git_context import export_git_context
from simplee_devkit.export_repo_tree import export_repo_tree


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Export a safe, upload-ready Simplee development context package "
            "without changing repository state."
        )
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Repository root. Defaults to auto-detection from this script.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/content/simplee_context_exports"),
        help="Directory outside Git where context folders and ZIPs are written.",
    )
    parser.add_argument(
        "--mode",
        choices=("focused", "full"),
        default="focused",
        help="focused selects likely active files; full includes all safe tracked text files.",
    )
    parser.add_argument("--checkpoint-limit", type=int, default=3)
    parser.add_argument("--recent-commit-limit", type=int, default=25)
    parser.add_argument("--max-file-bytes", type=int, default=512 * 1024)
    parser.add_argument("--max-total-bytes", type=int, default=40 * 1024 * 1024)
    parser.add_argument(
        "--keep-directory",
        action="store_true",
        help="Keep the unzipped context directory after ZIP creation.",
    )
    return parser


def _handoff_markdown(
    *,
    repo_root: Path,
    git_context: dict[str, Any],
    tree_summary: dict[str, Any],
    source_manifest: dict[str, Any],
    checkpoint_path: Path | None,
    checkpoint: dict[str, Any],
    zip_name: str,
) -> str:
    checkpoint_rel = (
        str(checkpoint_path.relative_to(repo_root))
        if checkpoint_path is not None
        else "<none found>"
    )

    lines = [
        "# Simplee Development Context Handoff",
        "",
        f"Generated: `{utc_now()}`",
        f"DevKit version: `{__version__}`",
        "",
        "## Repository",
        "",
        f"- Root: `{repo_root}`",
        f"- Branch: `{git_context.get('branch') or '<detached>'}`",
        f"- HEAD: `{git_context.get('head') or '<unknown>'}`",
        f"- origin/main: `{git_context.get('origin_main') or '<unavailable>'}`",
        f"- Working tree clean: `{git_context.get('working_tree_clean')}`",
        f"- Tracked files: `{tree_summary.get('tracked_file_count', 0)}`",
        f"- Python files: `{tree_summary.get('python_file_count', 0)}`",
        f"- Tests: `{tree_summary.get('test_file_count', 0)}`",
        "",
        "## Active checkpoint",
        "",
        f"- File: `{checkpoint_rel}`",
        f"- Closed layer: `{checkpoint.get('closed_layer', '<unknown>')}`",
        f"- Closed through step: `{checkpoint.get('closed_through_step', '<unknown>')}`",
        f"- Decision: `{checkpoint.get('final_decision', '<unknown>')}`",
        f"- Next boundary: `{checkpoint.get('next_boundary', '<unknown>')}`",
        "",
        "## Snapshot",
        "",
        f"- Mode: `{source_manifest.get('mode')}`",
        f"- Included files: `{source_manifest.get('included_file_count', 0)}`",
        f"- Included bytes: `{source_manifest.get('included_total_bytes', 0)}`",
        f"- Runtime candidates: `{source_manifest.get('runtime_candidate_count', 0)}`",
        f"- Environment variable names: `{source_manifest.get('environment_variable_name_count', 0)}`",
        f"- Upload file: `{zip_name}`",
        "",
        "## Safety",
        "",
        "- Raw runtime data directories are excluded.",
        "- Git internals and cache directories are excluded.",
        "- Common credential, key, certificate, and dotenv files are excluded.",
        "- Remote URLs are sanitized to remove embedded credentials.",
        "- Environment variable names may be included; values are never exported by the DevKit.",
        "- The exporter performs no commit, push, merge, checkout, reset, or provider action.",
    ]
    return "\n".join(lines) + "\n"


def export_context(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = find_repo_root(args.repo or TOOLS_ROOT)
    output_root = args.output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    stamp = utc_stamp()
    context_name = f"simplee_context_{safe_slug(repo_root.name)}_{stamp}"
    context_directory = output_root / context_name
    zip_path = output_root / f"{context_name}.zip"

    if context_directory.exists() or zip_path.exists():
        raise RuntimeError(f"Refusing to overwrite an existing export: {context_name}")

    context_directory.mkdir(parents=True)

    try:
        git_context = export_git_context(
            repo_root,
            context_directory / "git_context.json",
            recent_commit_limit=args.recent_commit_limit,
        )
        tree_summary = export_repo_tree(
            repo_root,
            context_directory / "repository_tree.txt",
            context_directory / "tracked_files.txt",
            context_directory / "repository_summary.json",
        )
        source_manifest = create_source_snapshot(
            repo_root,
            context_directory,
            mode=args.mode,
            checkpoint_limit=args.checkpoint_limit,
            max_file_bytes=args.max_file_bytes,
            max_total_bytes=args.max_total_bytes,
        )
        checkpoint_path, checkpoint = read_latest_resume_checkpoint(repo_root)

        handoff = _handoff_markdown(
            repo_root=repo_root,
            git_context=git_context,
            tree_summary=tree_summary,
            source_manifest=source_manifest,
            checkpoint_path=checkpoint_path,
            checkpoint=checkpoint,
            zip_name=zip_path.name,
        )
        (context_directory / "AI_HANDOFF.md").write_text(handoff, encoding="utf-8")

        summary = {
            "schema_version": "simplee.devkit.context_export.v1",
            "devkit_version": __version__,
            "generated_at": utc_now(),
            "repository_root": str(repo_root),
            "branch": git_context.get("branch"),
            "head": git_context.get("head"),
            "origin_main": git_context.get("origin_main"),
            "working_tree_clean": git_context.get("working_tree_clean"),
            "mode": args.mode,
            "latest_resume_checkpoint": (
                str(checkpoint_path.relative_to(repo_root))
                if checkpoint_path is not None
                else None
            ),
            "closed_layer": checkpoint.get("closed_layer"),
            "closed_through_step": checkpoint.get("closed_through_step"),
            "final_decision": checkpoint.get("final_decision"),
            "next_boundary": checkpoint.get("next_boundary"),
            "tracked_file_count": tree_summary.get("tracked_file_count"),
            "included_source_file_count": source_manifest.get("included_file_count"),
            "runtime_candidate_count": source_manifest.get("runtime_candidate_count"),
            "environment_variable_name_count": source_manifest.get(
                "environment_variable_name_count"
            ),
        }
        summary["summary_digest"] = canonical_digest(summary)
        write_json(context_directory / "export_summary.json", summary)

        create_zip(context_directory, zip_path)
        summary["zip_path"] = str(zip_path)
        summary["zip_sha256"] = sha256_file(zip_path)
        summary["zip_size_bytes"] = zip_path.stat().st_size

        if not args.keep_directory:
            shutil.rmtree(context_directory)

        return summary

    except Exception:
        if context_directory.exists():
            shutil.rmtree(context_directory)
        if zip_path.exists():
            zip_path.unlink()
        raise


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    summary = export_context(args)

    print("=" * 88)
    print("SIMPLEE DEVKIT CONTEXT EXPORT COMPLETE")
    print("=" * 88)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print()
    print("Upload this ZIP into ChatGPT:")
    print(summary["zip_path"])
    print()
    print("No repository files were modified by the exporter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

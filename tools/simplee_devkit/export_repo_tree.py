from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .common import tracked_files, write_json


_TREE_FILE = "__files__"


def _insert_path(tree: dict[str, Any], relative_path: str) -> None:
    parts = Path(relative_path).parts
    node = tree
    for part in parts[:-1]:
        node = node.setdefault(part, {_TREE_FILE: []})
    node.setdefault(_TREE_FILE, []).append(parts[-1])


def _render_node(node: dict[str, Any], prefix: str = "") -> list[str]:
    directories = sorted(key for key in node if key != _TREE_FILE)
    files = sorted(node.get(_TREE_FILE, []))
    entries: list[tuple[str, bool]] = [(name, True) for name in directories] + [
        (name, False) for name in files
    ]

    lines: list[str] = []
    for index, (name, is_directory) in enumerate(entries):
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{name}")

        if is_directory:
            extension = "    " if is_last else "│   "
            lines.extend(_render_node(node[name], prefix + extension))

    return lines


def render_tree(paths: list[str], root_label: str = ".") -> str:
    tree: dict[str, Any] = {_TREE_FILE: []}
    for relative_path in sorted(paths):
        _insert_path(tree, relative_path)
    return "\n".join([root_label, *_render_node(tree)]) + "\n"


def collect_tree_summary(paths: list[str]) -> dict[str, Any]:
    suffix_counts = Counter(Path(path).suffix.lower() or "<no_suffix>" for path in paths)
    top_level_counts = Counter(Path(path).parts[0] for path in paths if Path(path).parts)
    test_count = sum(
        1
        for path in paths
        if Path(path).name.startswith("test") and Path(path).suffix.lower() == ".py"
    )
    python_count = sum(1 for path in paths if Path(path).suffix.lower() == ".py")

    return {
        "tracked_file_count": len(paths),
        "python_file_count": python_count,
        "test_file_count": test_count,
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "top_level_counts": dict(sorted(top_level_counts.items())),
    }


def export_repo_tree(
    repo_root: Path,
    tree_destination: Path,
    tracked_destination: Path,
    summary_destination: Path,
) -> dict[str, Any]:
    paths = tracked_files(repo_root)

    tree_destination.parent.mkdir(parents=True, exist_ok=True)
    tree_destination.write_text(
        render_tree(paths, root_label=repo_root.name),
        encoding="utf-8",
    )
    tracked_destination.write_text("\n".join(paths) + "\n", encoding="utf-8")

    summary = collect_tree_summary(paths)
    write_json(summary_destination, summary)
    return summary

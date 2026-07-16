from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = ROOT / "tools"

if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from simplee_devkit.common import is_sensitive_path, sanitize_remote_url
from simplee_devkit.export_repo_tree import render_tree


def test_remote_url_credentials_are_removed() -> None:
    value = "https://x-access-token:secret-value@github.com/example/repo.git"
    assert sanitize_remote_url(value) == "https://github.com/example/repo.git"


def test_sensitive_paths_are_excluded() -> None:
    assert is_sensitive_path(".env") is True
    assert is_sensitive_path("config/.env.production") is True
    assert is_sensitive_path("certs/private.key") is True
    assert is_sensitive_path("tower/data/users_secure.json") is True
    assert is_sensitive_path("tower/tower_human_login_ob_launch.py") is False


def test_repository_tree_renderer_is_stable() -> None:
    tree = render_tree(
        [
            "tests/test_alpha.py",
            "tools/exporter.py",
            "tools/pkg/common.py",
        ],
        root_label="repo",
    )
    assert tree.startswith("repo\n")
    assert "├── tests" in tree
    assert "└── tools" in tree
    assert "common.py" in tree


def test_context_exporter_smoke(tmp_path: Path) -> None:
    command = [
        sys.executable,
        str(ROOT / "tools" / "export_chatgpt_context.py"),
        "--repo",
        str(ROOT),
        "--output-root",
        str(tmp_path),
        "--mode",
        "focused",
        "--checkpoint-limit",
        "1",
        "--recent-commit-limit",
        "2",
        "--max-file-bytes",
        str(256 * 1024),
        "--max-total-bytes",
        str(6 * 1024 * 1024),
        "--keep-directory",
    ]

    result = subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
        timeout=240,
    )

    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    zip_paths = sorted(tmp_path.glob("simplee_context_*.zip"))
    directories = sorted(path for path in tmp_path.glob("simplee_context_*") if path.is_dir())
    assert len(zip_paths) == 1
    assert len(directories) == 1

    context_directory = directories[0]
    summary = json.loads((context_directory / "export_summary.json").read_text())
    manifest = json.loads((context_directory / "source_manifest.json").read_text())

    assert summary["branch"]
    assert summary["head"]
    assert summary["tracked_file_count"] > 0
    assert manifest["included_file_count"] > 0
    assert (context_directory / "AI_HANDOFF.md").exists()
    assert (context_directory / "git_context.json").exists()
    assert (context_directory / "repository_tree.txt").exists()

    with zipfile.ZipFile(zip_paths[0]) as archive:
        names = set(archive.namelist())

    assert "AI_HANDOFF.md" in names
    assert "git_context.json" in names
    assert not any(name.startswith(".git/") for name in names)
    assert not any(name.startswith("data/") for name in names)
    assert not any(name.startswith("data_v2/") for name in names)
    assert not any(name.startswith("tower/data/") for name in names)
    assert not any(name.endswith("users_secure.json") for name in names)

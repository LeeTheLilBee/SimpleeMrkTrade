from __future__ import annotations

import os
from pathlib import Path


START_SCRIPT = Path("deploy/hosted_tower/start.sh")


def test_managed_staging_start_script_exists():
    assert START_SCRIPT.is_file()


def test_managed_staging_start_script_is_executable():
    assert os.access(START_SCRIPT, os.X_OK)


def test_managed_staging_start_script_uses_python_module_gunicorn_and_render_port():
    text = START_SCRIPT.read_text(encoding="utf-8")

    assert "python" in text.lower()
    assert "-m gunicorn" in text
    assert '${PORT:-10000}' in text
    assert "0.0.0.0" in text
    assert "web.hosted_tower:app" in text


def test_managed_staging_start_script_has_strict_shell_mode():
    text = START_SCRIPT.read_text(encoding="utf-8")

    assert "set -euo pipefail" in text

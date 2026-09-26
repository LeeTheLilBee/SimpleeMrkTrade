"""TWR198: fail closed when process-local handoff storage would cross workers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

START = Path(__file__).resolve().parents[1] / "deploy" / "hosted_tower" / "start.sh"


def run_start(worker_value):
    env = os.environ.copy()
    env["PYTHON_BIN"] = "/bin/echo"
    env["PORT"] = "10000"
    if worker_value is None:
        env.pop("WEB_CONCURRENCY", None)
    else:
        env["WEB_CONCURRENCY"] = worker_value
    return subprocess.run(
        ["bash", str(START)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("workers", [None, "1"])
def test_twr198_single_worker_starts_without_launching_app(workers):
    result = run_start(workers)
    assert result.returncode == 0
    assert "--workers 1" in result.stdout
    assert "web.hosted_tower:app" in result.stdout
    assert "denied" not in result.stderr


@pytest.mark.parametrize("workers", ["2", "3", "0", "-1", "abc", "1 2", " 1 ", ""])
def test_twr198_unsafe_worker_configuration_fails_before_launch(workers):
    # An empty variable is interpreted as an intentional empty configuration;
    # it must not silently turn into a second process.
    result = run_start(workers)
    if workers == "":
        # Shell's ${WEB_CONCURRENCY:-1} retains its historical default.
        assert result.returncode == 0
        assert "--workers 1" in result.stdout
        return
    assert result.returncode == 64
    assert result.stdout == ""
    assert "WEB_CONCURRENCY must be 1" in result.stderr
    assert "gunicorn" not in result.stdout


def test_twr198_source_has_process_local_handoff_store():
    source = (
        Path(__file__).resolve().parents[1] / "tower" / "owner_teller_handoff.py"
    ).read_text(encoding="utf-8")
    assert "_HANDOFF_STORE" in source
    assert "_STORE_LOCK" in source

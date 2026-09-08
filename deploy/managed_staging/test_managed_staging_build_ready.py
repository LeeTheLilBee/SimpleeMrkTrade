from __future__ import annotations

from pathlib import Path


def test_render_managed_staging_requirements_file_exists():
    path = Path("deploy/hosted_tower/requirements.txt")
    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "Flask" in text
    assert "gunicorn" in text
    assert "pandas" in text
    assert "numpy" in text
    assert "yfinance" in text


def test_render_managed_staging_entrypoint_file_exists():
    path = Path("web/hosted_tower.py")
    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "web.hosted_tower:app" in text
    assert "HOSTED_READY = False" in text
    assert "BROKER_SUBMISSION = False" in text
    assert "CAPITAL_MOVEMENT = False" in text

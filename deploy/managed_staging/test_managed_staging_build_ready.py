from __future__ import annotations

from pathlib import Path


def test_render_managed_staging_requirements_file_exists():
    path = Path("deploy/managed_staging/requirements.txt")
    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "Flask" in text
    assert "gunicorn" in text
    assert "pandas" in text
    assert "numpy" in text
    assert "yfinance" in text


def test_render_managed_staging_entrypoint_file_exists():
    path = Path("web/managed_staging.py")
    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "web.managed_staging:app" in text
    assert "STAGING_READY = False" in text
    assert "BROKER_SUBMISSION = False" in text
    assert "CAPITAL_MOVEMENT = False" in text

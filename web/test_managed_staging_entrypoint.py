from __future__ import annotations


def test_managed_staging_imports_canonical_app():
    from web import app as web_app
    from web.managed_staging import app, managed_staging_status

    assert app is web_app.app

    status = managed_staging_status()

    assert status["entrypoint"] == "web.managed_staging:app"
    assert status["app_imported"] is True
    assert status["production_deployment"] is False
    assert status["broker_submission"] is False
    assert status["capital_movement"] is False
    assert status["manual_live_authorized"] is False
    assert status["live_auto_authorized"] is False
    assert status["staging_ready"] is False

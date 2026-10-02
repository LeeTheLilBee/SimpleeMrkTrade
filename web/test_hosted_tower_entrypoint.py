def test_hosted_entrypoint_imports_canonical_app():
    from web import app as web_app

    from web.hosted_tower import (
        app,
        hosted_tower_status,
    )

    assert app is web_app.app

    payload = hosted_tower_status()

    assert (
        payload["entrypoint"]
        == "web.hosted_tower:app"
    )

    assert payload["app_imported"] is True
    assert payload["production_deployment"] is False
    assert payload["broker_submission"] is False
    assert payload["capital_movement"] is False
    assert payload["manual_live_authorized"] is False
    assert payload["live_auto_authorized"] is False

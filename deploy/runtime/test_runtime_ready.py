from pathlib import Path

from web.runtime import (
    RUNTIME_ENTRYPOINT,
    app,
    canonical_runtime_status,
)


def test_runtime_identity_is_environment_neutral():
    assert (
        RUNTIME_ENTRYPOINT
        == "web.runtime:app"
    )

    payload = (
        canonical_runtime_status()
    )

    assert (
        payload["runtime_class"]
        == "canonical_hosted_runtime"
    )

    assert (
        payload["broker_submission"]
        is False
    )

    assert (
        payload["capital_movement"]
        is False
    )

    assert (
        payload["manual_live_authorized"]
        is False
    )

    assert (
        payload["live_auto_authorized"]
        is False
    )


def test_runtime_health_is_anonymous_and_minimal():
    client = app.test_client()

    response = client.get(
        "/tower/healthz"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.get_json()
        == {
            "ok": True,
            "runtime": "simplee-world",
        }
    )

    assert (
        response.headers.get(
            "Cache-Control"
        )
        == "no-store"
    )


def test_runtime_start_script_uses_canonical_entrypoint():
    path = Path(
        "deploy/runtime/start.sh"
    )

    assert path.exists()

    text = path.read_text(
        encoding="utf-8"
    )

    assert (
        "web.runtime:app"
        in text
    )

    assert (
        "managed_staging"
        not in text
    )


def test_runtime_requirements_are_present():
    path = Path(
        "deploy/runtime/requirements.txt"
    )

    assert path.exists()

    text = path.read_text(
        encoding="utf-8"
    )

    assert "Flask" in text
    assert "gunicorn" in text
    assert "pandas" in text
    assert "numpy" in text

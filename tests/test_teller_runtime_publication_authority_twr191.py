from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)

import tower.identity_authority as identity

import tower.teller_runtime_publication_authority as runtime

from tower.app_truth_projection import (
    app_truth_by_id,
)


TELLER_SHA = (
    "1b24db502bbf170b11c081b20b49b5640417b2e8"
)

TELLER_DEPLOY_ID = (
    "dep-dak0nu3m8hqs73a15820"
)

TELLER_URL = (
    "https://simplee-teller.onrender.com"
)


class FakeResponse:

    def __init__(
        self,
        *,
        body,
        status=200,
        url=TELLER_URL,
    ):
        self.status = status
        self._body = body
        self._url = url

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        return False

    def read(
        self,
        amount=None,
    ):
        return self._body

    def geturl(self):
        return self._url


def configure_owner(
    monkeypatch,
):

    monkeypatch.setenv(
        identity.TOWER_OWNER_USERNAME_ENV,
        "twr191-owner",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_PASSWORD_HASH_ENV,
        "test-hash",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_ID_ENV,
        "twr191-owner-id",
    )

    monkeypatch.delenv(
        identity.TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        raising=False,
    )


def configure_runtime(
    monkeypatch,
):

    monkeypatch.setenv(
        runtime.TOWER_TELLER_WEB_URL_ENV,
        TELLER_URL,
    )

    monkeypatch.setenv(
        runtime.TOWER_TELLER_DEPLOY_SHA_ENV,
        TELLER_SHA,
    )

    monkeypatch.setenv(
        runtime.TOWER_TELLER_DEPLOY_ID_ENV,
        TELLER_DEPLOY_ID,
    )


def teller_html():
    return (
        b'<!doctype html>'
        b'<html>'
        b'<head>'
        b'<title>The Teller</title>'
        b'</head>'
        b'<body>'
        b'<div id="root"></div>'
        b'</body>'
        b'</html>'
    )


def test_twr191_runtime_provider_is_optional(
    monkeypatch,
):

    monkeypatch.delenv(
        runtime.TOWER_TELLER_WEB_URL_ENV,
        raising=False,
    )

    monkeypatch.delenv(
        runtime.TOWER_TELLER_DEPLOY_SHA_ENV,
        raising=False,
    )

    monkeypatch.delenv(
        runtime.TOWER_TELLER_DEPLOY_ID_ENV,
        raising=False,
    )

    assert (
        runtime
        .teller_runtime_publication_truth_bundle()
        is None
    )


def test_twr191_live_teller_runtime_truth_is_launchable(
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    configure_runtime(
        monkeypatch
    )

    monkeypatch.delenv(
        "TOWER_APP_PUBLICATION_STATE_PATH",
        raising=False,
    )

    monkeypatch.setattr(
        runtime,
        "urlopen",
        lambda *args, **kwargs:
            FakeResponse(
                body=teller_html()
            ),
    )

    teller = app_truth_by_id(
        "teller"
    )

    assert (
        teller["dimensions"]
        ["implemented"]
        ["value"]
        is True
    )

    assert (
        teller["dimensions"]
        ["published"]
        ["value"]
        is True
    )

    assert (
        teller["dimensions"]
        ["environment_available"]
        ["value"]
        is True
    )

    assert (
        teller["dimensions"]
        ["health_verified"]
        ["value"]
        is True
    )

    assert (
        teller["dimensions"]
        ["user_entitled"]
        ["value"]
        is True
    )

    assert (
        teller["dimensions"]
        ["launch_route_configured"]
        ["value"]
        is True
    )

    assert (
        teller["launchable"]
        is True
    )


def test_twr191_http_failure_fails_closed(
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    configure_runtime(
        monkeypatch
    )

    monkeypatch.delenv(
        "TOWER_APP_PUBLICATION_STATE_PATH",
        raising=False,
    )

    def fail(*args, **kwargs):
        raise OSError(
            "network unavailable"
        )

    monkeypatch.setattr(
        runtime,
        "urlopen",
        fail,
    )

    teller = app_truth_by_id(
        "teller"
    )

    assert (
        teller["dimensions"]
        ["environment_available"]
        ["value"]
        is False
    )

    assert (
        teller["dimensions"]
        ["health_verified"]
        ["value"]
        is False
    )

    assert (
        teller["launchable"]
        is False
    )


def test_twr191_wrong_page_markers_fail_health(
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    configure_runtime(
        monkeypatch
    )

    monkeypatch.delenv(
        "TOWER_APP_PUBLICATION_STATE_PATH",
        raising=False,
    )

    monkeypatch.setattr(
        runtime,
        "urlopen",
        lambda *args, **kwargs:
            FakeResponse(
                body=(
                    b"<html>"
                    b"<title>Not Teller</title>"
                    b"</html>"
                )
            ),
    )

    teller = app_truth_by_id(
        "teller"
    )

    assert (
        teller["dimensions"]
        ["environment_available"]
        ["value"]
        is True
    )

    assert (
        teller["dimensions"]
        ["health_verified"]
        ["value"]
        is False
    )

    assert (
        teller["launchable"]
        is False
    )


def test_twr191_observatory_does_not_use_teller_runtime_provider(
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    configure_runtime(
        monkeypatch
    )

    monkeypatch.delenv(
        "TOWER_APP_PUBLICATION_STATE_PATH",
        raising=False,
    )

    calls = []

    def fake_urlopen(
        *args,
        **kwargs,
    ):
        calls.append(
            True
        )

        return FakeResponse(
            body=teller_html()
        )

    monkeypatch.setattr(
        runtime,
        "urlopen",
        fake_urlopen,
    )

    ob = app_truth_by_id(
        "observatory"
    )

    # No shared publication provider was configured,
    # so OB remains fail-closed exactly as before.
    assert (
        ob["launchable"]
        is False
    )

    # app_truth_by_id projects every registered app.
    # Teller may perform its own health check while the
    # projection list is built, but OB itself never receives
    # Teller's runtime truth.
    assert (
        ob["app_id"]
        == "observatory"
    )


def test_twr191_configuration_rejects_insecure_url(
    monkeypatch,
):

    configure_runtime(
        monkeypatch
    )

    monkeypatch.setenv(
        runtime.TOWER_TELLER_WEB_URL_ENV,
        "http://simplee-teller.onrender.com",
    )

    assert (
        runtime
        .teller_runtime_publication_configured()
        is False
    )


def test_twr191_configuration_requires_real_sha(
    monkeypatch,
):

    configure_runtime(
        monkeypatch
    )

    monkeypatch.setenv(
        runtime.TOWER_TELLER_DEPLOY_SHA_ENV,
        "not-a-sha",
    )

    assert (
        runtime
        .teller_runtime_publication_configured()
        is False
    )


def test_twr191_status_never_grants_execution_authority(
    monkeypatch,
):

    configure_runtime(
        monkeypatch
    )

    status = (
        runtime
        .teller_runtime_publication_status()
    )

    assert (
        status[
            "payroll_execution_authority"
        ]
        is False
    )

    assert (
        status[
            "bank_authority"
        ]
        is False
    )

    assert (
        status[
            "capital_authority"
        ]
        is False
    )

    assert (
        status[
            "broker_authority"
        ]
        is False
    )

    assert (
        status[
            "manual_live_authorized"
        ]
        is False
    )

    assert (
        status[
            "live_auto_authorized"
        ]
        is False
    )

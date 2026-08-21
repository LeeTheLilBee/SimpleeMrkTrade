from __future__ import annotations

import json
from urllib.parse import urlsplit

import pytest

from tower.hosted_runtime_parity import (
    EXPECTED_ENTRYPOINT,
    evaluate_hosted_runtime_parity,
    normalize_base_url,
    probe_hosted_runtime,
)


REVISION = (
    "aaaaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaa"
)


def _manifest(
    *,
    revision=REVISION,
    routes=True,
    **overrides,
):
    payload = {
        "status": (
            "tower_managed_staging_"
            "runtime_manifest_ready"
        ),
        "entrypoint": (
            EXPECTED_ENTRYPOINT
        ),
        "revision": revision,
        "revision_source": (
            "environment:RENDER_GIT_COMMIT"
        ),
        "critical_routes": {
            "tower_login": routes,
            "tower_owner_dashboard": routes,
            "tower_security_map": routes,
            (
                "archive_vault_"
                "acceptance_records"
            ): routes,
            "archive_vault_intake": routes,
            (
                "person_archive_"
                "vault_queue"
            ): routes,
            "ob_dashboard": routes,
            "ob_market_map": routes,
            "ob_trade_center": routes,
            "ob_review_center": routes,
            "ob_owner_console": routes,
        },
        "critical_routes_present": routes,
        "production_deployment": False,
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "staging_ready": False,
    }

    payload.update(
        overrides
    )

    return payload


def _probe(
    path,
    *,
    status=200,
    revision=REVISION,
):
    return {
        "path": path,
        "status": status,
        "headers": {
            "X-Simplee-Entrypoint": (
                EXPECTED_ENTRYPOINT
            ),
            "X-Simplee-Revision": revision,
            (
                "X-Simplee-"
                "Revision-Source"
            ): (
                "environment:"
                "RENDER_GIT_COMMIT"
            ),
        },
        "body": "",
        "error": None,
    }


def _probes(
    *,
    revision=REVISION,
):
    return {
        "/tower/healthz": (
            _probe(
                "/tower/healthz",
                revision=revision,
            )
        ),
        "/tower/runtime-manifest.json": (
            _probe(
                "/tower/runtime-manifest.json",
                revision=revision,
            )
        ),
        "/tower/login": (
            _probe(
                "/tower/login",
                revision=revision,
            )
        ),
    }


def test_https_required_by_default():
    with pytest.raises(
        ValueError
    ):
        normalize_base_url(
            "http://example.test"
        )


def test_http_must_be_explicit():
    assert (
        normalize_base_url(
            "http://127.0.0.1:5000",
            allow_http=True,
        )
        == "http://127.0.0.1:5000"
    )


def test_embedded_credentials_rejected():
    with pytest.raises(
        ValueError
    ):
        normalize_base_url(
            (
                "https://user:password"
                "@example.test"
            )
        )


def test_query_and_fragment_rejected():
    with pytest.raises(
        ValueError
    ):
        normalize_base_url(
            "https://example.test/?token=x"
        )

    with pytest.raises(
        ValueError
    ):
        normalize_base_url(
            "https://example.test/#secret"
        )


def test_exact_candidate_parity_passes():
    result = (
        evaluate_hosted_runtime_parity(
            expected_revision=REVISION,
            probes=_probes(),
            manifest=_manifest(),
        )
    )

    assert (
        result[
            "parity_pass"
        ]
        is True
    )

    assert (
        result[
            "status"
        ]
        == (
            "tower_hosted_candidate_"
            "parity_pass"
        )
    )

    assert not (
        result[
            "failures"
        ]
    )


def test_revision_mismatch_fails_closed():
    result = (
        evaluate_hosted_runtime_parity(
            expected_revision=(
                "bbbbbbbbbbbbbbbbbbbb"
                "bbbbbbbbbbbbbbbbbbbb"
            ),
            probes=_probes(),
            manifest=_manifest(),
        )
    )

    assert (
        result[
            "parity_pass"
        ]
        is False
    )

    assert (
        result[
            "checks"
        ][
            "exact_candidate_revision_match"
        ]
        is False
    )


def test_unknown_expected_revision_fails():
    result = (
        evaluate_hosted_runtime_parity(
            expected_revision="unknown",
            probes=_probes(),
            manifest=_manifest(),
        )
    )

    assert (
        result[
            "parity_pass"
        ]
        is False
    )

    assert (
        result[
            "checks"
        ][
            "expected_revision_valid"
        ]
        is False
    )


def test_header_revision_inconsistency_fails():
    probes = (
        _probes()
    )

    probes[
        "/tower/login"
    ][
        "headers"
    ][
        "X-Simplee-Revision"
    ] = (
        "cccccccccccccccccccc"
        "cccccccccccccccccccc"
    )

    result = (
        evaluate_hosted_runtime_parity(
            expected_revision=REVISION,
            probes=probes,
            manifest=_manifest(),
        )
    )

    assert (
        result[
            "checks"
        ][
            "revision_headers_consistent"
        ]
        is False
    )

    assert (
        result[
            "parity_pass"
        ]
        is False
    )


def test_wrong_entrypoint_fails():
    manifest = (
        _manifest()
    )

    manifest[
        "entrypoint"
    ] = "web.other:app"

    result = (
        evaluate_hosted_runtime_parity(
            expected_revision=REVISION,
            probes=_probes(),
            manifest=manifest,
        )
    )

    assert (
        result[
            "checks"
        ][
            "manifest_entrypoint"
        ]
        is False
    )


def test_missing_critical_route_fails():
    manifest = (
        _manifest()
    )

    manifest[
        "critical_routes"
    ][
        "archive_vault_intake"
    ] = False

    manifest[
        "critical_routes_present"
    ] = False

    result = (
        evaluate_hosted_runtime_parity(
            expected_revision=REVISION,
            probes=_probes(),
            manifest=manifest,
        )
    )

    assert (
        result[
            "checks"
        ][
            "all_critical_routes_present"
        ]
        is False
    )

    assert (
        result[
            "parity_pass"
        ]
        is False
    )


@pytest.mark.parametrize(
    "field",
    [
        "production_deployment",
        "broker_submission",
        "capital_movement",
        "manual_live_authorized",
        "live_auto_authorized",
        "staging_ready",
    ],
)
def test_every_safety_flag_fails_closed(
    field,
):
    manifest = (
        _manifest()
    )

    manifest[
        field
    ] = True

    result = (
        evaluate_hosted_runtime_parity(
            expected_revision=REVISION,
            probes=_probes(),
            manifest=manifest,
        )
    )

    assert (
        result[
            "parity_pass"
        ]
        is False
    )

    assert (
        result[
            "checks"
        ][
            f"safety_{field}_false"
        ]
        is False
    )


def test_probe_client_sends_no_credentials():
    seen = []


    class FakeResponse:
        def __init__(
            self,
            *,
            status,
            headers,
            body,
        ):
            self.status = status
            self.headers = headers
            self._body = body

        def read(self):
            return self._body

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return False


    manifest_body = (
        json.dumps(
            _manifest()
        )
        .encode(
            "utf-8"
        )
    )


    def opener(
        request,
        timeout,
    ):
        headers = {
            key.lower(): value
            for key, value
            in request.header_items()
        }

        assert (
            "authorization"
            not in headers
        )

        assert (
            "cookie"
            not in headers
        )

        path = (
            urlsplit(
                request.full_url
            )
            .path
        )

        seen.append(
            path
        )

        body = (
            manifest_body
            if path
            == "/tower/runtime-manifest.json"
            else b"ok"
        )

        return FakeResponse(
            status=200,
            headers={
                "X-Simplee-Entrypoint": (
                    EXPECTED_ENTRYPOINT
                ),
                "X-Simplee-Revision": (
                    REVISION
                ),
                (
                    "X-Simplee-"
                    "Revision-Source"
                ): (
                    "environment:"
                    "RENDER_GIT_COMMIT"
                ),
            },
            body=body,
        )


    result = (
        probe_hosted_runtime(
            base_url=(
                "https://example.test"
            ),
            expected_revision=REVISION,
            opener=opener,
        )
    )

    assert seen == [
        "/tower/healthz",
        "/tower/runtime-manifest.json",
        "/tower/login",
    ]

    assert (
        result[
            "parity_pass"
        ]
        is True
    )


def test_result_never_authorizes_live_actions():
    result = (
        evaluate_hosted_runtime_parity(
            expected_revision=REVISION,
            probes=_probes(),
            manifest=_manifest(),
        )
    )

    assert (
        result[
            "deployment_authorized"
        ]
        is False
    )

    assert (
        result[
            "production_promotion_authorized"
        ]
        is False
    )

    assert (
        result[
            "broker_submission_authorized"
        ]
        is False
    )

    assert (
        result[
            "capital_movement_authorized"
        ]
        is False
    )

    assert (
        result[
            "manual_live_authorized"
        ]
        is False
    )

    assert (
        result[
            "live_auto_authorized"
        ]
        is False
    )

    assert (
        result[
            "staging_ready_changed"
        ]
        is False
    )

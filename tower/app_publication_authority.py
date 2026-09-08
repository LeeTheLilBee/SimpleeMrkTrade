"""Authoritative Tower app publication / availability provider.

TWR141-TWR145.

The Tower app registry proves registration and route metadata only.

This provider is deliberately separate. It can prove:
- implementation,
- publication,
- current environment availability,
- current health.

It does not create user entitlement.
It does not authorize a request.
It does not enable dangerous actions.
It does not expose the configured provider path.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tower.app_registry import app_ids
from tower.truth_contract import (
    AUTHORITATIVE,
    NOT_CONFIGURED,
    UNAVAILABLE,
    UNVERIFIED,
    VERIFIED,
    TowerTruthEnvelope,
    not_configured_truth,
    unavailable_truth,
    verified_truth,
)


TOWER_APP_PUBLICATION_STATE_PATH_ENV = (
    "TOWER_APP_PUBLICATION_STATE_PATH"
)

APP_PUBLICATION_SCHEMA_VERSION = (
    "tower.app-publication-authority.v1"
)

APP_PUBLICATION_SOURCE_ID = (
    "tower.app_publication_authority"
)

IMPLEMENTED = "implemented"
PUBLISHED = "published"
ENVIRONMENT_AVAILABLE = "environment_available"
HEALTH_VERIFIED = "health_verified"

APP_PUBLICATION_DIMENSIONS = (
    IMPLEMENTED,
    PUBLISHED,
    ENVIRONMENT_AVAILABLE,
    HEALTH_VERIFIED,
)

TEMPORAL_DIMENSIONS = frozenset({
    ENVIRONMENT_AVAILABLE,
    HEALTH_VERIFIED,
})


class AppPublicationAuthorityError(ValueError):
    """Invalid app publication authority state."""


def _clean(value: Any) -> str:
    return str(
        value
        if value is not None
        else ""
    ).strip()


def _provider_path() -> Path | None:

    raw = _clean(
        os.environ.get(
            TOWER_APP_PUBLICATION_STATE_PATH_ENV,
            "",
        )
    )

    if not raw:
        return None

    return Path(raw)


def _canonical_payload(
    document: Mapping[str, Any],
) -> dict[str, Any]:

    return {
        "schema_version":
            document.get("schema_version"),

        "apps":
            document.get("apps"),
    }


def canonical_publication_payload_bytes(
    document: Mapping[str, Any],
) -> bytes:

    payload = _canonical_payload(
        document
    )

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )


def publication_integrity_sha256(
    document: Mapping[str, Any],
) -> str:

    return hashlib.sha256(
        canonical_publication_payload_bytes(
            document
        )
    ).hexdigest()


def publication_document(
    apps: Mapping[str, Any],
) -> dict[str, Any]:
    """Convenience constructor used by authority producers/tests."""

    document = {
        "schema_version":
            APP_PUBLICATION_SCHEMA_VERSION,

        "apps":
            dict(apps),
    }

    document["integrity_sha256"] = (
        publication_integrity_sha256(
            document
        )
    )

    return document


def _parse_aware_timestamp(
    value: Any,
    *,
    field_name: str,
) -> datetime:

    text = _clean(
        value
    )

    if not text:
        raise AppPublicationAuthorityError(
            f"{field_name} is required."
        )

    candidate = text

    if candidate.endswith("Z"):
        candidate = (
            candidate[:-1]
            + "+00:00"
        )

    try:
        parsed = datetime.fromisoformat(
            candidate
        )
    except ValueError as exc:
        raise AppPublicationAuthorityError(
            f"{field_name} must be ISO-8601."
        ) from exc

    if parsed.tzinfo is None:
        raise AppPublicationAuthorityError(
            f"{field_name} must be timezone-aware."
        )

    return parsed.astimezone(
        timezone.utc
    )


def _validate_boolean_dimension(
    *,
    app_id: str,
    dimension: str,
    record: Any,
) -> None:

    if not isinstance(
        record,
        Mapping,
    ):
        raise AppPublicationAuthorityError(
            f"{app_id}.{dimension} must be an object."
        )

    if "value" not in record:
        raise AppPublicationAuthorityError(
            f"{app_id}.{dimension}.value is required."
        )

    if type(
        record["value"]
    ) is not bool:
        raise AppPublicationAuthorityError(
            f"{app_id}.{dimension}.value must be boolean."
        )


def _validate_static_dimension(
    *,
    app_id: str,
    dimension: str,
    record: Mapping[str, Any],
) -> None:

    _validate_boolean_dimension(
        app_id=app_id,
        dimension=dimension,
        record=record,
    )

    if not _clean(
        record.get(
            "evidence_id"
        )
    ):
        raise AppPublicationAuthorityError(
            f"{app_id}.{dimension}.evidence_id is required."
        )


def _validate_temporal_dimension(
    *,
    app_id: str,
    dimension: str,
    record: Mapping[str, Any],
) -> None:

    _validate_boolean_dimension(
        app_id=app_id,
        dimension=dimension,
        record=record,
    )

    if not _clean(
        record.get(
            "receipt_id"
        )
    ):
        raise AppPublicationAuthorityError(
            f"{app_id}.{dimension}.receipt_id is required."
        )

    observed = _parse_aware_timestamp(
        record.get(
            "observed_at_utc"
        ),
        field_name=(
            f"{app_id}.{dimension}.observed_at_utc"
        ),
    )

    fresh_until = _parse_aware_timestamp(
        record.get(
            "fresh_until_utc"
        ),
        field_name=(
            f"{app_id}.{dimension}.fresh_until_utc"
        ),
    )

    if fresh_until < observed:
        raise AppPublicationAuthorityError(
            f"{app_id}.{dimension}.fresh_until_utc "
            "cannot precede observed_at_utc."
        )


def validate_publication_document(
    document: Any,
) -> dict[str, Any]:

    if not isinstance(
        document,
        Mapping,
    ):
        raise AppPublicationAuthorityError(
            "Publication authority document must be an object."
        )

    if document.get(
        "schema_version"
    ) != APP_PUBLICATION_SCHEMA_VERSION:
        raise AppPublicationAuthorityError(
            "Unsupported app publication authority schema."
        )

    apps = document.get(
        "apps"
    )

    if not isinstance(
        apps,
        Mapping,
    ):
        raise AppPublicationAuthorityError(
            "Publication authority apps must be an object."
        )

    known = set(
        app_ids()
    )

    for app_id, record in apps.items():

        if app_id not in known:
            raise AppPublicationAuthorityError(
                "Unknown app IDs are not allowed."
            )

        if not isinstance(
            record,
            Mapping,
        ):
            raise AppPublicationAuthorityError(
                f"App publication record must be an object: {app_id}"
            )

        if _clean(
            record.get(
                "app_id"
            )
        ) != app_id:
            raise AppPublicationAuthorityError(
                f"App publication record ID mismatch: {app_id}"
            )

        for dimension in (
            IMPLEMENTED,
            PUBLISHED,
        ):
            _validate_static_dimension(
                app_id=app_id,
                dimension=dimension,
                record=record.get(
                    dimension
                ),
            )

        for dimension in (
            ENVIRONMENT_AVAILABLE,
            HEALTH_VERIFIED,
        ):
            _validate_temporal_dimension(
                app_id=app_id,
                dimension=dimension,
                record=record.get(
                    dimension
                ),
            )

    supplied_integrity = _clean(
        document.get(
            "integrity_sha256"
        )
    )

    if not supplied_integrity:
        raise AppPublicationAuthorityError(
            "Publication authority integrity hash is required."
        )

    expected_integrity = (
        publication_integrity_sha256(
            document
        )
    )

    if not hmac.compare_digest(
        supplied_integrity,
        expected_integrity,
    ):
        raise AppPublicationAuthorityError(
            "Publication authority integrity verification failed."
        )

    return {
        "schema_version":
            APP_PUBLICATION_SCHEMA_VERSION,

        "apps":
            {
                str(app_id):
                    dict(record)
                for app_id, record
                in apps.items()
            },

        "integrity_sha256":
            supplied_integrity,
    }


def app_publication_authority_snapshot(
) -> dict[str, Any]:

    path = _provider_path()

    if path is None:
        return {
            "status":
                "tower_app_publication_authority_not_configured",

            "configured":
                False,

            "verification_state":
                NOT_CONFIGURED,

            "reason":
                "app_publication_authority_provider_not_configured",

            "schema_version":
                APP_PUBLICATION_SCHEMA_VERSION,

            "apps":
                None,

            "provider_path_exposed":
                False,
        }

    try:
        source = path.read_text(
            encoding="utf-8"
        )

        document = json.loads(
            source
        )

        validated = (
            validate_publication_document(
                document
            )
        )

    except Exception:
        return {
            "status":
                "tower_app_publication_authority_unverified",

            "configured":
                True,

            "verification_state":
                UNVERIFIED,

            "reason":
                "app_publication_authority_validation_failed",

            "schema_version":
                APP_PUBLICATION_SCHEMA_VERSION,

            "apps":
                None,

            "provider_path_exposed":
                False,
        }

    return {
        "status":
            "tower_app_publication_authority_verified",

        "configured":
            True,

        "verification_state":
            VERIFIED,

        "reason":
            "integrity_verified_app_publication_authority",

        "schema_version":
            validated[
                "schema_version"
            ],

        "apps":
            validated[
                "apps"
            ],

        "integrity_sha256":
            validated[
                "integrity_sha256"
            ],

        "provider_path_exposed":
            False,
    }


def app_publication_record(
    app_id: str,
    *,
    snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:

    normalized = _clean(
        app_id
    )

    if normalized not in set(
        app_ids()
    ):
        raise AppPublicationAuthorityError(
            "Unknown Tower app ID."
        )

    authority = (
        dict(snapshot)
        if snapshot is not None
        else app_publication_authority_snapshot()
    )

    if authority.get(
        "verification_state"
    ) != VERIFIED:
        return None

    apps = authority.get(
        "apps"
    )

    if not isinstance(
        apps,
        Mapping,
    ):
        return None

    record = apps.get(
        normalized
    )

    if record is None:
        return None

    return dict(
        record
    )


def publication_authority_configured_truth(
    *,
    snapshot: Mapping[str, Any] | None = None,
) -> TowerTruthEnvelope:

    authority = (
        dict(snapshot)
        if snapshot is not None
        else app_publication_authority_snapshot()
    )

    state = authority.get(
        "verification_state"
    )

    if state == NOT_CONFIGURED:
        return not_configured_truth(
            source_id=APP_PUBLICATION_SOURCE_ID,
            reason=(
                "app_publication_authority_provider_not_configured"
            ),
        )

    if state != VERIFIED:
        return unavailable_truth(
            source_id=APP_PUBLICATION_SOURCE_ID,
            reason=(
                "configured_app_publication_authority_not_verified"
            ),
        )

    return verified_truth(
        value=True,
        source_id=APP_PUBLICATION_SOURCE_ID,
        source_class=AUTHORITATIVE,
        reason=(
            "app_publication_authority_integrity_verified"
        ),
    )


def app_dimension_truth(
    app_id: str,
    dimension: str,
    *,
    snapshot: Mapping[str, Any] | None = None,
) -> TowerTruthEnvelope:

    normalized_app = _clean(
        app_id
    )

    normalized_dimension = _clean(
        dimension
    )

    if normalized_app not in set(
        app_ids()
    ):
        raise AppPublicationAuthorityError(
            "Unknown Tower app ID."
        )

    if normalized_dimension not in set(
        APP_PUBLICATION_DIMENSIONS
    ):
        raise AppPublicationAuthorityError(
            "Unknown app publication dimension."
        )

    authority = (
        dict(snapshot)
        if snapshot is not None
        else app_publication_authority_snapshot()
    )

    state = authority.get(
        "verification_state"
    )

    source_id = (
        f"{APP_PUBLICATION_SOURCE_ID}:"
        f"{normalized_app}:"
        f"{normalized_dimension}"
    )

    if state == NOT_CONFIGURED:
        return not_configured_truth(
            source_id=source_id,
            reason=(
                "app_publication_authority_provider_not_configured"
            ),
        )

    if state != VERIFIED:
        return unavailable_truth(
            source_id=source_id,
            reason=(
                "configured_app_publication_authority_not_verified"
            ),
        )

    record = app_publication_record(
        normalized_app,
        snapshot=authority,
    )

    if record is None:
        return not_configured_truth(
            source_id=source_id,
            reason=(
                "app_not_configured_in_publication_authority"
            ),
        )

    dimension_record = record[
        normalized_dimension
    ]

    value = dimension_record[
        "value"
    ]

    if normalized_dimension in TEMPORAL_DIMENSIONS:

        return verified_truth(
            value=value,
            source_id=(
                f"{source_id}:"
                f"{dimension_record['receipt_id']}"
            ),
            source_class=AUTHORITATIVE,
            observed_at_utc=(
                dimension_record[
                    "observed_at_utc"
                ]
            ),
            fresh_until_utc=(
                dimension_record[
                    "fresh_until_utc"
                ]
            ),
            reason=(
                f"receipt_verified_{normalized_dimension}"
            ),
        )

    return verified_truth(
        value=value,
        source_id=(
            f"{source_id}:"
            f"{dimension_record['evidence_id']}"
        ),
        source_class=AUTHORITATIVE,
        reason=(
            f"evidence_verified_{normalized_dimension}"
        ),
    )

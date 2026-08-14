"""
GP071 — Source-owned Clouds summary publisher.

This publisher exposes only the compact approved Clouds summary
contract.

It does not expose raw source internals.
It does not contact Clouds.
It does not persist signing secret material.
"""

from __future__ import annotations

import hashlib
import hmac
import json


SOURCE_ID = "archive_vault"
SOURCE_LABEL = "Archive Vault"

SOURCE_CONTRACT_VERSION = (
    "archive-vault-clouds-summary-v1"
)

ADAPTER_ID = (
    "clouds-adapter-archive-vault-v1"
)

TRANSPORT_VERSION = (
    "tower-clouds-signed-summary-v1"
)

SIGNATURE_ALGORITHM = (
    "hmac-sha256"
)

SIGNING_KEY_REF = (
    "tower-secret-ref:clouds-summary-signing/archive_vault/v1"
)


VALID_MODES = {
    "projection",
    "live",
}

VALID_HEALTH = {
    "healthy",
    "watch",
    "attention",
    "blocked",
    "unknown",
}

VALID_READINESS = {
    "ready",
    "building",
    "planning",
    "reserved",
    "blocked",
}

VALID_ATTENTION = {
    "none",
    "informational",
    "review",
    "action_required",
}


def _canonical_json(
    payload,
):

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _normalize_metrics(
    metrics,
):

    normalized = []

    for raw in metrics:

        if not isinstance(
            raw,
            dict,
        ):

            raise TypeError(
                "Clouds summary metric must be a dict."
            )

        item = {

            "metric_id":
            str(
                raw.get(
                    "metric_id",
                    ""
                )
            ).strip(),

            "label":
            str(
                raw.get(
                    "label",
                    ""
                )
            ).strip(),

            "value":
            str(
                raw.get(
                    "value",
                    ""
                )
            ),

            "unit":
            (
                None
                if raw.get(
                    "unit"
                )
                is None

                else
                str(
                    raw.get(
                        "unit"
                    )
                )
            ),

            "explanation":
            str(
                raw.get(
                    "explanation",
                    ""
                )
            ).strip(),
        }


        if not item[
            "metric_id"
        ]:

            raise ValueError(
                "metric_id required"
            )


        if not item[
            "label"
        ]:

            raise ValueError(
                "metric label required"
            )


        if not item[
            "explanation"
        ]:

            raise ValueError(
                "metric explanation required"
            )


        normalized.append(
            item
        )


    return normalized


def build_clouds_summary(
    *,
    source_sequence,
    observed_at,
    health,
    readiness,
    attention,
    headline,
    explanation,
    owner_message,
    metrics=(),
    mode="projection",
    source_claims_live=False,
):

    if (
        not isinstance(
            source_sequence,
            int,
        )
        or source_sequence <= 0
    ):

        raise ValueError(
            "positive source_sequence required"
        )


    if (
        mode
        not in VALID_MODES
    ):

        raise ValueError(
            "invalid mode"
        )


    if (
        health
        not in VALID_HEALTH
    ):

        raise ValueError(
            "invalid health"
        )


    if (
        readiness
        not in VALID_READINESS
    ):

        raise ValueError(
            "invalid readiness"
        )


    if (
        attention
        not in VALID_ATTENTION
    ):

        raise ValueError(
            "invalid attention"
        )


    if (
        mode
        == "projection"

        and source_claims_live
        is not False
    ):

        raise ValueError(
            "projection payload cannot claim live status"
        )


    if (
        mode
        == "live"

        and source_claims_live
        is not True
    ):

        raise ValueError(
            "live mode requires explicit source live claim"
        )


    for field_name, value in {

        "observed_at":
        observed_at,

        "headline":
        headline,

        "explanation":
        explanation,

        "owner_message":
        owner_message,

    }.items():

        if not (
            isinstance(
                value,
                str,
            )
            and value.strip()
        ):

            raise ValueError(
                f"{field_name} required"
            )


    return {

        "source_contract_version":
        SOURCE_CONTRACT_VERSION,

        "feed_id":
        (
            f"{SOURCE_ID}-clouds-"
            f"{source_sequence:08d}"
        ),

        "source_id":
        SOURCE_ID,

        "source_label":
        SOURCE_LABEL,

        "mode":
        mode,

        "source_sequence":
        source_sequence,

        "observed_at":
        observed_at,

        "health":
        health,

        "readiness":
        readiness,

        "attention":
        attention,

        "headline":
        headline,

        "explanation":
        explanation,

        "owner_message":
        owner_message,

        "metrics":
        _normalize_metrics(
            metrics
        ),

        "source_claims_live":
        source_claims_live,
    }


def build_certification_summary(
    *,
    source_sequence,
    observed_at,
):

    return build_clouds_summary(

        source_sequence=(
            source_sequence
        ),

        observed_at=(
            observed_at
        ),

        health="healthy",

        readiness="ready",

        attention="none",

        headline=(
            f"{SOURCE_LABEL} Clouds publisher certification"
        ),

        explanation=(
            "This is a projection-only source-owned "
            "contract certification fixture."
        ),

        owner_message=(
            "This fixture proves publisher compatibility only. "
            "It is not a real live source connection."
        ),

        metrics=(),

        mode="projection",

        source_claims_live=False,
    )


def sign_clouds_summary(
    payload,
    *,
    secret,
    message_id,
    nonce,
    sent_at,
    certification_fixture_only,
):

    if not isinstance(
        secret,
        bytes,
    ):

        raise TypeError(
            "signing secret must be bytes"
        )


    if (
        payload.get(
            "source_id"
        )
        != SOURCE_ID
    ):

        raise ValueError(
            "source ID mismatch"
        )


    if (
        payload.get(
            "source_contract_version"
        )
        != SOURCE_CONTRACT_VERSION
    ):

        raise ValueError(
            "source contract mismatch"
        )


    body_sha256 = (
        hashlib.sha256(
            _canonical_json(
                payload
            ).encode(
                "utf-8"
            )
        ).hexdigest()
    )


    material = {

        "transport_version":
        TRANSPORT_VERSION,

        "source_id":
        SOURCE_ID,

        "source_contract_version":
        SOURCE_CONTRACT_VERSION,

        "message_id":
        message_id,

        "nonce":
        nonce,

        "sent_at":
        sent_at,

        "key_ref":
        SIGNING_KEY_REF,

        "signature_algorithm":
        SIGNATURE_ALGORITHM,

        "body_sha256":
        body_sha256,
    }


    signature_hex = (
        hmac.new(
            secret,
            _canonical_json(
                material
            ).encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).hexdigest()
    )


    return {

        **material,

        "signature_hex":
        signature_hex,

        "certification_fixture_only":
        certification_fixture_only,

        "payload":
        dict(
            payload
        ),
    }


def get_publisher_contract():

    return {

        "source_id":
        SOURCE_ID,

        "source_label":
        SOURCE_LABEL,

        "source_contract_version":
        SOURCE_CONTRACT_VERSION,

        "adapter_id":
        ADAPTER_ID,

        "transport_version":
        TRANSPORT_VERSION,

        "signature_algorithm":
        SIGNATURE_ALGORITHM,

        "signing_key_ref":
        SIGNING_KEY_REF,

        "source_owned_publisher":
        True,

        "raw_source_access_exported":
        False,

        "secret_material_persisted":
        False,

        "clouds_contact_performed":
        False,

        "external_transport_performed":
        False,

        "downstream_execution_performed":
        False,
    }

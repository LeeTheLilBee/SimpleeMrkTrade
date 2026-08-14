"""
GP073 — The Teller source-owned Clouds summary contract.

IMPORTANT
---------
This module is a source-contract bootstrap.

It does not prove that the full operational business system
exists or is connected.

It exposes only the narrow summary boundary expected by Clouds.
"""

from __future__ import annotations

import hashlib
import hmac
import json


SOURCE_ID = (
    "teller"
)

SOURCE_LABEL = (
    "The Teller"
)

SOURCE_CONTRACT_VERSION = (
    "teller-clouds-summary-v1"
)

ADAPTER_ID = (
    "clouds-adapter-teller-v1"
)

TRANSPORT_VERSION = (
    "tower-clouds-signed-summary-v1"
)

SIGNATURE_ALGORITHM = (
    "hmac-sha256"
)

SIGNING_KEY_REF = (
    "tower-secret-ref:clouds-summary-signing/teller/v1"
)

OPERATIONAL_SYSTEM_PREEXISTING = (
    False
)


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


def _canonical_json(payload):

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _normalize_metrics(metrics):

    result = []

    for item in metrics:

        if not isinstance(
            item,
            dict,
        ):
            raise TypeError(
                "Metric must be dict."
            )


        metric = {

            "metric_id":
            str(
                item.get(
                    "metric_id",
                    ""
                )
            ).strip(),

            "label":
            str(
                item.get(
                    "label",
                    ""
                )
            ).strip(),

            "value":
            str(
                item.get(
                    "value",
                    ""
                )
            ),

            "unit":
            (
                None

                if item.get(
                    "unit"
                )
                is None

                else str(
                    item.get(
                        "unit"
                    )
                )
            ),

            "explanation":
            str(
                item.get(
                    "explanation",
                    ""
                )
            ).strip(),
        }


        if not metric[
            "metric_id"
        ]:
            raise ValueError(
                "metric_id required"
            )


        if not metric[
            "label"
        ]:
            raise ValueError(
                "metric label required"
            )


        if not metric[
            "explanation"
        ]:
            raise ValueError(
                "metric explanation required"
            )


        result.append(
            metric
        )


    return result


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
        not in {
            "projection",
            "live",
        }
    ):
        raise ValueError(
            "invalid mode"
        )


    if (
        mode == "projection"
        and source_claims_live
        is not False
    ):
        raise ValueError(
            "Projection summary cannot claim live."
        )


    if (
        mode == "live"
        and source_claims_live
        is not True
    ):
        raise ValueError(
            "Live mode requires explicit live claim."
        )


    for value in (
        observed_at,
        headline,
        explanation,
        owner_message,
    ):

        if not (
            isinstance(
                value,
                str,
            )
            and value.strip()
        ):
            raise ValueError(
                "Required explanation field missing."
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

        health="unknown",

        readiness="planning",

        attention="informational",

        headline=(
            f"{SOURCE_LABEL} Clouds contract certification"
        ),

        explanation=(
            "This is a projection-only contract bootstrap "
            "fixture. It does not represent current operational "
            "business state."
        ),

        owner_message=(
            "Soulaana: I can verify this source contract shape, "
            "but I cannot tell you this business is live or current "
            "until its real operating system is connected."
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
            "secret must be bytes"
        )


    if (
        payload.get(
            "source_id"
        )
        != SOURCE_ID
    ):
        raise ValueError(
            "source mismatch"
        )


    if (
        payload.get(
            "source_contract_version"
        )
        != SOURCE_CONTRACT_VERSION
    ):
        raise ValueError(
            "contract mismatch"
        )


    body_sha256 = (
        hashlib.sha256(
            _canonical_json(
                payload
            )
            .encode(
                "utf-8"
            )
        )
        .hexdigest()
    )


    signature_material = {

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
                signature_material
            )
            .encode(
                "utf-8"
            ),
            hashlib.sha256,
        )
        .hexdigest()
    )


    return {

        **signature_material,

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

        "source_owned_contract_bootstrap":
        True,

        "operational_system_preexisting":
        OPERATIONAL_SYSTEM_PREEXISTING,

        "operational_system_verified":
        False,

        "real_business_data_connected":
        False,

        "source_endpoint_available":
        False,

        "raw_source_access_exported":
        False,

        "secret_material_persisted":
        False,

        "clouds_contact_performed":
        False,

        "external_transport_performed":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,
    }

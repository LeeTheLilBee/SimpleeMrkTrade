"""
GP066 — Signed summary transport /
authenticity + replay gate.

Secret bytes are supplied by the caller and are never persisted.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import hmac
import json

try:

    from .tower_clouds_feed_source_trust_service import (
        get_clouds_feed_source_trust_spec,
        get_clouds_gp065_status_payload,
    )

    from .tower_clouds_signed_summary_transport import (
        SignedSummaryTransportEnvelope,
        SignedSummaryTransportValidation,
    )

except ImportError:

    from tower_clouds_feed_source_trust_service import (
        get_clouds_feed_source_trust_spec,
        get_clouds_gp065_status_payload,
    )

    from tower_clouds_signed_summary_transport import (
        SignedSummaryTransportEnvelope,
        SignedSummaryTransportValidation,
    )


TRANSPORT_VERSION = (
    "tower-clouds-signed-summary-v1"
)


SIGNATURE_ALGORITHM = (
    "hmac-sha256"
)


CERTIFICATION_SECRET = (
    b"gp066-certification-only-"
    b"not-a-production-secret"
)


def _canonical_json(
    payload,
):

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _sha256_json(
    payload,
):

    return hashlib.sha256(
        _canonical_json(
            payload
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _signature_material(
    envelope,
):

    return {

        "transport_version":
        envelope.transport_version,

        "source_id":
        envelope.source_id,

        "source_contract_version":
        envelope.source_contract_version,

        "message_id":
        envelope.message_id,

        "nonce":
        envelope.nonce,

        "sent_at":
        envelope.sent_at,

        "key_ref":
        envelope.key_ref,

        "signature_algorithm":
        envelope.signature_algorithm,

        "body_sha256":
        envelope.body_sha256,
    }


def _sign_material(
    material,
    secret,
):

    return hmac.new(
        secret,
        _canonical_json(
            material
        ).encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


def build_signed_summary_transport(
    payload,
    *,
    source_id,
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
            "Signing secret must be bytes."
        )


    spec = (
        get_clouds_feed_source_trust_spec(
            source_id
        )
    )


    payload = dict(
        payload
    )


    envelope = (
        SignedSummaryTransportEnvelope(

            transport_version=(
                TRANSPORT_VERSION
            ),

            source_id=(
                source_id
            ),

            source_contract_version=(
                spec
                .source_contract_version
            ),

            message_id=(
                message_id
            ),

            nonce=(
                nonce
            ),

            sent_at=(
                sent_at
            ),

            key_ref=(
                spec.signing_key_ref
            ),

            signature_algorithm=(
                SIGNATURE_ALGORITHM
            ),

            body_sha256=(
                _sha256_json(
                    payload
                )
            ),

            signature_hex="",

            certification_fixture_only=(
                certification_fixture_only
            ),

            payload=(
                payload
            ),
        )
    )


    signature = (
        _sign_material(
            _signature_material(
                envelope
            ),
            secret,
        )
    )


    return replace(
        envelope,
        signature_hex=(
            signature
        ),
    )


def validate_signed_summary_transport(
    envelope,
    *,
    secret,
    seen_message_ids=(),
    seen_nonces=(),
):

    errors = []


    try:

        spec = (
            get_clouds_feed_source_trust_spec(
                envelope.source_id
            )
        )

        source_known = True

    except KeyError:

        spec = None

        source_known = False

        errors.append(
            "unknown_source"
        )


    payload_source = (
        envelope.payload.get(
            "source_id"
        )
    )


    payload_contract = (
        envelope.payload.get(
            "source_contract_version"
        )
    )


    source_contract_matches = (
        source_known

        and envelope
        .source_contract_version
        == spec
        .source_contract_version

        and payload_source
        == envelope.source_id

        and payload_contract
        == envelope
        .source_contract_version
    )


    if not source_contract_matches:

        errors.append(
            "source_contract_mismatch"
        )


    key_ref_matches = (
        source_known

        and envelope.key_ref
        == spec.signing_key_ref
    )


    if not key_ref_matches:

        errors.append(
            "key_ref_mismatch"
        )


    body_integrity_verified = (
        envelope.body_sha256
        == _sha256_json(
            envelope.payload
        )
    )


    if not body_integrity_verified:

        errors.append(
            "body_hash_mismatch"
        )


    signature_algorithm_verified = (
        envelope.signature_algorithm
        == SIGNATURE_ALGORITHM
    )


    if not signature_algorithm_verified:

        errors.append(
            "signature_algorithm_invalid"
        )


    expected_signature = (
        _sign_material(
            _signature_material(
                envelope
            ),
            secret,
        )

        if isinstance(
            secret,
            bytes,
        )

        else ""
    )


    signature_verified = (
        signature_algorithm_verified

        and bool(
            envelope.signature_hex
        )

        and hmac.compare_digest(
            envelope.signature_hex,
            expected_signature,
        )
    )


    if not signature_verified:

        errors.append(
            "signature_invalid"
        )


    message_replay = (
        envelope.message_id
        in set(
            seen_message_ids
        )
    )


    nonce_replay = (
        envelope.nonce
        in set(
            seen_nonces
        )
    )


    replay_rejected = (
        message_replay
        or nonce_replay
    )


    if message_replay:

        errors.append(
            "message_id_replay"
        )


    if nonce_replay:

        errors.append(
            "nonce_replay"
        )


    if not envelope.message_id:

        errors.append(
            "message_id_required"
        )


    if not envelope.nonce:

        errors.append(
            "nonce_required"
        )


    if not envelope.sent_at:

        errors.append(
            "sent_at_required"
        )


    accepted = (
        source_known

        and source_contract_matches

        and key_ref_matches

        and body_integrity_verified

        and signature_algorithm_verified

        and signature_verified

        and not replay_rejected

        and bool(
            envelope.message_id
        )

        and bool(
            envelope.nonce
        )

        and bool(
            envelope.sent_at
        )
    )


    return SignedSummaryTransportValidation(

        source_id=(
            envelope.source_id
        ),

        message_id=(
            envelope.message_id
        ),

        nonce=(
            envelope.nonce
        ),

        source_known=(
            source_known
        ),

        source_contract_matches=(
            source_contract_matches
        ),

        key_ref_matches=(
            key_ref_matches
        ),

        body_integrity_verified=(
            body_integrity_verified
        ),

        signature_algorithm_verified=(
            signature_algorithm_verified
        ),

        signature_verified=(
            signature_verified
        ),

        message_id_replay_detected=(
            message_replay
        ),

        nonce_replay_detected=(
            nonce_replay
        ),

        replay_rejected=(
            replay_rejected
        ),

        certification_fixture_only=(
            envelope
            .certification_fixture_only
        ),

        accepted_for_connection_evaluation=(
            accepted
        ),

        counts_as_real_live_connection=False,

        secret_material_persisted=False,

        downstream_execution_performed=False,

        rejection_reasons=tuple(
            errors
        ),
    )


def build_gp066_certification_payload():

    return {

        "source_contract_version":
        "tower-clouds-summary-v1",

        "feed_id":
        "gp066-tower-certification-feed",

        "source_id":
        "tower",

        "source_label":
        "The Tower",

        "mode":
        "live",

        "source_sequence":
        6601,

        "observed_at":
        "2026-08-14T22:00:00Z",

        "health":
        "healthy",

        "readiness":
        "ready",

        "attention":
        "none",

        "headline":
        (
            "Transport certification fixture"
        ),

        "explanation":
        (
            "This proves the signed transport contract only."
        ),

        "owner_message":
        (
            "This fixture is not a real Tower feed."
        ),

        "metrics":
        [],

        "source_claims_live":
        True,
    }


def build_gp066_certification_envelope():

    return build_signed_summary_transport(

        build_gp066_certification_payload(),

        source_id="tower",

        secret=(
            CERTIFICATION_SECRET
        ),

        message_id=(
            "gp066-message-0001"
        ),

        nonce=(
            "gp066-nonce-0001"
        ),

        sent_at=(
            "2026-08-14T22:00:00Z"
        ),

        certification_fixture_only=True,
    )


def get_clouds_gp066_status_payload():

    gp065 = (
        get_clouds_gp065_status_payload()
    )


    envelope = (
        build_gp066_certification_envelope()
    )


    valid = (
        validate_signed_summary_transport(

            envelope,

            secret=(
                CERTIFICATION_SECRET
            ),
        )
    )


    replay = (
        validate_signed_summary_transport(

            envelope,

            secret=(
                CERTIFICATION_SECRET
            ),

            seen_message_ids=(
                envelope.message_id,
            ),

            seen_nonces=(
                envelope.nonce,
            ),
        )
    )


    tampered = replace(

        envelope,

        payload={
            **envelope.payload,

            "headline":
            "tampered",
        },
    )


    tampered_receipt = (
        validate_signed_summary_transport(

            tampered,

            secret=(
                CERTIFICATION_SECRET
            ),
        )
    )


    safe = (
        gp065["status"]
        == "ready"

        and gp065[
            "safe_to_continue"
        ]
        is True

        and valid
        .accepted_for_connection_evaluation
        is True

        and valid
        .source_known
        is True

        and valid
        .source_contract_matches
        is True

        and valid
        .key_ref_matches
        is True

        and valid
        .body_integrity_verified
        is True

        and valid
        .signature_verified
        is True

        and valid
        .replay_rejected
        is False

        and valid
        .certification_fixture_only
        is True

        and valid
        .counts_as_real_live_connection
        is False

        and valid
        .secret_material_persisted
        is False

        and replay
        .accepted_for_connection_evaluation
        is False

        and replay
        .message_id_replay_detected
        is True

        and replay
        .nonce_replay_detected
        is True

        and replay
        .replay_rejected
        is True

        and tampered_receipt
        .accepted_for_connection_evaluation
        is False

        and tampered_receipt
        .body_integrity_verified
        is False

        and valid
        .downstream_execution_performed
        is False
    )


    return {

        "pack":
        "GP066",

        "section":
        (
            "SIGNED SUMMARY TRANSPORT / "
            "AUTHENTICITY + REPLAY GATE"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "transport_version":
        TRANSPORT_VERSION,

        "signature_algorithm":
        SIGNATURE_ALGORITHM,

        "source_identity_verified":
        True,

        "source_contract_verified":
        True,

        "key_reference_verified":
        True,

        "body_integrity_verified":
        True,

        "signature_verified":
        True,

        "message_id_replay_rejection_ready":
        True,

        "nonce_replay_rejection_ready":
        True,

        "tamper_rejection_ready":
        True,

        "certification_fixture_only":
        True,

        "certification_fixture_counts_as_live":
        False,

        "secret_material_persisted":
        False,

        "external_transport_attempted":
        False,

        "real_live_connection_count":
        0,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP067 — CONNECTION LIFECYCLE / "
            "FRESHNESS + DISCONNECT + REVOKE"
        ),
    }

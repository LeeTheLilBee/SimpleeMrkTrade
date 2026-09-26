"""BBX017–021: gated Tower-hosted owner exchange and session verification.

This module intentionally has no real Tower issuer, introspection connector, or
provider attestor. A hosted process cannot start merely by setting env flags:
trusted adapters must be explicitly injected after integration certification.
Test fakes are for tests only; they do not certify Render, backups or Tower.
"""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlsplit
from .hosted_readiness import inspect_private_hosted_config

WORKSPACE_ID = "tea-dag3rfu1egvs73a6s72g"
SESSION_MAX_SECONDS = 15 * 60

class HostedAuthError(ValueError):
    pass

def prepare_hosted_runtime(config):
    if config.get("BUYBOX_AUTH_MODE") != "tower":
        raise HostedAuthError("TOWER_AUTH_MODE_REQUIRED")
    inspected = inspect_private_hosted_config(
        config, is_mount=(config.get("BUYBOX_TEST_MOUNT_CHECK")
                          if config.get("TESTING") is True else None))
    if inspected["status"] != "SOURCE_CONFIGURATION_VALID":
        raise HostedAuthError("HOSTED_CONFIGURATION_BLOCKED:" + ",".join(inspected["reason_codes"]))
    session_verifier = config.get("TOWER_SESSION_VERIFIER")
    storage_attestor = config.get("BUYBOX_STORAGE_ATTESTOR")
    if not callable(session_verifier):
        raise HostedAuthError("AUTHENTICATED_TOWER_SESSION_VERIFIER_NOT_CONNECTED")
    if not callable(storage_attestor):
        raise HostedAuthError("INDEPENDENT_STORAGE_AND_RESTORE_ATTESTOR_NOT_CONNECTED")
    try:
        attestation = storage_attestor()
    except Exception as exc:
        raise HostedAuthError("STORAGE_ATTESTATION_FAILED") from exc
    # Source format checks, NOT proof that an injected attestor itself is trusted.
    if not isinstance(attestation,dict) or set(attestation)!={
        "status","workspace_id","mount","backup_restore_proven","evidence_reference",
    }:
        raise HostedAuthError("INVALID_STORAGE_ATTESTATION")
    if (attestation["status"]!="VERIFIED"
            or attestation["workspace_id"]!=WORKSPACE_ID
            or attestation["mount"]!=config["BUYBOX_DURABLE_MOUNT"]
            or attestation["backup_restore_proven"] is not True
            or not isinstance(attestation["evidence_reference"],str)
            or not attestation["evidence_reference"].strip()):
        raise HostedAuthError("STORAGE_AND_RESTORE_NOT_CERTIFIED")
    return {"source_configuration_valid":True,"runtime_adapters_present":True,
            "live_tower_issuer_proven":False,
            "provider_certification_independently_verified_here":False,
            "may_deploy_without_review":False}

def exact_receiver_origin(request, configured_origin):
    """Do not trust arbitrary forwarded headers or permit cross-origin posts."""
    supplied = request.headers.get("Origin","")
    expected = urlsplit(configured_origin)
    return bool(supplied == configured_origin
                and request.scheme == "https"
                and request.host.lower() == expected.netloc.lower()
                and request.path == "/tower/owner-exchange"
                and not request.args)

def require_verified_session(verifier, session_claims, *, now_epoch):
    """Invoke the injected Tower introspection adapter on every protected route.

    A bool, local cookie, stale/mismatched response, or session-reference alone
    is never authority. The adapter must independently consult live Tower
    session/revocation/entitlement truth; this module cannot supply it.
    """
    required=("tower_session_ref","actor_ref","entity_ref","owner_entitlement_ref")
    if not isinstance(session_claims,dict) or any(
            not isinstance(session_claims.get(k),str) or not session_claims[k]
            for k in required):
        raise HostedAuthError("TOWER_SESSION_CONTEXT_REQUIRED")
    if not callable(verifier):
        raise HostedAuthError("AUTHENTICATED_TOWER_SESSION_VERIFIER_NOT_CONNECTED")
    try:
        current=verifier(
            tower_session_ref=session_claims["tower_session_ref"],
            actor_ref=session_claims["actor_ref"],
            entity_ref=session_claims["entity_ref"],
            owner_entitlement_ref=session_claims["owner_entitlement_ref"],
        )
    except Exception as exc:
        raise HostedAuthError("TOWER_SESSION_VERIFICATION_UNAVAILABLE") from exc
    if not isinstance(current,dict) or set(current)!={
        "issuer","status","app_id","tower_session_ref","actor_ref","entity_ref",
        "owner_entitlement_ref","step_up_active","entitlement_active",
        "expires_at_epoch",
    }:
        raise HostedAuthError("TOWER_SESSION_NOT_VERIFIED")
    if (current["issuer"]!="tower" or current["status"]!="ACTIVE"
            or current["app_id"]!="buybox"
            or current["step_up_active"] is not True
            or current["entitlement_active"] is not True
            or any(current[k]!=session_claims[k] for k in required)
            or type(current["expires_at_epoch"]) is not int
            or not now_epoch < current["expires_at_epoch"] <= now_epoch+SESSION_MAX_SECONDS):
        raise HostedAuthError("TOWER_SESSION_NOT_VERIFIED")
    return {"tower_session_ref":current["tower_session_ref"],
            "actor_ref":current["actor_ref"],"entity_ref":current["entity_ref"],
            "owner_entitlement_ref":current["owner_entitlement_ref"],
            "expires_at_epoch":current["expires_at_epoch"]}

def owner_session_claims(verified_handoff):
    c=verified_handoff.claims
    return {k:c[k] for k in (
        "tower_session_ref","actor_ref","entity_ref","owner_entitlement_ref")}

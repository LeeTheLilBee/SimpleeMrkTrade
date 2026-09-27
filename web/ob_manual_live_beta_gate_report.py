"""OBML011–015: source-bound, amount-free owner beta / Manual Live gate report.

Full upstream OBML001 and OBML006 independent revalidation is mandatory.
This report can help the owner rehearse the checklist, but cannot authenticate
Tower, a financial institution, a broker account, options permissions, an actual
human broker placement or a hosted production session. External gates remain
explicitly PENDING, never client-supplied booleans.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json

from web.ob_manual_live_owner_preflight import (
    ManualLiveSourceBundle, OwnerManualLivePreflight, OwnerReviewPlan,
)
from web.ob_manual_live_tower_contract_inspection import (
    TowerContractInspection, verify_tower_contract_inspection,
)
from web.ob_recovery_review import RecoveryReview

SCHEMA_VERSION = "OB_OWNER_BETA_GATE_REPORT_V1"
REQUIRED_EXTERNAL_GATES = (
    ("TOWER_PURPOSE_BOUND_AUTHENTICATION", "Tower server: real owner session, exact account/purpose permission, fresh step-up, one-time nonce and revocation."),
    ("TOWER_HOSTED_OWNER_CROSSING", "Verify the actual deployed Tower-to-OB owner launch and runtime revision."),
    ("PROVIDER_ACCOUNT_AND_OPTIONS_PERMISSIONS", "Independently authenticate the real brokerage account and instrument/option permissions."),
    ("PROVIDER_SETTLEMENT_AND_PROTECTED_FLOORS", "Reconcile institution-reported settled/withdrawable capital and protected reserves through the appropriate financial authority."),
    ("CURRENT_SOURCE_RISK_AND_MARKET", "Recheck fresh canonical market, risk, policy, safety and account evidence immediately before any future real activity."),
    ("HUMAN_REVIEW_CENTER_DECISION", "Obtain separate owner-approved Manual Live L1 authorization and a human Review Center receipt."),
    ("EXTERNAL_MANUAL_ORDER_RECONCILIATION", "Only after separately authorized human brokerage placement, match an independently sourced provider order/fill receipt."),
    ("PRODUCTION_OPERATING_APPROVAL", "Require distinct independent owner/security/compliance/operating approval before any production mode changes."),
)
SOURCE_GATES = (
    ("CANONICAL_RECOVERY_AND_SAFETY", "Revalidate source recovery and retain canonical BLOCK/HOLD."),
    ("OWNER_PLAN_AND_ACCOUNT_BINDING", "Inspect the exact owner-declared account/candidate plan, never a trading instruction."),
    ("TOWER_HANDOFF_SHAPE", "Inspect the proposed versioned claim shape. Matching fields are not issuer authentication."),
)


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class BetaGate:
    gate_id: str
    group: str
    state: str
    explanation: str
    source_receipt_id: str | None
    source_integrity_hash: str | None
    externally_authenticated: bool
    live_authority_granted: bool


@dataclass(frozen=True)
class OwnerBetaGateReport:
    report_id: str
    authority: str
    account_key: str
    recovery_id: str
    recovery_hash: str
    preflight_id: str
    preflight_hash: str
    tower_inspection_id: str
    tower_inspection_hash: str
    as_of_utc: str
    canonical_recommendation_state: str
    source_preflight_state: str
    structural_tower_claim_matches: bool
    report_state: str
    gate_records: tuple[BetaGate, ...]
    upstream_reason_codes: tuple[str, ...]
    external_gate_ids_still_pending: tuple[str, ...]
    paper_rehearsal_is_not_production: bool
    actual_hosted_beta_access_verified: bool
    tower_server_grant_verified: bool
    broker_or_bank_provenance_verified: bool
    manual_live_unlocked: bool
    actual_broker_fill_verified: bool
    order_api_enabled: bool
    capital_movement: bool
    safety_block_dismissed: bool
    source_truth_mutated: bool
    hybrid_or_automated_enabled: bool
    direct_buybox_access: bool
    integrity_hash: str


def _material(value: OwnerBetaGateReport) -> dict[str, object]:
    return {
        k: [asdict(v) for v in value.gate_records] if k == "gate_records" else getattr(value, k)
        for k in OwnerBetaGateReport.__dataclass_fields__
        if k not in ("report_id", "integrity_hash")
    }


def _build(
    inspection: TowerContractInspection,
    preflight: OwnerManualLivePreflight,
    recovery: RecoveryReview,
    source_bundle: ManualLiveSourceBundle,
    *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None,
    as_of_utc: str,
) -> OwnerBetaGateReport:
    # Reconstruct both complete source families, not merely hash-check their ID.
    if not verify_tower_contract_inspection(
        inspection, preflight, recovery, source_bundle,
        owner_plan=owner_plan, presented=presented, as_of_utc=as_of_utc,
    ):
        raise ValueError("OBML owner beta report requires verified full Tower/source lineage")
    if inspection.account_key != preflight.account_key or preflight.account_key != recovery.account_key:
        raise ValueError("owner beta account source boundary mismatch")
    blocked = (
        preflight.status.startswith("BLOCKED") or
        inspection.status == "BLOCKED_CANONICAL_SOURCE" or
        recovery.canonical_recommendation_state == "BLOCKED"
    )
    reasons = tuple(sorted(set(preflight.reason_codes) | set(inspection.reasons) | set(recovery.reason_codes)))
    # OBRES has no state that independently certifies a real recovered provider.
    source_states = "BLOCKED_CANONICAL_SOURCE" if blocked else "HOLD_CANONICAL_REVALIDATION"
    records = (
        BetaGate(
            "CANONICAL_RECOVERY_AND_SAFETY", "SOURCE", source_states,
            SOURCE_GATES[0][1], recovery.review_id, recovery.integrity_hash,
            False, False,
        ),
        BetaGate(
            "OWNER_PLAN_AND_ACCOUNT_BINDING", "SOURCE",
            "OWNER_PLAN_REVIEW_ONLY" if owner_plan is not None and not blocked else
            "BLOCKED_UPSTREAM" if blocked else "MISSING_OWNER_PLAN",
            SOURCE_GATES[1][1], preflight.preflight_id, preflight.integrity_hash,
            False, False,
        ),
        BetaGate(
            "TOWER_HANDOFF_SHAPE", "SOURCE",
            "STRUCTURE_ONLY_UNTRUSTED" if inspection.structural_match_only and not blocked else
            "BLOCKED_UPSTREAM" if blocked else "HOLD_MISSING_OR_INVALID_CLAIM",
            SOURCE_GATES[2][1], inspection.inspection_id, inspection.integrity_hash,
            False, False,
        ),
    ) + tuple(BetaGate(
        gate, "EXTERNAL", "PENDING_INDEPENDENT_PROOF", text,
        None, None, False, False,
    ) for gate, text in REQUIRED_EXTERNAL_GATES)
    provisional = OwnerBetaGateReport(
        report_id="PENDING", authority=SCHEMA_VERSION,
        account_key=preflight.account_key,
        recovery_id=recovery.review_id, recovery_hash=recovery.integrity_hash,
        preflight_id=preflight.preflight_id, preflight_hash=preflight.integrity_hash,
        tower_inspection_id=inspection.inspection_id,
        tower_inspection_hash=inspection.integrity_hash,
        as_of_utc=as_of_utc,
        canonical_recommendation_state=recovery.canonical_recommendation_state,
        source_preflight_state=preflight.status,
        structural_tower_claim_matches=inspection.structural_match_only,
        report_state="BLOCKED_CANONICAL_SOURCE" if blocked else "HOLD_REAL_TOWER_AND_PROVIDER_GATES",
        gate_records=records, upstream_reason_codes=reasons,
        external_gate_ids_still_pending=tuple(x[0] for x in REQUIRED_EXTERNAL_GATES),
        paper_rehearsal_is_not_production=True,
        actual_hosted_beta_access_verified=False, tower_server_grant_verified=False,
        broker_or_bank_provenance_verified=False, manual_live_unlocked=False,
        actual_broker_fill_verified=False, order_api_enabled=False,
        capital_movement=False, safety_block_dismissed=False, source_truth_mutated=False,
        hybrid_or_automated_enabled=False, direct_buybox_access=False,
        integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, report_id="OBMLGATE-" + digest[:24], integrity_hash=digest)


def verify_owner_beta_gate_report(
    value: OwnerBetaGateReport, inspection: TowerContractInspection,
    preflight: OwnerManualLivePreflight, recovery: RecoveryReview,
    source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None, presented: dict[str, object] | None = None,
    as_of_utc: str,
) -> bool:
    if not isinstance(value, OwnerBetaGateReport) or value.authority != SCHEMA_VERSION:
        return False
    if value.paper_rehearsal_is_not_production is not True or any(
        getattr(value, key) is not False for key in (
            "actual_hosted_beta_access_verified", "tower_server_grant_verified",
            "broker_or_bank_provenance_verified", "manual_live_unlocked",
            "actual_broker_fill_verified", "order_api_enabled", "capital_movement",
            "safety_block_dismissed", "source_truth_mutated", "hybrid_or_automated_enabled",
            "direct_buybox_access",
        )
    ):
        return False
    try:
        return value == _build(
            inspection, preflight, recovery, source_bundle, owner_plan=owner_plan,
            presented=presented, as_of_utc=as_of_utc,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_owner_beta_gate_report(
    inspection: TowerContractInspection, preflight: OwnerManualLivePreflight,
    recovery: RecoveryReview, source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None, presented: dict[str, object] | None = None,
    as_of_utc: str,
) -> OwnerBetaGateReport:
    value = _build(
        inspection, preflight, recovery, source_bundle, owner_plan=owner_plan,
        presented=presented, as_of_utc=as_of_utc,
    )
    if not verify_owner_beta_gate_report(
        value, inspection, preflight, recovery, source_bundle, owner_plan=owner_plan,
        presented=presented, as_of_utc=as_of_utc,
    ):
        raise ValueError("owner beta gate report failed source revalidation")
    return value


def owner_beta_gate_reference(
    value: OwnerBetaGateReport, inspection: TowerContractInspection,
    preflight: OwnerManualLivePreflight, recovery: RecoveryReview,
    source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None, presented: dict[str, object] | None = None,
    as_of_utc: str,
) -> dict[str, object]:
    if not verify_owner_beta_gate_report(
        value, inspection, preflight, recovery, source_bundle, owner_plan=owner_plan,
        presented=presented, as_of_utc=as_of_utc,
    ):
        raise ValueError("owner beta reference requires fully reverified source evidence")
    return {
        "authority": SCHEMA_VERSION, "report_id": value.report_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "report_state": value.report_state,
        "recovery_id": value.recovery_id,
        "preflight_id": value.preflight_id,
        "tower_inspection_id": value.tower_inspection_id,
        "pending_external_gates": list(value.external_gate_ids_still_pending),
        "amounts_exposed": False,
        "owner_identity_or_token_exposed": False,
        "tower_server_grant_verified": False, "manual_live_unlocked": False,
        "broker_submission": False, "capital_movement": False,
        "tower_authorization_required": True,
    }


def owner_beta_gate_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "upstream_preflight": "OB_OWNER_MANUAL_LIVE_SOURCE_PREFLIGHT_V1",
        "upstream_contract_inspection": "OB_OWNER_MANUAL_LIVE_TOWER_CONTRACT_INSPECTION_V1",
        "full_source_lineage_revalidated": True,
        "external_gate_count": len(REQUIRED_EXTERNAL_GATES),
        "external_gate_evidence_accepted_from_untrusted_caller": False,
        "source_only_review_is_production_permission": False,
        "no_additional_authentication_engine": True,
        "manual_live_unlock": False, "broker_submission": False,
        "capital_movement": False, "mode_change": False,
        "hybrid_unlock": False, "automated_unlock": False,
        "direct_buybox_access": False, "teller_owns_financial_readiness": True,
    }

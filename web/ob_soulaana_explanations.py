"""OBSOUL001–005: deterministic, source-bound Soulaana explanation projection.

Only canonical verified receipts may appear. Text is a constrained explanation
of known codes, not a market-data source, investment prediction, new rule,
broker connector, or privileged action. The user's future conversational layer
must preserve these references and never fabricate unsupported claims.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json

from web.ob_adverse_guard_review import (
    GuardEvidence, GuardReview, verify_guard_review,
)

SCHEMA_VERSION = "OB_SOULAANA_EXPLANATION_V1"

STATE_TEXT = {
    "SOURCE_EVIDENCE_HOLD":
        "The reviewed source has an unresolved evidence or safety hold. No action is authorized.",
    "ADVERSE_SOURCE_REVIEW":
        "An adverse source assertion requires owner review. It is not authenticated market proof.",
    "REPEATED_ADVERSE_SOURCE_REVIEW":
        "Distinct adverse source assertions recur. Review their independent evidence; no automatic protective action was executed.",
    "NO_ADVERSE_SOURCE_REPORTED_NOT_SAFETY_PROOF":
        "No adverse source assertion was recorded in this set. That does not certify safety.",
}
RECOMMENDATION_TEXT = {
    "BLOCKED": "The canonical safety review blocks this candidate. No trade or mode permission follows.",
    "EVIDENCE_PENDING": "The canonical source evidence is incomplete. The candidate remains on hold.",
    "OWNER_REVIEW_READY": "The source-backed candidate is ready for owner review only, not execution.",
}
PATTERN_TEXT = {
    "NEGATIVE_DIVE": "Negative Dive source claims warrant owner review, not an inferred realized trading loss.",
    "OVERTIME": "Overtime source claims warrant owner review, not an inferred execution history.",
    "OVERREACH": "Overreach source claims warrant owner review without widening risk or changing policy.",
    "SOURCE_GAP": "Missing source evidence requires reconciliation before drawing a stronger conclusion.",
}


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class SoulaanaCard:
    card_id: str
    kind: str
    heading: str
    explanation: str
    source_receipt_id: str
    source_code: str
    owner_action_class: str
    verified_external_market_fact: bool
    execution_permission: bool


@dataclass(frozen=True)
class SoulaanaExplanation:
    explanation_id: str
    authority: str
    account_key: str
    guard_id: str
    guard_hash: str
    cards: tuple[SoulaanaCard, ...]
    source_receipt_ids: tuple[str, ...]
    claim_scope: str
    source_authenticated_as_broker: bool
    invents_market_truth: bool
    invents_money_truth: bool
    changes_safety_or_policy: bool
    issues_trade_intent: bool
    broker_submission: bool
    capital_movement: bool
    mode_change: bool
    integrity_hash: str


def _card(
    *, kind: str, heading: str, explanation: str,
    source_id: str, code: str,
) -> SoulaanaCard:
    material = dict(kind=kind, heading=heading, explanation=explanation,
                    source_receipt_id=source_id, source_code=code)
    return SoulaanaCard(
        card_id="SOULCARD-" + _hash(material)[:24],
        kind=kind, heading=heading, explanation=explanation,
        source_receipt_id=source_id, source_code=code,
        owner_action_class="OWNER_REVIEW_ONLY",
        verified_external_market_fact=False, execution_permission=False,
    )


def _material(value: SoulaanaExplanation) -> dict[str, object]:
    return {
        key: ([asdict(c) for c in value.cards] if key == "cards" else getattr(value, key))
        for key in SoulaanaExplanation.__dataclass_fields__
        if key not in ("explanation_id", "integrity_hash")
    }


def _build(guard: GuardReview, evidence: tuple[GuardEvidence, ...]) -> SoulaanaExplanation:
    if not verify_guard_review(guard, evidence):
        raise ValueError("Soulaana requires fully verified canonical OBGUARD lineage")
    cards = [
        _card(kind="GUARD_STATE", heading="Current review state",
              explanation=STATE_TEXT[guard.state], source_id=guard.guard_id,
              code=guard.state)
    ]
    for pattern in guard.source_assertion_patterns:
        cards.append(_card(
            kind="SOURCE_ASSERTED_PATTERN", heading=pattern.issue_code.replace("_", " ").title(),
            explanation=(
                PATTERN_TEXT[pattern.issue_code] +
                " Distinct source payloads observed: " +
                str(pattern.distinct_source_payload_count) +
                ". These are source assertions, not independently authenticated market incidents."
            ),
            source_id=guard.guard_id, code=pattern.issue_code,
        ))
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        rec = item.recommendation
        key = (rec.recommendation_id, rec.state)
        if key not in seen:
            seen.add(key)
            cards.append(_card(
                kind="RECOMMENDATION_STATUS", heading="Recommendation review",
                explanation=RECOMMENDATION_TEXT[rec.state],
                source_id=rec.recommendation_id, code=rec.state,
            ))
    for task in guard.owner_attention_tasks:
        cards.append(_card(
            kind="NEXT_REVIEW_TASK", heading="Owner attention",
            explanation=(
                "Review the canonical task " + task +
                " against its source receipt. No automated order or policy change is requested."
            ),
            source_id=guard.guard_id, code=task,
        ))
    provisional = SoulaanaExplanation(
        explanation_id="PENDING", authority=SCHEMA_VERSION,
        account_key=guard.account_key, guard_id=guard.guard_id,
        guard_hash=guard.integrity_hash, cards=tuple(cards),
        source_receipt_ids=guard.learning_receipt_ids,
        claim_scope="VERIFIED_REPOSITORY_RECEIPTS_SOURCE_ASSERTIONS_ONLY",
        source_authenticated_as_broker=False, invents_market_truth=False,
        invents_money_truth=False, changes_safety_or_policy=False,
        issues_trade_intent=False, broker_submission=False, capital_movement=False,
        mode_change=False, integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, explanation_id="OBSOUL-" + digest[:24],
                   integrity_hash=digest)


def verify_soulaana_explanation(
    value: SoulaanaExplanation, guard: GuardReview,
    evidence: tuple[GuardEvidence, ...],
) -> bool:
    if not isinstance(value, SoulaanaExplanation) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, key) is not False for key in (
        "source_authenticated_as_broker", "invents_market_truth", "invents_money_truth",
        "changes_safety_or_policy", "issues_trade_intent", "broker_submission",
        "capital_movement", "mode_change",
    )):
        return False
    try:
        return value == _build(guard, evidence)
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_soulaana_explanation(
    guard: GuardReview, evidence: tuple[GuardEvidence, ...],
) -> SoulaanaExplanation:
    result = _build(guard, evidence)
    if not verify_soulaana_explanation(result, guard, evidence):
        raise ValueError("Soulaana explanation failed source-bound verification")
    return result


def soulaana_reference(
    value: SoulaanaExplanation, guard: GuardReview,
    evidence: tuple[GuardEvidence, ...],
) -> dict[str, object]:
    if not verify_soulaana_explanation(value, guard, evidence):
        raise ValueError("Soulaana reference requires fully verified source lineage")
    return {
        "authority": SCHEMA_VERSION, "explanation_id": value.explanation_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "guard_id": value.guard_id, "source_receipt_ids": list(value.source_receipt_ids),
        "amounts_exposed": False, "execution_permission": False,
        "broker_submission": False, "capital_movement": False,
        "tower_authorization_required": True,
    }


def soulaana_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "upstream_authority": "OB_ADVERSE_GUARD_REVIEW_V1",
        "source_lineage_reverified": True, "constrained_explanation_templates": True,
        "freeform_model_invents_source_facts": False,
        "source_claims_are_not_broker_verified": True, "owner_review_only": True,
        "safety_override": False, "market_truth_mutation": False,
        "money_truth_mutation": False, "broker_submission": False,
        "capital_movement": False, "mode_change": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }

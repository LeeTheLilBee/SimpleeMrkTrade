"""GRD020 — source-bound apartment readiness display mediated by Teller.

This is a view validation contract, never an order, disbursement, underwriting,
loan approval or OB account query. Certified Teller transport verification is
required upstream. The five mission lanes and hard-bottom semantics are retained.
"""
from __future__ import annotations

from time import time
from typing import Callable, Mapping

from .access import AccessDenied, TowerScope

LANES = (
    "down_payment",
    "closing_costs",
    "repair_capex",
    "operating_emergency",
    "manager_ops_remodel",
)
STATUSES = frozenset(("ready","watch","weak","blocked","unknown"))
OVERALL = frozenset(("ready","review","not_ready","unknown"))


def verified_apartment_readiness(
    actor: TowerScope, signed_snapshot: object, *,
    property_ref: str, mission_ref: str, terms_digest: str,
    teller_verifier: Callable[[object], Mapping], now: int | None = None,
) -> dict:
    actor.require_role("owner", "property_manager")
    actor.require_property(property_ref)
    if not callable(teller_verifier):
        raise AccessDenied("certified Teller readiness verifier required")
    try:
        snapshot = teller_verifier(signed_snapshot)
    except Exception as exc:
        raise AccessDenied("readiness snapshot rejected") from exc
    if (not isinstance(snapshot, Mapping) or snapshot.get("source") != "teller"
        or snapshot.get("audience") != "grounds"
        or snapshot.get("property_ref") != property_ref
        or snapshot.get("mission_ref") != mission_ref
        or snapshot.get("terms_digest") != terms_digest):
        raise AccessDenied("Teller readiness scope or terms mismatch")
    clock=int(time()) if now is None else now
    observed,expires=snapshot.get("observed_at"),snapshot.get("expires_at")
    if (type(clock) is not int or type(observed) is not int or type(expires) is not int
        or observed > clock or expires <= clock or expires-observed > 300):
        raise AccessDenied("Teller readiness stale")
    if snapshot.get("overall") not in OVERALL:
        raise AccessDenied("invalid readiness status")
    lanes=snapshot.get("lanes")
    if not isinstance(lanes,Mapping) or set(lanes)!=set(LANES):
        raise AccessDenied("five separate apartment lanes required")
    safe={}
    for lane in LANES:
        value=lanes[lane]
        if not isinstance(value,Mapping) or value.get("status") not in STATUSES:
            raise AccessDenied("invalid Teller lane")
        numbers=("current_cents","target_cents","hard_bottom_cents","protected_cents",
                 "committed_cents","available_cents")
        if any(type(value.get(field)) is not int or value[field]<0 for field in numbers):
            raise AccessDenied("invalid Teller amount")
        current=value["current_cents"];bottom=value["hard_bottom_cents"]
        protected=value["protected_cents"];committed=value["committed_cents"]
        available=value["available_cents"]
        if (protected > current
            or available > max(0,current-max(bottom,protected)-committed)
            or (current < bottom and value["status"] == "ready")):
            raise AccessDenied("inconsistent protected capital")
        use=value.get("allowed_use")
        next_action=value.get("next_action")
        if (not isinstance(use,str) or not use.strip() or len(use)>256
            or not isinstance(next_action,str) or not next_action.strip() or len(next_action)>512):
            raise AccessDenied("missing Teller lane explanation")
        safe[lane]={field:value[field] for field in numbers}
        safe[lane].update(status=value["status"],allowed_use=use,next_action=next_action)
    return {
        "source":"teller","mode":"verified_projection","property_ref":property_ref,
        "mission_ref":mission_ref,"terms_digest":terms_digest,"overall":snapshot["overall"],
        "observed_at":observed,"expires_at":expires,"lanes":safe,
        "money_movement_enabled":False,"ob_account_query_performed":False,
        "recommendation_is_execution_authority":False,
    }

"""GRD011 — Teller-sourced rent projection, deliberately no payment execution.

A certified Teller verifier must authenticate original message/signature, source,
replay, freshness, currency and exact recipient. This module only narrows the
verified projection to a single Tower-authenticated resident/active lease. It
does not generate checkout links or accept an OB/account balance as rent truth.
"""
from __future__ import annotations

from datetime import date
from time import time
from typing import Callable, Mapping

from .access import AccessDenied, TowerScope


def resident_rent_projection(
    actor: TowerScope, home: Mapping, signed_message: object, *,
    teller_verifier: Callable[[object], Mapping], now: int | None = None,
) -> dict:
    actor.require_role("resident")
    if not callable(teller_verifier):
        raise AccessDenied("certified Teller verifier required")
    try:
        item = teller_verifier(signed_message)
    except Exception as exc:
        raise AccessDenied("Teller projection rejected") from exc
    if not isinstance(item, Mapping) or item.get("source") != "teller" or item.get("audience") != "grounds":
        raise AccessDenied("Teller projection rejected")
    if (item.get("resident_ref") != actor.subject_ref
        or item.get("property_ref") != home.get("property_ref")
        or item.get("unit_ref") != home.get("unit_ref")
        or item.get("lease_ref") != home.get("lease", {}).get("lease_ref")):
        raise AccessDenied("Teller projection scope mismatch")
    actor.require_unit(home["property_ref"], home["unit_ref"])
    clock = int(time()) if now is None else now
    observed, expiry = item.get("observed_at"), item.get("expires_at")
    if type(clock) is not int or type(observed) is not int or type(expiry) is not int:
        raise AccessDenied("invalid Teller freshness")
    if observed > clock or expiry <= clock or expiry - observed > 300:
        raise AccessDenied("stale Teller projection")
    amount = item.get("amount_due_cents")
    if type(amount) is not int or amount < 0 or amount > 10**12:
        raise AccessDenied("invalid Teller amount")
    if item.get("currency") != "USD":
        raise AccessDenied("wrong Teller currency")
    if item.get("invoice_status") not in ("due","partial","paid","overdue","credit","pending"):
        raise AccessDenied("invalid Teller invoice state")
    due = item.get("due_on")
    if not isinstance(due, str):
        raise AccessDenied("invalid Teller due date")
    try:
        if date.fromisoformat(due).isoformat() != due:
            raise ValueError
    except ValueError as exc:
        raise AccessDenied("invalid Teller due date") from exc
    intent_ref = item.get("teller_handoff_ref")
    if intent_ref is not None and (
        not isinstance(intent_ref, str) or not intent_ref.strip() or len(intent_ref) > 128
    ):
        raise AccessDenied("invalid Teller handoff reference")
    return {
        "source": "teller", "status": "verified_projection",
        "amount_due_cents": amount, "currency": "USD",
        "invoice_status": item["invoice_status"], "due_on": due,
        "observed_at": observed, "expires_at": expiry,
        "pay_rent_action": "request_tower_mediated_teller_handoff" if intent_ref else "unavailable",
        "teller_handoff_ref": intent_ref,
        "checkout_url": None, "checkout_execution_enabled": False,
        "projection_only": True,
    }

"""Market Data Desk process: owner-reviewed source lifecycle, zero execution authority.

This is an internal orchestration contract, not an HTTP endpoint or a way for a
browser to self-approve market-data rights. No network, secrets or order routing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping

from .contracts import SourceRights, _aware
from .provider_catalog import CATALOG, ProviderProduct


class CaseState(str, Enum):
    DISCOVERED = "DISCOVERED"
    RIGHTS_REVIEW = "RIGHTS_REVIEW"
    CONFIGURATION_PENDING = "CONFIGURATION_PENDING"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    OWNER_APPROVAL = "OWNER_APPROVAL"
    OBSERVING = "OBSERVING"
    HOLD = "HOLD"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class DeskReceipt:
    """Reference only: no raw provider payload, account IDs or credential values."""
    receipt_id: str
    occurred_at: datetime
    actor_authority_reference: str
    evidence_reference: str
    note: str

    def __post_init__(self) -> None:
        _aware(self.occurred_at, "receipt time")
        for label in ("receipt_id", "actor_authority_reference", "evidence_reference", "note"):
            if not str(getattr(self, label)).strip():
                raise ValueError(f"{label} required")
        if len(self.note) > 300:
            raise ValueError("bounded non-secret summary required")


@dataclass(frozen=True)
class ConnectionCheck:
    """A trusted backend supplies these results after actual transport validation.

    A planned adapter, fake screenshot or free sandbox by itself is not proof.
    """
    product_key: str
    source_id: str
    verified_at: datetime
    transport_authenticated: bool
    read_only_transport: bool
    exact_feed_entitled: bool
    true_provider_event_time_verified: bool
    canonical_market_time_verified: bool
    real_time_non_indicative: bool
    provider_limits_verified: bool
    receipt_reference: str

    def __post_init__(self) -> None:
        _aware(self.verified_at, "verification time")
        if not self.product_key.strip() or not self.source_id.strip() or not self.receipt_reference.strip():
            raise ValueError("exact source/product and verification receipt required")

    def passed(self) -> bool:
        return all((
            self.transport_authenticated, self.read_only_transport,
            self.exact_feed_entitled, self.true_provider_event_time_verified,
            self.canonical_market_time_verified, self.real_time_non_indicative,
            self.provider_limits_verified,
        ))


@dataclass
class ProviderCase:
    case_id: str
    product_key: str
    source_id: str
    state: CaseState = CaseState.DISCOVERED
    rights: SourceRights | None = None
    secret_reference_verified: bool = False  # no secret or secret name stored
    verification: ConnectionCheck | None = None
    owner_approval_reference: str = ""
    hold_reason: str = ""
    history: list[tuple[str, DeskReceipt]] = field(default_factory=list)


class ProviderDeskProcess:
    """Trusted owner/Tower backend uses this process; the UI can only read projection.

    The process never writes to the live gateway. Observation admission still
    requires independent ingress and all canonical market-source checks.
    """

    def __init__(self, products: Mapping[str, ProviderProduct] | None = None) -> None:
        self.products = dict(CATALOG if products is None else products)
        self._cases: dict[str, ProviderCase] = {}
        self._receipts: set[str] = set()

    def _log(self, item: ProviderCase, next_state: CaseState, receipt: DeskReceipt) -> None:
        if receipt.receipt_id in self._receipts:
            raise ValueError("duplicate audit receipt")
        if item.history and receipt.occurred_at <= item.history[-1][1].occurred_at:
            raise ValueError("audit receipt must follow the prior case event")
        previous = item.state
        self._receipts.add(receipt.receipt_id)
        item.state = next_state
        item.history.append((f"{previous.value}->{next_state.value}", receipt))

    def discover(self, *, case_id: str, product_key: str, source_id: str,
                 receipt: DeskReceipt) -> None:
        if not case_id.strip() or not source_id.strip() or case_id in self._cases:
            raise ValueError("unique case and source IDs required")
        if any(x.source_id == source_id for x in self._cases.values()):
            raise ValueError("source ID already assigned; avoid account/product mixing")
        p = self.products.get(product_key)
        if p is None:
            raise ValueError("unknown product")
        if receipt.receipt_id in self._receipts:
            raise ValueError("duplicate audit receipt")
        self._receipts.add(receipt.receipt_id)
        case = ProviderCase(case_id, product_key, source_id)
        case.history.append(("NEW->DISCOVERED", receipt))
        self._cases[case_id] = case

    def begin_review(self, case_id: str, receipt: DeskReceipt) -> None:
        item = self._case(case_id, CaseState.DISCOVERED)
        self._log(item, CaseState.RIGHTS_REVIEW, receipt)

    def record_rights(self, case_id: str, rights: SourceRights,
                      receipt: DeskReceipt) -> None:
        item = self._case(case_id, CaseState.RIGHTS_REVIEW)
        product = self.products[item.product_key]
        if not product.current_quote_eligible or product.instrument not in {"equity", "option"}:
            raise ValueError("event/reference/indicative lane cannot become a live quote")
        if rights.source_id != item.source_id or not rights.reviewed_for_scan():
            raise ValueError("separately reviewed exact product/source rights required")
        if product.instrument not in rights.entitled_instruments or not rights.real_time_entitled:
            raise ValueError("instrument-specific current market-data rights missing")
        if rights.verified_at is None or rights.verified_at > receipt.occurred_at or (
            rights.expires_at is not None and receipt.occurred_at >= rights.expires_at):
            raise ValueError("not yet valid or expired rights")
        self._log(item, CaseState.CONFIGURATION_PENDING, receipt)
        item.rights = rights

    def configuration_verified(self, case_id: str, *, backend_secret_reference_verified: bool,
                               receipt: DeskReceipt) -> None:
        item = self._case(case_id, CaseState.CONFIGURATION_PENDING)
        if not backend_secret_reference_verified:
            raise ValueError("secure backend credential reference was not independently verified")
        self._log(item, CaseState.VERIFICATION_PENDING, receipt)
        item.secret_reference_verified = True

    def verify(self, case_id: str, check: ConnectionCheck, receipt: DeskReceipt) -> None:
        item = self._case(case_id, CaseState.VERIFICATION_PENDING)
        if (check.product_key != item.product_key or check.source_id != item.source_id
            or check.verified_at > receipt.occurred_at or not check.passed()):
            raise ValueError("exact successful live connection test required")
        if item.rights is None or item.rights.expires_at is not None and (
            receipt.occurred_at >= item.rights.expires_at):
            raise ValueError("rights are missing or expired")
        self._log(item, CaseState.OWNER_APPROVAL, receipt)
        item.verification = check

    def approve(self, case_id: str, *, tower_owner_step_up_verified: bool,
                receipt: DeskReceipt) -> None:
        item = self._case(case_id, CaseState.OWNER_APPROVAL)
        if not tower_owner_step_up_verified or not receipt.actor_authority_reference.startswith("tower-owner:"):
            raise ValueError("fresh Tower owner step-up is required, never browser self-approval")
        if (item.rights is None or item.verification is None or not item.verification.passed()
                or item.rights.expires_at is not None and receipt.occurred_at >= item.rights.expires_at):
            raise ValueError("unverified or expired connection cannot be approved")
        self._log(item, CaseState.OBSERVING, receipt)
        item.owner_approval_reference = receipt.receipt_id

    def hold(self, case_id: str, reason: str, receipt: DeskReceipt) -> None:
        item = self._cases[case_id]
        if item.state in {CaseState.REVOKED, CaseState.HOLD}:
            raise ValueError("revoked or held case requires a new review case")
        if not reason.strip():
            raise ValueError("specific HOLD reason required")
        self._log(item, CaseState.HOLD, receipt)
        item.hold_reason = reason.strip()[:200]
        item.owner_approval_reference = ""

    def revoke(self, case_id: str, receipt: DeskReceipt) -> None:
        item = self._cases[case_id]
        if item.state == CaseState.REVOKED:
            raise ValueError("already revoked")
        self._log(item, CaseState.REVOKED, receipt)
        item.rights = None
        item.secret_reference_verified = False
        item.verification = None
        item.owner_approval_reference = ""
        item.hold_reason = "Revoked; remove corresponding source from market gateway."

    def status(self, now: datetime) -> dict[str, object]:
        _aware(now, "projection time")
        cases = []
        for item in sorted(self._cases.values(), key=lambda x: x.case_id):
            state = item.state.value
            reason = item.hold_reason
            if (item.rights is not None and item.rights.expires_at is not None
                    and now >= item.rights.expires_at and item.state != CaseState.REVOKED):
                state = CaseState.HOLD.value
                reason = "Rights expired; gateway must independently reject and revoke source."
            cases.append({
                "case_id": item.case_id, "product_key": item.product_key,
                "state": state, "reason": reason, "audit_count": len(item.history),
                "last_receipt": item.history[-1][1].receipt_id,
                "live_data_connected": False, # process cannot declare runtime stream health
                "trading_authorized": False,
            })
        return {
            "schema": "OB_MARKET_DATA_DESK_PROCESS_V1",
            "as_of": now.isoformat(), "cases": cases,
            "actionable": sum(x["state"] in {
                "DISCOVERED", "RIGHTS_REVIEW", "CONFIGURATION_PENDING",
                "VERIFICATION_PENDING", "OWNER_APPROVAL", "HOLD",
            } for x in cases),
            "mode": "read_only", "execution_authorized": False,
        }

    def _case(self, case_id: str, expected: CaseState) -> ProviderCase:
        item = self._cases[case_id]
        if item.state != expected:
            raise ValueError(f"illegal transition from {item.state.value}; expected {expected.value}")
        return item

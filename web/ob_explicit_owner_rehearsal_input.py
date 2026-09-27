"""OBSIM036–040: explicit historical/synthetic owner input for a local rehearsal desk.

This is a data-only bridge around the accepted OBSIM session and OBTIME builders,
not a new engine, market provider, trusted owner login or hosted Flask route.
Every frame and all three lane decisions are supplied explicitly by the caller.
No timer, order, recommendation, funds or real account authority is created.
"""
from __future__ import annotations

from datetime import date, datetime
import math
from typing import Mapping

from web.ob_market_time_authority import build_canonical_market_time, build_market_schedule
from web.ob_multi_simulation_harness import (
    SimulationAction, SimulationLane, build_market_frame, build_simulation_instrument,
)
from web.ob_multi_simulation_replay import ReplayDecision, ReplayStep
from web.ob_on_demand_simulation_session import (
    LocalSimulationReportStore, OwnerSimulationSession, SessionStatus, SourceKind,
    inspect_owner_session_due, pause_session, resume_session, stop_session, tick_session,
)

SCHEMA_VERSION = "OBSIM_EXPLICIT_OWNER_REHEARSAL_INPUT_V1"
DESK_VERSION = "OBSIM_LOCAL_OWNER_REHEARSAL_DESK_V1"
ROOT_FIELDS = frozenset(("schema_version", "source_kind", "frame", "calendar", "decisions"))
FRAME_FIELDS = frozenset((
    "frame_id", "observed_at", "symbol", "instrument_kind", "contract_id",
    "mark_price", "underlying_price", "source_reference",
))
CALENDAR_FIELDS = frozenset((
    "market", "exchange_timezone", "trading_date", "day_status",
    "calendar_authority", "calendar_reference", "calendar_payload",
    "premarket_open", "regular_open", "regular_close", "after_hours_close",
))
DECISION_FIELDS = frozenset((
    "decision_id", "action", "strategy", "reason", "quantity", "evidence_refs",
))
LOCAL_KINDS = (SourceKind.SYNTHETIC, SourceKind.HISTORICAL)


def _exact(value: object, keys: frozenset[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != keys:
        raise ValueError(f"{name} requires exact explicit fields")
    return value


def _text(value: object, name: str) -> str:
    if type(value) is not str or not value.strip() or len(value) > 512:
        raise ValueError(f"{name} requires nonempty bounded text")
    return value.strip()


def _aware(value: object, name: str) -> datetime:
    if type(value) is not str:
        raise ValueError(f"{name} requires explicit aware ISO time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} requires explicit aware ISO time") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} requires explicit aware ISO time")
    return parsed


def _positive_number(value: object, name: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} requires finite positive numeric simulation input")
    return float(value)


def build_explicit_owner_rehearsal_step(
    payload: Mapping[str, object], *, source_kind: SourceKind,
) -> ReplayStep:
    """Build only from all fields explicitly declared; never invent a price or decision.

    OBTIME verifies the constructed receipt's internal integrity, not external
    calendar/market-source authenticity. No LIVE_OBSERVED user JSON is accepted
    here; that category needs a distinct authenticated source adapter.
    """
    if source_kind not in LOCAL_KINDS or not isinstance(source_kind, SourceKind):
        raise ValueError("owner local input supports historical/synthetic simulation only")
    raw = _exact(payload, ROOT_FIELDS, "owner rehearsal input")
    if raw["schema_version"] != SCHEMA_VERSION or raw["source_kind"] != source_kind.value:
        raise ValueError("owner rehearsal schema/source kind mismatch")
    frame = _exact(raw["frame"], FRAME_FIELDS, "market frame")
    calendar = _exact(raw["calendar"], CALENDAR_FIELDS, "calendar")
    supplied = _exact(
        raw["decisions"], frozenset(lane.value for lane in SimulationLane),
        "three explicit lane decisions",
    )
    observed = _aware(frame["observed_at"], "frame observed_at")
    if calendar["day_status"] != "OPEN":
        raise ValueError("replay needs explicitly declared open historical/synthetic day")
    authority = _text(calendar["calendar_authority"], "calendar authority")
    if not authority.startswith("OWNER_DECLARED_"):
        raise ValueError("calendar requires owner-declared unauthenticated classification")
    try:
        trading_date = date.fromisoformat(_text(calendar["trading_date"], "trading date"))
    except ValueError as exc:
        raise ValueError("trading date requires ISO date") from exc
    if type(calendar["calendar_payload"]) is not dict:
        raise ValueError("calendar requires explicit owner-declared payload")
    time = build_market_schedule(
        market=_text(calendar["market"], "market"),
        exchange_timezone=_text(calendar["exchange_timezone"], "exchange timezone"),
        trading_date=trading_date, day_status="OPEN",
        calendar_authority=authority,
        calendar_reference=_text(calendar["calendar_reference"], "calendar reference"),
        calendar_payload=calendar["calendar_payload"],
        premarket_open=_aware(calendar["premarket_open"], "premarket open"),
        regular_open=_aware(calendar["regular_open"], "regular open"),
        regular_close=_aware(calendar["regular_close"], "regular close"),
        after_hours_close=_aware(calendar["after_hours_close"], "after-hours close"),
    )
    instrument = build_simulation_instrument(
        symbol=_text(frame["symbol"], "symbol"),
        instrument_kind=_text(frame["instrument_kind"], "instrument kind"),
        contract_id=None if frame["contract_id"] is None else _text(frame["contract_id"], "contract id"),
    )
    if instrument.instrument_kind == "STOCK" and frame["contract_id"] is not None:
        raise ValueError("stock rehearsal cannot silently discard supplied contract id")
    market_frame = build_market_frame(
        frame_id=_text(frame["frame_id"], "frame id"),
        observed_at=observed.isoformat(), instrument=instrument,
        mark_price=_positive_number(frame["mark_price"], "mark price"),
        underlying_price=None if frame["underlying_price"] is None
        else _positive_number(frame["underlying_price"], "underlying price"),
        source_reference=_text(frame["source_reference"], "source reference"),
    )
    decisions: list[ReplayDecision] = []
    for lane in SimulationLane:
        item = _exact(supplied[lane.value], DECISION_FIELDS, "explicit lane decision")
        action = SimulationAction(_text(item["action"], "simulation action"))
        if lane is SimulationLane.EXPERIMENTAL and action in (
            SimulationAction.OPEN, SimulationAction.CLOSE,
        ):
            raise ValueError("local rehearsal cannot bypass Experimental CAPSIM policy")
        quantity = item["quantity"]
        if type(quantity) is not int or quantity < 0:
            raise ValueError("simulation quantity must be a nonnegative integer")
        refs = item["evidence_refs"]
        if type(refs) is not list or not all(
            type(ref) is str and ref.strip() and len(ref) <= 512 for ref in refs
        ):
            raise ValueError("decision evidence refs must be explicit bounded strings")
        decisions.append(ReplayDecision(
            lane=lane, decision_id=_text(item["decision_id"], "decision id"),
            action=action, strategy=_text(item["strategy"], "strategy"),
            reason=_text(item["reason"], "decision reason"),
            quantity=quantity, evidence_refs=tuple(refs),
        ))
    return ReplayStep(
        frame=market_frame,
        market_time=build_canonical_market_time(schedule=time, observed_at=observed),
        decisions=tuple(decisions),
    )


class LocalOwnerRehearsalDesk:
    """An in-process owner-driven controller for a future protected active UI.

    Callers must supply an already scoped fresh harness and owner-approved
    private store. Nothing in this class authenticates a person, issues grants,
    polls providers or schedules a tick. Failure leaves the session unchanged.
    """

    def __init__(
        self, session: OwnerSimulationSession, store: LocalSimulationReportStore,
    ) -> None:
        if (
            not isinstance(session, OwnerSimulationSession)
            or session.source_kind not in LOCAL_KINDS
            or not isinstance(store, LocalSimulationReportStore)
        ):
            raise ValueError("local desk needs accepted historical/synthetic session and store")
        self._session = session
        self._store = store

    @property
    def session(self) -> OwnerSimulationSession:
        return self._session

    def view(self, *, now: datetime) -> dict[str, object]:
        due = inspect_owner_session_due(self._session, now=now)
        last = self._session.reports[-1] if self._session.reports else None
        return {
            "authority": DESK_VERSION,
            "session_id": self._session.session_id,
            "state": self._session.status.value,
            "declared_source_kind": self._session.source_kind.value,
            "source_provider_authenticated": False,
            "owner_authenticated_here": False,
            "due": due,
            "last_report_hash": last["report_hash"] if last else None,
            "accepted_ticks": len(self._session.reports),
            "simulation_only": True,
            "broker_submission": False,
            "capital_movement": False,
            "manual_live_unlock": False,
            "hybrid_unlock": False,
            "automated_unlock": False,
            "unattended_timer": False,
        }

    def submit_explicit_input(self, payload: Mapping[str, object], *, now: datetime) -> dict[str, object]:
        if inspect_owner_session_due(self._session, now=now)["state"] != "READY_FOR_EXPLICIT_INPUT":
            raise ValueError("owner desk is not due for an explicit replay input")
        step = build_explicit_owner_rehearsal_step(
            payload, source_kind=self._session.source_kind,
        )
        next_session = tick_session(self._session, step, now=now, store=self._store)
        self._session = next_session
        return self.view(now=now)

    def pause(self) -> None:
        self._session = pause_session(self._session)

    def resume(self, *, now: datetime) -> None:
        self._session = resume_session(self._session, now=now)

    def stop(self, *, now: datetime) -> dict[str, object]:
        next_session = stop_session(self._session, now=now, store=self._store)
        self._session = next_session
        return self._store.inspect_archive(self._session.session_id)


def explicit_owner_rehearsal_contract() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION, "desk_version": DESK_VERSION,
        "source_kinds": [kind.value for kind in LOCAL_KINDS],
        "explicit_owner_authored_three_lane_input": True,
        "external_calendar_or_market_provenance_authenticated": False,
        "live_observed_user_payload_admitted": False,
        "experimental_open_without_capsim": False,
        "automated_decision_or_price": False, "automatic_tick_scheduled": False,
        "hosted_route_or_tower_session_created": False,
        "simulation_only": True, "broker_submission": False,
        "capital_movement": False, "manual_live_unlock": False,
        "hybrid_unlock": False, "automated_unlock": False,
    }

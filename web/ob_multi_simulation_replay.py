"""Simulation-only, deterministic three-lane historical replay.

This is an orchestrator around OBSIM, OBTIME and CAPSIM, not a new fill or
decision engine. Caller-authored decisions are historical replay inputs, not
recommendations. No broker, execution, real capital or mode-unlock authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from web.ob_capital_simulation_authority import apply_experimental_open_with_capital_admission
from web.ob_market_time_authority import (
    CanonicalMarketTimeReceipt, MarketTimeState, verify_canonical_market_time_receipt,
)
from web.ob_multi_simulation_harness import (
    MultiSimulationHarness, SimulationAction, SimulationFillPolicy,
    SimulationLane, SimulationMarketFrame, apply_simulation_decision,
    bind_canonical_market_time_to_experimental, broadcast_market_frame,
    compare_simulation_lanes, lane_state, stable_hash, verify_lane_receipt_chain,
)

SCHEMA_VERSION = "OB_SIMULATION_REPLAY_V1"
SERVICE_VERSION = "OBSIM006_010_DETERMINISTIC_CAPITAL_GATED_REPLAY"
LANES = (SimulationLane.CONTROL, SimulationLane.INTEGRATED, SimulationLane.EXPERIMENTAL)


@dataclass(frozen=True)
class ReplayDecision:
    lane: SimulationLane
    decision_id: str
    action: SimulationAction
    strategy: str
    reason: str
    quantity: int = 0
    evidence_refs: tuple[str, ...] = ()
    declared_max_loss_amount: float | None = None
    risk_reference: str | None = None


@dataclass(frozen=True)
class ReplayStep:
    frame: SimulationMarketFrame
    market_time: CanonicalMarketTimeReceipt
    decisions: tuple[ReplayDecision, ...]


@dataclass(frozen=True)
class ReplayEvent:
    frame_id: str
    lane: SimulationLane
    decision_id: str
    action: SimulationAction
    status: str
    capital_assessment_id: str | None
    capital_admission_id: str | None


@dataclass(frozen=True)
class ReplayResult:
    harness: MultiSimulationHarness
    events: tuple[ReplayEvent, ...]
    report: dict[str, object]


def _instant(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("replay frame timestamp must be ISO-8601")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("replay frame timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("replay frame timestamp must have a timezone")
    return parsed.astimezone(timezone.utc)


def _validate_plan(harness: MultiSimulationHarness, steps: tuple[ReplayStep, ...]) -> None:
    if not isinstance(harness, MultiSimulationHarness):
        raise ValueError("replay requires the canonical OBSIM harness")
    if set(state.lane for state in harness.lanes) != set(LANES) or len(harness.lanes) != 3:
        raise ValueError("replay requires exactly the three isolated OBSIM lanes")
    if harness.market_frames or any(
        state.positions or state.trades or state.decisions or state.receipts
        or state.time_bindings or state.review_history
        for state in harness.lanes
    ):
        raise ValueError("replay requires a fresh harness; never silently reset existing history")
    if not steps:
        raise ValueError("replay needs at least one market frame")
    seen_frames: set[str] = set()
    seen_decisions: dict[SimulationLane, set[str]] = {lane: set() for lane in LANES}
    previous: datetime | None = None
    for step in steps:
        if not isinstance(step, ReplayStep) or not isinstance(step.frame, SimulationMarketFrame):
            raise ValueError("replay step/frame has invalid type")
        if not verify_canonical_market_time_receipt(step.market_time):
            raise ValueError("replay requires verified OBTIME receipt for every frame")
        if step.market_time.state is not MarketTimeState.RESOLVED:
            raise ValueError("replay requires resolved canonical market time")
        instant = _instant(step.frame.observed_at)
        if instant != step.market_time.observed_at_utc:
            raise ValueError("replay frame and canonical market time differ")
        if not isinstance(step.frame.frame_id, str) or not step.frame.frame_id.strip() or step.frame.frame_id in seen_frames:
            raise ValueError("replay frame IDs must be nonblank and unique")
        seen_frames.add(step.frame.frame_id)
        if previous is not None and instant <= previous:
            raise ValueError("replay frames must advance strictly in time")
        previous = instant
        if len(step.decisions) != 3 or {item.lane for item in step.decisions} != set(LANES):
            raise ValueError("replay requires exactly one explicit decision per lane and frame")
        for decision in step.decisions:
            if not isinstance(decision, ReplayDecision):
                raise ValueError("replay decision has invalid type")
            if not isinstance(decision.action, SimulationAction) or not isinstance(decision.lane, SimulationLane):
                raise ValueError("replay requires canonical action and lane enums")
            if not decision.decision_id.strip() or decision.decision_id in seen_decisions[decision.lane]:
                raise ValueError("replay decision ID must be nonblank and unique within lane")
            seen_decisions[decision.lane].add(decision.decision_id)
            if not decision.strategy.strip() or not decision.reason.strip():
                raise ValueError("replay requires explicit strategy and reason")
            if type(decision.quantity) is not int:
                raise ValueError("replay quantity must be an integer, not bool")
            if decision.action in (SimulationAction.OPEN, SimulationAction.CLOSE):
                if decision.quantity < 1:
                    raise ValueError("OPEN/CLOSE require positive quantity")
                if step.market_time.market_session.value != "REGULAR":
                    raise ValueError("replay trades require regular market session")
            elif decision.quantity != 0:
                raise ValueError("HOLD/SKIP cannot carry quantity")
            if decision.lane is not SimulationLane.EXPERIMENTAL and (
                decision.declared_max_loss_amount is not None or decision.risk_reference is not None
            ):
                raise ValueError("CAPSIM admission metadata belongs only to Experimental")
            if decision.action is not SimulationAction.OPEN and (
                decision.declared_max_loss_amount is not None or decision.risk_reference is not None
            ):
                raise ValueError("CAPSIM admission metadata belongs only to OPEN")


def replay_three_lanes(
    harness: MultiSimulationHarness,
    steps: Iterable[ReplayStep],
    *,
    effective_policy: dict[str, object] | None = None,
    fill_policy: SimulationFillPolicy = SimulationFillPolicy(),
) -> ReplayResult:
    """Replay one pre-authored historical schedule. Input stays untouched on failure.

    Experimental OPEN only delegates through CAPSIM's existing admission; a
    blocked admission leaves Experimental trades/positions unchanged and is
    returned as an explicit event, never silently converted into an OPEN.
    """
    plan = tuple(steps)
    _validate_plan(harness, plan)
    if any(
        any(d.lane is SimulationLane.EXPERIMENTAL and d.action is SimulationAction.OPEN
            for d in s.decisions) for s in plan
    ) and effective_policy is None:
        raise ValueError("Experimental OPEN requires CAPSIM effective policy")
    if effective_policy is not None and effective_policy.get("account_key") != harness.account_key:
        raise ValueError("replay effective policy crosses account boundary")
    initial_refs = tuple((lane.value, lane_state(harness, lane).build_ref) for lane in LANES)
    working = harness
    events: list[ReplayEvent] = []
    historical_receipts: list[CanonicalMarketTimeReceipt] = []
    for step in plan:
        working = broadcast_market_frame(working, step.frame)
        working = bind_canonical_market_time_to_experimental(
            working, frame=step.frame, market_time=step.market_time
        )
        historical_receipts.append(step.market_time)
        by_lane = {decision.lane: decision for decision in step.decisions}
        for lane in LANES:
            decision = by_lane[lane]
            assessment_id = None
            admission_id = None
            status = decision.action.value
            if lane is SimulationLane.EXPERIMENTAL and decision.action is SimulationAction.OPEN:
                working, admission, assessment = apply_experimental_open_with_capital_admission(
                    working,
                    effective_policy=effective_policy,
                    frame=step.frame,
                    market_time=step.market_time,
                    market_time_receipts=tuple(historical_receipts),
                    decision_id=decision.decision_id,
                    strategy=decision.strategy,
                    reason=decision.reason,
                    quantity=decision.quantity,
                    declared_max_loss_amount=decision.declared_max_loss_amount,
                    risk_reference=decision.risk_reference,
                    evidence_refs=decision.evidence_refs,
                    fill_policy=fill_policy,
                )
                assessment_id = assessment.assessment_id
                admission_id = admission.admission_id
                status = "ADMITTED" if admission.admitted else "REJECTED_" + assessment.state.value
            else:
                working = apply_simulation_decision(
                    working,
                    lane=lane,
                    frame=step.frame,
                    decision_id=decision.decision_id,
                    action=decision.action,
                    strategy=decision.strategy,
                    reason=decision.reason,
                    quantity=decision.quantity,
                    evidence_refs=decision.evidence_refs,
                    fill_policy=fill_policy,
                )
            events.append(ReplayEvent(
                frame_id=step.frame.frame_id, lane=lane, decision_id=decision.decision_id,
                action=decision.action, status=status,
                capital_assessment_id=assessment_id, capital_admission_id=admission_id,
            ))
    if tuple((lane.value, lane_state(working, lane).build_ref) for lane in LANES) != initial_refs:
        raise RuntimeError("replay changed a lane build reference")
    if not all(verify_lane_receipt_chain(lane_state(working, lane)) for lane in LANES):
        raise RuntimeError("replay produced invalid lane receipt chain")
    event_material = [
        dict(frame_id=e.frame_id, lane=e.lane.value, decision_id=e.decision_id,
             action=e.action.value, status=e.status,
             assessment_id=e.capital_assessment_id, admission_id=e.capital_admission_id)
        for e in events
    ]
    comparison = compare_simulation_lanes(working)
    report_material = {
        "schema_version": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "harness_id": working.harness_id,
        "account_key": working.account_key,
        "market_frame_ids": [frame.frame_id for frame in working.market_frames],
        "market_time_receipt_ids": [receipt.receipt_id for receipt in historical_receipts],
        "build_refs": initial_refs,
        "events": event_material,
        "comparison": comparison,
        "simulation_only": True,
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_unlock": False,
        "hybrid_unlock": False,
        "automated_unlock": False,
        "promotion_or_winner_selected": False,
    }
    report = {**report_material, "report_hash": stable_hash(report_material)}
    return ReplayResult(harness=working, events=tuple(events), report=report)


def replay_contract() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "three_explicit_isolated_lanes": True,
        "verified_obtime_each_frame": True,
        "strict_chronological_replay": True,
        "requires_fresh_harness": True,
        "existing_obsim_fill_math_only": True,
        "experimental_open_requires_existing_capsim_admission": True,
        "blocked_admission_never_opens_position": True,
        "no_source_feed_or_unattended_scheduler": True,
        "simulation_only": True,
        "broker_submission": False,
        "capital_movement": False,
        "automatic_contract_selection": False,
        "manual_live_unlock": False,
        "hybrid_unlock": False,
        "automated_unlock": False,
    }

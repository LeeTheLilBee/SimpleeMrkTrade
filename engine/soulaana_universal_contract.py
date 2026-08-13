from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "OBUX001"

TITLE = (
    "Soulaana Existing-System Canonicalization Contract"
)


CANONICAL_FIELDS = (
    "what_it_is",
    "what_it_means",
    "why_it_matters",
    "what_changed",
    "needs_attention",
    "can_wait",
    "next_action",
    "no_action_needed",
)


LEGACY_COMPATIBILITY_FIELDS = (
    "headline",
    "verdict",
    "assessment",
    "why",
    "risk",
    "next_action",
)


def _clean(value: Any) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip()


def _first(
    payload: Mapping[str, Any],
    *keys: str,
) -> tuple[str, str | None]:

    for key in keys:

        value = _clean(
            payload.get(
                key
            )
        )

        if value:

            return (
                value,
                key,
            )

    return (
        "",
        None,
    )


def _context_first(
    context: Mapping[str, Any],
    *keys: str,
) -> tuple[str, str | None]:

    for key in keys:

        value = _clean(
            context.get(
                key
            )
        )

        if value:

            return (
                value,
                f"context.{key}",
            )

    return (
        "",
        None,
    )


def _resolve(
    payload: Mapping[str, Any],
    context: Mapping[str, Any],
    payload_keys: tuple[str, ...],
    context_keys: tuple[str, ...],
    fallback: str,
) -> tuple[str, str, bool]:

    value, source = _first(
        payload,
        *payload_keys,
    )

    if value:

        return (
            value,
            source or "legacy",
            False,
        )

    value, source = _context_first(
        context,
        *context_keys,
    )

    if value:

        return (
            value,
            source or "context",
            False,
        )

    return (
        fallback,
        "safe_fallback",
        True,
    )


def infer_no_action_needed(
    payload: Mapping[str, Any],
) -> bool:

    explicit = payload.get(
        "no_action_needed"
    )

    if isinstance(
        explicit,
        bool,
    ):

        return explicit

    next_action = _clean(
        payload.get(
            "next_action"
        )
    ).lower()

    # Human-facing Soulaana language naturally carries punctuation.
    # Canonical meaning must not change because a sentence ends with
    # ".", "!", "?", ";", or ":".
    normalized_next_action = next_action.strip(
        " \\t\\r\\n.!?;:"
    )

    return normalized_next_action in {
        "no action",
        "no action needed",
        "continue monitoring",
        "keep watching",
        "monitor",
        "none",
    }


def canonicalize_soulaana_payload(
    payload: Mapping[str, Any] | None,
    *,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:

    legacy = dict(
        payload
        or {}
    )

    context = dict(
        context
        or {}
    )

    field_sources: dict[str, str] = {}

    source_gaps: list[str] = []


    what_it_is, source, gap = _resolve(
        legacy,
        context,
        (
            "what_it_is",
            "headline",
            "title",
            "subject",
        ),
        (
            "subject",
            "symbol",
            "room",
        ),
        "Soulaana reviewed this Observatory state.",
    )

    field_sources[
        "what_it_is"
    ] = source

    if gap:
        source_gaps.append(
            "what_it_is"
        )


    what_it_means, source, gap = _resolve(
        legacy,
        context,
        (
            "what_it_means",
            "assessment",
            "summary",
            "meaning",
        ),
        (
            "summary",
            "state_summary",
        ),
        "The source did not provide a complete plain-language meaning yet.",
    )

    field_sources[
        "what_it_means"
    ] = source

    if gap:
        source_gaps.append(
            "what_it_means"
        )


    why_it_matters, source, gap = _resolve(
        legacy,
        context,
        (
            "why_it_matters",
            "why",
            "decision_reason",
            "reason",
        ),
        (
            "why",
            "decision_reason",
        ),
        "The source did not provide a complete why-it-matters explanation yet.",
    )

    field_sources[
        "why_it_matters"
    ] = source

    if gap:
        source_gaps.append(
            "why_it_matters"
        )


    what_changed, source, gap = _resolve(
        legacy,
        context,
        (
            "what_changed",
            "change",
            "change_summary",
            "since_last_visit",
        ),
        (
            "what_changed",
            "change_summary",
        ),
        "No material change description was supplied by the source.",
    )

    field_sources[
        "what_changed"
    ] = source

    if gap:
        source_gaps.append(
            "what_changed"
        )


    needs_attention, source, gap = _resolve(
        legacy,
        context,
        (
            "needs_attention",
            "attention",
            "attention_reason",
            "risk",
        ),
        (
            "needs_attention",
            "attention_reason",
        ),
        "No specific attention requirement was supplied by the source.",
    )

    field_sources[
        "needs_attention"
    ] = source

    if gap:
        source_gaps.append(
            "needs_attention"
        )


    can_wait, source, gap = _resolve(
        legacy,
        context,
        (
            "can_wait",
            "can_wait_reason",
            "defer",
        ),
        (
            "can_wait",
            "can_wait_reason",
        ),
        "Lower-priority detail can stay closed until the main decision is clear.",
    )

    field_sources[
        "can_wait"
    ] = source

    if gap:
        source_gaps.append(
            "can_wait"
        )


    next_action, source, gap = _resolve(
        legacy,
        context,
        (
            "next_action",
            "action",
            "recommended_action",
        ),
        (
            "next_action",
            "recommended_action",
        ),
        "Continue monitoring.",
    )

    field_sources[
        "next_action"
    ] = source

    if gap:
        source_gaps.append(
            "next_action"
        )


    no_action_needed = infer_no_action_needed(
        legacy
    )


    canonical = {
        "what_it_is": what_it_is,
        "what_it_means": what_it_means,
        "why_it_matters": why_it_matters,
        "what_changed": what_changed,
        "needs_attention": needs_attention,
        "can_wait": can_wait,
        "next_action": next_action,
        "no_action_needed": no_action_needed,
    }


    legacy_compatibility = {
        key: legacy.get(
            key
        )
        for key in LEGACY_COMPATIBILITY_FIELDS
        if key in legacy
    }


    return {
        "package": PACKAGE,
        "title": TITLE,
        "canonical_schema_version": "soulaana_universal_v1",
        "canonical": canonical,
        "field_sources": field_sources,
        "source_gaps": source_gaps,
        "source_gap_count": len(
            source_gaps
        ),
        "source_complete": not source_gaps,
        "legacy_payload": legacy,
        "legacy_compatibility": legacy_compatibility,
        "legacy_fields_preserved": True,
        "parallel_soulaana_engine_created": False,
        "existing_soulaana_remains_authoritative": True,
        "gate_state": (
            "soulaana_existing_system_canonicalization_sealed"
        ),
        "recommendation": (
            "GO_FOR_SOULAANA_EXISTING_LAYER_BRIDGE"
        ),
    }

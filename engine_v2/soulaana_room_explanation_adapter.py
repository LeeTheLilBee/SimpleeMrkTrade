from __future__ import annotations

from typing import Any, Mapping

from engine.soulaana_context_permission_adapter import (
    apply_soulaana_context_permissions,
)

from engine.soulaana_universal_bridge import (
    build_universal_soulaana,
)


PACKAGE = "OBUX004"

TITLE = (
    "Soulaana Six-Room Explanation Coverage Adapter"
)


ROOM_CONTRACTS = {
    "Dashboard": {
        "core_question": (
            "What matters right now?"
        ),
        "lead": (
            "account health, attention, open positions, and what is worth watching"
        ),
    },
    "Market Map": {
        "core_question": (
            "Where is the opportunity?"
        ),
        "lead": (
            "market movement, strengthening areas, weakening areas, and why they matter"
        ),
    },
    "Symbol Page": {
        "core_question": (
            "What is happening with this company?"
        ),
        "lead": (
            "setup meaning, drivers, confirmation, invalidation, and what comes next"
        ),
    },
    "Trade Center": {
        "core_question": (
            "What am I considering or doing?"
        ),
        "lead": (
            "trade thesis, readiness, risk, conditions, and required owner action"
        ),
    },
    "Review Center": {
        "core_question": (
            "What happened and what did we learn?"
        ),
        "lead": (
            "result, thesis quality, execution quality, lessons, and follow-up"
        ),
    },
    "Owner Console": {
        "core_question": (
            "What needs owner control or oversight?"
        ),
        "lead": (
            "beta controls, safety state, diagnostics, system health, and owner decisions"
        ),
    },
}


SURFACE_ORDER = (
    "soulaana",
    "key_facts",
    "attention_and_actions",
    "visuals",
    "evidence",
)


def build_room_soulaana_experience(
    room: str,
    state: Mapping[str, Any],
    context: Mapping[str, Any],
) -> dict[str, Any]:

    if room not in ROOM_CONTRACTS:

        return {
            "package": PACKAGE,
            "title": TITLE,
            "gate_state": (
                "soulaana_room_adapter_hold"
            ),
            "room": room,
            "allowed": False,
            "failures": [
                "unknown_room"
            ],
            "recommendation": (
                "NO_GO_UNKNOWN_OB_ROOM"
            ),
        }


    state = dict(
        state
        or {}
    )

    context = dict(
        context
        or {}
    )

    context[
        "room"
    ] = room


    existing_soulaana = state.get(
        "soulaana"
    )

    source_soulaana_empty = (
        isinstance(
            existing_soulaana,
            dict,
        )
        and
        not existing_soulaana
    )


    existing_payload = (
        existing_soulaana
        if isinstance(
            existing_soulaana,
            dict,
        )
        and existing_soulaana
        else None
    )


    bridge = build_universal_soulaana(
        {
            **state,
            **context,
            "subject": (
                state.get(
                    "subject"
                )
                or
                state.get(
                    "symbol"
                )
                or
                room
            ),
        },
        emotional_state=context.get(
            "emotional_state"
        ),
        existing_payload=existing_payload,
    )


    permission = (
        apply_soulaana_context_permissions(
            bridge,
            context,
        )
    )


    canonical = (
        bridge
        .get(
            "universal",
            {}
        )
        .get(
            "canonical",
            {}
        )
    )


    sections = [
        {
            "id": "soulaana",
            "label": "Soulaana",
            "position": 1,
            "default_open": True,
            "content": canonical,
        },
        {
            "id": "key_facts",
            "label": "Key facts",
            "position": 2,
            "default_open": True,
            "content": list(
                state.get(
                    "key_facts"
                )
                or []
            ),
        },
        {
            "id": "attention_and_actions",
            "label": "What needs you",
            "position": 3,
            "default_open": True,
            "content": list(
                state.get(
                    "actions"
                )
                or []
            ),
        },
        {
            "id": "visuals",
            "label": "Visual context",
            "position": 4,
            "default_open": True,
            "content": list(
                state.get(
                    "visuals"
                )
                or []
            ),
        },
        {
            "id": "evidence",
            "label": "Show me why",
            "position": 5,
            "default_open": False,
            "content": list(
                state.get(
                    "technical_evidence"
                )
                or []
            ),
        },
    ]


    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "soulaana_six_room_coverage_adapter_sealed"
            if permission.get(
                "allowed"
            )
            else
            "soulaana_six_room_coverage_adapter_permission_hold"
        ),
        "room": room,
        "core_question": (
            ROOM_CONTRACTS[
                room
            ][
                "core_question"
            ]
        ),
        "room_lead": (
            ROOM_CONTRACTS[
                room
            ][
                "lead"
            ]
        ),
        "allowed": permission.get(
            "allowed"
        ),
        "permission": permission,
        "bridge": bridge,
        "source_soulaana_empty": (
            source_soulaana_empty
        ),
        "soulaana_leads_surface": True,
        "raw_data_precedes_interpretation": False,
        "engineering_plumbing_leads_normal_surface": False,
        "evidence_collapsed_by_default": True,
        "evidence_label": "Show me why",
        "surface_order": list(
            SURFACE_ORDER
        ),
        "sections": sections,
        "recommendation": (
            "GO_FOR_SOULAANA_COMPLETENESS_CALM_GATE"
            if permission.get(
                "allowed"
            )
            else
            "HOLD_ROOM_PERMISSION"
        ),
    }

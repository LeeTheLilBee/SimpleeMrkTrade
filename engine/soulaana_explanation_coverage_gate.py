from __future__ import annotations

import json

from pathlib import Path
from typing import Any, Mapping, Sequence


PACKAGE = "OBUX005"

TITLE = (
    "Soulaana Explanation Completeness and Calm-State Coverage Gate"
)


REQUIRED_CANONICAL_FIELDS = (
    "what_it_is",
    "what_it_means",
    "why_it_matters",
    "what_changed",
    "needs_attention",
    "can_wait",
    "next_action",
    "no_action_needed",
)


def assess_canonical_explanation(
    payload: Mapping[str, Any],
) -> dict[str, Any]:

    missing = []

    for field in REQUIRED_CANONICAL_FIELDS:

        if field not in payload:

            missing.append(
                field
            )

            continue

        if (
            field != "no_action_needed"
            and
            not str(
                payload.get(
                    field
                )
                or ""
            ).strip()
        ):

            missing.append(
                field
            )


    return {
        "coverage_ready": (
            not missing
        ),
        "missing_fields": missing,
        "required_fields": list(
            REQUIRED_CANONICAL_FIELDS
        ),
    }


def enforce_new_surface_coverage(
    payloads: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:

    failures = []

    for index, payload in enumerate(
        payloads
    ):

        result = assess_canonical_explanation(
            payload
        )

        if not result[
            "coverage_ready"
        ]:

            failures.append(
                {
                    "index": index,
                    "missing_fields": (
                        result[
                            "missing_fields"
                        ]
                    ),
                }
            )


    return {
        "coverage_gate_ready": (
            not failures
        ),
        "failures": failures,
        "new_user_facing_states_may_ship_empty": False,
    }


def evaluate_calm_state(
    items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:

    normalized = []

    for item in items:

        normalized.append(
            {
                "label": str(
                    item.get(
                        "label"
                    )
                    or ""
                ).strip(),
                "interesting": bool(
                    item.get(
                        "interesting",
                        False,
                    )
                ),
                "actionable": bool(
                    item.get(
                        "actionable",
                        False,
                    )
                ),
                "urgent": bool(
                    item.get(
                        "urgent",
                        False,
                    )
                ),
            }
        )


    urgent = [
        item
        for item in normalized
        if (
            item[
                "actionable"
            ]
            and
            item[
                "urgent"
            ]
        )
    ]


    actionable = [
        item
        for item in normalized
        if item[
            "actionable"
        ]
    ]


    interesting_only = [
        item
        for item in normalized
        if (
            item[
                "interesting"
            ]
            and
            not item[
                "actionable"
            ]
        )
    ]


    if urgent:

        state = (
            "NEEDS_ATTENTION_NOW"
        )

        message = (
            "Something needs your attention now. "
            "I will show you that before lower-priority information."
        )

        no_action_needed = False

    elif actionable:

        state = (
            "ACTION_AVAILABLE_NOT_URGENT"
        )

        message = (
            "There is an available action, but it does not require panic or urgency."
        )

        no_action_needed = False

    else:

        state = (
            "CALM_NO_ACTION"
        )

        no_action_needed = True

        if interesting_only:

            message = (
                "There are things worth watching, but nothing needs you right now."
            )

        else:

            message = (
                "Nothing needs you right now."
            )


    return {
        "state": state,
        "message": message,
        "no_action_needed": (
            no_action_needed
        ),
        "interesting_count": len(
            interesting_only
        ),
        "actionable_count": len(
            actionable
        ),
        "urgent_count": len(
            urgent
        ),
        "interesting_equals_actionable": False,
        "urgency_inflation_allowed": False,
    }


def _walk_for_soulaana(
    value: Any,
    path: str,
    result: dict[str, Any],
) -> None:

    if isinstance(
        value,
        dict,
    ):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
                if path
                else str(
                    key
                )
            )

            if key == "soulaana":

                result[
                    "soulaana_slots"
                ] += 1

                if isinstance(
                    child,
                    dict,
                ):

                    if child:

                        result[
                            "populated_soulaana_slots"
                        ] += 1

                    else:

                        result[
                            "empty_soulaana_slots"
                        ] += 1

                        if len(
                            result[
                                "empty_paths"
                            ]
                        ) < 50:

                            result[
                                "empty_paths"
                            ].append(
                                child_path
                            )

                else:

                    result[
                        "non_mapping_soulaana_slots"
                    ] += 1

            _walk_for_soulaana(
                child,
                child_path,
                result,
            )


    elif isinstance(
        value,
        list,
    ):

        for index, child in enumerate(
            value
        ):

            _walk_for_soulaana(
                child,
                f"{path}[{index}]",
                result,
            )


def scan_json_soulaana_coverage(
    path: str | Path,
) -> dict[str, Any]:

    source = Path(
        path
    )

    result = {
        "path": str(
            source
        ),
        "exists": source.exists(),
        "soulaana_slots": 0,
        "populated_soulaana_slots": 0,
        "empty_soulaana_slots": 0,
        "non_mapping_soulaana_slots": 0,
        "empty_paths": [],
        "read_error": None,
    }


    if not source.exists():

        return result


    try:

        value = json.loads(
            source.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )

    except Exception as exc:

        result[
            "read_error"
        ] = (
            f"{type(exc).__name__}: {exc}"
        )

        return result


    _walk_for_soulaana(
        value,
        "",
        result,
    )


    return result


def build_legacy_coverage_baseline(
    paths: Sequence[str | Path],
) -> dict[str, Any]:

    files = [
        scan_json_soulaana_coverage(
            path
        )
        for path in paths
    ]


    total_slots = sum(
        item[
            "soulaana_slots"
        ]
        for item in files
    )

    populated = sum(
        item[
            "populated_soulaana_slots"
        ]
        for item in files
    )

    empty = sum(
        item[
            "empty_soulaana_slots"
        ]
        for item in files
    )


    return {
        "files": files,
        "total_soulaana_slots": (
            total_slots
        ),
        "populated_soulaana_slots": (
            populated
        ),
        "empty_soulaana_slots": (
            empty
        ),
        "legacy_coverage_debt_detected": (
            empty > 0
        ),
        "legacy_empty_slots_are_not_silently_claimed_complete": True,
    }


def build_obux005_status(
    legacy_baseline: Mapping[str, Any],
) -> dict[str, Any]:

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "soulaana_explanation_completeness_calm_gate_sealed"
        ),
        "contract_ready": True,
        "legacy_baseline": dict(
            legacy_baseline
        ),
        "new_surface_empty_explanation_allowed": False,
        "legacy_debt_may_be_repaired_incrementally": True,
        "interesting_equals_actionable": False,
        "urgency_inflation_allowed": False,
        "no_action_is_first_class_outcome": True,
        "recommendation": (
            "GO_FOR_DASHBOARD_SOULAANA_APPLICATION"
        ),
    }

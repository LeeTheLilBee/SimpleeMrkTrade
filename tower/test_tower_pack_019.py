
# =============================================================================
# The Tower — Pack 019 Test
# =============================================================================

import json
from pathlib import Path

from tower.security_command_view import (
    build_security_command_view,
    save_security_command_view,
    get_security_command_cards_api,
)


def _print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _print_json(payload):
    print(json.dumps(payload, indent=2, sort_keys=True))


def main():
    _print_header("BUILD SECURITY COMMAND VIEW")
    view = build_security_command_view(include_raw_groups=False)

    _print_json({
        "view_name": view.get("view_name"),
        "state": view.get("status", {}).get("state"),
        "state_label": view.get("status", {}).get("label"),
        "headline": view.get("hero", {}).get("headline"),
        "metrics": view.get("metrics", {}),
        "summary_cards": len(view.get("summary_cards", [])),
        "top_review_groups": len(view.get("top_review_groups", [])),
        "primary_owner_tasks": len(view.get("primary_owner_tasks", [])),
    })

    _print_header("HERO")
    _print_json(view.get("hero", {}))

    _print_header("METRIC CARDS")
    _print_json(view.get("summary_cards", []))

    _print_header("PRIMARY OWNER TASKS")
    _print_json(view.get("primary_owner_tasks", []))

    _print_header("LANE COUNTS")
    lanes = view.get("lanes", {})
    _print_json({
        "urgent": len(lanes.get("urgent", [])),
        "high": len(lanes.get("high", [])),
        "watch": len(lanes.get("watch", [])),
        "other": len(lanes.get("other", [])),
    })

    _print_header("SAVE SECURITY COMMAND VIEW")
    saved = save_security_command_view()
    _print_json(saved)

    _print_header("CARDS API SHAPE")
    api_shape = get_security_command_cards_api()
    _print_json({
        "view_name": api_shape.get("view_name"),
        "hero": api_shape.get("hero"),
        "metrics": api_shape.get("metrics"),
        "summary_cards_count": len(api_shape.get("summary_cards", [])),
        "primary_owner_tasks_count": len(api_shape.get("primary_owner_tasks", [])),
        "lane_names": sorted(list((api_shape.get("lanes") or {}).keys())),
        "api_shape_version": api_shape.get("api_shape_version"),
    })

    assert view.get("view_name") == "The Tower Security Command View"
    assert isinstance(view.get("summary_cards"), list)
    assert isinstance(view.get("lanes"), dict)
    assert isinstance(view.get("primary_owner_tasks"), list)
    assert saved.get("ok") is True
    assert Path(saved.get("path")).exists()

    _print_header("PACK 019 RESULT")
    _print_json({
        "pack": "019",
        "status": "passed",
        "human_reason": "Security Command View created a clean UI/API-ready shape for The Tower dashboard.",
    })


if __name__ == "__main__":
    main()

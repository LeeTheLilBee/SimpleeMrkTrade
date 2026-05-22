
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_locked_state_transition_checkpoint() -> Dict[str, Any]:
    from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
    from tower.ob_privacy_wall_checkpoint import build_ob_privacy_wall_checkpoint
    from tower.locked_state_templates import (
        render_route_locked_response,
        render_object_locked_response,
        render_mode_locked_response,
        render_export_locked_response,
        render_unmapped_locked_response,
    )
    from web.app import app, _pack068_tower_locked_response

    smoke = run_ob_privacy_wall_smoke()
    privacy_checkpoint = build_ob_privacy_wall_checkpoint()

    # Direct template/variant proof.
    route_html, route_status, route_payload = render_route_locked_response(
        path="/signals",
        reason_code="ob_clearance_level_too_low",
        human_reason="Signals needs confidential clearance.",
        user_id="beta_001",
    )
    object_html, object_status, object_payload = render_object_locked_response(
        object_type="symbol",
        object_id="AAPL",
        path="/signals/AAPL",
        reason_code="parent_route_clearance_failed",
        human_reason="The parent route was not cleared.",
        user_id="beta_001",
    )
    mode_html, mode_status, mode_payload = render_mode_locked_response(
        mode_name="live_automated",
        reason_code="ob_mode_automation_authorization_missing",
        human_reason="Automated live mode needs explicit automation authorization.",
        user_id="owner_solice",
        required_actions=["owner_automation_authorization", "kill_switch_check"],
    )
    export_html, export_status, export_payload = render_export_locked_response(
        export_id="export_070",
        path="/export",
        user_id="beta_001",
    )
    unmapped_html, unmapped_status, unmapped_payload = render_unmapped_locked_response(
        path="/unmapped-secret",
        object_type="mystery",
        object_id="secret_070",
        user_id="owner_solice",
    )

    helper_html, helper_status = _pack068_tower_locked_response(
        lock_type="route",
        path="/signals?tower_keycard=SHOULD_NOT_SURVIVE",
        user_id="beta_001",
        reason_code="ob_clearance_level_too_low",
        human_reason="Signals needs confidential clearance.",
        required_actions=["upgrade_clearance", "owner_review"],
        soulaana_translation="Soulaana: This corridor is not public. The Tower held the line.",
    )

    client = app.test_client()
    preview = client.get("/tower/polished-locked-preview?path=/signals?tower_keycard=SHOULD_NOT_SURVIVE")
    preview_html = preview.get_data(as_text=True)

    html_bundle = "\n".join([
        route_html,
        object_html,
        mode_html,
        export_html,
        unmapped_html,
        helper_html,
        preview_html,
    ])

    locked_page_proof = {
        "route_status": route_status,
        "object_status": object_status,
        "mode_status": mode_status,
        "export_status": export_status,
        "unmapped_status": unmapped_status,
        "helper_status": helper_status,
        "preview_status": preview.status_code,
        "has_tower": "The Tower" in html_bundle,
        "has_clearance_gate": "Clearance Gate" in html_bundle,
        "has_soulaana": "Soulaana:" in html_bundle,
        "has_route_variant": "Observatory Corridor Locked" in route_html,
        "has_object_variant": "Symbol Locked" in object_html and "AAPL" in object_html,
        "has_mode_variant": "Live Automated Locked" in mode_html,
        "has_export_variant": "Export Locked" in export_html,
        "has_unmapped_variant": "Unmapped Corridor Locked" in unmapped_html,
        "no_keycard_query": "tower_keycard=" not in html_bundle,
        "no_raw_token_assignment": "raw_token=" not in html_bundle and '"raw_token":' not in html_bundle,
        "no_test_secret": "SHOULD_NOT_SURVIVE" not in html_bundle,
    }

    locked_pages_ok = all(locked_page_proof.values())

    built_packs = [
        {
            "pack": "066",
            "name": "Polished locked-state template system",
            "plain": "Reusable Tower-branded locked page template exists.",
        },
        {
            "pack": "067",
            "name": "Route/object/mode/export/unmapped variants",
            "plain": "Each denial type gets smarter wording and context.",
        },
        {
            "pack": "068",
            "name": "web/app.py locked response helper",
            "plain": "Flask can call the Tower-branded locked response helper.",
        },
        {
            "pack": "069",
            "name": "Privacy wall polished locked-page proof",
            "plain": "Smoke/checkpoint prove the polished locked pages safely render.",
        },
        {
            "pack": "070",
            "name": "Locked-state transition checkpoint",
            "plain": "Close this block before wiring UI POST actions.",
        },
    ]

    next_block = [
        {
            "pack": "071",
            "item": "Wire object inbox UI POST endpoint",
            "plain": "Make the Security Command forms actually call note/review/resolve/ignore backend actions.",
        },
        {
            "pack": "072",
            "item": "Add UI action audit receipts",
            "plain": "Every owner button click should create its own admin/action receipt.",
        },
        {
            "pack": "073",
            "item": "Update smoke/checkpoint for UI endpoint workflow",
            "plain": "Prove forms can submit actions and change object inbox status safely.",
        },
        {
            "pack": "074",
            "item": "Surface Archive Vault handoff summary in Tower UI/status",
            "plain": "Show queued evidence handoffs in the Tower command view.",
        },
        {
            "pack": "075",
            "item": "Save/transition checkpoint",
            "plain": "Close the UI action endpoint block cleanly.",
        },
    ]

    ok = (
        smoke.get("ok") is True
        and privacy_checkpoint.get("ok") is True
        and locked_pages_ok
    )

    return {
        "ok": ok,
        "pack": "070",
        "generated_at": _utc_now(),
        "readiness_score": 100 if ok else 90,
        "readiness_label": "Ready for UI endpoint wiring" if ok else "Needs repair before UI endpoint wiring",
        "smoke_ok": smoke.get("ok"),
        "smoke_failures": smoke.get("failures"),
        "privacy_checkpoint_ok": privacy_checkpoint.get("ok"),
        "privacy_checkpoint_label": privacy_checkpoint.get("readiness_label"),
        "polished_locked_pages_ready": privacy_checkpoint.get("polished_locked_pages_ready"),
        "locked_page_proof": locked_page_proof,
        "built_packs": built_packs,
        "next_block": next_block,
        "current_boundary": {
            "done": "Templates, variants, helper, preview route, and smoke/checkpoint proof are complete.",
            "not_done_yet": "Actual older deny paths are not all replaced yet. Next block wires owner action POST endpoint first.",
            "why": "We avoid changing too many live deny paths at once. The helper is proven; wiring can happen safely in controlled packs.",
        },
        "soulaana_translation": "Soulaana: The locked walls are polished and proven. Next we make the owner buttons actually move the review queue.",
        "human_reason": "Locked-state transition checkpoint is ready before UI endpoint wiring.",
    }


if __name__ == "__main__":
    import json

    result = build_locked_state_transition_checkpoint()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("Locked-state transition checkpoint failed.")

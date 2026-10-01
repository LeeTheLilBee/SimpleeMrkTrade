"""
Tower Access Home UI v2.

Simplee front door / owner control room surface.

This module is UI/presentation-focused. It does not unlock
dangerous actions, deployment, broker submission, live trading,
capital movement, or direct Vault writes.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List

from flask import render_template_string, request, session


TOWER_UI_V2_THEME = {
    "name": "Simplee Tower Black Glass",
    "primary": "obsidian_black",
    "secondary": "deep_royal_violet",
    "owner_accent": "soft_gold",
    "glass": True,
    "blue_minimized": True,
    "portal_glow_only_on_launch": True,
}


APP_CARDS = [
    {
        "id": "observatory",
        "category": "business",
        "mark": "OB",
        "name": "The Observatory",
        "subtitle": "Market intelligence",
        "status": "Live door",
        "tone": "live",
        "href": "/tower/launch/observatory",
        "primary_action": "Enter",
        "description": "Soulaana: market, research, risk, and trading review live here.",
        "requires_step_up": True,
    },
    {
        "id": "teller",
        "category": "business",
        "mark": "TL",
        "name": "The Teller",
        "subtitle": "Money operations",
        "status": "Live door",
        "tone": "live",
        "href": "/tower/launch/teller",
        "primary_action": "Enter",
        "description": "Soulaana: payroll, payments, records, and money-side workflow.",
        "requires_step_up": True,
    },
    {
        "id": "grounds",
        "category": "business",
        "mark": "GR",
        "name": "The Grounds",
        "subtitle": "Property operations",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: tenants, rent, maintenance, and owned-property operations.",
        "requires_step_up": True,
    },
    {
        "id": "buybox",
        "category": "business",
        "mark": "BB",
        "name": "BuyBox",
        "subtitle": "Acquisition intelligence",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: find, compare, qualify, and explain acquisition opportunities.",
        "requires_step_up": True,
    },
    {
        "id": "vault",
        "category": "business",
        "mark": "AV",
        "name": "Archive Vault",
        "subtitle": "Evidence & records",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: sealed evidence, receipts, records, and immutable proof.",
        "requires_step_up": True,
    },
    {
        "id": "clouds",
        "category": "business",
        "mark": "SC",
        "name": "Simplee Cloud",
        "subtitle": "Private storage",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: private storage, recovery, and infrastructure status.",
        "requires_step_up": True,
    },
    {
        "id": "simplee_on_the_go",
        "category": "business",
        "mark": "ATM",
        "name": "SimpleeOnTheGo",
        "subtitle": "ATM operations",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: ATM acquisition, routes, operations, and expansion.",
        "requires_step_up": True,
    },
    {
        "id": "crown_calendar",
        "category": "apps",
        "mark": "CC",
        "name": "Crown Calendar",
        "subtitle": "Calendar",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: your first consumer app after the shared app foundation.",
        "requires_step_up": False,
    },
    {
        "id": "beauty",
        "category": "apps",
        "mark": "SB",
        "name": "Simplee Beauty",
        "subtitle": "Beauty & booking",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: beauty organization, bookings, and later Teller-led payments.",
        "requires_step_up": False,
    },
    {
        "id": "sunday_table",
        "category": "apps",
        "mark": "ST",
        "name": "Sunday Table",
        "subtitle": "Food & gathering",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: recipes, meals, gathering, and table traditions.",
        "requires_step_up": False,
    },
    {
        "id": "our_oral_traditions",
        "category": "apps",
        "mark": "OT",
        "name": "Our Oral Traditions",
        "subtitle": "Stories & memory",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: preserve family stories, voices, and cultural memory.",
        "requires_step_up": False,
    },
    {
        "id": "cookout_ready",
        "category": "apps",
        "mark": "CR",
        "name": "Cookout Ready",
        "subtitle": "Cookout utility",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: get the food, people, timing, and setup together.",
        "requires_step_up": False,
    },
    {
        "id": "sunday_best",
        "category": "apps",
        "mark": "SB",
        "name": "Sunday Best",
        "subtitle": "Wardrobe",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: outfits, wardrobe planning, and getting dressed with less friction.",
        "requires_step_up": False,
    },
    {
        "id": "the_village",
        "category": "apps",
        "mark": "TV",
        "name": "The Village",
        "subtitle": "Family coordination",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: private household and family coordination.",
        "requires_step_up": False,
    },
    {
        "id": "simplee_fitness",
        "category": "apps",
        "mark": "SF",
        "name": "Simplee Fitness",
        "subtitle": "Fitness",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: workouts, routines, progress, and personal fitness.",
        "requires_step_up": False,
    },
    {
        "id": "simplee_skincare",
        "category": "apps",
        "mark": "SS",
        "name": "Simplee Skincare",
        "subtitle": "Skincare",
        "status": "Building",
        "tone": "building",
        "href": None,
        "primary_action": "Not connected yet",
        "description": "Soulaana: routines, products, progress, and skincare organization.",
        "requires_step_up": False,
    },
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def receipt_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(
        canonical_json(payload).encode("utf-8")
    ).hexdigest()


def active_return_receipt() -> Dict[str, Any] | None:
    value = session.get(
        "tower_ob_return_receipt"
    )

    if isinstance(value, dict):
        return deepcopy(value)

    return None


# Client navigation supplies this as a display hint, not evidence of location.
# Bound it so no caller can inject arbitrary content into the Tower session/UI.
OB_RETURN_ROOM_LABELS = frozenset({
    "Dashboard", "Market Map", "Trade Center", "Review Center",
    "Owner Console", "Owner Dashboard", "Symbol Page", "Market Data Desk",
})


def record_ob_return_receipt(
    *,
    source: str = "observatory",
    last_room: str | None = None,
) -> Dict[str, Any]:
    safe_last_room = (
        last_room if isinstance(last_room, str) and last_room in OB_RETURN_ROOM_LABELS
        else "unknown"
    )
    owner_id = session.get(
        "owner_id"
    )

    role = session.get(
        "tower_role"
    )

    receipt = {
        "receipt_type": "tower_ob_return",
        "source": source,
        "destination": "/tower/access-home",
        "owner_id": owner_id,
        "role": role,
        "owner_session_preserved": bool(owner_id and role == "owner"),
        "clearance_preserved": role == "owner",
        "last_room": safe_last_room,
        "returned_at": utc_now().isoformat(),
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "dangerous_action_unlocked": False,
    }

    receipt["receipt_hash"] = receipt_hash(receipt)

    session["tower_ob_return_receipt"] = receipt

    return deepcopy(receipt)



def verify_return_receipt(
    value: Dict[str, Any] | None,
) -> bool:
    if not isinstance(value, dict):
        return False

    supplied = deepcopy(value)

    supplied_hash = str(
        supplied.pop("receipt_hash", "")
        or ""
    )

    if not supplied_hash:
        return False

    return supplied_hash == receipt_hash(
        supplied
    )


def owner_session_summary(
    *,
    step_up_active: bool,
) -> Dict[str, Any]:
    return {
        "authenticated": (
            session.get("tower_authenticated") is True
        ),
        "role": session.get("tower_role"),
        "owner_id_present": bool(session.get("owner_id")),
        "username": session.get("tower_username"),
        "step_up_active": bool(step_up_active),
        "launch_receipt_present": bool(
            session.get("tower_ob_launch_receipt")
        ),
        "return_receipt_present": bool(
            session.get("tower_ob_return_receipt")
        ),
        "default_deny": True,
    }


def ui_v2_contract() -> Dict[str, Any]:
    return {
        "contract": "tower_access_home_ui_v2",
        "theme": deepcopy(TOWER_UI_V2_THEME),
        "clean_access_home": True,
        "app_launch_cards": True,
        "owner_session_status": True,
        "clear_tower_to_ob_launch": True,
        "clear_tower_to_teller_launch": True,
        "clear_ob_to_tower_return": True,
        "return_receipt_status_panel": True,
        "owner_actions_panel": False,
        "quick_launch_panel": True,
        "hidden_evidence_drawers": False,
        "proof_page_main_experience": False,
        "list_heavy_main_surface": False,
        "credentials_committed": False,
        "broker_submission": False,
        "capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "direct_vault_write": False,
    }


def render_access_home_v2(
    *,
    step_up_active: bool,
    username: str,
) -> str:

    summary = owner_session_summary(
        step_up_active=step_up_active
    )

    return_receipt = active_return_receipt()
    return_verified = verify_return_receipt(
        return_receipt
    )

    auth_status = (
        "Authenticated"
        if summary["authenticated"]
        else "Not authenticated"
    )

    role_status = str(
        summary["role"]
        or "UNAVAILABLE"
    )

    step_status = (
        "Protected doors ready"
        if summary["step_up_active"]
        else "Protected doors need verification"
    )

    step_chip = (
        "STEP-UP ACTIVE"
        if summary["step_up_active"]
        else "STEP-UP REQUIRED"
    )

    return_status = (
        "Verified return receipt"
        if return_verified
        else "No verified return receipt"
    )

    business_cards = [
        card for card in APP_CARDS
        if card.get("category") == "business"
    ]

    consumer_cards = [
        card for card in APP_CARDS
        if card.get("category") == "apps"
    ]

    live_count = sum(
        1 for card in APP_CARDS
        if card.get("href")
    )

    building_count = (
        len(APP_CARDS)
        - live_count
    )

    business_html = "\n".join(
        _render_app_card(card)
        for card in business_cards
    )

    consumer_html = "\n".join(
        _render_app_card(card)
        for card in consumer_cards
    )

    soulaana_line = (
        "Your protected doors are ready. Pick where you want to go."
        if summary["step_up_active"]
        else
        "Your world is here. OB and Teller are live; protected entry will ask for verification when needed."
    )

    owner_style = """
    <style>
    :root {
        --tower-ink: #050708;
        --tower-glass: rgba(13,18,18,.82);
        --tower-glass-2: rgba(18,31,29,.74);
        --tower-line: rgba(196,226,216,.12);
        --tower-text: #edf3f0;
        --tower-muted: #91a39d;
        --tower-soft: #c5ddd5;
        --tower-sage: #94b9aa;
        --tower-gold: #d8c99a;
        --tower-live: #a8dbc8;
        --tower-building: #a99bb8;
    }

    body {
        background:
            radial-gradient(circle at 14% 8%, rgba(91,142,124,.13), transparent 27%),
            radial-gradient(circle at 88% 4%, rgba(213,190,132,.08), transparent 24%),
            linear-gradient(160deg, #030506, #09100e 58%, #050708);
        color: var(--tower-text);
    }

    .tower-shell {
        display: block;
        min-height: 100vh;
    }

    .tower-lobby {
        width: min(1500px, calc(100% - 48px));
        margin: 0 auto;
        padding: 24px 0 64px;
    }

    .tower-topbar {
        position: sticky;
        top: 14px;
        z-index: 20;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        min-height: 62px;
        padding: 10px 14px;
        border: 1px solid var(--tower-line);
        border-radius: 22px;
        background: rgba(5,8,8,.76);
        backdrop-filter: blur(24px);
        box-shadow: 0 18px 48px rgba(0,0,0,.20);
    }

    .tower-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .tower-brand-mark {
        width: 42px;
        aspect-ratio: 1;
        border-radius: 14px;
        display: grid;
        place-items: center;
        color: #16110b;
        font-weight: 950;
        background: linear-gradient(145deg, var(--tower-gold), #f3e9bf);
        box-shadow: 0 0 28px rgba(216,201,154,.14);
    }

    .tower-brand strong,
    .tower-brand span {
        display: block;
    }

    .tower-brand strong {
        font-size: .95rem;
    }

    .tower-brand span {
        margin-top: 2px;
        color: var(--tower-muted);
        font-size: .72rem;
    }

    .tower-top-actions {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: flex-end;
    }

    .tower-mini-chip,
    .tower-top-link {
        display: inline-flex;
        align-items: center;
        min-height: 34px;
        padding: 0 11px;
        border: 1px solid var(--tower-line);
        border-radius: 999px;
        background: rgba(255,255,255,.035);
        color: var(--tower-muted);
        font-size: .72rem;
        font-weight: 800;
        text-decoration: none;
    }

    .tower-mini-chip strong {
        color: var(--tower-soft);
        margin-left: 5px;
    }

    .tower-top-link:hover {
        color: var(--tower-text);
        border-color: rgba(216,201,154,.28);
    }

    .tower-lobby-hero {
        position: relative;
        overflow: hidden;
        display: grid;
        grid-template-columns: minmax(0,1.45fr) minmax(280px,.65fr);
        gap: 22px;
        align-items: end;
        min-height: 320px;
        margin-top: 18px;
        padding: 38px;
        border: 1px solid var(--tower-line);
        border-radius: 32px;
        background:
            radial-gradient(circle at 78% 18%, rgba(148,185,170,.12), transparent 27%),
            linear-gradient(145deg, rgba(17,30,28,.86), rgba(5,8,8,.90));
        box-shadow: 0 28px 90px rgba(0,0,0,.26);
    }

    .tower-lobby-hero:after {
        content: "";
        position: absolute;
        right: -70px;
        top: -100px;
        width: 330px;
        height: 330px;
        border-radius: 50%;
        border: 1px solid rgba(216,201,154,.09);
        box-shadow:
            0 0 0 38px rgba(148,185,170,.025),
            0 0 0 78px rgba(216,201,154,.018);
    }

    .tower-lobby-hero > * {
        position: relative;
        z-index: 2;
    }

    .tower-kicker {
        color: var(--tower-gold);
        font-size: .68rem;
        font-weight: 900;
        letter-spacing: .16em;
        text-transform: uppercase;
    }

    .tower-lobby-hero h1 {
        max-width: 850px;
        margin: 9px 0 12px;
        font-size: clamp(2.8rem, 6vw, 6.4rem);
        line-height: .92;
        letter-spacing: -.065em;
    }

    .tower-lobby-hero .tower-hero-sub {
        max-width: 680px;
        margin: 0;
        color: var(--tower-muted);
        font-size: 1rem;
        line-height: 1.55;
    }

    .tower-soulaana-brief {
        padding: 20px;
        border: 1px solid rgba(148,185,170,.16);
        border-radius: 22px;
        background: rgba(9,17,16,.62);
    }

    .tower-soulaana-brief strong {
        display: block;
        margin: 8px 0 7px;
        font-size: 1.15rem;
    }

    .tower-soulaana-brief p {
        margin: 0;
        color: var(--tower-muted);
        font-size: .84rem;
        line-height: 1.5;
    }

    .tower-world-pulse {
        display: grid;
        grid-template-columns: repeat(3,minmax(0,1fr));
        gap: 10px;
        margin-top: 14px;
    }

    .tower-world-pulse span {
        padding: 10px 12px;
        border: 1px solid var(--tower-line);
        border-radius: 13px;
        background: rgba(255,255,255,.025);
        color: var(--tower-muted);
        font-size: .72rem;
        line-height: 1.35;
    }

    .tower-world-pulse strong {
        display: block;
        margin-top: 3px;
        color: var(--tower-text);
        font-size: .92rem;
    }

    .tower-world-section {
        margin-top: 34px;
    }

    .tower-world-head {
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 14px;
    }

    .tower-world-head h2 {
        margin: 5px 0 0;
        font-size: clamp(1.55rem, 3vw, 2.25rem);
        letter-spacing: -.035em;
    }

    .tower-world-head p {
        max-width: 520px;
        margin: 0;
        color: var(--tower-muted);
        font-size: .78rem;
        line-height: 1.45;
        text-align: right;
    }

    .tower-square-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(205px, 1fr));
        gap: 14px;
    }

    .tower-square-tile {
        position: relative;
        min-width: 0;
        aspect-ratio: 1 / 1;
        padding: 17px;
        border: 1px solid var(--tower-line);
        border-radius: 24px;
        background:
            radial-gradient(circle at 86% 9%, rgba(148,185,170,.08), transparent 28%),
            linear-gradient(150deg, rgba(19,29,28,.78), rgba(7,10,10,.91));
        box-shadow: 0 18px 48px rgba(0,0,0,.18);
        color: var(--tower-text);
        text-decoration: none;
        display: flex;
        flex-direction: column;
        transition: transform .16s ease, border-color .16s ease, background .16s ease;
    }

    a.tower-square-tile:hover {
        transform: translateY(-3px);
        border-color: rgba(168,219,200,.30);
        background:
            radial-gradient(circle at 82% 10%, rgba(168,219,200,.13), transparent 30%),
            linear-gradient(150deg, rgba(22,36,33,.86), rgba(7,10,10,.92));
    }

    .tower-square-tile.building {
        opacity: .82;
    }

    .tower-tile-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 10px;
    }

    .tower-tile-mark {
        width: 46px;
        aspect-ratio: 1;
        border-radius: 15px;
        display: grid;
        place-items: center;
        border: 1px solid rgba(216,201,154,.14);
        background: rgba(216,201,154,.075);
        color: var(--tower-gold);
        font-size: .76rem;
        font-weight: 950;
        letter-spacing: .04em;
    }

    .tower-tile-state {
        display: inline-flex;
        align-items: center;
        min-height: 25px;
        padding: 0 8px;
        border: 1px solid var(--tower-line);
        border-radius: 999px;
        color: var(--tower-muted);
        font-size: .62rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .tower-square-tile.live .tower-tile-state {
        color: var(--tower-live);
        border-color: rgba(168,219,200,.20);
        background: rgba(168,219,200,.06);
    }

    .tower-tile-copy {
        margin-top: auto;
        padding-top: 18px;
    }

    .tower-tile-copy h3 {
        margin: 0;
        font-size: clamp(1.2rem, 2vw, 1.55rem);
        line-height: 1.02;
        letter-spacing: -.03em;
    }

    .tower-tile-copy .tower-tile-subtitle {
        margin: 6px 0 0;
        color: var(--tower-gold);
        font-size: .75rem;
        font-weight: 800;
    }

    .tower-tile-copy p {
        margin: 10px 0 0;
        color: var(--tower-muted);
        font-size: .73rem;
        line-height: 1.42;
    }

    .tower-tile-action {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        margin-top: 15px;
        padding-top: 12px;
        border-top: 1px solid var(--tower-line);
        color: var(--tower-soft);
        font-size: .72rem;
        font-weight: 900;
    }

    .tower-tile-action span:last-child {
        color: var(--tower-muted);
        font-weight: 700;
    }

    .tower-infra-grid {
        display: grid;
        grid-template-columns: repeat(4,minmax(0,1fr));
        gap: 14px;
    }

    .tower-infra-tile {
        min-height: 150px;
        padding: 18px;
        border: 1px solid var(--tower-line);
        border-radius: 20px;
        background: rgba(255,255,255,.025);
        color: var(--tower-text);
        text-decoration: none;
    }

    .tower-infra-tile strong {
        display: block;
        margin: 8px 0 6px;
        font-size: 1.05rem;
    }

    .tower-infra-tile p {
        margin: 0;
        color: var(--tower-muted);
        font-size: .74rem;
        line-height: 1.45;
    }

    .tower-infra-tile small {
        display: block;
        margin-top: 13px;
        color: var(--tower-gold);
        font-size: .68rem;
        font-weight: 800;
    }

    .tower-return-card {
        border-color: rgba(216,201,154,.16);
    }

    .tower-evidence-mini {
        margin-top: 14px;
        border: 1px solid var(--tower-line);
        border-radius: 18px;
        background: rgba(255,255,255,.02);
        overflow: hidden;
    }

    .tower-evidence-mini summary {
        cursor: pointer;
        padding: 14px 16px;
        color: var(--tower-muted);
        font-size: .75rem;
        font-weight: 800;
    }

    .tower-evidence-mini div {
        padding: 0 16px 16px;
    }

    .tower-evidence-mini a {
        color: var(--tower-gold);
        font-size: .76rem;
        font-weight: 800;
    }

    .tower-access-footer {
        display: flex;
        justify-content: space-between;
        gap: 14px;
        flex-wrap: wrap;
        margin-top: 32px;
        padding: 16px 2px 0;
        color: var(--tower-muted);
        font-size: .72rem;
    }

    @media (max-width: 1050px) {
        .tower-lobby-hero {
            grid-template-columns: 1fr;
        }

        .tower-infra-grid {
            grid-template-columns: repeat(2,minmax(0,1fr));
        }
    }

    @media (max-width: 720px) {
        .tower-lobby {
            width: min(100% - 24px, 1500px);
            padding-top: 12px;
        }

        .tower-topbar {
            top: 8px;
        }

        .tower-top-actions .tower-mini-chip {
            display: none;
        }

        .tower-lobby-hero {
            min-height: 0;
            padding: 24px 20px;
            border-radius: 24px;
        }

        .tower-world-pulse {
            grid-template-columns: 1fr;
        }

        .tower-world-head {
            align-items: flex-start;
            flex-direction: column;
        }

        .tower-world-head p {
            text-align: left;
        }

        .tower-square-grid {
            grid-template-columns: repeat(2,minmax(0,1fr));
            gap: 10px;
        }

        .tower-square-tile {
            padding: 13px;
            border-radius: 19px;
        }

        .tower-tile-copy p {
            display: none;
        }

        .tower-infra-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 430px) {
        .tower-square-grid {
            grid-template-columns: 1fr 1fr;
        }

        .tower-square-tile {
            aspect-ratio: .92 / 1;
        }

        .tower-tile-mark {
            width: 38px;
            border-radius: 12px;
        }

        .tower-tile-copy h3 {
            font-size: 1.04rem;
        }
    }
    </style>
    """

    page = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Simplee Tower · Access Home</title>
        {_tower_css()}
        {owner_style}
    </head>

    <body>
        <main
            class="tower-shell"
            data-tower-owner-access-home="twr156-160"
        >
            <div class="tower-lobby">

                <header class="tower-topbar">
                    <div class="tower-brand">
                        <div class="tower-brand-mark">T</div>
                        <div>
                            <strong>Simplee Tower</strong>
                            <span>Simplee World · private access</span>
                        </div>
                    </div>

                    <div class="tower-top-actions">
                        <span class="tower-mini-chip">
                            {escape(auth_status)}
                            <strong>{escape(role_status)}</strong>
                        </span>
                        <span class="tower-mini-chip">
                            {escape(step_chip)}
                        </span>
                        <a class="tower-top-link" href="/tower/owner-dashboard">
                            Owner
                        </a>
                        <a class="tower-top-link" href="/tower/logout">
                            Logout
                        </a>
                    </div>
                </header>

                <section
                    class="tower-lobby-hero"
                    data-tower-owner-front-door="true"
                >
                    <div>
                        <div class="tower-kicker">
                            SIMPLEE WORLD · YOUR FRONT DOOR
                        </div>

                        <h1>
                            Welcome home, {escape(username)}.
                        </h1>

                        <p class="tower-hero-sub">
                            Everything you built, one place.
                            Pick a door and go.
                        </p>

                        <div class="tower-world-pulse">
                            <span>
                                LIVE DOORS
                                <strong>{live_count}</strong>
                            </span>
                            <span>
                                BUILDING
                                <strong>{building_count}</strong>
                            </span>
                            <span>
                                ACCESS
                                <strong>{escape(step_status)}</strong>
                            </span>
                        </div>
                    </div>

                    <aside class="tower-soulaana-brief">
                        <div class="tower-kicker">
                            SOULAANA
                        </div>
                        <strong>
                            Everything is where it belongs.
                        </strong>
                        <p>
                            {escape(soulaana_line)}
                        </p>
                    </aside>
                </section>

                <section
                    class="tower-world-section"
                    data-tower-primary-owner-action="protected-products"
                >
                    <div class="tower-world-head">
                        <div>
                            <div class="tower-kicker">BUSINESS SYSTEMS</div>
                            <h2>Run the world.</h2>
                        </div>
                        <p>
                            Live doors open through Tower.
                            Building tiles stay visible without pretending
                            their runtimes are published.
                        </p>
                    </div>

                    <div class="tower-square-grid">
                        {business_html}
                    </div>
                </section>

                <section class="tower-world-section">
                    <div class="tower-world-head">
                        <div>
                            <div class="tower-kicker">SIMPLEE APPS</div>
                            <h2>Your app shelf.</h2>
                        </div>
                        <p>
                            The full consumer portfolio lives here now.
                            Each tile becomes a real door when that app is hosted.
                        </p>
                    </div>

                    <div class="tower-square-grid">
                        {consumer_html}
                    </div>
                </section>

                <section class="tower-world-section">
                    <div class="tower-world-head">
                        <div>
                            <div class="tower-kicker">INFRASTRUCTURE & RECORDS</div>
                            <h2>Behind the walls.</h2>
                        </div>
                        <p>
                            Owner control and technical proof stay available
                            without taking over the front door.
                        </p>
                    </div>

                    <div class="tower-infra-grid">
                        <a
                            id="tower-owner-launch-dock"
                            class="tower-infra-tile"
                            data-tower-owner-control="integrated"
                            href="/tower/owner-dashboard"
                        >
                            <div class="tower-kicker">OWNER</div>
                            <strong>Owner Headquarters</strong>
                            <p>People, access, owner state, and control surfaces.</p>
                            <small>Open →</small>
                        </a>

                        <a
                            class="tower-infra-tile"
                            data-tower-control="integrations"
                            href="/tower/integrations"
                        >
                            <div class="tower-kicker">CONNECTIONS</div>
                            <strong>Integration Desk</strong>
                            <p>See which Simplee systems are connected and what is still waiting.</p>
                            <small>Open →</small>
                        </a>

                        <article
                            class="tower-infra-tile tower-return-card"
                            data-tower-return-status="compact"
                        >
                            <div class="tower-kicker">RECENT HANDOFF</div>
                            <strong>{escape(return_status)}</strong>
                            <p>Return state stays compact unless you ask for the receipt.</p>
                            <small>OB → Tower</small>
                        </article>

                        <article class="tower-infra-tile">
                            <div class="tower-kicker">SESSION</div>
                            <strong>{escape(step_status)}</strong>
                            <p>Default-deny remains underneath every protected doorway.</p>
                            <small>{escape(step_chip)}</small>
                        </article>
                    </div>

                    <details
                        class="tower-evidence-mini"
                        data-tower-backstage-evidence="true"
                    >
                        <summary>Evidence & audit</summary>
                        <div>
                            <a href="/tower/owner/evidence">
                                Open Evidence Basement →
                            </a>
                        </div>
                    </details>
                </section>

                <footer class="tower-access-footer">
                    <span>Simplee Tower · Simplee World</span>
                    <span>
                        DEFAULT DENY · No release execution ·
                        no broker submission · no capital movement
                    </span>
                </footer>

            </div>
        </main>
    </body>
    </html>
    """

    return render_template_string(
        page
    )


def _render_app_card(
    card: Dict[str, Any],
) -> str:

    live = bool(
        card.get("href")
    )

    state_class = (
        "live"
        if live
        else "building"
    )

    step_note = (
        "Protected"
        if card.get("requires_step_up")
        else "App"
    )

    content = f"""
        <div class="tower-tile-top">
            <span class="tower-tile-mark">
                {escape(card.get("mark") or "SW")}
            </span>
            <span class="tower-tile-state">
                {escape(card["status"])}
            </span>
        </div>

        <div class="tower-tile-copy">
            <h3>{escape(card["name"])}</h3>
            <p class="tower-tile-subtitle">
                {escape(card["subtitle"])}
            </p>
            <p>
                {escape(card["description"])}
            </p>
        </div>

        <div class="tower-tile-action">
            <span>{escape(card["primary_action"])}</span>
            <span>{escape(step_note)}</span>
        </div>
    """

    if live:
        return f"""
        <a
            id="{escape(card["id"])}-entry"
            class="tower-square-tile {state_class}"
            href="{escape(card["href"])}"
            aria-label="{escape(card["primary_action"])} {escape(card["name"])}"
        >
            {content}
        </a>
        """

    return f"""
    <article
        id="{escape(card["id"])}-entry"
        class="tower-square-tile {state_class}"
        aria-label="{escape(card["name"])} · building"
    >
        {content}
    </article>
    """

def _tower_css() -> str:
    return """
    <style>
    :root {
        color-scheme: dark;
        --bg: #05040a;
        --panel: rgba(20, 17, 31, .84);
        --panel-2: rgba(37, 26, 58, .74);
        --glass: rgba(255,255,255,.07);
        --line: rgba(255,255,255,.13);
        --text: #fbf7ff;
        --muted: #bdb3cf;
        --dim: #867a99;
        --violet: #7d4fd6;
        --violet-2: #24153f;
        --gold: #f4d27b;
        --gold-2: #a67c2b;
        --danger: #ff9fb0;
        --good: #bdf7da;
    }

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        min-height: 100vh;
        background:
            radial-gradient(
                circle at 18% 12%,
                rgba(125, 79, 214, .22),
                transparent 34%
            ),
            radial-gradient(
                circle at 80% 16%,
                rgba(244, 210, 123, .12),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #030208,
                #090617 46%,
                #05040a
            );
        color: var(--text);
        font-family:
            Inter, ui-sans-serif, system-ui,
            -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif;
    }

    a {
        color: inherit;
    }

    .tower-shell {
        display: grid;
        grid-template-columns: 260px minmax(0, 1fr);
        min-height: 100vh;
    }

    .tower-rail {
        position: sticky;
        top: 0;
        height: 100vh;
        padding: 30px 22px;
        border-right: 1px solid var(--line);
        background:
            linear-gradient(
                180deg,
                rgba(18, 14, 29, .92),
                rgba(7, 6, 13, .84)
            );
        backdrop-filter: blur(22px);
    }

    .tower-mark {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        display: grid;
        place-items: center;
        margin-bottom: 18px;
        color: #201307;
        font-size: 1.55rem;
        font-weight: 950;
        background:
            linear-gradient(
                135deg,
                var(--gold),
                #fff1b7
            );
        box-shadow:
            0 0 24px rgba(244, 210, 123, .24),
            inset 0 0 12px rgba(255,255,255,.5);
    }

    .tower-overline {
        color: var(--gold);
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .74rem;
        font-weight: 800;
    }

    .tower-rail h2 {
        margin: 8px 0 24px;
    }

    .tower-nav {
        display: grid;
        gap: 10px;
        margin: 24px 0;
    }

    .tower-nav a,
    .tower-rail-card {
        padding: 13px 14px;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(255,255,255,.045);
        text-decoration: none;
        color: var(--muted);
    }

    .tower-nav a:hover {
        color: var(--text);
        border-color: rgba(244, 210, 123, .45);
        background: rgba(244, 210, 123, .08);
    }

    .tower-rail-card {
        margin-top: 28px;
        display: grid;
        gap: 6px;
    }

    .tower-rail-card span,
    .tower-status-tile span,
    .tower-panel-head span,
    .tower-card-top span {
        color: var(--dim);
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .11em;
        font-weight: 800;
    }

    .tower-main {
        padding: 34px;
    }

    .tower-hero {
        min-height: 260px;
        display: grid;
        grid-template-columns: minmax(0, 1fr) 260px;
        gap: 22px;
        align-items: end;
        padding: 34px;
        border: 1px solid var(--line);
        border-radius: 30px;
        background:
            linear-gradient(
                135deg,
                rgba(31, 23, 49, .88),
                rgba(9, 7, 16, .82)
            );
        box-shadow: 0 34px 120px rgba(0,0,0,.34);
        overflow: hidden;
        position: relative;
    }

    .tower-hero:before {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        right: -110px;
        top: -120px;
        border-radius: 999px;
        background:
            radial-gradient(
                circle,
                rgba(244, 210, 123, .18),
                rgba(125, 79, 214, .15) 42%,
                transparent 68%
            );
        filter: blur(4px);
    }

    .tower-hero > * {
        position: relative;
        z-index: 2;
    }

    .tower-hero h1 {
        margin: 10px 0 12px;
        font-size: clamp(2.4rem, 5vw, 5.7rem);
        line-height: .94;
        letter-spacing: -.06em;
    }

    .tower-hero p,
    .tower-section p,
    .tower-panel p,
    .tower-app-card p {
        color: var(--muted);
        line-height: 1.58;
    }

    .tower-session-card,
    .tower-status-tile,
    .tower-panel,
    .tower-app-card,
    .tower-detail {
        border: 1px solid var(--line);
        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,.075),
                rgba(255,255,255,.035)
            );
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 70px rgba(0,0,0,.22);
    }

    .tower-session-card {
        border-radius: 24px;
        padding: 22px;
        display: grid;
        gap: 8px;
    }

    .tower-session-card strong {
        font-size: 1.6rem;
    }

    .tower-session-card small {
        color: var(--muted);
    }

    .tower-status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 18px 0 28px;
    }

    .tower-status-tile {
        padding: 20px;
        border-radius: 20px;
    }

    .tower-status-tile strong {
        display: block;
        margin-top: 8px;
        font-size: 1.1rem;
    }

    .tower-section {
        margin-top: 28px;
    }

    .tower-section-head {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 16px;
    }

    .tower-section h2 {
        margin: 0 0 6px;
        font-size: 1.7rem;
    }

    .tower-app-grid {
        display: grid;
        grid-template-columns:
            repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
    }

    .tower-app-card {
        border-radius: 24px;
        padding: 22px;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .tower-app-card-active {
        border-color: rgba(244, 210, 123, .5);
        background:
            radial-gradient(
                circle at 80% 8%,
                rgba(244, 210, 123, .14),
                transparent 32%
            ),
            linear-gradient(
                180deg,
                rgba(125, 79, 214, .2),
                rgba(255,255,255,.035)
            );
    }

    .tower-card-top,
    .tower-panel-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
        margin-bottom: 12px;
    }

    .tower-app-card h3 {
        margin: 8px 0 8px;
        font-size: 1.45rem;
    }

    .tower-card-subtitle {
        color: var(--gold) !important;
        margin-top: 0;
    }

    .tower-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        width: fit-content;
        padding: 0 18px;
        border-radius: 999px;
        background:
            linear-gradient(
                135deg,
                var(--gold),
                #fff2bd
            );
        color: #1a1109;
        text-decoration: none;
        font-weight: 900;
        border: 0;
    }

    .tower-button.secondary {
        background: rgba(255,255,255,.08);
        color: var(--text);
        border: 1px solid var(--line);
    }

    .tower-lower-grid {
        display: grid;
        grid-template-columns:
            minmax(0, 1.05fr)
            minmax(0, 1fr)
            minmax(0, .85fr);
        gap: 16px;
        margin-top: 28px;
    }

    .tower-panel {
        border-radius: 24px;
        padding: 22px;
    }

    .tower-panel h3 {
        margin: 4px 0 12px;
        font-size: 1.25rem;
    }

    .tower-return-panel {
        border-color: rgba(244, 210, 123, .35);
    }

    .tower-action-row {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        padding: 13px 0;
        border-top: 1px solid var(--line);
    }

    .tower-action-row:first-of-type {
        border-top: 0;
    }

    .tower-action-row p {
        margin: 4px 0 0;
    }

    .tower-action-row span {
        color: var(--gold);
        white-space: nowrap;
        font-weight: 800;
    }

    .tower-quick-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .tower-evidence {
        padding: 22px;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: rgba(255,255,255,.035);
    }

    .tower-detail {
        border-radius: 16px;
        padding: 15px 16px;
        margin-top: 10px;
    }

    .tower-detail summary {
        cursor: pointer;
        color: var(--gold);
        font-weight: 850;
    }

    .tower-footer {
        color: var(--dim);
        margin: 30px 0 4px;
        font-size: .9rem;
    }

    .tower-sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    .tower-ob-return-chip {
        position: fixed;
        left: 18px;
        bottom: 18px;
        z-index: 99999;
        display: inline-flex;
        align-items: center;
        min-height: 42px;
        padding: 0 16px;
        border-radius: 999px;
        color: #1a1109;
        background:
            linear-gradient(
                135deg,
                #f4d27b,
                #fff2bd
            );
        text-decoration: none;
        font-weight: 900;
        box-shadow: 0 14px 44px rgba(0,0,0,.34);
    }

    @media (max-width: 980px) {
        .tower-shell {
            grid-template-columns: 1fr;
        }

        .tower-rail {
            position: relative;
            height: auto;
        }

        .tower-hero,
        .tower-lower-grid,
        .tower-status-grid {
            grid-template-columns: 1fr;
        }

        .tower-main {
            padding: 20px;
        }
    }
    </style>
    """

def inject_ob_return_button(
    response,
    *,
    owner_session_active: bool,
):
    # Compatibility symbol only.
    # Historical UI injection behavior is retired.
    return response


from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower."):
        sys.modules.pop(name, None)

from tower.ob_object_guard import build_locked_ob_object_response
from tower.ob_object_guard import evaluate_ob_object_guard
from tower.ob_object_guard import get_ob_object_guard_report
from tower.ob_object_guard import match_ob_object_guard_policy
from tower.ob_object_guard import should_block_ob_object


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    report = get_ob_object_guard_report()
    _print("OBJECT GUARD REPORT", {
        "ok": report.get("ok"),
        "object_guard_count": report.get("object_guard_count"),
        "default_object_policy": report.get("default_object_policy"),
    })
    assert report.get("ok") is True
    assert report.get("object_guard_count", 0) >= 7
    assert "Soulaana:" in report.get("soulaana_translation", "")

    symbol_match = match_ob_object_guard_policy(
        object_kind="symbol",
        object_id="AAPL",
    )
    _print("SYMBOL MATCH", symbol_match)
    assert symbol_match.get("matched") is True
    assert symbol_match.get("policy", {}).get("object_type") == "symbol"

    unknown_match = match_ob_object_guard_policy(
        object_kind="mystery_drawer",
        object_id="secret_001",
    )
    _print("UNKNOWN MATCH", unknown_match)
    assert unknown_match.get("match_type") == "unmapped_object_default_deny"

    owner_symbol = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="symbol",
        object_id="AAPL",
        action="view",
        current_risk_score=10,
    )
    _print("OWNER SYMBOL ALLOWED", owner_symbol)
    assert owner_symbol.get("allowed") is True

    beta_symbol = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="symbol",
        object_id="AAPL",
        action="view",
        current_risk_score=10,
    )
    _print("BETA SYMBOL DENIED", beta_symbol)
    assert beta_symbol.get("allowed") is False

    owner_export = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="export",
        object_id="export_pack_049",
        action="download",
        current_risk_score=5,
    )
    _print("OWNER EXPORT ALLOWED", owner_export)
    assert owner_export.get("allowed") is True

    beta_export = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_pack_049",
        action="download",
        current_risk_score=5,
    )
    _print("BETA EXPORT DENIED", beta_export)
    assert beta_export.get("allowed") is False

    owner_trade = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="trade",
        object_id="trade_049_owner",
        owner_user_id="owner_solice",
        action="view",
        current_risk_score=5,
    )
    _print("OWNER TRADE ALLOWED", owner_trade)
    assert owner_trade.get("allowed") is True

    other_user_trade = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="trade",
        object_id="trade_049_owner",
        owner_user_id="owner_solice",
        action="view",
        current_risk_score=5,
    )
    _print("OTHER USER TRADE DENIED", other_user_trade)
    assert other_user_trade.get("allowed") is False

    high_risk_account = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="account",
        object_id="acct_049",
        action="view",
        current_risk_score=95,
    )
    _print("HIGH RISK ACCOUNT STEP UP", high_risk_account)
    assert high_risk_account.get("allowed") is False
    assert high_risk_account.get("decision") == "step_up"

    unmapped = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="mystery_drawer",
        object_id="secret_001",
        action="view",
    )
    _print("UNMAPPED OBJECT DENIED", unmapped)
    assert unmapped.get("allowed") is False
    assert unmapped.get("reason_code") == "ob_object_unmapped_default_deny"

    block = should_block_ob_object(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_pack_049",
        action="download",
    )
    _print("BLOCK OBJECT", block)
    assert block.get("block") is True

    html, status = build_locked_ob_object_response(
        reason_code="test_object_locked",
        human_reason="Testing object lock.",
        object_kind="export",
        object_id="export_pack_049",
        decision=block,
    )
    _print("LOCKED OBJECT RESPONSE", {
        "status": status,
        "has_drawer": "Private drawer locked" in html,
        "has_soulaana": "Soulaana:" in html,
    })
    assert status == 403
    assert "Private drawer locked" in html
    assert "Soulaana:" in html

    serialized = json.dumps(
        [
            report,
            owner_symbol,
            beta_symbol,
            owner_export,
            beta_export,
            owner_trade,
            other_user_trade,
            high_risk_account,
            unmapped,
            block,
        ],
        sort_keys=True,
        default=str,
    )
    assert "tower_keycard=" not in serialized
    assert "raw_token" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "049",
        "status": "passed",
        "human_reason": "OB object guard foundation protects specific symbols, trades, accounts, exports, analysis records, modes, and unmapped object kinds.",
    }
    _print("PACK 049 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()

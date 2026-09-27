"""TWR212–216: BuyBox-proposed Teller question is never money readiness."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tower.buybox_teller_proposal_review import (
    BuyBoxTellerProposalError,
    review_untrusted_teller_readiness_proposal,
    validate_untrusted_teller_readiness_proposal,
    SCHEMA_VERSION,
)

NOW = datetime(2026, 9, 27, 19, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[1]
PINNED_BUYBOX = ROOT / "source-buybox-pinned"


def packet(vertical="atm", lane="ATM_SET_1_ACQUISITION"):
    terms = {
        "proposed_purchase_price": "95000.00",
        "proposed_debt_amount": "75000.00",
        "proposed_equity_amount": "20000.00",
        "estimated_closing_costs": "5000.00",
        "proposed_reserve": "12000.00",
        "funding_lane": lane,
        "terms_reference": "synthetic-proposal-1",
    }
    core = {
        "opportunity_id": "synthetic-opportunity-1",
        "opportunity_revision": 1,
        "input_snapshot_digest": "a" * 64,
        "vertical_id": vertical,
        "stored_asking_price": "95000.00",
        "terms": terms,
    }
    fingerprint = hashlib.sha256(json.dumps(
        core, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "source_app": "buybox",
        "route_via": "tower",
        "destination": "teller",
        "requested_action": "REQUEST_TELLER_READINESS",
        "purpose": "acquisition_financing",
        **core,
        "terms_fingerprint": fingerprint,
        "issued_at": NOW.isoformat(),
        "valid_until": (NOW + timedelta(seconds=120)).isoformat(),
    }


def assert_blocked(result):
    assert result["state"] == "SOURCE_ONLY_NOT_SUBMITTED"
    for key in (
        "source_authenticity_verified", "tower_action_authorized",
        "teller_request_sent", "teller_issuer_verified",
        "teller_receipt_present", "acquisition_ready",
        "capital_deployment_authorized", "external_call_made",
    ):
        assert result[key] is False
    assert result["buyer_money_ready"] == "UNKNOWN"
    assert result["management_capacity_ready"] == "UNKNOWN"


def test_valid_synthetic_request_is_only_unsubmitted_source_shape():
    result = review_untrusted_teller_readiness_proposal(packet(), now_utc=NOW)
    assert_blocked(result)
    assert result["proposed_funding_lane"] == "ATM_SET_1_ACQUISITION"
    assert result["terms_fingerprint"] == packet()["terms_fingerprint"]
    assert "TELLER_CURRENT_MONEY_AND_MANAGEMENT_READINESS_NOT_RECEIVED" in result["reason_codes"]
    assert "proposed_purchase_price" not in result
    assert "broker_balance" not in json.dumps(result)


@pytest.mark.parametrize("vertical,lane", [
    ("atm", "ATM_SET_1_ACQUISITION"),
    ("atm", "ATM_SET_2_ACQUISITION"),
    ("multifamily", "GROUNDS_ACQUISITION_UNVERIFIED"),
    ("commercial", "MISSION_ACCOUNT_UNASSIGNED"),
    ("laundromat", "MISSION_ACCOUNT_UNASSIGNED"),
    ("land_farm", "MISSION_ACCOUNT_UNASSIGNED"),
    ("business", "MISSION_ACCOUNT_UNASSIGNED"),
    ("equipment", "MISSION_ACCOUNT_UNASSIGNED"),
])
def test_all_source_verticals_keep_unverified_lane_isolation(vertical, lane):
    assert_blocked(review_untrusted_teller_readiness_proposal(
        packet(vertical, lane), now_utc=NOW,
    ))


@pytest.mark.parametrize("bad", [
    {"source_app": "observatory"}, {"route_via": "ob"},
    {"destination": "broker"}, {"requested_action": "MOVE_CAPITAL"},
    {"purpose": "payroll"}, {"schema_version": "v2"},
    {"opportunity_revision": True}, {"opportunity_revision": 0},
    {"input_snapshot_digest": "not-a-digest"}, {"vertical_id": "unregistered"},
    {"opportunity_id": "../unsafe"},
    {"approved": True}, {"teller_receipt": "fake"}, {"buyer_money_ready": "READY"},
    {"broker_balance": "95000.00"}, {"actor_verified": True},
])
def test_bad_claims_and_smuggled_authority_fail_closed(bad):
    with pytest.raises(BuyBoxTellerProposalError):
        validate_untrusted_teller_readiness_proposal(
            {**packet(), **bad}, now_utc=NOW,
        )


@pytest.mark.parametrize("key,value", [
    ("proposed_purchase_price", 95000.0),
    ("proposed_purchase_price", "0.00"),
    ("proposed_debt_amount", "-5.00"),
    ("proposed_reserve", "NaN"),
    ("proposed_equity_amount", "250.001"),
    ("estimated_closing_costs", "1e10"),
    ("funding_lane", "ATM_SET_1_PLUS_SET_2"),
    ("terms_reference", "../unsafe"),
    ("other_funds", "1000000.00"),
])
def test_invalid_proposed_terms_fail_closed(key, value):
    item = packet()
    item["terms"] = {**item["terms"], key: value}
    with pytest.raises(BuyBoxTellerProposalError):
        validate_untrusted_teller_readiness_proposal(item, now_utc=NOW)


@pytest.mark.parametrize("change", [
    ("input_snapshot_digest", "b" * 64),
    ("opportunity_revision", 2),
    ("stored_asking_price", "89000.00"),
    ("terms_fingerprint", "0" * 64),
])
def test_changed_source_or_terms_cannot_reuse_existing_fingerprint(change):
    key, value = change
    with pytest.raises(BuyBoxTellerProposalError, match="TERMS_FINGERPRINT_MISMATCH"):
        validate_untrusted_teller_readiness_proposal(
            {**packet(), key: value}, now_utc=NOW,
        )


def test_expired_or_naive_or_future_question_denied():
    with pytest.raises(BuyBoxTellerProposalError, match="REQUEST_EXPIRED"):
        validate_untrusted_teller_readiness_proposal(
            packet(), now_utc=NOW + timedelta(seconds=121),
        )
    item = packet()
    item["valid_until"] = (NOW + timedelta(seconds=301)).isoformat()
    with pytest.raises(BuyBoxTellerProposalError, match="REQUEST_TIME_INVALID"):
        validate_untrusted_teller_readiness_proposal(item, now_utc=NOW)
    item = packet()
    item["issued_at"] = NOW.replace(tzinfo=None).isoformat()
    with pytest.raises(BuyBoxTellerProposalError):
        validate_untrusted_teller_readiness_proposal(item, now_utc=NOW)
    with pytest.raises(BuyBoxTellerProposalError):
        validate_untrusted_teller_readiness_proposal(
            packet(), now_utc=NOW.replace(tzinfo=None),
        )


def test_input_mapping_never_mutated():
    original = packet()
    before = copy.deepcopy(original)
    validated = validate_untrusted_teller_readiness_proposal(original, now_utc=NOW)
    assert original == before
    validated["terms"]["proposed_reserve"] = "0.00"
    assert original == before


def test_pinned_independent_buybox_producer_packet_accepted_without_grant(tmp_path):
    """Execute real BBX source in its own checkout, not Tower's copied fixture."""
    assert (PINNED_BUYBOX / "buybox" / "teller_readiness_question.py").is_file()
    script = """
from buybox.core import new_opportunity
from buybox.store import connect, save
from buybox.teller_readiness_question import prepare_unsubmitted_teller_readiness_question
from datetime import datetime, timezone
import json, sys
db = connect(sys.argv[1])
op = save(db, new_opportunity("atm", "Fictional source-only opportunity", "95000"))
terms = {
"proposed_purchase_price":"95000.00","proposed_debt_amount":"75000.00",
"proposed_equity_amount":"20000.00","estimated_closing_costs":"5000.00",
"proposed_reserve":"12000.00","funding_lane":"ATM_SET_1_ACQUISITION",
"terms_reference":"synthetic-proposal-1"
}
out = prepare_unsubmitted_teller_readiness_question(
db, op["id"], proposed_terms=terms,
now_utc=datetime(2026,9,27,19,0,tzinfo=timezone.utc)
)
assert out["state"] == "LOCAL_TERMS_QUESTION_UNSUBMITTED"
assert out["teller_readiness"] == "UNKNOWN"
print(json.dumps(out["packet"], sort_keys=True))
db.close()
"""
    run = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path / "synthetic.sqlite3")],
        cwd=PINNED_BUYBOX, capture_output=True, text=True, check=True,
    )
    external_packet = json.loads(run.stdout)
    validated = validate_untrusted_teller_readiness_proposal(
        external_packet, now_utc=NOW,
    )
    assert validated == external_packet
    assert_blocked(review_untrusted_teller_readiness_proposal(
        external_packet, now_utc=NOW,
    ))


def test_review_has_no_external_side_effects_or_live_route():
    import tower.buybox_teller_proposal_review as source
    code = Path(source.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "@app.route(", "requests.post(", "from observatory.",
        "from buybox.", "from teller.", "broker.place_order(",
        "TELLER_TOWER_TOKEN_SECRET", "os.environ",
    ):
        assert forbidden not in code

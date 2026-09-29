"""Synthetic tests of the hosted one-shot source/interpretation proof schema."""
import json
from copy import deepcopy
import pytest

from deploy.hosted_tower.keyless_one_shot_source_probe import summarize_snapshot


def packet():
    return {
        "schema": "OB_KEYLESS_PUBLIC_CONTEXT_V1",
        "source_only": True, "context_only": True,
        "prices_attached": False, "options_chain_attached": False,
        "live_quote_verified": False, "candidate_admitted": False,
        "broker_execution_authorized": False, "ai_input_approved": False,
        "sources": [
            {"source": "sec", "state": "DELEGATED_ISSUER_RESEARCH", "value": None},
            {"source": "bls", "state": "SOURCE_BOUND", "value": "SENSITIVE_SAMPLE_CPI"},
            {"source": "treasury", "state": "SOURCE_BOUND", "value": "SENSITIVE_SAMPLE_DEBT"},
            {"source": "openfigi", "state": "SOURCE_BOUND", "value": "SENSITIVE_SAMPLE_FIGI"},
        ],
        "soulaana_evidence_brief": {
            "schema": "OB_SOULAANA_KEYLESS_EVIDENCE_V1",
            "channel": "SOULAANA_REVIEWED_PUBLIC_RESEARCH",
            "external_model_called": False, "live_quote_verified": False,
            "candidate_admitted": False, "broker_execution_authorized": False,
            "capital_authorized": False,
            "observations": [{"source": s} for s in ("bls", "treasury", "openfigi")],
            "comparisons": [{"source": s} for s in ("bls", "treasury")],
        },
    }


def test_one_shot_proof_requires_actual_bound_sources_and_reviewed_examination():
    report = summarize_snapshot(packet())
    assert report["all_verified"] is True
    assert report["source_read_verified"] is True
    assert report["soulaana_evidence_verified"] is True
    assert report["two_period_comparisons_verified"] is True
    assert report["owner_browser_session_verified"] is False
    assert report["sec_filing_fetched_by_probe"] is False
    assert "SENSITIVE_SAMPLE" not in json.dumps(report)
    assert '"value":' not in json.dumps(report)
    assert report["raw_values_logged"] is False


def test_source_hold_remains_visible_and_never_claims_proof():
    held = packet()
    held["sources"][1]["state"] = "SOURCE_HOLD"
    held["soulaana_evidence_brief"]["observations"] = [
        {"source": "treasury"}, {"source": "openfigi"}
    ]
    held["soulaana_evidence_brief"]["comparisons"] = [{"source": "treasury"}]
    report = summarize_snapshot(held)
    assert report["source_states"]["bls"] == "SOURCE_HOLD"
    assert report["all_verified"] is False
    assert report["soulaana_evidence_verified"] is False
    assert report["two_period_comparisons_verified"] is False


def test_no_comparison_does_not_pretend_soulaana_examination_is_complete():
    p = packet()
    p["soulaana_evidence_brief"]["comparisons"] = []
    report = summarize_snapshot(p)
    assert report["source_read_verified"] is True
    assert report["soulaana_evidence_verified"] is True
    assert report["two_period_comparisons_verified"] is False
    assert report["all_verified"] is False


@pytest.mark.parametrize("key,value", [
    ("prices_attached", True),
    ("live_quote_verified", True),
    ("candidate_admitted", True),
    ("broker_execution_authorized", True),
    ("ai_input_approved", True),
])
def test_proof_rejects_trading_authority_or_blanket_ai(key, value):
    p = packet()
    p[key] = value
    with pytest.raises(ValueError):
        summarize_snapshot(p)


def test_proof_rejects_fake_external_model_call_and_wrong_source_order():
    p = packet()
    p["soulaana_evidence_brief"]["external_model_called"] = True
    with pytest.raises(ValueError):
        summarize_snapshot(p)
    q = packet()
    q["sources"] = q["sources"][::-1]
    with pytest.raises(ValueError):
        summarize_snapshot(q)


def test_probe_is_explicitly_off_in_normal_startup():
    from pathlib import Path
    script = Path("deploy/hosted_tower/start.sh").read_text()
    assert '${OB_KEYLESS_ONE_SHOT_SOURCE_PROBE:-0}' in script
    assert 'keyless_one_shot_source_probe' in script
    assert script.index('keyless_one_shot_source_probe') < script.index('exec "${PYTHON_VALUE}" -m gunicorn')

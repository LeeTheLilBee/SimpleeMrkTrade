
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

AUDIT = json.loads(
    (
        ROOT
        / "evidence/market_truth/obdata001_authority_map.json"
    ).read_text(
        encoding="utf-8"
    )
)


def test_obdata001_recognizes_existing_canonical_engine():
    modules = AUDIT["module_authority"]

    assert modules["engine/canonical_candidate.py"]["class"] == "CANONICAL_PROCESSOR"
    assert modules["engine/canonical_decision_gate.py"]["class"] == "CANONICAL_PROCESSOR"
    assert modules["engine/canonical_decision_object.py"]["class"] == "CANONICAL_SCHEMA_PROCESSOR"
    assert modules["engine/canonical_execution_guard.py"]["class"] == "CANONICAL_GUARD_PROCESSOR"
    assert modules["engine/canonical_trade_state.py"]["class"] == "CANONICAL_STATE_PROCESSOR"


def test_obdata001_does_not_call_seed_bootstrap_live_truth():
    modules = AUDIT["module_authority"]

    assert (
        modules["engine/bootstrap_signal_universe.py"]["class"]
        ==
        "SEED_GENERATOR_NOT_LIVE_MARKET_AUTHORITY"
    )


def test_obdata001_market_universe_is_discovery_not_quote_truth():
    authority = AUDIT["artifact_authority"]

    assert (
        authority["market_universe.json"]
        ==
        "DISCOVERY_UNIVERSE_NOT_QUOTE_TRUTH"
    )


def test_obdata001_reporting_snapshot_keeps_provenance_requirement():
    authority = AUDIT["artifact_authority"]

    assert (
        authority["canonical_reporting_snapshot.json"]
        ==
        "DERIVED_REVIEW_HISTORY_PROVENANCE_REQUIRED"
    )


def test_obdata001_architecture_reuses_existing_engine():
    assert AUDIT["do_not_build_second_engine"] is True
    assert (
        AUDIT["authority_doctrine"]["canonical_does_not_mean_live"]
        is True
    )
    assert (
        AUDIT["authority_doctrine"]["derived_outputs_inherit_input_provenance"]
        is True
    )

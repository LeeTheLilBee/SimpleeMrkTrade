"""Opt-in ONE-SHOT server-side availability proof, no owner/browser authority.

Print only fixed source names/states, evidence count and guard booleans. Never
print raw data, publisher text, EIA key, HTTP body, request URL or exceptions.
No background recurrence; normal Tower route remains signed/step-up protected.
"""
import json


def sanitized_proof(packet):
    order = ("federal_register", "cftc", "eia", "world_bank", "nws", "sec_edgar")
    rows = packet.get("sources")
    brief = packet.get("soulaana")
    if (packet.get("schema") != "OB_OFFICIAL_CATALYST_RADAR_V1"
            or not isinstance(rows, list) or len(rows) != 6
            or [row.get("source") for row in rows] != list(order)
            or packet.get("source_only") is not True
            or packet.get("prices_attached") is not False
            or packet.get("broker_execution_authorized") is not False
            or not isinstance(brief, dict)
            or brief.get("schema") != "OB_SOULAANA_OFFICIAL_CATALYST_V1"
            or brief.get("external_model_called") is not False
            or brief.get("candidate_admitted") is not False
            or not isinstance(brief.get("observations"), list)):
        raise ValueError("RADAR_CONTRACT_HOLD")
    valid_states = frozenset({
        "SOURCE_BOUND", "REVIEW_HOLD", "KEY_REQUIRED",
        "SOURCE_HOLD", "NO_PUBLICATION", "EXISTING_PROTECTED_CORRIDOR",
    })
    if any(r.get("state") not in valid_states for r in rows):
        raise ValueError("RADAR_CONTRACT_HOLD")
    return {
        "schema": "OB_OFFICIAL_CATALYST_ONE_SHOT_V1",
        "source_states": {r["source"]: r["state"] for r in rows},
        "soulaana_reviewed_observation_count": len(brief["observations"]),
        "owner_browser_session_verified": False,
        "real_time_price_feed_verified": False,
        "raw_values_logged": False,
    }


def main():
    try:
        from engine.market_intake.official_catalyst_radar import from_environment
        proof = sanitized_proof(from_environment().snapshot())
    except Exception:
        proof = {
            "schema": "OB_OFFICIAL_CATALYST_ONE_SHOT_V1",
            "status": "SOURCE_OR_CONTRACT_HOLD",
            "owner_browser_session_verified": False,
            "raw_values_logged": False,
        }
    print("OB_CATALYST_ONE_SHOT " + json.dumps(proof, sort_keys=True), flush=True)
    return 0 if proof.get("soulaana_reviewed_observation_count", 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""
Pack 2545 — Tower to OB Launch Continuity Contract.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ob_six_room_acceptance_handoff import (
    build_handoff_cert,
)


PACK_ID = "2545"
ENDPOINT = "/tower/ir-cert-v2545.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_handoff_cert(2545)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2545_preview():
    return deepcopy(_build_cached())

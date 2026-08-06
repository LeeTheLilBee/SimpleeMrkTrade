"""
Pack 2530 — Owner Decision Evidence Drawers.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_owner_console_v1 import (
    build_owner_console_cert,
)


PACK_ID = "2530"
ENDPOINT = "/tower/ir-cert-v2530.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_owner_console_cert(2530)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2530_preview():
    return deepcopy(_build_cached())

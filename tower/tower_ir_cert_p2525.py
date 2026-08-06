"""
Pack 2525 — Dangerous Action Review Cards.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_owner_console_v1 import (
    build_owner_console_cert,
)


PACK_ID = "2525"
ENDPOINT = "/tower/ir-cert-v2525.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_owner_console_cert(2525)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2525_preview():
    return deepcopy(_build_cached())

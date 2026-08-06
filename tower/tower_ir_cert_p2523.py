"""
Pack 2523 — Owner Console Route Shell.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_owner_console_v1 import (
    build_owner_console_cert,
)


PACK_ID = "2523"
ENDPOINT = "/tower/ir-cert-v2523.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_owner_console_cert(2523)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2523_preview():
    return deepcopy(_build_cached())

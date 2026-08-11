"""
Tower IR Cert Pack 2568: Login redirect and 403-safe route behavior
"""

from __future__ import annotations

from tower.tower_owner_beta_route_gate import owner_beta_route_gate_cert


def tower_ir_cert_p2568():
    return owner_beta_route_gate_cert(2568)

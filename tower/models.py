# =============================================================================
# THE TOWER — BASIC DATA SHAPES
# FILE: tower/models.py
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class TowerUser:
    user_id: str
    email: str
    display_name: str
    role: str = "user"
    account_type: str = "beta_user"
    status: str = "active"
    app_access: Dict[str, str] = field(default_factory=dict)
    consents: Dict[str, bool] = field(default_factory=dict)
    can_export: bool = False
    trust_score: int = 75
    risk_state: str = "clear"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "display_name": self.display_name,
            "role": self.role,
            "account_type": self.account_type,
            "status": self.status,
            "app_access": self.app_access,
            "consents": self.consents,
            "can_export": self.can_export,
            "trust_score": self.trust_score,
            "risk_state": self.risk_state,
        }

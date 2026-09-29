"""Owner-beta navigation must target only the Tower-mapped Observatory rooms.

A nav typo must not be repaired by making an unknown route public-safe.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest

from tower.ob_route_guard import match_ob_guard_policy, OB_ROUTE_GUARD_MAP


ROOT = Path(__file__).resolve().parents[1]
NAV = ROOT / "web" / "static" / "ob" / "ob_nav_shell.js"

CANONICAL = {
    "Dashboard": "/ob/dashboard",
    "Market Map": "/ob/market-map",
    "Market Data Desk": "/ob/data-desk",
    "Trade Center": "/ob/trade-center",
    "Review Center": "/ob/review-center",
    "Owner Console": "/ob/owner-console",
}


class ObservatoryCanonicalNavigationTests(unittest.TestCase):
    def test_all_hover_nav_targets_are_canonical_and_tower_mapped(self):
        script = NAV.read_text(encoding="utf-8")
        targets = re.findall(
            r'navLink\(path,\s*"([^"]+)",\s*"([^"]+)"',
            script,
        )
        self.assertEqual(
            {label: path for path, label in targets},
            CANONICAL,
            "Hover menu must not bypass the canonical /ob/ corridor",
        )
        self.assertEqual(len(targets), len(CANONICAL))
        for label, path in CANONICAL.items():
            with self.subTest(room=label):
                matched = match_ob_guard_policy(path)
                self.assertEqual(matched["match_type"], "exact")
                self.assertFalse(matched["policy"].get("public_allowed", False))
                self.assertIn(path, OB_ROUTE_GUARD_MAP)

    def test_old_root_level_shortcuts_are_still_unmapped_and_denied(self):
        for path in ("/trade-center", "/review-center"):
            with self.subTest(path=path):
                self.assertEqual(
                    match_ob_guard_policy(path)["match_type"],
                    "unmapped_default_deny",
                )

    def test_unknown_corridors_are_not_made_public_by_navigation_fix(self):
        for path in (
            "/ob/trade-center/move-money",
            "/ob/review-center/release-capital",
            "/ob/not-a-room",
        ):
            with self.subTest(path=path):
                result = match_ob_guard_policy(path)
                self.assertEqual(result["match_type"], "unmapped_default_deny")
                self.assertFalse(result["policy"]["public_allowed"])


if __name__ == "__main__":
    unittest.main()

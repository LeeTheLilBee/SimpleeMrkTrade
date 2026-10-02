"""Dashboard Practice cards must use canonical Tower-protected OB corridors."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest

from tower.ob_route_guard import match_ob_guard_policy

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "web/templates/dashboard.html"


class _AnchorCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = {"attrs": dict(attrs), "text": ""}

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.anchors.append(self.current)
            self.current = None


class ObservatoryDashboardPracticeNavigationTests(unittest.TestCase):
    def test_both_dashboard_practice_entry_points_use_guarded_trade_room(self):
        parser = _AnchorCollector()
        parser.feed(DASHBOARD.read_text(encoding="utf-8"))
        practice = [
            a for a in parser.anchors
            if "Paper Practice" in a["text"]
            or ("Practice" in a["text"] and "Paper Trade Center" in a["text"])
        ]
        self.assertEqual(len(practice), 2)
        for anchor in practice:
            with self.subTest(text=anchor["text"].strip()):
                self.assertEqual(anchor["attrs"].get("href"), "/ob/trade-center")

    def test_dashboard_cannot_reintroduce_legacy_unmapped_links(self):
        parser = _AnchorCollector()
        parser.feed(DASHBOARD.read_text(encoding="utf-8"))
        for anchor in parser.anchors:
            with self.subTest(text=anchor["text"].strip()):
                self.assertNotIn(anchor["attrs"].get("href"), {
                    "/trade-center", "/review-center",
                })

    def test_route_fix_does_not_unlock_legacy_corridors(self):
        canonical = match_ob_guard_policy("/ob/trade-center")
        self.assertEqual(canonical["match_type"], "exact")
        self.assertFalse(canonical["policy"].get("public_allowed", False))
        for legacy in ("/trade-center", "/review-center"):
            with self.subTest(path=legacy):
                result = match_ob_guard_policy(legacy)
                self.assertEqual(result["match_type"], "unmapped_default_deny")
                self.assertFalse(result["policy"]["public_allowed"])


if __name__ == "__main__":
    unittest.main()

"""Cross-vertical search, source normalization and duplicate candidate tests."""
import unittest
from buybox.core import new_opportunity, evaluate
from buybox.discovery import canonical_url, duplicate_candidates, filter_opportunities, card

class DiscoveryTests(unittest.TestCase):
    def test_tracking_urls_normalize(self):
        self.assertEqual(canonical_url("https://EXAMPLE.com/a/?utm_source=x&b=2&a=1#section"),
                         "https://example.com/a?a=1&b=2")
        self.assertIsNone(canonical_url("file:///tmp/secret"))

    def test_same_listing_only_suggests_duplicate(self):
        a = new_opportunity("atm","Route", 100000,{"url":"https://example.com/deal?utm_source=mail"})
        b = new_opportunity("atm","Different label", 110000,{"url":"https://example.com/deal"})
        matches=duplicate_candidates(a,[b])
        self.assertEqual(matches[0]["reason"],"EXACT_SOURCE_URL")
        self.assertFalse(matches[0]["auto_merge"])

    def test_vertical_filter_and_no_missing_as_zero(self):
        a=new_opportunity("atm","Georgia Route",100000)
        b=new_opportunity("multifamily","Garden Apartment",None)
        self.assertEqual(filter_opportunities([a,b],vertical="atm"),[a])
        self.assertEqual(filter_opportunities([a,b],max_price=200000),[a])
        self.assertEqual(filter_opportunities([a,b],query="Garden"),[b])

    def test_cards_are_vertical_aware(self):
        op=new_opportunity("land_farm","Green land",250000)
        rendered=card(op,evaluate(op))
        self.assertEqual(rendered["vertical_label"],"Land & Farms")
        self.assertEqual(rendered["evidence_confidence"],0)
        self.assertEqual(rendered["readiness"],"UNKNOWN")

if __name__=="__main__":
    unittest.main()

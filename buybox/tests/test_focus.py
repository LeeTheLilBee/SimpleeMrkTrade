"""Focus uses only actual saved events and tasks, with stable deterministic date tests."""
import unittest
from buybox.core import new_opportunity
from buybox.dealroom import new_task
from buybox.focus import build_focus

class FocusTests(unittest.TestCase):
    def test_empty_focus_has_no_fabricated_notifications(self):
        result=build_focus([],lambda _:[],as_of="2026-09-26")
        self.assertEqual(result["tasks"],[])
        self.assertEqual(result["changes"],[])
        self.assertEqual(result["total_opportunities"],0)

    def test_due_today_and_events_are_real_records(self):
        op=new_opportunity("atm","Owner entered route")
        op,item=new_task(op,title="Request inventory",due_date="2026-09-26")
        events=[{"event_type":"OriginalDocumentReceived","occurred_at":"2026-09-25T15:00:00+00:00"},
                {"event_type":"PageOpened","occurred_at":"2026-09-26T15:00:00+00:00"}]
        output=build_focus([op],lambda oid:events,as_of="2026-09-26")
        self.assertEqual(output["needs_attention"],1)
        self.assertEqual(output["tasks"][0]["priority"],"DUE_TODAY")
        self.assertEqual(len(output["changes"]),1)
        self.assertEqual(output["changes"][0]["event_type"],"OriginalDocumentReceived")

if __name__=="__main__": unittest.main()

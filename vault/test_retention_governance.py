import sqlite3
import pytest
from vault.retention_governance import RetentionGovernance,GovernanceError

def test_hold_blocks_disposition_and_replay(tmp_path):
    g=RetentionGovernance(tmp_path/"retention.db")
    base=dict(entity_id="entity-1",version_id="version-1")
    assert g.status(**base)["disposition_blocked"]
    g.record(**base,event_id="policy-1",action="POLICY_SET",policy_id="retain-7",reason="synthetic policy")
    g.record(**base,event_id="hold-1",action="HOLD_PLACED",reason="litigation preservation")
    assert g.status(**base)=={"policy_id":"retain-7","legal_hold":True,"disposition_blocked":True}
    with pytest.raises(GovernanceError,match="blocks"):
        g.record(**base,event_id="review-1",action="DISPOSITION_REVIEWED",reason="review")
    assert g.record(**base,event_id="hold-1",action="HOLD_PLACED",reason="litigation preservation")=="hold-1"
    with pytest.raises(GovernanceError,match="conflicting"):
        g.record(**base,event_id="hold-1",action="HOLD_PLACED",reason="changed")
    g.record(**base,event_id="release-1",action="HOLD_RELEASED",reason="approved release")
    assert not g.status(**base)["disposition_blocked"]
    g.record(**base,event_id="review-1",action="DISPOSITION_REVIEWED",reason="review")
    with sqlite3.connect(g.path) as db:
        with pytest.raises(sqlite3.IntegrityError):db.execute("DELETE FROM governance_events")
    assert g.status(entity_id="entity-2",version_id="version-1")["policy_id"] is None

def test_release_without_hold_fails(tmp_path):
    g=RetentionGovernance(tmp_path/"retention.db")
    with pytest.raises(GovernanceError,match="no active"):
        g.record(event_id="release",entity_id="entity",version_id="version",
                 action="HOLD_RELEASED",reason="no hold")

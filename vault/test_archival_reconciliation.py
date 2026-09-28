import pytest
from vault.test_local_archival_integration import fixture,params
from vault.archival_reconciliation import reconcile_archival,ReconciliationError

def test_missing_canonical_receipt_keeps_reconcile_hold(tmp_path):
    app=fixture(tmp_path)
    with pytest.raises(Exception):app.archive(**params(),fail_after_cloud=True)
    with pytest.raises(ReconciliationError,match="canonical receipt absent"):
        reconcile_archival(journal=app.journal,registry=app.registry,
            store=app.store,verifier=app.verifier,request_id="request-1",entity_id="entity-1")
    assert app.journal.status("request-1")=="RECONCILE_REQUIRED"

def test_cross_entity_reconciliation_denied(tmp_path):
    app=fixture(tmp_path)
    with pytest.raises(Exception):app.archive(**params(),fail_after_cloud=True)
    with pytest.raises(ReconciliationError,match="entity-scoped"):
        reconcile_archival(journal=app.journal,registry=app.registry,
            store=app.store,verifier=app.verifier,request_id="request-1",entity_id="other")

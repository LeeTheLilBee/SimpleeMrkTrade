from vault.test_local_archival_integration import fixture,params
from vault.integrity_report import integrity_report

def test_report_matches_canonical_receipt(tmp_path):
    app=fixture(tmp_path)
    app.archive(**params())
    report=integrity_report(entity_id="entity-1",journal=app.journal,registry=app.registry)
    assert report["integrity_ok"]
    assert report["canonical_receipt_count"]==1
    assert integrity_report(entity_id="other",journal=app.journal,registry=app.registry)["canonical_receipt_count"]==0

def test_report_flags_cloud_crash(tmp_path):
    app=fixture(tmp_path)
    try:app.archive(**params(),fail_after_cloud=True)
    except Exception:pass
    report=integrity_report(entity_id="entity-1",journal=app.journal,registry=app.registry)
    assert not report["integrity_ok"]
    assert any(i["issue"]=="RECONCILIATION_REQUIRED" for i in report["issues"])

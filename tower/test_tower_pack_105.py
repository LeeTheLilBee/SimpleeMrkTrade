
from __future__ import annotations

import json, os, sys, subprocess
from pathlib import Path

PROJECT_ROOT = Path('/content/SimpleeMrkTrade_REAL_CLONE')
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WEB_APP = PROJECT_ROOT / 'web' / 'app.py'

def show(title, payload=None):
    print()
    print('=' * 80)
    print(title)
    print('=' * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))

def no_secret(payload):
    s = json.dumps(payload, sort_keys=True, default=str).lower()
    bad = ['should_not_survive','tower_keycard=','"raw_token":','"api_key":','"password":','ghp_should_not_survive','sk_live_should_not_survive']
    for item in bad:
        assert item not in s, item

def run_tests():
    from tower.ob_route_coverage_report import (
        PANEL_PATH, REPORT_PATH, build_ob_route_coverage_report,
        load_ob_route_coverage_status, parse_web_app_routes, reset_ob_route_coverage_for_test
    )

    reset = reset_ob_route_coverage_for_test()
    show('RESET OB ROUTE COVERAGE', reset)
    assert reset.get('ok') is True

    text = WEB_APP.read_text(encoding='utf-8', errors='replace')
    checks = {
        'status_route_marker': 'PACK105_TOWER_OB_GUARD_STATUS_ROUTE' in text,
        'status_route_path': '/tower/ob-guard-status.json' in text,
        'pack104_helper_present': 'PACK104_TOWER_OB_FLASK_GUARD_HELPERS' in text,
    }
    show('PACK 105 WEB APP CHECKS', checks)
    assert all(checks.values())

    routes = parse_web_app_routes(text)
    show('PARSED ROUTE SUMMARY', {
        'count': len(routes),
        'guarded_count': len([r for r in routes if r.get('guarded')]),
        'sample': routes[:5],
    })
    assert len(routes) >= 1
    assert any(r.get('guarded') for r in routes)

    report = build_ob_route_coverage_report(write_panel=True)
    show('OB ROUTE COVERAGE REPORT', {
        'ok': report.get('ok'),
        'total_route_functions': report.get('total_route_functions'),
        'needs_guard_count': report.get('needs_guard_count'),
        'guarded_needed_count': report.get('guarded_needed_count'),
        'unguarded_needed_count': report.get('unguarded_needed_count'),
        'unguarded_high_risk_count': report.get('unguarded_high_risk_count'),
        'coverage_pct': report.get('coverage_pct'),
        'readiness_score': report.get('readiness_score'),
        'by_category': report.get('by_category'),
        'guarded_by_category': report.get('guarded_by_category'),
    })
    assert report.get('ok') is True
    assert report.get('helper_installed') is True
    assert report.get('total_route_functions', 0) >= 1
    assert report.get('guarded_needed_count', 0) >= 1
    assert report.get('coverage_pct', 0) >= 1
    assert report.get('readiness_score', 0) >= 60
    assert report.get('no_secret_leakage') is True
    assert REPORT_PATH.exists()
    assert PANEL_PATH.exists()
    no_secret(report)

    status = load_ob_route_coverage_status()
    show('OB ROUTE COVERAGE STATUS', status)
    assert status.get('ok') is True
    assert status.get('pack') == '105'
    assert status.get('coverage_pct') == report.get('coverage_pct')
    assert status.get('status_no_secret_leakage') is True
    no_secret(status)

    html = PANEL_PATH.read_text(encoding='utf-8')
    assert 'The Tower · OB Route Coverage' in html
    assert 'SHOULD_NOT_SURVIVE' not in html
    assert 'tower_keycard=' not in html

    for path in [WEB_APP, PROJECT_ROOT / 'tower' / 'ob_route_coverage_report.py']:
        result = subprocess.run([sys.executable, '-m', 'py_compile', str(path)], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        show('PY_COMPILE ' + str(path), {'returncode': result.returncode, 'stderr': result.stderr})
        assert result.returncode == 0

    final = {
        'pack': '105',
        'status': 'passed',
        'coverage_pct': report.get('coverage_pct'),
        'guarded_needed_count': report.get('guarded_needed_count'),
        'unguarded_high_risk_count': report.get('unguarded_high_risk_count'),
        'human_reason': 'OB route guard coverage report, panel, and status endpoint installed.'
    }
    show('PACK 105 RESULT', final)
    return final

if __name__ == '__main__':
    run_tests()

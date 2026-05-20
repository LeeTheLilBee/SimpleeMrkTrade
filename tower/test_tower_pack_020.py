
# =============================================================================
# The Tower - Pack 020 Test
# =============================================================================

import json
from pathlib import Path

from tower.security_command_page import (
    render_security_command_dashboard_html,
    save_security_command_dashboard_html,
    get_security_command_dashboard_html,
)


def _print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _print_json(payload):
    print(json.dumps(payload, indent=2, sort_keys=True))


def main():
    _print_header("RENDER SECURITY COMMAND DASHBOARD HTML")
    html_doc = render_security_command_dashboard_html()

    _print_json({
        "html_length": len(html_doc),
        "has_doctype": html_doc.lstrip().lower().startswith("<!doctype html>"),
        "has_tower_title": "The Tower" in html_doc,
        "has_primary_owner_focus": "Primary Owner Focus" in html_doc,
        "has_review_lanes": "Review Lanes" in html_doc,
    })

    _print_header("SAVE SECURITY COMMAND DASHBOARD HTML")
    saved = save_security_command_dashboard_html()
    _print_json(saved)

    _print_header("READ SAVED HTML")
    loaded_html = get_security_command_dashboard_html()
    _print_json({
        "path_exists": Path(saved["path"]).exists(),
        "loaded_length": len(loaded_html),
        "contains_attention_required": "Attention Required" in loaded_html,
        "contains_command_metrics": "Command Metrics" in loaded_html,
    })

    assert html_doc.lstrip().lower().startswith("<!doctype html>")
    assert "The Tower" in html_doc
    assert "Primary Owner Focus" in html_doc
    assert "Review Lanes" in html_doc
    assert saved.get("ok") is True
    assert Path(saved["path"]).exists()
    assert len(loaded_html) > 1000

    _print_header("PACK 020 RESULT")
    _print_json({
        "pack": "020",
        "status": "passed",
        "human_reason": "Security Command Dashboard HTML was rendered and saved as a standalone admin-ready page.",
        "html_path": saved["path"],
    })


if __name__ == "__main__":
    main()

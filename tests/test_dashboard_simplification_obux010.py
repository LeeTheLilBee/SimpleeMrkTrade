from pathlib import Path


TEMPLATE = Path(
    "web/templates/dashboard.html"
)

ORGANIZER = Path(
    "web/static/ob/ob_dashboard_simplification_obux.js"
)

CSS = Path(
    "web/static/ob/ob_dashboard_soulaana_obux.css"
)

DASHBOARD = Path(
    "web/static/ob/ob_dashboard.js"
)


def test_obux010_template_removed_old_static_soulaana_duplicate():

    text = TEMPLATE.read_text(
        encoding="utf-8"
    )

    assert (
        '<div class="ob-panel soulaana-panel">'
        not in text
    )

    assert (
        "OBUX006-OBUX010 DASHBOARD SIMPLIFICATION"
        in text
    )


def test_obux010_organizer_is_loaded_last_before_body_close():

    text = TEMPLATE.read_text(
        encoding="utf-8"
    )

    organizer = (
        "ob_dashboard_simplification_obux.js"
    )

    assert organizer in text

    assert (
        text.rfind(
            organizer
        )
        >
        text.rfind(
            "ob_manual_live_checklist_record_save_flow.js"
        )
    )


def test_obux010_engineering_panels_are_moved_not_deleted():

    text = ORGANIZER.read_text(
        encoding="utf-8"
    )

    assert (
        "Show me why"
        in DASHBOARD.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "appendChild"
        in text
    )

    assert (
        "panels_deleted: false"
        in text
    )


def test_obux010_dark_dashboard_has_no_white_background():

    text = CSS.read_text(
        encoding="utf-8"
    ).lower()

    assert (
        "background: white"
        not in text
    )

    assert (
        "background-color: white"
        not in text
    )

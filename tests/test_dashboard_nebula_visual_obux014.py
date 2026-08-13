from pathlib import Path


CSS = Path(
    "web/static/ob/ob_dashboard_soulaana_obux.css"
)


def test_obux014_dashboard_uses_nebula_gradients():

    text = CSS.read_text(
        encoding="utf-8"
    ).lower()

    assert (
        "radial-gradient"
        in text
    )

    assert (
        "background-attachment:"
        in text
    )

    assert (
        "#17172f"
        in text
    )

    assert (
        "#222049"
        in text
    )


def test_obux014_no_white_background():

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

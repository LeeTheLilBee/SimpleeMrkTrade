from pathlib import Path


def test_hosted_requirements():
    path = Path(
        "deploy/hosted_tower/requirements.txt"
    )

    assert path.is_file()

    text = path.read_text(
        encoding="utf-8"
    )

    assert "Flask" in text
    assert "gunicorn" in text

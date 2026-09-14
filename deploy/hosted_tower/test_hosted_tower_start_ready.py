from pathlib import Path


def test_hosted_start_script():
    path = Path(
        "deploy/hosted_tower/start.sh"
    )

    assert path.is_file()

    text = path.read_text(
        encoding="utf-8"
    )

    assert "set -euo pipefail" in text
    assert "-m gunicorn" in text
    assert "web.hosted_tower:app" in text
    assert '${PORT:-10000}' in text

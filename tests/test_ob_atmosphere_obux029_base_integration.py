from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BASE = (
    ROOT
    / "web/templates/base.html"
).read_text(
    encoding="utf-8"
)


def test_obux029_base_backed_pages_use_same_atmosphere_engine():
    assert "ob/ob_atmosphere.css" in BASE
    assert (
        'data-ob-room="{{ ob_room|default(\'legacy\') }}"'
        in BASE
    )
    assert 'class="ob-sky"' in BASE
    assert 'data-ob-atmosphere-version="OBUX026-OBUX030"' in BASE


def test_obux029_atmosphere_stylesheet_loads_after_legacy_inline_style():
    assert "</style>" in BASE
    assert BASE.index("ob_atmosphere.css") > BASE.index("</style>")


def test_obux029_base_shell_itself_remains_present():
    assert 'class="observatory-shell"' in BASE
    assert 'class="observatory-rail"' in BASE
    assert '{% block content %}{% endblock %}' in BASE

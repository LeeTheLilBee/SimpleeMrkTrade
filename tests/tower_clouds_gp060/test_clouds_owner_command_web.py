from clouds.owner_command_experience_service import (
    get_owner_command_experience,
)
from tower.clouds_owner_command_web import (
    render_owner_command_experience,
)


def _page_factory(*, title, body):
    return (
        "<html><title>"
        + title
        + "</title><body>"
        + body
        + "</body></html>"
    )


def test_owner_command_is_explanation_first_and_card_based():
    html = (
        render_owner_command_experience(
            experience=(
                get_owner_command_experience()
            ),
            page_factory=_page_factory,
            canonical_title="The Clouds",
            canonical_subtitle=(
                "Simplee World Owner Command"
            ),
        )
    )

    assert "Needs You" in html
    assert "Keep Watching" in html
    assert "Can Wait" in html
    assert "Soulaana explains" in html
    assert "Ecosystem Lines" in html

    assert (
        "/tower/ecosystem/launch/"
        in html
    )


def test_return_context_restores_owner_orientation():
    html = (
        render_owner_command_experience(
            experience=(
                get_owner_command_experience()
            ),
            page_factory=_page_factory,
            canonical_title="The Clouds",
            canonical_subtitle=(
                "Simplee World Owner Command"
            ),
            resume="clouds-observatory",
            returned_from="observatory",
        )
    )

    assert "Back in Clouds." in html
    assert "I kept your place" in html
    assert "resume-focus" in html

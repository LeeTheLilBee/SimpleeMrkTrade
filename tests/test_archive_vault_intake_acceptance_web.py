from flask import Flask

import tower.archive_vault_intake_acceptance as intake


def build_app(
    monkeypatch,
):

    app = Flask(
        __name__
    )


    app.secret_key = (
        "archive-vault-intake-test"
    )


    monkeypatch.setattr(
        intake,
        "owner_session_active",
        lambda: True,
    )


    intake.register_archive_vault_intake_acceptance(
        app
    )


    return app


def test_acceptance_route(
    monkeypatch,
):

    app = (
        build_app(
            monkeypatch
        )
    )


    monkeypatch.setattr(

        intake,

        "accept_and_record_archive_vault_handoff",

        lambda handoff_id: {

            "status": (
                "archive_vault_handoff_accepted"
            ),

            "handoff_id": (
                handoff_id
            ),

            "accepted": True,

            "sealed": True,

            "vault_status": (
                "VAULT_SEALED"
            ),

            "vault_receipt_id": (
                "receipt-test"
            ),
        },
    )


    response = (
        app.test_client().post(

            "/tower/archive-vault/"
            "intake/handoff-test"
        )
    )


    data = (
        response.get_json()
    )


    assert (
        response.status_code
        == 200
    )


    assert (
        data[
            "vault_status"
        ]
        == "VAULT_SEALED"
    )


def test_missing_handoff_404(
    monkeypatch,
):

    app = (
        build_app(
            monkeypatch
        )
    )


    monkeypatch.setattr(

        intake,

        "accept_and_record_archive_vault_handoff",

        lambda handoff_id: {

            "status": (
                "archive_vault_handoff_not_found"
            ),

            "accepted": False,

            "sealed": False,
        },
    )


    response = (
        app.test_client().post(

            "/tower/archive-vault/"
            "intake/missing"
        )
    )


    assert (
        response.status_code
        == 404
    )


def test_acceptance_records_route(
    monkeypatch,
):

    app = (
        build_app(
            monkeypatch
        )
    )


    monkeypatch.setattr(

        intake,

        "archive_vault_acceptance_payload",

        lambda: {

            "status": (
                "archive_vault_acceptance_records_ready"
            ),

            "total": 1,

            "recent": [
                {
                    "vault_receipt_id": (
                        "receipt-test"
                    ),
                }
            ],
        },
    )


    response = (
        app.test_client().get(

            "/tower/archive-vault/"
            "acceptance-records.json"
        )
    )


    assert (
        response.status_code
        == 200
    )


    assert (
        response.get_json()[
            "total"
        ]
        == 1
    )


def test_registration_idempotent(
    monkeypatch,
):

    app = (
        build_app(
            monkeypatch
        )
    )


    intake.register_archive_vault_intake_acceptance(
        app
    )


    rules = [

        rule.rule

        for rule
        in app.url_map.iter_rules()
    ]


    assert (
        rules.count(
            "/tower/archive-vault/intake/<handoff_id>"
        )
        == 1
    )

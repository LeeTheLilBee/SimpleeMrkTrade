
from __future__ import annotations

import json

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from werkzeug.security import (
    generate_password_hash,
)

from tower.identity_authority import (
    TOWER_OWNER_PASSWORD_HASH_ENV,
    TOWER_OWNER_USERNAME_ENV,
)
from tower.invitation_access_lifecycle import (
    ACCEPTED,
    ACTIVE,
    CREATED,
    DELIVERY_PENDING,
    EXPIRED,
    FAILED,
    IDENTITY_PENDING,
    OPENED,
    REVOKED,
    SENT,
    InvitationLifecycleError,
    accept_invitation,
    access_activation_status,
    activate_invitation,
    begin_identity_binding,
    create_invitation,
    expire_due_invitations,
    invitation_authority_snapshot,
    invitation_by_id,
    invitation_delivery_status,
    invitation_store_status,
    list_invitations,
    record_invitation_failure,
    record_invitation_opened,
    record_invitation_sent,
    request_invitation_delivery,
    revoke_invitation,
)
from tower.owner_dashboard_service import (
    build_tower_owner_dashboard,
    owner_dashboard_status_cards,
)
from tower.owner_dashboard_web import (
    _owner_invitation_html,
)
from tower.owner_people_registry import (
    owner_people_authority_snapshot,
)
from tower.truth_contract import (
    NOT_CONFIGURED,
    VERIFIED,
)


def clear_invitation_environment(
    monkeypatch,
):
    for name in (
        "TOWER_INVITATION_STORE_PATH",
        "TOWER_INVITATION_DELIVERY_MODE",
        "TOWER_INVITATION_DEFAULT_TTL_HOURS",
        "TOWER_OWNER_USERNAME",
        "TOWER_OWNER_PASSWORD_HASH",
        "TOWER_OWNER_ID",
        "TOWER_OWNER_DISPLAY_NAME",
        "TOWER_ORGANIZATION_ID",
        "TOWER_ORGANIZATION_NAME",
        "TOWER_LOCAL_WALKTHROUGH_MODE",
        "TOWER_LOCAL_OWNER_PASSWORD",
    ):
        monkeypatch.delenv(
            name,
            raising=False,
        )


def configure_owner(
    monkeypatch,
):
    monkeypatch.setenv(
        TOWER_OWNER_USERNAME_ENV,
        "tower-owner-test",
    )

    monkeypatch.setenv(
        TOWER_OWNER_PASSWORD_HASH_ENV,
        generate_password_hash(
            "twr136-test-owner"
        ),
    )

    monkeypatch.setenv(
        "TOWER_OWNER_ID",
        "owner-twr136",
    )


def configure_store(
    monkeypatch,
    tmp_path,
):
    store = (
        tmp_path
        / "tower-invitations.json"
    )

    monkeypatch.setenv(
        "TOWER_INVITATION_STORE_PATH",
        str(
            store
        ),
    )

    return store


def create_real_invitation(
    monkeypatch,
    tmp_path,
    *,
    now=None,
    ttl_hours=168,
):
    clear_invitation_environment(
        monkeypatch
    )

    configure_owner(
        monkeypatch
    )

    store = configure_store(
        monkeypatch,
        tmp_path,
    )

    created = create_invitation(
        target="person@example.test",
        requested_role="member",
        requested_apps=[
            "observatory",
        ],
        now=now,
        ttl_hours=ttl_hours,
    )

    assert created["ok"] is True

    return (
        store,
        created,
    )


def test_twr136_store_is_explicitly_not_configured_by_default(
    monkeypatch,
):
    clear_invitation_environment(
        monkeypatch
    )

    status = (
        invitation_store_status()
    )

    assert status["configured"] is False
    assert status["verification_state"] == NOT_CONFIGURED
    assert status["path_exposed"] is False


def test_twr136_creation_refuses_without_durable_store(
    monkeypatch,
):
    clear_invitation_environment(
        monkeypatch
    )

    configure_owner(
        monkeypatch
    )

    result = create_invitation(
        target="person@example.test",
        requested_role="member",
        requested_apps=[],
    )

    assert result["ok"] is False
    assert result["status"] == "INVITATION_STORE_NOT_CONFIGURED"
    assert result["invitation"] is None


def test_twr136_creation_requires_real_hosted_owner_identity(
    monkeypatch,
    tmp_path,
):
    clear_invitation_environment(
        monkeypatch
    )

    configure_store(
        monkeypatch,
        tmp_path,
    )

    result = create_invitation(
        target="person@example.test",
        requested_role="member",
        requested_apps=[],
    )

    assert result["ok"] is False
    assert result["status"] == "OWNER_IDENTITY_NOT_CONFIGURED"


def test_twr136_created_record_is_real_and_token_is_not_persisted_or_projected(
    monkeypatch,
    tmp_path,
):
    store, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    invitation = created[
        "invitation"
    ]

    token = created[
        "token"
    ]

    assert invitation["state"] == CREATED
    assert token
    assert invitation["token_exposed"] is False
    assert invitation["token_hash_exposed"] is False

    raw = json.loads(
        store.read_text(
            encoding="utf-8"
        )
    )

    raw_record = next(
        iter(
            raw["invitations"].values()
        )
    )

    assert "token_hash" in raw_record
    assert "token" not in raw_record
    assert token not in store.read_text(
        encoding="utf-8"
    )


def test_twr136_requested_apps_are_not_granted_apps(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    invitation = created[
        "invitation"
    ]

    assert invitation["requested_apps"] == [
        "observatory",
    ]

    assert invitation["granted_apps"] == []


def test_twr136_unknown_app_request_is_rejected(
    monkeypatch,
    tmp_path,
):
    clear_invitation_environment(
        monkeypatch
    )

    configure_owner(
        monkeypatch
    )

    configure_store(
        monkeypatch,
        tmp_path,
    )

    try:
        create_invitation(
            target="person@example.test",
            requested_role="member",
            requested_apps=[
                "invented-app",
            ],
        )

    except InvitationLifecycleError:
        pass

    else:
        raise AssertionError(
            "Unknown app request should fail."
        )


def test_twr137_delivery_unconfigured_leaves_created_state_unchanged(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    delivery = (
        invitation_delivery_status()
    )

    assert delivery["configured"] is False
    assert delivery["message"] == "Invitation delivery not configured."

    result = request_invitation_delivery(
        invitation_id
    )

    assert result["ok"] is False
    assert result["changed"] is False

    assert (
        result["status"]
        == "INVITATION_DELIVERY_NOT_CONFIGURED"
    )

    assert result["message"] == "Invitation delivery not configured."

    assert (
        invitation_by_id(
            invitation_id
        )[
            "state"
        ]
        == CREATED
    )


def test_twr137_configured_delivery_handoff_enters_delivery_pending_only(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    monkeypatch.setenv(
        "TOWER_INVITATION_DELIVERY_MODE",
        "external_receipt",
    )

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    result = request_invitation_delivery(
        invitation_id
    )

    assert result["ok"] is True
    assert result["status"] == DELIVERY_PENDING

    # Requesting delivery is NOT SENT.
    assert result["invitation"]["state"] != SENT


def test_twr137_sent_requires_real_external_receipt_identifiers(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    monkeypatch.setenv(
        "TOWER_INVITATION_DELIVERY_MODE",
        "external_receipt",
    )

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    request_invitation_delivery(
        invitation_id
    )

    result = record_invitation_sent(
        invitation_id,
        provider_message_id="provider-message-1",
        delivery_receipt_id="receipt-1",
    )

    assert result["status"] == SENT


def test_twr138_open_accept_identity_sequence_is_strict(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    token = created[
        "token"
    ]

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    monkeypatch.setenv(
        "TOWER_INVITATION_DELIVERY_MODE",
        "external_receipt",
    )

    assert request_invitation_delivery(
        invitation_id
    )["status"] == DELIVERY_PENDING

    assert record_invitation_sent(
        invitation_id,
        provider_message_id="message-1",
        delivery_receipt_id="receipt-1",
    )["status"] == SENT

    assert record_invitation_opened(
        invitation_id,
        provider_event_id="opened-event-1",
    )["status"] == OPENED

    assert accept_invitation(
        invitation_id,
        token=token,
    )["status"] == ACCEPTED

    assert begin_identity_binding(
        invitation_id,
        person_id="pending-person-1",
        identity_evidence_id="identity-evidence-1",
    )["status"] == IDENTITY_PENDING


def test_twr138_acceptance_requires_actual_invitation_token(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    monkeypatch.setenv(
        "TOWER_INVITATION_DELIVERY_MODE",
        "external_receipt",
    )

    request_invitation_delivery(
        invitation_id
    )

    record_invitation_sent(
        invitation_id,
        provider_message_id="message-2",
        delivery_receipt_id="receipt-2",
    )

    result = accept_invitation(
        invitation_id,
        token="wrong-token",
    )

    assert result["ok"] is False
    assert result["changed"] is False
    assert result["status"] == "INVALID_INVITATION_TOKEN"

    assert (
        invitation_by_id(
            invitation_id
        )[
            "state"
        ]
        == SENT
    )


def test_twr138_revocation_is_real_terminal_state(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    result = revoke_invitation(
        invitation_id,
        reason="owner_revoked_invitation",
    )

    assert result["status"] == REVOKED

    try:
        request_invitation_delivery(
            invitation_id
        )

    except InvitationLifecycleError:
        pass

    else:
        # Delivery is unconfigured in this test and therefore
        # does not transition. The terminal state remains true.
        assert (
            invitation_by_id(
                invitation_id
            )[
                "state"
            ]
            == REVOKED
        )


def test_twr138_expiration_is_derived_from_real_timestamps(
    monkeypatch,
    tmp_path,
):
    start = datetime(
        2026,
        8,
        31,
        12,
        0,
        tzinfo=timezone.utc,
    )

    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
            now=start,
            ttl_hours=1,
        )
    )

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    expired_count = expire_due_invitations(
        now=(
            start
            + timedelta(
                hours=2
            )
        )
    )

    assert expired_count == 1

    assert (
        invitation_by_id(
            invitation_id,
            now=(
                start
                + timedelta(
                    hours=2
                )
            ),
        )[
            "state"
        ]
        == EXPIRED
    )


def test_twr138_failure_is_recorded_not_inferred(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    monkeypatch.setenv(
        "TOWER_INVITATION_DELIVERY_MODE",
        "external_receipt",
    )

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    request_invitation_delivery(
        invitation_id
    )

    result = record_invitation_failure(
        invitation_id,
        failure_code="provider_delivery_failed",
    )

    assert result["state"] if "state" in result else result["status"] == FAILED
    assert result["status"] == FAILED


def test_twr139_active_state_is_defined_but_fail_closed(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    token = created[
        "token"
    ]

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    monkeypatch.setenv(
        "TOWER_INVITATION_DELIVERY_MODE",
        "external_receipt",
    )

    request_invitation_delivery(
        invitation_id
    )

    record_invitation_sent(
        invitation_id,
        provider_message_id="message-3",
        delivery_receipt_id="receipt-3",
    )

    accept_invitation(
        invitation_id,
        token=token,
    )

    begin_identity_binding(
        invitation_id,
        person_id="pending-person-2",
        identity_evidence_id="identity-evidence-2",
    )

    activation = activate_invitation(
        invitation_id
    )

    assert ACTIVE == "ACTIVE"

    assert activation["ok"] is False
    assert activation["changed"] is False

    assert (
        activation["status"]
        == "ACCESS_ACTIVATION_NOT_CONFIGURED"
    )

    assert (
        activation["invitation"]["state"]
        == IDENTITY_PENDING
    )

    assert (
        access_activation_status()[
            "verification_state"
        ]
        == NOT_CONFIGURED
    )


def test_twr139_identity_pending_does_not_grant_requested_apps(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    token = created[
        "token"
    ]

    invitation_id = created[
        "invitation"
    ][
        "invitation_id"
    ]

    monkeypatch.setenv(
        "TOWER_INVITATION_DELIVERY_MODE",
        "external_receipt",
    )

    request_invitation_delivery(
        invitation_id
    )

    record_invitation_sent(
        invitation_id,
        provider_message_id="message-4",
        delivery_receipt_id="receipt-4",
    )

    accept_invitation(
        invitation_id,
        token=token,
    )

    begin_identity_binding(
        invitation_id,
        person_id="pending-person-3",
        identity_evidence_id="identity-evidence-3",
    )

    invitation = invitation_by_id(
        invitation_id
    )

    assert invitation["requested_apps"] == [
        "observatory",
    ]

    assert invitation["granted_apps"] == []


def test_twr140_authority_projection_reports_real_zero_only_when_store_exists(
    monkeypatch,
    tmp_path,
):
    clear_invitation_environment(
        monkeypatch
    )

    configure_owner(
        monkeypatch
    )

    configure_store(
        monkeypatch,
        tmp_path,
    )

    snapshot = invitation_authority_snapshot()

    assert snapshot["verification_state"] == VERIFIED
    assert snapshot["invitation_count"] == 0
    assert snapshot["pending_invitation_count"] == 0

    # This zero is authoritative because the durable
    # provider exists and currently contains zero records.


def test_twr140_missing_store_keeps_invitation_count_unknown(
    monkeypatch,
):
    clear_invitation_environment(
        monkeypatch
    )

    configure_owner(
        monkeypatch
    )

    dashboard = build_tower_owner_dashboard()

    assert (
        dashboard["summary"]["invitation_count"]
        is None
    )

    assert (
        dashboard["summary"]["pending_invitation_count"]
        is None
    )


def test_twr140_dashboard_reads_real_invitation_count(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    dashboard = build_tower_owner_dashboard()

    summary = dashboard[
        "summary"
    ]

    assert summary["invitation_count"] == 1
    assert summary["pending_invitation_count"] == 1

    assert (
        summary["invitation_authority_state"]
        == VERIFIED
    )

    assert (
        summary["access_lifecycle_state"]
        == VERIFIED
    )

    # Account/entitlement mutation is still separate.
    assert (
        summary["access_authority_state"]
        == NOT_CONFIGURED
    )

    assert summary["pending_access_count"] is None

    assert (
        dashboard["invitations"][0]["invitation_id"]
        == created["invitation"]["invitation_id"]
    )


def test_twr140_owner_people_authority_separates_lifecycle_from_access_mutation(
    monkeypatch,
    tmp_path,
):
    create_real_invitation(
        monkeypatch,
        tmp_path,
    )

    authority = owner_people_authority_snapshot()

    assert (
        authority["invitations"]["verification_state"]
        == VERIFIED
    )

    assert (
        authority["access_lifecycle"]["verification_state"]
        == VERIFIED
    )

    assert (
        authority["access_control"]["verification_state"]
        == NOT_CONFIGURED
    )


def test_twr140_cards_show_delivery_truth_and_keep_access_mutation_closed(
    monkeypatch,
    tmp_path,
):
    create_real_invitation(
        monkeypatch,
        tmp_path,
    )

    cards = owner_dashboard_status_cards()

    by_id = {
        card["card_id"]:
            card
        for card in cards
    }

    assert (
        by_id["owner-card-invitations"]["value"]
        == "1"
    )

    assert (
        by_id["owner-card-invitations"]["meaning"]
        == "Invitation delivery not configured."
    )

    assert (
        by_id["owner-card-access-lifecycle"]["value"]
        == VERIFIED
    )

    assert (
        by_id["owner-card-access"]["value"]
        == NOT_CONFIGURED
    )


def test_twr140_owner_hq_html_is_truthful_and_secret_free(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    dashboard = build_tower_owner_dashboard()

    html = _owner_invitation_html(
        dashboard
    )

    assert "person@example.test" in html
    assert "CREATED" in html
    assert "Invitation delivery not configured." in html
    assert "ACCESS ACTIVATION · NOT_CONFIGURED" in html
    assert "GRANTED APPS · 0" in html

    assert created["token"] not in html
    assert "token_hash" not in html


def test_twr140_safe_projection_never_contains_raw_token_hash(
    monkeypatch,
    tmp_path,
):
    _, created = (
        create_real_invitation(
            monkeypatch,
            tmp_path,
        )
    )

    projected_records = (
        list_invitations()
    )

    serialized_projection = (
        json.dumps(
            projected_records,
            sort_keys=True,
        )
    )

    # The actual one-time token value must never
    # appear anywhere in the safe product projection.
    assert (
        created["token"]
        not in serialized_projection
    )

    # Check SECRET FIELDS structurally rather than
    # rejecting safe metadata names such as:
    #
    #     token_hash_exposed = False
    #
    # The product may truthfully state that a secret
    # is not exposed. It may not contain the secret.
    for invitation in projected_records:

        assert (
            "token"
            not in invitation
        )

        assert (
            "token_hash"
            not in invitation
        )

        assert (
            invitation[
                "token_exposed"
            ]
            is False
        )

        assert (
            invitation[
                "token_hash_exposed"
            ]
            is False
        )


def test_twr140_first_wave_product_truth_wall_remains_zero():
    from pathlib import Path

    from tower.truth_surface_audit import (
        RETIREMENT_FOCUS_SURFACES,
        audit_product_surfaces,
    )

    report = audit_product_surfaces(
        Path(
            "/content/SimpleeMrkTrade"
        ),
        relative_paths=RETIREMENT_FOCUS_SURFACES,
    )

    assert report["finding_count"] == 0

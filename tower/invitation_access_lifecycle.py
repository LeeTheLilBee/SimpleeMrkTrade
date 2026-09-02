
"""Canonical Tower invitation and onboarding lifecycle / TWR136-TWR140.

This module is a durable state authority when TOWER_INVITATION_STORE_PATH
is explicitly configured.

It does not send email.
It does not claim delivery without an external receipt.
It does not create user accounts.
It does not mutate app entitlements.
It does not claim ACTIVE without a future activation authority.
"""

from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
import secrets
import tempfile
import uuid

from datetime import (
    datetime,
    timedelta,
    timezone,
)
from pathlib import Path
from typing import Any, Dict, List

from tower.app_registry import (
    app_ids,
)
from tower.identity_authority import (
    hosted_owner_person_record,
)
from tower.truth_contract import (
    NOT_CONFIGURED,
    VERIFIED,
)


INVITATION_STORE_ENV = (
    "TOWER_INVITATION_STORE_PATH"
)

INVITATION_DELIVERY_MODE_ENV = (
    "TOWER_INVITATION_DELIVERY_MODE"
)

INVITATION_DEFAULT_TTL_HOURS_ENV = (
    "TOWER_INVITATION_DEFAULT_TTL_HOURS"
)

SUPPORTED_DELIVERY_MODE = (
    "external_receipt"
)

SCHEMA_VERSION = (
    "tower.invitation-access-lifecycle.v1"
)


CREATED = "CREATED"
DELIVERY_PENDING = "DELIVERY_PENDING"
SENT = "SENT"
OPENED = "OPENED"
ACCEPTED = "ACCEPTED"
IDENTITY_PENDING = "IDENTITY_PENDING"
ACTIVE = "ACTIVE"

EXPIRED = "EXPIRED"
REVOKED = "REVOKED"
FAILED = "FAILED"


ALL_STATES = {
    CREATED,
    DELIVERY_PENDING,
    SENT,
    OPENED,
    ACCEPTED,
    IDENTITY_PENDING,
    ACTIVE,
    EXPIRED,
    REVOKED,
    FAILED,
}


TERMINAL_STATES = {
    ACTIVE,
    EXPIRED,
    REVOKED,
    FAILED,
}


PENDING_STATES = {
    CREATED,
    DELIVERY_PENDING,
    SENT,
    OPENED,
    ACCEPTED,
    IDENTITY_PENDING,
}


ALLOWED_TRANSITIONS = {
    CREATED: {
        DELIVERY_PENDING,
        EXPIRED,
        REVOKED,
    },

    DELIVERY_PENDING: {
        SENT,
        FAILED,
        EXPIRED,
        REVOKED,
    },

    SENT: {
        OPENED,
        ACCEPTED,
        FAILED,
        EXPIRED,
        REVOKED,
    },

    OPENED: {
        ACCEPTED,
        FAILED,
        EXPIRED,
        REVOKED,
    },

    ACCEPTED: {
        IDENTITY_PENDING,
        FAILED,
        EXPIRED,
        REVOKED,
    },

    IDENTITY_PENDING: {
        ACTIVE,
        FAILED,
        EXPIRED,
        REVOKED,
    },

    ACTIVE:
        set(),

    EXPIRED:
        set(),

    REVOKED:
        set(),

    FAILED:
        set(),
}


INVITATION_AUTHORITY_SOURCE_ID = (
    "tower.identity.invitation_lifecycle"
)

INVITATION_DELIVERY_SOURCE_ID = (
    "tower.identity.invitation_delivery"
)

ACCESS_ONBOARDING_SOURCE_ID = (
    "tower.identity.access_onboarding_lifecycle"
)

ACCESS_ACTIVATION_SOURCE_ID = (
    "tower.identity.access_activation_authority"
)


class InvitationLifecycleError(
    RuntimeError
):
    pass


def _utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def _iso(
    value: datetime,
) -> str:
    return value.astimezone(
        timezone.utc
    ).isoformat()


def _parse_iso(
    value: str,
) -> datetime:

    parsed = datetime.fromisoformat(
        value
    )

    if parsed.tzinfo is None:
        raise InvitationLifecycleError(
            "Invitation timestamp must be timezone-aware."
        )

    return parsed.astimezone(
        timezone.utc
    )


def _store_path(
) -> Path | None:

    raw = str(
        os.environ.get(
            INVITATION_STORE_ENV,
            "",
        )
        or ""
    ).strip()

    if not raw:
        return None

    return Path(
        raw
    ).expanduser()


def invitation_store_status(
) -> Dict[str, Any]:

    path = _store_path()

    return {
        "configured":
            path is not None,

        "verification_state":
            (
                VERIFIED
                if path is not None
                else NOT_CONFIGURED
            ),

        "source_id":
            INVITATION_AUTHORITY_SOURCE_ID,

        "path_exposed":
            False,

        "reason":
            (
                "invitation_store_configured"
                if path is not None
                else "invitation_store_not_configured"
            ),
    }


def invitation_delivery_status(
) -> Dict[str, Any]:

    mode = str(
        os.environ.get(
            INVITATION_DELIVERY_MODE_ENV,
            "",
        )
        or ""
    ).strip()

    configured = (
        mode
        == SUPPORTED_DELIVERY_MODE
    )

    return {
        "configured":
            configured,

        "verification_state":
            (
                VERIFIED
                if configured
                else NOT_CONFIGURED
            ),

        "mode":
            (
                SUPPORTED_DELIVERY_MODE
                if configured
                else None
            ),

        "source_id":
            INVITATION_DELIVERY_SOURCE_ID,

        "message":
            (
                "Invitation delivery handoff configured."
                if configured
                else "Invitation delivery not configured."
            ),
    }


def access_activation_status(
) -> Dict[str, Any]:

    # ACTIVE remains intentionally unreachable here.
    #
    # General invited-user identity verification and
    # entitlement mutation are separate future authorities.

    return {
        "configured":
            False,

        "verification_state":
            NOT_CONFIGURED,

        "source_id":
            ACCESS_ACTIVATION_SOURCE_ID,

        "message":
            "Access activation authority not configured.",
    }


def _default_ttl_hours() -> int:

    raw = str(
        os.environ.get(
            INVITATION_DEFAULT_TTL_HOURS_ENV,
            "168",
        )
        or "168"
    ).strip()

    try:
        value = int(
            raw
        )
    except ValueError:
        value = 168

    return max(
        1,
        min(
            value,
            720,
        ),
    )


def _empty_store() -> Dict[str, Any]:

    return {
        "schema_version":
            SCHEMA_VERSION,

        "invitations":
            {},
    }


def _require_store_path() -> Path:

    path = _store_path()

    if path is None:
        raise InvitationLifecycleError(
            "Invitation store not configured."
        )

    return path


def _validate_store(
    store: Dict[str, Any],
) -> None:

    if not isinstance(
        store,
        dict,
    ):
        raise InvitationLifecycleError(
            "Invitation store must be an object."
        )

    if (
        store.get(
            "schema_version"
        )
        != SCHEMA_VERSION
    ):
        raise InvitationLifecycleError(
            "Invitation store schema mismatch."
        )

    invitations = store.get(
        "invitations"
    )

    if not isinstance(
        invitations,
        dict,
    ):
        raise InvitationLifecycleError(
            "Invitation collection must be an object."
        )

    for invitation_id, record in (
        invitations.items()
    ):

        if not isinstance(
            record,
            dict,
        ):
            raise InvitationLifecycleError(
                "Invitation record must be an object."
            )

        if (
            record.get(
                "invitation_id"
            )
            != invitation_id
        ):
            raise InvitationLifecycleError(
                "Invitation identifier mismatch."
            )

        if (
            record.get(
                "state"
            )
            not in ALL_STATES
        ):
            raise InvitationLifecycleError(
                "Invitation contains unknown state."
            )

        if not isinstance(
            record.get(
                "token_hash"
            ),
            str,
        ):
            raise InvitationLifecycleError(
                "Invitation token hash missing."
            )

        if (
            "token"
            in record
        ):
            raise InvitationLifecycleError(
                "Plain invitation token may not be persisted."
            )

        if not isinstance(
            record.get(
                "granted_apps",
                [],
            ),
            list,
        ):
            raise InvitationLifecycleError(
                "Granted apps must be a list."
            )


def _load_store_unlocked(
    path: Path,
) -> Dict[str, Any]:

    if not path.exists():
        return _empty_store()

    raw = path.read_text(
        encoding="utf-8"
    )

    if not raw.strip():
        raise InvitationLifecycleError(
            "Invitation store is empty."
        )

    store = json.loads(
        raw
    )

    _validate_store(
        store
    )

    return store


def _write_store_unlocked(
    path: Path,
    store: Dict[str, Any],
) -> None:

    _validate_store(
        store
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = (
        tempfile.mkstemp(
            prefix=(
                path.name
                + "."
            ),
            suffix=".tmp",
            dir=str(
                path.parent
            ),
        )
    )

    temporary_path = Path(
        temporary_name
    )

    try:

        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                store,
                handle,
                indent=2,
                sort_keys=True,
            )

            handle.write(
                "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.chmod(
            temporary_path,
            0o600,
        )

        os.replace(
            temporary_path,
            path,
        )

    finally:

        if temporary_path.exists():
            temporary_path.unlink()


def _with_locked_store(
    operation,
):

    path = _require_store_path()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lock_path = Path(
        str(path)
        + ".lock"
    )

    with lock_path.open(
        "a+",
        encoding="utf-8",
    ) as lock_handle:

        fcntl.flock(
            lock_handle.fileno(),
            fcntl.LOCK_EX,
        )

        try:

            store = (
                _load_store_unlocked(
                    path
                )
            )

            result = operation(
                store
            )

            _write_store_unlocked(
                path,
                store,
            )

            return result

        finally:

            fcntl.flock(
                lock_handle.fileno(),
                fcntl.LOCK_UN,
            )


def _token_hash(
    token: str,
) -> str:

    return hashlib.sha256(
        token.encode(
            "utf-8"
        )
    ).hexdigest()


def _safe_event(
    event: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "event":
            event.get(
                "event"
            ),

        "at_utc":
            event.get(
                "at_utc"
            ),

        "reason":
            event.get(
                "reason"
            ),

        "evidence_present":
            bool(
                event.get(
                    "evidence"
                )
            ),
    }


def _safe_record(
    record: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "invitation_id":
            record[
                "invitation_id"
            ],

        "target":
            record[
                "target"
            ],

        "requested_role":
            record[
                "requested_role"
            ],

        "requested_apps":
            list(
                record[
                    "requested_apps"
                ]
            ),

        # IMPORTANT:
        # Requested does not equal granted.
        "granted_apps":
            list(
                record.get(
                    "granted_apps",
                    [],
                )
            ),

        "state":
            record[
                "state"
            ],

        "created_by_person_id":
            record[
                "created_by_person_id"
            ],

        "created_at_utc":
            record[
                "created_at_utc"
            ],

        "updated_at_utc":
            record[
                "updated_at_utc"
            ],

        "expires_at_utc":
            record[
                "expires_at_utc"
            ],

        "identity_binding":
            record.get(
                "identity_binding"
            ),

        "events":
            [
                _safe_event(
                    event
                )
                for event
                in record.get(
                    "events",
                    [],
                )
            ],

        "token_exposed":
            False,

        "token_hash_exposed":
            False,
    }


def _event(
    *,
    event: str,
    now: datetime,
    reason: str | None = None,
    evidence: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    return {
        "event":
            event,

        "at_utc":
            _iso(
                now
            ),

        "reason":
            reason,

        # Raw evidence remains backstage in the
        # durable authority store.
        "evidence":
            (
                dict(
                    evidence
                )
                if evidence
                else None
            ),
    }


def _transition(
    record: Dict[str, Any],
    *,
    target_state: str,
    now: datetime,
    event_name: str,
    reason: str | None = None,
    evidence: Dict[str, Any] | None = None,
) -> None:

    current = record[
        "state"
    ]

    if (
        target_state
        not in ALLOWED_TRANSITIONS[
            current
        ]
    ):
        raise InvitationLifecycleError(
            f"Invalid invitation transition: "
            f"{current} -> {target_state}"
        )

    record[
        "state"
    ] = target_state

    record[
        "updated_at_utc"
    ] = _iso(
        now
    )

    record[
        "events"
    ].append(
        _event(
            event=event_name,
            now=now,
            reason=reason,
            evidence=evidence,
        )
    )


def _expire_due(
    store: Dict[str, Any],
    *,
    now: datetime,
) -> int:

    expired = 0

    for record in (
        store[
            "invitations"
        ].values()
    ):

        if (
            record[
                "state"
            ]
            not in PENDING_STATES
        ):
            continue

        expires_at = _parse_iso(
            record[
                "expires_at_utc"
            ]
        )

        if expires_at > now:
            continue

        _transition(
            record,
            target_state=EXPIRED,
            now=now,
            event_name="INVITATION_EXPIRED",
            reason="invitation_ttl_elapsed",
        )

        expired += 1

    return expired


def _record_by_id(
    store: Dict[str, Any],
    invitation_id: str,
) -> Dict[str, Any]:

    normalized = str(
        invitation_id
        or ""
    ).strip()

    record = (
        store[
            "invitations"
        ].get(
            normalized
        )
    )

    if record is None:
        raise InvitationLifecycleError(
            "Invitation not found."
        )

    return record


def create_invitation(
    *,
    target: str,
    requested_role: str,
    requested_apps: List[str],
    now: datetime | None = None,
    ttl_hours: int | None = None,
) -> Dict[str, Any]:

    if (
        invitation_store_status()[
            "configured"
        ]
        is not True
    ):
        return {
            "ok":
                False,

            "status":
                "INVITATION_STORE_NOT_CONFIGURED",

            "message":
                "Invitation store not configured.",

            "invitation":
                None,

            "token":
                None,
        }

    owner = (
        hosted_owner_person_record()
    )

    if owner is None:
        return {
            "ok":
                False,

            "status":
                "OWNER_IDENTITY_NOT_CONFIGURED",

            "message":
                "Hosted owner identity not configured.",

            "invitation":
                None,

            "token":
                None,
        }

    normalized_target = str(
        target
        or ""
    ).strip()

    if not normalized_target:
        raise InvitationLifecycleError(
            "Invitation target is required."
        )

    normalized_role = str(
        requested_role
        or ""
    ).strip().lower()

    if normalized_role not in {
        "member",
        "manager",
    }:
        raise InvitationLifecycleError(
            "Invitation role must be member or manager."
        )

    registered = set(
        app_ids()
    )

    normalized_apps: List[
        str
    ] = []

    for app_id in requested_apps:

        normalized_app = str(
            app_id
            or ""
        ).strip()

        if not normalized_app:
            continue

        if normalized_app not in registered:
            raise InvitationLifecycleError(
                f"Unknown requested app: {normalized_app}"
            )

        if (
            normalized_app
            not in normalized_apps
        ):
            normalized_apps.append(
                normalized_app
            )

    created_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    lifetime_hours = (
        ttl_hours
        if ttl_hours is not None
        else _default_ttl_hours()
    )

    lifetime_hours = max(
        1,
        min(
            int(
                lifetime_hours
            ),
            720,
        ),
    )

    expires_at = (
        created_at
        + timedelta(
            hours=lifetime_hours
        )
    )

    token = secrets.token_urlsafe(
        32
    )

    invitation_id = (
        "inv_"
        + uuid.uuid4().hex
    )

    record = {
        "invitation_id":
            invitation_id,

        "target":
            normalized_target,

        "requested_role":
            normalized_role,

        "requested_apps":
            normalized_apps,

        "granted_apps":
            [],

        "state":
            CREATED,

        "created_by_person_id":
            owner[
                "person_id"
            ],

        "created_at_utc":
            _iso(
                created_at
            ),

        "updated_at_utc":
            _iso(
                created_at
            ),

        "expires_at_utc":
            _iso(
                expires_at
            ),

        "token_hash":
            _token_hash(
                token
            ),

        "identity_binding":
            None,

        "activation_receipt":
            None,

        "events": [
            _event(
                event="INVITATION_CREATED",
                now=created_at,
            ),
        ],
    }

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=created_at,
        )

        store[
            "invitations"
        ][
            invitation_id
        ] = record

        return {
            "ok":
                True,

            "status":
                CREATED,

            "message":
                "Invitation created.",

            "invitation":
                _safe_record(
                    record
                ),

            # Returned ONCE.
            # Never persisted.
            "token":
                token,
        }

    return _with_locked_store(
        operation
    )


def list_invitations(
    *,
    now: datetime | None = None,
) -> List[Dict[str, Any]]:

    if (
        invitation_store_status()[
            "configured"
        ]
        is not True
    ):
        return []

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        records = [
            _safe_record(
                record
            )
            for record
            in store[
                "invitations"
            ].values()
        ]

        records.sort(
            key=lambda record: (
                record[
                    "created_at_utc"
                ],
                record[
                    "invitation_id"
                ],
            ),
            reverse=True,
        )

        return records

    return _with_locked_store(
        operation
    )


def invitation_by_id(
    invitation_id: str,
    *,
    now: datetime | None = None,
) -> Dict[str, Any] | None:

    if (
        invitation_store_status()[
            "configured"
        ]
        is not True
    ):
        return None

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = (
            store[
                "invitations"
            ].get(
                str(
                    invitation_id
                    or ""
                ).strip()
            )
        )

        if record is None:
            return None

        return _safe_record(
            record
        )

    return _with_locked_store(
        operation
    )


def request_invitation_delivery(
    invitation_id: str,
    *,
    now: datetime | None = None,
) -> Dict[str, Any]:

    delivery = (
        invitation_delivery_status()
    )

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = _record_by_id(
            store,
            invitation_id,
        )

        if (
            delivery[
                "configured"
            ]
            is not True
        ):
            return {
                "ok":
                    False,

                "changed":
                    False,

                "status":
                    "INVITATION_DELIVERY_NOT_CONFIGURED",

                "message":
                    "Invitation delivery not configured.",

                "invitation":
                    _safe_record(
                        record
                    ),
            }

        _transition(
            record,
            target_state=DELIVERY_PENDING,
            now=observed_at,
            event_name="DELIVERY_REQUESTED",
            evidence={
                "delivery_mode":
                    delivery[
                        "mode"
                    ],
            },
        )

        return {
            "ok":
                True,

            "changed":
                True,

            "status":
                DELIVERY_PENDING,

            "message":
                "Invitation delivery handoff requested.",

            "invitation":
                _safe_record(
                    record
                ),
        }

    return _with_locked_store(
        operation
    )


def record_invitation_sent(
    invitation_id: str,
    *,
    provider_message_id: str,
    delivery_receipt_id: str,
    now: datetime | None = None,
) -> Dict[str, Any]:

    delivery = (
        invitation_delivery_status()
    )

    if (
        delivery[
            "configured"
        ]
        is not True
    ):
        return {
            "ok":
                False,

            "changed":
                False,

            "status":
                "INVITATION_DELIVERY_NOT_CONFIGURED",

            "message":
                "Invitation delivery not configured.",
        }

    message_id = str(
        provider_message_id
        or ""
    ).strip()

    receipt_id = str(
        delivery_receipt_id
        or ""
    ).strip()

    if not (
        message_id
        and receipt_id
    ):
        raise InvitationLifecycleError(
            "SENT requires provider message and delivery receipt identifiers."
        )

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = _record_by_id(
            store,
            invitation_id,
        )

        _transition(
            record,
            target_state=SENT,
            now=observed_at,
            event_name="DELIVERY_CONFIRMED_SENT",
            evidence={
                "provider_message_id":
                    message_id,

                "delivery_receipt_id":
                    receipt_id,
            },
        )

        return {
            "ok":
                True,

            "changed":
                True,

            "status":
                SENT,

            "invitation":
                _safe_record(
                    record
                ),
        }

    return _with_locked_store(
        operation
    )


def record_invitation_opened(
    invitation_id: str,
    *,
    provider_event_id: str,
    now: datetime | None = None,
) -> Dict[str, Any]:

    if (
        invitation_delivery_status()[
            "configured"
        ]
        is not True
    ):
        return {
            "ok":
                False,

            "changed":
                False,

            "status":
                "INVITATION_DELIVERY_NOT_CONFIGURED",

            "message":
                "Invitation delivery not configured.",
        }

    event_id = str(
        provider_event_id
        or ""
    ).strip()

    if not event_id:
        raise InvitationLifecycleError(
            "OPENED requires a provider event identifier."
        )

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = _record_by_id(
            store,
            invitation_id,
        )

        _transition(
            record,
            target_state=OPENED,
            now=observed_at,
            event_name="INVITATION_OPENED",
            evidence={
                "provider_event_id":
                    event_id,
            },
        )

        return {
            "ok":
                True,

            "changed":
                True,

            "status":
                OPENED,

            "invitation":
                _safe_record(
                    record
                ),
        }

    return _with_locked_store(
        operation
    )


def accept_invitation(
    invitation_id: str,
    *,
    token: str,
    now: datetime | None = None,
) -> Dict[str, Any]:

    presented_token = str(
        token
        or ""
    )

    if not presented_token:
        return {
            "ok":
                False,

            "changed":
                False,

            "status":
                "INVALID_INVITATION_TOKEN",
        }

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = _record_by_id(
            store,
            invitation_id,
        )

        if record[
            "state"
        ] not in {
            SENT,
            OPENED,
        }:
            return {
                "ok":
                    False,

                "changed":
                    False,

                "status":
                    "INVITATION_NOT_ACCEPTABLE_IN_CURRENT_STATE",

                "invitation":
                    _safe_record(
                        record
                    ),
            }

        valid = hmac.compare_digest(
            record[
                "token_hash"
            ],
            _token_hash(
                presented_token
            ),
        )

        if not valid:
            return {
                "ok":
                    False,

                "changed":
                    False,

                "status":
                    "INVALID_INVITATION_TOKEN",

                "invitation":
                    _safe_record(
                        record
                    ),
            }

        _transition(
            record,
            target_state=ACCEPTED,
            now=observed_at,
            event_name="INVITATION_ACCEPTED",
            evidence={
                "token_verified":
                    True,
            },
        )

        return {
            "ok":
                True,

            "changed":
                True,

            "status":
                ACCEPTED,

            "invitation":
                _safe_record(
                    record
                ),
        }

    return _with_locked_store(
        operation
    )


def begin_identity_binding(
    invitation_id: str,
    *,
    person_id: str,
    identity_evidence_id: str,
    now: datetime | None = None,
) -> Dict[str, Any]:

    normalized_person = str(
        person_id
        or ""
    ).strip()

    evidence_id = str(
        identity_evidence_id
        or ""
    ).strip()

    if not (
        normalized_person
        and evidence_id
    ):
        raise InvitationLifecycleError(
            "Identity binding requires person and evidence identifiers."
        )

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = _record_by_id(
            store,
            invitation_id,
        )

        _transition(
            record,
            target_state=IDENTITY_PENDING,
            now=observed_at,
            event_name="IDENTITY_BINDING_REQUESTED",
            evidence={
                "person_id":
                    normalized_person,

                "identity_evidence_id":
                    evidence_id,
            },
        )

        record[
            "identity_binding"
        ] = {
            "person_id":
                normalized_person,

            "identity_evidence_id":
                evidence_id,

            # Pending is not verified.
            "verified":
                False,
        }

        return {
            "ok":
                True,

            "changed":
                True,

            "status":
                IDENTITY_PENDING,

            "invitation":
                _safe_record(
                    record
                ),
        }

    return _with_locked_store(
        operation
    )


def activate_invitation(
    invitation_id: str,
) -> Dict[str, Any]:

    current = invitation_by_id(
        invitation_id
    )

    if current is None:
        raise InvitationLifecycleError(
            "Invitation not found."
        )

    return {
        "ok":
            False,

        "changed":
            False,

        "status":
            "ACCESS_ACTIVATION_NOT_CONFIGURED",

        "message":
            "Access activation authority not configured.",

        "invitation":
            current,
    }


def revoke_invitation(
    invitation_id: str,
    *,
    reason: str,
    now: datetime | None = None,
) -> Dict[str, Any]:

    normalized_reason = str(
        reason
        or ""
    ).strip()

    if not normalized_reason:
        raise InvitationLifecycleError(
            "Revocation reason is required."
        )

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = _record_by_id(
            store,
            invitation_id,
        )

        _transition(
            record,
            target_state=REVOKED,
            now=observed_at,
            event_name="INVITATION_REVOKED",
            reason=normalized_reason,
        )

        return {
            "ok":
                True,

            "changed":
                True,

            "status":
                REVOKED,

            "invitation":
                _safe_record(
                    record
                ),
        }

    return _with_locked_store(
        operation
    )


def record_invitation_failure(
    invitation_id: str,
    *,
    failure_code: str,
    now: datetime | None = None,
) -> Dict[str, Any]:

    normalized_code = str(
        failure_code
        or ""
    ).strip()

    if not normalized_code:
        raise InvitationLifecycleError(
            "Failure code is required."
        )

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):

        _expire_due(
            store,
            now=observed_at,
        )

        record = _record_by_id(
            store,
            invitation_id,
        )

        _transition(
            record,
            target_state=FAILED,
            now=observed_at,
            event_name="INVITATION_FAILED",
            reason=normalized_code,
        )

        return {
            "ok":
                True,

            "changed":
                True,

            "status":
                FAILED,

            "invitation":
                _safe_record(
                    record
                ),
        }

    return _with_locked_store(
        operation
    )


def expire_due_invitations(
    *,
    now: datetime | None = None,
) -> int:

    if (
        invitation_store_status()[
            "configured"
        ]
        is not True
    ):
        return 0

    observed_at = (
        now
        or _utc_now()
    ).astimezone(
        timezone.utc
    )

    def operation(
        store: Dict[str, Any],
    ):
        return _expire_due(
            store,
            now=observed_at,
        )

    return _with_locked_store(
        operation
    )


def invitation_authority_snapshot(
) -> Dict[str, Any]:

    store_status = (
        invitation_store_status()
    )

    delivery = (
        invitation_delivery_status()
    )

    activation = (
        access_activation_status()
    )

    if (
        store_status[
            "configured"
        ]
        is not True
    ):
        return {
            "status":
                "tower_invitation_authority_not_configured",

            "verification_state":
                NOT_CONFIGURED,

            "configured":
                False,

            "invitations":
                [],

            "invitation_count":
                None,

            "pending_invitation_count":
                None,

            "state_counts":
                {},

            "delivery":
                delivery,

            "access_activation":
                activation,

            "message":
                "Invitation lifecycle not configured.",

            "store_path_exposed":
                False,
        }

    invitations = (
        list_invitations()
    )

    state_counts = {
        state:
            sum(
                1
                for invitation
                in invitations
                if invitation[
                    "state"
                ]
                == state
            )
        for state in sorted(
            ALL_STATES
        )
    }

    pending_count = sum(
        state_counts[
            state
        ]
        for state in PENDING_STATES
    )

    return {
        "status":
            "tower_invitation_authority_verified",

        "verification_state":
            VERIFIED,

        "configured":
            True,

        "invitations":
            invitations,

        "invitation_count":
            len(
                invitations
            ),

        "pending_invitation_count":
            pending_count,

        "state_counts":
            state_counts,

        "delivery":
            delivery,

        "access_activation":
            activation,

        "message":
            delivery[
                "message"
            ],

        "store_path_exposed":
            False,
    }

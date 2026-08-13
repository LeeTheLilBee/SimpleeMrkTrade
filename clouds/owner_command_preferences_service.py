"""
GP023 — Owner Settings / Command Preferences service.
"""

from __future__ import annotations

try:
    from .owner_command_detail_drawers_service import (
        get_clouds_gp022_status_payload,
    )

    from .owner_command_preferences import (
        AttentionThreshold,
        EvidenceDisclosurePreference,
        OwnerCommandPreferences,
        OwnerCommandPreferencesSurface,
        QuietCardBehavior,
        SoulaanaVerbosity,
    )

except ImportError:
    from owner_command_detail_drawers_service import (
        get_clouds_gp022_status_payload,
    )

    from owner_command_preferences import (
        AttentionThreshold,
        EvidenceDisclosurePreference,
        OwnerCommandPreferences,
        OwnerCommandPreferencesSurface,
        QuietCardBehavior,
        SoulaanaVerbosity,
    )


DEFAULT_OWNER_ID = "owner-primary"


DEFAULT_PREFERENCES = OwnerCommandPreferences(
    owner_id=DEFAULT_OWNER_ID,

    soulaana_verbosity=(
        SoulaanaVerbosity
        .EXPLAIN_EVERYTHING.value
    ),

    evidence_disclosure=(
        EvidenceDisclosurePreference
        .ON_REQUEST.value
    ),

    quiet_card_behavior=(
        QuietCardBehavior
        .COLLAPSED.value
    ),

    attention_threshold=(
        AttentionThreshold
        .REVIEW_AND_ACTION.value
    ),

    collapse_quiet_section=True,
    collapse_ecosystem_section=True,

    show_status_chips=True,
    show_owner_next_step=True,
    show_why_it_matters=True,

    preserve_tower_handoffs=True,
    preserve_step_up_requirements=True,
    preserve_downstream_authority=True,

    persistent_projection=True,
    downstream_authority_changed=False,
    execution_performed=False,
)


def get_owner_command_preferences(
    owner_id=DEFAULT_OWNER_ID,
):
    if owner_id != DEFAULT_OWNER_ID:
        raise KeyError(
            f"Unknown owner preference profile: {owner_id}"
        )

    return DEFAULT_PREFERENCES


def get_owner_command_preferences_payload(
    owner_id=DEFAULT_OWNER_ID,
):
    return (
        get_owner_command_preferences(
            owner_id
        ).to_dict()
    )


def get_owner_command_preferences_surface():
    prefs = get_owner_command_preferences()

    return OwnerCommandPreferencesSurface(
        title=(
            "Owner Settings / Command Preferences"
        ),
        preferences=prefs,
        presentation_only=True,
        tower_boundary_preserved=(
            prefs.preserve_tower_handoffs
        ),
        downstream_authority_preserved=(
            prefs.preserve_downstream_authority
        ),
        boundary_notice=(
            "Owner preferences change presentation only. "
            "They cannot bypass Tower, remove step-up, "
            "grant downstream authority, or execute actions."
        ),
    )


def get_owner_command_preferences_surface_payload():
    return (
        get_owner_command_preferences_surface()
        .to_dict()
    )


def get_clouds_gp023_status_payload():
    gp022 = get_clouds_gp022_status_payload()

    surface = (
        get_owner_command_preferences_surface()
    )

    prefs = surface.preferences

    safe = (
        gp022["status"] == "ready"
        and gp022["safe_to_continue"] is True
        and prefs.owner_id == DEFAULT_OWNER_ID
        and prefs.soulaana_verbosity
        == "explain_everything"
        and prefs.evidence_disclosure
        == "on_request"
        and prefs.quiet_card_behavior
        == "collapsed"
        and prefs.attention_threshold
        == "review_and_action"
        and prefs.preserve_tower_handoffs
        is True
        and prefs.preserve_step_up_requirements
        is True
        and prefs.preserve_downstream_authority
        is True
        and prefs.downstream_authority_changed
        is False
        and prefs.execution_performed
        is False
        and surface.presentation_only
        is True
        and surface.tower_boundary_preserved
        is True
        and surface.downstream_authority_preserved
        is True
    )

    return {
        "pack": "GP023",
        "section": (
            "OWNER SETTINGS "
            "/ COMMAND PREFERENCES SURFACE"
        ),
        "status": (
            "ready"
            if safe
            else "blocked"
        ),
        "safe_to_continue": safe,
        "owner_profile_count": 1,
        "soulaana_verbosity": (
            prefs.soulaana_verbosity
        ),
        "evidence_disclosure": (
            prefs.evidence_disclosure
        ),
        "quiet_card_behavior": (
            prefs.quiet_card_behavior
        ),
        "attention_threshold": (
            prefs.attention_threshold
        ),
        "presentation_only": True,
        "tower_boundary_preserved": True,
        "step_up_requirements_preserved": True,
        "downstream_authority_preserved": True,
        "downstream_authority_changed": False,
        "execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP024 — BETA READINESS "
            "/ TOWER-CLOUDS OWNER WALKTHROUGH CLOSEOUT"
        ),
    }

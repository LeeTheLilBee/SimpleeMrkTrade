
"""Tower product-surface truth-debt audit / TWR125.

This scanner is intentionally aimed at operating/product source surfaces,
not tests or evidence.

TWR125 records existing debt. TWR126-TWR130 will retire the user-facing
practice/false surfaces.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TowerTruthAuditRule:
    rule_id: str
    category: str
    pattern: str
    severity: str
    rationale: str


AUDIT_RULES = (
    TowerTruthAuditRule(
        rule_id="practice_walkthrough",
        category="PRACTICE_SURFACE",
        pattern=r"\bwalkthrough\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Walkthrough/rehearsal language must not be "
            "a normal Tower operating destination."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="practice_preview",
        category="PRACTICE_SURFACE",
        pattern=r"\bpreview\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Preview controls cannot masquerade as "
            "operational Tower actions."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="practice_simulate",
        category="PRACTICE_SURFACE",
        pattern=r"\bsimulat(?:e|ed|ion|or)\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Simulation belongs in tests/proof, not normal "
            "Tower operations."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="practice_rehearsal",
        category="PRACTICE_SURFACE",
        pattern=r"\brehearsal\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Rehearsal state cannot be presented as operation."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="practice_dry_run",
        category="PRACTICE_SURFACE",
        pattern=r"\bdry[-_ ]?run\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Dry-run language requires separation from "
            "real product controls."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="mock_language",
        category="TEST_OR_MOCK_STATE",
        pattern=r"\bmock\b",
        severity="REVIEW_PRODUCT_SOURCE",
        rationale=(
            "Mock state must never feed primary Tower truth."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="placeholder_language",
        category="PLACEHOLDER_STATE",
        pattern=r"\bplaceholder\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Placeholder state must not appear as real "
            "people/access/product state."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="draft_language",
        category="DRAFT_STATE",
        pattern=r"\bdraft(?:s|ed|_not_sent)?\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Draft controls must not look like real completed "
            "Tower operations."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="staged_only_identity",
        category="PLACEHOLDER_IDENTITY",
        pattern=r"\bstaged_only\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Staged-only identities are not real accounts."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="future_identity",
        category="PLACEHOLDER_IDENTITY",
        pattern=r"\bfuture[-_ ](?:manager|family|seat|invite|team)",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Future/example identities belong in test fixtures, "
            "not hosted owner people state."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="ready_status_claim",
        category="PLAUSIBLE_STATUS",
        pattern=r"\btower_[a-z0-9_]*ready\b",
        severity="REVIEW_AUTHORITY",
        rationale=(
            "Ready must be backed by an explicit authoritative "
            "provider, not a convenient default label."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="rooms_ready_claim",
        category="PLAUSIBLE_STATUS",
        pattern=r"\brooms are ready\b",
        severity="REVIEW_AUTHORITY",
        rationale=(
            "Product readiness claims require authoritative "
            "runtime/access proof."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="account_creation_false_gap",
        category="CONTROL_LOOKS_REAL_BUT_IS_NOT",
        pattern=r"\breal_account_creation\s*=\s*False\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "A control surface must not look operational when "
            "account creation is explicitly non-operational."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="invites_false_gap",
        category="CONTROL_LOOKS_REAL_BUT_IS_NOT",
        pattern=r"\breal_invites_sent\s*=\s*False\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Invitation UX must connect to a real invitation "
            "lifecycle or state unavailable."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="access_grants_false_gap",
        category="CONTROL_LOOKS_REAL_BUT_IS_NOT",
        pattern=r"\breal_access_granted\s*=\s*False\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Access-management UX must modify real authority "
            "or explicitly remain unavailable."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="future_app_registry",
        category="FUTURE_PRODUCT_REGISTRATION",
        pattern=r"\bregistered_future_room\b",
        severity="KEEP_REGISTRY_HIDE_PRODUCT",
        rationale=(
            "Future app registration is legitimate configuration "
            "but must not imply product availability."
        ),
    ),

    TowerTruthAuditRule(
        rule_id="walkthrough_route",
        category="PRACTICE_ROUTE",
        pattern=r"/walkthrough\b",
        severity="RETIRE_FROM_PRODUCT",
        rationale=(
            "Normal Tower navigation must not route humans into "
            "walkthrough/proof experiences."
        ),
    ),
)


DEFAULT_PRODUCT_SURFACES = (
    "tower/app_registry.py",
    "tower/owner_people_registry.py",
    "tower/owner_dashboard_service.py",
    "tower/access_home_owner_launches.py",
    "tower/owner_dashboard_web.py",
    "tower/hosted_owner_release_walkthrough_web.py",
    "tower/tower_human_login_ob_launch.py",
)


def audit_source_text(
    source: str,
    *,
    relative_path: str,
) -> list[dict]:

    findings = []

    for line_number, line in enumerate(
        str(source or "").splitlines(),
        start=1,
    ):

        for rule in AUDIT_RULES:

            if re.search(
                rule.pattern,
                line,
                flags=re.IGNORECASE,
            ):

                findings.append({
                    "relative_path": relative_path,
                    "line_number": line_number,
                    "rule_id": rule.rule_id,
                    "category": rule.category,
                    "severity": rule.severity,
                    "matched_line": line.strip()[:240],
                    "rationale": rule.rationale,
                })

    return findings


def audit_product_surfaces(
    repo: Path | str,
    *,
    relative_paths: Iterable[str] = DEFAULT_PRODUCT_SURFACES,
) -> dict:

    root = Path(repo)

    findings = []
    scanned = []

    for relative in relative_paths:

        normalized = str(relative).strip()

        if not normalized:
            continue

        if normalized.startswith("tests/"):
            raise ValueError(
                "Product truth audit must not treat tests "
                "as primary product surfaces."
            )

        if normalized.startswith("ob_evidence/"):
            raise ValueError(
                "Product truth audit must not treat evidence "
                "as primary product surfaces."
            )

        path = root / normalized

        if not path.is_file():
            raise FileNotFoundError(
                f"Missing Tower product surface: {normalized}"
            )

        source = path.read_text(
            encoding="utf-8"
        )

        scanned.append(
            normalized
        )

        findings.extend(
            audit_source_text(
                source,
                relative_path=normalized,
            )
        )

    categories = {}
    severities = {}
    files = {}

    for finding in findings:

        category = finding["category"]
        severity = finding["severity"]
        relative = finding["relative_path"]

        categories[category] = (
            categories.get(category, 0) + 1
        )

        severities[severity] = (
            severities.get(severity, 0) + 1
        )

        files[relative] = (
            files.get(relative, 0) + 1
        )

    return {
        "status": "tower_truth_debt_audit_complete",
        "scanned_product_surfaces": scanned,
        "scanned_surface_count": len(scanned),
        "finding_count": len(findings),
        "category_counts": categories,
        "severity_counts": severities,
        "file_counts": files,
        "findings": findings,
        "tests_scanned_as_product": False,
        "evidence_scanned_as_product": False,
    }


def findings_for_rule(
    report: dict,
    rule_id: str,
) -> list[dict]:

    return [
        finding
        for finding in report.get(
            "findings",
            [],
        )
        if finding.get("rule_id")
        == rule_id
    ]


def findings_for_file(
    report: dict,
    relative_path: str,
) -> list[dict]:

    return [
        finding
        for finding in report.get(
            "findings",
            [],
        )
        if finding.get("relative_path")
        == relative_path
    ]

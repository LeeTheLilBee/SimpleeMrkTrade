"""TWR-OBML031–035: secret-free owner→OB one-time ledger storage assessment.

An absolute path and a configured signing key do NOT prove durable storage,
cross-deploy replay protection, provider backup, or recoverability. This
source-only auditor has no HTTP route, file mutation, token or grant function.
It never presents synthetic filesystem evidence as a hosted release approval.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Callable

SCHEMA_VERSION = "tower.ob.owner_replay_storage.audit.v1"
FORBIDDEN_BASES = (Path("/tmp"), Path("/var/tmp"), Path("/dev/shm"))


def _private_directory(path: Path) -> bool:
    try:
        return (path.is_dir() and not path.is_symlink()
                and stat.S_IMODE(path.stat().st_mode) & 0o077 == 0)
    except (OSError, ValueError):
        return False


def inspect_owner_ob_replay_storage(
    ledger_path: str | None,
    mount_root: str | None,
    *,
    mount_probe: Callable[[str], bool] | None = None,
) -> dict[str, object]:
    """Check source-level path structure; never certify a provider or an owner.

    mount_probe is injectable for synthetic tests. A true result is only an
    observed mount assertion, not evidence of backup/restore or nonce survival.
    """
    reasons: list[str] = []
    structurally_valid = False
    mount_observed = False
    ledger = None
    mount = None
    if not isinstance(ledger_path, str) or not ledger_path.strip():
        reasons.append("LEDGER_PATH_NOT_CONFIGURED")
    elif not isinstance(mount_root, str) or not mount_root.strip():
        reasons.append("APPROVED_DURABLE_MOUNT_NOT_PROVIDED")
    else:
        ledger = Path(ledger_path)
        mount = Path(mount_root)
        if (
            ledger_path != ledger_path.strip() or mount_root != mount_root.strip()
            or not ledger.is_absolute() or not mount.is_absolute()
            or mount == Path("/") or ".." in ledger.parts or ".." in mount.parts
        ):
            reasons.append("ABSOLUTE_UNAMBIGUOUS_PRIVATE_PATHS_REQUIRED")
        elif any(ledger == bad or ledger.is_relative_to(bad)
                 or mount == bad or mount.is_relative_to(bad)
                 for bad in FORBIDDEN_BASES):
            reasons.append("EPHEMERAL_RUNTIME_PATH_REJECTED")
        elif ledger == mount or ledger.suffix not in (".sqlite", ".sqlite3", ".db"):
            reasons.append("DEDICATED_SQLITE_LEDGER_FILE_REQUIRED")
        else:
            try:
                if not mount.exists() or not ledger.parent.exists():
                    reasons.append("PRIVATE_DIRECTORIES_NOT_PROVISIONED")
                elif any(parent.is_symlink() for parent in
                         (ledger.parent, *ledger.parents, mount, *mount.parents)
                         if parent != Path("/")):
                    reasons.append("SYMLINKED_STORAGE_PATH_REJECTED")
                elif not ledger.parent.resolve().is_relative_to(mount.resolve()):
                    reasons.append("LEDGER_OUTSIDE_APPROVED_MOUNT")
                elif not (_private_directory(mount)
                          and _private_directory(ledger.parent)):
                    reasons.append("PRIVATE_DIRECTORY_PERMISSIONS_REQUIRED")
                elif ledger.exists() and (
                    not ledger.is_file() or ledger.is_symlink()
                    or stat.S_IMODE(ledger.stat().st_mode) & 0o077
                ):
                    reasons.append("EXISTING_LEDGER_NOT_PRIVATE")
                else:
                    structurally_valid = True
                    check = os.path.ismount if mount_probe is None else mount_probe
                    try:
                        mount_observed = check(str(mount)) is True
                    except (OSError, ValueError):
                        mount_observed = False
                    if not mount_observed:
                        reasons.append("REAL_MOUNT_NOT_OBSERVED")
            except (OSError, ValueError):
                reasons.append("STORAGE_INSPECTION_UNAVAILABLE")
    # The auditor cannot observe a provider guarantee or a real process/deploy
    # restart. Configuration and a test-supplied predicate cannot close them.
    reasons.extend((
        "PROVIDER_DURABILITY_AND_BACKUP_NOT_CERTIFIED",
        "DESTRUCTIVE_RESTORE_NOT_CERTIFIED",
        "CROSS_DEPLOY_REPLAY_DENIAL_NOT_CERTIFIED",
    ))
    return {
        "schema_version": SCHEMA_VERSION,
        "state": "SOURCE_PATH_REVIEW_ONLY",
        "reason_codes": reasons,
        "path_structure_valid": structurally_valid,
        "mount_observed": mount_observed,
        "provider_durability_verified": False,
        "backup_restore_verified": False,
        "cross_deploy_replay_verified": False,
        "owner_walkthrough_verified": False,
        "manual_live_authorized": False,
        "source_checks_are_release_authority": False,
        "private_paths_exposed": False,
        "secrets_exposed": False,
        "may_issue_manual_live_grant": False,
    }

# SIMPLEE SOVEREIGN CLOUD — SC031 OWNER-SAFE RESTORE METRICS

Date: September 28, 2026. Based on merged SC030 `vault-dev` commit `8b25e972f14b0b866b4dec8fa0b03224cfe8a7a9`. Source-only, **production NO_GO**.

## Purpose

SC029 and SC030 made bound restore requests auditable and gave them fail-closed lifecycle rules, but the owner source snapshot did not summarize restore activity. SC031 adds redacted aggregate restore metrics derived from the **same verified SQLite read snapshot** already used for storage health and backup coverage.

The operational journal reports:
- total bound restore request count;
- completed `RESTORE_BOUND_VERIFIED` request count;
- restore integrity-HOLD request count;
- pending restore request count;
- pending restore requests whose only recorded blocker is backup-provider reachability;
- pending non-outage restore count;
- restore integrity incident-event count and restore-provider-outage event count.

These are computed only after the complete storage/backup/read/restore reservation and event chain verifies. The counts are keyed internally by opaque request tags but no request tag, backup ref, object ref, namespace digest, ciphertext SHA, key reference, raw entity name, document body or provider exception text appears in the owner-safe result.

## Classification rules

A bound restore request is:
- **completed** when one verified `RESTORE_BOUND_VERIFIED` event exists;
- **integrity held** when its request tag has `BACKUP_INTEGRITY_FAILURE`;
- **pending** when it is reserved but neither completed nor integrity held;
- **retryable after outage** when a pending request has `BACKUP_VERIFY_BACKEND_ERROR`;
- **pending non-outage** when it is pending without that provider-outage marker.

Restore-integrity events are removed from the generic “other incidents” owner card so one failure is not presented twice. Provider outage events remain in the broader backend-error count because they are provider reachability incidents, while the restore retryable count identifies which pending logical restore requests are affected.

## Owner surfaces

`owner_safe_source_snapshot()`, its Markdown renderer, and the SC021 owner evidence desk now include the restore lifecycle counts. An integrity-HOLD card instructs the owner/operator to investigate/repair evidence and require a **fresh Tower/Vault restore authorization and new request ID**, consistent with SC030.

Every recovery-related truth flag remains false:
- no physical recovery certification;
- no Vault-original authentication claim from Cloud metrics;
- no independent failure-domain certification;
- no hosted alert certification;
- no production authorization.

A locally completed encrypted-copy verification is not a real site-loss recovery drill.

## Acceptance

Synthetic tests cover empty state, successful restore, provider outage then successful same-request retry, corruption/integrity hold, failed restore followed by fresh-request success, owner evidence desk redaction, and Markdown wording. All counts are source-local and generated through the existing consolidated Vault/Cloud CI.

No provider is contacted, no paid resource or credential is created, and no real Tower/Vault identity, external backup site, user document, RPO/RTO certification or release status is introduced.

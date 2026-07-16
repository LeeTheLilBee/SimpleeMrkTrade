# Tower–Observatory Managed Staging Provider Inputs and Owner Authorization

## Closed layer

`MANAGED_STAGING_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION`

## Closed through

Step `050`

## What this layer added

- Non-secret provider-input worksheet and schema validation
- Provider capability attestations
- Account/team, region, and billing fingerprint bindings
- Staging secret-custody rules
- Tower owner authorization challenge contract
- Tower step-up receipt binding requirement
- Frozen provider-authorization packet
- Inert no-call provisioning-readiness plan
- Offline operator utility: `tools/tower_ob_provider_authorization.py`

## Verification

- Provider authorization tests: 20 passed
- Managed staging runtime regressions: 14 passed
- Simplee DevKit regressions: 4 passed
- Existing Tower–OB regressions: 85 passed
- Total: 123 passed

## Decision

`NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED`

No managed-host provider, provider account/team, deployment region, or valid
Tower owner approval was recorded by this build. The layer therefore remains
fail-closed.

## Operator workflow

Create blank worksheets outside Git:

```bash
python tools/tower_ob_provider_authorization.py \
  --write-worksheets /content/tower_ob_provider_authorization
```

After completing and validating the provider-input worksheet, generate a
challenge-bound owner worksheet:

```bash
python tools/tower_ob_provider_authorization.py \
  --provider-inputs /content/tower_ob_provider_authorization/tower_ob_managed_staging_provider_inputs.json \
  --write-owner-decision /content/tower_ob_provider_authorization/tower_ob_managed_staging_owner_decision_bound.json
```

Do not place credentials, passwords, API keys, tokens, session cookies, private
keys, secret values, or full connection strings in either worksheet.

## Safety

No provider API, provider CLI, shell deployment command, resource creation,
secret creation/readback, deployment, or official walkthrough occurred.

Production Manual Live, broker submission, real capital movement, direct Vault
upload, and Live Auto remain disabled.

## Next boundary

`managed_staging_no_call_provider_provisioning_review`

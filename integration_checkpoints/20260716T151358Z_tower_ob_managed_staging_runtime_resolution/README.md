# Tower–Observatory Managed Staging Runtime Resolution

## Closed layer

`MANAGED_STAGING_PROVIDER_ACCESS_AND_OBSERVATORY_RUNTIME_RESOLUTION`

## Closed through

Step `040`

## Runtime resolution

- Source application: `web.app:app`
- Managed WSGI entrypoint: `web.managed_staging:app`
- Start command: `gunicorn --bind 0.0.0.0:$PORT web.managed_staging:app`
- Initial topology: one Tower-fronted managed Python web service
- Separate Observatory process required now: false
- Direct anonymous Observatory ingress: prohibited

## Verification

- Managed runtime contract tests: 14 passed
- Simplee DevKit regressions: 4 passed
- Existing Tower–OB regressions: 85 passed
- Total: 103 passed

## Decision

`NO_GO_HOLD_PROVIDER_SELECTION_ACCOUNT_REGION_AND_OWNER_APPROVAL_REQUIRED`

## Remaining blockers

```json
[
  {
    "requirement": "managed_host_provider",
    "status": "operator_input_required"
  },
  {
    "requirement": "managed_host_account_or_team",
    "status": "operator_input_required"
  },
  {
    "requirement": "deployment_region",
    "status": "operator_input_required"
  },
  {
    "requirement": "provider_owner_approval",
    "status": "owner_approval_required"
  }
]
```

## Safety

No provider API or shell deployment command was invoked.

No managed resources or secrets were created.

No deployment or official walkthrough occurred.

Production Manual Live, broker submission, real capital movement,
direct Vault upload, and Live Auto remain disabled.

## Next boundary

`managed_staging_provider_inputs_and_owner_authorization`

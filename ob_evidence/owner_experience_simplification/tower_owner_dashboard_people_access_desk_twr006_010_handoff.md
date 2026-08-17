# Tower Owner Dashboard + People Access Desk / TWR006–TWR010

- Base main: `77d9509cdc9519576951faab4cba4e31aa1de7bb`
- Branch: `tower-owner-dashboard-people-access-desk-twr006-010`
- New Tower routes:
  - `/tower/owner-dashboard`
  - `/tower/owner-dashboard.json`
- New modules:
  - `tower/owner_people_registry.py`
  - `tower/owner_dashboard_service.py`
  - `tower/owner_dashboard_web.py`

## What this layer does

This layer creates the first Tower Owner Dashboard / People Access Desk.

It gives Solice an owner-only place to see:

- People roster
- Future/staged seats
- Invite drafts
- Pending access requests
- App access visibility
- Owner review queue
- Dangerous access locks

## Safety boundaries

- Does not create real user accounts.
- Does not send real invite emails.
- Does not grant real app access.
- Does not open Teller.
- Does not open Vault.
- Does not open Clouds.
- Does not open Grounds.
- Does not redesign OB pages.
- Does not enable trading, broker execution, capital action, or Live Auto.

## Locked state

- Real account creation: false
- Real invite sending: false
- Real access grants: false
- Live Auto: locked
- Broker execution: false
- Capital action: false

This builds the owner desk before wiring real identity/invite/permission mutations.

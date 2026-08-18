# Tower Add Person Draft + Change Queue / TWR026–TWR030

- Base main: `9e33f5c6ace9a73427b1353159f44af888ca9b2f`
- Built from: `tower-dev`
- Branch: `tower-add-person-draft-change-queue-twr026-030`

## What this layer adds

- Add Person Draft packet builder
- Draft queue surface
- Change queue surface
- Small owner controls on `/tower/owner-dashboard`
- Owner-review-required safety language

## New routes

- `/tower/owner-dashboard/person-drafts.json`
- `/tower/owner-dashboard/change-queue.json`
- `/tower/owner-dashboard/person-draft`
- `/tower/owner-dashboard/change-queue`

## Safety

- No real accounts are created.
- No real invites are sent.
- No real access is granted.
- No real permissions are changed.
- Live Auto remains locked.
- Broker execution remains false.
- Capital action remains false.

# Observatory internal gRPC contract — 2026-10-01

## Decision

The Observatory keeps one `ObservatoryEventHub` as its internal nervous system.
The older feature-specific MarketStream/Catalyst hubs stay retired.

The first gRPC step is an explicit protobuf contract, not a second event bus and
not a fake loopback service. Today the relevant hosted OB components still share
one protected Python process. Starting another network server inside that same
process would add dependencies and failure modes without creating a useful
service boundary.

The stable future wire contract is:

`proto/observatory_event_v1.proto`

Package:

`simplee.observatory.v1`

Service:

`ObservatoryEventService`

RPCs:

- `StreamEvents`: server-streamed Observatory invalidation envelopes.
- `RecordLifecycle`: consumer receipt proving that a named internal stage
  actually handled the event.

When Scanner, Simulation, Soulaana, or another OB component becomes a separate
service/process, generated protobuf stubs can implement this contract without
changing the meaning of the existing EventHub events.

## Lifecycle proof

Each new EventHub event now gets a bounded content-free lifecycle trace:

1. `RECEIVED`
2. `VALIDATED`
3. `NORMALIZED`
4. `PUBLISHED`
5. `SCANNER_CONSUMED`
6. `SIMULATION_CONSUMED`
7. `SOULAANA_CONSUMED`
8. `SOULAANA_INTERPRETED`

A stage is false until code explicitly records it. The system must not mark
Soulaana interpreted merely because a provider connection, REST probe, WebSocket
or event publication succeeded.

Alpaca IEX native WebSocket intake now records the first four stages because the
server actually receives, validates and normalizes the provider event before
publishing the protected snapshot invalidation.

Scanner, Simulation and Soulaana receipts remain false until those consumers
actually handle the event. This makes the trace useful for the owner's key
question: "did Soulaana actually eat and interpret this?"

## Event content boundary

The gRPC/event envelope is the bell, not the book.

It carries only:

- schema and event ID
- event family/channel
- epoch/cursor
- source identifier
- optional symbol
- exact protected snapshot path
- explicit negative authority flags

It does not carry provider payloads, credentials, raw bid/ask, option chains,
positions, orders, capital instructions, broker execution permission, candidate
admission or trading-mode permission.

The consumer re-reads the exact protected authoritative snapshot through the
existing Tower boundary.

## Runtime status

`engine/market_intake/observatory_grpc_contract.py` validates the future gRPC
field projection and lifecycle receipt shape.

Current truthful state:

- protobuf contract installed: yes
- lifecycle ledger installed: yes
- Alpaca producer lifecycle proof installed: yes
- network gRPC server started: no
- loopback gRPC server started: no
- new paid Render service required: no
- browser switched to gRPC: no
- existing `/ob/events/stream` WebSocket replaced: no
- broker/capital authority added: no

## Activation rule

Do not start a network gRPC runtime merely to communicate between objects in the
same process.

Start the actual gRPC server/client transport when an internal consumer is moved
behind a real process/service boundary. At that point:

1. generate stubs from the checked-in proto,
2. use authenticated internal transport appropriate to the deployment,
3. keep Tower as the user-facing authorization boundary,
4. preserve the protected-snapshot truth rule,
5. add restart/replay and shared-state tests before multiple workers/replicas,
6. require lifecycle receipts from the real Scanner/Simulation/Soulaana
   consumers rather than inferring consumption.

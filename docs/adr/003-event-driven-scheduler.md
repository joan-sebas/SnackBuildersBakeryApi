# ADR-003: Event-Driven Scheduler

## Status

Accepted.

## Context

The kitchen scheduler is the most complex component of the system. It must:

- Detect when a baking slot becomes available
- Select the next item to bake based on dynamic priority (with aging)
- Assign items to slots and track their bake times
- Recalculate estimated ready times when state changes
- Handle VIP arrivals that disrupt the queue
- Operate safely under concurrent access

A naive design might collapse all of this into a single class with periodic polling. This would mix concerns and make testing difficult.

## Decision

The scheduler is built as **four cooperating components** communicating through an in-process event bus:

```
[BakeTimer]   subscribes to: ItemPlacedInSlot
              emits:         BakeTimerCompleted

[SlotMonitor] subscribes to: BakeTimerCompleted
              emits:         SlotBecameAvailable, ItemFinishedBaking,
                             OrderReady (when the last item of an order completes)

[Scheduler]   subscribes to: SlotBecameAvailable, OrderPaid, VipOrderArrived
              calls:         PlaceItemInSlot use case

[PlaceItemInSlot use case]
              emits:         ItemPlacedInSlot
                             → cycle repeats
```

Each component has a single responsibility. The flow is reactive, with no polling.

Concurrency is handled by a **single `asyncio.Lock`** in the `KitchenScheduler`. All state mutations occur within `async with self._lock:`.

For testing, the scheduler exposes `await scheduler.process_pending_timers()`. Combined with `FakeClock`, this allows deterministic verification of time-based behavior without `sleep`.

The **database is the source of truth**. The in-memory `heapq` priority queue is an optimization for fast next-item selection. On application startup, the scheduler rehydrates from the database.

## Alternatives Considered

### Polling with `scheduler.tick()`

A periodic tick method that scans for completed bakes. Rejected because it wastes resources in production and mixes the responsibilities of "measuring time" and "deciding next assignment" into one class. The event-driven approach achieves the same testability with cleaner separation.

### Fine-Grained Locking (Per Slot, Per Order)

Rejected because critical sections are short and the risk of deadlocks outweighs the marginal performance gain. A single lock is simpler and easier to reason about. Profiling would justify a refactor if a real bottleneck appears.

### Background Worker Process

Rejected because in-process `asyncio` is sufficient for a single-node deployment and avoids cross-process coordination overhead.

## Consequences

### Positive

- Each component has a single, clear responsibility and can be tested in isolation
- Every state transition is an observable event, supporting tracing, structured logging, and SSE streams to clients
- The scheduler logic is independent of time measurement, enabling deterministic tests with `FakeClock`
- The single lock eliminates deadlock risk completely
- New event subscribers (such as analytics or notifications) can be added without modifying existing code

### Trade-offs

- The event-driven flow has more moving parts than a single class would have, requiring careful documentation
- A subtle bug in event subscription would manifest as a missed transition, so test coverage of the event flow is essential
- The single lock theoretically limits throughput under extreme contention. For the scope of this system (two ovens, six slots), this is not a concern.

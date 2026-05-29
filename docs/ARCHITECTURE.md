# Architecture

This document describes the architectural design of the Snack Builders Bakery API. It is intended for developers reviewing the codebase and for future contributors.

---

## Architectural Style

The system is a **modular monolith** built with **Clean Architecture**. A single process hosts cohesive modules that are loosely coupled internally, making future extraction into separate services feasible without rework.

This style was chosen because:

- The challenge describes a single physical kitchen, making distributed systems over-engineering
- Strong domain boundaries make the code testable, maintainable, and clear to reviewers
- Future scaling (multi-location, dedicated services) remains an option without violating the current design

See [ADR-002](adr/002-clean-architecture-modular-monolith.md) for the full rationale.

---

## Layered Structure

The system is organized in four concentric layers. Dependencies always point inward.

```
┌─────────────────────────────────────────────────────┐
│  INTERFACE / API LAYER                              │
│  FastAPI routers, request/response DTOs (Pydantic), │
│  SSE endpoints, middleware                          │
├─────────────────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER                               │
│  SQLAlchemy repositories, payment mock, real clock, │
│  event bus, structured logging                      │
├─────────────────────────────────────────────────────┤
│  APPLICATION LAYER                                  │
│  Use cases that orchestrate the domain              │
├─────────────────────────────────────────────────────┤
│  DOMAIN LAYER                                       │
│  Entities, value objects, scheduler, ports          │
│  No external dependencies                           │
└─────────────────────────────────────────────────────┘
```

For a Mermaid diagram, see [diagrams/architecture.md](diagrams/architecture.md).

### Domain Layer

Contains the core business logic with no external dependencies. Pure Python.

- **Entities:** `Order`, `Item`, `MenuItem`, `Customer`, `Oven`, `Slot`
- **Value Objects:** `Money`, `Priority`, `BakeTime`, `OrderStatus`, `ItemStatus`, `CustomerType`
- **Domain Services:** `KitchenScheduler`, `PriorityQueue`, `AgingCalculator`, `BakeTimeCalculator`
- **Ports:** `Clock`, `OrderRepository`, `MenuRepository`, `CustomerRepository`, `PaymentProcessor`, `EventPublisher`
- **Events:** `OrderPlaced`, `OrderPaid`, `ItemPlacedInSlot`, `BakeTimerCompleted`, `SlotBecameAvailable`, `ItemFinishedBaking`, `VipOrderArrived`, `OrderReady`

### Application Layer

Use cases that orchestrate the domain to fulfill specific user intents. Each use case is a focused, testable command:

- `PlaceOrderUseCase`
- `ProcessPaymentUseCase`
- `GetOrderStatusUseCase`
- `GetKitchenStateUseCase`
- `MenuManagementUseCases`

### Infrastructure Layer

Concrete implementations of the ports defined in the domain:

- `SqlAlchemyOrderRepository`, `SqlAlchemyMenuRepository`, `SqlAlchemyCustomerRepository`
- `RealClock` and `FakeClock` implementations of the `Clock` port
- `MockPaymentProcessor` implementing the Strategy Pattern for cash and card
- `InMemoryEventBus` with `BakeTimer`, `SlotMonitor`, `SSEPublisher` subscribers
- `structlog` configuration for JSON-structured logs

### Interface Layer

FastAPI application exposing the HTTP API:

- REST routers under `/api/v1/`
- SSE streams under `/api/v1/streams/`
- Pydantic schemas for request and response DTOs
- Middleware for logging, error handling, and request tracking

---

## Event-Driven Scheduler

The kitchen scheduler operates through four cooperating components communicating via the event bus.

For a sequence diagram, see [diagrams/scheduler-flow.md](diagrams/scheduler-flow.md).

```
[BakeTimer]          subscribes to: ItemPlacedInSlot
                     emits:         BakeTimerCompleted

[SlotMonitor]        subscribes to: BakeTimerCompleted
                     emits:         SlotBecameAvailable, ItemFinishedBaking,
                                    (and OrderReady when the last item of an order completes)

[KitchenScheduler]   subscribes to: SlotBecameAvailable, OrderPaid, VipOrderArrived
                     calls:         PlaceItemInSlot use case

[PlaceItemInSlot]    emits:         ItemPlacedInSlot
                                    → cycle repeats
```

This design separates responsibilities cleanly:

- The `BakeTimer` only measures time
- The `SlotMonitor` only detects completions and releases slots
- The `Scheduler` only decides what to bake next
- The use case only performs the assignment

Each transition is an observable event, supporting tracing, logging, and real-time streaming to clients via SSE.

For details, see [ADR-003](adr/003-event-driven-scheduler.md).

---

## Concurrency Strategy

A single `asyncio.Lock` in the `KitchenScheduler` protects all state mutations:

```python
async with self._scheduler_lock:
    # 1. peek priority queue
    # 2. find available slot
    # 3. assign item to slot
    # 4. update estimated_ready_time of remaining queue
```

A single lock was chosen instead of fine-grained locking because:

- Deadlock risk is eliminated (no lock-ordering concerns)
- Critical sections are short (microseconds)
- Reasoning about correctness is simpler
- Refactoring to finer-grained locks remains possible if profiling reveals a real bottleneck

The database is the **source of truth**. The in-memory `heapq` is an optimization for fast next-item selection. On application startup, the scheduler rehydrates its in-memory state from the database.

---

## Priority and Aging

Orders are assigned a priority based on their customer type:

| Tier | Customer Type |
|------|--------------|
| Tier 1 | VIP |
| Tier 2 | App / Delivery |
| Tier 3 | Walk-in |

The priority is **always derived server-side**. Clients never send a priority directly.

To prevent starvation of lower-priority orders under continuous VIP traffic, an aging algorithm computes an `effective_priority` that improves over time:

```
effective_priority = base_priority - (wait_minutes / AGING_THRESHOLD) * AGING_FACTOR
```

Defaults: `AGING_THRESHOLD_MINUTES = 15`, `AGING_FACTOR = 1.0`. Configurable via environment variables.

The base priority is never mutated; only the effective priority is computed at queue inspection time.

For the full rationale, see [ADR-005](adr/005-aging-algorithm.md).

---

## Time Abstraction

All time access goes through the `Clock` port:

```python
class Clock(ABC):
    def now(self) -> datetime: ...
    async def sleep(self, seconds: float) -> None: ...
```

Implementations:

- `RealClock` — production
- `FakeClock` — tests, manually controlled with `tick(seconds)`

This eliminates time-related flakiness in tests and enables deterministic verification of future states. See [ADR-004](adr/004-time-abstraction.md).

---

## Order State Machine

Orders transition through a well-defined state machine.

For a Mermaid diagram, see [diagrams/order-state-machine.md](diagrams/order-state-machine.md).

```
PENDING_PAYMENT  →  PAID  →  QUEUED  →  BAKING  →  READY  →  DELIVERED
```

An order is `READY` when all its items finish baking. The state machine enforces valid transitions; invalid transitions raise `InvalidStateTransitionError`.

Items have their own simpler state machine: `WAITING → BAKING → DONE`.

A critical rule applies: an item in `BAKING` cannot be moved to a different slot or removed. This is the "lock at item level when baking starts" rule from the requirements. However, items still in `WAITING` from an order with other items already `BAKING` can be reprioritized by an incoming VIP order — the lock applies at the item level, not the order level.

---

## Persistence

PostgreSQL is the source of truth. Key tables:

- `customers` — with `customer_type`
- `menu_items` — with category, price, bake time
- `orders` — with status, priority, timestamps, idempotency_key
- `order_items` — items linked to orders and (when baking) to slots
- `ovens`, `slots` — kitchen infrastructure
- `domain_events` — append-only event log for auditing

Migrations are managed with Alembic. Seed data populates the menu and pre-registered VIP/APP customers.

---

## API Surface

The system exposes a REST API under `/api/v1/` and SSE streams under `/api/v1/streams/`. Full OpenAPI documentation is generated automatically and served at `/docs`.

See the [README](../README.md) for the endpoint summary.

---

## Future Extensibility

The architecture supports future additions without rewriting existing code:

- **Authentication** would be added as a FastAPI dependency in the interface layer. The domain remains unchanged.
- **Order cancellation** would be added as a new `CancelOrderUseCase` with a `CancellationPolicy` port. The scheduler already supports slot release.
- **Multi-instance scaling** would replace the in-memory queue and event bus with Redis without touching the domain.

Each of these is documented in greater detail in the relevant ADRs and in [ASSUMPTIONS.md](ASSUMPTIONS.md).

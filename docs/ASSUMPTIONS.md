# Assumptions

This document captures the assumptions and scoping decisions made during the design and implementation of the Snack Builders Bakery API. Some are based on confirmed clarifications from the client; others are scoping decisions made to keep the implementation focused on the stated requirements.

---

## Confirmed by the Client

These items were clarified via direct communication.

### Item-Level Lock During Baking

When an item starts baking, it cannot be removed or replaced. However, items still in the queue can be pushed back by an incoming VIP order — even if other items from the same order are already baking.

The unit of scheduling is the **item**, not the order. An order is considered ready when all of its items have finished baking.

### Starvation Prevention Policy

The client granted freedom to introduce a policy with justification. The system implements an **aging algorithm** that gradually improves the effective priority of orders waiting in the queue. See [ADR-005](adr/005-aging-algorithm.md) for the formula and rationale.

### Order Cancellation

Order cancellation is not part of the requirements and was explicitly marked as optional. It is not included because the cancellation policy (handling of in-progress items, refund rules, partial fulfillment) is a product decision outside the technical scope.

The architecture is prepared for this addition without rework: a `CANCELLED` state, a `CancellationPolicy` port (Strategy Pattern), and a `CancelOrderUseCase` can be added without modifying existing code.

### Payment Processing

No real credit card integration is required. A mock payment processor is implemented using the Strategy Pattern for cash and credit card. Swapping for a real provider (such as Stripe) would be a drop-in replacement at the infrastructure layer.

---

## Scoped-Out Features

### Authentication and Authorization

Authentication is not part of the requirements and is intentionally out of scope. The architecture is structured so that auth can be added later as a FastAPI dependency without changes to the domain, application, or repository layers.

The priority of an order is always **derived server-side** from the customer's type. Clients cannot supply a priority in the request payload.

### Real-Time Provider Integrations

The payment processor is a mock. Email and SMS notifications are not implemented.

---

## Design Decisions

### Customer Modeling

`Customer` is modeled as a domain entity, not as a user account. VIP and APP customers are pre-loaded as seed data — the system is assumed to know them ahead of time. Walk-in customers are created on-the-fly when an order is placed without a `customer_id`.

This separation makes it straightforward to add authentication later without conflating identity management with business modeling.

### Payment Before Cooking

An order is placed in `PENDING_PAYMENT` state and receives a hypothetical `estimated_ready_time` at placement. The order's items only enter the kitchen queue after payment is confirmed. This prevents cooking food that has not been paid for, and reflects how real bakeries operate.

The final `estimated_ready_time` is recalculated and confirmed when payment succeeds.

### Real-Time Updates via SSE

Server-Sent Events were chosen over WebSockets because all real-time updates are unidirectional (server → client). SSE provides automatic reconnection, simpler protocol semantics, and native FastAPI support.

### Persistence as the Source of Truth

PostgreSQL stores the authoritative state of orders, items, and slot assignments. The in-memory `heapq` priority queue is an optimization for fast next-item selection. On application startup, the scheduler rehydrates its in-memory state from the database, ensuring consistency after crashes or restarts.

### Single Lock for Concurrency

The `KitchenScheduler` uses a single `asyncio.Lock` to protect all state mutations. This eliminates the risk of deadlocks and keeps the implementation simple. Critical sections are intentionally short.

For workloads beyond a single-process deployment, this would be replaced by distributed locking (such as Redis Redlock) without changing the domain.

### Idempotency

The `POST /orders` endpoint supports an `Idempotency-Key` header. Duplicate requests with the same key return the original response, preventing duplicate orders on retry.

---

## Constraints and Limits

The system is designed for a single kitchen with two ovens and six concurrent slots. It is not designed for multi-location operation in its current form. The architectural choices (in-memory queue, in-process event bus) reflect this constraint.

---

## What Reviewers Should Know

When evaluating this implementation, please consider:

- Features explicitly excluded above were excluded for **scoping reasons**, not because the architecture does not support them
- The architecture's extensibility is demonstrated by the fact that adding cancellation, authentication, or distributed scheduling would not require modifying existing domain or application code
- The mock payment processor is intentionally realistic (with configurable latency and failure rates) to support resilience testing

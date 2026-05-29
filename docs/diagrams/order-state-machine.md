# Order State Machine

The lifecycle of an order from placement to delivery.

```mermaid
stateDiagram-v2
    [*] --> PENDING_PAYMENT: POST /orders
    
    PENDING_PAYMENT --> PAID: Payment succeeds
    PENDING_PAYMENT --> PAYMENT_FAILED: Payment fails
    
    PAYMENT_FAILED --> PAID: Retry succeeds
    
    PAID --> QUEUED: Items enter scheduler queue
    
    QUEUED --> BAKING: First item placed in slot
    
    BAKING --> READY: All items finished baking
    
    READY --> DELIVERED: Customer picks up
    
    DELIVERED --> [*]

    note right of PENDING_PAYMENT
        Order exists, items not yet
        queued for baking
    end note

    note right of PAID
        Trigger: scheduler enqueues items
    end note

    note right of BAKING
        At least one item is in an
        oven slot, others may be
        baking or still queued
    end note
```

## State Transitions

| From | To | Trigger |
|------|----|---------| 
| `PENDING_PAYMENT` | `PAID` | Payment processed successfully |
| `PENDING_PAYMENT` | `PAYMENT_FAILED` | Payment processor returned failure |
| `PAYMENT_FAILED` | `PAID` | Retry succeeded |
| `PAID` | `QUEUED` | Items added to scheduler queue (immediate) |
| `QUEUED` | `BAKING` | First item placed in an oven slot |
| `BAKING` | `READY` | Last item finished baking |
| `READY` | `DELIVERED` | Customer pickup confirmed |

## Item State Machine

Items have a simpler lifecycle within an order:

```mermaid
stateDiagram-v2
    [*] --> WAITING: Item created
    WAITING --> BAKING: Placed in slot
    BAKING --> DONE: Bake timer completes
    DONE --> [*]
    
    note right of BAKING
        An item in BAKING cannot
        be moved or removed
        (item-level lock)
    end note
```

## Invariants

- An order with state `BAKING` has at least one item in state `BAKING`
- An order with state `READY` has all items in state `DONE`
- Items in state `BAKING` cannot transition back to `WAITING` (item-level lock)
- The state machine rejects invalid transitions with `InvalidStateTransitionError`
- Items still in `WAITING` from an order with other items already `BAKING` can be reprioritized by an incoming VIP order

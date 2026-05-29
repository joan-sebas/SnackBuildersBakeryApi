# Scheduler Event Flow

The kitchen scheduler operates through four cooperating components that communicate via the event bus. This diagram shows the cycle from item placement to completion.

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Kitchen Scheduler
    participant UseCase as PlaceItemInSlot Use Case
    participant Bus as Event Bus
    participant BakeTimer as Bake Timer
    participant SlotMonitor as Slot Monitor

    Note over Scheduler: Slot becomes available
    Scheduler->>Scheduler: Acquire lock
    Scheduler->>Scheduler: Calculate effective priorities (aging)
    Scheduler->>Scheduler: Pick highest priority item
    Scheduler->>UseCase: Place item in slot

    UseCase->>UseCase: Mark item as BAKING
    UseCase->>UseCase: Persist state
    UseCase->>Bus: Emit ItemPlacedInSlot

    Bus->>BakeTimer: Notify
    BakeTimer->>BakeTimer: Schedule task with Clock.sleep(bake_time)

    Note over BakeTimer: Time passes (real or fake)

    BakeTimer->>Bus: Emit BakeTimerCompleted

    Bus->>SlotMonitor: Notify
    SlotMonitor->>SlotMonitor: Mark item as DONE
    SlotMonitor->>SlotMonitor: Release slot

    alt All items in order are DONE
        SlotMonitor->>Bus: Emit OrderReady
    end

    SlotMonitor->>Bus: Emit SlotBecameAvailable
    Bus->>Scheduler: Notify (cycle repeats)
```

## Component Responsibilities

- **Kitchen Scheduler:** Decides which item to bake next. Owns the priority queue and the single lock.
- **PlaceItemInSlot Use Case:** Performs the actual assignment, persists state, and emits the placement event.
- **Bake Timer:** Measures bake time and emits a completion event when time elapses.
- **Slot Monitor:** Detects completion, releases the slot, and triggers the next cycle.

## Why This Separation Matters

Each component has a single reason to change. The scheduler is independent of time measurement; the timer is independent of priority decisions; the monitor is independent of placement logic. This is the Single Responsibility Principle made concrete.

It also enables deterministic testing: by replacing the real clock with a fake clock and calling `process_pending_timers()`, tests can simulate the passage of any duration instantly.

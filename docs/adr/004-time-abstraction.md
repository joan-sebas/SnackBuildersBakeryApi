# ADR-004: Time Abstraction

## Status

Accepted.

## Context

The challenge explicitly requires that:

> The test suite should be able to mock or accelerate time to verify "future states" and scheduling flow without requiring real-world minutes to pass.

This forces a deliberate decision about how the system reads time and how it waits for time to pass.

If time is accessed directly via `datetime.now()` or `asyncio.sleep()` throughout the codebase, tests become slow, flaky, or both. A bake time of twenty minutes is impractical to test in real time.

## Decision

All time access goes through a `Clock` port defined in the domain layer:

```python
class Clock(ABC):
    def now(self) -> datetime: ...
    async def sleep(self, seconds: float) -> None: ...
```

Two implementations live in the infrastructure layer:

- **`RealClock`** — used in production. Delegates to `datetime.now(tz=UTC)` and `asyncio.sleep`.
- **`FakeClock`** — used in tests. Manually advanced with `tick(seconds)`. Pending `sleep` calls are resolved when their target time is reached.

The `Clock` is injected via FastAPI's dependency injection system. Tests override the dependency with `FakeClock`.

No code in the project calls `datetime.now()` or `asyncio.sleep()` directly except inside `RealClock`.

## Alternatives Considered

### Using `freezegun`

A popular library that monkey-patches `datetime`. Rejected because it relies on global state mutation, which conflicts with the principle of explicit dependencies. It also does not naturally handle `asyncio.sleep`.

### Hard-Coding Shorter Bake Times in Tests

Rejected because it changes business logic between tests and production. A test that uses a 5-second bake time does not validate the actual 5-minute behavior.

### A Real-Time Test Mode with Accelerated Clock

Considered as an additional option (an `AcceleratedClock` that runs at N times real speed). Useful for demos but not necessary for automated tests, and added implementation cost for limited benefit in the current scope.

## Consequences

### Positive

- Tests of bake-time behavior run in microseconds instead of minutes
- The dependency on time is explicit at every call site (the `Clock` parameter)
- Production and test code share the same logic, validated by the same tests
- Time-related bugs become deterministic and reproducible
- The abstraction is a textbook example of the Dependency Inversion Principle

### Trade-offs

- Every component that needs time must declare it as a dependency, adding a small amount of boilerplate
- Developers must remember to use `Clock.now()` instead of `datetime.now()`, which is enforced by code review and linting rules

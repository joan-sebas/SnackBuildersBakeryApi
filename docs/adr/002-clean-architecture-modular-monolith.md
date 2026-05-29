# ADR-002: Clean Architecture and Modular Monolith

## Status

Accepted.

## Context

The challenge involves a non-trivial domain with rich business rules: a priority-based scheduler with dynamic recalculation, an order state machine, multiple payment methods, and real-time event flows.

The architecture must support:

- Independent testing of business logic without HTTP or database concerns
- Easy substitution of components (mock payment, fake clock, in-memory event bus) for tests
- Long-term maintainability and clear extension points for features such as authentication or cancellation
- Reviewability by senior engineers who expect proper separation of concerns

## Decision

The project follows **Clean Architecture** with four strictly separated layers, structured as a **modular monolith**.

Layers, from outside to inside:

1. **Interface** — FastAPI routers, Pydantic DTOs, SSE endpoints, middleware
2. **Infrastructure** — SQLAlchemy repositories, payment mock, real clock, event bus subscribers
3. **Application** — Use cases orchestrating the domain
4. **Domain** — Entities, value objects, scheduler, ports (interfaces)

The dependency rule is enforced: dependencies always point inward. The domain has zero external dependencies and uses only the Python standard library.

## Alternatives Considered

### Layered Architecture (Controller / Service / Repository)

Common and familiar, but tends toward an anemic domain model where entities are dumb data carriers and behavior lives in services. The complexity of the scheduler and state machine in this challenge justifies a richer domain layer where entities own their behavior and invariants.

### Microservices

Considered for completeness. Rejected because the challenge describes a single bakery with a single physical kitchen. Microservices would introduce distributed-system complexity (network failures, data consistency, deployment coordination) without solving any problem present in the requirements. The modular monolith approach keeps the boundaries clear so a future migration to microservices remains possible.

### Hexagonal Architecture as a Distinct Style

Hexagonal Architecture is conceptually similar to Clean Architecture; they are often used interchangeably. The project adopts the "ports and adapters" vocabulary from Hexagonal where it clarifies the role of interfaces (such as `Clock`, `PaymentProcessor`, `EventPublisher`).

## Consequences

### Positive

- The domain layer can be tested without any infrastructure dependencies, leading to fast and deterministic tests
- The time abstraction (`Clock` port) and payment processor (`PaymentProcessor` port) are natural extensions of this design
- Adding authentication, cancellation, or distributed scheduling later is feasible without modifying existing domain or application code
- The modular monolith retains the simplicity of single-process deployment while preserving service-extraction options

### Trade-offs

- More files at the start, which can feel like overhead for small features
- The mapping between domain entities and SQLAlchemy models is explicit, requiring discipline at the repository boundary
- For a developer unfamiliar with Clean Architecture, there is a small learning curve when navigating the codebase

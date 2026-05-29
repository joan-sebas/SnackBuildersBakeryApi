# ADR-001: Stack Choice

## Status

Accepted.

## Context

The Snack Builders Bakery API requires a backend that handles concurrent orders, real-time scheduling, and stateful kitchen operations. The challenge gives freedom over technology choices.

The system must demonstrate:

- High-quality engineering with SOLID principles
- Robust handling of concurrency without race conditions
- Clean separation of concerns
- Comprehensive automated testing
- Easy environment setup through Docker

## Decision

The project uses the following stack:

- **Language and runtime:** Python 3.12
- **Web framework:** FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Testing:** pytest + pytest-asyncio + httpx
- **Code quality:** Ruff + mypy
- **Logging:** structlog
- **Containers:** Docker + Docker Compose

## Alternatives Considered

### Python + FastAPI vs TypeScript + NestJS

FastAPI was selected over NestJS based on a combination of technical fit and operational factors:

- **Native async runtime.** FastAPI is built on Starlette and `asyncio`, providing first-class support for concurrent I/O without thread-pool overhead. NestJS achieves similar results on Node.js, so the two are roughly equivalent on this axis.
- **Type-safe request/response cycle.** Pydantic v2 provides runtime validation and editor-time type inference end-to-end, generating OpenAPI documentation automatically. NestJS achieves this with class-validator and DTOs, requiring more boilerplate.
- **Ecosystem maturity for data engineering.** PostgreSQL + SQLAlchemy 2.0 is the de-facto standard combination for async Python services and offers granular control over transactions, isolation levels, and row-level locking. The Node.js ecosystem provides comparable tools but with more fragmentation.
- **Testing ergonomics.** pytest's fixture system and the dependency-injection model of FastAPI make it trivial to swap real implementations for fakes (such as `FakeClock`) at the boundary of the application.

NestJS is a strong alternative, but the existing depth of FastAPI experience available for this delivery allowed more time to be spent on architectural design rather than framework idioms. For a longer engagement, the choice would be re-evaluated based on team composition.

### Python + Django

Rejected because Django's batteries-included approach is overweight for a focused backend API. The system does not need an admin panel, a template engine, or session-based auth. Django's ORM is synchronous by default and async support is still maturing.

### SQLite instead of PostgreSQL

Rejected because SQLite has a single-writer lock at the file level, which is incompatible with the explicit concurrency requirements of the challenge. PostgreSQL provides row-level locking, isolation levels, and `SELECT ... FOR UPDATE`, all of which are needed for safe concurrent state updates.

### Redis-backed queue or Celery

Rejected as over-engineering. The system runs on a single node with two ovens and six slots. An in-process queue with `asyncio` primitives is appropriate and avoids the operational cost of a separate broker. The architecture leaves room to swap this for Redis in the future without affecting the domain.

## Consequences

### Positive

- FastAPI provides async-native HTTP, automatic OpenAPI generation, and excellent integration with Pydantic for type-safe request and response handling
- PostgreSQL offers strong transactional guarantees and row-level locking when needed
- SQLAlchemy 2.0's async support is mature and provides fine-grained control over transactions and isolation levels
- The stack is widely understood, easing review by any senior backend reviewer
- Ruff replaces black, isort, and flake8 with a single fast tool, simplifying the toolchain

### Trade-offs

- Python's Global Interpreter Lock limits CPU-bound parallelism, but the workload here is I/O-bound, so this is not a concern in practice
- The in-process queue does not survive process restarts in memory. However, the database is the source of truth, and the scheduler rehydrates from the database on startup. This pattern is documented in [ADR-003](003-event-driven-scheduler.md)

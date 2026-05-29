# Snack Builders Bakery API

A backend API for managing orders, payments, menu, and a priority-based kitchen scheduler.

> **Status:** Project in active development. This commit establishes the architectural foundation. Implementation milestones follow.

---

## Overview

The system models a bakery kitchen with two ovens (three slots each, six concurrent slots total) and a priority-based scheduling queue. It handles order placement, payment processing, and dynamic recalculation of estimated ready times when VIP orders arrive.

Three priority tiers are supported:

- **Tier 1 (VIP):** highest priority
- **Tier 2 (App / Delivery):** medium priority
- **Tier 3 (Walk-in):** standard priority

A starvation prevention mechanism (aging algorithm) ensures that lower-priority orders cannot wait indefinitely under continuous VIP traffic.

---

## Architectural Foundation

The system is designed as a **modular monolith** following **Clean Architecture** with four strictly separated layers (Domain, Application, Infrastructure, Interface). The dependency rule is enforced: dependencies always point inward.

For full architectural details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Significant design decisions are documented as ADRs in [docs/adr/](docs/adr/):

- [ADR-001: Stack Choice](docs/adr/001-stack-choice.md)
- [ADR-002: Clean Architecture and Modular Monolith](docs/adr/002-clean-architecture-modular-monolith.md)
- [ADR-003: Event-Driven Scheduler](docs/adr/003-event-driven-scheduler.md)
- [ADR-004: Time Abstraction](docs/adr/004-time-abstraction.md)
- [ADR-005: Aging Algorithm for Starvation Prevention](docs/adr/005-aging-algorithm.md)

Scoping decisions and assumptions are documented in [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| Web framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio |
| Code quality | Ruff + mypy |
| Containers | Docker + Docker Compose |

---

## Quick Start

```bash
docker compose up
```

Once running:

- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Development

```bash
make install       # install dependencies
make test          # run all tests
make lint          # run ruff and mypy
make migrate       # apply database migrations
make up            # start the full stack via docker compose
make down          # stop the stack
```

---

## Project Structure

```
snack-builders-bakery/
├── src/
│   ├── domain/           # Pure business logic
│   ├── application/      # Use cases
│   ├── infrastructure/   # Adapters (DB, payment, clock)
│   └── interface/        # HTTP API
├── tests/                # Unit, integration, concurrency
├── docs/
│   ├── adr/              # Architecture Decision Records
│   ├── diagrams/         # Mermaid diagrams
│   ├── ARCHITECTURE.md
│   ├── ASSUMPTIONS.md
│   └── AI_USAGE.md
├── alembic/              # Database migrations
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## AI-Assisted Development

This project was built with the help of AI-assisted development tools. See [docs/AI_USAGE.md](docs/AI_USAGE.md) for details on how those tools were used and how their output was verified.

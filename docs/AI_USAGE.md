# AI-Assisted Development

This project was built collaboratively with AI tools. This document explains how those tools were used and what was verified independently.

The intent of this document is transparency: AI tools served as a productivity multiplier, not a substitute for judgment.

---

## Tools Used

- **Claude (Anthropic)** — used for architectural exploration, drafting ADRs, and reviewing trade-offs between design alternatives.
- **Claude Code** — used as a pair programmer for boilerplate generation, scaffolding, and routine implementation. Every suggestion was reviewed before being accepted.
- **GitHub Copilot** — used for in-editor autocomplete on routine code patterns.

---

## Where AI Helped

- Generating initial scaffolding for SQLAlchemy models from domain entities
- Drafting initial structure for ADR documents
- Exploring trade-offs between alternative implementations (for example, single lock versus fine-grained locking; SSE versus WebSocket)
- Suggesting test scenarios for edge cases
- Polishing documentation for clarity and consistency
- Generating Mermaid diagram syntax from architectural descriptions

---

## What Was Owned by the Developer

The following decisions and artifacts were owned by the developer throughout the project:

- The choice of stack and the justification for each component
- Domain modeling — entities, value objects, events, and invariants
- The event-driven scheduler design with four cooperating components
- The decision to use a single lock instead of fine-grained locking
- The aging algorithm choice and its parameters
- The decision to scope out authentication and cancellation
- All architectural decisions documented in ADRs
- Every line of code merged to `main`

---

## How AI Output Was Verified

- Every code snippet was reviewed line by line before being committed
- Tests were written first (TDD) for critical domain logic, ensuring AI-generated implementations had to satisfy human-defined behavior
- Architectural reviews were performed against SOLID principles and Clean Architecture rules
- Suggestions that violated the dependency rule (for example, importing infrastructure types into the domain) were rejected
- When AI suggested adding features outside the scope (such as authentication or cancellation), those suggestions were declined

---

## Why This Matters

Using AI tools well is itself a skill. The same way a senior engineer uses an IDE, a debugger, and a profiler effectively, AI tools become productive when paired with clear architectural standards and disciplined review.

For a technical assessment, the relevant question is not "did AI help?" but "did the developer use AI with judgment?" The structure of this codebase — its architectural discipline, its testing rigor, and the conscious scoping of features — is intended to demonstrate the latter.

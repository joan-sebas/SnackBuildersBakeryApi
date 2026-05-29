# CLAUDE.md

Conventions and guidelines for working on this codebase. Read this before contributing.

For architectural details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
For scoping decisions, see [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md).

---

## Architectural Boundaries

The project follows **Clean Architecture** with four layers. The dependency rule is absolute: dependencies point inward.

- **Domain** has zero external dependencies (no FastAPI, no SQLAlchemy, no Pydantic)
- **Application** depends only on Domain
- **Infrastructure** implements Domain ports
- **Interface** depends on Application and Domain contracts

If a change would violate the dependency rule, the change is wrong. Refactor or stop.

---

## Code Style

### Naming

- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: leading underscore

### Imports

Standard library, then third-party, then local — separated by blank lines. Absolute imports only.

### Type Hints

Mandatory in domain and application layers. Modern syntax preferred (`list[X]`, `X | None`).

### Docstrings

Concise (1-3 lines for most functions). Skip docstrings on trivial methods.

Acceptable:
```python
def calculate_price(items: list[Item]) -> Money:
    """Sum the prices of all items at their respective quantities."""
```

Not acceptable:
```python
def calculate_price(items: list[Item]) -> Money:
    """
    This function calculates the total price for a given list of items.
    It iterates through each item, multiplies the unit price by the quantity,
    and accumulates the total. It then returns the final price.
    """
```

### Comments

Comments explain *why*, not *what*. If code is self-explanatory, no comment is needed.

Acceptable:
```python
# Sort by effective priority, not base priority — aging may have changed ordering
queue.sort(key=lambda item: item.effective_priority)
```

Not acceptable:
```python
# Loop through each item in the list
for item in items:
    # Calculate the price for this item
    price = item.unit_price * item.quantity
```

### Documentation Tone

All written documentation uses **impersonal voice**. Avoid "we", "I", "let's", "now we will".

Acceptable:
- "Python was chosen because..."
- "The scheduler uses a single lock"
- "Tests run in microseconds"

Not acceptable:
- "We chose Python because..."
- "I use a single lock"
- "Let's run the tests"

---

## Testing

- **TDD is mandatory for the domain layer.** Write the test first, then make it pass.
- Tests mirror `src/` structure under `tests/`
- Test names: `test_<scenario>_<expected_outcome>`
- Time-dependent tests use `FakeClock`, never `time.sleep`
- Coverage targets: 80% global, 95% on domain

---

## Git Conventions

### Branch Strategy

Trunk-based with `main`. Short feature branches when working in parallel.

### Conventional Commits

Required format:

```
feat:     new feature
fix:      bug fix
refactor: refactor without behavior change
test:     adding or modifying tests
docs:     documentation only
chore:    tooling, dependencies, config
ci:       CI/CD changes
perf:     performance improvements
style:    formatting, no logic change
```

Subject lines: imperative present tense, under 72 characters, no trailing period.

Acceptable:
```
feat: add priority queue with aging algorithm
test: vip order pushes back queued lower-priority items
fix: rehydrate scheduler state from db on startup
```

Not acceptable:
```
feat: added new code              (past tense, vague)
update                            (no type prefix)
WIP                               (never commit WIP to main)
```

One logical change per commit. If the message needs "and", split into two commits.

---

## Definition of Done

A task is done when:

1. Code follows the conventions in this file
2. Tests pass (`make test`)
3. Linter passes (`make lint`)
4. Type checker passes (`mypy`)
5. Committed with a conventional commit message
6. No `TODO`, `FIXME`, or `XXX` comments left

---

## Architecture Decision Records

Significant decisions are recorded as ADRs in [docs/adr/](docs/adr/). When introducing a new pattern or making a non-trivial choice, write an ADR. When modifying behavior covered by an ADR, reference it in the commit message.

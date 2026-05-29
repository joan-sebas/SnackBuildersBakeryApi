<!-- Title: scoped Conventional Commit, e.g. feat(domain): add money value object -->

Closes #

## What

<!-- One or two sentences on what this PR delivers. -->

## Why / design decisions

<!-- The reasoning a reviewer cannot infer from the diff: trade-offs taken,
     alternatives rejected, and any ADR this follows or introduces.
     Example: Decimal over float to avoid rounding; currency guard instead of
     conversion because multi-currency is out of scope (ADR-00X). -->

## Checklist

- [ ] `make test` and `make lint` are green
- [ ] Dependency rule respected (no inward layer imports an outward one)
- [ ] Domain/application changes are typed and unit-tested (`FakeClock` for time)
- [ ] No out-of-scope work (see `docs/ASSUMPTIONS.md`)
- [ ] Commits follow scoped Conventional Commits

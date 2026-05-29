# ADR-005: Aging Algorithm for Starvation Prevention

## Status

Accepted.

## Context

The challenge specifies three priority tiers (VIP, App/Delivery, Walk-in) with the rule that "when an oven slot opens, the system must pick the highest-priority item from the queue first."

A strict implementation of this rule leads to **starvation**: if VIP orders arrive continuously, a Tier 3 order could theoretically wait forever.

When asked, the client granted freedom to introduce a policy with justification:

> Feel free to introduce your own policy and justify why.

A decision is required on whether to implement strict priority preemption (with the risk of starvation) or introduce a fairness mechanism.

## Decision

The scheduler implements an **aging algorithm** that improves an order's effective priority based on how long it has been waiting:

```
effective_priority = base_priority_value
                   - (wait_minutes / AGING_THRESHOLD_MINUTES) * AGING_FACTOR
```

Where lower values represent higher priority (the queue is a min-heap).

Default configuration:

- `AGING_THRESHOLD_MINUTES = 15`
- `AGING_FACTOR = 1.0`

Both are configurable via environment variables.

The `base_priority` is **never mutated**. The `effective_priority` is computed at queue-inspection time, preserving an accurate audit trail of the original tier.

## Alternatives Considered

### Strict Priority Preemption (No Aging)

Theoretically valid and matches the literal reading of the requirement. Rejected because it permits starvation, which is unrealistic in a business context. A Tier 3 customer who has waited thirty minutes deserves to be served before a Tier 1 VIP who just walked in.

### Hard Cap on Wait Time

Promote any order that has waited more than X minutes directly to top priority. Rejected because the transition is abrupt and less elegant than gradual aging.

### Weighted Random Selection

Each tier has a probability weight, with weights adjusted by wait time. Rejected because non-determinism complicates debugging and reasoning.

## Consequences

### Positive

- Lower-priority orders cannot starve indefinitely under continuous VIP load
- The algorithm is a recognized pattern, used in production schedulers including Unix nice values and the Linux Completely Fair Scheduler. This gives the design intellectual lineage.
- Parameters are configurable, allowing operational tuning without code changes
- Under normal load, the algorithm has minimal effect; VIP orders still go first
- The base priority is preserved, so analytics and auditing remain accurate

### Trade-offs

- The system is slightly more complex than a strict priority queue
- Operators must understand the meaning of the threshold and factor to tune them effectively. This is mitigated by sensible defaults and documentation.
- A pathological set of parameters could over-promote Tier 3 orders and starve VIPs. Tests verify that under normal load, VIP priority is preserved.

"""Priority tiers for baking queue; lower numeric value = higher priority (min-heap compatible)."""

from enum import IntEnum


class Priority(IntEnum):
    VIP = 1
    APP = 2
    WALKIN = 3

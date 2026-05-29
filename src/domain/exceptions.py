"""Root exception hierarchy for the domain layer."""


class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidStateTransitionError(DomainError):
    """Raised when a requested state transition is not permitted."""

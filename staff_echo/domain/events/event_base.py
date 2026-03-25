"""
Domain Event Base

Architectural Intent:
- Foundation for all domain events in the Staff-Echo system
- Events are immutable value objects that record what happened in the domain
- Collected on aggregates and dispatched after persistence
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

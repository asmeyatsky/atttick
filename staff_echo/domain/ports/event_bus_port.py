"""Event Bus Port — defines the contract for domain event publishing."""

from collections.abc import Callable
from typing import Protocol

from staff_echo.domain.events.event_base import DomainEvent


class EventBusPort(Protocol):
    async def publish(self, events: list[DomainEvent]) -> None: ...
    async def subscribe(self, event_type: type, handler: Callable) -> None: ...

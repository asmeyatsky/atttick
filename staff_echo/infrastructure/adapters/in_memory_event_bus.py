"""In-memory Event Bus — implements EventBusPort for development/testing."""

import asyncio
from collections import defaultdict
from collections.abc import Callable

from staff_echo.domain.events.event_base import DomainEvent


class InMemoryEventBus:

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)
        self._published: list[DomainEvent] = []

    async def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            self._published.append(event)
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)

    async def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    @property
    def published_events(self) -> list[DomainEvent]:
        return list(self._published)

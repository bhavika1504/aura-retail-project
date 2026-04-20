# =============================================================
# events/event_bus.py
# PATTERN: Observer (Publish-Subscribe) + Singleton
#
# Central message bus for all inter-subsystem communication.
# Publishers call publish(event) — they never import subscribers.
# Subscribers call subscribe(EventType, handler).
# =============================================================
from __future__ import annotations
from typing import Callable, Dict, List, Type
from events.events import Event


class EventBus:
    """
    PATTERN: Observer + Singleton

    One global instance. All subsystems share the same bus,
    so adding a new subscriber never changes any publisher.
    """
    _instance: "EventBus | None" = None

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: Dict[Type[Event], List[Callable]] = {}
        return cls._instance

    # ----------------------------------------------------------
    # Subscription management
    # ----------------------------------------------------------
    def subscribe(self, event_type: Type[Event], handler: Callable) -> None:
        """Register a handler for a specific event type."""
        self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: Type[Event], handler: Callable) -> None:
        """Remove a previously registered handler."""
        handlers = self._subscribers.get(event_type, [])
        try:
            handlers.remove(handler)
        except ValueError:
            pass

    # ----------------------------------------------------------
    # Publishing
    # ----------------------------------------------------------
    def publish(self, event: Event) -> None:
        """
        Broadcast an event to all registered handlers.
        Errors in individual handlers are caught so one bad
        subscriber cannot block others.
        """
        for handler in self._subscribers.get(type(event), []):
            try:
                handler(event)
            except Exception as exc:
                print(f"[EventBus] Handler error ({type(event).__name__}): {exc}")

    # ----------------------------------------------------------
    # Utility (testing / reset)
    # ----------------------------------------------------------
    @classmethod
    def reset(cls) -> None:
        """Destroy the singleton (useful for isolated test runs)."""
        cls._instance = None

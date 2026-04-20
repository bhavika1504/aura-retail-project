# =============================================================
# hardware/failure_chain.py  — Bhavika Mulani (202512079)
# PATTERN: Chain of Responsibility
#
# When a hardware or transaction failure occurs, it travels
# through three handlers in sequence.  Each handler either
# resolves the issue and returns True, or passes it forward.
#
#   RetryHandler → RecalibrationHandler → TechnicianAlertHandler
# =============================================================
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class FailureHandler(ABC):
    """
    PATTERN: Chain of Responsibility — Abstract Handler

    Every handler can:
      1. Attempt to resolve the failure and return True.
      2. Call _pass_to_next() to delegate to the next handler.

    Build the chain with:
        h1.set_next(h2).set_next(h3)
    """

    def __init__(self) -> None:
        self._next: Optional[FailureHandler] = None

    def set_next(self, handler: FailureHandler) -> FailureHandler:
        """Fluent chain builder — returns handler so calls can be chained."""
        self._next = handler
        return handler

    @abstractmethod
    def handle_failure(self, failure: Dict[str, Any]) -> bool:
        """Try to handle failure. Returns True if resolved."""

    def _pass_to_next(self, failure: Dict[str, Any]) -> bool:
        if self._next:
            return self._next.handle_failure(failure)
        print("[FailureChain] 🚨 All handlers exhausted. Manual intervention required.")
        return False


class RetryHandler(FailureHandler):
    """
    PATTERN: CoR — Handler 1: Retry the failed operation.

    On the first call attempts a simple retry.
    If already retried MAX_RETRIES times, escalates.
    """
    MAX_RETRIES: int = 3

    def handle_failure(self, failure: Dict[str, Any]) -> bool:
        component = failure.get("component", "unknown")
        retries = failure.get("retry_count", 0)
        print(f"[RetryHandler] Retrying '{component}' "
              f"(attempt {retries + 1}/{self.MAX_RETRIES})")

        if retries < self.MAX_RETRIES:
            failure["retry_count"] = retries + 1
            # Simulate: second attempt succeeds in a transient fault
            if retries >= 1:
                print(f"[RetryHandler] ✅ Retry succeeded for '{component}'.")
                return True

        print(f"[RetryHandler] ❌ Max retries reached. Escalating to recalibration.")
        return self._pass_to_next(failure)


class RecalibrationHandler(FailureHandler):
    """
    PATTERN: CoR — Handler 2: Recalibrate the hardware component.

    Calls recalibrate() on the hardware object stored in the
    failure dict (put there by HardwareManager).
    """

    def handle_failure(self, failure: Dict[str, Any]) -> bool:
        component = failure.get("component", "unknown")
        hw_ref = failure.get("hardware_ref")          # actual hardware object
        print(f"[RecalibrationHandler] 🔧 Recalibrating '{component}'…")

        if hw_ref and hasattr(hw_ref, "recalibrate"):
            success = hw_ref.recalibrate()
            if success:
                print(f"[RecalibrationHandler] ✅ Recalibration succeeded.")
                return True

        print(f"[RecalibrationHandler] ❌ Recalibration failed. Escalating to technician.")
        return self._pass_to_next(failure)


class TechnicianAlertHandler(FailureHandler):
    """
    PATTERN: CoR — Handler 3: Alert a human technician.

    Last resort — publishes HardwareFailureEvent so city monitoring
    and maintenance service are notified via EventBus.
    Always returns False (human must physically intervene).
    """

    def handle_failure(self, failure: Dict[str, Any]) -> bool:
        from events.event_bus import EventBus
        from events.events import HardwareFailureEvent
        component = failure.get("component", "unknown")
        print(f"[TechnicianAlertHandler] 🚨 TECHNICIAN ALERT: '{component}' unrecoverable!")
        EventBus().publish(HardwareFailureEvent(
            source="FailureChain",
            component=component,
            error_message=failure.get("error", "Unresolved hardware fault"),
            failure_count=failure.get("retry_count", 0),
        ))
        return False   # human intervention required — do not mark as resolved

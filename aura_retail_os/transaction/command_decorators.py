# =============================================================
# PATTERN: Decorator
#
# CommandDecorator wraps ANY Command object and adds
# cross-cutting behaviour WITHOUT modifying the command class.
#
# Decorators implemented:
#   LoggingDecorator    — structured pre/post execution log
#   TimingDecorator     — measures wall-clock execution time
#   ValidationDecorator — pre-flight check; blocks on failure
#
# Usage (composable):
#   raw_cmd = PurchaseCommand(...)
#   cmd = TimingDecorator(LoggingDecorator(raw_cmd))   # chain
#   invoker.execute(cmd)
#
# The CommandInvoker and concrete commands are UNAWARE of
# decorators — open/closed principle preserved.
# =============================================================
from __future__ import annotations
import time
from abc import abstractmethod
from transaction.command import Command


class CommandDecorator(Command):
    """
    PATTERN: Decorator — Abstract Component Wrapper

    Wraps a Command and delegates all calls to the wrapped object.
    Subclasses override execute() to add cross-cutting behaviour.
    undo() and get_description() are always forwarded to the inner
    command so the decorator is transparent to the invoker.
    """

    def __init__(self, command: Command) -> None:
        self._wrapped = command

    @abstractmethod
    def execute(self) -> bool:
        """Subclasses add behaviour here, then call self._wrapped.execute()."""

    def undo(self) -> bool:
        return self._wrapped.undo()

    def get_description(self) -> str:
        return self._wrapped.get_description()


# ── Concrete Decorator 1 ──────────────────────────────────────

class LoggingDecorator(CommandDecorator):
    """
    PATTERN: Decorator — Logging Cross-Cutting Concern

    Intercepts execute() and emits structured log lines before
    and after the real command runs.  No change to the command.

    Example output:
        [LoggingDecorator] PRE  → PurchaseCommand.execute()
        [LoggingDecorator] POST ← PurchaseCommand SUCCESS ✅
    """

    def __init__(self, command: Command) -> None:
        super().__init__(command)
        self._log: list[str] = []

    def execute(self) -> bool:
        cmd_name = type(self._wrapped).__name__

        pre_msg = f"[LoggingDecorator] PRE  -> {cmd_name}.execute() called"
        self._log.append(pre_msg)
        print(pre_msg)

        result = self._wrapped.execute()

        status = "[SUCCESS]" if result else "[FAILED]"
        post_msg = f"[LoggingDecorator] POST <- {cmd_name} {status}"
        self._log.append(post_msg)
        print(post_msg)

        return result

    def get_log(self) -> list[str]:
        """Return a copy of all log lines emitted so far."""
        return list(self._log)

    def clear_log(self) -> None:
        self._log.clear()


# ── Concrete Decorator 2 ──────────────────────────────────────

class TimingDecorator(CommandDecorator):
    """
    PATTERN: Decorator — Performance Timing Cross-Cutting Concern

    Wraps execute() with high-resolution wall-clock measurement.
    Adds 'execution_ms' to result without touching the command.

    Example output:
        [TimingDecorator] PurchaseCommand completed in 1.23 ms
    """

    def __init__(self, command: Command) -> None:
        super().__init__(command)
        self._last_ms: float | None = None

    def execute(self) -> bool:
        start = time.perf_counter()
        result = self._wrapped.execute()
        self._last_ms = round((time.perf_counter() - start) * 1000, 3)

        cmd_name = type(self._wrapped).__name__
        print(
            f"[TimingDecorator] {cmd_name} completed in "
            f"{self._last_ms} ms"
        )
        return result

    @property
    def last_execution_ms(self) -> float | None:
        """Wall-clock time (ms) of the most recent execute(), or None."""
        return self._last_ms


# ── Concrete Decorator 3 ──────────────────────────────────────

class ValidationDecorator(CommandDecorator):
    """
    PATTERN: Decorator — Pre-Flight Validation Cross-Cutting Concern

    Runs a caller-supplied validator BEFORE delegating to the
    wrapped command.  If validation fails the command never runs.

    validator: callable() -> tuple[bool, str]
        Returns (True, "") on pass, (False, reason) on block.

    Example output:
        [ValidationDecorator] PRE-CHECK passed ✅
        [ValidationDecorator] PRE-CHECK FAILED — Stock below safety level
    """

    def __init__(self, command: Command, validator) -> None:
        super().__init__(command)
        self._validator = validator       # () -> (bool, str)

    def execute(self) -> bool:
        ok, reason = self._validator()

        if not ok:
            msg = (
                f"[ValidationDecorator] PRE-CHECK FAILED — {reason} [BLOCK]\n"
                f"  Command '{self._wrapped.get_description()}' was BLOCKED."
            )
            print(msg)
            return False

        print("[ValidationDecorator] PRE-CHECK PASSED")
        return self._wrapped.execute()

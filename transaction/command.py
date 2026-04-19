# =============================================================
# transaction/command.py  — Kajal Varlani (202512017)
# PATTERN: Command (abstract interface)
#
# Encapsulates every kiosk operation as an object so that:
#   - Operations can be queued, logged, and undone.
#   - CommandInvoker never knows what a command does internally.
#   - New operations can be added without changing the invoker.
# =============================================================
from abc import ABC, abstractmethod


class Command(ABC):
    """
    PATTERN: Command — Abstract base

    All concrete commands (Purchase, Refund, Restock) implement:
      execute()          → perform the operation, return True/False
      undo()             → reverse the operation, return True/False
      get_description()  → human-readable string for logging
    """

    @abstractmethod
    def execute(self) -> bool:
        """Run the command. Returns True on success."""

    @abstractmethod
    def undo(self) -> bool:
        """Reverse the last successful execute(). Returns True on success."""

    @abstractmethod
    def get_description(self) -> str:
        """One-line description used in the transaction log."""

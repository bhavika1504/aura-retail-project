# =============================================================
# transaction/command_invoker.py  — Kajal Varlani (202512017)
# PATTERN: Command (Invoker)
#
# The invoker knows nothing about what a command does.
# It simply calls execute(), records history for undo support,
# and logs every operation via PersistenceManager.
# =============================================================
from __future__ import annotations
from datetime import datetime
from typing import List

from transaction.command import Command
from inventory.persistence_manager import PersistenceManager


class CommandInvoker:
    """
    PATTERN: Command — Invoker

    Responsibilities
    ----------------
    - Execute commands through a single gateway
    - Maintain a history stack for undo support
    - Persist every command (success or failure) to the CSV log
    """

    def __init__(self, persistence_manager: PersistenceManager) -> None:
        self._history: List[Command] = []
        self._persistence = persistence_manager

    # ----------------------------------------------------------
    # Execution
    # ----------------------------------------------------------
    def execute(self, command: Command) -> bool:
        """Execute command, push to history on success, log always."""
        success = command.execute()
        if success:
            self._history.append(command)
        self._log(command, "SUCCESS" if success else "FAILED")
        return success

    # ----------------------------------------------------------
    # Undo
    # ----------------------------------------------------------
    def undo_last(self) -> bool:
        """Undo the most recently executed command."""
        if not self._history:
            print("[CommandInvoker] No commands to undo.")
            return False
        command = self._history.pop()
        success = command.undo()
        self._log(command, "UNDONE" if success else "UNDO_FAILED")
        return success

    # ----------------------------------------------------------
    # History query
    # ----------------------------------------------------------
    def get_history(self) -> List[str]:
        return [cmd.get_description() for cmd in self._history]

    def history_size(self) -> int:
        return len(self._history)

    # ----------------------------------------------------------
    # Logging
    # ----------------------------------------------------------
    def _log(self, command: Command, status: str) -> None:
        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "command": command.get_description(),
            "status": status,
        }
        self._persistence.log_transaction(record)

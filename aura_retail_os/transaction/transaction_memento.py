# =============================================================

# PATTERN: Memento
#
# Before dispensing a product, PurchaseCommand takes a snapshot
# (TransactionMemento) of the transaction + inventory state.
# If hardware fails mid-dispense, TransactionCaretaker uses the
# snapshot to restore the previous consistent state — guaranteeing
# atomic transactions (either fully done or fully rolled back).
# =============================================================
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class TransactionMemento:
    """
    PATTERN: Memento — Snapshot

    Captures transaction state BEFORE the point of no return
    (physical dispensing).  Stored by TransactionCaretaker.

    Fields
    ------
    transaction_id      : unique ID for this purchase attempt
    product_id          : which product is being purchased
    quantity            : how many units
    amount              : price charged (may be 0 before payment)
    inventory_snapshot  : copy of product.to_dict() before any changes
    timestamp           : when the snapshot was taken
    """
    transaction_id: str
    product_id: str
    quantity: int
    amount: float
    inventory_snapshot: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class TransactionCaretaker:
    """
    PATTERN: Memento — Caretaker

    Stores snapshots indexed by transaction_id.
    PurchaseCommand calls:
      save_memento()    → before dispensing
      get_memento()     → to restore on failure
      discard_memento() → after successful commit (cleanup)
    """

    def __init__(self) -> None:
        self._mementos: Dict[str, TransactionMemento] = {}

    def save_memento(self, memento: TransactionMemento) -> None:
        self._mementos[memento.transaction_id] = memento
        print(f"[Caretaker] [MEMO] Snapshot saved for transaction '{memento.transaction_id}'")

    def get_memento(self, transaction_id: str) -> Optional[TransactionMemento]:
        return self._mementos.get(transaction_id)

    def discard_memento(self, transaction_id: str) -> None:
        """Remove snapshot once a transaction is fully committed."""
        self._mementos.pop(transaction_id, None)

    def has_memento(self, transaction_id: str) -> bool:
        return transaction_id in self._mementos

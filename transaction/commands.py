# =============================================================
# transaction/commands.py  — Kajal Varlani (202512017)
# PATTERN: Command (concrete commands)
#
# PurchaseCommand — full atomic purchase with Memento rollback
# RefundCommand   — refund + inventory restoration
# RestockCommand  — add stock, undoable
# =============================================================
import uuid
from transaction.command import Command
from transaction.transaction_memento import TransactionMemento, TransactionCaretaker


class PurchaseCommand(Command):
    """
    PATTERN: Command + Memento

    Execute sequence
    ----------------
    1. Check derived available stock  (blocks overselling)
    2. Reserve stock                  (prevents concurrent oversell)
    3. Compute final price via Strategy
    4. Save Memento snapshot          ← point of no return
    5. Process payment
    6. Dispense product (via HardwareManager → failure chain)
    7a. On success → commit inventory, discard memento
    7b. On failure → refund, release reservation, publish RollbackEvent
    """

    def __init__(
        self,
        kiosk_id: str,
        product_id: str,
        quantity: int,
        inventory,               # Inventory instance
        hardware_manager,        # HardwareManager instance
        pricing_strategy,        # PricingStrategy instance
        context,                 # PricingContext instance
        caretaker: TransactionCaretaker,
    ) -> None:
        self._kiosk_id = kiosk_id
        self._product_id = product_id
        self._quantity = quantity
        self._inventory = inventory
        self._hw = hardware_manager
        self._pricing = pricing_strategy
        self._context = context
        self._caretaker = caretaker
        self._transaction_id: str = str(uuid.uuid4())[:8].upper()
        self._amount_paid: float = 0.0
        self._executed: bool = False

    # ----------------------------------------------------------
    def execute(self) -> bool:
        from events.event_bus import EventBus
        from events.events import TransactionRollbackEvent

        # 1. Derived attribute check
        avail = self._inventory.get_available_stock(self._product_id)
        if avail < self._quantity:
            print(f"[PurchaseCommand] ❌ Insufficient stock for '{self._product_id}' "
                  f"(available: {avail}, requested: {self._quantity})")
            return False

        # 2. Reserve stock (concurrent safety)
        if not self._inventory.reserve_stock(self._product_id, self._quantity):
            print(f"[PurchaseCommand] ❌ Reservation failed for '{self._product_id}'")
            return False

        # 3. Compute final price (Strategy)
        product = self._inventory.get_product(self._product_id)
        self._amount_paid = self._pricing.calculate_price(
            product.base_price * self._quantity, self._context
        )

        # 4. Save Memento BEFORE any irreversible action
        memento = TransactionMemento(
            transaction_id=self._transaction_id,
            product_id=self._product_id,
            quantity=self._quantity,
            amount=self._amount_paid,
            inventory_snapshot=product.to_dict().copy(),
        )
        self._caretaker.save_memento(memento)

        # 5. Payment
        payment_ok = self._hw.process_payment(self._amount_paid, self._transaction_id)
        if not payment_ok:
            self._inventory.release_reservation(self._product_id, self._quantity)
            self._caretaker.discard_memento(self._transaction_id)
            print(f"[PurchaseCommand] ❌ Payment failed — transaction {self._transaction_id} aborted.")
            return False

        # 6. Dispense
        dispense_ok = self._hw.dispense_product(self._product_id, self._quantity)
        if not dispense_ok:
            # ROLLBACK: refund + release
            self._hw.process_refund(self._amount_paid, self._transaction_id)
            self._inventory.release_reservation(self._product_id, self._quantity)
            EventBus().publish(TransactionRollbackEvent(
                source=self._kiosk_id,
                transaction_id=self._transaction_id,
                reason="Hardware dispense failure",
            ))
            print(f"[PurchaseCommand] ❌ Rollback complete for {self._transaction_id}")
            return False

        # 7a. Commit
        self._inventory.commit_transaction(self._product_id, self._quantity)
        self._caretaker.discard_memento(self._transaction_id)
        self._executed = True
        print(f"[PurchaseCommand] ✅ Transaction {self._transaction_id} complete — "
              f"₹{self._amount_paid:.2f} charged.")
        return True

    # ----------------------------------------------------------
    def undo(self) -> bool:
        """Reverse: refund the customer and put stock back."""
        if not self._executed:
            return False
        ok = self._hw.process_refund(self._amount_paid, self._transaction_id)
        if ok:
            self._inventory.restock(self._product_id, self._quantity)
            self._executed = False
            print(f"[PurchaseCommand] ↩️  Undo successful for {self._transaction_id}")
        return ok

    def get_description(self) -> str:
        return (f"Purchase[{self._transaction_id}]: "
                f"{self._quantity}× {self._product_id} @ ₹{self._amount_paid:.2f}")


# =============================================================

class RefundCommand(Command):
    """
    PATTERN: Command — Refund an earlier transaction.
    Releases payment back to customer and restores inventory.
    """

    def __init__(
        self,
        kiosk_id: str,
        transaction_id: str,
        amount: float,
        product_id: str,
        quantity: int,
        inventory,
        hardware_manager,
    ) -> None:
        self._kiosk_id = kiosk_id
        self._transaction_id = transaction_id
        self._amount = amount
        self._product_id = product_id
        self._quantity = quantity
        self._inventory = inventory
        self._hw = hardware_manager
        self._executed: bool = False

    def execute(self) -> bool:
        ok = self._hw.process_refund(self._amount, self._transaction_id)
        if ok:
            self._inventory.restock(self._product_id, self._quantity)
            self._executed = True
            print(f"[RefundCommand] ✅ Refund ₹{self._amount:.2f} for {self._transaction_id}")
        return ok

    def undo(self) -> bool:
        """Re-charge to reverse the refund."""
        ok = self._hw.process_payment(self._amount, self._transaction_id)
        if ok:
            self._inventory.commit_transaction(self._product_id, self._quantity)
            self._executed = False
        return ok

    def get_description(self) -> str:
        return f"Refund[{self._transaction_id}]: ₹{self._amount:.2f}"


# =============================================================

class RestockCommand(Command):
    """
    PATTERN: Command — Add stock to inventory. Fully undoable.
    """

    def __init__(self, product_id: str, quantity: int, inventory) -> None:
        self._product_id = product_id
        self._quantity = quantity
        self._inventory = inventory
        self._executed: bool = False

    def execute(self) -> bool:
        self._inventory.restock(self._product_id, self._quantity)
        self._executed = True
        return True

    def undo(self) -> bool:
        if not self._executed:
            return False
        p = self._inventory.get_product(self._product_id)
        if p and p.quantity >= self._quantity:
            p.quantity -= self._quantity
            self._executed = False
            print(f"[RestockCommand] ↩️  Undo restock: -{self._quantity}× {self._product_id}")
            return True
        return False

    def get_description(self) -> str:
        return f"Restock: {self._quantity}× {self._product_id}"

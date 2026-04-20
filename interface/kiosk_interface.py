# =============================================================
# interface/kiosk_interface.py  — Devam Tanna (202512010)
# PATTERN: Facade
#
# Single simplified entry point for ALL external actors:
#   Touchscreen UI, City Monitoring, Maintenance App, Tests.
#
# External systems call:
#   purchase_item()        — full atomic purchase flow
#   refund_transaction()   — reverse a completed transaction
#   restock_inventory()    — add stock (maintenance / supply)
#   run_diagnostics()      — full operational status report
#   set_operating_mode()   — force a mode transition
#   get_stock_info()       — derived stock + live price for a product
#   undo_last_command()    — reverse most recent operation
#
# The facade hides:
#   CommandInvoker, PurchaseCommand construction, PricingContext,
#   ModeManager delegation, validation, memento caretaker wiring.
# =============================================================
from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING

from transaction.commands import PurchaseCommand, RefundCommand, RestockCommand

if TYPE_CHECKING:
    from core.aura_kiosk import AuraKiosk


class KioskInterface:
    """
    PATTERN: Facade

    Provides a clean, minimal API over the entire kiosk system.
    One class — five public methods — hides all internal complexity.
    """

    def __init__(self, kiosk: "AuraKiosk") -> None:
        self._kiosk = kiosk

    # ----------------------------------------------------------
    # Core operations
    # ----------------------------------------------------------
    def purchase_item(
        self,
        product_id: str,
        qty: int = 1,
        user_id: str = "ANON",
    ) -> bool:
        """
        Full atomic purchase flow:
          mode check → kiosk validation → PurchaseCommand → execute
        Returns True on success, False on any rejection or failure.
        """
        sep = "─" * 55
        print(f"\n{sep}")
        print(
            f"[KioskInterface] PURCHASE  kiosk={self._kiosk.kiosk_id}  "
            f"product={product_id}  qty={qty}  user={user_id}"
        )

        # 1. Mode check (state pattern delegates here)
        if not self._kiosk.mode_manager.handle_purchase(product_id, qty):
            return False

        # 2. Kiosk-specific validation (prescription, refrigeration, etc.)
        if not self._kiosk.validate_purchase(product_id, qty, user_id):
            return False

        # 3. Build and execute the command (command + memento patterns inside)
        cmd = PurchaseCommand(
            kiosk_id=self._kiosk.kiosk_id,
            product_id=product_id,
            quantity=qty,
            inventory=self._kiosk.inventory,
            hardware_manager=self._kiosk.hardware,
            pricing_strategy=self._kiosk.mode_manager.get_pricing_strategy(),
            context=self._kiosk.mode_manager.get_pricing_context(),
            caretaker=self._kiosk.caretaker,
        )
        return self._kiosk.invoker.execute(cmd)

    def refund_transaction(
        self,
        transaction_id: str,
        amount: float,
        product_id: str,
        qty: int,
    ) -> bool:
        """
        Reverse a completed transaction.
        Refunds payment and restores inventory.
        """
        print(f"\n[KioskInterface] REFUND  txn={transaction_id}  ₹{amount:.2f}")
        cmd = RefundCommand(
            kiosk_id=self._kiosk.kiosk_id,
            transaction_id=transaction_id,
            amount=amount,
            product_id=product_id,
            quantity=qty,
            inventory=self._kiosk.inventory,
            hardware_manager=self._kiosk.hardware,
        )
        return self._kiosk.invoker.execute(cmd)

    def restock_inventory(self, product_id: str, qty: int) -> bool:
        """
        Add stock to the inventory (supply chain / maintenance).
        Blocked during non-maintenance modes if needed.
        """
        print(f"\n[KioskInterface] RESTOCK  product={product_id}  qty={qty}")
        if not self._kiosk.mode_manager.handle_restock():
            return False
        cmd = RestockCommand(
            product_id=product_id,
            quantity=qty,
            inventory=self._kiosk.inventory,
        )
        return self._kiosk.invoker.execute(cmd)

    def run_diagnostics(self) -> Dict[str, Any]:
        """
        Return the full operational status report of the kiosk.
        Includes mode, hardware, pricing, and mode constraints.
        """
        status = self._kiosk.get_operational_status()
        print(f"\n{'─'*55}")
        print(f"[KioskInterface] DIAGNOSTICS — {self._kiosk.kiosk_id}")
        for key, value in status.items():
            print(f"  {key:<22}: {value}")
        return status

    def set_operating_mode(self, mode: str) -> None:
        """
        Force a mode transition.
        mode ∈ {"active", "power_saving", "maintenance", "emergency"}
        """
        from core.kiosk_states import (
            ActiveState, PowerSavingState, MaintenanceState, EmergencyState,
        )
        mode_map = {
            "active":       ActiveState,
            "power_saving": PowerSavingState,
            "maintenance":  MaintenanceState,
            "emergency":    EmergencyState,
        }
        cls = mode_map.get(mode.lower())
        if cls is None:
            print(f"[KioskInterface] ❌ Unknown mode '{mode}'. "
                  f"Valid: {list(mode_map)}")
            return
        self._kiosk.mode_manager.set_state(cls())

    # ----------------------------------------------------------
    # Query helpers
    # ----------------------------------------------------------
    def get_stock_info(self, product_id: str) -> Dict[str, Any]:
        """
        Return live stock + computed price for a product.
        Both values are DERIVED — never stored.
        """
        product = self._kiosk.inventory.get_product(product_id)
        if product is None:
            return {"error": f"Product '{product_id}' not found."}

        available = self._kiosk.inventory.get_available_stock(product_id)
        ctx       = self._kiosk.mode_manager.get_pricing_context()
        strategy  = self._kiosk.mode_manager.get_pricing_strategy()
        live_price = strategy.calculate_price(product.base_price, ctx)

        return {
            "product_id":  product_id,
            "name":        product.name,
            "available":   available,
            "reserved":    product.reserved,
            "hw_faulted":  product.hw_faulted,
            "base_price":  product.base_price,
            "live_price":  live_price,
            "strategy":    strategy.get_name(),
        }

    def undo_last_command(self) -> bool:
        """Undo the most recently executed command."""
        print("\n[KioskInterface] UNDO last command…")
        return self._kiosk.invoker.undo_last()

    def get_transaction_history(self):
        """Return list of description strings for all executed commands."""
        return self._kiosk.invoker.get_history()
